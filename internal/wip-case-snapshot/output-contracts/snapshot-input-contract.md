# WIP Case Snapshot Contract

## 职责

`wip-case-snapshot` 在 Flow 01 启动时，直接从 `case_data_snapshot` 生成结构化 `WIP Case Snapshot` 容器。它不连接数据库、不生成当前阶段对话或当前阶段结果。

## 输入与输出

输入事实只来自：

- `case_data_snapshot.sql_results.locate_high_wip_stage`
- `case_data_snapshot.sql_results.locate_downstream_starvation`
- `data/snapshot_mock.json` 中实际存在的补充字段

输出结构：

```json
{
  "case_id": "...",
  "flow": {"flow_no": "01", "flow_name": "异常发现"},
  "bubble_status": "WIP Bubble",
  "case_status": "Processing",
  "next_flow_no": "02",
  "next_flow_name": "异常确认",
  "wip_case_snapshot": {
    "title": "WIP Case Snapshot",
    "sections": [
      {"title": "Case Header", "items": []},
      {"title": "Case Risk Snapshot｜异常发生时（风险快照）", "items": []}
    ]
  }
}
```

未达到 WIP Bubble 条件时，`wip_case_snapshot=null`，由 Flow 01 输出轻量关闭结果。

## 字段配置

[字段配置](snapshot-display-schema.md) 是唯一的快照字段清单。可直接在其中增删字段、修改标签、来源模板或百分比格式；脚本按配置生成 Header 和风险快照。

模板字段找不到来源时，整个字段自动省略。不得填写固定业务数值或结论。

## 关键映射

- `Occur Time` 只能取 `case_data_snapshot.sql_results.locate_high_wip_stage.update_time`。
- 不得使用 `biz_time`、当前时间、快照采集时间或补充数据时间替代。
- `update_time` 缺失时，`Occur Time` 自动省略。
- WIP、Queue、Q-Time、下游等风险字段均按字段配置从 SQL 或补充数据读取。

## Flow 01 使用规则

Flow 01 必须将非空的 `wip_case_snapshot` 原样作为 `content.containers[0]`，不得改写、补充或重排其中字段。后续 Flow 复用 Flow 01 已保存的该容器，不重新生成快照。
