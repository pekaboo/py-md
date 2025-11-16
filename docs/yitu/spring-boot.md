---
title: Springboot相关
description: Springboot相关
---
# Springboot相关
## 5. Spring Boot 启动流程

### 要点速览 · 5

- `SpringApplication.run` 启动；准备环境→加载上下文→刷新→执行 Runner。
- 自动配置依赖 `SpringFactoriesLoader` 与条件装配。
- 内嵌容器通过 `ServletWebServerFactory` 启动。

### 基础要点 · 5

- 创建 `SpringApplication`：推断应用类型（Servlet/Reactive）、推断主类。
- **prepareEnvironment**：加载配置文件、`EnvironmentPostProcessor`。
- **createApplicationContext**：根据类型创建 `AnnotationConfigServletWebServerApplicationContext`。
- **refreshContext**：BeanDefinition 注册、后置处理器、Bean 实例化。

### 进阶扩展 · 5

- 自动配置读取 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，通过 `@Conditional` 控制加载。
- `SpringApplicationRunListeners` 贯穿启动过程（如 `EventPublishingRunListener`）。
- 嵌入式容器通过 `EmbeddedWebServerFactoryCustomizer` 自定义端口、SSL。

### ⚠️注意事项 · 5

- 自定义 `ApplicationContextInitializer`、`ApplicationRunner` 顺序需关注 `Ordered`。
- 自动配置冲突时使用 `@ConditionalOnMissingBean`、`@AutoConfigureAfter` 避免覆盖。
- 启动耗时排查可启用 `spring.main.log-startup-info=true` 和 `ApplicationStartup`。

## 7. Spring 自动装配流程

### 要点速览 · 7

- `@SpringBootApplication` → `@EnableAutoConfiguration` → Import Selector。
- BeanDefinition 注册后按生命周期实例化。
- 条件注解决定装配。

### 基础要点 · 7

- `EnableAutoConfigurationImportSelector` 读取 `AutoConfiguration.imports` 列表。
- 通过 `ConditionEvaluationReport` 记录条件匹配原因。
- Bean 创建经历：实例化→属性填充→`Aware` 回调→`BeanPostProcessor`→初始化方法→就绪。

### 进阶扩展 · 7

- 自定义 `@Conditional` 实现复杂条件，如环境变量、ClassPath、配置值。
- `@ConfigurationProperties` + `Binder` 实现配置绑定。
- 使用 `spring.factories` 或新版本 `AutoConfiguration.imports` 注册自定义自动配置模块。

### ⚠️注意事项 · 7

- 避免把组件扫描到同名 Bean 导致 `BeanDefinitionOverrideException`。
- 自动配置调试可用 `--debug` 查看条件报告。
- `BeanFactoryPostProcessor` 与 `BeanPostProcessor` 顺序易混；注意生命周期。

## 8. AOP 原理与场景

### 要点速览 · 8

- 基于代理：JDK 动态代理、CGLIB。
- 织入：执行链构建、切面匹配。
- 常用场景：日志、事务、安全、限流。

### 基础要点 · 8

- AOP 核心概念：切点（Pointcut）、通知（Advice）、切面（Aspect）、连接点（JoinPoint）。
- Spring AOP 默认运行期代理方式，针对接口用 JDK Proxy，无接口用 CGLIB。

### 进阶扩展 · 8

- BeanPostProcessor：`AnnotationAwareAspectJAutoProxyCreator` 在 Bean 初始化前创建代理。
- AOP 调用链通过 `MethodInterceptor` 链执行，类似责任链。
- 与事务传播：事务本质也是 AOP，`TransactionInterceptor` 拦截方法执行。

### ⚠️注意事项 · 8

- 自调用会绕过代理导致切面失效，可用 `AopContext.currentProxy()` 或分离 Bean。
- CGLIB 代理 final 类/方法无效；谨慎使用 `final`。
- 过多切面增加调用开销，注意监控。
- 过多切面增加调用开销，注意监控。



## 12. ThreadLocal 使用场景

### 要点速览 · 12

- 为线程提供独立变量副本，适用线程封闭数据。
- 常见场景：请求上下文、数据库连接、格式化器。
- 注意内存泄漏，特别在线程池。

### 基础要点 · 12

- `ThreadLocal.set` 将值存储在线程的 `ThreadLocalMap` 中，键是 `ThreadLocal` 本身。
- 每个线程访问互不干扰，无需同步。

### 进阶扩展 · 12

