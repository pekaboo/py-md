---
title: Java基础
description: Java基础
---
# 面试题参考答案

## HashMap / HashSet / ConcurrentHashMap / synchronized/ AQS / ReentrantLock / CopyOnWriteArrayList 与相关并发工具 

- `HashMap` (1)数组+链表/红黑树，线程不安全，默认加载因子 0.75；(2)数组扩容(元素是Entry) (3)`put`  key hash 定位桶位，桶位冲突时形成链表，链表长度> 8 且容量 ≥64 时转红黑树。
- `HashMap` 扩容流程：(1) 新建 2 倍容量新数组，(2) 遍历旧数组，(3) 按 key hash 定位桶位，(4) 元素迁移：链表/树迁移到新桶位，或者转链表(<6)/树(≥64,> 8)后迁移
- LinkedHashMap(1) 继承 HashMap，数组 + 链表 / 红黑树 + 双向链表，保留插入 / 访问顺序；(2) 线程不安全，默认加载因子 0.75，扩容逻辑同 HashMap；(3) 双向链表维护顺序，accessOrder=true 支持 LRU 特性。
- `HashSet` (1)基于 `HashMap`，内部将元素作为 `HashMap` 的 key，value 为常量 `PRESENT`，因此所有行为复用 `HashMap`。(3) `public static final Object PRESENT = new Object(); transient HashMap<E, Object> map;`去重依赖 HashMap 的 key 唯一性，添加元素本质是 map.put (elem, PRESENT)
-  `transient` 仅用于**实现 `Serializable` 接口**的序列化场景（Java 原生序列化）
- `HashSet` 【cpu密集型用并行流】若两个元素 equals() 返回 true 且 hashCode() 返回值相同，则视为重复元素，无法重复添加（与 HashMap 去重逻辑完全一致）。HashSet 的元素允许：基本类型包装类（Integer、String 等，已重写 hashCode() 和 equals()）、自定义对象（需正确重写上述两个方法）、null（仅一个）；不允许：无意义的自定义对象（未重写 hashCode()/equals()）（会导致无法去重）、重复元素（无论类型）。
- `ConcurrentHashMap` JDK7 分段锁（Segment），JDK8 采用 `CAS + synchronized` 在桶位粒度控制，链表转树同样触发条件。读操作基本无锁，写操作竞争点较少。(1) 跳表实现，并发安全，key 必须可比较，天然有序；(2) 无固定容量，无加载因子，通过跳表分层提升查询效率；(3) 插入 / 查询 / 删除 O (log n)，支持并发读写，无锁设计为主。
- `TreeMap`：红黑树实现，key 必须可比较，天然有序；线程不安全，无加载因子，无扩容； 插入 / 查询 / 删除 O (log n)，依赖 key 比较定位节点，无 hash 冲突问题。
- `TreeSet`： (1) 基于 TreeMap 实现，元素作为 key，value 为常量 PRESENT；(2) 线程不安全，元素有序且唯一；(3) 排序依赖 TreeMap 的 key 比较，去重依据 compareTo () 返回 0。
- `Hashtable`
(1) 数组 + 链表，线程安全（全局 synchronized 锁）；(2) 默认容量 11，加载因子 0.75，扩容为旧容量 * 2+1；(3) 不允许 key/value 为 null，hash 逻辑未优化，冲突概率高。
- `WeakHashMap` (1) 数组 + 链表 / 红黑树，key 为弱引用，线程不安全；(2) 默认加载因子 0.75，扩容逻辑同 HashMap；(3) 当 key 无强引用时会被 GC 回收，自动移除对应条目。
---
- `synchronized` (1)Jvm级别内置锁,通过对象头Markword+Monitor锁，通过锁升级保证不同并发场景下性能/安全平衡，支持偏向，轻重自适应优化（2）基于对象头Markword(存锁状态，线程id)+Monitor（互斥锁，包含owner，EntryList，Waitlist） ，
- `synchronized核心逻辑` （1）一个线程加锁时，try Monitor owner 设置为自己，失败接入EntryList（2）解锁时，唤醒EntryList线程（3）调用wait时，线程释放锁，进入waitlist，需被Notify(All)唤醒
- 对象包含markword，用于存储锁状态、哈希码、GC 年龄等核心信息 ——Mark Word 是对象头的固定组成部。 Java 对象头由两部分组成（32 位 JVM 示例）
-  JVM 在创建对象时，会先分配对象头的内存（包括 Mark Word 的固定字节数：32 位 JVM 中 Mark Word 占 4 字节，64 位 JVM 中占 8 字节），再分配对象的实例字段内存。
-  组成部分	作用	是否必选
   - Mark Word	存储锁状态、线程 ID、哈希码、GC 分代年龄等	✅ 必选（所有对象都有）
   - Klass Pointer（类型指针）	指向对象所属类的元数据（如User.class），确定对象类型	- ✅ 必选（除数组外，数组的类型指针略有不同）
   - 数组长度（仅数组对象）	存储数组的长度（如new int[10]的长度 10）	❌ 仅数组有，普通对象无
- synchronized 锁获取流程核心是「按需升级、不可逆」，全程由 JVM 自动控制，简述如下：
   - 初始状态为「无锁」，锁对象的 Mark Word 存储哈希码 + 无锁标记；
   - 单线程请求：直接升级为「偏向锁」，Mark Word 记录当前线程 ID，后续该线程可零开销复用锁；
   - 多线程交替竞争：撤销偏向锁，升级为「轻量级锁」，线程通过自旋 CAS 尝试抢占锁（避免阻塞）；
   - 竞争激烈（自旋超时 / 多线程并发）：轻量级锁膨胀为「重量级锁」，Mark Word 指向 Monitor，竞争失败的线程进入 EntryList 阻塞，等待被唤醒后重新竞争。
   - 案例： 
