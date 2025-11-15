---
title: 欢迎使用 md2html爱上大大
description: 核心特性与语法示例
---

## 欢迎使用 md2html

md2html 支持 GitHub 风格主题、目录生成与自定义容器扩展。

## 折叠示例

::: hide 更多细节
折叠区域中的内容默认隐藏，点击标题后展开。
:::

## 提示示例

::: note 使用指南
通过 `python -m md2html --src docs --dst build/html` 即可将 Markdown 批量转换为 HTML。
:::

## 警告示例

::: warning 注意事项

- 确保 `docs/` 下文件编码为 UTF-8。
- 调整主题时可在 `theme/` 目录下扩展。
:::

## 代码示例

```python
from md2html.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```
