# Flow 05 JSON Output Contract - Case 分级与处置判定

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 04 case_id",
  "flow_no": "05",
  "flow_name": "Case 分级与处置判定",
  "flow_status": "Closed",
  "case_status": "Processing | On Hold",
  "next_flow_no": "06 或 null",
  "next_flow_name": "异常原因排查 或 null",
  "case_classification_status": "已完成分级与处置判定",
  "text": "完整 Markdown",
  "content": {
    "title": "05 Case 分级与处置判定",
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
          {"label": "Impact Severity", "value": "...", "status": "Done"},
          {"label": "Case Level", "value": "...", "status": "Done"},
          {"label": "Disposition Path", "value": "...", "status": "Done"},
          {"label": "Owner Assignment", "value": "...", "status": "Done"},
          {"label": "Next Flow Gate", "value": "...", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Case Classification Status", "value": "已完成分级与处置判定"}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 06 异常原因排查", "Gate: Case Owner 确认分级与处置路径后进入原因排查"]},
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
- `数据 / 工具调用.items` 必须覆盖 `Impact Severity`、`Case Level`、`Disposition Path`、`Owner Assignment` 和 `Next Flow Gate`。
- 禁止输出 `internal_payload`、`internal_render`、`model_context`、`case_snapshot`、`prompt`、`mock`。
- 禁止输出最终根因、原因候选排序、工程问题包已派发或任务已派发结论。
