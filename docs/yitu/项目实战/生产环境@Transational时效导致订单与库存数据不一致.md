---
title: 生产环境@Transational时效导致订单与库存数据不一致
---

# 🚨 生产环境异常排查案例：@Transactional 失效导致订单与库存数据不一致
## 一、故障现象 📊
- 核心问题：电商平台「下单减库存」功能异常，用户下单后 **订单创建成功，但库存未扣减**。
- 衍生问题：库存为0时仍能下单，出现“超卖”现象，影响数据一致性。
- 影响范围：高频出现，虽未造成重大损失，但破坏业务规则，需快速修复。

## 二、环境背景 🛠️
- 技术栈：Spring Boot 2.5 + MySQL 8.0（InnoDB引擎，支持事务）
- 核心流程：用户下单 → 创建订单记录 → 扣减商品库存（期望原子执行）
- 事务控制：使用 `@Transactional` 注解标注下单方法，预期“任一操作失败则整体回滚”。

## 三、排查过程 🔍
### 1. 查看日志，定位异常
- 日志关键信息：
[2025-09-01 14:30:22.456] ERROR 67890 --- [nio-8080-exec-9] c.e.shop.service.OrderService : 库存扣减失败：商品 ID=202，当前库存 = 0[2025-09-01 14:30:22.458] INFO 67890 --- [nio-8080-exec-9] c.e.shop.service.OrderService : 订单创建成功，订单号 = ORDER20250901143022
plaintext





- 初步判断：库存扣减失败（抛出异常），但订单未回滚 → `@Transactional` 事务失效。

### 2. 检查核心代码，发现配置漏洞
- 下单方法代码：
```java
@Service
public class OrderService {
    @Autowired
    private OrderMapper orderMapper;
    @Autowired
    private StockMapper stockMapper;

    // ❌ 未指定 rollbackFor 属性
    @Transactional
    public void createOrder(OrderDTO orderDTO) throws StockInsufficientException {
        // 1. 创建订单记录
        orderMapper.insert(orderDTO);
        // 2. 扣减库存（库存不足抛自定义异常）
        stockMapper.deductStock(orderDTO.getGoodsId(), orderDTO.getNum());
    }
}
```
### 3. 验证异常类型，确认根因

自定义异常定义（问题关键）： 

❌ 受检查异常（未继承 RuntimeException）
public class StockInsufficientException extends Exception {
    public StockInsufficientException(String message) {
        super(message);
    }
}


Spring 事务默认规则：仅对「RuntimeException 及其子类」触发回滚，受检查异常（extends Exception）不回滚 → 库存不足抛出的异常未被事务识别，导致订单创建操作正常提交。
## 四、根因总结 📌

事务注解配置缺失：@Transactional 未显式指定 rollbackFor，依赖默认回滚规则。

异常类型设计不当：自定义业务异常为受检查异常，未被 Spring 事务切面捕获。

最终结果：库存扣减失败抛出异常，但订单创建操作未回滚，导致订单与库存数据不一致。
五、修复方案 ✅

1. 修正事务注解，指定回滚异常
 
// ✅ 显式指定需回滚的异常，覆盖默认规则
```java
@Transactional(rollbackFor = {StockInsufficientException.class, Exception.class})
public void createOrder(OrderDTO orderDTO) throws StockInsufficientException {
    orderMapper.insert(orderDTO);
    stockMapper.deductStock(orderDTO.getGoodsId(), orderDTO.getNum());
}
```

2. 优化异常设计（可选）

将自定义异常改为未检查异常，无需显式声明抛出，兼容 Spring 默认回滚规则：

```
// ✅ 继承 RuntimeException（未检查异常）
public class StockInsufficientException extends RuntimeException {
    public StockInsufficientException(String message) {
        super(message);
    }
}
```

1. 验证与发布

本地测试：模拟库存不足场景，抛出异常后，订单创建操作被回滚，数据一致。

灰度发布：先灰度 10% 流量，观察 1 小时无异常后全量发布。

监控确认：订单与库存操作一致性恢复，无超卖现象。

## 六、经验教训 📚

🚫 禁用 @Transactional 裸注解：必须显式指定 rollbackFor = Exception.class，覆盖所有异常场景。

🎯 自定义异常推荐继承 RuntimeException：无需声明抛出，且能被 Spring 事务默认识别。

🧪 上线前必做异常测试：模拟业务异常场景，验证事务回滚是否生效。

⚠️ 复杂场景优先编程式事务：多数据源、动态规则等场景，用 TransactionTemplate 显式控制事务，降低 AOP 依赖导致的失效风险。


| 模块         | 详情                                                                 |
|--------------|----------------------------------------------------------------------|
| 📊 故障现象   | 下单后订单创建成功，库存未扣减，出现超卖，数据不一致                 |
| 🛠️ 环境背景   | Spring Boot 2.5 + MySQL 8.0（InnoDB），@Transactional 注解控制事务   |
| 🔍 排查关键1  | 日志显示库存扣减失败抛异常，但订单未回滚                            |
| 🔍 排查关键2  | @Transactional 未指定 rollbackFor（裸注解）                          |
| 🔍 排查关键3  | 自定义异常继承 Exception（受检查异常），Spring 默认不回滚            |
| 📌 根因总结   | 注解配置缺失+异常设计不当，事务未捕获异常导致失效                   |
| ✅ 修复方案1  | @Transactional(rollbackFor = {Exception.class}) 显式指定回滚异常     |
| ✅ 修复方案2  | 异常改为继承 RuntimeException（未检查异常）                          |
| ✅ 验证发布   | 本地测试→灰度10%流量→全量发布，监控无超卖                           |
| 📚 经验教训   | 禁用@Transactional裸注解，异常优先RuntimeException，上线必测回滚     |