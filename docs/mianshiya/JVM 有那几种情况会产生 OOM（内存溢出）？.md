# JVM 有那几种情况会产生 OOM（内存溢出）？

**难度**：中等

**创建时间**：2025-10-06 15:47:13

## 答案
JVM 在运行过程中可能因多种原因导致内存溢出（OOM, Out Of Memory），这些情况通常与内存区域分配不当或资源耗尽有关。以下是 JVM 中常见的 OOM 场景及其原因分析：

---

### **1. Java 堆内存溢出（Heap OOM）**
- **原因**：对象不断创建且未被回收，堆内存（Heap）耗尽。
- **典型场景**：
  - 内存泄漏：对象被长期持有（如静态集合、未关闭的连接）。
  - 分配过大对象：直接创建超过堆容量的数组或集合。
  - 堆设置过小：`-Xms` 和 `-Xmx` 参数配置不合理。
- **异常信息**：
  ```java
  java.lang.OutOfMemoryError: Java heap space
  ```
- **示例代码**：
  ```java
  List<byte[]> list = new ArrayList<>();
  while (true) {
      list.add(new byte[1024 * 1024]); // 持续分配1MB数组
  }
  ```
- **解决方案**：
  - 使用 `jmap -histo:live <pid>` 分析对象占用。
  - 检查内存泄漏（如静态集合、未关闭的资源）。
  - 调整堆大小：`-Xms512m -Xmx2g`。

---

### **2. 方法区/元空间溢出（Metaspace OOM）**
- **原因**：类元数据（元空间，Metaspace）或永久代（PermGen，JDK 8 之前）内存耗尽。
- **典型场景**：
  - 动态生成大量类（如 CGLIB 代理、ASM 字节码操作）。
  - 加载过多 JAR 或类文件（如 Spring Boot 的 `@ComponentScan` 范围过大）。
  - 元空间设置过小：`-XX:MaxMetaspaceSize` 参数配置不合理。
- **异常信息**：
  ```java
  java.lang.OutOfMemoryError: Metaspace
  // 或 JDK 8 之前的 PermGen
  java.lang.OutOfMemoryError: PermGen space
  ```
- **示例代码**：
  ```java
  while (true) {
      Enhancer enhancer = new Enhancer();
      enhancer.setSuperclass(Object.class);
      enhancer.setCallback(NoOp.INSTANCE);
      enhancer.create(); // 动态生成类
  }
  ```
- **解决方案**：
  - 调整元空间大小：`-XX:MaxMetaspaceSize=256m`。
  - 减少动态类生成（如优化 CGLIB 使用）。

---

### **3. 栈溢出（Stack Overflow）**
- **原因**：方法调用层次过深或栈帧过大，导致栈内存耗尽。
- **典型场景**：
  - 无限递归（未设置终止条件）。
  - 栈大小设置过小：`-Xss` 参数配置不合理。
- **异常信息**：
  ```java
  java.lang.StackOverflowError
  ```
- **示例代码**：
  ```java
  public void recursiveCall() {
      recursiveCall(); // 无限递归
  }
  ```
- **解决方案**：
  - 检查递归逻辑，确保有终止条件。
  - 调整栈大小：`-Xss2m`（默认通常为 256KB~1MB）。

---

### **4. 直接内存溢出（Direct Buffer OOM）**
- **原因**：通过 `ByteBuffer.allocateDirect()` 分配的堆外内存（Direct Memory）耗尽。
- **典型场景**：
  - 频繁分配大块直接内存（如 Netty 的 `ByteBuf`）。
  - 未显式释放直接内存（依赖 GC 回收，但回收时机不确定）。
  - 直接内存限制过小：`-XX:MaxDirectMemorySize` 参数配置不合理。
- **异常信息**：
  ```java
  java.lang.OutOfMemoryError: Direct buffer memory
  ```
- **示例代码**：
  ```java
  while (true) {
      ByteBuffer.allocateDirect(1024 * 1024); // 分配1MB直接内存
  }
  ```
- **解决方案**：
  - 显式释放直接内存（如调用 `Cleaner` 或复用 `ByteBuf`）。
  - 调整直接内存大小：`-XX:MaxDirectMemorySize=512m`。

---

### **5. 本地内存溢出（Native Memory OOM）**
- **原因**：JVM 进程的本地内存（非堆内存，如线程栈、JNI 分配的内存）耗尽。
- **典型场景**：
  - 创建过多线程（每个线程默认占用 1MB 栈内存）。
  - JNI 调用分配大量本地内存（如 C/C++ 代码内存泄漏）。
  - 操作系统对进程内存限制（如 `ulimit` 或容器内存限制）。
- **异常信息**：
  ```java
  java.lang.OutOfMemoryError: unable to create new native thread
  // 或操作系统级错误（如 Linux 的 "Cannot allocate memory"）
  ```
- **示例代码**：
  ```java
  while (true) {
      new Thread(() -> {
          try { Thread.sleep(Long.MAX_VALUE); } catch (InterruptedException e) {}
      }).start(); // 创建大量线程
  }
  ```
- **解决方案**：
  - 减少线程数量，使用线程池。
  - 检查 JNI 代码是否存在内存泄漏。
  - 调整操作系统或容器内存限制。

---

### **6. GC 开销过大（GC Overhead Limit）**
- **原因**：JVM 花费过多时间在 GC 上（默认超过 98% 时间用于 GC 且回收不足 2% 内存）。
- **典型场景**：
  - 堆中存活对象过多，导致频繁 Full GC。
  - 内存碎片化严重（如使用 CMS 收集器）。
- **异常信息**：
  ```java
  java.lang.OutOfMemoryError: GC overhead limit exceeded
  ```
- **解决方案**：
  - 优化对象生命周期（减少长生命周期对象）。
  - 更换 GC 算法（如 G1 或 ZGC）。
  - 调整堆大小或分代比例（如 `-XX:NewRatio=2`）。

---

### **总结与排查建议**
| **OOM 类型**       | **关键参数**               | **排查工具**               |
|---------------------|---------------------------|---------------------------|
| 堆内存溢出          | `-Xms`, `-Xmx`            | `jmap`, `jstat`           |
| 元空间溢出          | `-XX:MaxMetaspaceSize`   | `jcmd <pid> VM.metaspace` |
| 栈溢出              | `-Xss`                    | 线程转储（`jstack`）       |
| 直接内存溢出        | `-XX:MaxDirectMemorySize`| `Native Memory Tracking`  |
| 本地内存溢出        | 操作系统限制              | `pmap`, `top`             |
| GC 开销过大          | GC 算法配置              | `-Xlog:gc*`               |

**通用排查步骤**：
1. **捕获异常堆栈**：确认 OOM 类型和发生位置。
2. **分析内存使用**：使用 `jmap -histo` 或 `VisualVM`。
3. **检查 GC 日志**：启用 `-Xlog:gc*:file=gc.log`。
4. **监控系统资源**：使用 `top`、`nmon` 或容器监控工具。

通过合理配置 JVM 参数和优化代码逻辑，可以有效避免或快速定位 OOM 问题。
