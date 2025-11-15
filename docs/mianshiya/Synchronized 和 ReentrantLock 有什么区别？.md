# Synchronized 和 ReentrantLock 有什么区别？

**难度**：中等

**创建时间**：2025-10-06 15:42:27

## 答案
`Synchronized` 和 `ReentrantLock` 都是 Java 中用于实现线程同步的机制，但它们在**底层实现、功能特性、使用灵活性**等方面存在显著差异。以下是两者的详细对比：

---

### **一、底层实现**
| **特性**               | **Synchronized**                          | **ReentrantLock**                          |
|------------------------|-------------------------------------------|-------------------------------------------|
| **实现方式**           | JVM 层面实现，依赖 `monitor` 对象（对象头标记）。 | 基于 Java 代码实现，通过 `AQS`（AbstractQueuedSynchronizer）框架实现。 |
| **锁升级机制**         | 支持锁升级（无锁→偏向锁→轻量级锁→重量级锁）。 | 无锁升级机制，直接竞争重量级锁。            |
| **跨平台一致性**       | 由 JVM 保证，行为在不同 JVM 实现中一致。    | 依赖 JDK 实现，可能因版本不同有细微差异。   |

---

### **二、功能特性对比**
#### **1. 锁的获取与释放**
- **Synchronized**：  
  - 隐式获取和释放锁：进入同步代码块/方法时自动获取锁，退出时自动释放。  
  - 无法中断等待锁的线程：若线程长时间获取不到锁，只能阻塞等待。  

- **ReentrantLock**：  
  - 显式获取和释放锁：需通过 `lock()` 和 `unlock()` 方法手动控制。  
  - 支持中断响应：通过 `lockInterruptibly()` 方法可响应中断，抛出 `InterruptedException`。  

**示例**：
```java
// ReentrantLock 支持中断
ReentrantLock lock = new ReentrantLock();
try {
    lock.lockInterruptibly(); // 可中断的锁获取
    // 临界区代码
} catch (InterruptedException e) {
    Thread.currentThread().interrupt(); // 恢复中断状态
} finally {
    lock.unlock();
}
```

#### **2. 公平锁与非公平锁**
- **Synchronized**：  
  - 默认是非公平锁：线程竞争锁时可能插队，导致某些线程长时间等待。  

- **ReentrantLock**：  
  - 支持公平锁模式：通过构造函数 `new ReentrantLock(true)` 启用，按请求顺序分配锁，避免线程饥饿。  

**公平锁示例**：
```java
ReentrantLock fairLock = new ReentrantLock(true); // 公平锁
fairLock.lock();
try {
    // 临界区代码
} finally {
    fairLock.unlock();
}
```

#### **3. 条件变量（Condition）**
- **Synchronized**：  
  - 仅支持单个条件等待：通过 `wait()`、`notify()`、`notifyAll()` 实现，所有等待线程共享同一条件队列。  

- **ReentrantLock**：  
  - 支持多个条件变量：通过 `newCondition()` 创建多个 `Condition` 对象，实现更精细的线程唤醒控制。  

**多条件变量示例**：
```java
ReentrantLock lock = new ReentrantLock();
Condition conditionA = lock.newCondition();
Condition conditionB = lock.newCondition();

lock.lock();
try {
    conditionA.await(); // 线程A等待
    conditionB.signal(); // 唤醒线程B
} finally {
    lock.unlock();
}
```

#### **4. 锁的可重入性**
- **两者均支持可重入锁**：  
  - 同一线程可多次获取锁（需对应次数的释放），避免死锁。  
  - 示例：
    ```java
    // Synchronized 可重入
    public synchronized void method1() {
        method2(); // 同一线程可再次进入同步方法
    }
    public synchronized void method2() {}

    // ReentrantLock 可重入
    ReentrantLock lock = new ReentrantLock();
    lock.lock();
    lock.lock(); // 同一线程可再次获取锁
    lock.unlock();
    lock.unlock(); // 需释放两次
    ```

#### **5. 读写锁支持**
- **Synchronized**：  
  - 不支持读写分离：所有锁请求均为独占锁。  

- **ReentrantLock**：  
  - 可结合 `ReentrantReadWriteLock` 实现读写锁：读操作共享锁，写操作独占锁，提升并发性能。  

**读写锁示例**：
```java
ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
rwLock.readLock().lock(); // 读锁
try {
    // 读操作
} finally {
    rwLock.readLock().unlock();
}

rwLock.writeLock().lock(); // 写锁
try {
    // 写操作
} finally {
    rwLock.writeLock().unlock();
}
```

---

### **三、性能对比**
| **场景**               | **Synchronized**                          | **ReentrantLock**                          |
|------------------------|-------------------------------------------|-------------------------------------------|
| **低竞争环境**         | 性能略优（JVM 优化，如锁消除、锁粗化）。    | 稍慢（需调用 AQS 方法）。                   |
| **高竞争环境**         | 性能下降明显（重量级锁开销大）。            | 可通过公平锁或条件变量优化，性能更稳定。   |
| **JDK 版本优化**       | JDK 6 后持续优化（如自适应自旋锁）。        | 性能依赖 AQS 实现，变化较小。              |

---

### **四、使用建议**
1. **优先使用 `Synchronized`**：  
   - 代码简洁，无需手动释放锁。  
   - 适合大多数同步场景（如方法级同步、简单临界区）。  
   - JDK 优化后性能已接近 `ReentrantLock`。  

2. **选择 `ReentrantLock` 的场景**：  
   - 需要**可中断的锁获取**（如超时控制）。  
   - 需要**公平锁**或**多条件变量**。  
   - 需要**读写锁**分离（通过 `ReentrantReadWriteLock`）。  
   - 代码需要更灵活的锁控制（如尝试获取锁 `tryLock()`）。  

**典型用例**：
```java
// 尝试获取锁，避免长时间阻塞
ReentrantLock lock = new ReentrantLock();
if (lock.tryLock(1, TimeUnit.SECONDS)) { // 1秒内获取锁
    try {
        // 临界区代码
    } finally {
        lock.unlock();
    }
} else {
    // 处理获取锁失败
}
```

---

### **五、总结**
| **特性**               | **Synchronized**                          | **ReentrantLock**                          |
|------------------------|-------------------------------------------|-------------------------------------------|
| **语法复杂度**         | 低（隐式同步）                            | 高（显式锁操作）                          |
| **功能灵活性**         | 基础同步（锁升级、非公平锁）              | 高级功能（公平锁、条件变量、可中断）      |
| **适用场景**           | 简单同步需求                              | 复杂线程控制需求                          |
| **性能**               | 低竞争时更优                              | 高竞争时可优化                            |

**选择原则**：  
- 默认用 `Synchronized`，简化代码。  
- 需要高级功能时（如可中断、公平锁），用 `ReentrantLock`。
