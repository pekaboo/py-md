# 说说 MyBatis 的缓存机制？

**难度**：中等

**创建时间**：2025-10-06 06:02:45

## 答案
MyBatis 的缓存机制是其核心特性之一，通过多级缓存设计显著提升数据库访问性能，尤其适用于读多写少的场景。其缓存体系分为**一级缓存（本地缓存）**和**二级缓存（全局缓存）**，两者协同工作，同时支持与第三方缓存（如 Ehcache、Redis）集成。以下是详细解析：

---

### **一、一级缓存（Local Cache，SqlSession 级别）**
#### **1. 核心特性**
- **作用范围**：绑定到单个 `SqlSession` 对象，生命周期与 `SqlSession` 一致。  
- **默认启用**：无需配置，MyBatis 自动为每个 `SqlSession` 创建缓存。  
- **存储位置**：内存中，以 `Map` 形式存储（键为 `StatementId + 参数`，值为查询结果）。

#### **2. 工作流程**
1. **首次查询**：执行 SQL 后，结果存入一级缓存。  
2. **相同查询复用**：同一 `SqlSession` 内，若执行相同的 SQL（相同 `StatementId` 和参数），直接从缓存返回结果。  
3. **失效场景**：  
   - 执行任何增删改操作（`INSERT`/`UPDATE`/`DELETE`）会自动清空一级缓存。  
   - 调用 `sqlSession.clearCache()` 手动清空。  
   - 不同 `SqlSession` 之间不共享缓存（每个 `SqlSession` 有独立缓存）。

#### **3. 示例代码**
```java
SqlSession sqlSession = sqlSessionFactory.openSession();
try {
    // 首次查询，结果存入一级缓存
    User user1 = sqlSession.selectOne("com.example.mapper.UserMapper.selectById", 1);
    
    // 相同查询直接从缓存返回
    User user2 = sqlSession.selectOne("com.example.mapper.UserMapper.selectById", 1);
    System.out.println(user1 == user2); // 输出 true（同一对象）
    
    // 执行更新操作，清空一级缓存
    sqlSession.update("com.example.mapper.UserMapper.updateName", Map.of("id", 1, "name", "Alice"));
    
    // 再次查询，重新执行 SQL
    User user3 = sqlSession.selectOne("com.example.mapper.UserMapper.selectById", 1);
} finally {
    sqlSession.close();
}
```

#### **4. 适用场景**
- 单次数据库操作中的多次相同查询（如循环内查询）。  
- 避免在同一个 `SqlSession` 中混用读写操作（否则缓存可能失效）。

---

### **二、二级缓存（Second Level Cache，Mapper 级别）**
#### **1. 核心特性**
- **作用范围**：跨 `SqlSession`，属于 `Mapper` 命名空间级别的缓存。  
- **默认关闭**：需在配置文件中显式启用。  
- **存储位置**：默认使用 `PerpetualCache`（内存缓存），可集成 Ehcache、Redis 等第三方缓存。

#### **2. 启用与配置**
1. **全局配置**：在 `mybatis-config.xml` 中开启二级缓存：
   ```xml
   <settings>
       <setting name="cacheEnabled" value="true"/>
   </settings>
   ```
2. **Mapper 级别配置**：在 Mapper XML 文件中添加 `<cache>` 标签：
   ```xml
   <mapper namespace="com.example.mapper.UserMapper">
       <cache eviction="LRU" flushInterval="60000" size="512" readOnly="true"/>
       <!-- 其他 SQL 定义 -->
   </mapper>
   ```
   - **参数说明**：  
     - `eviction`：回收策略（LRU、FIFO、SOFT、WEAK）。  
     - `flushInterval`：缓存刷新间隔（毫秒）。  
     - `size`：缓存对象数量。  
     - `readOnly`：是否只读（`true` 时返回同一对象，`false` 返回副本）。

3. **POJO 要求**：缓存的实体类需实现 `Serializable` 接口（否则序列化可能失败）。

#### **3. 工作流程**
1. **首次查询**：结果存入一级缓存和二级缓存。  
2. **跨 Session 复用**：不同 `SqlSession` 执行相同查询时，优先从二级缓存读取。  
3. **失效场景**：  
   - 执行任何增删改操作（`INSERT`/`UPDATE`/`DELETE`）会清空对应 Mapper 的二级缓存。  
   - 手动调用 `sqlSession.clearCache()` 仅清空一级缓存。  
   - 分布式环境下需注意缓存一致性（需结合 Redis 等分布式缓存）。