- Web 应用中的上下文信息（用户信息、租户 ID）保存在 ThreadLocal。
- `InheritableThreadLocal` 支持子线程继承值（需谨慎）。
- 与 MDC（Mapped Diagnostic Context）结合，为日志注入上下文。

### ⚠️注意事项 · 12

- 使用完必须 `remove`，防止线程池线程复用导致脏数据。
- `ThreadLocal` key 是弱引用，但 value 不是——及时清理。
- 避免用于大对象，减少内存压力。

## 13. ThreadLocal 结合 TraceId 链路追踪

### 要点速览 · 13

- 请求入口生成 TraceId，保存在 ThreadLocal/MDC。
- Logback/Log4j2 通过 `%X{traceId}` 输出。
- 跨线程、跨进程需传递 TraceId。

### 基础要点 · 13

- 在 Gateway/Controller 拦截器生成 TraceId（UUID/Snowflake）。
- 使用 `MDC.put("traceId", id)` 保存在日志上下文。

### 进阶扩展 · 13

- **跨 Dubbo**：利用 RPC 上下文，Consumer 发送时写入 Attachment，Provider 读取后放入 ThreadLocal。
- **跨 Spring Cloud**：Sleuth 使用 `TraceContext`，通过 HTTP header（`X-B3-TraceId`）。
- **跨 MQ**：消息属性携带 TraceId，消费端取出后写入 ThreadLocal。
- **定时任务**：触发时创建新的 TraceId，输出日志关联。

### ⚠️注意事项 · 13

- 异步线程需手动复制 MDC（`MdcTaskDecorator`）。
- 链路过长 TraceId 传递失败会断链，需监控 header 丢失。
- 对敏感信息做脱敏，避免在日志暴露。

## 14. 生产环境故障排查流程

### 要点速览 · 14

- OOM：抓取堆 dump，分析对象占用。
- 频繁 Full GC：监控 GC 日志，分析老年代/元空间压力。
- 慢 SQL、接口慢：定位计划、索引、外部依赖。
- JVM 调优：基于监控数据迭代。

### 基础要点 · 14

- **OOM**：启用 `-XX:+HeapDumpOnOutOfMemoryError`，使用 MAT/VisualVM 分析。定位内存泄漏（缓存未清理、集合无限增长）。
- **Full GC**：查看 GC 日志（`-Xlog:gc*`），分析触发原因（晋升失败、元空间满）。
- **慢 SQL**：开启慢查询日志，分析执行计划、索引命中；优化索引、SQL 改写。
- **接口慢**：链路追踪定位瓶颈（数据库、下游、锁），查看线程池、连接池。

### 进阶扩展 · 14

- **OOM**：分代区分（Eden/Old/Metaspace/Direct）不同策略；使用 `jmap`, `arthas`, `async-profiler`。
- **Full GC**：调整新生代比例、晋升阈值、元空间大小；评估是否需要 G1/ZGC。
- **慢 SQL**：利用 `Explain Analyze`、索引覆盖、分区表、缓存；关注 InnoDB buffer pool 命中率。
- **接口慢**：限流降级、请求打散、依赖熔断；利用火焰图定位 CPU 热点。
- **JVM 调优**：压测→监控→调整堆大小、GC 算法、线程栈尺寸。

### ⚠️注意事项 · 14

- 线上调参数需灰度验证，避免一次性大改。
- Dump 文件包含敏感数据，妥善处理。
- 慢 SQL 需结合数据量和业务场景，避免盲目添加索引导致写性能下降。

## 15. 布隆过滤器原理

### 要点速览 · 15

- 位数组 + 多个哈希函数判重，允许误判存在，不允许误判不存在。
- 插入/查询 O(k)。
- 适用于大规模去重、缓存穿透防护。

### 基础要点 · 15

- 初始化位数组全 0，元素加入时通过 k 个哈希函数计算位置置 1。
- 查询时所有位为 1 判为可能存在，否则一定不存在。

### 进阶扩展 · 15

- 误判率由位数组长度 m、元素数 n、哈希函数个数 k 决定：`(1 - e^{-kn/m})^k`。
- 可扩展布隆过滤器（分层）和计数布隆过滤器（支持删除）。
- Redis `bf.add`/`cf.add` (RedisBloom) 提供实现。

### ⚠️注意事项 · 15

- 哈希函数独立性影响误判，需选取均匀的哈希。
- 不能删除（标准 Bloom），删除需计数型但内存更大。
- 误判率随元素增加而上升，应预估容量或扩展层级。

