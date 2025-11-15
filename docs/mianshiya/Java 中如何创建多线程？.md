# Java 中如何创建多线程？

**难度**：简单

**创建时间**：2025-10-06 06:02:58

## 答案
在 Java 中创建多线程主要有以下几种方式，每种方式适用于不同的场景：

---

### 1. **继承 `Thread` 类**
通过继承 `Thread` 类并重写 `run()` 方法，然后创建实例并调用 `start()` 启动线程。
```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程运行中: " + Thread.currentThread().getName());
    }
}

public class Main {
    public static void main(String[] args) {
        MyThread thread = new MyThread();
        thread.start(); // 启动线程
    }
}
```
**缺点**：单继承限制，灵活性较差。

---

### 2. **实现 `Runnable` 接口**
通过实现 `Runnable` 接口（更推荐，避免单继承限制），将实例传递给 `Thread` 对象。
```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("线程运行中: " + Thread.currentThread().getName());
    }
}

public class Main {
    public static void main(String[] args) {
        Thread thread = new Thread(new MyRunnable());
        thread.start();
    }
}
```
**优点**：适合资源共享（多个线程共享同一个 `Runnable` 实例）。

---

### 3. **实现 `Callable` 接口 + `FutureTask`**
`Callable` 可以返回结果并抛出异常，通过 `FutureTask` 获取结果。
```java
import java.util.concurrent.Callable;
import java.util.concurrent.FutureTask;

class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "线程返回结果: " + Thread.currentThread().getName();
    }
}

public class Main {
    public static void main(String[] args) throws Exception {
        FutureTask<String> futureTask = new FutureTask<>(new MyCallable());
        Thread thread = new Thread(futureTask);
        thread.start();
        System.out.println(futureTask.get()); // 阻塞获取结果
    }
}
```
**优点**：支持返回值和异常处理。

---

### 4. **使用线程池（`ExecutorService`）**
通过 `Executors` 工厂类创建线程池，管理线程生命周期。
```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Main {
    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        // 提交任务（Runnable）
        executor.execute(() -> {
            System.out.println("任务1执行: " + Thread.currentThread().getName());
        });

        // 提交任务（Callable）
        executor.submit(() -> {
            return "任务2结果";
        });

        executor.shutdown(); // 关闭线程池
    }
}
```
**优点**：高效管理线程资源，避免频繁创建/销毁线程。

---

### 5. **Lambda 表达式简化**
Java 8+ 可以用 Lambda 简化 `Runnable` 或 `Callable` 的创建。
```java
// Runnable 简化
new Thread(() -> System.out.println("Lambda线程")).start();

// Callable 简化
FutureTask<Integer> future = new FutureTask<>(() -> 100);
new Thread(future).start();
```

---

### 关键区别：
| 方式               | 返回值 | 异常处理 | 资源复用 | 适用场景               |
|--------------------|--------|----------|----------|------------------------|
| 继承 `Thread`      | ❌     | ❌       | ❌       | 简单任务，无需共享资源 |
| 实现Runnable`    | ❌     | ❌       | ✔️       | 资源共享               |
| 实现 `Callable`    | ✔️     | ✔️       | ✔️       | 需要结果或异常处理     |
| 线程池             | ✔️     | ✔️       | ✔️       | 高并发、任务频繁       |

---

### 注意事项：
1. **不要直接调用 `run()`**：必须通过 `start()` 启动线程。
2. **线程安全**：多线程共享数据时需同步（如 `synchronized`、`Lock`）。
3. **线程池优先**：避免频繁创建线程，推荐使用 `Executors` 或 `ThreadPoolExecutor`。

根据需求选择合适的方式，通常**线程池 + `Runnable`/`Callable`**是生产环境的最佳实践。
