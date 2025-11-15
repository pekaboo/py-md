# 说下 Spring Bean 的生命周期？

**难度**：中等

**创建时间**：2025-10-06 15:47:07

## 答案
Spring Bean 的生命周期是指 Bean 从创建到销毁的整个过程，涉及多个阶段的回调和扩展点。理解 Bean 的生命周期有助于在合适的时机进行资源初始化、依赖注入、自定义逻辑处理等操作。以下是 Spring Bean 生命周期的详细步骤和关键阶段：

---

## **1. Bean 生命周期概述**
Spring Bean 的生命周期主要分为以下几个阶段：
1. **实例化（Instantiation）**：创建 Bean 的实例。
2. **属性填充（Populate Properties）**：设置 Bean 的依赖属性（通过依赖注入）。
3. **初始化（Initialization）**：执行自定义初始化逻辑。
4. **使用（In Use）**：Bean 被应用程序使用。
5. **销毁（Destruction）**：释放 Bean 占用的资源。

---

## **2. 详细生命周期阶段**
### **阶段 1：实例化（Instantiation）**
- **触发条件**：Spring 容器通过反射（如 `Class.newInstance()` 或构造函数）创建 Bean 的实例。
- **关键点**：
  - 如果 Bean 实现了 `InstantiationAwareBeanPostProcessor` 接口，其 `postProcessBeforeInstantiation` 方法可能在此阶段拦截实例化（例如通过 AOP 代理）。
  - 实例化方式：
    - 无参构造函数（默认）。
    - 静态工厂方法（`@Bean` 注解或 XML 配置的 `factory-method`）。
    - 实例工厂方法。

---

### **阶段 2：属性填充（Populate Properties）**
- **触发条件**：Bean 实例化后，Spring 通过依赖注入（DI）设置 Bean 的属性。
- **关键点**：
  - 依赖注入方式：
    - 构造器注入（`@Autowired` 标注构造器）。
    - Setter 方法注入（`@Autowired` 标注 Setter 方法）。
    - 字段注入（直接通过反射设置字段，不推荐）。
  - 如果 Bean 实现了 `InstantiationAwareBeanPostProcessor`，其 `postProcessAfterInstantiation` 方法可以在此阶段修改属性值。

---

### **阶段 3：BeanPostProcessor 前置处理**
- **触发条件**：属性填充完成后，Spring 调用所有注册的 `BeanPostProcessor` 的 `postProcessBeforeInitialization` 方法。
- **关键点**：
  - 允许在初始化前修改 Bean 的状态（例如 AOP 代理的创建）。
  - 常见实现：
    - `AutowiredAnnotationBeanPostProcessor`：处理 `@Autowired` 和 `@Value` 注解。
    - `CommonAnnotationBeanPostProcessor`：处理 `@Resource`、`@PostConstruct` 等注解。

---

### **阶段 4：初始化（Initialization）**
#### **4.1 执行自定义初始化方法**
- **触发条件**：如果 Bean 实现了以下接口或注解，Spring 会调用对应的初始化方法：
  - `InitializingBean` 接口的 `afterPropertiesSet()` 方法。
  - `@PostConstruct` 注解标注的方法（通过 `CommonAnnotationBeanPostProcessor` 处理）。
  - XML 配置的 `init-method` 属性指定的方法。
- **执行顺序**：
  1. `@PostConstruct` 方法。
  2. `InitializingBean.afterPropertiesSet()`。
  3. XML 或 `@Bean(initMethod = "...")` 指定的方法。

#### **4.2 BeanPostProcessor 后置处理**
- **触发条件**：初始化方法执行后，Spring 调用所有注册的 `BeanPostProcessor` 的 `postProcessAfterInitialization` 方法。
- **关键点**：
  - 允许在初始化后修改 Bean 的状态（例如 AOP 代理的最终创建）。
  - 常见实现：
    - `AbstractAutoProxyCreator`：创建 AOP 代理（如 `@Transactional`、`@AspectJ`）。

---

### **阶段 5：Bean 准备就绪（Ready for Use）**
- **触发条件**：初始化完成后，Bean 被放入 Spring 容器的单例池（`DefaultSingletonBeanRegistry`）中，供应用程序使用。
- **关键点**：
  - 单例 Bean（`scope="singleton"`）会在容器启动时初始化。
  - 原型 Bean（`scope="prototype"`）会在每次请求时实例化，不调用销毁方法。

---

### **阶段 6：销毁（Destruction）**
#### **6.1 触发条件**
- 单例 Bean：容器关闭时（如 `ConfigurableApplicationContext.close()`）。
- 原型 Bean：不会自动销毁，需手动调用销毁逻辑。

#### **6.2 执行自定义销毁方法**
- **销毁顺序**：
  1. `@PreDestroy` 注解标注的方法（通过 `CommonAnnotationBeanPostProcessor` 处理）。
  2. `DisposableBean` 接口的 `destroy()` 方法。
  3. XML 配置的 `destroy-method` 属性指定的方法。

