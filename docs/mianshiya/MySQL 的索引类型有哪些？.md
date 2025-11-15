# MySQL 的索引类型有哪些？

**难度**：简单

**创建时间**：2025-10-04 08:47:36

## 答案
MySQL 提供了多种索引类型，每种类型针对不同的查询场景和数据特性进行优化。以下是 MySQL 中常见的索引类型及其详细说明：

---

### **一、按数据结构分类**
#### **1. B-Tree 索引（默认索引）**
- **适用引擎**：InnoDB、MyISAM、MEMORY 等。
- **特点**：
  - 基于平衡树结构，支持范围查询和排序。
  - 适合等值查询（`=`、`IN`）和范围查询（`>`、`<`、`BETWEEN`）。
  - 默认情况下，InnoDB 使用聚簇索引（数据按主键物理存储），MyISAM 使用非聚簇索引。
- **示例**：
  ```sql
  -- 单列索引
  CREATE INDEX idx_name ON users(name);
  
  -- 复合索引
  CREATE INDEX idx_name_age ON users(name, age);
  ```

#### **2. 哈希索引（Hash Index）**
- **适用引擎**：MEMORY 引擎默认使用，InnoDB 支持自适应哈希索引（AHI）。
- **特点**：
  - 基于哈希表，仅支持等值查询（`=`、`IN`），不支持范围查询。
  - 查询速度极快（O(1) 时间复杂度），但无法排序。
  - InnoDB 的自适应哈希索引会自动为频繁访问的索引页建立哈希索引。
- **示例**：
  ```sql
  -- MEMORY 引擎显式指定哈希索引
  CREATE TABLE mem_table (
    id INT,
    name VARCHAR(50),
    INDEX idx_id USING HASH (id)
  ) ENGINE=MEMORY;
  ```

#### **3. 全文索引（FULLTEXT Index）**
- **适用引擎**：InnoDB（MySQL 5.6+）、MyISAM。
- **特点**：
  - 用于文本内容的全文搜索，支持 `MATCH AGAINST` 语法。
  - 适合长文本字段（如文章内容、评论）。
  - 默认使用自然语言模式，也支持布尔模式（`+`、`-`、`*` 等操作符）。
- **示例**：
  ```sql
  -- 创建全文索引
  CREATE FULLTEXT INDEX ft_idx_content ON articles(content);
  
  -- 全文查询
  SELECT * FROM articles WHERE MATCH(content) AGAINST('数据库 优化');
  ```

#### **4. 空间索引（R-Tree Index）**
- **适用引擎**：MyISAM、InnoDB（MySQL 5.7+）。
- **特点**：
  - 用于地理空间数据类型（如 `POINT`、`LINESTRING`、`POLYGON`）。
  - 支持空间操作（如 `MBRContains()`、`MBRWithin()`）。
- **示例**：
  ```sql
  -- 创建空间索引
  CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    geom GEOMETRY NOT NULL,
    SPATIAL INDEX sp_idx_geom (geom)
  ) ENGINE=MyISAM;
  ```

---

### **二、按功能分类**
#### **1. 普通索引（Normal Index）**
- 最基础的索引类型，无特殊约束。
- **示例**：
  ```sql
  CREATE INDEX idx_email ON users(email);
  ```

#### **2. 唯一索引（Unique Index）**
- 确保索引列的值唯一（允许 `NULL` 值，但最多一个 `NULL`）。
- **示例**：
  ```sql
  -- 单列唯一索引
  CREATE UNIQUE INDEX uq_email ON users(email);
  
  -- 复合唯一索引
  CREATE UNIQUE INDEX uq_name_phone ON users(name, phone);
  ```

#### **3. 主键索引（Primary Key Index）**
- 特殊的唯一索引，不允许 `NULL` 值，且每个表只能有一个主键。
- InnoDB 中，主键索引是聚簇索引（数据按主键物理存储）。
- **示例**：
  ```sql
  CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
  );
  ```

