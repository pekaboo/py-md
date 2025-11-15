# Redis 中常见的数据类型有哪些？

**难度**：简单

**创建时间**：2025-10-06 06:02:07

## 答案
Redis 提供了多种高效的数据类型，每种类型针对特定场景优化，支持丰富的原子操作。以下是 Redis 中常见的数据类型及其核心特性和应用场景的详细总结：

---

### **1. String（字符串）**
- **底层实现**：动态字符串（SDS, Simple Dynamic String），支持自动扩容和二进制安全（可存储图片、序列化对象等）。
- **核心操作**：
  - `SET key value` / `GET key`：存储和获取字符串。
  - `INCR key` / `DECR key`：原子增减（适合计数器）。
  - `SETEX key seconds value`：设置过期时间。
- **应用场景**：
  - 缓存（如 HTML 片段、JSON 数据）。
  - 分布式锁（`SETNX key value`，仅当键不存在时设置）。
  - 计数器（如文章访问量、点赞数）。
- **示例**：
  ```bash
  SET user:1000:name "Alice"  # 存储用户名
  GET user:1000:name          # 获取用户名
  INCR page:views             # 页面访问量+1
  ```

---

### **2. Hash（哈希）**
- **底层实现**：压缩列表（ziplist）或哈希表（dict），根据字段数量和值大小自动选择。
- **核心操作**：
  - `HSET key field value` / `HGET key field`：设置和获取字段值。
  - `HMSET key field1 value1 field2 value2`：批量设置。
  - `HGETALL key`：获取所有字段和值。
  - `HINCRBY key field increment`：原子增减字段值。
- **应用场景**：
  - 存储对象（如用户信息、商品属性）。
  - 减少内存占用（相比多个 String 键，Hash 更节省空间）。
- **示例**：
  ```bash
  HSET user:1000 name "Alice" age 25  # 存储用户对象
  HGET user:1000 name                  # 获取用户名
  HINCRBY user:1000 age 1              # 年龄+1
  ```

---

### **3. List（列表）**
- **底层实现**：双向链表或快速列表（quicklist，结合了链表和压缩列表的优点）。
- **核心操作**：
  - `LPUSH key value1 value2` / `RPUSH key value1 value2`：从头部或尾部插入。
  - `LPOP key` / `RPOP key`：从头部或尾部弹出。
  - `LRANGE key start stop`：获取指定范围内的元素。
  - `BLPOP key timeout`：阻塞式弹出（队列为空时等待）。
- **应用场景**：
  - 消息队列（如订单处理、任务调度）。
  - 最新消息排行（如微博时间线）。
- **示例**：
  ```bash
  LPUSH messages "task1" "task2"  # 插入任务到队列头部
  RPOP messages                   # 从队列尾部取出任务
  LRANGE messages 0 -1           # 获取所有消息
  ```

---

### **4. Set（集合）**
- **底层实现**：整数集合（intset）或哈希表（dict），根据元素类型和数量自动选择。
- **核心操作**：
  - `SADD key member1 member2`：添加元素。
  - `SMEMBERS key`：获取所有元素。
  - `SISMEMBER key member`：检查元素是否存在。
  - `SINTER key1 key2`：交集（适合共同好友、标签匹配）。
  - `SUNION key1 key2`：并集。
  - `SDIFF key1 key2`：差集。
- **应用场景**：
  - 标签系统（如文章分类、用户兴趣）。
  - 共同关注、推荐系统。
  - 去重（如用户访问记录）。
- **示例**：
  ```bash
  SADD tags:article:100 "tech" "redis"  # 添加文章标签
  SISMEMBER tags:article:100 "tech"     # 检查标签是否存在
  SINTER tags:user:1 tags:user:2        # 获取两个用户的共同标签
  ```

---

### **5. ZSet（有序集合）**
- **底层实现**：跳跃表（skiplist）或压缩列表（ziplist），根据元素数量和长度自动选择。
- **核心操作**：
  - `ZADD key score member`：添加元素及其分数。
  - `ZRANGE key start stop [WITHSCORES]`：按分数排序获取元素。
  - `ZREVRANGE key start stop [WITHSCORES]`：逆序获取。
  - `ZRANK key member`：获取元素的排名（从小到大）。
  - `ZREVRANK key member`：逆序排名。
  - `ZRANGEBYSCORE key min max`：按分数范围获取。
- **应用场景**：
  - 排行榜（如游戏得分、热搜榜）。
  - 范围查询（如时间范围内的数据）。
