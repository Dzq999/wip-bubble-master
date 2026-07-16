## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 09 Result Prompt - 影响消除观察

你正在生成 WIP Bubble SOP 的 Flow 09 最终结果。

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
- 正常演示输出应为 `impact_clearance_status=观察通过`、`case_status=Processing`、`next_flow_no=10`、`next_flow_name=Case 关闭确认`；只有输入明确存在复发、转移、副作用或证据不足时才 On Hold。
