# 说说 AQS 吧？

**难度**：中等

**创建时间**：2025-10-06 06:03:27

## 答案
AQS（AbstractQueuedSynchronizer）是 **Java 并发编程中实现锁和同步器的核心框架**，位于 `java.util.concurrent.locks` 包中。它通过抽象同步状态管理和线程排队机制，为开发者提供了一套高效、可扩展的同步工具实现方案。

### **核心设计思想**
1. **模板方法模式**  
   AQS 定义了同步器的基本流程（如获取锁、释放锁），但将具体业务逻辑（如是否允许获取锁）交给子类实现。子类只需重写以下方法：
   - **独占模式**：`tryAcquire()`、`tryRelease()`
   - **共享模式**：`tryAcquireShared()`、`tryReleaseShared()`

2. **状态管理**  
   使用 `volatile int state` 表示同步状态，不同同步器对其含义不同：
   - **ReentrantLock**：`state=0` 表示未锁定，`>0` 表示重入次数。
   - **Semaphore**：`state` 表示剩余许可数。
   - **CountDownLatch**：`state` 表示初始计数器值。

3. **线程排队机制**  
   通过 **双向链表** 实现的 FIFO 队列管理等待线程。队列头部是当前持有锁的线程，其他线程按顺序排队。当锁释放时，唤醒队列头部下一个线程。

### **关键组件**
1. **同步状态（State）**  
   - 通过 `getState()`、`setState()`、`compareAndSetState()` 操作，保证线程安全。
   - `volatile` 修饰确保可见性，CAS 操作保证原子性。

2. **等待队列（CLH 队列变种）**  
   - 每个节点（`Node`）包含线程引用、等待状态（`waitStatus`）、前驱/后继指针。
   - 线程获取锁失败时，被封装为节点加入队列尾部，通过 `LockSupport.park()` 阻塞。

3. **阻塞与唤醒**  
   - **阻塞**：`LockSupport.park(thread)` 使线程挂起。
   - **唤醒**：`LockSupport.unpark(thread)` 唤醒线程，或通过前驱节点的 `SIGNAL` 状态触发唤醒。

### **工作原理**
#### **独占锁示例（如 ReentrantLock）**
1. **获取锁**：
   - 调用 `acquire(int arg)`，内部调用子类的 `tryAcquire(arg)`。
   - 若成功，线程持有锁；若失败，封装为节点加入队列，通过自旋或阻塞等待。

2. **释放锁**：
   - 调用 `release(int arg)`，内部调用子类的 `tryRelease(arg)`。
   - 若成功，唤醒队列头部下一个节点。

#### **共享锁示例（如 Semaphore）**
1. **获取资源**：
   - 调用 `acquireShared(int arg)`，内部调用子类的 `tryAcquireShared(arg)`。
   - 返回值 ≥0 表示成功，<0 表示失败需排队。

2. **释放资源**：
   - 调用 `releaseShared(int arg)`，唤醒后续等待节点。

### **应用场景**
1. **ReentrantLock**  
   - 实现可重入独占锁，支持公平/非公平模式。
   - 公平锁：按队列顺序获取锁；非公平锁：直接尝试获取锁，失败再排队。

2. **Semaphore**  
   - 控制资源访问数量，如数据库连接池。
   - 共享模式下允许多线程同时获取许可。

3. **CountDownLatch**  
   - 等待多个线程完成操作。
   - 通过共享模式实现，计数器归零时唤醒所有等待线程。

4. **ReentrantReadWriteLock**  
   - 实现读写分离锁。
   - `state` 的高16位表示读锁计数，低16位表示写锁计数。

### **优缺点**
- **优点**：
  - **统一框架**：简化锁和同步器的实现，避免重复造轮子。
  - **高效线程管理**：通过 FIFO 队列和 CAS 操作减少竞争。
  - **灵活性**：支持独占/共享模式，适应不同场景。

- **缺点**：
  - **复杂度高**：需深入理解其原理才能正确扩展。
  - **性能开销**：队列操作和 CAS 在高并发下可能成为瓶颈。

### **代码示例：自定义独占锁**
```java
import java.util.concurrent.locks.AbstractQueuedSynchronizer;

public class SimpleLock {
    private static class Sync extends AbstractQueuedSynchronizer {
        @Override
        protected boolean tryAcquire(int acquires) {
            if (compareAndSetState(0, 1)) {
                setExclusiveOwnerThread(Thread.currentThread());
                return true;
            }
            return false;
        }

        @Override
        protected boolean tryRelease(int releases) {
            if (getState() == 0) throw new IllegalMonitorStateException();
            setExclusiveOwnerThread(null);
            setState(0);
            return true;
        }
    }

    private final Sync sync = new Sync();

    public void lock() {
        sync.acquire(1);
    }

    public void unlock() {
        sync.release(1);
    }
}
```

### **总结**
AQS 是 Java 并发编程的基石，通过抽象同步状态和线程排队机制，为开发者提供了高效、灵活的同步工具实现方案。理解 AQS 的原理和设计思想，有助于更好地使用和扩展 Java 的并发工具，编写出高效、可靠的并发程序。
