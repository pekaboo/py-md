# 如果发现 Redis 内存溢出了？你会怎么做？请给出排查思路和解决方案

**难度**：困难

**创建时间**：2025-10-06 15:46:17

## 答案
当发现 Redis 内存溢出（`OOM command not allowed when used memory > maxmemory` 或 `MAXMEMORY POLICY` 相关错误）时，需要系统性地排查原因并采取解决方案。以下是详细的排查思路和分阶段处理方案：

---

### **一、排查思路**
#### 1. **确认内存使用现状**
```bash
# 查看Redis内存使用总量、峰值和限制
redis-cli info memory
```
**关键指标**：
- `used_memory`：当前使用内存（字节）
- `used_memory_peak`：历史峰值内存
- `maxmemory`：配置的内存上限（0表示无限制）
- `mem_fragmentation_ratio`：内存碎片率（>1.5可能需清理）

#### 2. **分析内存占用来源**
```bash
# 查看各数据类型占用内存（需Redis 4.0+）
redis-cli --bigkeys
# 或手动统计
redis-cli info keyspace  # 查看各DB键数量
redis-cli --stat         # 实时监控键数量变化
```
**重点检查**：
- 大键（如百万级元素的Hash/List）
- 热点键（频繁更新的键）
- 未设置过期时间的键

#### 3. **检查内存淘汰策略**
```bash
redis-cli config get maxmemory-policy
```
**常见策略**：
- `noeviction`（默认）：内存满时拒绝写入（触发OOM）
- `volatile-lru`：淘汰设置了过期时间的键（LRU算法）
- `allkeys-lru`：淘汰所有键（LRU算法）

#### 4. **排查内存泄漏**
- **客户端连接**：检查是否有大量连接未释放
  ```bash
  redis-cli info clients | grep connected_clients
  ```
- **持久化文件**：检查RDB/AOF文件是否异常增大
  ```bash
  ls -lh /var/lib/redis/dump.rdb
  ```
- **Lua脚本**：检查是否有长运行脚本占用内存
  ```bash
  redis-cli script list
  ```

---

### **二、解决方案**
#### **阶段1：紧急处理（立即生效）**
1. **扩大内存限制（临时）**
   ```bash
   # 动态修改（需Redis配置允许）
   redis-cli config set maxmemory 2gb
   # 或修改redis.conf后重启
   ```
   **注意**：需确保服务器有足够物理内存，否则可能触发OOM Killer。

2. **手动清理无用数据**
   ```bash
   # 删除特定模式的键（谨慎操作）
   redis-cli --scan --pattern "temp:*" | xargs redis-cli del
   # 清空整个DB（慎用！）
   redis-cli flushdb  # 当前DB
   redis-cli flushall # 所有DB
   ```

3. **触发主动淘汰**
   ```bash
   # 临时切换为allkeys-lru策略（需maxmemory已设置）
   redis-cli config set maxmemory-policy allkeys-lru
   ```

#### **阶段2：优化配置（中长期）**
1. **合理设置maxmemory**
   - 建议设置为物理内存的70-80%（如16GB服务器设为12GB）
   - 示例配置：
     ```
     maxmemory 12gb
     maxmemory-policy volatile-lru
     ```

2. **优化数据结构**
   - **拆分大键**：将单个Hash/List拆分为多个小键
   - **使用压缩列表**：对小数据启用`ziplist`编码
     ```
     hash-max-ziplist-entries 512
     hash-max-ziplist-value 64
     ```
   - **避免存储大对象**：如直接存储图片二进制数据

3. **设置合理的过期时间**
   ```bash
   # 为批量键设置过期时间（示例）
   redis-cli --scan --pattern "session:*" | xargs -I {} redis-cli expire {} 3600
   ```

4. **启用内存碎片整理**
   ```
   # redis.conf中配置（Redis 4.0+）
   activedefrag yes
   active-defrag-cycle-min 25
   active-defrag-cycle-max 75
   ```

#### **阶段3：监控与预防**
1. **部署监控告警**
   - 使用`redis-exporter` + Prometheus监控内存指标
   - 设置阈值告警（如`used_memory_rss` > 90% maxmemory）

2. **定期维护**
   - 每周执行`MEMORY PURGE`（Redis 6.0+）清理碎片
   - 每月检查大键和过期键分布

3. **水平扩展方案**
   - **分片**：使用Twemproxy或Redis Cluster分散负载
   - **读写分离**：将读操作分流到从库
   - **缓存层优化**：引入多层缓存（如本地Cache + Redis）

---

### **三、典型案例处理**
#### **案例1：大键导致OOM**
- **现象**：`used_memory`突然激增，`--bigkeys`发现某个Hash有100万字段
- **解决**：
  1. 拆分Hash为多个小Hash（如按用户ID哈希分片）
  2. 改用Redis模块（如RedisJSON）存储结构化数据

#### **案例2：内存泄漏**
- **现象**：内存缓慢增长，无对应业务流量变化
- **排查**：
  1. 检查`slowlog get`是否有阻塞命令
  2. 使用`INFO COMMANDSTATS`分析命令耗时
- **解决**：
  1. 优化热点键操作（如用`PIPELINE`批量处理）
  2. 限制客户端长连接数（`maxclients 10000`）

#### **案例3：持久化文件过大**
- **现象**：RDB文件超过maxmemory限制
- **解决**：
  1. 修改`save`策略减少保存频率
  2. 启用AOF并设置`appendfsync everysec`
  3. 对大键禁用持久化（`no-appendfsync-on-rewrite yes`）

---

### **四、工具推荐**
| **工具**               | **用途**                                  |
|------------------------|-------------------------------------------|
| `redis-rdb-tools`      | 分析RDB文件中的大键和内存分布             |
| `redis-stat`           | 实时监控内存、命中率等指标                |
| `RedisInsight`         | 可视化分析内存使用（Redis官方GUI工具）    |
| `memtier_benchmark`    | 模拟压力测试验证内存优化效果              |

---

### **五、预防措施清单**
1. **生产环境必备**：
   - 始终设置`maxmemory`和淘汰策略
   - 禁止使用`noeviction`策略（除非有特殊需求）
   - 为所有业务键设置合理的TTL

2. **开发规范**：
   - 禁止在Redis中存储大于100KB的单个值
   - 复杂查询改用Lua脚本或模块实现
   - 避免使用`KEYS *`等全量扫描命令

3. **容量规划**：
   - 预估业务数据量（键数量×平均值大小）
   - 预留30%内存作为缓冲（应对突发流量）

---

通过以上系统化的排查和处理，可以快速解决Redis内存溢出问题，并建立长效的内存管理机制。关键是要结合业务特点选择合适的优化策略，避免"一刀切"式的配置调整。
