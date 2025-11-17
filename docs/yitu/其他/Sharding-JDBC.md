Sharding-JDBC 是 ShardingSphere 生态中的轻量级分库分表框架，基于 JDBC 层实现，无需额外部署中间件，仅通过配置即可实现数据分片（分库、分表）、读写分离等功能，对业务代码无侵入性。
以下是 Spring Boot 环境下 Sharding-JDBC 5.x 版本的完整使用步骤（主流场景：水平分表 / 分库分表），包含核心配置、代码实现、测试验证。
一、核心概念先明确
使用前需理解 3 个关键概念：
分片键：用于拆分数据的字段（如 user_id，按其取模 / 范围拆分数据）；
分片策略：定义数据如何分配到不同库 / 表（如 user_id % 2 决定写入 user_1 或 user_2）；
数据源：被分片的原始数据库（可多个库，也可单个库分表）。
二、环境准备
1. 技术栈依赖
框架：Spring Boot 2.7.x + MyBatis-Plus（简化 DAO 开发，也可直接用 MyBatis）；
数据库：MySQL 8.0（示例用单库分表，多库同理）；
分库分表：Sharding-JDBC 5.3.2（ShardingSphere 核心依赖）。
2. Maven 依赖引入
在 pom.xml 中添加核心依赖（排除冲突的数据源自动配置）：
xml
<!-- Spring Boot 核心 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.15</version>
    <relativePath/>
</parent>

<!-- Web + 数据库基础 -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-jdbc</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- MyBatis-Plus（简化 CRUD） -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.3.1</version>
    </dependency>

    <!-- Sharding-JDBC 核心依赖（分库分表） -->
    <dependency>
        <groupId>org.apache.shardingsphere</groupId>
        <artifactId>shardingsphere-jdbc-core-spring-boot-starter</artifactId>
        <version>5.3.2</version>
    </dependency>

    <!--  lombok（简化实体类） -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
3. 数据库准备（单库分表示例）
假设要对 user 表进行水平分表，拆分为 2 张表：user_1、user_2（表结构完全一致）。
创建 SQL（MySQL）：
sql
-- 数据库（可多个库，示例用单库）
CREATE DATABASE IF NOT EXISTS sharding_db DEFAULT CHARSET utf8mb4;
USE sharding_db;

