# Java 中什么情况会导致死锁？如何避免？

**难度**：中等

**创建时间**：2025-10-06 15:38:39

## 答案
在 Java 中，**死锁（Deadlock）** 是指两个或多个线程在执行过程中，因争夺资源而造成的一种互相等待的现象，导致所有相关线程都无法继续执行。死锁是并发编程中常见的问题，理解其成因和避免方法至关重要。

---

## **1. 死锁的四个必要条件**
死锁的发生必须同时满足以下四个条件：
1. **互斥条件（Mutual Exclusion）**：资源一次只能被一个线程占用（如锁、数据库连接）。
2. **占有并等待（Hold and Wait）**：线程持有至少一个资源，并等待获取其他被占用的资源。
3. **非抢占条件（No Preemption）**：已分配的资源不能被其他线程强行夺取，必须由持有线程主动释放。
4. **循环等待（Circular Wait）**：存在一个线程循环链，每个线程都在等待下一个线程持有的资源（如线程1等待线程2的资源，线程2等待线程3的资源，线程3等待线程1的资源）。

---

## **2. Java 中导致死锁的常见场景**
### **（1）嵌套锁顺序不一致**
**示例**：
```java
public class DeadlockExample {
    private final Object lock1 = new Object();
    private final Object lock2 = new Object();

    public void thread1() {
        synchronized (lock1) {
            System.out.println("Thread1: Holding lock1...");
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            synchronized (lock2) { // 线程1尝试获取lock2
                System.out.println("Thread1: Acquired lock2!");
            }
        }
    }

    public void thread2() {
        synchronized (lock2) {
            System.out.println("Thread2: Holding lock2...");
            try { Thread.sleep(100); } catch (InterruptedException e) {}
            synchronized (lock1) { // 线程2尝试获取lock1
                System.out.println("Thread2: Acquired lock1!");
            }
        }
    }

    public static void main(String[] args) {
        DeadlockExample example = new DeadlockExample();
        new Thread(example::thread1).start();
        new Thread(example::thread2).start();
    }
}
```
**结果**：线程1和线程2互相等待对方释放锁，导致死锁。

### **（2）多线程操作数据库或外部资源**
- 两个事务分别持有对方需要的表锁或行锁（如数据库死锁）。
- 示例：事务A更新表T1后尝试更新表T2，事务B更新表T2后尝试更新表T1。

### **（3）`ReentrantLock` 未正确释放**
- 使用 `ReentrantLock` 时未调用 `unlock()`，或未在 `finally` 块中释放锁。
- 示例：
  ```java
  Lock lock = new ReentrantLock();
  lock.lock();
  try {
      // 业务逻辑
  } // 忘记调用 lock.unlock()，导致其他线程无法获取锁
  ```

### **（4）线程池中的任务依赖**
- 任务A依赖任务B的结果，任务B依赖任务A的结果，且两者提交到同一线程池，可能导致线程饥饿或死锁。

---

## **3. 如何检测死锁？**
### **（1）使用 `jstack` 工具**
1. 找到 Java 进程的 PID：
   ```bash
   jps -l
   ```
2. 导出线程堆栈：
   ```bash
   jstack <PID> > thread_dump.txt
   ```
3. 检查输出中的 `DEADLOCK` 关键字，或搜索 `found one java-level deadlock`。

### **（2）代码中捕获死锁**
- 通过 `ThreadMXBean` 检测死锁：
  ```java
  ThreadMXBean bean = ManagementFactory.getThreadMXBean();
  long[] threadIds = bean.findDeadlockedThreads(); // 返回死锁线程ID数组
  if (threadIds != null) {
      ThreadInfo[] infos = bean.getThreadInfo(threadIds);
      for (ThreadInfo info : infos) {
          System.out.println(info.getThreadName() + " is waiting on " + info.getLockName());
      }
  }
  ```

### **（3）日志和监控**
- 在关键锁操作处添加日志，记录锁的获取和释放顺序。
- 使用 APM 工具（如 SkyWalking、Prometheus）监控线程状态。

---

