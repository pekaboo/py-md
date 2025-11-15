# Spring 如何解决循环依赖？

**难度**：中等

**创建时间**：2025-10-06 15:44:48

## 答案
Spring 通过**三级缓存**和**提前暴露对象引用**的机制解决循环依赖问题，但仅支持**单例作用域**下的**构造器注入外的循环依赖**（如 setter 注入或字段注入）。以下是详细解析：

---

### **一、循环依赖的场景**
#### **1. 什么是循环依赖？**
当两个或多个 Bean 相互依赖时形成闭环，例如：
```java
@Component
public class A {
    @Autowired
    private B b;  // A 依赖 B
}

@Component
public class B {
    @Autowired
    private A a;  // B 依赖 A
}
```

#### **2. 循环依赖的类型**
| **类型**               | **示例**                          | **Spring 是否支持**       |
|------------------------|-----------------------------------|--------------------------|
| **构造器注入循环依赖**  | `public A(B b) {...}`             | ❌ 不支持（直接抛异常）   |
| **Setter/字段注入循环**| `@Autowired private B b;`        | ✅ 支持（通过三级缓存）   |

---

### **二、Spring 解决循环依赖的核心机制**
#### **1. 三级缓存结构**
Spring 容器维护了三个 `Map` 来缓存 Bean 的不同状态：
- **一级缓存（singletonObjects）**：存放完全初始化好的 Bean（最终成品）。
- **二级缓存（earlySingletonObjects）**：存放原始 Bean 对象（已实例化但未填充属性）。
- **三级缓存（singletonFactories）**：存放 `ObjectFactory`（用于生成原始 Bean 的代理或原始对象）。

```java
// Spring 源码中的缓存结构（简化）
private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);
private final Map<String, Object> earlySingletonObjects = new HashMap<>(16);
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);
```

#### **2. 解决循环依赖的流程**
以 `A` 依赖 `B`，`B` 又依赖 `A` 为例：

1. **初始化 A**：
   - 实例化 `A`（调用构造器），此时 `A` 的对象已创建，但属性未注入。
   - 将 `A` 的 `ObjectFactory` 放入三级缓存（`singletonFactories`）。

2. **填充 A 的属性 B**：
   - 发现 `B` 未初始化，开始初始化 `B`。

3. **初始化 B**：
   - 实例化 `B`，将 `B` 的 `ObjectFactory` 放入三级缓存。
   - 填充 `B` 的属性 `A`：
     - 从一级缓存未找到 `A`，转而检查二级缓存。
     - 二级缓存未找到，检查三级缓存，发现 `A` 的 `ObjectFactory`。
     - 调用 `ObjectFactory.getObject()` 获取 `A` 的**原始对象引用**（此时 `A` 未完全初始化），并放入二级缓存（`earlySingletonObjects`），同时从三级缓存移除。
     - 将 `A` 的原始对象注入到 `B` 中。
   - `B` 完成初始化，放入一级缓存（`singletonObjects`）。

4. **继续初始化 A**：
   - 从一级缓存获取已初始化的 `B`，注入到 `A` 中。
   - `A` 完成初始化，放入一级缓存。

---

### **三、关键点解析**
#### **1. 为什么构造器注入无法解决？**
- 构造器注入要求 Bean 在实例化时必须完成所有依赖的注入，而循环依赖会导致死锁（无法同时完成两个 Bean 的构造）。
- Spring 在实例化阶段（调用构造器）后才会处理依赖注入，因此构造器注入的循环依赖无法通过提前暴露对象引用解决。

#### **2. 为什么需要三级缓存？**
- **三级缓存（singletonFactories）**：存放 `ObjectFactory`，支持 AOP 代理（如 Bean 实现了接口或被 `@Aspect` 注解修饰）。
  - 如果 Bean 需要代理，`ObjectFactory.getObject()` 会返回代理对象；否则返回原始对象。
- **二级缓存（earlySingletonObjects）**：缓存原始对象，避免重复调用 `ObjectFactory` 生成对象。
- **一级缓存（singletonObjects）**：存放完全初始化好的 Bean。

#### **3. 代理对象的处理**
如果 Bean 需要被 AOP 代理（如 `@Transactional`），三级缓存会返回代理对象，而非原始对象。例如：
```java
// 伪代码：ObjectFactory 的实现
protected Object getEarlyBeanReference(String beanName, RootBeanDefinition mbd, Object bean) {
    Object exposedObject = bean;
    if (!mbd.isSynthetic() && hasInstantiationAwareBeanPostProcessors()) {
        for (BeanPostProcessor bp : getBeanPostProcessors()) {
            if (bp instanceof SmartInstantiationAwareBeanPostProcessor) {
                exposedObject = ((SmartInstantiationAwareBeanPostProcessor) bp).getEarlyBeanReference(exposedObject, beanName);
            }
        }
    }
    return exposedObject;  // 可能返回代理对象
}
```

---

### **四、源码流程（简化版）**
Spring 解决循环依赖的核心逻辑在 `AbstractBeanFactory.doGetBean()` 和 `DefaultSingletonBeanRegistry.getSingleton()` 中：

1. **`doGetBean()`**：
   - 尝试从一级缓存获取 Bean。
   - 若未找到，标记 Bean 为正在创建，并调用 `getSingleton(beanName, () -> { ... })` 创建 Bean。

2. **`getSingleton()`**：
   - 先检查三级缓存，若存在 `ObjectFactory`，则调用 `getObject()` 获取对象。
   - 将对象从三级缓存升级到二级缓存（原始对象）。
   - 若对象需要代理，则在后续初始化阶段处理。

3. **属性注入**：
   - 填充依赖时，重复上述过程，从缓存中获取半成品对象。

---

### **五、示例验证**
#### **1. 正常循环依赖（Setter 注入）**
```java
@Component
public class A {
    private B b;
    @Autowired
    public void setB(B b) { this.b = b; }
}

@Component
public class B {
    private A a;
    @Autowired
    public void setA(A a) { this.a = a; }
}
```
**结果**：Spring 能正常初始化 `A` 和 `B`。

#### **2. 构造器注入循环依赖**
```java
@Component
public class A {
    private final B b;
    public A(B b) { this.b = b; }  // 构造器注入
}

@Component
public class B {
    private final A a;
    public B(A a) { this.a = a; }  // 构造器注入
}
```
**结果**：Spring 抛出 `BeanCurrentlyInCreationException`。

---

### **六、总结**
| **机制**               | **说明**                                                                 |
|------------------------|--------------------------------------------------------------------------|
| **三级缓存**           | 一级（成品）、二级（半成品原始对象）、三级（半成品工厂，支持代理）       |
| **提前暴露对象引用**   | 在实例化后、属性注入前，将对象引用存入缓存，供其他 Bean 提前使用         |
| **限制条件**           | 仅支持单例 Bean，且不能是构造器注入的循环依赖                            |
| **AOP 代理支持**       | 通过三级缓存的 `ObjectFactory` 动态生成代理对象                          |

**最佳实践**：
- 避免循环依赖（通过重构设计）。
- 若必须存在，优先使用 setter/字段注入，而非构造器注入。
- 注意代理对象的行为是否符合预期（如 `@Transactional` 的切面逻辑）。