-- 分表 1：user_1
CREATE TABLE IF NOT EXISTS user_1 (
    id BIGINT NOT NULL COMMENT '主键ID',
    user_id BIGINT NOT NULL COMMENT '用户ID（分片键）',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    age INT COMMENT '年龄',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 分表 2：user_2
CREATE TABLE IF NOT EXISTS user_2 (
    id BIGINT NOT NULL COMMENT '主键ID',
    user_id BIGINT NOT NULL COMMENT '用户ID（分片键）',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    age INT COMMENT '年龄',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
三、核心配置（YAML 方式，推荐）
在 src/main/resources 下创建 application-sharding.yml（分片配置文件），通过配置定义数据源、分片规则。
配置说明（单库分表）
yaml
spring:
  # 激活分片配置文件（也可直接写在 application.yml 中）
  profiles:
    active: sharding
  # Sharding-JDBC 核心配置
  shardingsphere:
    # 数据源配置（被分片的数据库）
    datasource:
      # 数据源名称（自定义，可多个，示例用 1 个）
      names: db0
      # 数据源 0 配置
      db0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        url: jdbc:mysql://localhost:3306/sharding_db?useSSL=false&serverTimezone=Asia/Shanghai
        username: root
        password: 123456
    # 分片规则配置
    rules:
      sharding:
        # 表分片规则（key：逻辑表名，value：分片配置）
        tables:
          # 逻辑表名（业务中使用的表名，对应真实分表 user_1、user_2）
          user:
            # 真实表名表达式（${0..1} 表示 0 和 1，对应 user_1、user_2）
            actual-data-nodes: db0.user_${1..2}
            # 分表策略（按分片键分片）
            table-strategy:
              # 分片算法类型：INLINE（行表达式，简单场景用）
              standard:
                # 分片键（必须是表中存在的字段）
                sharding-column: user_id
                # 分片算法名称（需与下方 algorithms 中定义的一致）
                sharding-algorithm-name: user_table_inline
            # 主键生成策略（避免分表主键冲突，用雪花算法）
            key-generate-strategy:
              column: id
              key-generator-name: snowflake
        # 分片算法配置（全局复用）
        algorithms:
          # 分表算法（名称：user_table_inline）
          user_table_inline:
            type: INLINE
            props:
              # 行表达式：user_id % 2 + 1 → 结果为 1 或 2，对应 user_1、user_2
              algorithm-expression: user_${user_id % 2 + 1}
        # 主键生成算法（雪花算法）
        key-generators:
          snowflake:
            type: SNOWFLAKE
            props:
              worker-id: 123  # 工作节点ID（集群环境需唯一，单机可随意）
    # 运行模式（开发环境用 MEMORY，生产用 Cluster）
    mode:
      type: MEMORY
    # 日志配置（打印 SQL 路由日志，方便调试）
    props:
      sql-show: true
多库分表扩展配置（可选）
如果需要分库 + 分表（如 2 个库，每个库 2 张表），只需修改：
新增数据源 db1；
调整 actual-data-nodes 为多库表达式；
新增分库策略。
示例片段：
yaml
spring:
  shardingsphere:
    datasource:
      names: db0,db1  # 2 个数据源
      db0:  # 库 0：sharding_db0
        url: jdbc:mysql://localhost:3306/sharding_db0?xxx
      db1:  # 库 1：sharding_db1
        url: jdbc:mysql://localhost:3306/sharding_db1?xxx
    rules:
      sharding:
        tables:
          user:
            # 多库分表：db0.user_1、db0.user_2、db1.user_1、db1.user_2
            actual-data-nodes: db${0..1}.user_${1..2}
            # 分库策略（先分库，再分表）
            database-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: user_db_inline
            # 分表策略（同单库）
            table-strategy: ...
        algorithms:
          # 分库算法（user_id % 2 → 0 或 1，对应 db0、db1）
          user_db_inline:
            type: INLINE
            props:
              algorithm-expression: db${user_id % 2}
          # 分表算法（同单库）
          user_table_inline: ...
四、代码开发（无侵入，与普通 CRUD 一致）
Sharding-JDBC 对业务代码无侵入，DAO 层、Service 层开发与普通单表完全一致。
1. 实体类（Entity）
java
运行
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("user")  // 对应逻辑表名（非真实分表名）
public class User {
    private Long id;         // 主键（雪花算法生成）
    private Long userId;     // 分片键（分表/分库依据）
    private String username; // 用户名
    private Integer age;     // 年龄
}
2. Mapper 接口（MyBatis-Plus）
java
运行
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.springframework.stereotype.Repository;

@Repository
public interface UserMapper extends BaseMapper<User> {
    // 无需手动写 SQL，BaseMapper 已提供 CRUD 方法（insert、selectById、list 等）
}
3. 启动类（添加 Mapper 扫描）
java
运行
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.example.sharding.mapper") // 扫描 Mapper 接口包
public class ShardingJdbcDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(ShardingJdbcDemoApplication.class, args);
    }
}
五、测试验证
编写测试类，验证分表是否生效（数据按 user_id 拆分到 user_1 和 user_2）。
1. 测试代码
java
运行
import com.example.sharding.mapper.UserMapper;
import com.example.sharding.entity.User;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;

@SpringBootTest
public class ShardingJdbcTest {

    @Resource
    private UserMapper userMapper;

    // 测试插入数据（验证分表规则）
    @Test
    public void testInsert() {
        List<User> userList = new ArrayList<>();
        // 插入 4 条数据，user_id 分别为 1001（1001%2+1=2 → user_2）、1002（1002%2+1=1 → user_1）
        userList.add(buildUser(1001L, "张三", 20));
        userList.add(buildUser(1002L, "李四", 22));
        userList.add(buildUser(1003L, "王五", 25)); // 1003%2+1=2 → user_2
        userList.add(buildUser(1004L, "赵六", 28)); // 1004%2+1=1 → user_1

        // 批量插入（Sharding-JDBC 自动路由到对应分表）
        userMapper.insertBatchSomeColumn(userList);
    }

    // 测试查询数据（验证路由和聚合）
    @Test
    public void testSelect() {
        // 1. 按分片键查询（精准路由到单表）
        User user = userMapper.selectOne(new QueryWrapper<User>().eq("user_id", 1001L));
        System.out.println("精准查询结果：" + user);

        // 2. 全表查询（Sharding-JDBC 自动聚合所有分表数据）
        List<User> userList = userMapper.selectList(null);
        System.out.println("全表查询总条数：" + userList.size());
    }

