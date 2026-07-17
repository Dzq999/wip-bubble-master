# Flow 08 JSON Output Contract - 处置效果确认

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 07 case_id",
  "flow_no": "08",
  "flow_name": "处置效果确认",
  "flow_status": "Closed",
  "case_status": "Processing | On Hold",
  "next_flow_no": "09 或 null",
  "next_flow_name": "影响消除观察 或 null",
  "effect_confirmation_status": "初步有效 | 部分有效 | 证据不足 | 需回退/升级",
  "text": "完整 Markdown",
  "content": {
    "title": "08 处置效果确认",
    "containers": [
      {"title": "WIP Case Snapshot", "sections": [
        {"title": "Case Header", "items": [{"label": "Case ID", "value": "..."}]},
        {"title": "Case Risk Trend｜处置后（恢复趋势）", "items": [{"label": "Actual WIP", "value": "8,050 -> 248 / Target 258", "meta": {"from": "8,050", "to": "248", "target": "258", "status": "Recovered", "tone": "down", "mocked": true}}]}
      ]},
      {"title": "当前阶段对话", "sections": [
        {"title": "系统 / 用户触发", "items": ["..."]},
        {"title": "Agent 接管", "items": ["..."]},
        {"title": "Agent 思考过程", "items": ["..."]},
        {"title": "Agent 分析计划", "items": ["..."]},
        {"title": "数据 / 工具调用", "items": [
          {"label": "Action Feedback Check", "value": "...", "status": "Done"},
          {"label": "SLA Check", "value": "...", "status": "Done"},
          {"label": "Recovery Metric Check", "value": "...", "status": "Done"},
          {"label": "WIP / Queue Trend", "value": "...", "status": "Done"},
          {"label": "Downstream Risk Check", "value": "...", "status": "Done"},
          {"label": "Rollback / Escalation Decision", "value": "...", "status": "Done"},
          {"label": "Next Flow Gate", "value": "...", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Effect Confirmation Status", "value": "..."}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 09 影响消除观察 / On Hold", "Gate: 初步效果证据充分后进入影响消除观察"]},
        {"title": "关键证据", "items": ["..."]}
      ]}
    ]
  }
}
```

## 校验要求

- `content.containers` 恰好 3 个。
- `WIP Case Snapshot.sections` 恰好 2 个，第二个必须是 `Case Risk Trend｜处置后（恢复趋势）`；Flow 08 不输出 `Case Risk Snapshot｜异常发生时（风险快照）`。
- `当前阶段对话.sections` 恰好 9 个。
- `当前阶段结果.sections` 恰好 5 个。
- `数据 / 工具调用.items` 必须包含业务事实和 `status=Done`，不能只有 Done。
- `数据 / 工具调用.items` 必须覆盖 Action Feedback Check、SLA Check、Recovery Metric Check、WIP / Queue Trend、Downstream Risk Check、Rollback / Escalation Decision 和 Next Flow Gate。
- 禁止输出 `internal_payload`、`internal_render`、`model_context`、`case_snapshot`、`prompt`、`mock`。
- `Case Risk Trend｜处置后（恢复趋势）.items` 必须使用 `{label,value,meta}`，`value` 展示 `异常值 -> 正常值`，`meta` 包含 `from/to/status/tone/mocked`。
- 禁止输出异常已完全恢复、Case 可关闭、已完成复盘、已完成处置或处置已生效。
