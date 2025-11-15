# MySQL 中使用索引一定有效吗？如何排查索引效果？

**难度**：中等

**创建时间**：2025-10-05 08:00:17

## 答案
在 MySQL 中，**索引并不总是有效**，其效果受查询方式、数据分布、索引设计等多种因素影响。即使创建了索引，也可能出现未使用、效率低下甚至性能下降的情况。以下是详细分析索引无效的原因及排查方法：

---

## **一、索引可能无效的常见原因**
### 1. **查询未命中索引**
   - **未使用索引的列**：查询条件中的列未创建索引。
   - **函数或运算导致失效**：对索引列使用函数、计算或类型转换。
     ```sql
     -- 错误示例：对索引列使用函数
     SELECT * FROM users WHERE YEAR(create_time) = 2023;  -- 索引失效
     SELECT * FROM users WHERE id + 1 = 10;               -- 索引失效
     ```
   - **隐式类型转换**：列与查询值的类型不匹配（如字符串 vs 数字）。
     ```sql
     -- 错误示例：user_id是字符串类型，但用数字查询
     SELECT * FROM users WHERE user_id = 123;  -- 索引失效
     ```

### 2. **索引选择性差**
   - **低选择性列**：索引列的值重复率高（如性别、状态字段），优化器可能选择全表扫描。
     ```sql
     -- 示例：status字段只有'active'/'inactive'两种值
     SELECT * FROM orders WHERE status = 'active';  -- 可能不走索引
     ```

### 3. **组合索引未遵循最左前缀原则**
   - 组合索引 `INDEX (a, b, c)` 仅对 `a`、`a+b`、`a+b+c` 的查询有效，单独使用 `b` 或 `c` 不会命中。
     ```sql
     CREATE INDEX idx_abc ON users (name, age, gender);
     SELECT * FROM users WHERE age = 20;  -- 不走索引（缺少name）
     ```

### 4. **索引覆盖不足**
   - 查询需要返回的列未全部包含在索引中，导致回表（随机 I/O 成本高）。
     ```sql
     -- 索引idx_name仅覆盖name列，但查询需要id和name
     SELECT id, name FROM users WHERE name = 'Alice';  -- 可能走索引
     SELECT * FROM users WHERE name = 'Alice';          -- 需要回表，可能不走索引
     ```

### 5. **数据量过小或统计信息不准确**
   - 表数据量极少（如 < 1000 行），优化器可能认为全表扫描更快。
   - 统计信息过时（`ANALYZE TABLE` 未更新），导致优化器误判。

### 6. **OR 条件或复杂查询**
   - 使用 `OR` 连接的条件可能无法利用索引。
     ```sql
     SELECT * FROM users WHERE name = 'Alice' OR age = 20;  -- 可能不走索引
     ```
   - 子查询、联合查询等复杂逻辑可能绕过索引。

### 7. **索引碎片或维护成本高**
   - 频繁更新的表可能导致索引碎片化，影响查询效率。
   - 索引列过多会拖慢写入速度（INSERT/UPDATE/DELETE 需维护索引）。

---

## **二、排查索引效果的方法**
### 1. **使用 `EXPLAIN` 分析执行计划**
   - 关键字段说明：
     - `type`：访问类型（`const` > `eq_ref` > `ref` > `range` > `index` > `ALL`），`ALL` 表示全表扫描。
     - `key`：实际使用的索引名，`NULL` 表示未使用索引。
     - `rows`：预估需要检查的行数，值越小越好。
     - `Extra`：额外信息（如 `Using where`、`Using index`、`Using filesort`）。
   - 示例：
     ```sql
     EXPLAIN SELECT * FROM users WHERE name = 'Alice';
     ```
     **输出分析**：
     - 若 `key` 为 `NULL`，说明未使用索引。
     - 若 `type=ALL`，说明全表扫描。
     - 若 `Extra=Using where; Using index`，表示覆盖索引（无需回表）。

### 2. **检查索引使用统计**
   - 通过 `performance_schema` 或 `sys` 库查看索引命中情况：
     ```sql
     -- 查看未使用的索引（MySQL 5.7+）
     SELECT * FROM sys.schema_unused_indexes;

     -- 查看索引使用频率（需开启performance_schema）
     SELECT * FROM performance_schema.table_io_waits_summary_by_index_usage;
     ```

### 3. **强制使用索引测试**
   - 使用 `FORCE INDEX` 强制走索引，对比性能差异：
     ```sql
     SELECT * FROM users FORCE INDEX(idx_name) WHERE name = 'Alice';
     ```
   - 如果强制索引后性能提升，说明优化器未正确选择索引。