---
- **ReentrantLock**：可公平/非公平、可中断、可定时、可配合条件变量。底层依赖 AQS 的可重入 state 计数。
- **CopyOnWriteArrayList**：写时复制，适合读多写少且迭代快照一致性需求。 
- **CountDownLatch**：
- **Semaphore**：
- **AQS(AbstractQueuedSynchronizer)** 维护 `state` 和 FIFO 队列，提供 `acquire/release` 模板方法。`ReentrantLock`、`CountDownLatch`、`Semaphore` 等均基于 AQS。

<!-- ::: 测试
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
::: -->

### 1. synchronized 和 ReentrantLock 的区别是什么？底层实现原理有何不同？
#### 回答要点关键字
(1) 核心区别：锁实现、灵活性、功能特性、性能表现  
(2) synchronized 底层：对象头 MarkWord、监视器锁（Monitor）、锁升级（偏向锁→轻量级锁→重量级锁）  
(3) ReentrantLock 底层：AQS（抽象队列同步器）、CAS+volatile、自定义同步状态  
(4) 适用场景：简单同步（synchronized）、复杂场景（ReentrantLock，如公平锁、条件变量）  
::: hide  打开详情
 🍺基础回答:

 synchronized 是 Java 内置的关键字，用法简单，加在方法或代码块上就行；ReentrantLock 是 JUC 包下的类，需要手动 lock() 和 unlock()，还得在 finally 里释放锁。两者都支持可重入，区别在于 ReentrantLock 更灵活，能实现公平锁、条件变量，还能中断锁等待；synchronized 是自动释放锁，不用手动管。底层的话，synchronized 靠对象头的 MarkWord 和 Monitor 锁，还会升级；ReentrantLock 靠 AQS 实现。
 
🎉高级扩展版：

 两者核心区别：1. 实现方式：synchronized 是 JVM 层面的内置锁，由字节码指令（monitorenter/monitorexit）实现；ReentrantLock 是 API 层面的锁，基于 Java 代码实现。2. 灵活性：ReentrantLock 支持公平锁（构造函数传 true）和非公平锁（默认），synchronized 仅支持非公平锁；ReentrantLock 提供条件变量（Condition），支持多线程按条件唤醒；ReentrantLock 可通过 lockInterruptibly() 中断锁等待，synchronized 不可中断。3. 性能：JDK1.6 后 synchronized 经过锁升级优化，性能接近 ReentrantLock；高并发场景下，ReentrantLock 的性能更稳定，可通过自定义策略优化。底层实现：synchronized 依赖对象头 MarkWord 存储锁状态，关联 Monitor 对象（包含等待队列和同步队列），锁升级流程是偏向锁（单线程竞争）→ 轻量级锁（自旋竞争）→ 重量级锁（阻塞竞争），减少锁竞争开销；ReentrantLock 基于 AQS 实现，AQS 核心是 volatile 修饰的 state 变量和双向同步队列，通过 CAS 操作修改 state 实现锁获取和释放，可重入性通过记录当前持有锁的线程和重入次数实现。
 
📌 加分项：

 举例说明条件变量的用法（如生产者-消费者模型中，用 Condition 实现精准唤醒）；提到 ReentrantLock 的 tryLock() 方法，支持超时获取锁，避免死锁；对比两者的死锁排查方式（synchronized 可通过 jstack 命令查看，ReentrantLock 可通过 LockSupport 工具分析）。
 
⚠️注意事项：

 ReentrantLock 必须在 finally 块中释放锁（unlock()），否则会导致锁泄漏；公平锁虽然公平，但性能低于非公平锁，需根据业务场景选择；
:::


### 2. 【面试题目】volatile 关键字的底层实现原理是什么？与 synchronized、原子类的区别是什么？
#### 回答要点关键字
(1) 底层原理：`【内存屏障】`、主内存刷新机制、禁止指令重排  
(2) 核心特性：保障可见性、有序性，**不保障原子性**  
(3) 对比差异：volatile 无锁（轻量）、synchronized 有锁（全保障）、原子类基于 `【CAS】`（原子操作）  
(4) 适用场景：状态标记、单例 DCL、避免指令重排  
::: hide  打开详情
 🍺基础回答:

 volatile 底层是靠内存屏障实现的，写操作后加个屏障阻止后面的指令往前排，读操作前加屏障确保读主内存的最新值。它能让变量修改后立刻刷到主内存，其他线程读的时候直接取主内存的值，所以能保证可见性和有序性，但像 i++ 这种三步操作它管不了，不能保证原子性。和 synchronized 比，volatile 更轻量，没有锁竞争，但功能少；原子类是专门解决原子性的，底层是 CAS，比 synchronized 效率高。
 