## **4. 如何避免死锁？**
### **（1）破坏死锁的四个必要条件**
#### **① 破坏互斥条件**
- 尽可能使用非阻塞数据结构（如 `ConcurrentHashMap`、`AtomicInteger`）。
- 示例：用 `CopyOnWriteArrayList` 替代 `ArrayList` + `synchronized`。

#### **② 破坏占有并等待**
- **一次性获取所有资源**：使用 `tryLock` 超时机制或合并锁。
- 示例：
  ```java
  Lock lock1 = new ReentrantLock();
  Lock lock2 = new ReentrantLock();

  // 尝试同时获取两个锁，避免死锁
  boolean acquired1 = false, acquired2 = false;
  try {
      acquired1 = lock1.tryLock(1, TimeUnit.SECONDS);
      acquired2 = lock2.tryLock(1, TimeUnit.SECONDS);
  } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
  }
  if (acquired1 && acquired2) {
      try {
          // 业务逻辑
      } finally {
          lock1.unlock();
          lock2.unlock();
      }
  }
  ```

#### **③ 破坏非抢占条件**
- 使用可中断的锁（如 `ReentrantLock.lockInterruptibly()`）。
- 示例：
  ```java
  ReentrantLock lock = new ReentrantLock();
  try {
      lock.lockInterruptibly(); // 允许其他线程中断当前锁
      // 业务逻辑
  } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
  } finally {
      lock.unlock();
  }
  ```

#### **④ 破坏循环等待条件**
- **按固定顺序获取锁**：所有线程必须以相同的顺序请求锁。
- 示例：
  ```java
  public class OrderedLockExample {
      private final Object lockA = new Object();
      private final Object lockB = new Object();

      public void method1() {
          synchronized (lockA) { // 先获取lockA
              synchronized (lockB) { // 再获取lockB
                  // 业务逻辑
              }
          
      }

      public void method2() {
          synchronized (lockA) { // 同样先获取lockA
              synchronized (lockB) { // 再获取lockB
                  // 业务逻辑
              }
          }
      }
  }
  ```

### **（2）其他最佳实践**
1. **减少锁的粒度**：
   - 使用细粒度锁（如分段锁）替代全局锁。
   - 示例：`ConcurrentHashMap` 将数据分段，每段独立加锁。

2. **避免嵌套锁**：
   - 尽量减少 `synchronized` 块的嵌套。

3. **使用并发工具类**：
   - 优先使用 `java.util.concurrent` 包中的类（如 `Semaphore`、`CountDownLatch`）。

4. **设置锁超时**：
   - 使用 `tryLock` 避免无限等待：
     ```java
     Lock lock = new ReentrantLock();
     if (lock.tryLock(1, TimeUnit.SECONDS)) { // 尝试1秒内获取锁
         try {
             // 业务逻辑
         } finally {
             lock.unlock();
         }
     } else {
         // 处理获取锁失败
     }
     ```

5. **线程池任务隔离**：
   - 将相互依赖的任务提交到不同的线程池，或使用 `CompletableFuture` 异步编排。

---

## **5. 总结**
| **死锁原因**               | **避免方法**                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| 嵌套锁顺序不一致           | 按固定顺序获取锁，或使用 `tryLock` 超时机制                                 |
| 资源竞争激烈               | 减少锁粒度（如分段锁），使用无锁数据结构（如 `Atomic` 类）                  |
| 未正确释放锁               | 在 `finally` 块中释放锁，或使用 `try-with-resources`（Java 9+ 的 `Cleaner`）|
| 数据库事务死锁             | 设置事务隔离级别，优化 SQL 顺序，或使用乐观锁（版本号）                     |
| 线程池任务依赖             | 隔离任务到不同线程池，或使用异步编排（如 `CompletableFuture`）              |

**关键点**：  
- 死锁的核心是**循环等待**，破坏任意一个必要条件即可避免。  
- 实际开发中，推荐**按固定顺序加锁** + **超时机制** + **无锁化设计**的组合策略。  
- 通过工具（如 `jstack`）和日志监控死锁，及时修复。

通过合理设计锁的获取顺序和释放机制，可以显著降低死锁风险，提升系统的并发性能。
