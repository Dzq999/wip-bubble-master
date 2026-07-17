## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 10 Result Prompt - Case 关闭确认

你正在生成 WIP Bubble SOP 的 Flow 10 最终结果。

## 分析方向

最终每个 section 只保留支撑当前判断的事实、指标和结论；不重复前序结果，不展开通用过程描述。

## 当前阶段对话

### 系统 / 用户触发

说明影响消除观察已通过，需要确认 Case 是否满足正式结案条件。

### Agent 接管

限定为结案条件核验、控制解除建议和责任确认，不重做前序分析。

### Agent 思考过程

核对处置任务、风险消除、指标稳定、临时控制解除条件和责任人确认是否完整。

### Agent 分析计划

逐项检查任务完成证据、观察通过结论、遗留风险、控制释放与关闭责任。

### 数据 / 工具调用

引用 Flow 07 任务与反馈、Flow 08 恢复结论、Flow 09 观察结论及当前 Case 状态。

### Agent 观察结果

明确哪些结案条件已满足，哪些条件仍缺少证据或需要人工确认。

### Agent 分析判断

给出“可结案”“暂不结案”或“需补充确认”，不得模糊处理遗留风险。

### Agent 阶段输出

结案条件满足则进入 Flow 11 复盘；否则列出阻塞项和责任方。

### AI Agent

不把复盘内容提前写入本阶段，也不替代责任人作最终授权。

## 当前阶段结果

### 业务结果

呈现任务完成、风险清除、指标稳定、控制释放和责任确认状态。

### 本阶段结论

明确是否满足结案条件及未满足项。

### Agent 判断逻辑

说明各项关闭检查如何与前序恢复和观察证据对应。

### 状态与门禁

可结案进入 Flow 11；未满足时维持 Case 并指定补充确认门禁。

### 关键证据

保留任务反馈、恢复结果、观察通过证据、控制状态和责任确认。

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
- 正常预置输出应为 `closure_confirmation_status=关闭确认通过`、`case_status=Processing`、`next_flow_no=11`、`next_flow_name=Case 复盘沉淀`；只有输入明确存在未完成项时才 On Hold。