🎉高级扩展版：

 volatile 的底层实现依赖 CPU 内存屏障指令，JVM 会在 volatile 变量的写操作后插入 StoreLoad 屏障，防止后续指令重排到写操作之前；读操作前插入 LoadLoad 屏障，确保读取主内存最新值而非工作内存缓存。可见性机制是 “写回+失效”：线程修改 volatile 变量后，强制将值刷入主内存，同时使其他线程工作内存中该变量的缓存失效，下次读必须重新加载。与其他同步机制的区别：1. 与 synchronized：volatile 是无锁同步，仅保障可见性和有序性，无锁竞争开销；synchronized 是有锁同步，通过锁升级（偏向锁→轻量级锁→重量级锁）优化，保障三大特性，但高并发下有锁竞争开销。2. 与原子类（AtomicInteger）：原子类基于 CAS 实现原子操作，解决 volatile 无法保障的原子性问题；volatile 侧重解决可见性和有序性，原子类侧重原子性，两者可结合使用（如 AtomicReference 修饰 volatile 变量）。
 
📌 加分项：

 举例说明 volatile 的典型场景，如线程停止标记（boolean flag）、单例 DCL 中的实例变量；提到 CAS 的 ABA 问题及解决方案（AtomicStampedReference）；对比 JDK1.6 前后 synchronized 的性能变化（锁升级后性能接近 volatile）。
 
⚠️注意事项：

 volatile 不能替代 synchronized 或原子类，复合操作必须用锁或原子类保障原子性；内存屏障会增加少量性能开销，但远低于锁竞争；volatile 变量的访问不能被编译器优化，需避免过度使用。
:::

---

## 📚【面试题目1：HashMap的底层数据结构、put流程与扩容机制？】
### 回答要点关键字
(1) 底层结构：数组+链表/红黑树（JDK8+）、Entry/Node 存储键值对  
(2) 核心参数：默认容量16、加载因子0.75、树化阈值8、链化阈值6  
(3) put流程：hash计算→桶位定位→冲突处理（链表/树化）→扩容判断  
(4) 扩容机制：2倍容量扩容、元素迁移（链表尾插/树拆分）、阈值更新
::: hide 打开详情
 🍺基础回答:

 HashMap 底层是数组加链表，JDK8 之后如果链表太长还会变成红黑树。默认初始容量是16，加载因子0.75，当元素个数超过16*0.75=12时就会扩容。put元素的时候，先算key的hash值找到对应的数组位置（桶位），如果桶位没人就直接放，有人的话就形成链表，链表长度超过8且数组容量≥64就转红黑树。扩容的时候会新建一个2倍大的数组，然后把旧数组的元素一个个迁移过去。
 
🎉高级扩展版：

 HashMap 核心结构是“数组（table）+ 链表（Node）+ 红黑树（TreeNode）”：1. hash计算：通过key的hashCode()二次哈希（减少碰撞），得到桶位索引（(n-1)&hash）；2. 冲突处理：桶位为空则直接创建Node插入，不为空则判断key是否相等（hash+equals），相等则覆盖value，不相等则插入链表尾部（JDK8尾插法），链表长度>8且数组容量≥64时，将链表转为红黑树；3. 扩容触发：元素数量（size）> 容量（table.length）×加载因子（loadFactor），扩容为原容量2倍（必须是2的幂次，保证桶位计算高效）；4. 迁移逻辑：遍历旧数组，对每个桶的元素（链表/红黑树）重新计算桶位，链表直接迁移，红黑树则拆分为两个链表，若长度≤6则转链表，否则保持红黑树。
 
📌 加分项：

 能解释为什么加载因子是0.75（平衡空间利用率和查询效率）；说明2的幂次容量的原因（(n-1)&hash 等价于取模，效率更高）；对比JDK7和JDK8的差异（JDK7头插法导致并发死循环，JDK8尾插法修复）；提到红黑树的优势（查询时间复杂度从O(n)降为O(logn)）。
 
⚠️注意事项：

 key为null时，固定存放在桶位0（HashMap允许一个null key）；自定义对象作为key时，必须重写hashCode()和equals()，否则会导致元素无法正确查找；扩容是耗时操作，若预知数据量，可提前指定初始容量（如new HashMap<>(1024)），减少扩容次数；红黑树转链表的阈值是6（避免频繁树化/链化切换）。
:::

## 📚【面试题目2：HashSet的底层实现原理是什么？与HashMap有何关联？】
### 回答要点关键字
(1) 核心依赖：基于 HashMap 实现，复用其线程不安全特性  
(2) 存储结构：元素作为 HashMap 的 key，value 为固定常量 PRESENT  
(3) 核心特性：无序、不可重复、允许null元素（仅一个）  
(4) 关键关联：所有方法均委托 HashMap 实现，特性与 HashMap 一致
::: hide 打开详情
 🍺基础回答:

 HashSet 本质就是个包装后的 HashMap，它里面没有自己的存储结构，而是维护了一个 HashMap 实例。存元素的时候，把元素当作 HashMap 的 key 存进去，value 固定用一个叫 PRESENT 的空对象。因为 HashMap 的 key 不能重复，所以 HashSet 也就实现了元素不可重复的特性。
 
🎉高级扩展版：

 HashSet 的底层源码非常简洁，核心是 `transient HashMap<E, Object> map;` 和 `private static final Object PRESENT = new Object();`：1. 构造方法：所有 HashSet 构造方法都会初始化内部的 HashMap（如无参构造器调用 new HashMap<>()）；2. 核心方法：add(E e) 本质是 map.put(e, PRESENT)，返回值为 null 则表示添加成功（元素不存在），返回 PRESENT 则表示元素已存在（添加失败）；remove(E e) 是 map.remove(e) == PRESENT；size() 直接返回 map.size()；3. 特性继承：HashSet 的无序性、不可重复性、允许null元素（仅一个，因为 HashMap 只能有一个 null key）、线程不安全等特性，均完全继承自 HashMap；4. 差异点：HashSet 没有键值对概念，仅存储单值，不支持根据索引访问（HashMap 可通过 key 访问 value）。
 
