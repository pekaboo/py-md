# 如何对 Java 的垃圾回收进行调优？

**难度**：中等

**创建时间**：2025-10-06 15:44:35

## 答案
对 Java 的垃圾回收（GC）进行调优是优化应用性能、减少停顿时间、提升吞吐量的关键手段。调优的核心在于根据应用特性（如内存占用、响应时间要求、对象分配频率等）选择合适的 GC 算法，并通过参数调整优化 GC 行为。以下是详细的调优方法和实践建议：

---

### **一、明确调优目标**
在开始调优前，需明确以下目标：
1. **低延迟（Low Latency）**：适用于实时系统（如金融交易），要求 GC 停顿时间短（<100ms）。
2. **高吞吐量（High Throughput）**：适用于批处理任务，要求单位时间内完成更多任务。
3. **内存占用最小化**：适用于内存受限环境（如嵌入式设备）。

**示例场景**：
- 电商网站：优先低延迟，避免用户操作卡顿。
- 大数据分析：优先高吞吐量，快速完成计算任务。

---

### **二、选择合适的 GC 算法**
Java 提供了多种 GC 算法，需根据应用场景选择：

| **GC 算法**       | **适用场景**                          | **特点**                                                                 |
|-------------------|---------------------------------------|--------------------------------------------------------------------------|
| **Serial GC**     | 单核 CPU、小内存应用（如嵌入式设备）  | 单线程收集，停顿时间长，但简单高效。                                     |
| **Parallel GC**   | 后台任务、批处理（高吞吐量优先）      | 多线程并行收集，吞吐量高，但停顿时间较长（适合可接受长停顿的场景）。     |
| **CMS（并发标记清除）** | 低延迟应用（如 Web 服务）            | 并发收集，停顿时间短，但易产生碎片，需配合 `-XX:+UseCMSInitiatingOccupancyOnly` 避免过早/过晚触发。 |
| **G1 GC**         | 大内存应用（>4GB）、平衡型场景        | 分代收集，将堆划分为 Region，优先回收高价值区域，停顿时间可控（<200ms）。 |
| **ZGC/Shenandoah**| 超低延迟应用（如金融交易）           | 基于 Region 的并发压缩收集，停顿时间极短（<10ms），但可能影响吞吐量。   |

**推荐选择**：
- 默认情况下，Java 8+ 使用 **Parallel GC**（吞吐量优先）。
- 若需低延迟，优先尝试 **G1 GC**（Java 9+ 默认），或升级到 **ZGC**（Java 11+ 实验性支持，Java 15+ 正式）。

---

### **三、关键调优参数**
#### **1. 堆内存设置**
- **`-Xms` 和 `-Xmx`**：设置初始堆大小和最大堆大小。
  - **建议**：将两者设为相同值（如 `-Xms4g -Xmx4g`），避免动态调整带来的性能开销。
  - **公式**：堆大小 ≈ 最大并发线程数 × 每个线程栈大小（默认 1MB） + 年轻代/老年代预留空间。

- **`-XX:NewRatio`**：设置老年代与年轻代的比例（默认 2，即老年代:年轻代=2:1）。
  - **调整**：若对象存活率高，增大老年代比例（如 `-XX:NewRatio=3`）。

- **`-XX:SurvivorRatio`**：设置 Eden 区与 Survivor 区的比例（默认 8，即 Eden:Survivor=8:1）。
  - **调整**：若对象晋升频繁，增大 Survivor 区（如 `-XX:SurvivorRatio=6`）。

#### **2. 年轻代调优**
- **`-Xmn`**：直接设置年轻代大小（优先级高于 `NewRatio`）。
  - **建议**：年轻代大小 ≈ 堆大小 × 1/3 ~ 1/2。
  - **示例**：`-Xmx8g -Xmn4g`。

- **`-XX:MaxTenuringThreshold`**：设置对象晋升到老年代的年龄阈值（默认 15）。
  - **调整**：若对象存活周期短，降低阈值（如 `-XX:MaxTenuringThreshold=5`）；若对象长期存活，提高阈值。

