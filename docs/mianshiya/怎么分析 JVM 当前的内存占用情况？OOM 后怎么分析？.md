# 怎么分析 JVM 当前的内存占用情况？OOM 后怎么分析？

**难度**：困难

**创建时间**：2025-10-06 15:48:09

## 答案
分析JVM内存占用和排查OOM（OutOfMemoryError）是性能调优和故障排查的关键技能。以下是系统化的分析方法和工具使用指南：

---

### **一、分析JVM当前内存占用**
#### **1. 基础命令行工具**
- **`jstat`**：监控GC和内存区域使用情况
  ```bash
  jstat -gc <pid> 1s  # 每1秒刷新一次
  ```
  输出示例：
  ```
  S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU
  2048.0 2048.0 0.0    1024.0  16384.0  8192.0    40960.0    20480.0   51200.0 49152.0
  ```
  - **关键指标**：
    - `EU`（Eden区使用量）、`OU`（老年代使用量）、`MC`（元空间容量）

- **`jmap`**：查看堆内存快照
  ```bash
  jmap -heap <pid>       # 显示堆内存配置和各区域使用
  jmap -histo <pid>      # 显示对象统计（按类排序）
  jmap -dump:format=b,file=heap.hprof <pid>  # 生成堆转储文件
  ```

- **`jcmd`**：多功能诊断工具
  ```bash
  jcmd <pid> VM.flags      # 查看JVM启动参数
  jcmd <pid> GC.heap_info  # 显示堆内存摘要
  ```

#### **2. 可视化工具**
- **VisualVM**：
  - 连接JVM后查看"Monitor"标签页的堆/元空间使用曲线
  - 使用"Visual GC"插件实时观察各代内存变化

- **JConsole**：
  - 监控"内存"标签页的堆/非堆内存使用趋势
  - 触发手动GC观察内存回收情况

- **Arthas**（阿里开源工具）：
  ```bash
  heapdump /tmp/heap.hprof  # 生成堆转储
  dashboard                 # 实时监控内存和GC
  ```

#### **3. 关键监控指标**
| **区域**       | **监控指标**                     | **危险阈值**               |
|----------------|----------------------------------|----------------------------|
| **堆内存**     | 已用/总容量（Used/Committed）   | 持续>80%且GC后不下降       |
| **元空间**     | 已用/总容量                     | 频繁Full GC或增长至Max     |
| **GC频率**     | Minor GC/Full GC次数            | Full GC每小时>3次          |
| **GC耗时**     | 单次GC暂停时间                  | 超过应用SLA要求（如>200ms）|

---

### **二、OOM后分析流程**
#### **1. 确认OOM类型**
JVM可能抛出多种OOM错误，需先定位类型：
```java
java.lang.OutOfMemoryError: Java heap space       # 堆内存不足
java.lang.OutOfMemoryError: Metaspace            # 元空间不足
java.lang.OutOfMemoryError: Direct buffer memory  # 堆外内存不足
java.lang.OutOfMemoryError: Unable to create new native thread  # 线程过多
```

#### **2. 获取诊断文件**
- **自动生成**：
  - 添加JVM参数自动生成堆转储和GC日志：
    ```bash
    -XX:+HeapDumpOnOutOfMemoryError 
    -XX:HeapDumpPath=/tmp/
    -Xloggc:/tmp/gc.log -XX:+PrintGCDetails
    ```

- **手动获取**：
  ```bash
  jmap -dump:format=b,file=oom.hprof <pid>  # 强制生成堆转储
  jstack <pid> > thread.log                 # 获取线程栈
  ```

#### **3. 分析工具**
- **MAT（Memory Analyzer Tool）**：
  1. 导入`.hprof`文件
  2. 查看"Leak Suspects"报告（自动分析内存泄漏）
  3. 检查大对象路径（Dominator Tree）
  4. 分析对象引用链（Path to GC Roots）

- **Eclipse Memory Analyzer**：
  - 识别重复字符串、缓存未清理等常见问题
  - 对比多个堆转储文件观察内存增长趋势

- **jhat**（JDK自带，轻量级）：
  ```bash
  jhat oom.hprof  # 启动Web服务分析堆转储
  ```

#### **4. 典型问题排查**
**案例1：堆内存OOM**
- **现象**：`Java heap space`错误，堆使用率持续100%
- **分析步骤**：
  1. 用MAT检查"Problem Suspects"
  2. 查找占用最高的类（如`HashMap`、`byte[]`）
  3. 检查是否因缓存未设置大小限制（如Guava Cache）
  4. 确认是否存在内存泄漏（如静态集合持续添加）

**案例2：元空间OOM**
- **现象**：`Metaspace`错误，伴随频繁Full GC
- **解决方案**：
  ```bash
  -XX:MaxMetaspaceSize=256m  # 限制元空间大小
  -XX:+UseG1GC               # 改用G1垃圾回收器
  ```

**案例3：线程OOM**
- **现象**：`Unable to create new native thread`
- **检查命令**：
  ```bash
  ps -eLf | grep <pid> | wc -l  # 检查线程数
  ulimit -u                     # 查看系统线程限制
  ```
- **优化方向**：
  - 减少线程池大小
  - 检查是否有死锁导致线程堆积

---

### **三、预防性优化建议**
1. **JVM参数调优**：
   ```bash
   -Xms2g -Xmx2g -Xmn800m       # 堆内存初始/最大值相同避免动态调整
   -XX:MetaspaceSize=128m       # 元空间初始大小
   -XX:MaxDirectMemorySize=512m # 堆外内存限制
   ```

2. **代码层面优化**：
   - 避免`String.intern()`在大量字符串场景使用
   - 及时关闭`ByteBuffer.allocateDirect()`分配的堆外内存
   - 使用弱引用（`WeakReference`）缓存大对象

3. **监控告警**：
   - 设置Prometheus+Grafana监控JVM指标
   - 配置阈值告警（如堆使用>85%持续5分钟）

---

### **四、分析模板（应急检查清单）**
1. [ ] 确认OOM类型（堆/元空间/线程等）
2. [ ] 检查GC日志是否有频繁Full GC
3. [ ] 用`jmap -histo`查看对象数量分布
4. [ ] 用MAT分析堆转储的Leak Suspects
5. [ ] 检查是否有大对象或集合未释放
6. [ ] 验证JVM参数是否合理（Xmx/MetaspaceSize）
7. [ ] 复现问题并监控内存增长趋势

通过系统化的工具使用和结构化分析，可以快速定位内存问题根源。对于生产环境，建议结合APM工具（如SkyWalking、Pinpoint）实现实时内存监控。
