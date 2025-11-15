# Redis 中如何实现分布式锁？

**难度**：中等

**创建时间**：2025-10-06 05:57:37

## 答案
在 Redis 中实现分布式锁的核心目标是确保**多个客户端在分布式环境下对共享资源的互斥访问**，防止并发操作导致数据不一致。Redis 官方推荐使用 **Redlock 算法**（基于多节点）或简化版的 **单节点锁**（需处理异常情况）。以下是详细实现方案及注意事项：

---

## **一、单节点分布式锁（基础版）**
### **1. 核心命令**
使用 `SETNX`（SET if Not eXists）命令实现锁的原子性获取，结合 `EXPIRE` 设置锁的过期时间，避免死锁。

```bash
# 获取锁（原子操作，Redis 2.6.12+ 支持）
SET lock_key unique_value NX PX 30000
```
- **`lock_key`**：锁的键名（如 `resource_lock`）。
- **`unique_value`**：客户端唯一标识（如 UUID），用于安全释放锁。
- **`NX`**：仅当键不存在时设置。
- **`PX 30000`**：锁的过期时间（30秒），防止客户端崩溃后锁无法释放。

### **2. 释放锁**
使用 Lua 脚本保证**检查唯一值+删除键**的原子性，避免误删其他客户端的锁。

```lua
-- 释放锁的 Lua 脚本
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```
执行命令：
```bash
EVAL "脚本内容" 1 lock_key unique_value
```

### **3. 缺点**
- **单点故障**：若 Redis 主节点崩溃，锁可能丢失（即使有从节点，因异步复制可能导致锁重复获取）。
- **时钟漂移**：若服务器时间不准，`PX` 设定的过期时间可能失效。

---

## **二、Redlock 算法（多节点版，官方推荐）**
### **1. 算法步骤**
Redlock 通过在 **N 个独立 Redis 节点**上尝试获取锁，降低单点故障风险。步骤如下：

1. **获取当前时间**（毫秒级）。
2. **按顺序向 N 个节点申请锁**：
   - 使用相同 `lock_key` 和 `unique_value`。
   - 设置随机过期时间（如 `PX 10000`，10秒）。
   - 若节点返回 `OK`，记录获取到锁的时间。
3. **计算锁的有效时间**：
   - `锁有效时间 = 过期时间 - (当前时间 - 第一步时间)`。
   - 若多数节点（`N/2 + 1`）获取成功且剩余有效时间 > 0，则认为获取锁成功。
4. **释放锁**：向所有节点发送删除请求（无论是否获取成功）。

### **2. 代码示例（伪代码）**
```python
import redis
import time
import uuid

def acquire_redlock(nodes, lock_key, ttl=10000):
    unique_value = str(uuid.uuid4())
    voted = 0
    start_time = time.time() * 1000  # 毫秒

    for node in nodes:
        r = redis.StrictRedis(host=node['host'], port=node['port'])
        try:
            # 尝试获取锁
            if r.set(lock_key, unique_value, nx=True, px=ttl):
                voted += 1
        except:
            pass

        # 超过半数且剩余时间足够
        remaining_time = ttl - (time.time() * 1000 - start_time)
        if voted > len(nodes) // 2 and remaining_time > 0:
            return unique_value, remaining_time

    # 获取失败，释放所有锁
    release_redlock(nodes, lock_key, unique_value)
    return None, 0

def release_redlock(nodes, lock_key, unique_value):
    for node in nodes:
        r = redis.StrictRedis(host=node['host'], port=node['port'])
        try:
            # 使用 Lua 脚本安全释放锁
            script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
            """
            r.eval(script, 1, lock_key, unique_value)
        except:
            pass
```

### **3. 注意事项**
- **节点数量**：建议至少 5 个独立 Redis 节点，容忍 2 个节点故障。
- **时钟同步**：各节点需时间同步（如 NTP），避免时钟漂移导致锁提前过期。
- **性能开销**：多次网络往返可能影响响应速度，需权衡一致性与性能。

---

## **三、Redisson 实现（生产级方案）**
Redisson 是一个基于 Redis 的 Java 客户端，提供了开箱即用的分布式锁实现（支持单节点和 Redlock）。

### **1. 单节点锁示例**
```java
Config config = new Config();
config.useSingleServer().setAddress("redis://127.0.0.1:6379");
RedissonClient redisson = Redisson.create(config);

RLock lock = redisson.getLock("resource_lock");
try {
    // 尝试获取锁，最多等待100秒，锁自动过期30秒
    boolean isLocked = lock.tryLock(100, 30, TimeUnit.SECONDS);
    if (isLocked) {
        // 执行业务逻辑
    }
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
} finally {
    lock.unlock();
}
```

### **2. Redlock 示例**
```java
Config config1 = new Config();
config1.useSingleServer().setAddress("redis://127.0.0.1:6379");
Config config2 = new Config();
config2.useSingleServer().setAddress("redis://127.0.0.2:6379");

RedissonClient redisson1 = Redisson.create(config1);
RedissonClient redisson2 = Redisson.create(config2);

RedissonRedLock redLock = new RedissonRedLock(
    redisson1.getLock("resource_lock"),
    redisson2.getLock("resource_lock")
);

try {
    redLock.tryLock(100, 30, TimeUnit.SECONDS);
    // 执行业务逻辑
} finally {
    redLock.unlock();
}
```

---

## **四、常见问题与解决方案**
### **1. 锁过期导致并发问题**
- **问题**：业务执行时间超过锁的过期时间，其他客户端可能获取锁。
- **解决方案**：
  - 启动后台线程定期续期（如 Redisson 的 `WatchDog` 机制）。
  - 预估最长执行时间，合理设置 `PX`。

### **2. 误删其他客户端的锁**
- **问题**：释放锁时未校验 `unique_value`，导致误删。
- **解决方案**：必须使用 Lua 脚本保证原子性。

### **3. Redis 集群脑裂**
- **问题**：网络分区导致部分节点不可用，可能同时存在多个锁持有者。
- **解决方案**：使用 Redlock 或等待分区恢复后人工干预。

---

## **五、对比与选型建议**
| **方案**       | **适用场景**                          | **优点**                     | **缺点**                     |
|----------------|--------------------------------------|------------------------------|------------------------------|
| 单节点锁       | 简单场景，对一致性要求不高           | 实现简单，性能高             | 单点故障风险                 |
| Redlock        | 高可用要求，容忍部分节点故障         | 降低单点风险                 | 实现复杂，性能开销大         |
| Redisson        | Java 生态，需要开箱即用              | 功能完善，支持续期和 Redlock | 依赖特定客户端               |

---

## **总结**
- **简单场景**：使用单节点锁 + Lua 脚本释放（需处理重试和过期）。
- **高可用场景**：采用 Redlock 算法或多节点部署 + Redisson 客户端。
- **关键原则**：
  1. 锁必须有唯一标识（防止误删）。
  2. 锁必须设置过期时间（防止死锁）。
  3. 释放锁必须原子性校验标识（避免误删）。
  4. 考虑锁续期和故障恢复机制。

Redis 分布式锁是分布式系统中协调资源访问的基础工具，合理选择方案可有效避免并发问题。
