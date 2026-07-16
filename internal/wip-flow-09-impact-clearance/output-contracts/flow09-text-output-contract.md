# Flow 09 Text Output Contract - 影响消除观察

Flow 09 只完成“影响消除观察”：基于 Flow 08 的恢复趋势，观察异常是否无复发、风险是否无下游转移、处置是否无副作用，并判断是否进入 Flow 10 关闭确认。

## Markdown 结构

```text
# 09 影响消除观察

## WIP Case Snapshot
### Case Header
- ...
### Case Risk Trend｜影响消除观察（稳定趋势）
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
- Observation Window Check: ... [Done]
- Recurrence Check: ... [Done]
- Downstream Transfer Check: ... [Done]
- Side Effect Check: ... [Done]
- Control Release Readiness: ... [Done]
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
- Impact Clearance Status: ...
- Observation Result: ...
- Recurrence Risk: ...
- Downstream Transfer Risk: ...
- Side Effect: ...
- Control Release Readiness: ...
- Next Flow: 10 Case 关闭确认 / null

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 10 Case 关闭确认 / On Hold
- Gate: 影响消除观察通过后进入关闭确认
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 08 已确认初步效果，现在进入影响消除观察。
- `数据 / 工具调用`：必须覆盖 Observation Window Check、Recurrence Check、Downstream Transfer Check、Side Effect Check、Control Release Readiness 和 Next Flow Gate。
- `Agent 分析判断`：只判断观察是否通过和是否进入关闭确认，不宣布 Case 已关闭。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- `WIP Case Snapshot` 只包含 `Case Header` 和 `Case Risk Trend｜影响消除观察（稳定趋势）` 两段。
- 如果输入明确观察未通过，`case_status=On Hold`、`next_flow_no=null`，并说明阻塞原因；否则默认进入 Flow 10。