- **示例**：
  ```bash
  ZADD leaderboard 1000 "Alice" 800 "Bob"  # 添加玩家得分
  ZRANGE leaderboard 0 -1 WITHSCORES       # 获取排行榜（按分数升序）
  ZREVRANGE leaderboard 0 2                # 获取前3名（按分数降序）
  ZRANGEBYSCORE leaderboard 900 1000       # 获取900-1000分的玩家
  ```

---

### **6. 其他特殊类型**
#### **BitMap（位图）**
- **底层实现**：字符串的二进制位操作。
- **核心操作**：
  - `SETBIT key offset value`：设置或清除位。
  - `GETBIT key offset`：获取位的值。
  - `BITCOUNT key`：统计设置为1的位数。
  - `BITOP AND/OR/XOR/NOT destkey key1 key2`：位运算。
- **应用场景**：
  - 用户在线状态统计（如百万用户每日活跃）。
  - 布隆过滤器（Bloom Filter）实现。
- **示例**：
  ```bash
  SETBIT user:sign:20231001 1000 1  # 标记用户1000在20231001签到
  GETBIT user:sign:20231001 1000    # 检查用户1000是否签到
  BITCOUNT user:sign:20231001        # 统计签到用户数
  ```

#### **HyperLogLog（基数统计）**
- **底层实现**：概率算法，占用极小内存（约12KB）统计不重复元素数量。
- **核心操作**：
  - `PFADD key element1 element2`：添加元素。
  - `PFCOUNT key`：获取基数估计值。
  - `PFMERGE destkey sourcekey1 sourcekey2`：合并多个HyperLogLog。
- **应用场景**：
  - 独立访客（UV）统计。
  - 大规模数据去重计数。
- **示例**：
  ```bash
  PFADD page:uv:20231001 "user1" "user2" "user1"  # 添加用户（重复用户不计）
  PFCOUNT page:uv:20231001                       # 估计独立访客数（结果≈2）
  ```

#### **Geo（地理位置）**
- **底层实现**：基于ZSet存储经纬度，使用Geohash编码。
- **核心操作**：
  - `GEOADD key longitude latitude member`：添加地理位置。
  - `GEODIST key member1 member2 [unit]`：计算两个位置的距离。
  - `GEORADIUS key longitude latitude radius m|km|ft|mi`：查询指定范围内的位置。
- **应用场景**：
  - 附近的人（LBS服务）。
  - 物流配送范围查询。
- **示例**：
  ```bash
  GEOADD cities 116.40 39.90 "Beijing" 121.47 31.23 "Shanghai"  # 添加城市坐标
  GEODIST cities "Beijing" "Shanghai" km                        # 计算北京到上海的距离（单位：km）
  GEORADIUS cities 116.40 39.90 500 km                          # 查询北京500km范围内的城市
  ```

#### **Stream（流，Redis 5.0+）**
- **底层实现**：类似Kafka的消息流结构，支持消费者组。
- **核心操作**：
  - `XADD key ID field value`：添加消息到流。
  - `XREAD [COUNT count] [STREAMS key1 key2 ...] ID1 ID2 ...`：读取消息。
  - `XGROUP CREATE key groupname ID`：创建消费者组。
  - `XREADGROUP GROUP groupname consumername [COUNT count] STREAMS key ID`：消费者组读取。
- **应用场景**：
  - 消息队列（支持多消费者）。
  - 事件溯源（Event Sourcing）。
- **示例**：
  ```bash
  XADD orders * item "book" price 100  # 添加订单消息
  XREAD STREAMS orders 0               # 读取订单流（从ID=0开始）
  XGROUP CREATE orders mygroup $       # 创建消费者组
  XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS orders >  # 消费者组读取
  ```

---

### **总结：Redis 数据类型选择指南**
| **场景**               | **推荐类型**       | **理由**                                  |
|------------------------|--------------------|------------------------------------------|
| 缓存、计数器           | String             | 简单高效，支持原子操作                   |
| 存储对象属性           | Hash               | 节省内存，支持字段级操作                 |
| 消息队列、时间线       | List               | 双向操作，支持阻塞弹出                   |
| 标签、去重             | Set                | 唯一性保证，支持集合运算                 |
| 排行榜、范围查询       | ZSet               | 按分数排序，支持范围操作                 |
| 用户签到、状态统计     | BitMap             | 极低内存占用，位操作高效                 |
| 大规模UV统计           | HyperLogLog        | 概率算法，12KB内存估计百万级不重复数     |
| 附近的人、地理位置     | Geo                | 基于ZSet，支持距离计算和范围查询         |
| 消息队列（多消费者）   | Stream             | 支持消费者组，类似Kafka                  |

Redis 的数据类型设计紧密结合内存优化和原子操作，开发者应根据具体场景选择最合适的类型，以最大化性能和资源利用率。
