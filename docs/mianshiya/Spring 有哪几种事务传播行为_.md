# Spring 有哪几种事务传播行为?

**难度**：中等

**创建时间**：2025-10-06 05:57:31

## 答案
Spring 框架通过 `@Transactional` 注解的 `propagation` 属性支持多种事务传播行为（Transaction Propagation），用于控制方法在调用时的**事务边界**和**交互方式**。以下是 Spring 提供的 7 种事务传播行为及其适用场景：

---

### **1. REQUIRED（默认行为）**
- **行为**：如果当前存在事务，则加入该事务；如果不存在，则新建一个事务。
- **适用场景**：大多数业务方法，需要保证操作的原子性。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.REQUIRED)
  public void updateOrder(Order order) {
      // 操作订单
  }
  ```
  - 如果调用 `updateOrder()` 时外部已有事务（如另一个 `@Transactional` 方法调用它），则加入该事务。
  - 如果直接调用（无外部事务），则新建一个事务。

---

### **2. SUPPORTS**
- **行为**：如果当前存在事务，则加入该事务；如果不存在，则以非事务方式执行。
- **适用场景**：读操作或允许非事务执行的场景（如查询日志）。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.SUPPORTS)
  public List<Order> getOrders() {
      // 查询订单（不强制事务）
  }
  ```
  - 如果外部有事务，则加入；否则无事务。

---

### **3. MANDATORY**
- **行为**：必须在一个已有的事务中执行，否则抛出异常（`IllegalTransactionStateException`）。
- **适用场景**：强制依赖外部事务的方法（如嵌套服务调用）。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.MANDATORY)
  public void validateOrder(Order order) {
      // 必须在外层事务中调用
  }
  ```
  - 如果直接调用（无外部事务），抛出异常。

---

### **4. REQUIRES_NEW**
- **行为**：总是新建一个事务，如果当前存在事务，则挂起（Suspend）当前事务。
- **适用场景**：需要独立事务的方法（如日志记录、审计）。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.REQUIRES_NEW)
  public void logOperation(String message) {
      // 独立事务，不受外层事务影响
  }
  ```
  - 外层事务回滚时，`logOperation()` 的事务仍会提交。
  - 适用于需要确保操作一定执行的场景（如支付成功后记录日志）。

---

### **5. NOT_SUPPORTED**
- **行为**：以非事务方式执行，如果当前存在事务，则挂起当前事务。
- **适用场景**：明确不需要事务的方法（如批量导出数据）。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.NOT_SUPPORTED)
  public void exportData() {
      // 非事务执行
  }
  ```
  - 如果外层有事务，执行时会挂起事务，方法执行完毕后再恢复。

---

### **6. NEVER**
- **行为**：以非事务方式执行，如果当前存在事务，则抛出异常。
- **适用场景**：强制要求无事务的方法（如纯读操作）。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.NEVER)
  public void readConfig() {
      // 必须无事务
  }
  ```
  - 如果外层有事务，调用时抛出异常。

---

### **7. NESTED**
- **行为**：如果当前存在事务，则在嵌套事务中执行（保存点回滚）；如果不存在，则新建事务。
- **适用场景**：需要部分回滚的场景（如大事务中分阶段提交）。
- **示例**：
  ```java
  @Transactional(propagation = Propagation.NESTED)
  public void updateInventory(Item item) {
      // 嵌套事务，可独立回滚
  }
  ```
  - 外层事务回滚时，嵌套事务也会回滚。
  - 嵌套事务回滚时，不影响外层事务（通过保存点实现）。
  - **注意**：仅部分数据库（如 MySQL 的 InnoDB）支持保存点。

---

### **传播行为对比表**
| 传播行为          | 当前有事务时                     | 当前无事务时                     | 典型场景                     |
|-------------------|----------------------------------|----------------------------------|------------------------------|
| REQUIRED          | 加入事务                         | 新建事务                         | 默认行为，大多数业务方法     |
| SUPPORTS          | 加入事务                         | 非事务执行                       | 读操作                       |
| MANDATORY         | 加入事务                         | 抛出异常                         | 强制依赖外部事务             |
| REQUIRES_NEW      | 挂起当前事务，新建事务           | 新建事务                         | 独立事务（如日志）           |
| NOT_SUPPORTED     | 挂起当前事务，非事务执行         | 非事务执行                       | 明确不需要事务               |
| NEVER             | 抛出异常                         | 非事务执行                       | 强制无事务                   |
| NESTED            | 嵌套事务（保存点）               | 新建事务                         | 部分回滚的大事务             |

---

### **使用示例**
#### **1. 默认 REQUIRED（推荐）**
```java
@Service
public class OrderService {
    @Transactional
    public void placeOrder(Order order) {
        // 插入订单（REQUIRED）
        orderDao.insert(order);
        // 调用其他方法（自动加入同一事务）
        paymentService.processPayment(order);
    }
}
```

#### **2. REQUIRES_NEW（独立事务）**
```java
@Service
public class PaymentService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processPayment(Order order) {
        // 支付操作（独立事务）
        paymentDao.update(order);
        // 即使外层回滚，此方法仍会提交
    }
}
```

#### **3. NESTED（嵌套事务）**
```java
@Service
public class InventoryService {
    @Transactional
    public void updateStock(Item item, int quantity) {
        // 外层事务
        inventoryDao.reserve(item, quantity);
        try {
            auditService.logChange(item, quantity); // 可能失败
        } catch (Exception e) {
            // 仅回滚 auditService 的操作（NESTED）
            throw e;
        }
    }
}

@Service
public class AuditService {
    @Transactional(propagation = Propagation.NESTED)
    public void logChange(Item item, int quantity) {
        // 嵌套事务操作
        auditDao.insert(item, quantity);
    }
}
```

---

### **注意事项**
1. **默认行为**：`@Transactional` 不指定 `propagation` 时默认为 `REQUIRED`。
2. **性能影响**：`REQUIRES_NEW` 和 `NESTED` 会增加数据库连接开销（需额外事务）。
3. **数据库支持**：`NESTED` 依赖数据库的保存点功能（如 MySQL 的 InnoDB 支持，但 MyISAM 不支持）。
4. **异常处理**：默认仅对 `RuntimeException` 回滚，可通过 `@Transactional(rollbackFor = Exception.class)` 修改。

---

### **总结**
- **常用场景**：
  - 默认用 `REQUIRED`（90% 场景）。
  - 独立事务用 `REQUIRES_NEW`（如日志、审计）。
  - 部分回滚用 `NESTED`（需数据库支持）。
- **避免滥用**：过多的事务嵌套可能导致性能下降或意外回滚。

理解事务传播行为有助于设计更合理的事务边界，平衡数据一致性与系统性能。
