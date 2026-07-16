# Flow 03 Text Output Contract - 临时措施

Flow 03 只完成“临时措施”：异常已确认成立后，在根因完全确认前先控制生产风险，保护 Hot Lot / Super Hot Run，控制非关键 Move-In，通知下游风险，并避免不必要的全量 Hold。

## Markdown 结构

```text
# 03 临时措施

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
- Hot Lot Query: Hot Lot = ...，Super Hot Run = ... [Done]
- Move-In Check: 建议限制非关键 Product / Lot [Done]
- Downstream Risk Check: ... [Done]
- Hold Recommendation: 不建议全量 Hold [Done]
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
- Containment Status: 临时措施已生成 / 已执行
- Hot Lot Protection: ...
- Move-In Control: ...
- Downstream Notice: ...
- Hold Recommendation: 不建议全量 Hold
- Rollback Condition: ...

### 本阶段结论
- ...
### Agent 判断逻辑
- ...
### 状态与门禁
- Next Flow: 04 影响范围评估
- Gate: 确认临时措施已执行并进入影响范围评估
### 关键证据
- ...
```

## 内容要求

- `系统 / 用户触发`：说明 Flow 02 已确认异常成立，需要先执行风险遏制；不要写成用户提问触发。
- `数据 / 工具调用`：必须是事实值 + Done 状态，不要只写 Done；Hot Lot Query 来自 `locate_priority_lots.sql`，Downstream Risk Check 来自 `locate_downstream_starvation.sql`。
- `Downstream Risk Check`：下游对象必须来自前序 `Downstream / Next Stage` 实际值；如果前序为 `PW-PH`，这里也必须写 `PW-PH`。
- `Agent 分析判断`：只判断临时控制策略，不进入原因排查、影响范围量化或正式 Case 分级。
- `状态与门禁`：只写 Next Flow 和 Gate，不展示 Flow Status / Case Status。
- 高风险动作只能写成建议、通知、草案或待确认，不要写成 Agent 已直接修改生产主系统。
- 如果临时措施不能执行，`case_status=On Hold`、`next_flow_no=null`，并说明阻塞原因。

