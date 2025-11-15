# 简述 MyBatis 的插件运行原理，以及如何编写一个插件？

**难度**：中等

**创建时间**：2025-10-06 06:01:56

## 答案
MyBatis 插件通过 **动态代理机制** 在核心组件方法执行前后插入自定义逻辑，其运行原理基于 **拦截器链** 和 **方法签名匹配**，编写插件需实现 `Interceptor` 接口并配置拦截目标。以下是详细说明：

### **一、插件运行原理**
1. **核心组件**  
   MyBatis 插件通过拦截以下四大核心接口的方法实现扩展：
   - **Executor**：执行增删改查（`update`、`query`）、事务管理（`commit`、`rollback`）等。
   - **ParameterHandler**：处理 SQL 参数（`setParameters`）。
   - **ResultSetHandler**：处理结果集（`handleResultSets`）。
   - **StatementHandler**：操作 JDBC Statement（`prepare`、`batch`）。

2. **代理机制**  
   - MyBatis 启动时解析插件配置，将拦截器存入 `InterceptorChain`（责任链模式）。
   - 创建核心对象（如 `Executor`）时，调用 `interceptorChain.pluginAll(target)`，遍历拦截器并通过 `Plugin.wrap(target, interceptor)` 生成动态代理对象。
   - 代理对象在方法调用时，先检查是否存在匹配的拦截器，若存在则执行 `intercept()` 方法，再决定是否继续调用原方法（`invocation.proceed()`）。

3. **执行流程**  
   ```mermaid
   graph TD
     A[SqlSession 创建 Executor] --> B[InterceptorChain.pluginAll]
     B --> C{遍历拦截器}
     C -->|匹配签名| D[生成代理对象]
     C -->|不匹配| E[返回原对象]
     D --> F[执行方法时触发 intercept()]
     F --> G{是否调用 proceed()}
     G -->|是| H[执行原方法]
     G -->|否| I[返回自定义结果]
   ```

### **二、编写插件步骤**
#### **1. 实现 `Interceptor` 接口**
需重写以下方法：
- `Object intercept(Invocation invocation)`：拦截逻辑的核心方法，通过 `invocation.proceed()` 控制原方法执行。
- `Object plugin(Object target)`：生成代理对象，通常直接调用 `Plugin.wrap(target, this)`。
- `void setProperties(Properties properties)`：接收配置参数（如 XML 中 `<property>` 配置的值）。

#### **2. 定义拦截目标**
使用 `@Intercepts` 和 `@Signature` 注解指定拦截的类、方法及参数类型：
```java
@Intercepts({
    @Signature(
        type = Executor.class,          // 拦截 Executor 接口
        method = "query",               // 拦截 query 方法
        args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class}
    )
})
public class ExamplePlugin implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 前置逻辑（如日志、性能监控）
        System.out.println("Before query execution");
        
        // 执行原方法
        Object result = invocation.proceed();
        
        // 后置逻辑（如结果处理）
        System.out.println("After query execution");
        return result;
    }

    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
        // 处理配置参数
    }
}
```

#### **3. 注册插件**
- **XML 配置**：在 `mybatis-config.xml` 中添加 `<plugins>` 节点：
  ```xml
  <configuration>
      <plugins>
          <plugin interceptor="com.example.ExamplePlugin">
              <property name="key" value="value"/> <!-- 可选参数 -->
          </plugin>
      </plugins>
  </configuration>
  ```
- **Spring Boot 配置**：通过 Java 代码注入插件：
  ```java
  @Configuration
  public class MyBatisConfig {
      @Bean
      public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
          SqlSessionFactoryBean factoryBean = new SqlSessionFactoryBean();
          factoryBean.setDataSource(dataSource);
          factoryBean.setPlugins(new Interceptor[]{new ExamplePlugin()}); // 注册插件
          return factoryBean.getObject();
      }
  }
  ```

### **三、关键注意事项**
1. **方法签名匹配**：`@Signature` 的 `args` 需精确匹配目标方法的参数类型，否则拦截失效。
2. **性能影响**：拦截器会拦截所有匹配的方法，避免在高频操作（如批量查询）中添加复杂逻辑。
3. **代理链顺序**：多个插件按配置顺序生成代理链，执行顺序为 **从外到内**（即配置靠前的插件先执行前置逻辑，后执行后置逻辑）。

### **四、典型应用场景**
- **分页插件**：拦截 `StatementHandler.prepare()`，修改 SQL 添加 `LIMIT` 子句。
- **数据加密**：拦截 `ParameterHandler.setParameters()`，对敏感字段加密。
- **性能监控**：拦截 `Executor.query()`/`update()`，记录方法执行时间。

通过动态代理和拦截器链，MyBatis 插件实现了灵活的扩展机制，开发者可在不修改框架源码的情况下定制核心行为。
