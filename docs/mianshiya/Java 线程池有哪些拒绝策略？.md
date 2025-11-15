# Java 线程池有哪些拒绝策略？

**难度**：中等

**创建时间**：2025-10-06 15:39:28

## 答案
在 Java 中，线程池（`ThreadPoolExecutor`）提供了 **4 种内置的拒绝策略**，用于处理当任务队列已满且线程数达到最大值时的新任务提交。这些策略通过 `RejectedExecutionHandler` 接口实现，开发者也可以自定义策略。

---

## **一、Java 内置的 4 种拒绝策略**
### **1. AbortPolicy（默认策略）**
- **行为**：直接抛出 `RejectedExecutionException` 异常，阻止任务提交。
- **适用场景**：需要快速失败（Fail-Fast）的场景，例如关键任务必须被处理，否则立即报错。
- **代码示例**：
  ```java
  ThreadPoolExecutor executor = new ThreadPoolExecutor(
      2, 4, 60, TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(2),
      new ThreadPoolExecutor.AbortPolicy() // 默认策略
  );
  executor.execute(() -> System.out.println("Task 1")); // 正常执行
  executor.execute(() -> System.out.println("Task 2")); // 正常执行
  executor.execute(() -> System.out.println("Task 3")); // 队列满，线程未达最大值，进入队列
  executor.execute(() -> System.out.println("Task 4")); // 队列满，线程未达最大值，进入队列
  executor.execute(() -> System.out.println("Task 5")); // 线程池满，抛出 RejectedExecutionException
  ```

### **2. CallerRunsPolicy**
- **行为**：由提交任务的线程（如主线程）直接执行该任务，而不是交给线程池。
- **适用场景**：
  - 任务可以由调用线程执行（非耗时任务）。
  - 避免任务丢失，但可能阻塞调用线程。
- **代码示例**：
  ```java
  ThreadPoolExecutor executor = new ThreadPoolExecutor(
      2, 2, 60, TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(2),
      new ThreadPoolExecutor.CallerRunsPolicy()
  );
  executor.execute(() -> System.out.println("Task 1")); // 线程1执行
  executor.execute(() -> System.out.println("Task 2")); // 线程2执行
  executor.execute(() -> System.out.println("Task 3")); // 进入队列
  executor.execute(() -> System.out.println("Task 4")); // 进入队列
  executor.execute(() -> System.out.println("Task 5")); // 主线程直接执行
  ```

### **3. DiscardPolicy**
- **行为**：静默丢弃被拒绝的任务，不抛出异常，也不执行。
- **适用场景**：
  - 任务可丢弃且无需反馈（如日志记录）。
  - 允许任务丢失，但需确保后续能补救。
- **代码示例**：
  ```java
  ThreadPoolExecutor executor = new ThreadPoolExecutor(
      2, 2, 60, TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(2),
      new ThreadPoolExecutor.DiscardPolicy()
  );
  executor.execute(() -> System.out.println("Task 1")); // 线程1执行
  executor.execute(() -> System.out.println("Task 2")); // 线程2执行
  executor.execute(() -> System.out.println("Task 3")); // 进入队列
  executor.execute(() -> System.out.println("Task 4")); // 进入队列
  executor.execute(() -> System.out.println("Task 5")); // 静默丢弃，无输出
  ```

### **4. DiscardOldestPolicy**
- **行为**：丢弃队列中最旧的任务，然后重新提交当前任务。
- **适用场景**：
  - 队列中存在过期或低优先级任务。
  - 需要保证最新任务优先执行。
- **代码示例**：
  ```java
  ThreadPoolExecutor executor = new ThreadPoolExecutor(
      2, 2, 60, TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(2),
      new ThreadPoolExecutor.DiscardOldestPolicy()
  );
  executor.execute(() -> System.out.println("Task 1")); // 线程1执行
  executor.execute(() -> System.out.println("Task 2")); // 线程2执行
  executor.execute(() -> System.out.println("Task 3")); // 进入队列
  executor.execute(() -> System.out.println("Task 4")); // 进入队列
  executor.execute(() -> System.out.println("Task 5")); // 丢弃 Task 3，执行 Task 5
  ```

