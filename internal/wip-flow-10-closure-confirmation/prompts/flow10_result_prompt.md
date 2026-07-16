## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 10 Result Prompt - Case 关闭确认

你正在生成 WIP Bubble SOP 的 Flow 10 最终结果。

## 输入

- `model_context.previous_flows`：前序 Flow 已保存的轻量 `content`，尤其是 Flow 09 的影响消除观察结果。
- `model_context.raw_inputs.flow10_inputs`：Flow 10 默认关闭确认规则和门禁。
- `model_context.raw_inputs.derived_context.flow09_closure_context`：从 Flow 09 提取的观察通过、无复发、无转移、无副作用和控制释放准备度信息。

## 生成要求

- 输出完整 Markdown `text` 和完整结构化 `content.containers`。
- Flow 10 默认假设关闭确认通过，因为 Flow 09 已经确认影响消除观察通过。
- `WIP Case Snapshot` 仍然只包含 2 个 section：`Case Header`、`Case Closure Checklist｜关闭确认`。
- `Case Closure Checklist｜关闭确认` 的 items 使用 `{label,value,meta}`；`value` 展示关闭条件确认状态，`meta` 可包含 `status`、`tone`、`source`。
- Flow 10 只做 Case 关闭确认：任务完成、风险解除、指标恢复、受控动作关闭、责任人确认、是否进入 Flow 11。
- 可以写“关闭确认通过 / 进入复盘沉淀 / 关闭条件满足”，不能写“已完成复盘 / 已完成案例沉淀 / 最终根因已确认”。
- `数据 / 工具调用` 必须包含：
  - Task Completion Check
  - Risk Clearance Check
  - Metric Recovery Check
  - Control Release Check
  - Owner Closure Confirmation
  - Next Flow Gate
- 正常演示输出应为 `closure_confirmation_status=关闭确认通过`、`case_status=Processing`、`next_flow_no=11`、`next_flow_name=Case 复盘沉淀`；只有输入明确存在未完成项时才 On Hold。
