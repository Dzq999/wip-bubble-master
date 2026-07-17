# Flow 06 Text Output Contract - 异常原因排查

Flow 06 只完成“异常原因排查”：基于前序 Flow 结论和 Flow 06 SQL 结果，输出候选原因排序、证据链、待补证据和下一步验证动作。

## Markdown 结构

```text
# 06 异常原因排查

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
- WIP State Check: ... [Done]
- Tool Status Check: ... [Done]
- Tool Efficiency Check: ... [Done]
- Move-In Trend: ... [Done]
- Move-Out Trend: ... [Done]
- Root Cause Candidate: ... [Done]
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
- Root Cause Analysis Status: 已完成候选原因排查
- Primary Candidate: ...
- Secondary Candidate: ...
- Confidence: ...
- Missing Evidence: ...
- Next Flow: 07 跨部门协同处置

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 07 跨部门协同处置
- Gate: 工程师确认候选原因和补证项后进入跨部门协同处置
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 05 已完成分级与处置判定，现在进入异常原因排查。
- `数据 / 工具调用`：必须覆盖 WIP State Check、Tool Status Check、Tool Efficiency Check、Move-In Trend、Move-Out Trend 和 Root Cause Candidate。
- `Agent 分析判断`：输出候选原因排序，不写最终根因已确认。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- 如果证据不足，`case_status=On Hold`、`next_flow_no=null`，并说明缺失证据。
