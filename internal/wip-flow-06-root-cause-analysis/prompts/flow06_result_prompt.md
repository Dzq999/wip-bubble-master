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