#### **4. 示例代码**
```java
// 第一个 SqlSession
SqlSession sqlSession1 = sqlSessionFactory.openSession();
try {
    User user1 = sqlSession1.selectOne("com.example.mapper.UserMapper.selectById", 1);
} finally {
    sqlSession1.close(); // 关闭时一级缓存失效，但结果已存入二级缓存
}

// 第二个 SqlSession（不同 Session）
SqlSession sqlSession2 = sqlSessionFactory.openSession();
try {
    // 直接从二级缓存读取
    User user2 = sqlSession2.selectOne("com.example.mapper.UserMapper.selectById", 1);
} finally {
    sqlSession2.close();
}
```

#### **5. 适用场景**
- 跨事务或跨线程的相同查询（如 Web 应用中不同请求的相同数据）。  
- 读多写少且数据变更不频繁的表（如配置表、字典表）。

---

### **三、缓存注解与细节**
#### **1. 注解方式配置**
- **`@CacheNamespace`**：在 Mapper 接口上使用注解启用二级缓存：
  ```java
  @CacheNamespace(eviction = FifoCache.class, flushInterval = 60000)
  public interface UserMapper {
      @Select("SELECT * FROM user WHERE id = #{id}")
      User selectById(int id);
  }
  ```

#### **2. 缓存刷新策略**
- **手动刷新**：调用 `sqlSession.getConfiguration().getCache("namespace").clear()`。  
- **自动刷新**：通过 `flushInterval` 定时刷新，或结合 `SqlSession` 提交时刷新。

#### **3. 缓存键生成**
- 默认使用 `StatementId + 参数` 作为缓存键。  
- 自定义缓存键：实现 `org.apache.ibatis.cache.CacheKey` 接口。

---

### **四、与第三方缓存集成**
#### **1. 集成 Ehcache**
1. 添加依赖：
   ```xml
   <dependency>
       <groupId>org.mybatis.caches</groupId>
       <artifactId>mybatis-ehcache</artifactId>
       <version>1.2.1</version>
   </dependency>
   ```
2. 配置 `ehcache.xml`：
   ```xml
   <ehcache>
       <defaultCache maxEntriesLocalHeap="1000" timeToIdleSeconds="300"/>
   </ehcache>
   ```
3. 在 Mapper XML 中引用：
   ```xml
   <cache type="org.mybatis.caches.ehcache.EhcacheCache"/>
   ```

#### **2. 集成 Redis**
1. 添加依赖：
   ```xml
   <dependency>
       <groupId>org.mybatis.caches</groupId>
       <artifactId>mybatis-redis</artifactId>
       <version>1.0.0-beta2</version>
   </dependency>
   ```
2. 配置 Redis 连接：
   ```properties
   redis.host=localhost
   redis.port=6379
   ```
3. 在 Mapper XML 中引用：
   ```xml
   <cache type="org.mybatis.caches.redis.RedisCache"/>
   ```

---

### **五、缓存使用建议**
1. **合理选择缓存级别**：  
   - 单线程或短事务场景用一级缓存。  
   - 多线程或长事务场景用二级缓存。  
2. **避免缓存雪崩**：  
   - 设置不同的 `flushInterval` 或随机过期时间。  
3. **处理缓存穿透**：  
   - 对空结果也缓存（如 `CacheKey: "NULL"`），或使用布隆过滤器。  
4. **分布式环境**：  
   - 优先使用 Redis 等分布式缓存，避免本地缓存不一致。

---

### **六、总结**
| **缓存类型**   | **作用范围**       | **生命周期**               | **配置方式**               | **典型场景**                     |
|----------------|--------------------|----------------------------|----------------------------|----------------------------------|
| 一级缓存       | SqlSession 级别   | 与 SqlSession 同生命周期   | 默认启用，无需配置         | 单次操作中的多次相同查询         |
| 二级缓存       | Mapper 级别        | 跨 SqlSession，手动或定时刷新 | 显式配置 `<cache>` 或注解 | 跨事务/线程的相同查询（读多写少） |

**最佳实践**：  
- 结合业务场景选择缓存策略，避免盲目启用二级缓存。  
- 在高并发或分布式系统中，优先使用 Redis 等分布式缓存解决一致性问题。  
- 监控缓存命中率，调整 `size` 和 `flushInterval` 参数优化性能。
