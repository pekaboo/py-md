# 常用的 JVM 配置参数有哪些？

**难度**：中等

**创建时间**：2025-10-06 15:45:04

## 答案
JVM（Java虚拟机）的配置参数对程序的性能、稳定性和资源利用率有重要影响。以下是常用的JVM配置参数分类及说明，涵盖内存管理、垃圾回收、线程调优、日志分析等关键场景。

---

### **一、内存相关参数**
#### 1. **堆内存（Heap）**
- **`-Xms<size>`**：设置堆的初始大小（如 `-Xms512m`）。  
  **作用**：避免启动时频繁扩容，减少GC次数。
- **`-Xmx<size>`**：设置堆的最大大小（如 `-Xmx2g`）。  
  **作用**：限制JVM最大内存，防止OOM（Out of Memory）。
- **`-Xmn<size>`**：设置年轻代大小（如 `-Xmn256m`）。  
  **作用**：年轻代过大会导致老年代GC频繁，过小会导致Minor GC频繁。
- **`-XX:NewRatio=<n>`**：年轻代与老年代的比例（默认 `2`，即年轻代:老年代=1:2）。  
  **作用**：调整两代内存分配比例。
- **`-XX:SurvivorRatio=<n>`**：Eden区与Survivor区的比例（默认 `8`，即Eden:Survivor=8:1:1）。  
  **作用**：控制对象在年轻代的分配策略。

#### 2. **非堆内存（Non-Heap）**
- **`-XX:MetaspaceSize=<size>`**：元空间初始大小（如 `-XX:MetaspaceSize=128m`）。  
  **作用**：替代PermGen（永久代），存储类元数据。
- **`-XX:MaxMetaspaceSize=<size>`**：元空间最大大小（如 `-XX:MaxMetaspaceSize=512m`）。  
  **作用**：防止元空间无限增长导致OOM。
- **`-Xss<size>`**：设置线程栈大小（如 `-Xss256k`）。  
  **作用**：控制每个线程的栈内存，过大会导致线程数减少。

---

### **二、垃圾回收（GC）相关参数**
#### 1. **GC算法选择**
- **`-XX:+UseSerialGC`**：使用串行GC（单线程，适合小型应用）。  
- **`-XX:+UseParallelGC`**：并行GC（多线程，吞吐量优先，默认在Server模式）。  
- **`-XX:+UseConcMarkSweepGC`**：CMS GC（并发标记清除，低延迟，JDK 9+已废弃）。  
- **`-XX:+UseG1GC`**：G1 GC（分区收集，平衡吞吐量和延迟，JDK 9+默认）。  
- **`-XX:+UseZGC`**：ZGC（超低延迟，JDK 11+引入，适合大内存场景）。  
- **`-XX:+UseShenandoahGC`**：Shenandoah GC（并发压缩，OpenJDK特有）。

#### 2. **GC调优参数**
- **`-XX:MaxGCPauseMillis=<n>`**：目标最大GC停顿时间（G1/ZGC适用）。  
  **示例**：`-XX:MaxGCPauseMillis=200` 表示希望GC停顿不超过200ms。
- **`-XX:GCTimeRatio=<n>`**：GC时间与总时间的比例（Parallel GC适用）。  
  **示例**：`-XX:GCTimeRatio=4` 表示GC时间不超过总时间的1/5。
- **`-XX:InitiatingHeapOccupancyPercent=<n>`**：触发GC的堆占用百分比（G1适用）。  
  **示例**：`-XX:InitiatingHeapOccupancyPercent=45` 表示堆使用45%时触发Mixed GC。

---

### **三、日志与监控参数**
#### 1. **GC日志**
- **`-Xloggc:<file>`**：指定GC日志文件路径（如 `-Xloggc:/var/log/jvm/gc.log`）。  
- **`-XX:+PrintGCDetails`**：打印GC详细信息（如年轻代/老年代回收情况）。  
- **`-XX:+PrintGCDateStamps`**：在GC日志中添加时间戳。  
- **统一日志配置（JDK 9+）**：  
  ```bash
  -Xlog:gc*:file=/var/log/jvm/gc.log:time,uptime,level,tags:filecount=5,filesize=10m
  ```
  **作用**：按时间、级别等标签输出GC日志，并限制文件数量和大小。

