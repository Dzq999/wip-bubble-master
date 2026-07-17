# Flow 11 Text Output Contract - Case 复盘沉淀

Flow 11 完成“Case 复盘沉淀”：基于完整闭环结果，沉淀根因摘要、有效措施、无效或需改进措施、规则优化建议和案例标签，并关闭 Case。

## Markdown 结构

```text
# 11 Case 复盘沉淀

## WIP Case Snapshot
### Case Header
- ...
### Case Retrospective Summary｜复盘沉淀
- ...

## 当前阶段对话
### 系统 / 用户触发
...
### Agent 接管
...
### Agent 思考过程
...
### Agent 分析计划
- ...
### 数据 / 工具调用
- Root Cause Summary: ... [Done]
- Effective Action Review: ... [Done]
- Ineffective Action Review: ... [Done]
- Rule Optimization: ... [Done]
- Case Tagging: ... [Done]
- Case Archive: ... [Done]
### Agent 观察结果
- ...
### Agent 分析判断
...
### Agent 阶段输出
...
### AI Agent
...

## 当前阶段结果
### 业务结果
- Retrospective Status: ...
- Root Cause Summary: ...
- Effective Actions: ...
- Improvement Items: ...
- Rule Optimization: ...
- Case Tags: ...
- Archive Status: ...

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Case Status: Closed / On Hold
- Next Flow: null
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 10 已完成关闭确认，现在进入 Case 复盘沉淀。
- `数据 / 工具调用`：必须覆盖 Root Cause Summary、Effective Action Review、Ineffective Action Review、Rule Optimization、Case Tagging 和 Case Archive。
- `Agent 分析判断`：只总结本次闭环沉淀，不输出新的现场处置指令。
- `状态与门禁`：可以展示 Case Status 和 Next Flow；正常预置为 Closed / null。
- `WIP Case Snapshot` 只包含 `Case Header` 和 `Case Retrospective Summary｜复盘沉淀` 两段。
- 禁止声称已自动更新真实生产规则；只能输出规则优化建议或待业务确认项。