### 4. **更新统计信息**
   - 执行 `ANALYZE TABLE` 更新统计信息，帮助优化器生成更优的执行计划：
     ```sql
     ANALYZE TABLE users;
     ```

### 5. **监控慢查询日志**
   - 开启慢查询日志，分析未使用索引的 SQL：
     ```sql
     -- 在my.cnf中配置
     slow_query_log = ON
     slow_query_threshold = 1  -- 超过1秒的查询记录
     ```
   - 通过 `mysqldumpslow` 或 `pt-query-digest` 分析慢查询。

### 6. **使用 `SHOW INDEX` 检查索引设计**
   - 查看索引的基数（Cardinality）和选择性：
     ```sql
     SHOW INDEX FROM users;
     ```
     - **Cardinality**：唯一值的预估数量，值越高选择性越好。
     - **选择性** = Cardinality / 表总行数，> 30% 的列适合建索引。

---

## **三、优化索引效果的策略**
### 1. **设计高选择性索引**
   - 优先为高频查询、区分度高的列创建索引（如用户ID、订单号）。
   - 避免为低选择性列建索引（如性别、状态）。

### 2. **合理使用组合索引**
   - 遵循最左前缀原则，将高频查询条件放在左侧。
   - 示例：
     ```sql
     -- 组合索引设计（适合 WHERE name=? AND age=? 的查询）
     CREATE INDEX idx_name_age ON users (name, age);
     ```

### 3. **覆盖索引优化**
   - 将查询需要的列全部包含在索引中，避免回表：
     ```sql
     -- 覆盖索引（查询name和age时无需回表）
     CREATE INDEX idx_name_age ON users (name, age);
     SELECT name, age FROM users WHERE name = 'Alice';
     ```

### 4. **避免索引失效的操作**
   - 禁止对索引列使用函数、计算或隐式转换。
   - 拆分 `OR` 条件为 `UNION ALL`：
     ```sql
     SELECT * FROM users WHERE name = 'Alice'
     UNION ALL
     SELECT * FROM users WHERE age = 20 AND name IS NULL;
     ```

### 5. **定期维护索引**
   - 重建碎片化索引：
     ```sql
     ALTER TABLE users ENGINE=InnoDB;  -- 重建表并整理索引
     ```
   - 删除冗余索引：
     ```sql
     -- 例如已有(a,b)，则(a)是冗余索引
     DROP INDEX idx_a ON users;
     ```

---

## **四、示例：索引优化实战**
### **问题 SQL**
```sql
SELECT * FROM orders WHERE YEAR(create_time) = 2023 AND status = 'completed';
```
**问题**：对 `create_time` 使用函数导致索引失效。

### **优化方案**
1. **修改查询条件**：
   ```sql
   SELECT * FROM orders 
   WHERE create_time BETWEEN '2023-01-01' AND '2023-12-31' 
   AND status = 'completed';
   ```
2. **创建组合索引**：
   ```sql
   CREATE INDEX idx_create_time_status ON orders (create_time, status);
   ```
3. **验证效果**：
   ```sql
   EXPLAIN SELECT * FROM orders 
   WHERE create_time BETWEEN '2023-01-01' AND '2023-12-31' 
   AND status = 'completed';
   ```
   **预期结果**：`type=range`，`key=idx_create_time_status`。

---

## **五、总结**
| **排查步骤**               | **工具/命令**                          | **目标**                          |
|----------------------------|----------------------------------------|-----------------------------------|
| 1. 检查执行计划            | `EXPLAIN SELECT ...`                   | 确认是否使用索引                  |
| 2. 查看索引使用统计        | `sys.schema_unused_indexes`            | 发现未使用的索引                  |
| 3. 强制索引测试            | `FORCE INDEX`                          | 验证索引对性能的影响              |
| 4. 更新统计信息            | `ANALYZE TABLE`                        | 修正优化器误判                    |
| 5. 监控慢查询              | 慢查询日志 + `pt-query-digest`         | 定位高频低效SQL                   |
| 6. 优化索引设计            | `SHOW INDEX` + 组合索引/覆盖索引       | 提高索引选择性，减少回表          |

**核心原则**：
- **索引不是越多越好**，需平衡查询与写入性能。
- **通过数据验证**，而非仅凭理论设计索引。
- **定期维护**，避免索引碎片和统计信息过时。
