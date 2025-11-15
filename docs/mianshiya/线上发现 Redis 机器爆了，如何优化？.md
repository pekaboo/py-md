# 线上发现 Redis 机器爆了，如何优化？

**难度**：中等

**创建时间**：2025-10-06 15:47:01

## 答案
当线上 Redis 机器出现性能瓶颈甚至“爆掉”（如 CPU 100%、内存耗尽、连接数打满等），需快速定位问题并优化。以下是分步骤的排查和优化方案：

---

## **1. 紧急处理：快速恢复服务**
### **1.1 扩容或切换实例**
- **横向扩容**：如果是集群模式（如 Redis Cluster），将部分槽位迁移到新节点。
- **纵向扩容**：临时升级机器配置（如从 8GB 内存升级到 32GB）。
- **切换备用实例**：如果有高可用架构（如主从+哨兵），手动触发故障转移（`SENTINEL FAILOVER`）。

### **1.2 限流或降级**
- **客户端限流**：通过 Redis 客户端（如 Lettuce/Jedis）配置最大连接数或请求速率。
- **服务降级**：临时关闭非核心功能（如日志统计、推荐缓存），减少 Redis 负载。

### **1.3 清理无用数据**
- 执行 `FLUSHDB`（清理当前库）或 `FLUSHALL`（谨慎使用）释放内存。
- 删除大 Key：通过 `redis-cli --bigkeys` 扫描并删除占用内存过多的 Key。

---

## **2. 根因分析：定位性能瓶颈**
### **2.1 监控指标检查**
通过 `INFO` 命令或监控工具（如 Prometheus + Grafana）检查以下指标：
- **内存**：`used_memory` 是否接近 `maxmemory`？是否有大量碎片（`mem_fragmentation_ratio > 1.5`）？
- **CPU**：`used_cpu_sys` 是否持续高负载？可能是大 Key 查询或网络阻塞。
- **连接数**：`connected_clients` 是否超过 `maxclients`（默认 10000）？
- **命中率**：`keyspace_hits` / (`keyspace_hits + keyspace_misses`) 是否低于 90%？
- **阻塞操作**：`blocked_clients` 是否有大量客户端因命令阻塞（如 `BLPOP`）？

### **2.2 慢查询日志**
- 开启慢查询日志：`CONFIG SET slowlog-log-slower-than 1000`（单位：微秒）。
- 查看慢查询：`SLOWLOG GET`，分析高频或耗时长的命令（如 `KEYS *`、`HGETALL`）。

### **2.3 大 Key 检测**
- 使用 `redis-cli --bigkeys` 扫描数据库，找出占用内存过多的 String/Hash/List/Set/ZSet。
- 示例输出：
  ```
  Summary: {
    "String": 1000,
    "List": 10,
    "Hash": 50,
    "Biggest String": "key123" (10MB),
    "Biggest Hash": "user:1000" (1MB, 1000 fields)
  }
  ```

### **2.4 网络问题**
- 检查网络带宽是否打满：`iftop` 或 `nethogs`。
- 测试客户端到 Redis 的延迟：`ping` 和 `telnet` 命令。

---

## **3. 长期优化方案**
### **3.1 内存优化**
- **设置过期时间**：为临时数据（如会话、验证码）设置 `EXPIRE`。
- **使用更紧凑的数据结构**：
  - 用 Bitmap 存储布尔值（如用户签到）。
  - 用 HyperLogLog 统计 UV（误差 0.81%）。
  - 用压缩列表（ZipList）替代 Hash/List（当元素数量少时）。
- **避免大 Key**：
  - 拆分大 Hash：将 `user:1000` 拆分为 `user:1000:profile`、`user:1000:orders`。
  - 分片大 List：用多个 List 存储（如 `log:202301`、`log:202302`）。

### **3.2 命令优化**
- **禁用危险命令**：通过 `rename-command` 禁用 `KEYS`、`FLUSHALL` 等。
- **替换高耗时命令**：
  - 用 `SCAN` 替代 `KEYS *`（避免阻塞）。
  - 用 `HSCAN`/`ZSCAN` 替代全量遍历。
  - 用 `PIPELINE` 批量操作（减少网络往返）。
- **避免复杂计算**：将耗时操作（如正则匹配）放到应用层处理。

### **3.3 架构优化**
- **读写分离**：主库写，从库读（需处理主从同步延迟）。
- **数据分片**：按业务拆分（如用户库、订单库）或使用 Redis Cluster。
- **缓存层隔离**：核心数据（如支付）和非核心数据（如日志）分开部署。
- **多级缓存**：本地缓存（Caffeine/Guava） + 分布式缓存（Redis）。

### **3.4 参数调优**
- **内存配置**：
  ```bash
  maxmemory 16gb          # 限制最大内存
  maxmemory-policy allkeys-lru  # 淘汰策略（LRU/LFU/TTL）
  ```
- **连接数**：
  ```bash
  maxclients 40000        # 根据实际连接数调整
  tcp-backlog 511         # 等待连接队列长度
  ```
- **持久化优化**：
  - 使用 RDB+AOF 混合持久化（Redis 4.0+）。
  - 异步删除大文件：`CONFIG SET lazyfree-lazy-eviction yes`。

### **3.5 监控与告警**
- **实时监控**：Prometheus 采集 Redis 指标，Grafana 可视化。
- **告警规则**：
  - 内存使用率 > 85%。
  - 连接数 > 90% `maxclients`。
  - 慢查询数量 > 10 次/分钟。
  - 命令拒绝率（`rejected_connections`） > 0。

---

## **4. 预防措施**
- **压测**：使用 `redis-benchmark` 模拟高并发场景，提前发现瓶颈。
  ```bash
  redis-benchmark -t set,get -n 100000 -c 50 -h 127.0.0.1 -p 6379
  ```
- **容量规划**：根据业务增长预测内存和 QPS 需求。
- **混沌工程**：随机杀死 Redis 节点，测试高可用性。

---

## **5. 案例：大 Key 导致 Redis 崩溃**
**问题现象**：Redis 实例 CPU 100%，响应延迟 > 1s。  
**排查过程**：
1. 通过 `SLOWLOG GET` 发现大量 `HGETALL user:1000` 命令耗时 > 500ms。
2. 使用 `redis-cli --bigkeys` 发现 `user:1000` 是一个 10MB 的 Hash，包含 10 万字段。
3. 检查代码发现某功能误将全量用户数据存入单个 Hash。  
**解决方案**：
1. 临时方案：拆分 `user:1000` 为多个小 Hash（如 `user:1000:profile`、`user:1000:orders`）。
2. 长期方案：改用分页查询或本地缓存。

---

## **总结**
| 问题类型       | 优化方向                          | 工具/命令                          |
|----------------|-----------------------------------|-----------------------------------|
| 内存不足       | 淘汰策略、大 Key 拆分             | `maxmemory-policy`、`--bigkeys`  |
| CPU 高负载     | 慢查询、复杂命令                  | `SLOWLOG GET`、`SCAN` 替代 `KEYS`|
| 连接数打满     | 连接池、限流                      | `maxclients`、客户端配置          |
| 网络延迟       | 压缩、批量操作                    | `PIPELINE`、Snappy 压缩           |

通过紧急处理、根因分析、长期优化和预防措施，可以系统性解决 Redis 性能问题，避免再次“爆掉”。
