# 面试题参考答案

## 1. HashMap / ConcurrentHashMap / AQS / HashSet 与相关并发工具

### 要点速览 · 1

- `HashMap` 数组+链表/红黑树，线程不安全；`ConcurrentHashMap` 分段锁→CAS；`HashSet` 基于 `HashMap`。
- AQS 提供模板化同步器；`synchronized`、`ReentrantLock`、`CopyOnWriteArrayList` 分别适配不同场景。
- 并发结构选型取决于冲突概率、读写比例、迭代需求。

### 基础要点 · 1

- **HashMap**：底层是数组+链表/红黑树，默认加载因子 0.75。`put` 通过 key hash 定位桶位，桶位冲突时形成链表，链表长度超过 8 且容量 ≥64 时转红黑树。
- **HashSet**：内部将元素作为 `HashMap` 的 key，value 为常量 `PRESENT`，因此所有行为复用 `HashMap`。
- **synchronized**：JVM 级别的内置锁，支持偏向锁、轻量级锁、重量级锁的自适应优化。

### 进阶扩展 · 1

- **ConcurrentHashMap**：JDK7 分段锁（Segment），JDK8 采用 `CAS + synchronized` 在桶位粒度控制，链表转树同样触发条件。读操作基本无锁，写操作竞争点较少。
- **AQS(AbstractQueuedSynchronizer)**：维护 `state` 和 FIFO 队列，提供 `acquire/release` 模板方法。`ReentrantLock`、`CountDownLatch`、`Semaphore` 等均基于 AQS。
- **ReentrantLock**：可公平/非公平、可中断、可定时、可配合条件变量。底层依赖 AQS 的可重入 state 计数。
- **CopyOnWriteArrayList**：写时复制，适合读多写少且迭代快照一致性需求。

### ⚠️注意事项 · 1

- HashMap 在多线程扩容可能导致环形链表死循环，绝不能直接共享。
- ConcurrentHashMap 迭代弱一致，不保证实时视图；需要强一致时考虑加锁或快照。
- CopyOnWrite 类在写多场景下开销巨大（复制数组），及时回收旧数组避免内存压力。

## 2. Redis 数据类型与场景

### 要点速览 · 2

- 常用五大类型：String、Hash、List、Set、ZSet。
- 扩展类型：Bitmap、HyperLogLog、Geo、Stream。
- 场景选型基于数据结构特点。

### 基础要点 · 2

- **String**：二进制安全，可存 JSON、计数器。典型场景：缓存对象、分布式锁、限流计数。
- **Hash**：类似字典，适合存用户信息、配置项等结构化数据。
- **List**：双端链表，用于消息队列、任务队列（`LPUSH`/`BRPOP`）。
- **Set**：无序去重集合，用于标签、好友关系、抽奖。
- **ZSet**：有序集合，成员分数排序，适合排行榜、延迟队列。

### 进阶扩展 · 2

- **Bitmap**：位图，适合签到、活跃用户标记；1 bit 表示一个状态。
- **HyperLogLog**：估算基数，适合 UV 统计，误差约 0.81%。
- **Geo**：地理位置，查询附近地点。
- **Stream**：消息队列，支持消费组、可靠消费。

### ⚠️注意事项 · 2

- 选择数据结构时考虑内存占用与操作复杂度，避免误用 ZSet 做大宽表。
- Hash 内部字段过多会与 String 体积相差无几，需要设置 `hash-max-ziplist-entries/values`。
- Stream 需要定期 `XDEL`/`XTRIM` 避免无限增长。

## 3. JVM 内存模型 (JMM)

### 要点速览 · 3

- 逻辑内存划分：堆、方法区、栈、本地方法栈、程序计数器。
- JMM 关注线程可见性、有序性、原子性。
- `volatile`、`synchronized`、`final` 等提供内存语义保障。

### 基础要点 · 3

- **堆**：对象实例存储，含新生代（Eden+两个 Survivor）与老年代。
- **方法区**：类元数据、常量、静态变量（HotSpot 对应 Metaspace）。
- **虚拟机栈**：栈帧保存局部变量、操作数栈。
- **程序计数器**：记录当前线程执行字节码行号。

### 进阶扩展 · 3

