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

