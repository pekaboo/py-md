---
title: Redis相关
description: Redis相关
---
# Redis相关

## Redis 数据类型与场景
- 常用五大类型：String、Hash、List、Set、ZSet 扩展类型：Bitmap、HyperLogLog、Geo、Stream。 
- **String**：二进制安全，可**存 JSON**、计数器。典型场景：**缓存对象、分布式锁、限流计数**。
- **Hash**：类似字典，适合存用户信息、配置项等结构化数据。
- **List**：双端链表，用于消息队列、任务队列（`LPUSH`/`BRPOP`）。
- **Set**：无序去重集合，用于标签、好友关系、抽奖。
- **ZSet**：有序集合，成员分数排序，适合排行榜、延迟队列。 
- **Bitmap**：位图，适合签到、活跃用户标记；1 bit 表示一个状态。
- **HyperLogLog**：估算基数，适合 UV 统计，误差约 0.81%。
- **Geo**：地理位置，查询附近地点。
- **Stream**：消息队列，支持消费组、可靠消费。
::: Warning ⚠️注意事项
- 选择数据结构时考虑内存占用与操作复杂度，避免误用 ZSet 做大宽表。
- Hash 内部字段过多会与 String 体积相差无几，需要设置 `hash-max-ziplist-entries/values`。
- Stream 需要定期 `XDEL`/`XTRIM` 避免无限增长。
:::