# Java 中 ConcurrentHashMap 1.7 和 1.8 之间有哪些区别？

**难度**：中等

**创建时间**：2025-10-02 12:59:58

## 答案
在 Java 中，`ConcurrentHashMap` 是并发编程中常用的线程安全哈希表实现。从 **JDK 1.7** 到 **JDK 1.8**，其内部实现发生了重大优化，主要区别体现在 **数据结构**、**并发控制** 和 **性能优化** 上。以下是详细对比：

---

## **1. 数据结构差异**
### **JDK 1.7：分段锁（Segment + HashEntry）**
- **分段锁（Segmentation）**：  
  - 将整个哈希表划分为多个 **Segment**（默认 16 个），每个 Segment 是一个独立的子哈希表。
  - 每个 Segment 内部使用 **链表**（`HashEntry` 数组 + 链表）存储键值对。
  - 插入/查询时，先定位到 Segment，再操作该 Segment 内部的链表。
- **优点**：  
  - 分段锁减少了锁的粒度，不同 Segment 可以并行操作。
- **缺点**：  
  - 分段数量固定（16），无法动态扩展。
  - 内存占用较高（每个 Segment 需要额外存储元数据）。

```java
// JDK 1.7 的 Segment 结构
static final class Segment<K,V> extends ReentrantLock implements Serializable {
    volatile HashEntry<K,V>[] table; // 链表数组
    int count; // 元素数量
}
```

### **JDK 1.8：同步锁 + 红黑树（Node + 树化）**
- **同步锁（Synchronized + CAS）**：  
  - 取消 Segment 分段，直接使用 **Node 数组 + 链表/红黑树** 存储键值对。
  - 对数组头节点（`table`）使用 **CAS** 操作，对链表/树节点使用 **Synchronized** 锁。
- **红黑树优化**：  
  - 当链表长度超过 **8** 且数组长度 ≥ **64** 时，链表转为红黑树，减少查询时间复杂度（从 O(n) → O(log n)）。
- **优点**：  
  - 锁粒度更细（仅锁当前节点），并发性能更高。
  - 动态扩容，内存占用更优。
- **缺点**：  
  - 树化操作可能带来额外开销（但概率较低）。

```java
// JDK 1.8 的 Node 结构
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    volatile V val;
    volatile Node<K,V> next; // 链表或树节点
}
```

---

## **2. 并发控制差异**
### **JDK 1.7：分段锁（ReentrantLock）**
- 每个 Segment 是一个独立的 `ReentrantLock`，操作不同 Segment 时不会阻塞。
- **锁范围**：整个 Segment（包括链表遍历和修改）。
- **问题**：  
  - 如果多个线程操作同一个 Segment，仍会串行化。
  - Segment 数量固定，无法适应高并发场景。

### **JDK 1.8：Synchronized + CAS**
- **CAS 操作**：  
  - 初始化数组（`resizeStamp`）和扩容时使用 CAS 保证原子性。
- **Synchronized 锁**：  
  - 仅对当前操作的节点（或桶头）加锁，减少锁竞争。
- **锁升级**：  
  - 链表 → 红黑树时无需额外锁（通过 `tryLock` 尝试获取锁）。
- **优势**：  
  - 锁粒度更细，并发吞吐量显著提升。

---

## **3. 扩容机制差异**
### **JDK 1.7：分段扩容**
- 每个 Segment 独立扩容，但扩容时需要锁定整个 Segment。
- **问题**：  
  - 扩容期间其他线程无法访问该 Segment。

### **JDK 1.8：全局扩容 + 协助扩容**
- **全局扩容**：  
  - 所有节点共享一个扩容标记（`sizeCtl`），通过 CAS 控制。
- **协助扩容**：  
  - 线程在插入数据时，如果检测到正在扩容，会主动协助迁移数据（ForwardingNode 机制）。
- **优势**：  
  - 扩容期间仍可并发读写，减少阻塞。

---

## **4. 性能对比**
| **特性**               | **JDK 1.7**                     | **JDK 1.8**                     |
|------------------------|----------------------------------|----------------------------------|
| **数据结构**           | Segment + 链表                  | Node 数组 + 链表/红黑树         |
| **锁粒度**             | Segment 级别（粗粒度）          | 节点级别（细粒度）              |
| **查询复杂度**         | O(n)（链表）                    | O(log n)（红黑树）              |
| **扩容方式**           | 分段独立扩容                    | 全局协助扩容                    |
| **内存占用**           | 较高（固定 16 个 Segment）      | 较低（动态扩展）                |
| **并发性能**           | 中等（分段锁竞争）              | 高（CAS + Synchronized）        |

---

## **5. 代码示例对比**
### **JDK 1.7 插入操作**
```java
// 定位到 Segment，然后加锁操作链表
final V put(K key, int hash, V value, boolean onlyIfAbsent) {
    Segment<K,V> s = segmentFor(hash);
    return s.put(key, hash, value, onlyIfAbsent);
}
```

### **JDK 1.8 插入操作**
```java
// 直接定位到桶，通过 CAS 或 Synchronized 操作节点
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        if (tab == null || (n = tab.length) == 0)
            tab = initTable(); // CAS 初始化数组
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            if (casTabAt(tab, i, null, new Node<>(hash, key, value)))
                break; // CAS 插入新节点
        } else {
            synchronized (f) { // 加锁操作链表或树
                // ... 链表/树插入逻辑
            }
        }
    }
    addCount(1L, binCount);
    return null;
}
```

---

## **6. 总结**
| **版本** | **核心优化** | **适用场景** |
|----------|--------------|--------------|
| JDK 1.7  | 分段锁       | 中低并发     |
| JDK 1.8  | 同步锁 + 红黑树 + 协助扩容 | 高并发、大规模数据 |

### **推荐选择**
- **JDK 1.8+** 的 `ConcurrentHashMap` 是首选，尤其在 **高并发读写** 场景下性能更优。
- JDK 1.7 的分段锁设计在 JDK 1.8 中已被完全替代，新项目无需考虑。

通过优化数据结构和并发控制，JDK 1.8 的 `ConcurrentHashMap` 在保证线程安全的同时，显著提升了吞吐量和资源利用率。
