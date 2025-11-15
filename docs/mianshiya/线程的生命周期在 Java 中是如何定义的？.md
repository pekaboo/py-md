# 线程的生命周期在 Java 中是如何定义的？

**难度**：中等

**创建时间**：2025-10-06 15:48:43

## 答案
在 Java 中，线程的生命周期定义了线程从创建到销毁的完整过程，包括多个状态及其转换。Java 通过 `Thread` 类和 `Thread.State` 枚举来管理线程状态，并提供了线程启动、运行、阻塞、终止等操作的 API。以下是 Java 线程生命周期的详细说明：

---

## **1. 线程生命周期的六个状态**
Java 线程的状态通过 `Thread.State` 枚举定义，包括以下六种状态：

| **状态**                | **描述**                                                                 |
|-------------------------|--------------------------------------------------------------------------|
| **NEW（新建）**          | 线程对象已创建，但尚未调用 `start()` 方法。                              |
| **RUNNABLE（可运行）**   | 线程已调用 `start()`，正在 JVM 中执行或等待 CPU 时间片（包括运行和就绪状态）。 |
| **BLOCKED（阻塞）**      | 线程因等待获取锁（如同步块）而被阻塞。                                   |
| **WAITING（等待）**      | 线程进入等待状态，需其他线程显式唤醒（如调用 `Object.wait()` 或 `Thread.join()`）。 |
| **TIMED_WAITING（限时等待）** | 线程在指定时间内等待（如 `Thread.sleep(time)` 或 `Object.wait(timeout)`）。 |
| **TERMINATED（终止）**   | 线程执行完毕或因异常退出，生命周期结束。                                 |

---

## **2. 线程生命周期的详细阶段**
### **阶段 1：新建（NEW）**
- **触发条件**：通过 `new Thread()` 创建线程对象，但未调用 `start()`。
- **关键点**：
  - 线程尚未分配系统资源（如线程 ID、栈空间）。
  - 仅存在于 JVM 内存中，未与操作系统线程关联。
- **示例**：
  ```java
  Thread thread = new Thread(() -> System.out.println("Running"));
  System.out.println(thread.getState()); // 输出: NEW
  ```

### **阶段 2：可运行（RUNNABLE）**
- **触发条件**：调用 `start()` 方法后，线程进入就绪状态，等待 CPU 调度。
- **关键点**：
  - 包含两种子状态：
    - **就绪（Ready）**：线程已准备好执行，等待操作系统分配 CPU 时间片。
    - **运行（Running）**：线程正在 CPU 上执行。
  - 线程调度由操作系统决定，JVM 不直接控制。
- **示例**：
  ```java
  thread.start();
  System.out.println(thread.getState()); // 输出: RUNNABLE（可能瞬间切换到其他状态）
  ```

### **阶段 3：阻塞（BLOCKED）**
- **触发条件**：线程尝试获取同步锁（`synchronized`）但失败，进入阻塞状态。
- **关键点**：
  - 阻塞是暂时的，当锁释放后，线程会回到 `RUNNABLE` 状态。
  - 常见场景：多个线程竞争同一个对象的同步方法或代码块。
- **示例**：
  ```java
  Object lock = new Object();
  Thread t1 = new Thread(() -> {
      synchronized (lock) {
          while (true) {} // 持有锁不释放
      }
  });
  Thread t2 = new Thread(() -> {
      synchronized (lock) { // t2 会阻塞，直到 t1 释放锁
          System.out.println("Acquired lock");
      }
  });
  t1.start();
  t2.start();
  // t2 的状态会变为 BLOCKED
  ```

### **阶段 4：等待（WAITING）**
- **触发条件**：线程主动调用以下方法之一：
  - `Object.wait()`：在同步块中释放锁并等待。
  - `Thread.join()`：等待目标线程终止。
  - `LockSupport.park()`：挂起线程。
- **关键点**：
  - 线程会无限期等待，直到被其他线程显式唤醒（如 `notify()`、`interrupt()`）。
  - 唤醒后进入 `RUNNABLE` 状态。
- **示例**：
  ```java
  Object lock = new Object();
  Thread waiter = new Thread(() -> {
      synchronized (lock) {
          try {
              lock.wait(); // 释放锁并进入 WAITING 状态
          } catch (InterruptedException e) {}
      }
  });
  waiter.start();
  // 需另一个线程调用 lock.notify() 唤醒 waiter
  ```

### **阶段 5：限时等待（TIMED_WAITING）**
- **触发条件**：线程调用带超时参数的等待方法：
  - `Thread.sleep(timeout)`：休眠指定时间。
  - `Object.wait(timeout)`：在同步块中等待超时或被唤醒。
  - `Thread.join(timeout)`：等待目标线程终止或超时。
  - `LockSupport.parkNanos(timeout)`：挂起线程指定时间。
- **关键点**：
  - 超时后自动回到 `RUNNABLE` 状态。
  - 也可被中断提前唤醒（抛出 `InterruptedException`）。
