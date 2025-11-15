# 你使用过哪些 Java 并发工具类？

**难度**：中等

**创建时间**：2025-10-06 15:40:13

## 答案
在 Java 并发编程中，工具类提供了线程安全、同步控制和任务调度的核心功能。以下是常用的 Java 并发工具类及其典型应用场景，结合代码示例说明：

---

### **一、核心同步工具类**
#### 1. **`synchronized` 关键字**
   - **作用**：隐式锁，通过方法或代码块同步。
   - **特点**：简单但灵活性低，可能引发线程饥饿。
   - **示例**：
     ```java
     public class Counter {
         private int count = 0;
         public synchronized void increment() {
             count++;
         }
         public synchronized int getCount() {
             return count;
         }
     }
     ```

#### 2. **`ReentrantLock`（可重入锁）**
   - **作用**：显式锁，支持公平锁、超时获取锁、可中断锁。
   - **场景**：需要更灵活的锁控制（如尝试获取锁、公平性）。
   - **示例**：
     ```java
     import java.util.concurrent.locks.ReentrantLock;
     public class LockExample {
         private final ReentrantLock lock = new ReentrantLock();
         public void performTask() {
             lock.lock(); // 获取锁
             try {
                 // 临界区代码
             } finally {
                 lock.unlock(); // 必须释放锁
             }
         }
     }
     ```

#### 3. **`ReadWriteLock`（读写锁）**
   - **作用**：分离读锁（共享）和写锁（独占），提高读多写少场景的性能。
   - **场景**：缓存、配置文件读取等。
   - **示例**：
     ```java
     import java.util.concurrent.locks.ReentrantReadWriteLock;
     public class Cache {
         private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
         private String data;
         public String read() {
             rwLock.readLock().lock();
             try { return data; } finally { rwLock.readLock().unlock(); }
         }
         public void write(String newData) {
             rwLock.writeLock().lock();
             try { data = newData; } finally { rwLock.writeLock().unlock(); }
         }
     }
     ```

---

### **二、线程协作工具类**
#### 1. **`CountDownLatch`（倒计时门闩）**
   - **作用**：等待多个线程完成后再继续执行。
   - **场景**：并行任务汇总、初始化等待。
   - **示例**：
     ```java
     import java.util.concurrent.CountDownLatch;
     public class LatchExample {
         public static void main(String[] args) throws InterruptedException {
             CountDownLatch latch = new CountDownLatch(3);
             for (int i = 0; i < 3; i++) {
                 new Thread(() -> {
                     System.out.println("Task completed");
                     latch.countDown(); // 计数减1
                 }).start();
             }
             latch.await(); // 等待计数归零
             System.out.println("All tasks done");
         }
     }
     ```

#### 2. **`CyclicBarrier`（循环屏障）**
   - **作用**：让多个线程在屏障点等待，全部到达后继续执行。
   - **场景**：多阶段任务同步（如游戏回合）。
   - **示例**：
     ```java
     import java.util.concurrent.CyclicBarrier;
     public class BarrierExample {
         public static void main(String[] args) {
             CyclicBarrier barrier = new CyclicBarrier(3, () -> 
                 System.out.println("All players ready")
             );
             for (int i = 0; i < 3; i++) {
                 new Thread(() -> {
                     try {
                         System.out.println("Player ready");
                         barrier.await(); // 等待其他线程
                     } catch (Exception e) {}
                 }).start();
             }
         }
     }
     ```

#### 3. **`Semaphore`（信号量）**
   - **作用**：控制同时访问资源的线程数量。
   - **场景**：限流、连接池管理。
   - **示例**：
     ```java
     import java.util.concurrent.Semaphore;
     public class SemaphoreExample {
         private final Semaphore semaphore = new Semaphore(2); // 允许2个线程
         public void accessResource() {
             try {
                 semaphore.acquire(); // 获取许可
                 // 访问共享资源
             } catch (InterruptedException e) {}
             finally { semaphore.release(); } // 释放许可
         }
     }
     ```

---

### **三、并发集合类**
#### 1. **`ConcurrentHashMap`**
   - **作用**：线程安全的哈希表，分段锁优化性能。
   - **场景**：高并发读写映射。
   - **示例**：
     ```java
     import java.util.concurrent.ConcurrentHashMap;
     public class ConcurrentMapExample {
         private final ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
         public void update(String key, int value) {
             map.put(key, map.getOrDefault(key, 0) + value);
         }
     }
     ```

