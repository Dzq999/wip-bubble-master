---
name: wip-case-snapshot
description: WIP Bubble 总控 Skill 的 Case 快照内部模块。用于 Flow 01 异常触发时准备原始 SQL 与 mock 数据包，供当前 Agent 自行生成并保存 WIP Case Snapshot。
---

# WIP Case 快照内部模块

本模块只在 Flow 01 异常触发时由总控 Skill 调用，用来准备 `fab-agent-demo` 红框区域需要的原始数据输入。它不生成用户可读文本，也不拼接最终展示结构。

Flow 01 的 Agent 结果保存后，后续 Flow 应读取已保存的 `wip_case_snapshot`。其中 WIP、Queue、Tool Uptime、Q-Time 等风险指标是异常触发瞬间的历史快照；Case Age、Stage Elapsed、SLA Remaining 等动态字段可在打开界面时按当前时间刷新。Flow 02 及以后不要为了拿快照而重新执行本模块。


## 输出契约

本模块的原始输入包契约单独维护在：

```text
output-contracts/snapshot-input-contract.md
```

执行本模块或读取脚本输出时，当前 Agent 必须遵守该契约。`snapshot_inputs`、`source_data`、mock 数据边界以及与最终 `content` 中 `WIP Case Snapshot` 容器的关系，全部到该契约文件查看。

注意：`wip-case-snapshot` 的契约不是最终前端展示契约，而是原始数据包契约。最终展示结构由具体 Flow 的 `output-contracts/` 决定。
## 数据来源

- 数仓 SQL 原始行：例如 `stage_name`、`actual_wip`、`target_wip`、`queue_wip`、`queue_actual_ratio`、`wip_gap`、`wip_ratio`、`biz_time` 等。脚本只透传查询结果，不抽字段组织展示内容。
- mock JSON：demo 中暂时无法从数仓或自建表查询的数据，例如 Case Age、Flow Elapsed、SLA Remaining、Owner、Eligible Tool、Move-Out、Q-Time 等。Downstream / 下游 starvation 必须优先来自 SQL 查询 `locate_downstream_starvation.sql`，不要写入 mock 固定文本。
- Flow 专属 mock：放在各 Flow 自己的 `data` 目录，例如 Flow 01 使用 `internal/wip-flow-01-anomaly-detection/data/flow01_mock.json`。

mock 文件位置：

```text
internal/wip-case-snapshot/data/snapshot_mock.json
```

## 规则

- `case_id` 使用总控 Skill 每次 Flow 01 新建的 UUID。
- 本模块不计算 `bubble_status`，不拼接标题，不生成系统话术、门禁文案或前端容器内容。
- mock JSON 只存放数据，不存放固定展示标题、系统话术、门禁文案等可由当前 Agent 根据模板生成的文本。
- 如果 SQL 和 mock 都没有某字段，则当前 Agent 忽略该字段，不输出占位值。
- 如果后续有依赖 SQL 结果的计算任务，当前 Agent 先拿到 SQL 原始结果，再把所需数据显式传给计算脚本；计算脚本不自行查询 SQL。