- **示例**：
  ```java
  Thread timer = new Thread(() -> {
      try {
          Thread.sleep(2000); // 进入 TIMED_WAITING 状态，2秒后恢复
      } catch (InterruptedException e) {}
  });
  timer.start();
  ```

### **阶段 6：终止（TERMINATED）**
- **触发条件**：线程执行完毕或因异常退出。
- **关键点**：
  - 线程无法重新启动（调用 `start()` 会抛出 `IllegalThreadStateException`）。
  - 需通过 `isAlive()` 方法检查线程是否终止。
- **示例**：
  ```java
  thread.start();
  thread.join(); // 等待线程终止
  System.out.println(thread.getState()); // 输出: TERMINATED
  ```

---

## **3. 线程状态转换图**
```mermaid
graph TD
    A[NEW] -->|start()| B[RUNNABLE]
    B -->|获取锁| C[RUNNABLE]
    B -->|竞争锁失败| D[BLOCKED]
    D -->|锁释放| B
    B -->|wait()/join()/park()| E[WAITING]
    E -->|notify()/interrupt()| B
    B -->|sleep()/wait(timeout)/join(timeout)| F[TIMED_WAITING]
    F -->|超时/interrupt()| B
    B -->|执行完毕| G[TERMINATED]
```

---

## **4. 关键方法与注意事项**
### **4.1 状态查询方法**
- `thread.getState()`：返回当前线程状态（`Thread.State` 枚举）。
- `thread.isAlive()`：判断线程是否已启动且未终止。

### **4.2 线程中断**
- `thread.interrupt()`：设置中断标志，线程需自行处理中断（如检查 `Thread.interrupted()`）。
- 中断会唤醒 `WAITING` 或 `TIMED_WAITING` 状态的线程，并抛出 `InterruptedException`。

### **4.3 线程终止**
- **正确方式**：通过标志位控制线程退出（而非强制停止）。
  ```java
  class Worker implements Runnable {
      private volatile boolean running = true;
      public void stop() { running = false; }
      @Override
      public void run() {
          while (running) {
              // 工作逻辑
          }
      }
  }
  ```
- **错误方式**：`Thread.stop()` 已废弃（可能导致数据不一致）。

### **4.4 守护线程**
- 通过 `setDaemon(true)` 设置守护线程，当所有非守护线程终止时，JVM 会自动退出。

---

## **5. 示例代码**
```java
public class ThreadLifecycleDemo {
    public static void main(String[] args) throws InterruptedException {
        Object lock = new Object();
        
        // 新建状态
        Thread newThread = new Thread(() -> {});
        System.out.println("New thread state: " + newThread.getState()); // NEW

        // 可运行状态
        Thread runnableThread = new Thread(() -> {
            synchronized (lock) {
                while (true) {} // 模拟长时间运行
            }
        });
        runnableThread.start();
        Thread.sleep(100); // 确保线程启动
        System.out.println("Runnable thread state: " + runnableThread.getState()); // RUNNABLE

        // 阻塞状态
        Thread blockedThread = new Thread(() -> {
            synchronized (lock) {
                System.out.println("Blocked thread acquired lock");
            }
        });
        blockedThread.start();
        Thread.sleep(100);
        System.out.println("Blocked thread state: " + blockedThread.getState()); // BLOCKED

        // 等待状态
        Thread waitingThread = new Thread(() -> {
            synchronized (lock) {
                try {
                    lock.wait(); // 释放锁并进入 WAITING
                } catch (InterruptedException e) {}
            }
        });
        waitingThread.start();
        Thread.sleep(100);
        System.out.println("Waiting thread state: " + waitingThread.getState()); // WAITING
        lock.notify(); // 唤醒等待线程

        // 限时等待状态
        Thread timedWaitingThread = new Thread(() -> {
            try {
                Thread.sleep(1000); // TIMED_WAITING
            } catch (InterruptedException e) {}
        });
        timedWaitingThread.start();
        Thread.sleep(100);
        System.out.println("Timed waiting thread state: " + timedWaitingThread.getState()); // TIMED_WAITING

        // 终止状态
        Thread terminatedThread = new Thread(() -> {});
        terminatedThread.start();
        terminatedThread.join();
        System.out.println("Terminated thread state: " + terminatedThread.getState()); // TERMINATED
    }
}
```

---

## **6. 总结**
- **线程状态**：`NEW` → `RUNNABLE` → (`BLOCKED`/`WAITING`/`TIMED_WAITING`) → `TERMINATED`。
- **关键方法**：
  - `start()`：启动线程（仅能调用一次）。
  - `interrupt()`：中断线程（需线程自行处理）。
  - `join()`：等待线程终止。
- **最佳实践**：
  - 避免直接操作线程状态（如强制停止）。
  - 使用同步机制（`synchronized`、`Lock`）和条件变量（`wait()`/`notify()`）协调线程。
  - 通过标志位或中断机制优雅终止线程。

理解线程生命周期是编写多线程程序的基础，能帮助开发者避免死锁、资源竞争和性能问题。
