# Spring Boot 是如何通过 main 方法启动 web 项目的？

**难度**：中等

**创建时间**：2025-10-06 06:00:06

## 答案
Spring Boot 通过 `main` 方法启动 Web 项目的过程，本质上是利用 **Java 主类入口** + **Spring Boot 内置的 Servlet 容器（如 Tomcat/Jetty/Undertow）** + **自动配置机制** 的协同工作。以下是详细的启动流程解析：

---

## **1. 入口：`main` 方法**
Spring Boot 项目的启动入口是一个标准的 Java 主类，包含 `main` 方法。例如：
```java
@SpringBootApplication
public class MyApp {
    public static void main(String[] args) {
        SpringApplication.run(MyApp.class, args);
    }
}
```
- **`@SpringBootApplication`**：这是一个组合注解，包含以下核心注解：
  - `@SpringBootConfiguration`：标识该类为 Spring Boot 的配置类。
  - `@EnableAutoConfiguration`：启用 Spring Boot 的自动配置机制。
  - `@ComponentScan`：自动扫描当前包及其子包下的 Spring 组件（如 `@Controller`、`@Service`）。

- **`SpringApplication.run()`**：  
  这是 Spring Boot 启动的核心方法，负责初始化 Spring 容器并启动内置的 Web 服务器。

---

## **2. 启动流程详解**
### **（1）初始化 `SpringApplication` 实例**
在 `SpringApplication.run()` 内部，会先创建一个 `SpringApplication` 对象，并完成以下准备：
1. **推断应用类型**：  
   根据类路径（Classpath）判断是否为 Web 项目（如存在 `spring-boot-starter-web` 依赖）。
2. **加载配置源**：  
   收集 `META-INF/spring.factories` 文件中的自动配置类（Auto Configuration Classes）。
3. **设置监听器**：  
   初始化 Spring 事件监听器（如 `ApplicationListener`），用于监听启动过程中的事件（如 `ApplicationStartedEvent`）。

### **（2）运行启动阶段**
调用 `run()` 方法后，进入启动流程，主要分为以下步骤：

#### **阶段 1：准备环境（Prepare Environment）**
- 加载外部配置（如 `application.properties`/`application.yml`）。
- 绑定命令行参数（`args`）到 Spring 环境（`Environment`）。
- 触发 `ApplicationEnvironmentPreparedEvent` 事件。

#### **阶段 2：创建应用上下文（Create ApplicationContext）**
- 根据应用类型（Web/非 Web）创建对应的 `ApplicationContext`：
  - Web 项目：`AnnotationConfigServletWebServerApplicationContext`（内置 Servlet 容器）。
  - 非 Web 项目：`AnnotationConfigApplicationContext`。
- 加载自动配置类（通过 `@EnableAutoConfiguration`）。

#### **阶段 3：刷新上下文（Refresh Context）**
- 执行 Spring 容器的核心初始化逻辑（`ConfigurableApplicationContext.refresh()`）：
  1. **Bean 定义加载**：扫描 `@ComponentScan` 包下的组件，并注册到 Bean 工厂。
  2. **自动配置**：根据条件注解（如 `@ConditionalOnClass`）加载预定义的 Bean（如数据源、DispatcherServlet）。
  3. **发布事件**：触发 `ContextRefreshedEvent`。

#### **阶段 4：启动内置 Web 服务器（Start Embedded Server）**
- **关键步骤**：
  1. **创建 Servlet 容器**：  
     通过 `ServletWebServerApplicationContext` 初始化内置的 Tomcat/Jetty/Undertow（依赖 `spring-boot-starter-tomcat` 等）。
  2. **注册 DispatcherServlet**：  
     自动配置 `DispatcherServlet` 并映射到 `/` 路径（Spring MVC 的前端控制器）。
  3. **启动服务器**：  
     调用 `ServletWebServer.start()` 绑定端口（默认 `8080`），并监听 HTTP 请求。

#### **阶段 5：发布启动完成事件（ApplicationReadyEvent）**
- 触发 `ApplicationReadyEvent`，表示应用已完全启动，可以接收请求。

---

## **3. 内置 Web 服务器的奥秘**
Spring Boot 通过 **自动配置** 嵌入 Servlet 容器，无需手动部署 WAR 包到外部服务器。以下是关键实现：

### **（1）依赖管理**
- `spring-boot-starter-web` 默认引入 `spring-boot-starter-tomcat`，包含 Tomcat 的核心依赖。
- 如果需要替换为 Jetty/Undertow，需排除 Tomcat 并引入对应依赖：
  ```xml
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
      <exclusions>
          <exclusion>
              <groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-starter-tomcat</artifactId>
          </exclusion>
      </exclusions>
  </dependency>
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-jetty</artifactId>
  </dependency>
  ```

### **（2）自动配置 Servlet 容器**
- Spring Boot 通过 `ServletWebServerFactoryAutoConfiguration` 自动配置：
  - 检测类路径中的 `Servlet` 类（如 `javax.servlet.Servlet`）判断是否为 Web 环境。
  - 根据依赖选择对应的 `ServletWebServerFactory`（如 `TomcatServletWebServerFactory`）。
  - 创建 `ServletWebServer` 实例并启动。

### **（3）DispatcherServlet 的注册**
- `DispatcherServletAutoConfiguration` 会自动注册 `DispatcherServlet`，并映射到 `/` 路径：
  ```java
  @Bean(name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
  public DispatcherServlet dispatcherServlet() {
      return new DispatcherServlet();
  }

  @Bean
  public ServletRegistrationBean<DispatcherServlet> dispatcherServletRegistration() {
      return new ServletRegistrationBean<>(
          dispatcherServlet(), 
          "/"  // 映射路径
      );
  }
  ```

---

## **4. 调试与验证**
### **（1）查看启动日志**
Spring Boot 启动时会输出关键日志，包括：
- 自动配置的 Bean（通过 `debug=true` 启用详细日志）。
- 嵌入的服务器类型和端口（如 `Tomcat started on port(s): 8080 (http)`）。
- 扫描到的组件（如 `Mapping servlet: 'dispatcherServlet' to [/]`）。

### **（2）自定义启动行为**
- **修改端口**：在 `application.properties` 中设置：
  ```properties
  server.port=8081
  ```
- **禁用 Web 环境**：通过 `main` 方法参数或配置：
  ```java
  new SpringApplicationBuilder(MyApp.class)
      .web(WebApplicationType.NONE)  // 禁用 Web
      .run(args);
  ```

### **（3）编程式控制**
- 通过 `SpringApplication` 的 API 自定义启动流程：
  ```java
  SpringApplication app = new SpringApplication(MyApp.class);
  app.setBannerMode(Banner.Mode.OFF);  // 关闭启动 Banner
  app.run(args);
  ```

---

## **5. 总结**
Spring Boot 通过 `main` 方法启动 Web 项目的核心流程如下：
1. **初始化 `SpringApplication`**：推断应用类型、加载配置。
2. **创建 `ApplicationContext`**：根据 Web 环境选择容器类型。
3. **自动配置**：加载预定义的 Bean（如 `DispatcherServlet`、数据源）。
4. **启动内置服务器**：初始化 Tomcat/Jetty/Undertow 并绑定端口。
5. **发布就绪事件**：应用可接收 HTTP 请求。

这种设计使得 Spring Boot 项目能够以 **“约定优于配置”** 的方式快速启动，同时保持足够的灵活性（如替换服务器、自定义配置）。
