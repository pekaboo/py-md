# MySQL 中的 MVCC 是什么？

**难度**：困难

**创建时间**：2025-10-05 12:10:28

## 答案
MySQL 中的 **MVCC（Multi-Version Concurrency Control，多版本并发控制）** 是一种通过维护数据的多个版本实现高并发读写的机制。它允许事务在**不阻塞其他事务**的情况下并发读取和修改数据，避免了传统的锁机制（如读写锁）带来的性能问题，是 MySQL **InnoDB 存储引擎**的核心特性之一。

---

## **一、MVCC 的核心原理**
### **1. 数据版本链（Undo Log）**
- **每行数据存储多个版本**：InnoDB 通过 **Undo Log（回滚日志）** 保存数据的旧版本。每次修改数据时，不会直接覆盖原数据，而是将旧值存入 Undo Log，并生成一个新版本的数据。
- **版本链结构**：每行数据隐藏两个字段：
  - `DB_TRX_ID`：记录最近修改该行的事务 ID。
  - `DB_ROLL_PTR`：指向该行旧版本的指针（指向 Undo Log 中的历史记录）。
- **版本链示例**：
  ```
  当前版本 → DB_TRX_ID=102, DB_ROLL_PTR=地址A → 版本1(DB_TRX_ID=101) → 版本0(初始数据)
  ```

### **2. ReadView（读视图）**
- **事务隔离级别的实现**：MVCC 通过 **ReadView** 决定事务能看到哪些数据版本。ReadView 包含以下关键信息：
  - `m_ids`：当前活跃（未提交）的事务 ID 列表。
  - `min_trx_id`：`m_ids` 中的最小事务 ID。
  - `max_trx_id`：下一个待分配的事务 ID（预分配值）。
  - `creator_trx_id`：创建该 ReadView 的事务 ID。
- **版本可见性规则**：
  1. **若 `DB_TRX_ID < min_trx_id`**：版本在 ReadView 创建前已提交，**可见**。
  2. **若 `DB_TRX_ID >= max_trx_id`**：版本在 ReadView 创建后生成，**不可见**。
  3. **若 `min_trx_id <= DB_TRX_ID < max_trx_id`**：
     - 若 `DB_TRX_ID` 在 `m_ids` 中：版本所属事务未提交，**不可见**。
     - 否则：版本已提交，**可见**。
  4. **若 `DB_TRX_ID == creator_trx_id`**：当前事务修改的行，**可见**。

---

## **二、MVCC 如何支持不同隔离级别？**
### **1. READ COMMITTED（读已提交）**
- **每次查询生成新的 ReadView**：每个 SQL 语句执行时都会创建一个新的 ReadView，因此能看到其他事务已提交的最新数据。
- **现象**：可能读到其他事务中间提交的数据（不可重复读）。

### **2. REPEATABLE READ（可重复读，InnoDB 默认）**
- **事务内共享同一个 ReadView**：事务第一次查询时生成 ReadView，后续查询复用该视图，因此看到的数据版本一致。
- **现象**：避免不可重复读（但可能读到快照前的旧数据）。

### **3. 对比 SERIALIZABLE**
- MVCC 本身不解决幻读问题（REPEATABLE READ 下仍可能因插入新数据出现幻读）。
- InnoDB 通过 **间隙锁（Gap Lock）** 在 REPEATABLE READ 下进一步避免幻读，而 SERIALIZABLE 会强制加锁，牺牲并发性。

---

## **三、MVCC 的操作流程**
### **1. SELECT 操作（快照读）**
- 根据当前事务的隔离级别生成 ReadView。
- 沿着版本链从最新版本开始，根据 ReadView 的规则判断版本是否可见。
- 找到第一个可见版本后返回结果。

### **2. INSERT/UPDATE/DELETE 操作（当前读）**
- **INSERT**：直接写入新数据，`DB_TRX_ID` 设置为当前事务 ID。
- **UPDATE**：
  - 若行存在：将原数据标记为旧版本（存入 Undo Log），插入新版本并更新 `DB_TRX_ID`。
  - 若行不存在：等同于 INSERT。
- **DELETE**：将行标记为删除（存入 Undo Log），但保留数据供其他事务读取（直到无事务需要该版本）。

---

## **四、MVCC 的优势与局限**
### **1. 优势**
- **高并发**：读操作无需等待写锁，写操作无需等待读锁（读多写少场景性能显著提升）。
- **避免锁竞争**：减少死锁和锁等待时间。
- **支持多种隔离级别**：通过 ReadView 灵活控制数据可见性。

### **2. 局限**
- **存储开销**：Undo Log 会占用额外空间，长时间运行的事务可能导致 Undo Log 膨胀。
- **幻读问题**：REPEATABLE READ 下仍可能因插入新数据出现幻读（需间隙锁解决）。
- **清理成本**：旧版本数据需通过 **Purge 线程** 定期清理，若事务长时间未提交，可能导致空间无法释放。

---

## **五、MVCC 与锁的对比**
| **机制**       | **MVCC**                          | **锁（如 2PL）**               |
|----------------|-----------------------------------|--------------------------------|
| **读操作**     | 无锁，读快照数据                  | 可能阻塞（共享锁/排他锁）      |
| **写操作**     | 通过版本链更新，不阻塞读          | 需获取排他锁，阻塞其他事务     |
| **隔离级别**   | 依赖 ReadView 实现                | 依赖锁的粒度和时机             |
| **适用场景**   | 读多写少，高并发                  | 写冲突频繁，强一致性要求       |

---

## **六、实际案例分析**
### **案例 1：REPEATABLE READ 下的快照读**
- **事务 A**（ID=100）：
  ```sql
  BEGIN;
  SELECT * FROM users WHERE id=1; -- 生成 ReadView，看到版本 X
  ```
- **事务 B**（ID=101）：
  ```sql
  BEGIN;
  UPDATE users SET name='Bob' WHERE id=1; -- 生成新版本 Y，DB_TRX_ID=101
  COMMIT;
  ```
- **事务 A 再次查询**：
  ```sql
  SELECT * FROM users WHERE id=1; -- 复用 ReadView，仍看到版本 X（避免不可重复读）
  ```

### **案例 2：READ COMMITTED 下的读已提交**
- **事务 A**（ID=100）：
  ```sql
  BEGIN;
  SELECT * FROM users WHERE id=1; -- 生成 ReadView1，看到版本 X
  ```
- **事务 B**（ID=101）提交更新：
  ```sql
  COMMIT; -- 版本 Y（DB_TRX_ID=101）已提交
  ```
- **事务 A 再次查询**：
  ```sql
  SELECT * FROM users WHERE id=1; -- 生成 ReadView2，看到版本 Y（读到已提交数据）
  ```

---

## **七、总结**
- **MVCC 是 InnoDB 实现高并发的核心**，通过多版本数据和 ReadView 机制，在保证一致性的同时减少锁竞争。
- **不同隔离级别通过 ReadView 的生成策略区分**：READ COMMITTED 每次查询生成新视图，REPEATABLE READ 事务内共享视图。
- **MVCC 并非万能**，需结合间隙锁解决幻读，并注意 Undo Log 的存储开销和 Purge 清理效率。

理解 MVCC 的工作原理，能帮助开发者优化事务设计（如避免长事务）、选择合适的隔离级别，并高效排查并发问题（如死锁、数据不一致）。
