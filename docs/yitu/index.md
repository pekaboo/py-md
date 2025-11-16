---
title: Java基础
description: Java基础
---
# 面试题参考答案

## HashMap / HashSet / ConcurrentHashMap / synchronized/ AQS / ReentrantLock / CopyOnWriteArrayList 与相关并发工具 

- `HashMap` (1)数组+链表/红黑树，线程不安全，默认加载因子 0.75；(2)数组扩容(元素是Entry) (3)`put`  key hash 定位桶位，桶位冲突时形成链表，链表长度> 8 且容量 ≥64 时转红黑树。
- `HashMap` 扩容流程：(1) 新建 2 倍容量新数组，(2) 遍历旧数组，(3) 按 key hash 定位桶位，(4) 元素迁移：链表/树迁移到新桶位，或者转链表(<6)/树(≥64,> 8)后迁移
- `HashSet` (1)基于 `HashMap`，内部将元素作为 `HashMap` 的 key，value 为常量 `PRESENT`，因此所有行为复用 `HashMap`。(3) `public static final Object PRESENT = new Object(); transient HashMap<E, Object> map;`
- `ConcurrentHashMap` JDK7 分段锁（Segment），JDK8 采用 `CAS + synchronized` 在桶位粒度控制，链表转树同样触发条件。读操作基本无锁，写操作竞争点较少。
---
- `synchronized` (1)Jvm级别内置锁,通过对象头Markword+Monitor锁，通过锁升级保证不同并发场景下性能/安全平衡，支持偏向，轻重自适应优化（2）基于对象头Markword(存锁状态，线程id)+Monitor（互斥锁，包含owner，EntryList，Waitlist） ，
- `synchronized核心逻辑` （1）一个线程加锁时，try Monitor owner 设置为自己，失败接入EntryList（2）解锁时，唤醒EntryList线程（3）调用wait时，线程释放锁，进入waitlist，需被Notify(All)唤醒
---
- **AQS(AbstractQueuedSynchronizer)** 维护 `state` 和 FIFO 队列，提供 `acquire/release` 模板方法。`ReentrantLock`、`CountDownLatch`、`Semaphore` 等均基于 AQS。
- **ReentrantLock**：可公平/非公平、可中断、可定时、可配合条件变量。底层依赖 AQS 的可重入 state 计数。
- **CopyOnWriteArrayList**：写时复制，适合读多写少且迭代快照一致性需求。

::: note 使用指南 
- `HashMap` (1)数组+链表/红黑树，线程不安全，默认加载因子 0.75；(2)数组扩容(元素是Entry) (3)`put`  key hash 定位桶位，桶位冲突时形成链表，链表长度> 8 且容量 ≥64 时转红黑树。
- HashMap 在多线程扩容可能导致环形链表死循环，绝不能直接共享。
- ConcurrentHashMap 迭代弱一致，不保证实时视图；需要强一致时考虑加锁或快照。
- CopyOnWrite 类在写多场景下开销巨大（复制数组），及时回收旧数组避免内存压力。
:::
 


::: 测试
折叠区域中的内容默认隐藏，点击标题后展开。
:::

::: hide 更多细节
折叠区域中的内容默认隐藏，点击标题后展开。
:::
  
::: note 使用指南
通过 `python -m md2html --src docs --dst build/html` 即可将 Markdown 批量转换为 HTML。
:::
 

::: warning 注意事项

- 确保 `docs/` 下文件编码为 UTF-8。
- 调整主题时可在 `theme/` 目录下扩展。
:::

### 1. synchronized 和 ReentrantLock 的区别是什么？底层实现原理有何不同？
#### 回答要点关键字
(1) 核心区别：锁实现、灵活性、功能特性、性能表现  
(2) synchronized 底层：对象头 MarkWord、监视器锁（Monitor）、锁升级（偏向锁→轻量级锁→重量级锁）  
(3) ReentrantLock 底层：AQS（抽象队列同步器）、CAS+volatile、自定义同步状态  
(4) 适用场景：简单同步（synchronized）、复杂场景（ReentrantLock，如公平锁、条件变量）  
::: ### 打开详情
- 🍺基础回答：synchronized 是 Java 内置的关键字，用法简单，加在方法或代码块上就行；ReentrantLock 是 JUC 包下的类，需要手动 lock() 和 unlock()，还得在 finally 里释放锁。两者都支持可重入，区别在于 ReentrantLock 更灵活，能实现公平锁、条件变量，还能中断锁等待；synchronized 是自动释放锁，不用手动管。底层的话，synchronized 靠对象头的 MarkWord 和 Monitor 锁，还会升级；ReentrantLock 靠 AQS 实现。
- 🎉高级扩展版：两者核心区别：1. 实现方式：synchronized 是 JVM 层面的内置锁，由字节码指令（monitorenter/monitorexit）实现；ReentrantLock 是 API 层面的锁，基于 Java 代码实现。2. 灵活性：ReentrantLock 支持公平锁（构造函数传 true）和非公平锁（默认），synchronized 仅支持非公平锁；ReentrantLock 提供条件变量（Condition），支持多线程按条件唤醒；ReentrantLock 可通过 lockInterruptibly() 中断锁等待，synchronized 不可中断。3. 性能：JDK1.6 后 synchronized 经过锁升级优化，性能接近 ReentrantLock；高并发场景下，ReentrantLock 的性能更稳定，可通过自定义策略优化。底层实现：synchronized 依赖对象头 MarkWord 存储锁状态，关联 Monitor 对象（包含等待队列和同步队列），锁升级流程是偏向锁（单线程竞争）→ 轻量级锁（自旋竞争）→ 重量级锁（阻塞竞争），减少锁竞争开销；ReentrantLock 基于 AQS 实现，AQS 核心是 volatile 修饰的 state 变量和双向同步队列，通过 CAS 操作修改 state 实现锁获取和释放，可重入性通过记录当前持有锁的线程和重入次数实现。
- 📌 加分项：举例说明条件变量的用法（如生产者-消费者模型中，用 Condition 实现精准唤醒）；提到 ReentrantLock 的 tryLock() 方法，支持超时获取锁，避免死锁；对比两者的死锁排查方式（synchronized 可通过 jstack 命令查看，ReentrantLock 可通过 LockSupport 工具分析）。
- ⚠️注意事项：ReentrantLock 必须在 finally 块中释放锁（unlock()），否则会导致锁泄漏；公平锁虽然公平，但性能低于非公平锁，需根据业务场景选择；
:::


