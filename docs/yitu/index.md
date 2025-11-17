---
title: Yitu 笔记
description: Yitu 笔记
---
## 基础部分
- Hashmap:数组(Node<K,V> implements Map.Entry<K,V>)-链表红黑树，keyhash定位筒，hash冲突链表。链表长度超过8，数组长度超过64，转红黑树。当数组长度小于64，链表长度小于8，转链表。 扩容过程：新建2倍数组，遍历旧数组，keyhash定位桶位，迁移元素。（初始容量（16）、负载因子（0.75））
- Hashset: Hashmap实现， key存值，value存PRESENT（复用 HashMap 的初始容量（16）、负载因子（0.75））
- 