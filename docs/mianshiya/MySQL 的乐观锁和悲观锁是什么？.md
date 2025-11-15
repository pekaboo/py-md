# MySQL 的乐观锁和悲观锁是什么？

**难度**：中等

**创建时间**：2025-10-06 05:55:07

## 答案
MySQL 中的乐观锁和悲观锁是两种不同的并发控制策略，用于解决多事务或线程同时操作数据时的冲突问题。它们的核心区别在于对数据竞争的假设和实现方式：**悲观锁假设冲突频繁发生，通过预先加锁避免；乐观锁假设冲突较少，通过冲突检测和重试解决**。以下是详细解析：

---

## **1. 悲观锁（Pessimistic Locking）**
### **核心思想**
- **假设冲突频繁发生**：在操作数据前，先获取锁（如排他锁），确保独占访问，避免其他事务修改数据。
- **适用场景**：高并发写操作、数据一致性要求严格的场景（如金融交易、库存扣减）。

### **实现方式**
#### **（1）数据库锁机制**
- **共享锁（S锁，读锁）**：  
  多个事务可同时读取数据，但阻止其他事务获取排他锁。  
  ```sql
  SELECT * FROM products WHERE id = 1 LOCK IN SHARE MODE; -- MySQL 语法
  -- 或
  SELECT * FROM products WHERE id = 1 FOR SHARE; -- MySQL 8.0+
  ```
- **排他锁（X锁，写锁）**：  
  独占数据，阻止其他事务获取任何锁（读或写）。  
  ```sql
  SELECT * FROM products WHERE id = 1 FOR UPDATE; -- 获取排他锁
  UPDATE products SET stock = stock - 1 WHERE id = 1; -- 修改数据
  COMMIT; -- 提交后释放锁
  ```

#### **（2）行锁、表锁、间隙锁**
- **行锁**：锁定单行数据（InnoDB 支持）。  
- **表锁**：锁定整个表（MyISAM 仅支持表锁）。  
- **间隙锁（Gap Lock）**：锁定索引记录间隙，防止幻读（仅 InnoDB 在 `REPEATABLE READ` 隔离级别下生效）。

### **优缺点**
- **优点**：
  - 严格保证数据一致性，避免并发冲突。
- **缺点**：
  - 性能开销大（锁等待、死锁风险）。
  - 高并发下可能导致事务阻塞或超时。

### **示例：库存扣减**
```sql
-- 事务1
START TRANSACTION;
SELECT * FROM products WHERE id = 1 FOR UPDATE; -- 加排他锁
-- 模拟其他操作...
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;

-- 事务2（若事务1未提交，会被阻塞）
START TRANSACTION;
SELECT * FROM products WHERE id = 1 FOR UPDATE; -- 等待锁释放
```

---

## **2. 乐观锁（Optimistic Locking）**
### **核心思想**
- **假设冲突较少发生**：不预先加锁，而是在更新时检查数据是否被其他事务修改过。若冲突，则拒绝操作或重试。
- **适用场景**：读多写少、冲突概率低的场景（如评论系统、版本控制）。

### **实现方式**
#### **（1）版本号（Versioning）**
- 在表中增加 `version` 字段，更新时检查版本号是否匹配。  
  ```sql
  -- 初始数据
  CREATE TABLE products (
      id INT PRIMARY KEY,
      name VARCHAR(100),
      stock INT,
      version INT DEFAULT 0
  );

  -- 事务1：更新时版本号+1
  START TRANSACTION;
  SELECT * FROM products WHERE id = 1; -- 获取当前版本（假设version=0）
  -- 模拟其他操作...
  UPDATE products 
  SET stock = stock - 1, version = version + 1 
  WHERE id = 1 AND version = 0; -- 仅当版本匹配时更新
  -- 若影响行数为0，说明版本已变更（冲突）
  COMMIT;
  ```

#### **（2）时间戳（Timestamp）**
- 使用 `last_modified` 字段记录最后修改时间，更新时检查时间戳是否未变。  
  ```sql
  UPDATE products 
  SET stock = stock - 1 
  WHERE id = 1 AND last_modified = '2023-10-01 10:00:00';
  ```

#### **（3）CAS（Compare-And-Swap）**
- 类似版本号，但通过原子操作直接比较并更新（如 Redis 的 `WATCH` 命令）。

### **优缺点**
- **优点**：
  - 无锁开销，性能高（适合读多写少）。
  - 避免死锁问题。
