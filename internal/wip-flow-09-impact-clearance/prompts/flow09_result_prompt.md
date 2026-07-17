## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 09 Result Prompt - 影响消除观察

你正在生成 WIP Bubble SOP 的 Flow 09 最终结果。

## 分析方向

最终每个 section 只保留支撑当前判断的事实、指标和结论；不重复前序结果，不展开通用过程描述。

## 当前阶段对话

### 系统 / 用户触发

说明 Flow 08 已确认指标恢复，需要观察是否复发、转移或产生新的下游影响。

### Agent 接管

限定为影响消除观察与稳定性判断，不重新定义根因或跳过观察证据。

### Agent 思考过程

检查 WIP、Queue、Move-Out、下游供料、Q-Time 与关键批次是否维持恢复状态。

### Agent 分析计划

比对恢复前后和观察期内的风险趋势，确认无复发、无下游转移、无新增副作用。

### 数据 / 工具调用

引用 Flow 08 恢复结果、原始异常快照和观察期内可用的 WIP、Queue、Move-Out、下游及 Q-Time 指标。

### Agent 观察结果

指出已消除的影响、仍需观察的指标，以及是否出现风险回升或转移。

### Agent 分析判断

给出“观察通过”“继续观察”或“恢复处置”，并说明触发条件。

### Agent 阶段输出

观察通过才进入 Flow 10 结案确认；未通过返回持续处置或人工复核。

### AI Agent

不输出关闭结论，只输出观察结论与结案资格。

## 当前阶段结果

### 业务结果

呈现观察期内的风险趋势、复发检查、下游影响和关键批次状态。

### 本阶段结论

明确影响是否消除及观察是否通过。

### Agent 判断逻辑

说明稳定性、无复发、无转移和无副作用如何共同构成通过条件。

### 状态与门禁

观察通过进入 Flow 10；否则保持观察、追加处置或人工决策。

### 关键证据

保留原始异常、恢复值、观察期趋势及下游和关键批次证据。

## 输入

- `model_context.previous_flows`：前序 Flow 已保存的轻量 `content`，尤其是 Flow 08 的 `Case Risk Trend` 和恢复证据。
- `model_context.raw_inputs.flow09_inputs`：Flow 09 默认观察规则和门禁。
- `model_context.raw_inputs.derived_context.flow08_observation_context`：从 Flow 08 提取的恢复趋势和处置效果信息。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
- Flow 09 默认假设影响消除观察通过，因为 Flow 08 已经形成恢复趋势。
- `WIP Case Snapshot` 仍然只包含 2 个 section：`Case Header`、`Case Risk Trend｜影响消除观察（稳定趋势）`。
- `Case Risk Trend｜影响消除观察（稳定趋势）` 的 items 使用 `{label,value,meta}`；`value` 展示恢复后的稳定观察状态，`meta` 可包含 `status`、`tone`、`source`。
- Flow 09 只做影响消除观察：无复发、无下游转移风险、无处置副作用、临时控制释放准备度、是否进入 Flow 10。
- 可以写“观察通过 / 进入关闭确认 / 继续保持观察口径”，不能写“Case 已关闭 / 已复盘沉淀 / 最终根因已确认”。
- `数据 / 工具调用` 必须包含：
  - Observation Window Check
  - Recurrence Check
  - Downstream Transfer Check
  - Side Effect Check
  - Control Release Readiness
  - Next Flow Gate
- 正常预置输出应为 `impact_clearance_status=观察通过`、`case_status=Processing`、`next_flow_no=10`、`next_flow_name=Case 关闭确认`；只有输入明确存在复发、转移、副作用或证据不足时才 On Hold。