### 3. 【面试题目】volatile 关键字的底层实现原理是什么？与 synchronized、原子类的区别是什么？
#### 回答要点关键字
(1) 底层原理：`【内存屏障】`、主内存刷新机制、禁止指令重排  
(2) 核心特性：保障可见性、有序性，**不保障原子性**  
(3) 对比差异：volatile 无锁（轻量）、synchronized 有锁（全保障）、原子类基于 `【CAS】`（原子操作）  
(4) 适用场景：状态标记、单例 DCL、避免指令重排  
::: ### 打开详情
- 🍺基础回答：volatile 底层是靠内存屏障实现的，写操作后加个屏障阻止后面的指令往前排，读操作前加屏障确保读主内存的最新值。它能让变量修改后立刻刷到主内存，其他线程读的时候直接取主内存的值，所以能保证可见性和有序性，但像 i++ 这种三步操作它管不了，不能保证原子性。和 synchronized 比，volatile 更轻量，没有锁竞争，但功能少；原子类是专门解决原子性的，底层是 CAS，比 synchronized 效率高。
- 🎉高级扩展版：volatile 的底层实现依赖 CPU 内存屏障指令，JVM 会在 volatile 变量的写操作后插入 StoreLoad 屏障，防止后续指令重排到写操作之前；读操作前插入 LoadLoad 屏障，确保读取主内存最新值而非工作内存缓存。可见性机制是 “写回+失效”：线程修改 volatile 变量后，强制将值刷入主内存，同时使其他线程工作内存中该变量的缓存失效，下次读必须重新加载。与其他同步机制的区别：1. 与 synchronized：volatile 是无锁同步，仅保障可见性和有序性，无锁竞争开销；synchronized 是有锁同步，通过锁升级（偏向锁→轻量级锁→重量级锁）优化，保障三大特性，但高并发下有锁竞争开销。2. 与原子类（AtomicInteger）：原子类基于 CAS 实现原子操作，解决 volatile 无法保障的原子性问题；volatile 侧重解决可见性和有序性，原子类侧重原子性，两者可结合使用（如 AtomicReference 修饰 volatile 变量）。
- 📌 加分项：举例说明 volatile 的典型场景，如线程停止标记（boolean flag）、单例 DCL 中的实例变量；提到 CAS 的 ABA 问题及解决方案（AtomicStampedReference）；对比 JDK1.6 前后 synchronized 的性能变化（锁升级后性能接近 volatile）。
- ⚠️注意事项：volatile 不能替代 synchronized 或原子类，复合操作必须用锁或原子类保障原子性；内存屏障会增加少量性能开销，但远低于锁竞争；volatile 变量的访问不能被编译器优化，需避免过度使用。
:::


## 多线程 HashMap 死循环原因

### 要点速览 · 23

- JDK7 扩容迁移非线程安全，链表节点拆分时可能形成环。
- 线程同时触发 `resize` 导致链表自旋，表现为 CPU 飙升。
- 解决：使用并发容器或加锁，JDK8 改进但仍非线程安全。

### 基础要点 · 23

- HashMap 扩容时将桶内节点移动到新数组，未同步保护。
- 多线程迁移同一桶，`next` 指针被覆盖，形成循环链。
- 死循环体现为 get/put 卡住或 CPU 100%。

### 进阶扩展 · 23

- JDK8 引入尾插与链表树化，但扩容仍非原子；并发写会数据丢失。
- 可通过 `Collections.synchronizedMap`、`ConcurrentHashMap`、`ImmutableMap` 规避。
- 自定义分段锁或使用 `AtomicReference` + CAS 构建无锁结构。

### ⚠️注意事项 · 23

- 不要在多线程环境直接共享可变 HashMap。
- 即使只读，也需在构建后发布时保证可见性（`final` 或安全发布）。
- 面试回答可补充 `computeIfAbsent` 线程安全差异。
- 









## 欢迎使用 md2html

md2html 支持 GitHub 风格主题、目录生成与自定义容器扩展。

## 折叠示例

::: hide 更多细节
折叠区域中的内容默认隐藏，点击标题后展开。
:::

## 提示示例

::: note 使用指南
通过 `python -m md2html --src docs --dst build/html` 即可将 Markdown 批量转换为 HTML。
:::

## 警告示例

::: warning 注意事项

- 确保 `docs/` 下文件编码为 UTF-8。
- 调整主题时可在 `theme/` 目录下扩展。
:::

## 代码示例

```python
from md2html.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```