#### **6.3 调用销毁回调**
- Spring 调用所有注册的 `DestructionAwareBeanPostProcessor` 的 `postProcessBeforeDestruction` 方法（例如清理资源）。

---

## **3. 生命周期关键接口与注解**
| 接口/注解                     | 作用阶段                     | 说明                                                                 |
|------------------------------|------------------------------|----------------------------------------------------------------------|
| `InstantiationAwareBeanPostProcessor` | 实例化前后                 | 拦截 Bean 的实例化和属性填充（如 `AutowiredAnnotationBeanPostProcessor`）。 |
| `BeanPostProcessor`          | 初始化前后                 | 修改 Bean 的初始化行为（如 AOP 代理创建）。                          |
| `InitializingBean`           | 初始化方法                 | 实现 `afterPropertiesSet()` 方法。                                   |
| `@PostConstruct`             | 初始化方法                 | 标注在方法上，在依赖注入后执行。                                     |
| `DisposableBean`             | 销毁方法                   | 实现 `destroy()` 方法。                                              |
| `@PreDestroy`                | 销毁方法                   | 标注在方法上，在容器关闭前执行。                                     |
| `init-method`/`destroy-method` | 初始化/销毁方法           | 通过 XML 或 `@Bean` 注解指定自定义方法。                              |

---

## **4. 生命周期示例代码**
### **4.1 定义 Bean**
```java
public class UserService implements InitializingBean, DisposableBean {
    private String name;

    public UserService() {
        System.out.println("1. 实例化");
    }

    @Autowired
    public void setName(String name) {
        System.out.println("2. 属性填充: name=" + name);
        this.name = name;
    }

    @PostConstruct
    public void init() {
        System.out.println("3. @PostConstruct 初始化");
    }

    @Override
    public void afterPropertiesSet() {
        System.out.println("4. InitializingBean.afterPropertiesSet()");
    }

    public void customInit() {
        System.out.println("5. XML/init-method 初始化");
    }

    public void customDestroy() {
        System.out.println("6. XML/destroy-method 销毁");
    }

    @Override
    public void destroy() {
        System.out.println("7. DisposableBean.destroy()");
    }

    @PreDestroy
    public void preDestroy() {
        System.out.println("8. @PreDestroy 销毁");
    }
}
```

### **4.2 配置 Bean**
#### **XML 配置**
```xml
<bean id="userService" class="com.example.UserService" init-method="customInit" destroy-method="customDestroy">
    <property name="name" value="Spring" />
</bean>
```

#### **Java 配置（`@Bean`）**
```java
@Configuration
public class AppConfig {
    @Bean(initMethod = "customInit", destroyMethod = "customDestroy")
    public UserService userService() {
        return new UserService();
    }
}
```

### **4.3 自定义 BeanPostProcessor**
```java
public class CustomBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        System.out.println("BeanPostProcessor.postProcessBeforeInitialization: " + beanName);
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        System.out.println("BeanPostProcessor.postProcessAfterInitialization: " + beanName);
        return bean;
    }
}
```

### **4.4 输出顺序**
```
1. 实例化
2. 属性填充: name=Spring
BeanPostProcessor.postProcessBeforeInitialization: userService
3. @PostConstruct 初始化
4. InitializingBean.afterPropertiesSet()
5. XML/init-method 初始化
BeanPostProcessor.postProcessAfterInitialization: userService
[Bean 使用中...]
BeanPostProcessor.postProcessBeforeDestruction: userService  （需手动触发销毁）
8. @PreDestroy 销毁
7. DisposableBean.destroy()
6. XML/destroy-method 销毁
```

---

## **5. 常见问题与注意事项**
1. **循环依赖**：
   - 构造器注入导致的循环依赖无法解决（会抛出 `BeanCurrentlyInCreationException`）。
   - Setter 注入或字段注入可通过三级缓存（单例池、早期曝光对象、原型对象）解决。
2. **AOP 代理创建时机**：
   - 在 `postProcessAfterInitialization` 阶段通过 `AbstractAutoProxyCreator` 创建代理。
3. **销毁方法调用**：
   - 原型 Bean 不会自动调用销毁方法，需手动管理。
4. **性能优化**：
   - 避免在 `BeanPostProcessor` 中执行耗时操作。
   - 合理使用 `@Lazy` 延迟初始化单例 Bean。

---

## **6. 总结**
Spring Bean 的生命周期是一个高度可扩展的框架，通过接口和注解提供了多个回调点。理解生命周期的关键在于：
1. **实例化 → 属性填充 → 初始化 → 使用 → 销毁** 的主流程。
2. **`BeanPostProcessor` 和 `DestructionAwareBeanPostProcessor`** 的扩展机制。
3. **初始化/销毁方法的执行顺序**（`@PostConstruct` → `InitializingBean` → `init-method`）。

通过合理利用这些机制，可以实现依赖注入、AOP 代理、资源管理等核心功能。
