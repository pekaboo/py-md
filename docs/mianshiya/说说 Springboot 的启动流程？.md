# 说说 Springboot 的启动流程？

**难度**：中等

**创建时间**：2025-10-06 05:57:53

## 答案
Spring Boot 的启动流程是一个高度自动化的过程，通过`SpringApplication.run()`方法触发，核心步骤包括初始化环境、创建应用上下文、加载配置、启动内嵌服务器等。以下是详细的启动流程解析：

---

### **1. 准备阶段：初始化 `SpringApplication` 实例**
当调用`SpringApplication.run(Application.class, args)`时，首先会创建`SpringApplication`实例，执行以下操作：
- **推断应用类型**：通过类路径判断是Web应用（存在`javax.servlet.Servlet`或`org.springframework.web.reactive.HttpHandler`）还是非Web应用。
- **加载初始化器（Initializers）**：从`META-INF/spring.factories`中加载`ApplicationContextInitializer`实现类（如`SpringBootContextLoaderListener`），用于初始化应用上下文。
- **加载监听器（Listeners）**：同样从`META-INF/spring.factories`中加载`ApplicationListener`实现类（如`EventPublishingRunListener`），用于发布启动事件。
- **确定主类**：通过栈轨迹找到调用`run()`方法的类（即`@SpringBootApplication`标注的主类）。

---

### **2. 启动阶段：运行 `SpringApplication`**
调用`springApplication.run()`后，执行以下核心步骤：

#### **2.1 发布启动事件**
- 触发`ApplicationStartingEvent`事件，通知所有监听器应用已启动。

#### **2.2 准备环境（Environment）**
- **配置环境**：根据`application.properties`/`application.yml`和命令行参数创建`ConfigurableEnvironment`（如`StandardEnvironment`或`StandardServletEnvironment`）。
- **绑定属性**：将外部配置（如环境变量、JVM参数）绑定到`Environment`对象。
- **发布事件**：触发`ApplicationEnvironmentPreparedEvent`事件。

#### **2.3 创建应用上下文（ApplicationContext）**
- 根据应用类型选择上下文：
  - Web应用：`AnnotationConfigServletWebServerApplicationContext`（Servlet环境）或`AnnotationConfigReactiveWebServerApplicationContext`（响应式环境）。
  - 非Web应用：`AnnotationConfigApplicationContext`。
- 加载上下文初始化器（`ApplicationContextInitializer`），对上下文进行预处理。

#### **2.4 准备上下文（Prepare Context）**
- **设置环境**：将`Environment`注入到上下文中。
- **应用初始化器**：执行所有`ApplicationContextInitializer`的`initialize()`方法。
- **发布事件**：触发`ApplicationContextInitializedEvent`事件。

#### **2.5 加载Bean定义（Refresh Context）**
调用上下文的`refresh()`方法（继承自`AbstractApplicationContext`），执行以下操作：
- **准备刷新**：初始化属性源、监听器等。
- **获取Bean工厂**：创建`DefaultListableBeanFactory`作为Bean容器。
- **加载Bean定义**：
  - 扫描主类所在包及其子包下的`@Component`、`@Service`、`@Controller`等注解类。
  - 处理自动配置（`@EnableAutoConfiguration`）：通过`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`加载自动配置类。
- **注册Bean定义**：将扫描到的Bean定义注册到Bean工厂。
- **初始化单例Bean**：预初始化所有`@Lazy(false)`的单例Bean。
- **完成刷新**：触发`ContextRefreshedEvent`事件。

#### **2.6 启动内嵌服务器（Web应用）**
- **创建服务器**：根据依赖（如Tomcat、Jetty、Undertow）创建`ServletWebServerFactory`（如`TomcatServletWebServerFactory`）。
- **启动服务器**：绑定端口、部署应用上下文到服务器。
- **发布事件**：触发`ApplicationStartedEvent`事件。

#### **2.7 执行运行监听器（Run Listeners）**
- 调用所有`ApplicationRunner`和`CommandLineRunner`的`run()`方法，允许在应用启动后执行自定义逻辑。

#### **2.8 发布就绪事件**
- 触发`ApplicationReadyEvent`事件，表示应用已完全启动并准备接收请求。

---

### **3. 关键事件流**
Spring Boot启动过程中会按顺序发布以下事件（可通过`ApplicationListener`监听）：
1. `ApplicationStartingEvent`：启动前。
2. `ApplicationEnvironmentPreparedEvent`：环境准备完成。
3. `ApplicationContextInitializedEvent`：上下文初始化完成。
4. `ApplicationPreparedEvent`：上下文刷新前。
5. `ApplicationStartedEvent`：上下文刷新完成，服务器启动前。
6. `ApplicationReadyEvent`：应用就绪。
7. `ApplicationFailedEvent`：启动失败时触发。

---

### **4. 自动化配置的秘密**
Spring Boot的自动配置通过以下机制实现：
- **条件注解**：如`@ConditionalOnClass`、`@ConditionalOnProperty`等，根据环境动态决定是否加载配置。
- **自动配置类**：如`DataSourceAutoConfiguration`、`WebMvcAutoConfiguration`，通过`@EnableAutoConfiguration`导入。
- **排除机制**：可通过`spring.autoconfigure.exclude`排除特定自动配置。

---

### **5. 调试启动流程**
- **日志级别**：设置`logging.level.org.springframework.boot=DEBUG`查看详细启动日志。
- **事件监听**：实现`ApplicationListener`监听特定事件。
- **Actuator端点**：通过`/actuator/startup`端点（需启用）查看启动阶段耗时。

---

### **总结**
Spring Boot的启动流程是一个分层递进的过程，从环境准备到上下文刷新，再到服务器启动，最终通过事件机制实现高度可扩展性。理解这一流程有助于排查启动问题、优化启动性能或自定义启动行为。