📌 加分项：

 能说出 HashSet 与 TreeSet 的区别（TreeSet 基于 TreeMap，有序，元素需实现 Comparable）；提到 HashSet 的迭代器本质是 HashMap 的 keySet 迭代器；解释为什么 HashSet 不可重复（依赖 HashMap 的 key 去重逻辑，hashCode+equals 校验）；对比 LinkedHashSet（基于 LinkedHashMap，保证插入顺序）。
 
⚠️注意事项：

 HashSet 线程不安全，多线程并发修改需用 Collections.synchronizedSet() 或 CopyOnWriteArraySet；元素作为 HashMap 的 key，需遵循 HashMap 的 key 规范（重写 hashCode() 和 equals()）；PRESENT 是静态常量，所有 HashSet 实例共享同一个对象，节省内存；HashSet 没有 get() 方法（因为 HashMap 的 value 无意义），需通过 contains() 判断元素是否存在。
:::

## 📚【面试题目3：ConcurrentHashMap的底层实现原理（JDK7 vs JDK8）？】
### 回答要点关键字
(1) JDK7 实现：分段锁（Segment）、ReentrantLock 支持、分段独立扩容  
(2) JDK8 实现：CAS+synchronized 桶位锁、数组+链表/红黑树、无锁读  
(3) 核心特性：线程安全、高并发支持、读操作高效、树化机制与 HashMap 一致  
(4) 关键优化：锁粒度缩小（从分段到桶位）、减少锁竞争、提升并发吞吐量
::: hide 打开详情
 🍺基础回答:

 ConcurrentHashMap 是线程安全的 HashMap，JDK7 和 JDK8 的实现不一样。JDK7 用的是分段锁，把整个 map 分成好几个 Segment，每个 Segment 都是个 ReentrantLock，修改数据只锁对应 Segment，其他 Segment 还能正常用，并发性能不错。JDK8 改了，不用分段锁了，而是用 CAS 加 synchronized 锁单个桶位，锁粒度更细，效率更高，底层数据结构和 HashMap 一样，也是数组+链表/红黑树。
 
🎉高级扩展版：

 ConcurrentHashMap 核心是“线程安全+高并发”，两代实现的核心差异：1. JDK7 实现：- 结构：Segment 数组 + HashEntry 数组 + 链表（每个 Segment 对应一个小 HashMap）；- 锁机制：每个 Segment 继承 ReentrantLock，修改操作（put/remove）需获取对应 Segment 锁，不同 Segment 可并发操作；- 扩容：每个 Segment 独立扩容，不影响其他 Segment；- 缺点：分段锁粒度较粗， Segment 数量固定（默认16），高并发下仍有竞争。2. JDK8 实现：- 结构：与 HashMap 一致（Node 数组 + 链表/红黑树）；- 锁机制：读操作无锁（volatile 保证可见性），写操作锁单个桶位（synchronized 修饰 Node 节点），CAS 用于无竞争时的节点插入/更新；- 优化点：锁粒度从“分段”缩小到“桶位”，减少锁竞争；支持数组整体扩容，效率更高；树化机制与 HashMap 一致（链表长度>8且容量≥64）；- 优势：高并发下吞吐量远超 JDK7，读操作无需加锁，性能接近 HashMap。
 
📌 加分项：

 能解释 JDK8 为什么弃用分段锁（锁粒度粗、扩容效率低、ReentrantLock 开销高于 synchronized 优化后）；提到 JDK8 的无锁读实现（Node 节点的 val 和 next 用 volatile 修饰，保证修改后对其他线程可见）；对比 Hashtable（全表锁，并发性能差）；说明 ConcurrentHashMap 不支持 null key/value（避免空指针与并发场景下的歧义）。
 
⚠️注意事项：

 ConcurrentHashMap 是线程安全的，但不保证原子性复合操作（如 putIfAbsent() 是原子的，但 get() + put() 组合需手动加锁）；JDK8 的 synchronized 锁桶位，仅影响当前桶的操作，其他桶可并发；扩容时会阻塞写操作，但读操作仍可进行；避免在高并发场景下使用 size() 方法（需遍历所有桶，开销大，可通过 estimateSize() 估算）。
:::

## 📚【面试题目4：AQS（AbstractQueuedSynchronizer）的底层原理与核心应用？】
### 回答要点关键字
(1) 核心结构：volatile state 同步状态、FIFO 双向同步队列（CLH 队列）  
(2) 核心机制：模板方法模式、CAS 操作 state、线程阻塞/唤醒（LockSupport）  
(3) 核心方法：acquire()（获取锁）、release()（释放锁）、条件变量支持  
(4) 典型应用：ReentrantLock、CountDownLatch、Semaphore、CyclicBarrier
::: hide 打开详情
 🍺基础回答:

 AQS 是 JUC 包的核心，是个抽象类，很多并发工具都是基于它实现的。它主要维护了一个 volatile 的 state 变量（比如锁的状态、计数器）和一个 FIFO 队列（存等待的线程）。核心是模板方法模式，子类只要实现 tryAcquire()、tryRelease() 这些方法，就能用它的 acquire() 和 release() 来处理线程的排队和唤醒。像 ReentrantLock 就是用 state 表示重入次数，CountDownLatch 用 state 表示计数器。
 
