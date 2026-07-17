---
name: wip-case-snapshot
description: Flow 01 的结构化 WIP Case Snapshot 生成模块。基于 case_data_snapshot 和可配置字段清单生成 Case Header 与风险快照容器。
---

# WIP Case Snapshot

本模块只在 Flow 01 启动时使用。它直接生成 `WIP Case Snapshot` 容器，Flow 01 原样嵌入最终 `content.containers[0]`。

- SQL 事实只来自 `case_data_snapshot.sql_results`。
- 字段、标签与模板只由 [字段配置](output-contracts/snapshot-display-schema.md) 控制。
- 模块的完整输入、输出和字段来源规则见 [快照契约](output-contracts/snapshot-input-contract.md)。
- 未达到 WIP Bubble 条件时不生成快照容器，Flow 01 输出轻量关闭结果。
- Flow 02 及以后只读取 Flow 01 已保存的快照，不重新调用本模块。

## 无文件执行约束

运行时不创建临时文件、请求文件或下载产物；只在内存中返回结构化结果。
