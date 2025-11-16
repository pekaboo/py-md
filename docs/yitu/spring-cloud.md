---
title: Springcloud相关
description: Springcloud相关
---
# Springcloud相关



## 10. OpenFeign 远程调用原理

### 要点速览 · 10

- 基于动态代理生成 HTTP 客户端。
- 与 Ribbon/LoadBalancer、Hystrix/Resilience4j 集成。
- 支持契约与编码器/解码器扩展。

### 基础要点 · 10

- 接口上标注 `@FeignClient`，Spring 在启动时创建代理。
- 代理调用时构造请求：解析注解→拼装 URL→执行 `Client`（默认基于 Apache HttpClient 或 OkHttp）。

### 进阶扩展 · 10

- `FeignClientsRegistrar` 注册 BeanDefinition，`FeignClientFactoryBean` 创建代理。
- `Contract` 解析注解为 `MethodMetadata`，`Encoder/Decoder` 转换请求响应。
- 与 Spring Cloud LoadBalancer 集成实现客户端负载均衡，结合拦截器做统一鉴权、日志。

### ⚠️注意事项 · 10

- 接口方法返回类型要与 Decoder 匹配，避免 `ClassCastException`。
- 默认超时较长，需结合业务设置 `ReadTimeout/ConnectTimeout`。
- 大量并发调用需关注连接池与线程池配置。