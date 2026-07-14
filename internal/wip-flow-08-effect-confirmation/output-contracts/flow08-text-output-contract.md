# Flow 08 Text Output Contract - 处置效果确认

Flow 08 只完成“处置效果确认”：基于 Flow 07 的协同任务、SLA、恢复指标和反馈要求，判断是否具备进入 Flow 09 观察的初步效果证据。

## Markdown 结构

```text
# 08 处置效果确认

## WIP Case Snapshot
### Case Header
- ...
### Case Risk Snapshot｜异常发生时（风险快照）
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
- Action Feedback Check: ... [Done]
- SLA Check: ... [Done]
- Recovery Metric Check: ... [Done]
- WIP / Queue Trend: ... [Done]
- Downstream Risk Check: ... [Done]
- Rollback / Escalation Decision: ... [Done]
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
- Effect Confirmation Status: ...
- Feedback Status: ...
- Recovery Evidence: ...
- Risk Decision: ...
- Missing Evidence: ...
- Next Flow: 09 影响消除观察 / null

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 09 影响消除观察 / On Hold
- Gate: 初步效果证据充分后进入影响消除观察
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 07 已生成工程问题包与协同任务，且处置反馈已返回并完成初步确认，现在进入处置效果确认。
- `数据 / 工具调用`：必须覆盖 Action Feedback Check、SLA Check、Recovery Metric Check、WIP / Queue Trend、Downstream Risk Check、Rollback / Escalation Decision 和 Next Flow Gate。
- `Agent 分析判断`：只判断初步效果和是否需要回退/升级，不宣布异常完全恢复。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- `Case Risk Trend｜处置后（恢复趋势）` 必须展示异常值 -> 正常值；恢复值来自 `dynamic_recovery_mock.trend_items`。`meta.tone` 使用 `down`、`up` 或 `complete`。
- 如果输入明确证据不足，`case_status=On Hold`、`next_flow_no=null`，并说明缺失证据；否则默认进入 Flow 09。



