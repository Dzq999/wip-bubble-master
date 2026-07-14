# Flow 08 Result Prompt - 处置效果确认

你正在生成 WIP Bubble SOP 的 Flow 08 最终结果。

请只使用 `model_context.previous_flows[].content` 和 `model_context.raw_inputs.flow08_inputs` 中的事实、效果确认维度和门禁规则。不要使用未在这些输入中出现的前端 demo 数据、字段或指标。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
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
- 若缺少角色反馈或恢复指标，输出 `case_status=On Hold`、`next_flow_no=null`，并说明需要补齐哪些证据。
- 只有具备初步效果证据时，`next_flow_no` 才能是 `09`，`next_flow_name` 为 `影响消除观察`。
