# Flow 02 JSON Output Contract - 异常确认

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 01 case_id",
  "flow_no": "02",
  "flow_name": "异常确认",
  "flow_status": "Closed",
  "case_status": "Processing | Closed | On Hold",
  "next_flow_no": "03 或 null",
  "next_flow_name": "临时措施 或 null",
  "confirmation_status": "异常确认成立",
  "text": "完整 Markdown",
  "content": {
    "title": "02 异常确认",
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
          {"label": "Data Freshness Check", "value": "数据刷新正常", "status": "Done"},
          {"label": "Metric Scope Check", "value": "Stage WIP", "status": "Done"},
          {"label": "Target WIP Query", "value": "Target WIP = ...，有效", "status": "Done"},
          {"label": "Open Case Search", "value": "无重复 Case", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Confirmation Status", "value": "异常确认成立"}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 03 临时措施", "Gate: MFG / Shift 确认异常成立"]},
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
- 禁止输出 `frontend_payload`、`frontend_demo`、`model_context`、`case_snapshot`、`prompt`、`mock`。
