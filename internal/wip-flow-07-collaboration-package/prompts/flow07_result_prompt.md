# Flow 07 Result Prompt - 工程问题包与协同任务

你正在生成 WIP Bubble SOP 的 Flow 07 最终结果。

请只使用 `model_context.previous_flows[].content` 和 `model_context.raw_inputs.flow07_inputs` 中的事实、角色矩阵和任务模板。不要使用未在这些输入中出现的前端 demo 数据、字段或指标。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
- Flow 07 只做工程问题包与跨部门协同任务：问题包摘要、任务拆分、主责/协同、SLA、反馈要求、恢复指标和进入 Flow 08 的门禁。
- 可以写“建议创建 / 待派发 / 待反馈”的任务，不能写“已真实派单 / 已通知 / 已完成处置”。
- `数据 / 工具调用` 必须覆盖：
  - Engineering Package
  - Root Cause Candidate
  - Task Breakdown
  - Owner Assignment
  - Collaboration SLA
  - Recovery Metric
  - Next Flow Gate
- 若 Flow 06 证据不足，输出 `case_status=On Hold`、`next_flow_no=null`，并说明需要补齐哪些候选原因或证据。
- 正常情况下 `next_flow_no` 为 `08`，`next_flow_name` 为 `处置效果确认`。
