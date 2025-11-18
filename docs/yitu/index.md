---
title: Yitu 笔记
description: Yitu 笔记
---

::: hide Java 基础
集合

    - `Hashmap`:数组链表红黑树，8,64,0.75 Entry，扩容2倍新数组，
    - `LinkedHashMap` 继承HashMap
    - `Hashset` Hashmap key， value PRESENT，去重相同元素认定（hashcode + equals - true）
    - `transient` 序列化排除（比如password）
    - `ConcurrentHashMap` 7分段锁，8 cas+synchonized
    - `TreeMap` 红黑树，key必须可比较，天然有序
    - `TreeSet` 基于TreeMap，key value PRESENT，去重相同元素认定（compareTo返回0）
    - `HashTable` 数组+链表，默认11，0.75，不允许null，hash未优化，冲突概率高 
    - `ConcurrentSkipListMap` 跳表，线程安全，效率高，key必须可比较，天然有序 
    - `ConcurrentSkipListSet` 跳表，线程安全，效率高，key value PRESENT，去重相同元素
    - `LinkedHashSet` 继承HashSet，底层是LinkedHashMap，key value PRESENT，去重相同元素
    --- 
    - `synchronized` 对象包含markword jvm级别锁，支持无锁（初始），偏向（单线程，Mark Word 记录线程 ID），轻（多线程交替 CAS抢占） 重量级（多线程抢占  markword指向monitor，失败进entrylist） ；对象头markword(锁状态和线程id+类型指针)+Monitor(互斥锁 owner EEntryList Waitlist)； 流程： 一个线程try 设置Monitor Owner为自己，失败进Waitlist，
    - 线程是否 “同时争抢锁”（竞争重叠度）：重量级（不是线程数决定） 
    - T1 synchronized(LOCK){.. LOCK.`wait`()...} ==> T1 Waitlist
    - T2 synchronized(LOCK){.. LOCK.`notify`()...} ==> 唤醒 Waitlist中T1
    - 互斥，部分代码同步（自定义锁 object lock, static 代码块），，需区分「实例级互斥锁this」和「全局级互斥 - 锁 类.class」 
    - 单例模式（volatile+双重检查锁，避免重复创建）
    - ReentrantLock 可公平/非公平、 AQS「状态变量 + 双向链表队列」 、CAS+volatile、自定义同步状态 、Lock() 是非阻塞的、
    - CountDownLatch  produceLatch = new CountDownLatch(2);                  
      -final:produceLatch.countDown();  
      - produceLatch.await(); 等待 变0
      - produceLatch.await(2, TimeUnit.SECONDS); // 超时 2 秒,阻塞2s
    - Semaphore 基于 AQS（「AQS 状态变量（state）+ 双向等待队列」，且 Semaphore 是 AQS 的「共享模式」实现（区别于 ReentrantLock 的独占模式）  
      - acquire 获取许可
      -  release 释放许可
      -  tryAcquire 尝试获取许可 
---
-  ❓ synchronized 和 ReentrantLock 的区别是什么？底层实现原理有何不同？
   -  区别：实现原理（s是jvm内置锁，字节码指令实现；R API层面，Java代码实现），灵活性（s非公平锁，R支持非/公平锁，R可以中断锁等待）、功能（s 1.6后性能优化接近R，R更稳定） 、性能
-  ❓ volatile ？ 内存屏障，写操作加内存屏障，阻止后面指令，读操作加屏障保证读主内存最新。修改变量后主动刷新到主内存。可以保障可见性、有序性，不保障原子性。 无锁CAS。 
   -  场景：停止标记，
   -  CAS漏洞 ABA问题。大部分场景不影响，少部分影响。 比如链表A-B-C，T1想删除B（Anext修改为C），但是T2先删除B，然后在C增加了B（AnextCnextB）；后面T1再做删除，就会把新加的B删除变成（AnextC）。 解决方案（1）版本号+值一起作为CAS值比较 （2）使用带版本号的原子类（Java 自带，首选）AtomicStampedReference 和 AtomicMarkableReference，专门解决 ABA 问题：AtomicStampedReference：给变量绑定一个 “int 类型的版本号”，每次修改变量时，版本号自动 +1；
AtomicMarkableReference：给变量绑定一个 “boolean 类型的标记”（仅表示 “是否被修改过”，不记录修改次数）
-  ❓HashMap原理？ 数据结构，16, 0.75,12。64,8 。 key hash，冲突 加快查询效率，树化，扩容迁移
-  ❓HshSet： Hashmap，key是值，value 常量PRESENT。 eques + hash
-  ❓ConcurrentHashMap： synchronized+分段锁。 key不能为null（歧义）
-  ❓AQS 抽象队列同步器：volatile state 同步状态、FIFO 双向同步队列（CLH 队列） ； acquire()（获取锁）、release()
-  ❓ReentrantLock： 基于 AQS、state 重入计数、FIFO 同步队列、CAS+synchronized 辅助。tryLock()（非阻塞）、lock()（阻塞）、lockInterruptibly()（可中断）  公平锁
-  ❓CopyOnWriteArrayList 读多写少。 volatile 数组（保障读可见性）、ReentrantLock 写锁
-  
:::

::: hide Redis
- String(json 缓存对象 限流计数器，分布式锁)、Hash（字典，kv，用户消息，配置）、List（消息队列，任务队列，「有序、可重复、支持两端插入 / 删除」）、Set（无序去重， 好友，抽奖）、ZSet （有序，排行榜，延迟队列），Bitmap 活跃用户 ， 或者 签到 
  - Bitmap（SETBIT key offset value） 比如签到：用户 ID=1001，2025 年 11 月 5 号签到（5 号对应 offset=4）  SETBIT user:sign:1001:202511 4 1 
  - 查询某一天是否签到：GETBIT user:sign:1001:202511 4
  - 统计某月签到：BITCOUNT user:sign:1001:202511
  - 查询当月第一次 / 最后一次签到日期BITPOS user:sign:1001:202511 1
  - 最后一次签到（需结合当月天数，反向查找）# 思路：从当月最后一天的偏移量（如30天=29）反向查第一个1  BITPOS user:sign:1001:202511 1 29 29  # 从offset=29开始查，步长-1
  - 统计连续签到天数（核心业务逻辑） java 从今天向前遍历，直到遇到0或offset<0

:::


#### jstatck 分析死锁  
 jps 获取 列表 pid，  jstatck pid

#### 数据库连接池爆满
可能： 线程数不够了 并发请求太高了 有慢SQL
思路： 看流量监控，没有异常流量。
      查下SQL 耗时，慢SQL日志。 
      更新工单
      WHERE id = ?   AND deleted = ?   AND lock_version = ? 
简单的一个更新语句，其中使用了乐观锁进行并发控制。 热点行更新 


#### 