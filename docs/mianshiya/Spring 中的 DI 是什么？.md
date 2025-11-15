# Spring 中的 DI 是什么？

**难度**：中等

**创建时间**：2025-10-06 15:49:01

## 答案
在 Spring 框架中，**DI（Dependency Injection，依赖注入）** 是一种核心设计原则，用于实现对象之间的依赖关系管理。它是 **IoC（Inversion of Control，控制反转）** 的一种具体实现方式，旨在降低代码间的耦合度，提高可维护性和可测试性。

---

### **DI 的核心概念**
1. **依赖（Dependency）**  
   一个类在运行时需要依赖其他类的对象（如服务、工具类等）。例如，`UserService` 可能依赖 `UserRepository` 来访问数据库。

2. **注入（Injection）**  
   由外部容器（如 Spring）将依赖对象**自动传入**到目标类中，而非目标类自己创建或查找依赖。

---

### **DI 的三种注入方式**
Spring 支持以下方式实现依赖注入：

1. **构造器注入（Constructor Injection）**  
   - 通过类的构造器传入依赖。
   - **推荐方式**：确保依赖不可变（`final`），且在对象创建时必须提供。
   ```java
   @Service
   public class UserService {
       private final UserRepository userRepository;
       
       // 构造器注入
       public UserService(UserRepository userRepository) {
           this.userRepository = userRepository;
       }
   }
   ```

2. **Setter 注入（Setter Injection）**  
   - 通过 `setter` 方法设置依赖。
   - 适用于可选依赖或需要动态修改依赖的场景。
   ```java
   @Service
   public class UserService {
       private UserRepository userRepository;
       
       @Autowired
       public void setUserRepository(UserRepository userRepository) {
           this.userRepository = userRepository;
       }
   }
   ```

3. **字段注入（Field Injection）**  
   - 直接通过注解（如 `@Autowired`）注入到类的字段。
   - **不推荐**：破坏封装性，且难以测试（需通过反射）。
   ```java
   @Service
   public class UserService {
       @Autowired
       private UserRepository userRepository; // 字段注入
   }
   ```

---

### **DI 的优势**
1. **解耦**  
   类不直接创建依赖对象，而是通过外部注入，降低代码间的硬编码依赖。

2. **可测试性**  
   可以轻松替换依赖为模拟对象（Mock），便于单元测试。

3. **灵活性**  
   依赖的实现可以在运行时动态切换（如通过配置文件或环境变量）。

4. **符合单一职责原则**  
   每个类只关注自身逻辑，依赖管理交给容器处理。

---

### **Spring 中的 DI 实现**
Spring 通过以下注解支持 DI：
- `@Autowired`：自动注入依赖（默认按类型匹配）。
- `@Qualifier`：当存在多个同类型 Bean 时，指定具体注入的 Bean 名称。
- `@Resource`（JSR-250）：类似 `@Autowired`，但默认按名称匹配。
- `@Inject`（JSR-330）：标准 Java 注解，Spring 也支持。

---

### **示例场景**
假设有一个 `OrderService` 依赖 `PaymentGateway`：
```java
@Service
public class OrderService {
    private final PaymentGateway paymentGateway;
    
    // 构造器注入
    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }
    
    public void processOrder(Order order) {
        paymentGateway.charge(order.getAmount());
    }
}
```
Spring 容器会自动找到 `PaymentGateway` 的实现（如 `PayPalGateway` 或 `StripeGateway`）并注入到 `OrderService` 中。

---

### **总结**
- **DI 是 Spring 的核心机制**，通过外部容器管理对象间的依赖关系。
- **推荐使用构造器注入**，兼顾安全性和可维护性。
- DI 的本质是 **“由调用者决定被调用者的依赖”**，而非被调用者自己创建依赖。

通过 DI，Spring 实现了松耦合、高内聚的架构设计，是现代企业级应用开发的基础。
