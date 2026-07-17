# Flow 07 JSON Output Contract - 跨部门协同处置

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 06 case_id",
  "flow_no": "07",
  "flow_name": "跨部门协同处置",
  "flow_status": "Closed",
  "case_status": "Processing | On Hold",
  "next_flow_no": "08 或 null",
  "next_flow_name": "处置效果确认 或 null",
  "collaboration_package_status": "已生成跨部门协同处置建议",
  "text": "完整 Markdown",
  "content": {
    "title": "07 跨部门协同处置",
    "containers": [
      {"title": "WIP Case Snapshot", "sections": [
        {"title": "Case Header", "items": [{"label": "Case ID", "value": "..."}]},
        {"title": "Case Risk Snapshot｜异常发生时（风险快照）", "items": [{"label": "WIP", "value": "..."}]}
      ]},
      {"title": "当前阶段对话", "sections": [
        {"title": "系统 / 用户触发", "items": ["..."]},
        {"title": "Agent 接管", "items": ["..."]},
        {"title": "Agent 思考过程", "items": ["..."]},
        {"title": "Agent 分析计划", "items": ["..."]},
        {"title": "数据 / 工具调用", "items": [
          {"label": "Engineering Package", "value": "...", "status": "Done"},
          {"label": "Root Cause Candidate", "value": "...", "status": "Done"},
          {"label": "Task Breakdown", "value": "...", "status": "Done"},
          {"label": "Owner Assignment", "value": "...", "status": "Done"},
          {"label": "Collaboration SLA", "value": "...", "status": "Done"},
          {"label": "Recovery Metric", "value": "...", "status": "Done"},
          {"label": "Next Flow Gate", "value": "...", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Collaboration Package Status", "value": "已生成跨部门协同处置建议"}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 08 处置效果确认", "Gate: 角色完成初步反馈并定义恢复验证指标后进入处置效果确认"]},
        {"title": "关键证据", "items": ["..."]}
      ]}
    ]
  }
}
```

## 校验要求

- `content.containers` 恰好 3 个。
- `当前阶段对话.sections` 恰好 9 个。
- `当前阶段结果.sections` 恰好 5 个。
- `数据 / 工具调用.items` 必须包含业务事实和 `status=Done`，不能只有 Done。
- `数据 / 工具调用.items` 必须覆盖 Engineering Package、Root Cause Candidate、Task Breakdown、Owner Assignment、Collaboration SLA、Recovery Metric 和 Next Flow Gate。
- 禁止输出 `internal_payload`、`internal_render`、`model_context`、`case_snapshot`、`prompt`、`mock`。
- 禁止输出已真实派单、已通知、已完成处置、处置已生效、最终根因已确认或 Case 已关闭。
