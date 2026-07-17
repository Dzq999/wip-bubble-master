# Flow 06 JSON Output Contract - 异常原因排查

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 05 case_id",
  "flow_no": "06",
  "flow_name": "异常原因排查",
  "flow_status": "Closed",
  "case_status": "Processing | On Hold",
  "next_flow_no": "07 或 null",
  "next_flow_name": "跨部门协同处置 或 null",
  "root_cause_analysis_status": "已完成候选原因排查",
  "text": "完整 Markdown",
  "content": {
    "title": "06 异常原因排查",
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
          {"label": "WIP State Check", "value": "...", "status": "Done"},
          {"label": "Tool Status Check", "value": "...", "status": "Done"},
          {"label": "Tool Efficiency Check", "value": "...", "status": "Done"},
          {"label": "Move-In Trend", "value": "...", "status": "Done"},
          {"label": "Move-Out Trend", "value": "...", "status": "Done"},
          {"label": "Root Cause Candidate", "value": "...", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Root Cause Analysis Status", "value": "已完成候选原因排查"}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 07 跨部门协同处置", "Gate: 工程师确认候选原因和补证项后进入跨部门协同处置"]},
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
- `数据 / 工具调用.items` 必须覆盖 WIP State Check、Tool Status Check、Tool Efficiency Check、Move-In Trend、Move-Out Trend 和 Root Cause Candidate。
- 禁止输出 `internal_payload`、`internal_render`、`model_context`、`case_snapshot`、`prompt`、`mock`。
- 禁止输出最终根因已确认、责任已锁定、Case 已关闭原因或工程任务已派发结论。