    // 构建 User 对象
    private User buildUser(Long userId, String username, Integer age) {
        User user = new User();
        user.setUserId(userId);
        user.setUsername(username);
        user.setAge(age);
        return user;
    }
}
2. 验证结果
插入验证：
执行 testInsert() 后，查看 MySQL 数据库：
user_1 包含 user_id=1002、1004 的数据；
user_2 包含 user_id=1001、1003 的数据；
控制台打印 SQL 路由日志（sql-show: true 生效），可见插入语句自动路由到对应分表。
查询验证：
精准查询（按 user_id=1001）：SQL 路由到 user_2，直接返回结果；
全表查询：Sharding-JDBC 自动查询 user_1 和 user_2，聚合结果返回（总条数 4）。
六、关键扩展场景
1. 分片算法类型（除了 INLINE）
STANDARD：标准算法（支持精确查询、范围查询，需实现 PreciseShardingAlgorithm 接口）；
COMPLEX：复合分片（多字段分片，需实现 ComplexKeysShardingAlgorithm）；
HINT：强制路由（不通过分片键，手动指定路由库 / 表，适合管理后台操作）。
示例：自定义标准分片算法（Java 代码）
java
运行
import org.apache.shardingsphere.sharding.api.sharding.standard.PreciseShardingAlgorithm;
import org.apache.shardingsphere.sharding.api.sharding.standard.PreciseShardingValue;
import java.util.Collection;

// 按 user_id 范围分片（1-1000 → user_1，1001-2000 → user_2）
public class UserTableStandardAlgorithm implements PreciseShardingAlgorithm<Long> {

    @Override
    public String doSharding(Collection<String> availableTargetNames, PreciseShardingValue<Long> shardingValue) {
        Long userId = shardingValue.getValue();
        // 路由逻辑
        if (userId <= 1000) {
            return "user_1";
        } else {
            return "user_2";
        }
    }
}
然后在 YAML 中配置算法：
yaml
spring:
  shardingsphere:
    rules:
      sharding:
        algorithms:
          user_table_standard:
            type: STANDARD
            props:
              strategy: CLASS_BASED
              algorithm-class-name: com.example.sharding.algorithm.UserTableStandardAlgorithm
2. 读写分离（结合分库分表）
Sharding-JDBC 支持读写分离，只需在数据源配置中添加主从库，再配置读写分离规则：
yaml
spring:
  shardingsphere:
    datasource:
      names: master,slave1,slave2  # 主库 + 从库
      master: # 主库（写操作）
        url: jdbc:mysql://localhost:3306/sharding_db_master
      slave1: # 从库1（读操作）
        url: jdbc:mysql://localhost:3306/sharding_db_slave1
      slave2: # 从库2（读操作）
        url: jdbc:mysql://localhost:3306/sharding_db_slave2
    rules:
      readwrite-splitting: # 读写分离规则
        data-sources:
          master-slave-group: # 读写分离组名称
            type: Static
            props:
              write-data-source-name: master  # 写库
              read-data-source-names: slave1,slave2  # 读库列表
              load-balancer-name: round_robin  # 负载均衡算法（轮询）
      sharding: # 分库分表规则（同前，关联读写分离组）
        tables:
          user:
            actual-data-nodes: master-slave-group.user_${1..2}  # 关联读写分离组
七、注意事项
分片键选择：优先选择查询频繁、分布均匀的字段（如 user_id、order_id），避免范围查询导致全表扫描；
主键冲突：分表后主键需全局唯一，推荐用雪花算法（Sharding-JDBC 内置）或 UUID；
事务支持：Sharding-JDBC 支持本地事务（单库事务），跨库事务需结合 Seata 等分布式事务框架；
索引优化：分表字段建议加索引，避免跨表查询时全表扫描；
版本兼容：Sharding-JDBC 5.x 与 Spring Boot 2.7.x 兼容，3.x 需用 Spring Boot 3.x。
总结
Sharding-JDBC 的核心优势是轻量、无侵入、配置灵活，使用步骤可归纳为：
引入依赖 → 2. 创建分库分表 → 3. 配置分片规则（数据源、分片键、算法）→ 4. 正常开发 CRUD 代码 → 5. 测试验证。
如果需要更复杂的场景（如动态分片、加密传输、影子表），可参考 ShardingSphere 官方文档。