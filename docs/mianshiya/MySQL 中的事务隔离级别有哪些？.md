# MySQL 中的事务隔离级别有哪些？

**难度**：简单

**创建时间**：2025-10-05 12:10:56

## 答案
MySQL 中的事务隔离级别用于控制多个事务并发执行时的可见性规则，避免因并发操作导致的数据不一致问题（如脏读、不可重复读、幻读）。MySQL 支持 **4 种标准隔离级别**，从低到高分别为：**读未提交（Read Uncommitted）**、**读已提交（Read Committed）**、**可重复读（Repeatable Read）** 和 **串行化（Serializable）**。以下是详细解析：

---

### **1. 隔离级别的作用**
事务隔离级别通过限制事务间的交互方式，解决以下并发问题：
- **脏读（Dirty Read）**：读取到其他事务未提交的修改（可能导致回滚后数据不一致）。
- **不可重复读（Non-repeatable Read）**：同一事务内多次读取同一数据，结果因其他事务的修改而不同。
- **幻读（Phantom Read）**：同一事务内多次查询，结果因其他事务插入或删除数据而不同（行数变化）。

---

### **2. MySQL 的 4 种隔离级别**
#### **（1）读未提交（Read Uncommitted）**
- **规则**：事务可以读取其他事务未提交的修改（最低隔离级别）。
- **并发问题**：
  - 允许脏读、不可重复读、幻读。
- **适用场景**：
  - 对数据一致性要求极低，且性能优先的场景（如日志记录）。
- **示例**：
  ```sql
  SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
  START TRANSACTION;
  SELECT * FROM users WHERE id = 1; -- 可能读到其他事务未提交的修改
  COMMIT;
  ```

#### **（2）读已提交（Read Committed）**
- **规则**：事务只能读取其他事务已提交的修改。
- **并发问题**：
  - 解决脏读，但允许不可重复读和幻读。
- **Oracle/SQL Server 默认级别**：
  - MySQL 默认不使用此级别，但可通过配置支持。
- **适用场景**：
  - 需要避免脏读，但对重复读取结果一致性要求不高的场景（如统计报表）。
- **示例**：
  ```sql
  SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
  START TRANSACTION;
  SELECT * FROM users WHERE id = 1; -- 只能读到已提交的数据
  COMMIT;
  ```

#### **（3）可重复读（Repeatable Read）**
- **规则**：同一事务内多次读取同一数据，结果始终一致（MySQL 默认级别）。
- **并发问题**：
  - 解决脏读和不可重复读，但允许幻读（通过多版本并发控制 MVCC 和间隙锁优化）。
- **MySQL 特性**：
  - 通过 **MVCC（多版本并发控制）** 实现快照读，避免不可重复读。
  - 通过 **间隙锁（Gap Lock）** 防止幻读（在特定查询条件下）。
- **适用场景**：
  - 需要事务内数据一致性的场景（如金融交易）。
- **示例**：
  ```sql
  SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
  START TRANSACTION;
  SELECT * FROM users WHERE age > 20; -- 多次读取结果相同
  COMMIT;
  ```

#### **（4）串行化（Serializable）**
- **规则**：所有事务串行执行，完全隔离（最高隔离级别）。
- **并发问题**：
  - 解决脏读、不可重复读、幻读，但性能最低。
- **实现方式**：
  - 通过强制锁机制（如共享锁、排他锁）实现。
- **适用场景**：
  - 对数据一致性要求极高，且并发量低的场景（如银行核心系统）。
- **示例**：
  ```sql
  SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  START TRANSACTION;
  SELECT * FROM users WHERE status = 'active'; -- 事务会阻塞其他写操作
  COMMIT;
  ```

---

### **3. 隔离级别与并发问题的关系**
| **隔离级别**         | **脏读** | **不可重复读** | **幻读** | **性能** |
|----------------------|----------|----------------|----------|----------|
| 读未提交（RU）       | ❌ 可能   | ❌ 可能         | ❌ 可能   | 最高     |
| 读已提交（RC）       | ✅ 解决   | ❌ 可能         | ❌ 可能   | 高       |
| 可重复读（RR）       | ✅ 解决   | ✅ 解决         | ⚠️ 部分解决 | 中       |
| 串行化（S）          | ✅ 解决   | ✅ 解决         | ✅ 解决   | 最低     |

> **注**：MySQL 的 `REPEATABLE READ` 通过 MVCC 和间隙锁部分解决幻读问题，但非完全避免。

---

### **4. 如何设置隔离级别？**
#### **（1）全局设置（影响所有新会话）**
```sql
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

#### **（2）会话级设置（仅影响当前连接）**
```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

#### **（3）事务内设置（仅影响当前事务）**
```sql
START TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- 事务操作
COMMIT;
```

#### **（4）查看当前隔离级别**
```sql
SELECT @@transaction_isolation; -- MySQL 8.0+
-- 或
SELECT @@tx_isolation; -- MySQL 5.7 及以下
```

---

### **5. 实际应用建议**
- **默认选择**：MySQL 默认使用 `REPEATABLE READ`，适合大多数场景。
- **高并发场景**：若允许短暂不一致，可降级为 `READ COMMITTED`（如统计类操作）。
- **强一致性场景**：升级为 `SERIALIZABLE`，但需评估性能影响。
- **避免脏读**：至少使用 `READ COMMITTED`。

---

### **6. 示例：隔离级别对查询的影响**
假设有两个事务 `T1` 和 `T2`，按以下顺序执行：
```sql
-- T1:
START TRANSACTION;
SELECT * FROM users WHERE id = 1; -- 初始值：name='Alice'

-- T2:
START TRANSACTION;
UPDATE users SET name = 'Bob' WHERE id = 1;
COMMIT;

-- T1 再次查询：
SELECT * FROM users WHERE id = 1;
```

| **隔离级别**         | **T1 第二次查询结果** | **说明**                     |
|----------------------|----------------------|-----------------------------|
| 读未提交（RU）       | 'Bob'                | 读到 T2 未提交的修改（脏读） |
| 读已提交（RC）       | 'Alice' 或 'Bob'     | 取决于 T2 是否已提交        |
| 可重复读（RR）       | 'Alice'              | 始终读取事务开始时的快照     |
| 串行化（S）          | 阻塞或报错           | T2 的修改会阻塞 T1 的查询   |

---

### **总结**
MySQL 的事务隔离级别通过权衡一致性和性能，为并发事务提供不同的可见性规则。理解各级别的差异和适用场景，有助于设计高可靠、高性能的数据库应用。实际开发中，建议根据业务需求选择合适的隔离级别，并配合锁机制或应用层逻辑进一步优化并发控制。
