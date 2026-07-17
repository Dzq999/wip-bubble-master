# Flow 11 JSON Output Contract - Case 复盘沉淀

Flow 11 必须返回完整 JSON，供展示层按 `content.containers[].sections[].items[]` 渲染。

## 顶层字段

```json
{
  "ok": true,
  "case_id": "...",
  "flow_no": "11",
  "flow_name": "Case 复盘沉淀",
  "flow_status": "Closed",
  "case_status": "Closed 或 On Hold",
  "next_flow_no": null,
  "next_flow_name": null,
  "retrospective_status": "复盘沉淀完成 / 证据不足",
  "text": "...",
  "content": {
    "title": "11 Case 复盘沉淀",
    "containers": [
      {"title": "WIP Case Snapshot", "sections": [
        {"title": "Case Header", "items": [{"label": "Case ID", "value": "..."}]},
        {"title": "Case Retrospective Summary｜复盘沉淀", "items": [{"label": "Root Cause Summary", "value": "...", "meta": {"status": "Archived", "tone": "complete", "source": "Flow 06-10"}}]}
      ]},
      {"title": "当前阶段对话", "sections": [
        {"title": "系统 / 用户触发", "items": ["..."]},
        {"title": "Agent 接管", "items": ["..."]},
        {"title": "Agent 思考过程", "items": ["..."]},
        {"title": "Agent 分析计划", "items": ["..."]},
        {"title": "数据 / 工具调用", "items": [{"label": "Root Cause Summary", "value": "...", "status": "Done"}]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": [{"label": "Retrospective Status", "value": "..."}]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["Case Status: Closed", "Next Flow: null"]},
        {"title": "关键证据", "items": ["..."]}
      ]}
    ]
  }
}
```

## 校验要求

- `content.containers` 恰好 3 个。
- `WIP Case Snapshot.sections` 恰好 2 个，第二个必须是 `Case Retrospective Summary｜复盘沉淀`。
- `当前阶段对话.sections` 恰好 9 个。
- `当前阶段结果.sections` 恰好 5 个。
- `数据 / 工具调用.items` 必须包含业务事实和 `status=Done`，不能只有 Done。
- `数据 / 工具调用.items` 必须覆盖 Root Cause Summary、Effective Action Review、Ineffective Action Review、Rule Optimization、Case Tagging、Case Archive。
- 正常预置输出必须设置 `retrospective_status=复盘沉淀完成`、`case_status=Closed`、`next_flow_no=null`、`next_flow_name=null`。
- 禁止输出已自动更新真实生产规则。