#### **3. GC 日志与分析**
- **启用 GC 日志**：
  ```bash
  -Xloggc:/path/to/gc.log -XX:+PrintGCDetails -XX:+PrintGCDateStamps
  ```
  - **工具分析**：使用 `GCViewer`、`GCEasy` 或 `VisualVM` 可视化日志，识别频繁 Full GC 或长停顿。

#### **4. 并发标记参数（CMS/G1）**
- **`-XX:CMSInitiatingOccupancyFraction`**：CMS 触发并发标记的堆占用率（默认 68%）。
  - **调整**：若过早触发，增大值（如 `-XX:CMSInitiatingOccupancyFraction=75`）；若过晚触发，减小值。

- **`-XX:G1HeapRegionSize`**：G1 的 Region 大小（默认堆大小/2048，范围 1MB~32MB）。
  - **调整**：若对象大小分布不均，手动设置 Region 大小（如 `-XX:G1HeapRegionSize=4M`）。

#### **5. 其他参数**
- **`-XX:+DisableExplicitGC`**：禁用 `System.gc()` 调用，避免手动触发 Full GC。
- **`-XX:+UseStringDeduplication`**：G1 字符串去重（Java 8u20+），减少字符串内存占用。
- **`-XX:+HeapDumpOnOutOfMemoryError`**：OOM 时生成堆转储文件，便于分析内存泄漏。

---

### **四、调优实践步骤**
1. **基准测试**：使用 JMeter 或 Gatling 模拟生产负载，记录 GC 日志。
2. **分析日志**：识别频繁 Full GC、长停顿或内存泄漏。
3. **调整参数**：
   - 若 Young GC 频繁：增大年轻代（`-Xmn`）或 Eden 区（`-XX:SurvivorRatio`）。
   - 若 Full GC 频繁：增大堆大小（`-Xmx`）或调整晋升阈值（`-XX:MaxTenuringThreshold`）。
   - 若停顿时间过长：切换到 G1/ZGC，或调整并发标记参数。
4. **验证效果**：再次测试并对比 GC 日志，确认指标改善。

---

### **五、常见问题与解决方案**
#### **1. 频繁 Full GC**
- **原因**：内存泄漏、老年代空间不足、大对象直接分配到老年代。
- **解决方案**：
  - 使用 `jmap -histo:live <pid>` 分析对象分布。
  - 增大堆大小或调整 `-XX:NewRatio`。
  - 启用 `-XX:+PrintPromotionFailure` 检查晋升失败。

#### **2. Young GC 停顿时间长**
- **原因**：年轻代过大、Survivor 区不足。
- **解决方案**：
  - 减小年轻代大小（`-Xmn`）。
  - 调整 `-XX:SurvivorRatio` 或 `-XX:MaxTenuringThreshold`。

#### **3. 并发模式失败（CMS）**
- **现象**：日志中出现 `Concurrent Mode Failure`。
- **原因**：CMS 收集期间老年代空间不足。
- **解决方案**：
  - 增大老年代空间（调整 `-XX:NewRatio`）。
  - 降低 `-XX:CMSInitiatingOccupancyFraction` 提前触发并发标记。

---

### **六、示例配置**
#### **场景 1：低延迟 Web 服务（G1 GC）**
```bash
java -Xms4g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 \
     -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=4M \
     -Xloggc:/var/log/gc.log -XX:+PrintGCDetails -jar app.jar
```

#### **场景 2：高吞吐量批处理（Parallel GC）**
```bash
java -Xms8g -Xmx8g -XX:+UseParallelGC -XX:ParallelGCThreads=4 \
     -XX:NewRatio=2 -XX:SurvivorRatio=8 -jar batch.jar
```

---

### **七、总结**
1. **选择 GC 算法**：根据延迟/吞吐量需求选择 Parallel GC、G1 或 ZGC。
2. **设置堆内存**：固定 `-Xms` 和 `-Xmx`，避免动态调整。
3. **调整代大小**：通过 `-Xmn`、`NewRatio`、`SurvivorRatio` 优化年轻代/老年代比例。
4. **监控与分析**：启用 GC 日志，使用工具定位问题。
5. **迭代调优**：根据测试结果逐步调整参数，避免过度优化。

**最终建议**：优先使用 G1 GC（Java 11+），它结合了低延迟和高吞吐量的优势，且参数调优相对简单。对于超低延迟场景，可评估 ZGC 或 Shenandoah。
