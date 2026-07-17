# Flow 10 JSON Output Contract - Case 关闭确认

Flow 10 必须返回完整 JSON，供展示层按 `content.containers[].sections[].items[]` 渲染。

## 顶层字段

```json
{
  "ok": true,
  "case_id": "...",
  "flow_no": "10",
  "flow_name": "Case 关闭确认",
  "flow_status": "Closed",
  "case_status": "Processing 或 On Hold",
  "next_flow_no": "11 或 null",
  "next_flow_name": "Case 复盘沉淀 或 null",
  "closure_confirmation_status": "关闭确认通过 / 关闭确认未通过 / 证据不足",
  "text": "...",
  "content": {
    "title": "10 Case 关闭确认",
    "containers": [
      {"title": "WIP Case Snapshot", "sections": [
        {"title": "Case Header", "items": [{"label": "Case ID", "value": "..."}]},
        {"title": "Case Closure Checklist｜关闭确认", "items": [{"label": "Task Completion", "value": "角色任务反馈完成", "meta": {"status": "Confirmed", "tone": "complete", "source": "Flow 09"}}]}
      ]},
      {"title": "当前阶段对话", "sections": [
        {"title": "系统 / 用户触发", "items": ["..."]},
        {"title": "Agent 接管", "items": ["..."]},
        {"title": "Agent 思考过程", "items": ["..."]},
        {"title": "Agent 分析计划", "items": ["..."]},
        {"title": "数据 / 工具调用", "items": [{"label": "Task Completion Check", "value": "...", "status": "Done"}]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Closure Confirmation Status", "value": "..."}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Next Flow: 11 Case 复盘沉淀", "Gate: 关闭确认通过后进入复盘沉淀"]},
        {"title": "关键证据", "items": ["..."]}
      ]}
    ]
  }
}
```

## 校验要求

- `content.containers` 恰好 3 个。
- `WIP Case Snapshot.sections` 恰好 2 个，第二个必须是 `Case Closure Checklist｜关闭确认`。
- `当前阶段对话.sections` 恰好 9 个。
- `当前阶段结果.sections` 恰好 5 个。
- `数据 / 工具调用.items` 必须包含业务事实和 `status=Done`，不能只有 Done。
- `数据 / 工具调用.items` 必须覆盖 Task Completion Check、Risk Clearance Check、Metric Recovery Check、Control Release Check、Owner Closure Confirmation、Next Flow Gate。
- 正常预置输出必须设置 `closure_confirmation_status=关闭确认通过`、`case_status=Processing`、`next_flow_no=11`、`next_flow_name=Case 复盘沉淀`。
- 禁止输出已完成复盘、已完成案例沉淀或最终根因已确认。
