## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

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
