# Java 中 HashMap 的扩容机制是怎样的？

**难度**：中等

**创建时间**：2025-10-06 06:01:00

## 答案
在 Java 中，`HashMap` 的扩容机制是其核心特性之一，它通过动态调整内部数组（桶）的大小来平衡查询效率和内存占用。以下是 `HashMap` 扩容机制的详细解析，包括触发条件、扩容过程、性能影响及优化策略。

---

### **一、扩容的触发条件**
`HashMap` 的扩容由两个关键因素决定：
1. **负载因子（Load Factor）**  
   - 默认负载因子为 `0.75`（可通过构造函数调整）。  
   - 当已存储的键值对数量（`size`）超过 **容量（capacity） × 负载因子** 时，触发扩容。  
   - 例如：默认初始容量为 `16`，负载因子为 `0.75`，则当 `size > 16 × 0.75 = 12` 时扩容。

2. **插入时发现哈希冲突过多**  
   - 如果在插入过程中发现某个桶（bucket）中的链表过长（超过 `TREEIFY_THRESHOLD = 8`），且当前容量未达到最小树化阈值（`MIN_TREEIFY_CAPACITY = 64`），会优先触发扩容以减少冲突。

---

### **二、扩容的核心过程**
#### **1. 扩容步骤**
1. **创建新数组**  
   - 新容量为旧容量的 **2 倍**（`newCapacity = oldCapacity << 1`）。  
   - 新阈值（threshold）也更新为 `newCapacity × loadFactor`。  
   - 例如：旧容量为 `16`，扩容后新容量为 `32`，阈值变为 `24`。

2. **重新哈希（Rehash）**  
   - 遍历旧数组中的每个桶，将所有键值对重新计算哈希值，并分配到新数组的对应位置。  
   - 哈希计算方式：  
     ```java
     // JDK 8 优化后的哈希计算（扰动函数）
     static final int hash(Object key) {
         int h;
         return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
     }
     ```
     通过 `h ^ (h >>> 16)` 将高位哈希与低位异或，减少高位信息丢失，提升哈希分布均匀性。

3. **处理链表和红黑树**  
   - 如果桶中是链表结构，直接遍历链表并重新插入到新桶。  
   - 如果是红黑树结构，可能需要拆分红黑树（当新桶的索引不同时）或保持原结构。

#### **2. 扩容的代码逻辑（JDK 8）**
```java
final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;
    
    // 计算新容量和阈值
    if (oldCap > 0) {
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        newCap = oldCap << 1; // 容量翻倍
        newThr = oldThr << 1; // 阈值翻倍
    } else if (oldThr > 0) {
        newCap = oldThr; // 初始化时指定了阈值
    } else {
        newCap = DEFAULT_INITIAL_CAPACITY; // 默认初始容量16
        newThr = (int)(DEFAULT_INITIAL_CAPACITY * DEFAULT_LOAD_FACTOR);
    }
    
    // 更新阈值
    if (newThr == 0) {
        float ft = (float)newCap * loadFactor;
        newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                  (int)ft : Integer.MAX_VALUE);
    }
    threshold = newThr;
    
    // 创建新数组并迁移数据
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    table = newTab;
    if (oldTab != null) {
        for (int j = 0; j < oldCap; ++j) {
            Node<K,V> e;
            if ((e = oldTab[j]) != null) {
                oldTab[j] = null;
                if (e.next == null) {
                    // 单个节点直接迁移
                    newTab[e.hash & (newCap - 1)] = e;
                } else if (e instanceof TreeNode) {
                    // 红黑树拆分
                    ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                } else {
                    // 链表拆分（优化为低位链和高位链）
                    Node<K,V> loHead = null, loTail = null;
                    Node<K,V> hiHead = null, hiTail = null;
                    Node<K,V> next;
                    do {
                        next = e.next;
                        if ((e.hash & oldCap) == 0) {
                            if (loTail == null) loHead = e;
                            else loTail.next = e;
                            loTail = e;
                        } else {
                            if (hiTail == null) hiHead = e;
                            else hiTail.next = e;
                            hiTail = e;
                        }
                    } while ((e = next) != null);
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;
                    }
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;
                    }
                }
            }
        }
    }
    return newTab;
}
```

---

### **三、扩容的性能影响**
1. **时间复杂度**  
   - 扩容时需要遍历所有键值对并重新哈希，时间复杂度为 **O(n)**。  
   - 频繁扩容会导致性能抖动，尤其在数据量大时。

2. **优化策略**  
   - **预分配容量**：通过构造函数指定初始容量（`new HashMap<>(initialCapacity)`），避免多次扩容。  
   - **合理设置负载因子**：根据业务场景调整负载因子（如对查询性能要求高时，可降低负载因子）。  
   - **JDK 8 的链表拆分优化**：在扩容时，通过 `e.hash & oldCap` 判断节点是否需要移动到新索引（`j + oldCap`），减少不必要的计算。

---

### **四、扩容的常见问题**
1. **为什么容量必须是 2 的幂次方？**  
   - `HashMap` 通过 `hash & (capacity - 1)` 计算索引，当容量为 2 的幂次方时，`capacity - 1` 的二进制全为 1，能充分利用哈希值的高位信息，避免哈希冲突。  
   - 例如：容量为 16（`0b10000`），`capacity - 1 = 15`（`0b1111`），`hash & 15` 等价于取哈希值的低 4 位。

2. **多线程下的扩容问题**  
   - `HashMap` 是非线程安全的，多线程环境下扩容可能导致 **死循环**（JDK 7 的头插法问题）或数据不一致。  
   - 解决方案：使用 `ConcurrentHashMap` 或 `Collections.synchronizedMap`。

3. **树化与退化**  
   - 当链表长度超过 `TREEIFY_THRESHOLD = 8` 且容量 ≥ `MIN_TREEIFY_CAPACITY = 64` 时，链表转为红黑树。  
   - 当删除节点导致链表长度 ≤ `UNTREEIFY_THRESHOLD = 6` 时，红黑树退化为链表。

---

### **五、总结**
| 关键点               | 说明                                                                 |
|----------------------|----------------------------------------------------------------------|
| **触发条件**         | `size > capacity × loadFactor` 或哈希冲突过多                        |
| **扩容方式**         | 容量翻倍（`newCapacity = oldCapacity << 1`）                         |
| **重新哈希**         | 通过 `hash & (newCapacity - 1)` 计算新索引                            |
| **性能优化**         | 预分配容量、链表拆分优化（JDK 8）、避免多线程竞争                     |
| **线程安全**         | 多线程下使用 `ConcurrentHashMap`                                     |

**最佳实践**：  
- 初始化时预估数据量并设置合适容量（如 `new HashMap<>(100)`）。  
- 避免在高频修改的场景下使用 `HashMap` 的同步包装类（如 `Collections.synchronizedMap`），优先选择 `ConcurrentHashMap`。  
- 监控 `HashMap` 的 `size` 和 `loadFactor`，及时调整参数。