#### 2. **`CopyOnWriteArrayList`**
   - **作用**：写时复制的线程安全列表，适合读多写少场景。
   - **场景**：事件监听器列表。
   - **示例**：
     ```java
     import java.util.concurrent.CopyOnWriteArrayList;
     public class CopyOnWriteExample {
         private final CopyOnWriteArrayList<String> listeners = new CopyOnWriteArrayList<>();
         public void addListener(String listener) {
             listeners.add(listener);
         }
         public void notifyListeners() {
             for (String listener : listeners) { // 迭代时无需加锁
                 System.out.println("Notify: " + listener);
             }
         }
     }
     ```

#### 3. **`BlockingQueue`（阻塞队列）**
   - **作用**：线程安全的队列，支持阻塞插入/取出。
   - **子类**：
     - `ArrayBlockingQueue`：固定容量。
     - `LinkedBlockingQueue`：可选容量限制。
     - `PriorityBlockingQueue`：优先级队列。
   - **场景**：生产者-消费者模型。
   - **示例**：
     ```java
     import java.util.concurrent.BlockingQueue;
     import java.util.concurrent.LinkedBlockingQueue;
     public class ProducerConsumer {
         private final BlockingQueue<Integer> queue = new LinkedBlockingQueue<>(10);
         public void produce() throws InterruptedException {
             queue.put(1); // 阻塞直到空间可用
         }
         public int consume() throws InterruptedException {
             return queue.take(); // 阻塞直到有元素
         }
     }
     ```

---

### **四、线程池与任务调度**
#### 1. **`ExecutorService`（线程池）**
   - **作用**：管理线程生命周期，复用线程资源。
   - **子类**：
     - `FixedThreadPool`：固定线程数。
     - `CachedThreadPool`：可伸缩线程数。
     - `ScheduledThreadPool`：定时任务。
   - **示例**：
     ```java
     import java.util.concurrent.ExecutorService;
     import java.util.concurrent.Executors;
     public class ThreadPoolExample {
         public static void main(String[] args) {
             ExecutorService executor = Executors.newFixedThreadPool(3);
             executor.submit(() -> System.out.println("Task running"));
             executor.shutdown(); // 关闭线程池
         }
     }
     ```

#### 2. **`ScheduledExecutorService`（定时任务）**
   - **作用**：延迟或周期性执行任务。
   - **场景**：定时数据同步、心跳检测。
   - **示例**：
     ```java
     import java.util.concurrent.Executors;
     import java.util.concurrent.ScheduledExecutorService;
     import java.util.concurrent.TimeUnit;
     public class ScheduledTask {
         public static void main(String[] args) {
             ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
             scheduler.scheduleAtFixedRate(
                 () -> System.out.println("Periodic task"),
                 0, 1, TimeUnit.SECONDS // 初始延迟0秒，每1秒执行一次
             );
         }
     }
     ```

---

### **五、原子类（`java.util.concurrent.atomic`）**
   - **作用**：基于 CAS（Compare-And-Swap）实现无锁并发。
   - **常用类**：
     - `AtomicInteger`、`AtomicLong`：原子计数器。
     - `AtomicReference`：原子引用。
     - `AtomicBoolean`：原子布尔值。
   - **示例**：
     ```java
     import java.util.concurrent.atomic.AtomicInteger;
     public class AtomicExample {
         private final AtomicInteger counter = new AtomicInteger(0);
         public void increment() {
             counter.incrementAndGet(); // 原子操作
         }
     }
     ```

---

### **六、并发工具类选择指南**
| **场景**                     | **推荐工具类**                     |
|------------------------------|----------------------------------|
| 简单同步                     | `synchronized`                  |
| 灵活锁控制                   | `ReentrantLock`、`ReadWriteLock` |
| 线程间等待                   | `CountDownLatch`、`CyclicBarrier` |
| 资源限流                     | `Semaphore`                     |
| 高并发读写                   | `ConcurrentHashMap`             |
| 生产者-消费者模型           | `BlockingQueue`                 |
| 定时/周期任务               | `ScheduledExecutorService`      |
| 无锁计数器                   | `AtomicInteger`等原子类          |

---

### **最佳实践建议**
1. **优先使用并发集合**：如 `ConcurrentHashMap` 替代 `Hashtable`。
2. **避免滥用锁**：优先选择原子类或无锁数据结构。
3. **合理配置线程池**：根据任务类型（CPU密集型/IO密集型）设置线程数。
4. **及时释放资源**：确保锁、信号量等在 `finally` 块中释放。
5. **监控线程状态**：通过 `Thread.getAllStackTraces()` 或工具（如 VisualVM）排查死锁。

通过灵活组合这些工具类，可以高效解决多线程环境下的同步、协作和性能问题。