- JMM 定义主内存与工作内存，线程操作需遵循 `load/store/use/assign` 规则。
- **`volatile`**：禁止指令重排，写入后刷新主内存，读操作直接从主内存获取。
- **Happens-Before**：程序次序、监视器锁、volatile、线程启动/终止、`final` 字段发布、传递性。
- 垃圾收集器（G1、ZGC）结合内存区域优化暂停时间。

### ⚠️注意事项 · 3

- `volatile` 仅保证可见性与有序性，不保证复合操作原子。
- 栈溢出与堆溢出诊断方法不同，栈通过 `-Xss`，堆通过 `-Xmx/-Xms`。
- 不恰当的 `finalize` 使用会增加 GC 压力。

## 4. 新建类的 JVM 流程

### 要点速览 · 4

- 类加载生命周期：加载→验证→准备→解析→初始化。
- 类加载器委派模型：Bootstrap→Extension→Application。
- 初始化阶段执行 `<clinit>`，实例化触发 `<init>`。

### 基础要点 · 4

- **加载**：读取 class 字节流，生成字节数组。
- **验证**：文件格式、元数据、字节码、符号引用合法性。
- **准备**：为静态变量分配内存、设默认值。
- **解析**：符号引用替换为直接引用。
- **初始化**：执行 `<clinit>`，按声明顺序赋初值。

### 进阶扩展 · 4

- 类加载器自定义需重写 `findClass`，遵循双亲委派；可破坏委派应谨慎。
- 动态代理、SPI 利用线程上下文类加载器绕过双亲委派。
- `new` 执行：类已加载→分配内存（TLAB/堆）→零值初始化→执行 `<init>`→返回引用。

### ⚠️注意事项 · 4

- `<clinit>` 中使用未初始化类（循环依赖）会触发 `ExceptionInInitializerError`。
- 多线程类初始化，JVM 用 `init_lock` 保证仅一次；避免在静态块内做耗时 IO。
- 类卸载仅发生在自定义 ClassLoader 无引用且相关类无实例，谨防类加载泄漏。

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

## 9. 三高系统设计考量

### 要点速览 · 9

- 三高：高可用、高性能/高并发、高可扩展。
- 架构分层、容量规划、降级限流。
- 数据一致性与容灾策略。

### 基础要点 · 9

- **高可用**：多活部署、故障转移、健康检查、自动化运维。
- **高性能/高并发**：缓存、异步化、读写分离、负载均衡。
- **高可扩展**：拆分服务、弹性伸缩、无状态服务。

### 进阶扩展 · 9

- **容量规划**：QPS 预测、压测、模型计算 Peak Factor。
- **容灾**：跨机房双活/多活、数据复制、RPO/RTO 指标。
- **一致性**：分布式事务（TCC、SAGA）、幂等、补偿。
- **观测**：埋点监控、链路追踪、灰度发布、熔断降级策略。

### ⚠️注意事项 · 9

- 优先解决单点瓶颈，再谈复杂方案。
- 避免过度设计：监控、自动化运维是落地关键。
- 防止缓存雪崩/穿透，设计预热、限流、降级策略。

## 10. OpenFeign 远程调用原理

### 要点速览 · 10

- 基于动态代理生成 HTTP 客户端。
- 与 Ribbon/LoadBalancer、Hystrix/Resilience4j 集成。
- 支持契约与编码器/解码器扩展。

### 基础要点 · 10

- 接口上标注 `@FeignClient`，Spring 在启动时创建代理。
- 代理调用时构造请求：解析注解→拼装 URL→执行 `Client`（默认基于 Apache HttpClient 或 OkHttp）。

### 进阶扩展 · 10

- `FeignClientsRegistrar` 注册 BeanDefinition，`FeignClientFactoryBean` 创建代理。
- `Contract` 解析注解为 `MethodMetadata`，`Encoder/Decoder` 转换请求响应。
- 与 Spring Cloud LoadBalancer 集成实现客户端负载均衡，结合拦截器做统一鉴权、日志。

### ⚠️注意事项 · 10

- 接口方法返回类型要与 Decoder 匹配，避免 `ClassCastException`。
- 默认超时较长，需结合业务设置 `ReadTimeout/ConnectTimeout`。
- 大量并发调用需关注连接池与线程池配置。

