# 为什么 Spring 循环依赖需要三级缓存，二级不够吗？

**难度**：中等

**创建时间**：2025-10-06 15:45:49

## 答案
Spring 解决循环依赖的核心是通过**三级缓存**（`singletonFactories`、`earlySingletonObjects`、`singletonObjects`）实现，而二级缓存无法完全解决问题。根本原因在于**AOP 代理对象生成**和**对象完整性的冲突**。以下是详细分析：

---

### **一、循环依赖的场景**
假设有两个类 `A` 和 `B` 相互依赖：
```java
@Component
public class A {
    @Autowired
    private B b;
}

@Component
public class B {
    @Autowired
    private A a;
}
```
当 Spring 初始化 `A` 时，发现需要注入 `B`，于是去初始化 `B`；而 `B` 又需要注入 `A`，此时 `A` 尚未完全初始化，形成循环依赖。

---

### **二、二级缓存的局限性**
二级缓存通常指：
1. **一级缓存（singletonObjects）**：存放完全初始化好的 Bean。
2. **二级缓存（earlySingletonObjects）**：存放提前暴露的**原始对象**（未完成属性填充和初始化）。

#### **问题 1：无法处理 AOP 代理**
- 如果 `A` 或 `B` 是需要被 AOP 代理的（如 `@Transactional`、`@Async`），二级缓存只能存储原始对象，而无法存储代理对象。
- 当 `B` 依赖 `A` 时，从二级缓存拿到的 `A` 是原始对象，但最终需要的是代理对象，导致不一致。

#### **问题 2：对象状态不一致**
- 原始对象可能处于“半初始化”状态（属性未填充），直接暴露可能导致后续初始化逻辑错误。

---

### **三、三级缓存的设计**
Spring 的三级缓存结构：
1. **`singletonObjects`**：存放完全初始化好的 Bean。
2. **`earlySingletonObjects`**：存放提前暴露的**原始对象**（缓存优化，避免重复创建）。
3. **`singletonFactories`**：存放**对象工厂**（`ObjectFactory`），用于生成代理对象或原始对象。

#### **解决循环依赖的关键流程**
1. **初始化 `A`**：
   - 创建 `A` 的原始对象（调用构造函数），放入 `singletonFactories`（存储 `ObjectFactory`，可生成代理或原始对象）。
   - 暴露 `A` 的引用（允许其他 Bean 注入）。

2. **初始化 `B`**：
   - 创建 `B` 的原始对象，放入 `singletonFactories`。
   - 注入 `A` 时，从 `singletonFactories` 获取 `A` 的 `ObjectFactory`，调用 `getObject()`：
     - 如果 `A` 需要代理，则生成代理对象；否则返回原始对象。
     - 将代理对象/原始对象放入 `earlySingletonObjects`（缓存优化）。

3. **完成 `B` 的初始化**：
   - `B` 完成属性填充和初始化后，放入 `singletonObjects`。

4. **完成 `A` 的初始化**：
   - `A` 注入 `B` 时，从 `singletonObjects` 获取完全初始化的 `B`。
   - `A` 完成初始化后，放入 `singletonObjects`，并从 `singletonFactories` 和 `earlySingletonObjects` 中移除。

---

### **四、为什么二级缓存不够？**
#### **场景 1：无 AOP 的普通 Bean**
- 二级缓存可以存储原始对象，解决循环依赖。
- 但 Spring 的设计需要兼容 AOP，因此必须支持代理对象生成。

#### **场景 2：有 AOP 的 Bean**
- 二级缓存无法存储代理对象，只能存储原始对象。
- 当其他 Bean 依赖时，拿到的对象与最终容器中的对象不一致（原始对象 vs 代理对象），导致功能错误。

#### **三级缓存的优势**
- **`singletonFactories`** 存储 `ObjectFactory`，在需要时动态决定生成原始对象还是代理对象。
- **`earlySingletonObjects`** 缓存已生成的对象（避免重复调用 `ObjectFactory`），提升性能。

---

### **五、代码级验证**
以 Spring 源码中的 `AbstractAutowireCapableBeanFactory` 为例：
1. **提前暴露对象**：
   ```java
   protected void addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory) {
       Assert.notNull(singletonFactory, "Singleton factory must not be null");
       synchronized (this.singletonObjects) {
           if (!this.singletonObjects.containsKey(beanName)) {
               this.singletonFactories.put(beanName, singletonFactory);
               this.earlySingletonObjects.remove(beanName);
               this.registeredSingletons.add(beanName);
           }
       }
   }
   ```
   - 先将 `ObjectFactory` 放入 `singletonFactories`，允许后续通过工厂生成对象。

2. **获取早期对象**：
   ```java
   protected Object getEarlyBeanReference(String beanName, RootBeanDefinition mbd, Object bean) {
       Object exposedObject = bean;
       if (!mbd.isSynthetic() && hasInstantiationAwareBeanPostProcessors()) {
           for (BeanPostProcessor bp : getBeanPostProcessors()) {
               if (bp instanceof SmartInstantiationAwareBeanPostProcessor) {
                   SmartInstantiationAwareBeanPostProcessor ibp = (SmartInstantiationAwareBeanPostProcessor) bp;
                   exposedObject = ibp.getEarlyBeanReference(exposedObject, beanName);
               }
           }
       }
       return exposedObject;
   }
   ```
   - 调用 `SmartInstantiationAwareBeanPostProcessor`（如 `AbstractAutoProxyCreator`）生成代理对象。

---

### **六、总结**
- **二级缓存的局限性**：无法同时处理原始对象和代理对象，导致 AOP 场景下对象不一致。
- **三级缓存的必要性**：
  1. **`singletonFactories`**：动态生成对象（原始或代理），支持 AOP。
  2. **`earlySingletonObjects`**：缓存已生成的对象，优化性能。
  3. **`singletonObjects`**：存储完全初始化的 Bean。
- **Spring 的权衡**：通过三级缓存兼顾循环依赖解决和 AOP 代理的正确性，是设计上的最优解。

**最终结论**：二级缓存无法满足 AOP 代理对象生成的需求，三级缓存是 Spring 解决循环依赖的完整方案。
