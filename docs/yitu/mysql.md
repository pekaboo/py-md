---
title: Mysql相关
description: Mysql相关
---
# Mysql相关

## 18. MySQL 索引失效原因

### 要点速览 · 18

- 函数/表达式包裹列、类型转换导致无法走索引。
- 模糊匹配左模糊、范围条件影响联合索引。
- 统计信息过期、选择度低。

### 基础要点 · 18

- `LIKE '%xxx'` 左模糊无法利用 B+Tree 前缀。
- 对列做运算、`WHERE DATE(create_time)=...` 会导致全表扫描。
- 数据类型不一致触发隐式转换。

### 进阶扩展 · 18

- 联合索引遵循最左前缀；在范围查询后续列失效。
- OR 条件若其中一列无索引总体失效，可拆分 Union。
- 统计信息 stale 使优化器选择错误，可 `ANALYZE TABLE`。

### ⚠️注意事项 · 18

- 注意字符集排序规则影响索引；`ORDER BY` 最好复用索引顺序避免 filesort。
- 长度过大的 `VARCHAR` 建议前缀索引，注意选择度。
- 避免在 `where` 使用 `!=`、`<>`、`IS NULL` 破坏索引。





## 19. 锁类型与 MySQL 行锁/间隙锁/临键锁

### 要点速览 · 19

- 锁分类：乐观/悲观、共享/排它、表锁/行锁。
- InnoDB 行级锁基于索引。
- 间隙锁、临键锁用于防止幻读。

### 基础要点 · 19

- **共享锁(S)**：允许并发读，不允许写。
- **排他锁(X)**：独占访问。
- **行锁**：通过索引记录锁定，避免锁全表。

### 进阶扩展 · 19

- **间隙锁(Gap Lock)**：锁定索引区间，不含记录本身，防止插入。
- **临键锁(Next-Key Lock)**：记录锁 + 间隙锁组合，默认 RR 隔离下用于范围查询。
- **意向锁**：表级锁与行锁协调。
- 锁冲突诊断：`information_schema.innodb_locks`、`performance_schema`。

### ⚠️注意事项 · 19

- 查询未使用索引会退化为表锁。
- 合理使用 `FOR UPDATE`，避免大事务长时间持锁。
- Gap Lock 仅在 RR 下生效；RC 可通过 `binlog_format=ROW` 减少锁范围。




## 26. MVCC / ReadView / Undo Log / Redo Log / Binlog

### 要点速览 · 26

- MVCC 通过版本链、ReadView 提供快照读。
- Undo log 支持回滚与构建历史版本。
- Redo log 保证崩溃恢复，Binlog 用于主从复制。

### 基础要点 · 26

- InnoDB 行记录包含隐藏列 `trx_id`、`roll_pointer` 构建版本链。
- 快照读生成 ReadView，记录当前活跃事务 ID 列表。
- Undo log 保存旧值；Redo log Write-Ahead 保证持久性；Binlog 顺序记录逻辑操作。

### 进阶扩展 · 26

- ReadView 判定规则：`trx_id` < `up_limit_id` 可见，落在活跃集合不可见。
- Redo log (物理) 与 Binlog (逻辑) 双写，结合形成两阶段提交保证一致性。
- GC: Purge 线程清理不再需要的 Undo log；长事务阻塞清理导致 `history list length` 增长。

### ⚠️注意事项 · 26

- Repeatable Read 下快照读使用同一 ReadView，避免幻读需锁定读。
- 定期监控 redo/buffer 池刷盘压力，避免 `checkpoint age` 膨胀。
- Binlog 模式 (ROW/STATEMENT/MIXED) 影响复制准确性与日志体积。