🎉高级扩展版：

 AQS 是“抽象队列同步器”，核心目标是封装线程同步的通用逻辑（排队、阻塞、唤醒），让子类聚焦业务逻辑（state 操作）：1. 核心结构：- state：volatile 修饰，存储同步状态（如 ReentrantLock 的重入次数、CountDownLatch 的计数）；- 同步队列：双向链表，节点为 Node（存储线程、等待状态），采用 CLH 队列锁设计，线程获取锁失败后入队，释放锁时唤醒队首线程；2. 核心机制：- 模板方法模式：AQS 提供 acquire()（独占式获取）、release()（独占式释放）、acquireShared()（共享式获取）等模板方法，子类通过重写 tryAcquire()、tryRelease() 等钩子方法实现具体逻辑；- CAS 操作：通过 Unsafe 类的 CAS 方法修改 state，保证原子性；- 线程阻塞/唤醒：通过 LockSupport.park()/unpark() 实现，避免线程忙等；3. 典型应用：- ReentrantLock：state 表示重入次数，tryAcquire() 尝试 CAS 修改 state 为 1（首次获取）或+1（重入）；- CountDownLatch：state 表示计数，countDown() 调用 tryReleaseShared() 递减 state，await() 调用 acquireShared() 等待 state 为 0；- Semaphore：state 表示许可数，acquire() 递减许可，release() 递增许可。
 
📌 加分项：

 能区分独占式（ReentrantLock）和共享式（CountDownLatch）同步；解释同步队列的节点状态（如 CANCELLED、SIGNAL）；提到 AQS 的条件变量（ConditionObject），基于条件队列实现线程按条件等待/唤醒（如 ReentrantLock 的 Condition）；对比 AQS 与 synchronized（AQS 是 API 层面，灵活可控；synchronized 是 JVM 层面，自动释放）。
 
⚠️注意事项：

 子类重写钩子方法（tryAcquire() 等）时，需保证线程安全（依赖 CAS 或锁）；AQS 的同步队列是 FIFO，保证线程等待的公平性（但子类可实现非公平，如 ReentrantLock 默认非公平）；LockSupport.park() 可响应中断，需处理 InterruptedException；state 是 volatile 的，仅保证可见性，原子修改需用 CAS（不可直接赋值）。
:::

## 📚【面试题目5：ReentrantLock的核心特性与底层实现原理？】
### 回答要点关键字
(1) 核心特性：可重入、可公平/非公平、可中断、可定时、条件变量（Condition）  
(2) 底层实现：基于 AQS、state 重入计数、FIFO 同步队列、CAS+synchronized 辅助  
(3) 锁获取：tryLock()（非阻塞）、lock()（阻塞）、lockInterruptibly()（可中断）  
(4) 适用场景：复杂同步需求（如公平锁、超时获取、精准唤醒）
::: hide 打开详情
 🍺基础回答:

 ReentrantLock 是 JUC 包下的可重入锁，比 synchronized 灵活多了。它支持公平锁和非公平锁（默认非公平），能中断等待锁的线程，还能设置超时时间获取锁，避免死锁。底层是基于 AQS 实现的，用 AQS 的 state 变量记录重入次数，比如线程第一次获取锁，state 变成 1，再次获取就变成 2，释放一次减 1，直到 0 才完全释放锁。
 
🎉高级扩展版：

 ReentrantLock 核心是“灵活可控的可重入锁”，底层依赖 AQS 实现：1. 核心特性详解：- 可重入：基于 AQS 的 state 计数，当前线程持有锁时，再次获取锁会递增 state，释放时递减，state=0 时锁完全释放；- 公平/非公平：公平锁通过 AQS 同步队列的 FIFO 顺序获取锁（构造函数传 true），非公平锁会先尝试 CAS 抢锁（默认，效率更高）；- 可中断：lockInterruptibly() 方法支持线程在等待锁时响应中断（抛出 InterruptedException），避免无限等待；- 可定时：tryLock(long timeout, TimeUnit unit) 支持超时获取锁，超时未获取则返回 false；- 条件变量：通过 newCondition() 获取 Condition 对象，支持多线程按条件等待/唤醒（如生产者-消费者模型中，分别唤醒生产者或消费者）。2. 底层实现：- 锁获取：非公平锁调用 lock() 时，先尝试 CAS 修改 state 为 1（抢锁），失败则调用 AQS 的 acquire() 入队等待；公平锁直接入队，按顺序获取；- 锁释放：调用 unlock() 时，调用 AQS 的 release()，递减 state，state=0 时唤醒队首线程；- 条件变量：ConditionObject 是 AQS 的内部类，维护条件队列，await() 会释放锁并入条件队列，signal() 会将条件队列的线程移到同步队列等待获取锁。
 
📌 加分项：

 对比 ReentrantLock 与 synchronized 的核心差异（灵活性、功能特性、死锁排查）；举例说明条件变量的用法（如多条件唤醒，比 synchronized 的 notifyAll() 更精准）；提到 ReentrantLock 的锁释放必须在 finally 块中（否则锁泄漏）；解释非公平锁比公平锁效率高的原因（减少线程切换开销，抢锁成功无需排队）。
 
⚠️注意事项：

 ReentrantLock 必须手动释放锁（unlock()），且需在 finally 块中执行，否则会导致锁泄漏；公平锁虽然公平，但并发性能低于非公平锁，需根据业务场景选择；lockInterruptibly() 需处理 InterruptedException，避免忽略中断；条件变量的 await() 必须在 lock() 和 unlock() 之间调用，否则抛 IllegalMonitorStateException。
