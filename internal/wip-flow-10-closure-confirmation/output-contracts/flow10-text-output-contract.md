# Flow 10 Text Output Contract - Case 关闭确认

Flow 10 只完成“Case 关闭确认”：基于 Flow 09 的影响消除观察结果，确认关闭条件是否满足，并判断是否进入 Flow 11 复盘沉淀。

## Markdown 结构

```text
# 10 Case 关闭确认

## WIP Case Snapshot
### Case Header
- ...
### Case Closure Checklist｜关闭确认
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
- Task Completion Check: ... [Done]
- Risk Clearance Check: ... [Done]
- Metric Recovery Check: ... [Done]
- Control Release Check: ... [Done]
- Owner Closure Confirmation: ... [Done]
- Next Flow Gate: ... [Done]
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
- Closure Confirmation Status: ...
- Task Completion: ...
- Risk Clearance: ...
- Metric Recovery: ...
- Control Release: ...
- Owner Confirmation: ...
- Next Flow: 11 Case 复盘沉淀 / null

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 11 Case 复盘沉淀 / On Hold
- Gate: 关闭确认通过后进入复盘沉淀
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 09 已确认影响消除观察通过，现在进入 Case 关闭确认。
- `数据 / 工具调用`：必须覆盖 Task Completion Check、Risk Clearance Check、Metric Recovery Check、Control Release Check、Owner Closure Confirmation 和 Next Flow Gate。
- `Agent 分析判断`：只判断关闭条件是否满足和是否进入复盘沉淀，不输出复盘沉淀结论。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- `WIP Case Snapshot` 只包含 `Case Header` 和 `Case Closure Checklist｜关闭确认` 两段。
- 如果输入明确关闭条件不满足，`case_status=On Hold`、`next_flow_no=null`，并说明阻塞原因；否则默认进入 Flow 11。