## 11. Dubbo 调用原理

### 要点速览 · 11

- 注册中心（Zookeeper、Nacos）服务注册发现。
- 消费端基于动态代理、负载均衡、集群容错。
- 序列化、网络协议支持可插拔。

### 基础要点 · 11

- Provider 启动后暴露服务，注册到注册中心；Consumer 订阅服务列表。
- 消费方调用代理→Invoker→Protocol→Client（如 Netty）。

### 进阶扩展 · 11

- **协议**：Dubbo 协议（TCP + Hessian2），支持多协议（gRPC、REST）。
- **负载均衡**：随机、轮询、一致性哈希、最少活跃。
- **容错策略**：Failover、Failfast、Failsafe、Failback、Forking。
- **SPI**：Dubbo 扩展机制，基于自定义 ClassLoader 与包装类。

### ⚠️注意事项 · 11

- 注册中心不可用时，Consumer 使用本地缓存；确保缓存刷新策略。
- 版本、分组隔离避免接口冲突。
- 监控（Dubbo Admin、Metrics）对容量治理至关重要。

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

## 17. 常见设计模式

### 要点速览 · 17

- 工厂、适配器、代理、模板、策略、责任链核心意图。
- 结合场景说明使用时机。
- 注意与框架实现的联系。

### 基础要点 · 17

- **工厂模式**：隐藏对象创建（Spring IoC 容器、`FactoryBean`）。
- **适配器模式**：接口转换（`HandlerAdapter`, JDBC 驱动）。
- **代理模式**：控制访问、增强（Spring AOP、MyBatis Mapper）。
- **模板方法**：定义算法骨架，子类实现（`JdbcTemplate`）。
- **策略模式**：封装变化算法（支付渠道、序列化）。
- **责任链模式**：多个处理器顺序处理（Servlet Filter、Netty Pipeline）。

### 进阶扩展 · 17

- 组合使用：如策略 + 工厂动态选择实现。
- 借助枚举/注解实现策略注册，减少 `if/else`。
- 使用责任链处理可扩展需求，如审批流。

### ⚠️注意事项 · 17

- 模式选择应基于问题，不要为模式而模式。
- 责任链需处理终止条件，防止空链。
- 策略注册需防止 Bean 重名或覆盖。

## 18. MySQL 索引失效原因

### 要点速览 · 18

- 函数/表达式包裹列、类型转换导致无法走索引。
- 模糊匹配左模糊、范围条件影响联合索引。
- 统计信息过期、选择度低。

### 基础要点 · 18

- `LIKE '%xxx'` 左模糊无法利用 B+Tree 前缀。
- 对列做运算、`WHERE DATE(create_time)=...` 会导致全表扫描。
- 数据类型不一致触发隐式转换。

### 进阶扩展 · 18

- 联合索引遵循最左前缀；在范围查询后续列失效。
- OR 条件若其中一列无索引总体失效，可拆分 Union。
- 统计信息 stale 使优化器选择错误，可 `ANALYZE TABLE`。

### ⚠️注意事项 · 18

- 注意字符集排序规则影响索引；`ORDER BY` 最好复用索引顺序避免 filesort。
- 长度过大的 `VARCHAR` 建议前缀索引，注意选择度。
- 避免在 `where` 使用 `!=`、`<>`、`IS NULL` 破坏索引。

## 19. 锁类型与 MySQL 行锁/间隙锁/临键锁

### 要点速览 · 19

- 锁分类：乐观/悲观、共享/排它、表锁/行锁。
- InnoDB 行级锁基于索引。
- 间隙锁、临键锁用于防止幻读。

### 基础要点 · 19

- **共享锁(S)**：允许并发读，不允许写。
- **排他锁(X)**：独占访问。
- **行锁**：通过索引记录锁定，避免锁全表。

### 进阶扩展 · 19

- **间隙锁(Gap Lock)**：锁定索引区间，不含记录本身，防止插入。
- **临键锁(Next-Key Lock)**：记录锁 + 间隙锁组合，默认 RR 隔离下用于范围查询。
- **意向锁**：表级锁与行锁协调。
- 锁冲突诊断：`information_schema.innodb_locks`、`performance_schema`。

