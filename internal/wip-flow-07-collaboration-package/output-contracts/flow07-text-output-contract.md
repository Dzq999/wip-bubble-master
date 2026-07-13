# Flow 07 Text Output Contract - 工程问题包与协同任务

Flow 07 只完成“工程问题包与协同任务”：基于前序结论组织 Case 问题包、角色任务、SLA、反馈要求和恢复验证指标。

## Markdown 结构

```text
# 07 工程问题包与协同任务

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
- Engineering Package: ... [Done]
- Root Cause Candidate: ... [Done]
- Task Breakdown: ... [Done]
- Owner Assignment: ... [Done]
- Collaboration SLA: ... [Done]
- Recovery Metric: ... [Done]
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
- Collaboration Package Status: 已生成工程问题包与协同任务建议
- Package Scope: ...
- Primary Owner: ...
- Collaboration Tasks: ...
- SLA: ...
- Recovery Metrics: ...
- Next Flow: 08 处置效果确认

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 08 处置效果确认
- Gate: 角色完成初步反馈并定义恢复验证指标后进入处置效果确认
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 06 已完成候选原因排查，现在进入工程问题包与协同任务。
- `数据 / 工具调用`：必须覆盖 Engineering Package、Root Cause Candidate、Task Breakdown、Owner Assignment、Collaboration SLA、Recovery Metric 和 Next Flow Gate。
- `Agent 分析判断`：只判断任务包和协同路径，不宣布处置已生效。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- 如果证据不足以拆分任务，`case_status=On Hold`、`next_flow_no=null`，并说明缺失证据。
