# WIP Case Snapshot 字段配置

此文件控制 Flow 01 的 `WIP Case Snapshot` 容器。增删字段对象即可调整显示字段；修改 `label`、`value_template`、`meta_template` 可调整标签和文案。

字段来源：

- `runtime`：当前 Case 与 Flow 信息。
- `sql.high_wip`：`case_data_snapshot.sql_results.locate_high_wip_stage`。
- `sql.downstream`：`case_data_snapshot.sql_results.locate_downstream_starvation`。
- `snapshot`：`snapshot_mock.json` 中实际存在的字段。
- `derived`：由同一份 SQL 快照按 Flow 01 阈值规则计算的状态字段。

模板中的 `${字段路径}` 会替换为来源值；`${字段路径|percent}` 会按百分比展示。任一模板依赖字段不存在时，该字段自动省略。

```json
{
  "case_header": [
    {"label": "Case ID", "value_template": "${runtime.case_id}"},
    {"label": "Priority", "value_template": "${derived.priority}"},
    {"label": "Object", "value_template": "${sql.high_wip.stage_name} Stage"},
    {"label": "Case Type", "value_template": "${derived.bubble_status}"},
    {"label": "Occur Time", "value_template": "${sql.high_wip.update_time}"},
    {"label": "Operator", "value_template": "${snapshot.operator}"},
    {"label": "Current Stage", "value_template": "${runtime.flow_no} ${runtime.flow_name}"},
    {"label": "Case Age", "value_template": "${snapshot.case_age}"},
    {"label": "Stage Elapsed", "value_template": "${snapshot.stage_elapsed}"},
    {"label": "SLA Remaining", "value_template": "${snapshot.sla_remaining}"},
    {"label": "Owner", "value_template": "${snapshot.owner}"},
    {"label": "Status", "value_template": "${derived.case_status}"}
  ],
  "risk_snapshot": [
    {
      "label": "WIP",
      "value_template": "Actual ${sql.high_wip.actual_wip} / Target ${sql.high_wip.target_wip}",
      "meta_template": "Gap ${sql.high_wip.wip_gap}; Actual / Target = ${sql.high_wip.wip_ratio}"
    },
    {
      "label": "Queue",
      "value_template": "${sql.high_wip.queue_wip}",
      "meta_template": "占 Actual WIP ${sql.high_wip.queue_actual_ratio|percent}"
    },
    {"label": "Eligible Tool", "value_template": "${snapshot.risk_snapshot.eligible_tool.value}", "meta_template": "${snapshot.risk_snapshot.eligible_tool.meta}"},
    {"label": "Move-Out", "value_template": "${snapshot.risk_snapshot.move_out.value}", "meta_template": "${snapshot.risk_snapshot.move_out.meta}"},
    {"label": "Q-Time", "value_template": "${snapshot.risk_snapshot.q_time.value}", "meta_template": "${snapshot.risk_snapshot.q_time.meta}"},
    {
      "label": "Downstream",
      "value_template": "Next Stage = ${sql.downstream.next_stage_name}",
      "meta_template": "Status = ${sql.downstream.if_starved}"
    }
  ]
}
```