### ⚠️注意事项 · 19

- 查询未使用索引会退化为表锁。
- 合理使用 `FOR UPDATE`，避免大事务长时间持锁。
- Gap Lock 仅在 RR 下生效；RC 可通过 `binlog_format=ROW` 减少锁范围。

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

## 21. 接口防刷方案设计

### 要点速览 · 21

- 多维限流（IP、账号、设备）。
- 黑白名单、设备指纹、验证码。
- 日志审计、异常监控。

### 基础要点 · 21

- **限流**：单 IP、单用户、单接口滑动窗口；慢速模式。
- **黑名单**：响应式封禁恶意 IP/设备。
- **设备指纹**：收集硬件信息、浏览器指纹。

### 进阶扩展 · 21

- **分层架构**：CDN/WAF 初筛 → 网关限流 → 业务限流。
- **动态规则**：结合行为模型、机器学习识别异常。
- **验证码/滑块**：在阈值内渐进触发。
- **风控闭环**：实时监控→人工复核→策略发布；支持灰度。
- **数据采集**：埋点记录请求频率、成功率、UA、Referer。

### ⚠️注意事项 · 21

- 合法高频用户需白名单或提额。
- 设备指纹涉及隐私合规，遵守 GDPR/个人信息保护。
- 限流失败需兜底页面或降级服务，防止直接 500。

## 22. 40 亿 QQ 号、1GB 内存去重方案

### 要点速览 · 22

- 数据量大、内存限制；考虑分桶 + 位图/外排序。
- 布隆过滤器或位图 + 磁盘辅助。
- 控制误判与资源。

### 基础要点 · 22

- 假设 QQ 号为 32 位整数，可用位图：`40e8` 位 ≈ 5 GB，内存不够。
- 采用分治：对数据按哈希写入多个文件（桶），每个桶容量约 1GB 内可处理。

### 进阶扩展 · 22

- **外部排序**：
  1. 遍历数据使用哈希函数将 QQ 号写入 100 个桶文件（磁盘）。
  2. 每次读取一个桶到内存，用位图或排序+去重，再写回。
- **布隆过滤器**：若允许低误判，可用布隆过滤器+磁盘校验；但需谨慎。
- **压缩位图**：`RoaringBitmap` 可压缩稀疏数据；结合磁盘分片。
- **MapReduce/Hadoop**：分布式去重，内存限制不再是单点问题。

### ⚠️注意事项 · 22

- 分桶数需确保单桶数据量 < 可用内存。
- 处理顺序与磁盘 I/O 成本需优化，使用顺序写入避免随机 I/O。
- 考虑数据倾斜（哈希冲突），可使用二级哈希或动态扩容桶。

## 23. 多线程 HashMap 死循环原因

### 要点速览 · 23

- JDK7 扩容迁移非线程安全，链表节点拆分时可能形成环。
- 线程同时触发 `resize` 导致链表自旋，表现为 CPU 飙升。
- 解决：使用并发容器或加锁，JDK8 改进但仍非线程安全。

### 基础要点 · 23

- HashMap 扩容时将桶内节点移动到新数组，未同步保护。
- 多线程迁移同一桶，`next` 指针被覆盖，形成循环链。
- 死循环体现为 get/put 卡住或 CPU 100%。

### 进阶扩展 · 23

- JDK8 引入尾插与链表树化，但扩容仍非原子；并发写会数据丢失。
- 可通过 `Collections.synchronizedMap`、`ConcurrentHashMap`、`ImmutableMap` 规避。
- 自定义分段锁或使用 `AtomicReference` + CAS 构建无锁结构。

### ⚠️注意事项 · 23

- 不要在多线程环境直接共享可变 HashMap。
- 即使只读，也需在构建后发布时保证可见性（`final` 或安全发布）。
- 面试回答可补充 `computeIfAbsent` 线程安全差异。

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

## 26. MVCC / ReadView / Undo Log / Redo Log / Binlog

### 要点速览 · 26

- MVCC 通过版本链、ReadView 提供快照读。
- Undo log 支持回滚与构建历史版本。
- Redo log 保证崩溃恢复，Binlog 用于主从复制。