:::

## 📚【面试题目6：CopyOnWriteArrayList的底层实现原理与适用场景？】
### 回答要点关键字
(1) 核心机制：写时复制（COW）、读无锁、写加锁、数组副本替换  
(2) 底层结构：volatile 数组（保障读可见性）、ReentrantLock 写锁  
(3) 核心特性：线程安全、迭代器快照一致性、读操作高效、写操作开销大  
(4) 适用场景：读多写少、迭代频繁、对数据一致性要求不高（最终一致性）
::: hide 打开详情
 🍺基础回答:

 CopyOnWriteArrayList 是线程安全的 ArrayList，核心是“写时复制”。就是说读数据的时候不用锁，直接读原数组；写数据（加、删、改）的时候，会先复制一份原数组，在副本上做修改，修改完之后把原数组的引用换成副本，而且写操作的时候会加锁，保证只有一个线程在写。它适合读特别多、写特别少的场景，比如配置信息缓存，读频繁，偶尔更新。
 
🎉高级扩展版：

 CopyOnWriteArrayList 核心是“写时复制（COW）”，底层实现：1. 核心结构：- 存储：volatile Object[] array（volatile 保障读操作的可见性，所有读操作直接访问 array）；- 写锁：ReentrantLock lock（保证写操作的原子性，避免多线程同时复制数组）。2. 核心方法实现：- 读操作（get()）：直接返回 array[index]，无锁，效率极高；- 写操作（add()/set()/remove()）：先获取锁，然后复制原数组到新数组（新数组长度+1 或不变），在新数组上做修改，最后将 array 引用指向新数组，释放锁；- 迭代器：迭代器创建时会持有当前 array 的快照（引用），之后原数组被修改（复制新数组），迭代器仍遍历旧快照，保证迭代过程中数据一致性（快照一致性）。3. 核心特性：- 线程安全：写操作加锁，读操作无锁，基于 volatile 可见性；- 快照一致性：迭代器不抛出 ConcurrentModificationException（与 ArrayList 不同）；- 优缺点：读操作高效（无锁），写操作开销大（复制数组+加锁），内存占用高（修改时存在两个数组副本）。
 
📌 加分项：

 对比 CopyOnWriteArrayList 与 Vector（Vector 读写都加锁，效率低，CopyOnWriteArrayList 读无锁）；对比 CopyOnWriteArraySet（基于 CopyOnWriteArrayList，元素不可重复）；解释为什么迭代器是快照一致性（迭代器持有创建时的 array 引用，原数组修改不影响快照）；提到 CopyOnWriteArrayList 不支持元素为 null（JDK 源码限制，避免空指针歧义）。
 
⚠️注意事项：

 CopyOnWriteArrayList 写操作开销大，不适合写频繁的场景；修改操作（add/remove）后，之前获取的迭代器仍访问旧数据（最终一致性），需注意数据时效性；数组复制时若数组较大，会占用大量内存，且复制过程耗时；不支持 getAndSet() 等原子操作，复合操作需手动加锁。
:::


### 35. 【面试题目】ConcurrentHashMap 的 key 为什么不能为 null？
#### 回答要点关键字
(1) 核心原因：并发场景下的歧义（无法区分“key不存在”和“key为null”）  
(2) 设计原则：并发安全语义明确、与HashMap接口差异化（避免开发误解）  
(3) 实现影响：破坏并发操作（putIfAbsent、getOrDefault）的原子性语义  
(4) 设计哲学：并发组件优先保证语义清晰，牺牲少量灵活性（允许null key）  
::: hide 打开详情
 🍺基础回答:

 主要是并发场景下会有歧义问题。比如你用get(null)返回null，到底是这个key本身就是null，还是根本没有这个key？单线程的HashMap能容忍，因为开发者自己清楚，但ConcurrentHashMap是并发场景用的，多线程操作时根本没法判断。而且它的一些并发方法比如putIfAbsent（不存在才插入），如果key能为null，语义就乱了，没法保证原子性。所以设计时就禁止key和value为null，避免这种歧义。
 
🎉高级扩展版：

 1. 歧义问题的深层影响：  
    - 并发操作语义冲突：ConcurrentHashMap的核心价值是提供线程安全的原子操作（如putIfAbsent、computeIfAbsent）。若允许key为null，当get(null)返回null时，无法确定是“key不存在”还是“key为null且value为null”，导致原子操作无法判断是否需要执行（如putIfAbsent(null, value)无法确定是否该插入）。  
    - 多线程一致性问题：比如线程A put(null, "a")，线程B put(null, "b")，若允许null key，需要保证原子性，但null key的哈希计算（HashMap中null key哈希为0）会导致并发冲突，且语义模糊。  
 2. 接口一致性设计：  
    - HashMap允许key/value为null（单线程场景无歧义），但ConcurrentHashMap作为并发替代方案，需通过接口限制明确区分，避免开发者混淆两者用法，减少线程安全问题。  
    - 源码层面：ConcurrentHashMap的put、get等方法会主动检查key/value是否为null，抛NullPointerException，从底层阻断歧义场景。  
 3. 设计权衡：禁止null key/value牺牲了少量灵活性，但换来了并发语义的清晰性，符合“并发组件优先保证安全和语义明确”的设计哲学。  
 
