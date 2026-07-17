# Flow 04 JSON Output Contract - 影响范围评估

最终 JSON 必须是完整 Flow 输出，不是摘要 JSON。必须包含 `text` 和 `content.containers`。

```json
{
  "ok": true,
  "case_id": "Flow 03 case_id",
  "flow_no": "04",
  "flow_name": "影响范围评估",
  "flow_status": "Closed",
  "case_status": "Processing | On Hold",
  "next_flow_no": "05 或 null",
  "next_flow_name": "Case 分级与处置判定 或 null",
  "impact_assessment_status": "影响范围已评估",
  "text": "完整 Markdown",
  "content": {
    "title": "04 影响范围评估",
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
          {"label": "Lot Impact", "value": "Impact Lot = ...，Impact WO = ...", "status": "Done"},
          {"label": "Priority Lot", "value": "Hot Lot = ...，Super Hot Run = ...", "status": "Done"},
          {"label": "Q-Time Impact", "value": "Risk = ...", "status": "Done"},
          {"label": "Move-Out Impact", "value": "Gap = ...", "status": "Done"},
          {"label": "Downstream Supply", "value": "Stage = ...，Status = ...", "status": "Done"}
        ]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Impact Assessment Status", "value": "影响范围已评估"}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 05 Case 分级与处置判定", "Gate: 确认影响范围后进入 Case 分级"]},
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
- `数据 / 工具调用.items` 必须覆盖 `Lot Impact`、`Priority Lot`、`Q-Time Impact`、`Move-Out Impact` 和 `Downstream Supply`。
- `Downstream Supply.value` 必须使用前序 `Downstream / Next Stage` 实际值；如果前序为 `PW-PH`，不得输出其他泛化对象。
- 禁止输出 `internal_payload`、`internal_render`、`model_context`、`case_snapshot`、`prompt`、`mock`。
- 禁止输出 Product 数、Q-Time 高风险 Lot 数、Recommendation、Shift Risk、ETA Risk、Delivery Risk Level、Affected Commitment 等既定业务字段 没有的数据。