# 如何使用 Redis 快速实现排行榜？

**难度**：中等

**创建时间**：2025-10-06 05:59:12

## 答案
在 Redis 中实现排行榜功能非常高效，主要利用其 **有序集合（Sorted Set）** 数据结构。有序集合通过分数（score）排序成员（member），支持快速插入、更新、删除和范围查询，天然适合排行榜场景。

---

## **1. 核心命令**
Redis 的 `ZADD`、`ZRANGE`、`ZREVRANGE` 等命令是实现排行榜的关键：

| 命令 | 作用 | 示例 |
|------|------|------|
| `ZADD key score member` | 添加或更新成员分数 | `ZADD leaderboard 1000 "user:1"` |
| `ZRANGE key start stop [WITHSCORES]` | 按分数升序获取排名（从低到高） | `ZRANGE leaderboard 0 9 WITHSCORES` |
| `ZREVRANGE key start stop [WITHSCORES]` | 按分数降序获取排名（从高到低，适合排行榜） | `ZREVRANGE leaderboard 0 9 WITHSCORES` |
| `ZSCORE key member` | 获取成员分数 | `ZSCORE leaderboard "user:1"` |
| `ZRANK key member` | 获取成员升序排名（从0开始） | `ZRANK leaderboard "user:1"` |
| `ZREVRANK key member` | 获取成员降序排名（从0开始，适合排行榜） | `ZREVRANK leaderboard "user:1"` |
| `ZINCRBY key increment member` | 增加成员分数 | `ZINCRBY leaderboard 50 "user:1"` |
| `ZREM key member` | 删除成员 | `ZREM leaderboard "user:1"` |

---

## **2. 快速实现排行榜**
### **场景示例：游戏积分排行榜**
#### **（1）添加/更新用户分数**
```bash
# 用户1获得1000分
ZADD leaderboard 1000 "user:1"
# 用户2获得1500分
ZADD leaderboard 1500 "user:2"
# 用户1再获得200分（总分变为1200）
ZINCRBY leaderboard 200 "user:1"
```

#### **（2）查询前10名（降序）**
```bash
# 获取前10名用户及其分数（排行榜）
ZREVRANGE leaderboard 0 9 WITHSCORES
```
输出示例：
```
1) "user:2"
2) "1500"
3) "user:1"
4) "1200"
```

#### **（3）查询用户排名**
```bash
# 查询用户1的排名（从0开始，实际显示需+1）
ZREVRANK leaderboard "user:1"  # 返回1（表示第2名）
```

#### **（4）查询用户分数**
```bash
ZSCORE leaderboard "user:1"  # 返回"1200"
```

#### **（5）删除用户**
```bash
ZREM leaderboard "user:1"
```

---

## **3. 高级功能**
### **（1）时间范围排行榜**
如果需要按时间周期（如每日、每周）统计，可以使用 **多个有序集合 + `ZUNIONSTORE`** 合并：
```bash
# 合并昨日和今日的排行榜（权重分别为0.5和1）
ZUNIONSTORE weekly_leaderboard 2 yesterday_leaderboard today_leaderboard WEIGHTS 0.5 1
```

### **（2）分页查询**
```bash
# 查询第11~20名（偏移量10，获取10条）
ZREVRANGE leaderboard 10 19 WITHSCORES
```

### **（3）处理分数相同的情况**
Redis 默认按分数升序排序，分数相同则按成员字典序排序。如需自定义规则，可以在 `member` 中嵌入时间戳：
```bash
# 格式：member:timestamp（如"user:1:1630000000"）
ZADD leaderboard 1000 "user:1:1630000000"
```

---

## **4. 代码示例（Python）**
使用 `redis-py` 库实现：
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# 添加/更新分数
r.zadd("leaderboard", {"user:1": 1000})
r.zincrby("leaderboard", 200, "user:1")

# 查询前10名
top10 = r.zrevrange("leaderboard", 0, 9, withscores=True)
for rank, (user, score) in enumerate(top10, 1):
    print(f"Rank {rank}: {user.decode()}, Score: {int(score)}")

# 查询用户排名和分数
user = "user:1"
rank = r.zrevrank("leaderboard", user) + 1  # +1因为从0开始
score = r.zscore("leaderboard", user)
print(f"{user} is Rank #{rank} with Score {int(score)}")
```

---

## **5. 性能优化**
1. **批量操作**：使用 `pipeline` 减少网络开销。
   ```python
   with r.pipeline() as pipe:
       for user_id, score in updates.items():
           pipe.zadd("leaderboard", {user_id: score})
       pipe.execute()
   ```
2. **分片存储**：超大规模排行榜可按业务分片（如 `leaderboard:202310` 表示2023年10月数据）。
3. **本地缓存**：对Top N数据做本地缓存，减少Redis查询。

---

## **6. 适用场景**
- 游戏排名（积分、战力）
- 直播平台礼物排行榜
- 电商销售排行榜
- 社交平台热度榜（点赞、评论数）

---

## **总结**
Redis 的有序集合（Sorted Set）是排行榜的天然解决方案，支持：
- **高效排序**：O(log N) 复杂度的插入、更新、删除。
- **灵活查询**：Top N、分页、用户排名、分数增量更新。
- **原子性操作**：适合高并发场景。

通过合理设计 `member` 和 `score`，可以覆盖绝大多数排行榜需求。
