## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 08 Result Prompt - 处置效果确认

你正在生成 WIP Bubble SOP 的 Flow 08 最终结果。

请只使用 `model_context.previous_flows[].content`、`model_context.raw_inputs.flow08_inputs` 和 `model_context.raw_inputs.derived_context.dynamic_recovery_mock` 中的事实、效果确认维度、门禁规则与动态恢复预置值。不要使用未在这些输入中出现的既定业务字段 数据、字段或指标。

## 分析方向

最终每个 section 只保留支撑当前判断的事实、指标和结论；不重复前序结果，不展开通用过程描述。

## 当前阶段对话

### 系统 / 用户触发

说明协同处置已获得反馈，需要确认异常指标是否从风险状态恢复到可接受区间。

### Agent 接管

限定为效果确认，不在指标恢复后直接宣布 Case 关闭。

### Agent 思考过程

对照异常发生时与当前的 Actual / Target、Queue、Move-Out、下游 WIP、Q-Time 和工具效率变化。

### Agent 分析计划

逐项确认异常指标是否恢复、恢复幅度是否满足目标，以及是否仍有副作用或回退风险。

### 数据 / 工具调用

引用原始风险快照、处置反馈和恢复后的 Actual / Target、Queue、Move-Out、下游 Actual / Target / Ratio 等数据。

### Agent 观察结果

以“异常值 -> 当前值”呈现恢复趋势，只描述发生恢复的指标和仍异常的指标。

### Agent 分析判断

判定处置有效、部分有效或无效，并明确是否需要继续控制、追加处置或回退。

### Agent 阶段输出

形成效果确认结论，满足条件才进入 Flow 09 影响消除观察。

### AI Agent

不因单次恢复即关闭 Case，需继续验证稳定性和扩散风险。

## 当前阶段结果

### 业务结果

呈现各风险指标的异常值、当前值、恢复状态及剩余风险。

### 本阶段结论

明确处置效果等级和下一步建议。

### Agent 判断逻辑

说明 Actual / Target、Queue、Move-Out、下游供料等恢复证据如何支撑效果结论。

### 状态与门禁

效果确认通过进入 Flow 09；部分有效或无效则保持处置或回退门禁。

### 关键证据

保留风险发生时与当前的成对指标、处置反馈及剩余风险。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
- Flow 08 默认假设处置反馈已返回并完成初步确认，当前要确认是否可以进入 Flow 09 影响消除观察。
- 异常数据恢复部分使用 `dynamic_recovery_mock.trend_items`：只展示前序中已异常指标的恢复值；原本不异常的指标只能写 Stable / 保持观测值，不要强行改值。
- `WIP Case Snapshot` 仍然只包含 2 个 section：`Case Header`、`Case Risk Trend｜处置后（恢复趋势）`。Flow 08 中不再输出 `Case Risk Snapshot｜异常发生时（风险快照）`，而是由 `Case Risk Trend` 替代它。
- `Case Risk Trend｜处置后（恢复趋势）` 的 items 使用 `{label,value,meta}`，`value` 展示 `异常值 -> 正常值`，`meta` 包含 `from`、`to`、`status`、`tone`、`mocked`。`tone` 使用 `down`、`up` 或 `complete`，以贴合既定业务字段 的恢复趋势样式。
- Flow 08 只做处置效果确认：角色反馈检查、恢复指标检查、风险是否继续扩散、是否需要回退/升级、是否进入 Flow 09。
- 可以写“初步有效 / 部分有效 / 证据不足 / 需回退升级”，不能写“异常已完全恢复 / Case 可关闭”。
- `数据 / 工具调用` 必须覆盖：
  - Action Feedback Check
  - SLA Check
  - Recovery Metric Check
  - WIP / Queue Trend
  - Downstream Risk Check
  - Rollback / Escalation Decision
  - Next Flow Gate
- 正常预置输出应为 `case_status=Processing`、`next_flow_no=09`、`next_flow_name=影响消除观察`；只有输入明确缺少反馈或恢复指标时才 On Hold。
