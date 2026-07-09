# Flow 04 Text Output Contract - 影响范围评估

Flow 04 只完成“影响范围评估”：在临时措施已生成或已执行后，基于前端 demo / SQL 已有字段评估异常对 Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out 和下游供料的影响，判断是否超过单点波动。

## Markdown 结构

```text
# 04 影响范围评估

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
- Lot Impact: Impact Lot = ...，Impact WO = ... [Done]
- Priority Lot: Hot Lot = ...，Super Hot Run = ... [Done]
- Q-Time Impact: Risk = ... [Done]
- Move-Out Impact: Gap = ... [Done]
- Downstream Supply: Stage = ...，Status = ... [Done]
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
- Impact Assessment Status: 影响范围已评估
- Impact Scope: ... Lot / ... WO
- Priority Lot: Hot Lot = ...，Super Hot Run = ...
- Q-Time Impact: ...
- Move-Out Impact: ...
- Downstream Impact: ...
- Spread Assessment: 超过单点波动 / 仍局限于单点波动

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 05 Case 分级与处置判定
- Gate: 确认影响范围后进入 Case 分级
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 03 已生成或执行临时措施，现在进入影响范围评估；不要写成用户提问触发。
- `数据 / 工具调用`：必须只使用前端 demo / SQL 已有字段，且必须是事实值 + Done 状态，不要只写 Done。
- 不要输出 Product 数、Q-Time 高风险 Lot 数、Recommendation、Shift Risk、ETA Risk、Delivery Risk Level、Affected Commitment 等前端 demo 没有的数据。
- `Downstream Supply`：下游对象必须来自前序 `Downstream / Next Stage` 实际值；如果前序为 `PW-PH`，这里也必须写 `PW-PH`。
- `Agent 分析判断`：只判断影响范围和扩散程度，不进入最终根因、正式 Case 分级或主责归属。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- 如果无法评估关键影响范围，`case_status=On Hold`、`next_flow_no=null`，并说明阻塞原因。