#### 2. **OOM日志**
- **`-XX:+HeapDumpOnOutOfMemoryError`**：OOM时生成堆转储文件（`.hprof`）。  
- **`-XX:HeapDumpPath=<path>`**：指定堆转储文件路径（如 `-XX:HeapDumpPath=/tmp`）。

---

### **四、线程与系统参数**
#### 1. **线程栈**
- **`-Xss<size>`**：设置线程栈大小（如 `-Xss1m`）。  
  **注意**：栈过小会导致`StackOverflowError`，过大则减少线程数。

#### 2. **并行线程数**
- **`-XX:ParallelGCThreads=<n>`**：并行GC的线程数（默认与CPU核心数相关）。  
- **`-XX:ConcGCThreads=<n>`**：并发GC的线程数（如G1的并发标记线程）。

#### 3. **系统属性**
- **`-D<name>=<value>`**：设置系统属性（如 `-Dfile.encoding=UTF-8`）。  
  **常见用途**：配置日志路径、数据库连接等。

---

### **五、高级调优参数**
#### 1. **JIT编译**
- **`-XX:+TieredCompilation`**：启用分层编译（默认开启，混合C1/C2编译器）。  
- **`-XX:CompileThreshold=<n>`**：触发JIT编译的阈值（方法调用次数）。

#### 2. **内存分配策略**
- **`-XX:+AlwaysPreTouch`**：启动时预分配所有堆内存（减少运行时内存申请开销）。  
  **适用场景**：对延迟敏感的应用（如金融交易系统）。
- **`-XX:+UseLargePages`**：使用大页内存（减少TLB缺失，提升性能）。  
  **注意**：需操作系统支持（如Linux的`hugepages`）。

#### 3. **安全点（Safepoint）**
- **`-XX:+UseCountedLoopSafepoints`**：在循环中插入安全点（避免长循环阻塞GC）。  
  **作用**：减少GC停顿时的等待时间。

---

### **六、常用参数组合示例**
#### 1. **通用生产环境配置**
```bash
java -Xms2g -Xmx2g -Xmn512m \
     -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m \
     -XX:+UseG1GC -XX:MaxGCPauseMillis=200 \
     -Xloggc:/var/log/jvm/gc.log -XX:+PrintGCDetails \
     -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp \
     -Dfile.encoding=UTF-8 -jar app.jar
```

#### 2. **低延迟场景（如金融交易）**
```bash
java -Xms4g -Xmx4g -Xss256k \
     -XX:+UseZGC -XX:MaxGCPauseMillis=10 \
     -XX:+AlwaysPreTouch -XX:+UseLargePages \
     -Xlog:gc*:file=/var/log/jvm/gc.log:time,uptime:filecount=10,filesize=50m \
     -jar trading-system.jar
```

---

### **七、参数查看与验证**
1. **查看默认参数**：  
   ```bash
   java -XX:+PrintFlagsFinal -version
   ```
2. **运行时动态修改**（需启用JMX或`jcmd`）：  
   ```bash
   jcmd <pid> VM.set_flag <flag> <value>
   ```

---

### **总结表**
| **分类**       | **常用参数**                                                                 |
|----------------|-----------------------------------------------------------------------------|
| **堆内存**     | `-Xms`, `-Xmx`, `-Xmn`, `-XX:NewRatio`, `-XX:SurvivorRatio`               |
| **非堆内存**   | `-XX:MetaspaceSize`, `-XX:MaxMetaspaceSize`, `-Xss`                        |
| **GC算法**     | `-XX:+UseG1GC`, `-XX:+UseZGC`, `-XX:+UseParallelGC`                       |
| **GC调优**     | `-XX:MaxGCPauseMillis`, `-XX:GCTimeRatio`, `-XX:InitiatingHeapOccupancyPercent` |
| **日志监控**   | `-Xloggc`, `-XX:+PrintGCDetails`, `-XX:+HeapDumpOnOutOfMemoryError`       |
| **线程**       | `-Xss`, `-XX:ParallelGCThreads`, `-XX:ConcGCThreads`                       |
| **高级**       | `-XX:+AlwaysPreTouch`, `-XX:+UseLargePages`, `-XX:+TieredCompilation`    |

**建议**：  
1. 根据应用类型（吞吐量型/低延迟型）选择GC算法。  
2. 通过监控工具（如Prometheus + Grafana）分析GC日志，动态调整参数。  
3. 避免盲目设置大内存，需结合实际负载测试。