---

## **二、自定义拒绝策略**
如果内置策略不满足需求，可以通过实现 `RejectedExecutionHandler` 接口自定义逻辑：
```java
public class CustomRejectPolicy implements RejectedExecutionHandler {
    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        System.err.println("任务被拒绝: " + r.toString());
        // 例如：记录日志、降级处理、重试等
    }
}

// 使用自定义策略
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    2, 2, 60, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(2),
    new CustomRejectPolicy()
);
```

---

## **三、策略对比与选择建议**
| 策略                | 行为                          | 优点                          | 缺点                          | 适用场景                     |
|---------------------|-------------------------------|-------------------------------|-------------------------------|------------------------------|
| **AbortPolicy**     | 抛出异常                      | 快速失败，避免隐藏问题        | 可能丢失任务                  | 关键任务，必须立即报错       |
| **CallerRunsPolicy**| 调用线程执行任务              | 避免任务丢失，降低压力        | 可能阻塞调用线程              | 非耗时任务，允许调用方处理   |
| **DiscardPolicy**   | 静默丢弃任务                  | 简单，不阻塞                  | 任务丢失无感知                | 可丢弃任务（如非关键日志）   |
| **DiscardOldestPolicy** | 丢弃最旧任务，重试当前任务  | 保证最新任务执行              | 可能丢弃重要任务              | 队列中存在过期任务的场景     |

---

## **四、最佳实践**
1. **根据业务重要性选择策略**：
   - 关键任务：优先用 `AbortPolicy` 或 `CallerRunsPolicy`。
   - 非关键任务：可用 `DiscardPolicy` 或 `DiscardOldestPolicy`。
2. **监控与告警**：
   - 记录拒绝任务的数量和原因，设置阈值告警。
3. **动态调整线程池参数**：
   - 通过 `setCorePoolSize()`、`setMaximumPoolSize()` 动态扩容。
4. **结合队列类型**：
   - 使用 `SynchronousQueue`（无队列）时，拒绝策略会频繁触发。
   - 使用 `LinkedBlockingQueue`（无界队列）时，需避免内存溢出。

---

## **五、示例代码（完整线程池配置）**
```java
import java.util.concurrent.*;

public class ThreadPoolDemo {
    public static void main(String[] args) {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            2, // 核心线程数
            4, // 最大线程数
            60, TimeUnit.SECONDS, // 空闲线程存活时间
            new LinkedBlockingQueue<>(2), // 任务队列容量
            new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
        );

        // 提交任务
        for (int i = 1; i <= 6; i++) {
            final int taskId = i;
            try {
                executor.execute(() -> {
                    System.out.println(Thread.currentThread().getName() + " 执行任务 " + taskId);
                    try {
                        Thread.sleep(1000); // 模拟耗时任务
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                });
            } catch (RejectedExecutionException e) {
                System.err.println("任务 " + taskId + " 被拒绝");
            }
        }

        executor.shutdown();
    }
}
```

**输出示例**：
```
pool-1-thread-1 执行任务 1
pool-1-thread-2 执行任务 2
pool-1-thread-1 执行任务 3  // 线程1执行完任务1后继续执行任务3
pool-1-thread-2 执行任务 4
main 执行任务 5           // 队列满且线程数达上限，主线程执行任务5
任务 6 被拒绝             // 任务6被拒绝（根据策略可能不同）
```

---

## **总结**
- Java 线程池的拒绝策略通过 `RejectedExecutionHandler` 实现，提供 4 种内置方案。
- **默认策略**是 `AbortPolicy`（抛出异常），需根据业务场景选择合适策略。
- 自定义策略可实现更复杂的逻辑（如降级、重试、记录日志）。
- 合理配置线程池参数（核心线程数、队列容量、最大线程数）能减少拒绝策略的触发。