📌 加分项：

 1. 对比HashMap：HashMap允许null key是因为单线程场景下，开发者可通过containsKey(null)判断key是否存在，而ConcurrentHashMap中containsKey和get存在并发间隙（可能get返回null后，containsKey返回true），无法可靠判断；  
 2. 源码细节：ConcurrentHashMap的哈希计算逻辑中，无针对null key的特殊处理（HashMap会将null key映射到索引0），进一步说明其设计上就不支持null key；  
 3. 替代方案：若需存储“无key”的逻辑，可使用特殊占位符（如new Object()）作为key，明确语义且不破坏并发安全。  
 
⚠️注意事项：

 1. 开发中需避免将null作为ConcurrentHashMap的key/value，否则直接抛异常，影响程序运行；  
 2. 迁移HashMap到ConcurrentHashMap时，需先清理null key/value，避免兼容性问题；  
 3. 不要试图通过反射等方式强制插入null key，会破坏ConcurrentHashMap的并发语义，导致不可预期的线程安全问题。  
:::


### 41. 【面试题目】Java 对象创建过程？
#### 回答要点关键字
(1) 核心步骤：类加载检查、内存分配、初始化零值、设置对象头、执行init方法  
(2) 内存分配：指针碰撞、空闲列表（取决于堆内存是否规整）  
(2) 内存分配：指针碰撞、空闲列表（取决于堆内存是否规整）  
(3) 线程安全：TLAB（本地线程分配缓冲）、CAS+失败重试  
(4) 关键区别：clinit方法（类初始化）与init方法（对象初始化）的执行时机  
::: hide 打开详情
 🍺基础回答:

 Java创建对象大概分五步。首先虚拟机要检查这个类有没有加载、链接、初始化过，没的话先执行类加载。然后给对象分配内存，从堆里找块空间。分配完内存后，会把这块内存的所有字段初始化为零值（比如int=0、Object=null）。接下来设置对象头，里面存类的元数据指针、哈希码、锁状态这些信息。最后执行构造方法（init方法），给对象的字段赋初始值，还有代码里的业务逻辑，这步完了对象才算真正创建好。另外，分配内存时为了线程安全，虚拟机用TLAB或者CAS的方式，避免多个线程抢一块内存。
 
🎉高级扩展版：

 1. 详细步骤拆解：  
    (1) 类加载检查：当执行new指令时，JVM先检查常量池是否有该类的符号引用，且该类是否已完成加载、链接、初始化（即类初始化阶段，执行clinit方法）。若未加载，则触发类加载流程。  
    (2) 内存分配：根据类元数据确定对象所需内存大小，从堆中分配空间。分配方式有两种：  
      - 指针碰撞：堆内存规整（Serial、ParNew等收集器），用过的内存和空闲内存之间有一个指针，分配时指针向空闲区移动对应大小；  
      - 空闲列表：堆内存不规整（CMS等收集器），JVM维护空闲内存块列表，分配时从列表中找合适的块。  
    (3) 初始化零值：将分配的内存空间（除对象头外）全部初始化为零值（boolean=false、byte=0、reference=null等）。这一步保证了对象字段无需显式初始化就能直接使用默认值。  
    (4) 设置对象头：给对象头赋值，包含三部分信息：  
      - 类元数据指针：指向对象所属类的元数据（确定对象的类型）；  
      - 哈希码、GC分代年龄、锁状态标志等运行时数据；  
      - 数组长度（仅数组对象有，记录数组元素个数）。  
    (5) 执行init方法：这是对象创建的最后一步，执行构造方法（包括默认构造器、显式构造器），按代码逻辑初始化对象字段（如给name赋值“张三”）、调用父类构造方法等。init方法执行完毕，对象创建完成。  
 2. 线程安全保障：  
    - TLAB（Thread Local Allocation Buffer）：JVM为每个线程分配独立的内存缓冲区，线程创建对象时优先在TLAB中分配，避免线程间竞争，提升效率；TLAB耗尽后，用CAS+失败重试的方式分配堆内存。  
 3. 关键区别：  
    - clinit方法：类初始化方法，在类加载的初始化阶段执行，仅执行一次（初始化静态变量、静态代码块）；  
    - init方法：对象初始化方法，在对象创建的最后一步执行，每个对象创建时都会执行（初始化实例变量、实例代码块、构造方法）。  
 
📌 加分项：

 1. 逃逸分析优化：若JVM通过逃逸分析判断对象不会逃出当前线程（如仅在方法内使用），会将对象分配在栈上（而非堆上），减少GC压力；  
 2. 对象头细节：对象头的锁状态标志会随着锁升级（偏向锁→轻量级锁→重量级锁）动态变化，影响对象内存布局；  
 3. 特殊对象创建：通过clone()创建对象时，会跳过类加载检查和init方法，直接复制已有对象的内存（包括零值初始化后的字段和对象头）；通过反序列化创建对象时，也会跳过init方法，从字节流中恢复对象状态。  
 
