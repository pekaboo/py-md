# Redis 的 Lua 脚本功能是什么？如何使用？

**难度**：中等

**创建时间**：2025-10-06 15:42:33

## 答案
Redis 的 **Lua 脚本功能** 允许在 Redis 服务器端直接执行 Lua 脚本，实现原子性的复杂操作，避免多次网络往返和竞态条件。以下是其核心作用、使用方法及示例：

---

### **1. Lua 脚本的核心作用**
#### **（1）原子性操作**
- Redis 保证单个 Lua 脚本的执行是**原子性**的，脚本中的所有命令会按顺序执行，不会被其他客户端命令打断。
- 适用于需要多步操作的场景（如条件更新、事务性操作）。

#### **（2）减少网络开销**
- 将多个命令合并为一个脚本，减少客户端与服务器之间的网络往返（RTT）。

#### **（3）复杂逻辑处理**
- 支持条件判断、循环、字符串处理等逻辑，弥补 Redis 命令的局限性。

#### **（4）避免竞态条件**
- 替代 `WATCH/MULTI/EXEC` 事务，避免因重试导致的性能问题。

---

### **2. 基本使用方法**
#### **（1）`EVAL` 命令**
直接执行 Lua 脚本：
```bash
EVAL <script> <number_of_keys> <key1> <key2> ... <arg1> <arg2> ...
```
- **`<script>`**：Lua 脚本内容。
- **`<number_of_keys>`**：脚本中使用的键（Key）数量。
- **`<key1> <key2> ...`**：键的参数，可通过 `KEYS[1]`, `KEYS[2]` 访问。
- **`<arg1> <arg2> ...`**：其他参数，可通过 `ARGV[1]`, `ARGV[2]` 访问。

**示例**：
```bash
# 脚本：如果键 "counter" 存在，则将其值 +1；否则初始化为 1
EVAL "local current = redis.call('GET', KEYS[1]); \
      if current == false then \
          return redis.call('SET', KEYS[1], '1'); \
      else \
          return redis.call('INCR', KEYS[1]); \
      end" 1 counter
```

#### **（2）`EVALSHA` 命令**
先预编译脚本获取 SHA1 校验和，后续通过 SHA1 执行以减少网络传输：
```bash
# 1. 预编译脚本
SCRIPT LOAD "local current = redis.call('GET', KEYS[1]); if current == false then return redis.call('SET', KEYS[1], '1'); else return redis.call('INCR', KEYS[1]); end"
# 返回 SHA1: "5f3b2c6d..."

# 2. 通过 SHA1 执行
EVALSHA 5f3b2c6d... 1 counter
```

#### **（3）`SCRIPT` 命令**
管理脚本缓存：
- `SCRIPT FLUSH`：清空脚本缓存。
- `SCRIPT EXISTS <sha1>`：检查脚本是否在缓存中。

---

### **3. Lua 脚本中的 Redis 操作**
通过 `redis.call()` 或 `redis.pcall()` 调用 Redis 命令：
- **`redis.call()`**：出错时抛出 Lua 错误。
- **`redis.pcall()`**：出错时返回错误信息（不中断脚本）。

**常用命令示例**：
```lua
redis.call('SET', 'key', 'value')          -- 设置键值
redis.call('GET', 'key')                   -- 获取值
redis.call('INCR', 'counter')              -- 自增
redis.call('HSET', 'hash', 'field', 'val') -- 哈希表操作
redis.call('LPUSH', 'list', 'item')        -- 列表操作
```

---

### **4. 实际应用场景**
#### **（1）限流器（Rate Limiter）**
```lua
-- 参数：KEYS[1]=限流键, ARGV[1]=时间窗口(秒), ARGV[2]=最大请求数
local key = KEYS[1]
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])

local current = redis.call('GET', key)
if current == false then
    redis.call('SET', key, 1, 'EX', window)  -- 初始化并设置过期时间
    return 1
else
    local new_val = tonumber(current) + 1
    if new_val > limit then
        return 0  -- 超过限制
    else
        redis.call('SET', key, new_val, 'EX', window)
        return 1
    end
end
```

#### **（2）分布式锁**
```lua
-- 参数：KEYS[1]=锁键, ARGV[1]=锁值(唯一标识), ARGV[2]=过期时间(毫秒)
local lock_key = KEYS[1]
local lock_value = ARGV[1]
local expire_time = ARGV[2]

-- 尝试获取锁
if redis.call('SETNX', lock_key, lock_value) == 1 then
    redis.call('PEXPIRE', lock_key, expire_time)
    return 1
else
    -- 检查锁是否已过期（防止死锁）
    local current_value = redis.call('GET', lock_key)
    if current_value == false then
        return 0
    elseif current_value == lock_value then
        -- 续期逻辑（可选）
        return 0
    else
        return 0
    end
end
```

#### **（3）事务性更新**
```lua
-- 参数：KEYS[1]=用户ID, ARGV[1]=扣减金额, ARGV[2]=当前余额
local user_id = KEYS[1]
local deduct_amount = tonumber(ARGV[1])
local current_balance = tonumber(redis.call('GET', user_id) or 0)

if current_balance >= deduct_amount then
    redis.call('SET', user_id, current_balance - deduct_amount)
    return 1  -- 成功
else
    return 0  -- 余额不足
end
```

---

### **5. 注意事项**
1. **避免长时间运行**：Lua 脚本会阻塞 Redis 其他操作，建议单脚本执行时间 < 1ms。
2. **键名一致性**：通过 `KEYS` 和 `ARGV` 传递参数，避免硬编码键名。
3. **错误处理**：使用 `redis.pcall()` 捕获异常，防止脚本中断。
4. **调试技巧**：
   - 在本地 Lua 环境（如 [Lua 解释器](https://www.lua.org/)）中测试逻辑。
   - 使用 `redis-cli --eval` 调试脚本：
     ```bash
     redis-cli --eval script.lua key1 key2 , arg1 arg2
     ```

---

### **6. 示例：完整的 Java 调用**
```java
import redis.clients.jedis.Jedis;

public class RedisLuaExample {
    public static void main(String[] args) {
        Jedis jedis = new Jedis("localhost");
        
        // 定义 Lua 脚本
        String script = 
            "local current = redis.call('GET', KEYS[1]); " +
            "if current == false then " +
            "   return redis.call('SET', KEYS[1], ARGV[1]); " +
            "else " +
            "   return redis.call('SET', KEYS[1], tonumber(current) + tonumber(ARGV[1])); " +
            "end";
        
        // 执行脚本
        String sha1 = jedis.scriptLoad(script);
        Object result = jedis.evalsha(sha1, 1, "counter", "5");
        
        System.out.println("Result: " + result);
        jedis.close();
    }
}
```

---

### **总结**
Redis 的 Lua 脚本通过原子性、高性能和灵活性，成为处理复杂逻辑的利器。合理使用可避免竞态条件、减少网络开销，并简化分布式系统设计。建议将常用脚本预加载（`SCRIPT LOAD`），并通过 SHA1 复用以提高效率。
