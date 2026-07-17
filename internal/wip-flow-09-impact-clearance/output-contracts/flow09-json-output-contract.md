# Flow 09 JSON Output Contract - 影响消除观察

Flow 09 必须返回完整 JSON，供展示层按 `content.containers[].sections[].items[]` 渲染。

## 顶层字段

```json
{
  "ok": true,
  "case_id": "...",
  "flow_no": "09",
  "flow_name": "影响消除观察",
  "flow_status": "Closed",
  "case_status": "Processing 或 On Hold",
  "next_flow_no": "10 或 null",
  "next_flow_name": "Case 关闭确认 或 null",
  "impact_clearance_status": "观察通过 / 观察未通过 / 证据不足",
  "text": "...",
  "content": {
    "title": "09 影响消除观察",
    "containers": [
      {"title": "WIP Case Snapshot", "sections": [
        {"title": "Case Header", "items": [{"label": "Case ID", "value": "..."}]},
        {"title": "Case Risk Trend｜影响消除观察（稳定趋势）", "items": [{"label": "Actual WIP", "value": "248 / Target 258，观察期保持正常", "meta": {"status": "Stable", "tone": "complete", "source": "Flow 08"}}]}
      ]},
      {"title": "当前阶段对话", "sections": [
        {"title": "系统 / 用户触发", "items": ["..."]},
        {"title": "Agent 接管", "items": ["..."]},
        {"title": "Agent 思考过程", "items": ["..."]},
        {"title": "Agent 分析计划", "items": ["..."]},
        {"title": "数据 / 工具调用", "items": [{"label": "Observation Window Check", "value": "...", "status": "Done"}]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Impact Clearance Status", "value": "..."}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 10 Case 关闭确认", "Gate: 影响消除观察通过后进入关闭确认"]},
        {"title": "关键证据", "items": ["..."]}
      ]}
    ]
  }
}
```

## 校验要求

- `content.containers` 恰好 3 个。
- `WIP Case Snapshot.sections` 恰好 2 个，第二个必须是 `Case Risk Trend｜影响消除观察（稳定趋势）`。
- `当前阶段对话.sections` 恰好 9 个。
- `当前阶段结果.sections` 恰好 5 个。
- `数据 / 工具调用.items` 必须包含业务事实和 `status=Done`，不能只有 Done。
- `数据 / 工具调用.items` 必须覆盖 Observation Window Check、Recurrence Check、Downstream Transfer Check、Side Effect Check、Control Release Readiness、Next Flow Gate。
- 正常预置输出必须设置 `impact_clearance_status=观察通过`、`case_status=Processing`、`next_flow_no=10`、`next_flow_name=Case 关闭确认`。
- 禁止输出 Case 已关闭、已完成复盘、已完成案例沉淀或最终根因已确认。
