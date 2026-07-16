## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 11 Result Prompt - Case 复盘沉淀

你正在生成 WIP Bubble SOP 的 Flow 11 最终结果。

## 输入

- `model_context.previous_flows`：前序 Flow 已保存的轻量 `content`，尤其是 Flow 06 的原因候选、Flow 07 的协同任务、Flow 08/09 的恢复验证和 Flow 10 的关闭确认。
- `model_context.raw_inputs.flow11_inputs`：Flow 11 默认复盘沉淀规则和标签。
- `model_context.raw_inputs.derived_context.retrospective_context`：从前序内容提取的候选原因、有效动作、关闭确认信息。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
- Flow 11 默认假设复盘沉淀完成，因为 Flow 10 已经关闭确认通过。
- `WIP Case Snapshot` 仍然只包含 2 个 section：`Case Header`、`Case Retrospective Summary｜复盘沉淀`。
- `Case Retrospective Summary｜复盘沉淀` 的 items 使用 `{label,value,meta}`；`value` 展示沉淀摘要，`meta` 可包含 `status`、`tone`、`source`。
- Flow 11 完成根因摘要、有效措施、无效或需改进措施、规则优化建议、案例标签和案例归档。
- 可以写“复盘沉淀完成 / Case 关闭 / 形成案例标签”，不能写“已自动更新真实生产规则”。
- `数据 / 工具调用` 必须包含：
  - Root Cause Summary
  - Effective Action Review
  - Ineffective Action Review
  - Rule Optimization
  - Case Tagging
  - Case Archive
- 正常演示输出应为 `retrospective_status=复盘沉淀完成`、`case_status=Closed`、`next_flow_no=null`、`next_flow_name=null`；只有输入明确缺少关闭确认或复盘信息不足时才 On Hold。
