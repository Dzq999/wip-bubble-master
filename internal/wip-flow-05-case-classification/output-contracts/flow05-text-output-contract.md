# Flow 05 Text Output Contract - Case 分级与处置判定

Flow 05 只完成“Case 分级与处置判定”：在影响范围评估完成后，基于已有影响证据判定 Case Level、处置路径、初始主责、协作角色和进入 Flow 06 的门禁。

## Markdown 结构

```text
# 05 Case 分级与处置判定

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
- Impact Severity: ... [Done]
- Case Level: ... [Done]
- Disposition Path: ... [Done]
- Owner Assignment: ... [Done]
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
- Case Classification Status: 已完成分级与处置判定
- Case Level: ...
- Disposition Path: ...
- Initial Owner: ...
- Collaboration: ...
- Escalation Gate: ...

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 06 异常原因排查
- Gate: Case Owner 确认分级与处置路径后进入原因排查
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 04 已完成影响范围评估，现在进入 Case 分级与处置判定；不要写成用户提问触发。
- `数据 / 工具调用`：必须覆盖 Impact Severity、Case Level、Disposition Path、Owner Assignment 和 Next Flow Gate。
- `Agent 分析判断`：只判断分级和处置路径，不进入最终根因、原因候选排序或工程问题包派发。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- 如果证据不足以分级，`case_status=On Hold`、`next_flow_no=null`，并说明缺失证据。
