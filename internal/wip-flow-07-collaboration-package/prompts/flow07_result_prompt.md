## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 07 Result Prompt - 跨部门协同处置

你正在生成 WIP Bubble SOP 的 Flow 07 最终结果。

请只使用 `model_context.previous_flows[].content` 和 `model_context.raw_inputs.flow07_inputs` 中的事实、角色矩阵和任务模板。不要使用未在这些输入中出现的既定业务字段 数据、字段或指标。

## 分析方向

最终每个 section 只保留支撑当前判断的事实、指标和结论；不重复前序结果，不展开通用过程描述。

## 当前阶段对话

### 系统 / 用户触发

说明根因候选和风险等级已明确到可组织跨部门协同处置的程度。

### Agent 接管

界定为跨部门协同处置：明确责任、动作、时限、反馈证据与恢复验收指标。

### Agent 思考过程

将根因候选、影响范围、临时措施和当前风险映射到工艺、设备、生产、计划等责任角色。

### Agent 分析计划

为每项处置任务定义负责人、SLA、输入输出、回传证据及 Actual WIP、Queue、Move-Out、下游供料等验收指标。

### 数据 / 工具调用

引用根因候选、分级、Impact Lot / WO、Q-Time、工具效率、WIP 与下游风险数据。

### Agent 观察结果

指出需要优先协同的风险点，以及不同部门的行动边界和依赖关系。

### Agent 分析判断

输出任务是否足以覆盖当前风险，未覆盖部分需明确追加任务或人工决策。

### Agent 阶段输出

形成协同处置任务包与反馈要求，进入 Flow 08 验证处置效果。

### AI Agent

只输出协同计划和验收标准，不把计划写成已完成事实。

## 当前阶段结果

### 业务结果

呈现问题摘要、责任角色、任务、SLA、反馈要求及恢复验收指标。

### 本阶段结论

明确协同处置是否覆盖主要候选根因和当前风险。

### Agent 判断逻辑

说明根因候选、影响与风险指标如何决定任务分工和优先级。

### 状态与门禁

任务包确认后进入 Flow 08；需要授权、资源协调或扩大动作时保留人工门禁。

### 关键证据

保留候选根因、Impact、Q-Time、WIP、工具效率、Move-Out 和下游供料数据。

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