### 基础要点 · 26

- InnoDB 行记录包含隐藏列 `trx_id`、`roll_pointer` 构建版本链。
- 快照读生成 ReadView，记录当前活跃事务 ID 列表。
- Undo log 保存旧值；Redo log Write-Ahead 保证持久性；Binlog 顺序记录逻辑操作。

### 进阶扩展 · 26

- ReadView 判定规则：`trx_id` < `up_limit_id` 可见，落在活跃集合不可见。
- Redo log (物理) 与 Binlog (逻辑) 双写，结合形成两阶段提交保证一致性。
- GC: Purge 线程清理不再需要的 Undo log；长事务阻塞清理导致 `history list length` 增长。

### ⚠️注意事项 · 26

- Repeatable Read 下快照读使用同一 ReadView，避免幻读需锁定读。
- 定期监控 redo/buffer 池刷盘压力，避免 `checkpoint age` 膨胀。
- Binlog 模式 (ROW/STATEMENT/MIXED) 影响复制准确性与日志体积。

## 27. 项目中的异步编排

### 要点速览 · 27

- 常见方案：消息队列、`CompletableFuture`、调度编排框架。
- 核心关注点：任务依赖、失败补偿、可观测性。
- 保证幂等与重试机制。

### 基础要点 · 27

- 使用 MQ（Kafka/RabbitMQ）实现解耦，消费者异步处理耗时任务。
- 应用内用线程池+`CompletableFuture`/`@Async` 并行查询。
- 调度系统（xxl-job/Quartz）处理定时任务链。

### 进阶扩展 · 27

- 落地时定义编排 DAG，利用工作流引擎（Camunda、Airflow）处理复杂依赖。
- 结合事件总线与 Saga/TCC 实现跨服务补偿。
- 通过链路追踪、埋点监控异步任务耗时、成功率。

### ⚠️注意事项 · 27

- 控制线程池、消费者速率，避免洪峰拖垮下游。
- 幂等键设计（主键、业务唯一标识）防止重复消费。
- 异步失败需有告警与手动补偿渠道。

## 28. ThreadLocal 在异步多线程环境

### 要点速览 · 28

- ThreadLocal 默认仅限当前线程，异步线程无法继承。
- 线程池复用导致脏数据、内存泄漏。
- 解决：显式传递上下文或使用装饰器。

### 基础要点 · 28

- 线程切换时 ThreadLocal 值不会自动传播。
- 线程池中的线程复用旧值，若未 `remove` 会污染新任务。
- 异步回调需在执行前设值，执行后清理。

### 进阶扩展 · 28

- 使用 `TransmittableThreadLocal`（TTL）配合线程池自动传递上下文。
- Spring `TaskDecorator`、`MdcTaskDecorator` 可封装上下文复制与清理。
- Reactor/Sleuth 提供上下文传播 API（`Context`、`Hook`）。

### ⚠️注意事项 · 28

- 控制 ThreadLocal 储存对象大小，避免 OOM。
- 尽量使用不可变对象或快照，减少并发修改。
- 上下文传递需考虑安全与隐私，避免越权。

## 29. ThreadLocal 使用流程需注意事项

### 要点速览 · 29

- 明确生命周期：初始化、使用、清理。
- 遵循安全发布与访问模式。
- 配合监控及时发现泄漏。

### 基础要点 · 29

- 创建 ThreadLocal 时提供初始值供应器（`withInitial`）。
- 使用完毕执行 `remove`，尤其在线程池场景。
- 值对象需线程封闭，不共享可变引用。

### 进阶扩展 · 29

- 建立统一封装（如 `ThreadLocalContext`）管理 set/remove，提高可维护性。
- 日志 MDC 结合 ThreadLocal，需在过滤器/拦截器中集中清理。
- 配合诊断工具监控 `ThreadLocalMap` 占用，可定期 dump 分析。

### ⚠️注意事项 · 29

- 禁止在 ThreadLocal 存放连接等可复用资源，易造成泄漏。
- 建议配合 try-finally 模式，确保异常情况下也清理。
- 对关键上下文需提供 fallback（如默认租户），防止缺失导致 NPE。
