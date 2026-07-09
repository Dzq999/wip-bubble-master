# Flow 03 JSON Output Contract - 临时措施

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 02 case_id",
  "flow_no": "03",
  "flow_name": "临时措施",
  "flow_status": "Closed",
  "case_status": "Processing | On Hold",
  "next_flow_no": "04 或 null",
  "next_flow_name": "影响范围评估 或 null",
  "containment_status": "临时措施已生成",
  "text": "完整 Markdown",
  "content": {
    "title": "03 临时措施",
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
          {"label": "Hot Lot Query", "value": "Hot Lot = ...，Super Hot Run = ...", "status": "Done"},
          {"label": "Move-In Check", "value": "建议限制非关键 Product / Lot", "status": "Done"},
          {"label": "Downstream Risk Check", "value": "...", "status": "Done"},
          {"label": "Hold Recommendation", "value": "不建议全量 Hold", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Containment Status", "value": "临时措施已生成"}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 04 影响范围评估", "Gate: 确认临时措施已执行并进入影响范围评估"]},
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
- `Downstream Risk Check.value` 必须使用前序 `Downstream / Next Stage` 实际值；如果前序为 `PW-PH`，不得输出其他泛化对象。
- 禁止输出 `frontend_payload`、`frontend_demo`、`model_context`、`case_snapshot`、`prompt`、`mock`。
