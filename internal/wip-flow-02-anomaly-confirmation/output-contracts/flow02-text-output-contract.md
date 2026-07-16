# Flow 02 Text Output Contract - 异常确认

Flow 02 只完成“异常成立性确认”：确认 Flow 01 发现的 WIP Bubble 是否真实成立，排除数据延迟、指标口径错误、Target 无效、短时波动和重复 Case。

## Markdown 结构

```text
# 02 异常确认

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
- Data Freshness Check: 数据刷新正常 [Done]
- Metric Scope Check: Stage WIP [Done]
- Target WIP Query: Target WIP = ...，有效 [Done]
- Open Case Search: 无重复 Case [Done]
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
- Confirmation Status: 异常确认成立
- Data Freshness: 数据刷新正常
- Metric Scope: Stage WIP
- Target Validity: 有效
- Duration: ...
- Duplicate Case: 无重复 Case

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 03 临时措施
- Gate: MFG / Shift 确认异常成立
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 01 已生成异常事件，需要进行成立性校验；不要写成用户提问触发。
- `数据 / 工具调用`：必须是事实值 + Done 状态，不要只写 Done。
- `Agent 分析判断`：只判断异常是否成立，不进入原因排查和临时措施。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- 如果确认不成立，`case_status=Closed`、`next_flow_no=null`，并说明未成立原因。