## 16. 限流算法（滑动窗口、令牌桶、漏桶）

### 要点速览 · 16

- 固定窗口：简单但有临界突刺问题。
- 滑动窗口：平滑统计。
- 令牌桶：控制平均速率允许突发。
- 漏桶：平滑输出。

### 基础要点 · 16

- **滑动窗口**：按时间片记录请求数，窗口移动时淘汰过期计数。
- **令牌桶**：按速率生成令牌，桶满即丢；请求获取令牌才执行。
- **漏桶**：请求进入漏桶，按常量速率流出，多余请求被丢弃。

### 进阶扩展 · 16

- 分布式限流可用 Redis + Lua 原子操作，实现滑动窗口或令牌桶。
- 令牌桶适合突发流量（比如支付答题），漏桶适合严格平滑输出（下游能力有限）。
- 结合熔断、降级、黑名单、灰度发布形成全链路保护。

### ⚠️注意事项 · 16

- Redis 限流脚本需防雪崩，注意键过期策略。
- 单机限流与分布式限流需区分；多实例需共享状态。
- 限流反馈需友好（排队、降级页面）。



## 20. Spring AOP 失效场景

### 要点速览 · 20

- 自调用、非 Spring 管理、代理类型不匹配。
- Final 方法/类、私有方法无法代理。
- Bean 初始化顺序导致代理没生效。

### 基础要点 · 20

- 同类方法互调绕过代理（`this.method()`）。
- Bean 未纳入 Spring 容器（`new` 出来）。
- 使用 JDK 动态代理时目标类没有接口。

### 进阶扩展 · 20

- 配置 `proxyTargetClass=true` 强制使用 CGLIB。
- 使用 `@Lazy` + `ObjectProvider` 注入自身代理。
- 在 `@PostConstruct` 内调用 AOP 方法同样无效。

### ⚠️注意事项 · 20

- 在异步线程调用需确保拿到代理（组合 `@Async` + AOP 时顺序）。
- 切面表达式写错或优先级导致未匹配。
- 多重代理堆叠影响性能，检查 `Advisor` 顺序。


## 24. @Transactional 失效原因

### 要点速览 · 24

- 代理未生效：自调用、非 public 方法、对象未托管。
- 声明式事务条件不满足：异常未抛出、传播行为不符。
- 事务管理器或数据源配置问题。

### 基础要点 · 24

- `@Transactional` 依赖 AOP 代理，仅对公共方法生效。
- 自调用跳过代理，导致事务不启用。
- 非运行期异常（默认仅 `RuntimeException`）不会触发回滚。

### 进阶扩展 · 24

- 多数据源场景需指定 `transactionManager`，否则找不到 Bean。
- 使用 JDK 代理时目标类需实现接口，否则需 `proxyTargetClass=true`。
- 异步方法（`@Async`）在新线程执行，事务上下文丢失。

### ⚠️注意事项 · 24

- 避免在构造函数、`@PostConstruct` 调用事务方法。
- 明确 rollbackFor/ noRollbackFor，避免业务异常误吞。
- MyBatis mapper `SqlSessionTemplate` 自带事务管理，注意配置冲突。

## 25. 事务传播机制

### 要点速览 · 25

- Spring 提供 7 种传播方式，默认 `REQUIRED`。
- 关键行为：加入现有事务、开启新事务、非事务执行。
- 正确选择决定嵌套调用的一致性与隔离。

### 基础要点 · 25

- `REQUIRED`：存在事务加入，否则新建。
- `REQUIRES_NEW`：挂起当前事务，开启新事务。
- `SUPPORTS`：有事务就加入，没有就非事务。
- `MANDATORY`/`NEVER`/`NOT_SUPPORTED`/`NESTED` 各代表强制、有无事务约束。

### 进阶扩展 · 25

- `NESTED` 依赖保存点，底层只对支持 `Savepoint` 的数据源有效。
- 事务传播结合回滚规则可能导致外层事务决策不同。
- MQ 事务消息、TCC 方案可类比 `REQUIRES_NEW` 行为。

### ⚠️注意事项 · 25

- 嵌套调用默认 `REQUIRED` 共用一个事务，一旦外层回滚全体回滚。
- `REQUIRES_NEW` 可能导致外层回滚但内层已提交，需明确业务意义。
- 使用声明式事务时注意与编程式事务混用的优先级。