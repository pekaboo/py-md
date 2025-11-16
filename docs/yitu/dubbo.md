---
title: Dubbo相关
description: Dubbo相关
---
# Dubbo相关

## 11. Dubbo 调用原理

### 要点速览 · 11

- 注册中心（Zookeeper、Nacos）服务注册发现。
- 消费端基于动态代理、负载均衡、集群容错。
- 序列化、网络协议支持可插拔。

### 基础要点 · 11

- Provider 启动后暴露服务，注册到注册中心；Consumer 订阅服务列表。
- 消费方调用代理→Invoker→Protocol→Client（如 Netty）。

### 进阶扩展 · 11

- **协议**：Dubbo 协议（TCP + Hessian2），支持多协议（gRPC、REST）。
- **负载均衡**：随机、轮询、一致性哈希、最少活跃。
- **容错策略**：Failover、Failfast、Failsafe、Failback、Forking。
- **SPI**：Dubbo 扩展机制，基于自定义 ClassLoader 与包装类。

### ⚠️注意事项 · 11

- 注册中心不可用时，Consumer 使用本地缓存；确保缓存刷新策略。
- 版本、分组隔离避免接口冲突。
- 监控（Dubbo Admin、Metrics）对容量治理至关重要。