- **缺点**：
  - 冲突时需重试或回滚，可能增加业务复杂度。
  - 高并发下频繁冲突会导致性能下降。

### **示例：评论点赞**
```sql
-- 用户A点赞
START TRANSACTION;
SELECT likes, version FROM comments WHERE id = 1; -- 获取likes=10, version=0
-- 模拟延迟...
UPDATE comments 
SET likes = likes + 1, version = version + 1 
WHERE id = 1 AND version = 0; -- 成功
COMMIT;

-- 用户B同时点赞（版本已变为1）
START TRANSACTION;
SELECT likes, version FROM comments WHERE id = 1; -- 获取likes=11, version=1
UPDATE comments 
SET likes = likes + 1, version = version + 1 
WHERE id = 1 AND version = 1; -- 成功
COMMIT;

-- 用户C迟到点赞（版本已变为2）
START TRANSACTION;
SELECT likes, version FROM comments WHERE id = 1; -- 获取likes=12, version=2
UPDATE comments 
SET likes = likes + 1, version = version + 1 
WHERE id = 1 AND version = 2; -- 成功
COMMIT;
```

---

## **3. 悲观锁 vs 乐观锁对比**
| **特性**         | **悲观锁**                     | **乐观锁**                     |
|------------------|-------------------------------|-------------------------------|
| **冲突假设**     | 频繁发生                      | 较少发生                      |
| **加锁时机**     | 操作前加锁                    | 更新时检查版本/时间戳          |
| **性能**         | 高并发下性能低（锁竞争）      | 高并发下性能高（无锁）        |
| **实现复杂度**   | 简单（直接加锁）              | 复杂（需处理冲突重试）        |
| **适用场景**     | 写多读少、强一致性            | 读多写少、低冲突              |
| **死锁风险**     | 高（需处理死锁）              | 无                            |

---

## **4. 实际应用建议**
### **（1）选择悲观锁的场景**
- **库存扣减**：避免超卖。  
  ```sql
  START TRANSACTION;
  SELECT * FROM inventory WHERE product_id = 1 FOR UPDATE;
  UPDATE inventory SET stock = stock - 1 WHERE product_id = 1;
  COMMIT;
  ```
- **银行转账**：确保资金安全。  
  ```sql
  START TRANSACTION;
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE; -- 锁定转出账户
  SELECT * FROM accounts WHERE id = 2 FOR UPDATE; -- 锁定转入账户
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
  COMMIT;
  ```

### **（2）选择乐观锁的场景**
- **评论系统**：用户点赞、踩。  
  ```sql
  -- 前端提交时携带版本号
  UPDATE comments 
  SET likes = likes + 1, version = version + 1 
  WHERE id = 1 AND version = ${前端版本号};
  -- 若影响行数为0，提示用户“操作失败，请刷新重试”
  ```
- **分布式系统**：如订单状态更新。  
  ```java
  // 伪代码：使用版本号重试
  int retry = 3;
  while (retry-- > 0) {
      Order order = dao.getOrderById(orderId);
      if (order.getStatus() != "PENDING") {
          throw new Exception("订单状态已变更");
      }
      order.setStatus("COMPLETED");
      int updated = dao.updateOrderWithVersion(order);
      if (updated > 0) break; // 成功
  }
  ```

### **（3）混合使用**
- **读多写少但关键操作需强一致性**：  
  - 读取时用乐观锁（无锁），更新时用悲观锁（如秒杀场景）。  
  ```sql
  -- 用户查看库存（乐观读）
  SELECT stock FROM products WHERE id = 1;

  -- 秒杀时加悲观锁（防止超卖）
  START TRANSACTION;
  SELECT * FROM products WHERE id = 1 FOR UPDATE;
  IF (stock > 0) {
      UPDATE products SET stock = stock - 1 WHERE id = 1;
      COMMIT;
  } ELSE {
      ROLLBACK;
  }
  ```

---

## **5. 总结**
- **悲观锁**：适合写多读少、强一致性的场景，但性能受锁竞争影响。  
- **乐观锁**：适合读多写少、低冲突的场景，通过版本控制避免锁开销。  
- **选择依据**：根据业务冲突概率、性能需求和数据一致性要求综合决定。  
- **最佳实践**：在 MySQL 中，通常结合事务隔离级别（如 `REPEATABLE READ`）和锁机制（如 `FOR UPDATE`）实现悲观锁，通过版本号或时间戳实现乐观锁。