⚠️注意事项：

 1. 类加载检查是对象创建的前提，若类未加载或初始化失败（如静态代码块抛异常），会抛出NoClassDefFoundError或ExceptionInInitializerError；  
 2. 内存分配时若堆内存不足，会触发GC，GC后仍不足则抛出OutOfMemoryError；  
 3. init方法执行时若构造方法抛异常，对象创建失败，但已分配的内存会被GC回收；  
 4. 数组对象的内存分配需额外存储数组长度，且数组类的元数据是JVM动态生成的（如[Ljava.lang.String;）。  
:::


### 🔒 `synchronized` 底层实现：JVM 级别锁机制解析
#### 1. 核心底层结构
`synchronized` 是 JVM 内置锁（隐式锁），底层依赖 **对象头 Mark Word** + **Monitor（管程）** 实现互斥与同步，核心是「通过对象关联锁状态，通过 Monitor 控制线程竞争」。

#### 2. 核心组件拆解
##### （1）对象头 Mark Word（锁状态载体）
- **作用**：存储对象的锁状态、持有锁的线程 ID 等核心信息，是 JVM 识别锁状态的关键。
- **结构（32位JVM示例，压缩指针开启）**：
  | 锁状态       | Mark Word 存储内容                          | 说明                                  |
  |--------------|---------------------------------------------|---------------------------------------|
  | 无锁状态     | 哈希码（31位） + 无锁标记（1位）            | 对象未被锁定，仅存储哈希值            |
  | 偏向锁       | 线程ID（23位） + Epoch（2位） + 偏向标记（1位） | 单线程竞争时，直接关联线程ID，无CAS开销 |
  | 轻量级锁     | 指向线程栈中锁记录的指针（30位） + 轻量标记（2位） | 多线程交替竞争，用CAS自旋获取锁        |
  | 重量级锁     | 指向 Monitor 的指针（30位） + 重量标记（2位） | 多线程并发竞争，进入 Monitor 阻塞队列  |

- **核心逻辑**：线程竞争锁时，JVM 会修改 Mark Word 的「锁状态标记」和「关联数据」（线程ID/Monitor指针），通过 CAS 操作保证原子性。

##### （2）Monitor（管程/互斥锁核心）
- **本质**：JVM 为每个对象关联的一个「同步监视器」，是操作系统级别的互斥锁（依赖 pthread_mutex 实现），负责控制线程的进入、阻塞、唤醒。
- **核心结构（3个关键队列）**：
  | 组件         | 作用                                  | 线程状态                              |
  |--------------|---------------------------------------|---------------------------------------|
  | Owner（拥有者） | 存储当前持有锁的线程                     | 线程处于「运行中」，独占 Monitor      |
  | EntryList（入口队列） | 等待获取锁的线程集合（锁被占用时进入）   | 线程处于「阻塞状态」（BLOCKED）        |
  | WaitSet（等待队列） | 调用 `wait()` 后释放锁的线程集合         | 线程处于「等待状态」（WAITING/TIMED_WAITING） |

- **Monitor 工作流程**：
  1. 线程请求锁时，先尝试通过 CAS 修改 Mark Word 抢占锁；
  2. 抢占失败（锁已被占用）：线程进入 EntryList 阻塞；
  3. 持有锁的线程（Owner）释放锁（执行完同步代码块/调用 `wait()`）：
     - 若调用 `wait()`：线程释放锁，进入 WaitSet 等待，需被 `notify()` 唤醒后重新进入 EntryList 竞争；
     - 若执行完毕：JVM 唤醒 EntryList 中一个线程，使其成为新的 Owner，抢占锁。

#### 3. `synchronized` 锁升级流程（基于 Mark Word + Monitor）
1. **无锁 → 偏向锁**：单线程首次获取锁，JVM 在 Mark Word 中记录当前线程ID，后续该线程可直接进入同步块（无竞争，零开销）。
2. **偏向锁 → 轻量级锁**：出现第二个线程竞争锁，偏向锁撤销，JVM 为线程在栈中创建「锁记录」，通过 CAS 自旋尝试修改 Mark Word 为轻量级锁指针，自旋失败则升级。
3. **轻量级锁 → 重量级锁**：多线程频繁竞争（自旋超过阈值/自旋时线程数过多），轻量级锁膨胀为重量级锁，Mark Word 指向 Monitor，竞争线程进入 EntryList 阻塞（避免 CPU 空转）。

#### 4. 核心总结
- `Mark Word` 是「锁状态的存储载体」，通过修改其内容标识锁的类型和持有线程；
- `Monitor` 是「锁的执行引擎」，通过 Owner/EntryList/WaitSet 控制线程的竞争与同步；
- `synchronized` 的高效性源于「锁升级机制」：从无锁→偏向锁→轻量级锁→重量级锁，按需升级，平衡性能与并发。
####
ReentrantLock 与 synchronized 对比（核心区别）

对比维度	ReentrantLock（显式锁）	synchronized（隐式锁）
锁的获取 / 释放	显式：lock()/unlock()（必须手动释放，需 finally）	隐式：JVM 自动获取释放（进入 / 退出同步块 / 方法）
公平性	支持公平 / 非公平锁（构造函数指定）	仅支持非公平锁（默认）
线程协作	支持多个 Condition 队列（精细唤醒）	仅支持一个 WaitSet 队列（wait()/notify()）
可中断性	支持（lockInterruptibly()）	不支持（阻塞时无法中断）
尝试锁	支持（tryLock()，非阻塞 / 超时）	不支持（仅阻塞式抢锁）
锁状态查询	支持（isLocked()/getHoldCount() 等）	不支持（无公开 API 查询）
底层实现	AQS（双向链表 + 状态变量）	Mark Word + Monitor 管程
锁升级	无（始终是重量级锁的语义，AQS 队列实现）	支持（无锁→偏向锁→轻量级锁→重量级锁）
适用场景	复杂并发（如多条件等待、可中断、超时抢锁）	简单并发（如普通同步、单例、基础原子操作）
性能	高并发场景下性能优于 synchronized（JDK 1.6 后 synchronized 优化后差距缩小）	低并发场景下开销小（JVM 优化充分）

