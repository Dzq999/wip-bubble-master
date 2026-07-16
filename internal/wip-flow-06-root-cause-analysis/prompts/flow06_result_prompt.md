## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 06 Result Prompt - 异常原因排查

你正在生成 WIP Bubble SOP 的 Flow 06 最终结果。

请只使用 `model_context.previous_flows[].content` 和 `model_context.raw_inputs.sql_results` 中的事实。不要使用未在这些输入中出现的前端 demo 数据、字段或指标。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
- Flow 06 只做异常原因排查：候选原因排序、证据链、排除项、缺失证据和下一步验证动作。
- 可以写“主候选原因”“次候选原因”“初步判断”，不能写“最终根因已确认”。
- `数据 / 工具调用` 必须覆盖：
  - WIP State Check
  - Tool Status Check
  - Tool Efficiency Check
  - Move-In Trend
  - Move-Out Trend
  - Root Cause Candidate
- 若证据不足，输出低置信度并要求补齐数据；不要硬判。
- 最终 `next_flow_no` 应为 `07`，`next_flow_name` 应为 `工程问题包与协同任务`，除非证据不足导致 `case_status=On Hold`。
