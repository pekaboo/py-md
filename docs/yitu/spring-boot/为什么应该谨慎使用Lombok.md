---
title: 为什么应该谨慎使用Lombok
date: 2025-06-11 10:38:00
tags:
---
### 📝 面试总结：为何谨慎使用 Lombok？
#### 1. ✅ Lombok 核心优势
- 通过 `@Data`、`@Getter/@Setter` 等注解自动生成模板代码，精简 POJO 类，减少冗余。
- 支持多种构建工具（Maven/Gradle）和 IDE，集成成本低，开发效率高。

#### 2. ❌ 谨慎使用的核心原因
- 🤝 强依赖队友：需所有开发者安装 IDE 插件，依赖其 Jar 包的项目也需安装，侵入性强。
- 📖 可读性/调试性差：编译时才生成代码，开发阶段缺失 getter/setter 等，无法直接查看引用关系。
- 🕳️ 注解使用易踩坑：`@Data` 默认 `callSuper=false`，`equals()` 不比较父类属性；过度依赖易忽略注解底层逻辑。
- 🚀 影响版本升级：JDK 迭代速度快，Lombok 开源维护迭代滞后，可能不支持新 JDK 特性；多 Jar 包依赖易引发版本冲突。
- 🔒 破坏封装性：`@Data` 自动生成所有属性的 getter/setter，暴露不必要的修改接口，违反面向对象封装原则（如购物车类属性关联关系易被破坏）。

#### 3. 🆕 替代方案：JDK 14+ Records
- 官方原生支持，无需第三方依赖，语法紧凑：`record Person(String firstName, String lastName) {}`。
- 自动生成构造器、`equals()`、`hashCode()`、`toString()` 及属性访问方法，且属性默认不可变（`final`）。
- 遵循封装原则，专注纯数据载体场景，无 Lombok 带来的侵入性和版本兼容问题。

#### 4. 📌 最终建议
- 不禁止但不建议过度依赖 Lombok，使用前需理解注解底层逻辑。
- 简单纯数据载体场景，优先使用 JDK 14+ Records 替代 Lombok。
- 团队协作需统一规范，明确是否使用 Lombok，避免依赖冲突和协作成本。