#### **4. 复合索引（Composite Index）**
- 多列组合的索引，遵循最左前缀原则。
- **示例**：
  ```sql
  -- 复合索引 (name, age)
  CREATE INDEX idx_name_age ON users(name, age);
  
  -- 查询需从左匹配：WHERE name='John'（有效）
  -- WHERE age=30（无效，除非优化器选择索引跳跃扫描）
  ```

#### **5. 前缀索引（Prefix Index）**
- 对字符串列的前 N 个字符建立索引，节省空间。
- **限制**：无法用于排序或分组，且前缀长度需合理选择。
- **示例**：
  ```sql
  -- 对 email 列的前 10 个字符建立索引
  CREATE INDEX idx_email_prefix ON users(email(10));
  ```

#### **6. 函数索引（Functional Index）**
- MySQL 8.0+ 支持基于表达式或函数的索引。
- **示例**：
  ```sql
  -- 对 LOWER(name) 建立索引
  CREATE INDEX idx_lower_name ON users((LOWER(name)));
  
  -- 查询需使用相同表达式
  SELECT * FROM users WHERE LOWER(name) = 'john';
  ```

#### **7. 隐藏索引（Invisible Index）**
- MySQL 8.0+ 支持将索引标记为不可见，用于测试索引必要性。
- **示例**：
  ```sql
  -- 创建不可见索引
  CREATE INDEX idx_phone ON users(phone) INVISIBLE;
  
  -- 临时启用
  ALTER TABLE users ALTER INDEX idx_phone VISIBLE;
  ```

---

### **三、按存储引擎分类**
#### **1. InnoDB 索引特性**
- **聚簇索引**：主键索引的叶子节点存储完整数据行。
- **二级索引**：非主键索引的叶子节点存储主键值（需回表查询）。
- **自适应哈希索引**：自动为热点数据建立哈希索引。

#### **2. MyISAM 索引特性**
- **非聚簇索引**：所有索引的叶子节点存储数据行指针（文件偏移量）。
- **表压缩**：支持对索引和数据文件进行压缩。

#### **3. MEMORY 索引特性**
- 默认使用哈希索引，也可指定 B-Tree 索引。
- 不支持 TEXT/BLOB 类型的索引。

---

### **四、索引选择建议**
1. **等值查询**：优先使用 B-Tree 或哈希索引。
2. **范围查询**：使用 B-Tree 索引。
3. **全文搜索**：使用 FULLTEXT 索引。
4. **地理数据**：使用 R-Tree 空间索引。
5. **复合索引**：遵循最左前缀原则，将高频查询列放在左侧。
6. **避免过度索引**：每个额外索引会增加写入开销。

---

### **五、示例汇总**
| **索引类型**       | **适用场景**                          | **语法示例**                                  |
|--------------------|---------------------------------------|-----------------------------------------------|
| B-Tree 索引        | 等值/范围查询、排序                   | `CREATE INDEX idx_name ON users(name);`      |
| 哈希索引           | 内存表等值查询                        | `CREATE INDEX idx_id USING HASH (id);`       |
| 全文索引           | 文本搜索                              | `CREATE FULLTEXT INDEX ft_idx ON articles(content);` |
| 空间索引           | 地理数据查询                          | `SPATIAL INDEX sp_idx ON locations(geom);`   |
| 唯一索引           | 确保列值唯一                          | `CREATE UNIQUE INDEX uq_email ON users(email);` |
| 复合索引           | 多列联合查询                          | `CREATE INDEX idx_name_age ON users(name, age);` |
| 前缀索引           | 长字符串部分匹配                      | `CREATE INDEX idx_email ON users(email(10));` |

---

通过合理选择索引类型，可以显著提升 MySQL 的查询性能。实际优化时，需结合 `EXPLAIN` 分析执行计划，并考虑数据分布和查询模式。
