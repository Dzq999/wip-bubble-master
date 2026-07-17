## 最优先：运行时事实来源

只使用本次 `model_context.raw_inputs` 的事实生成结果：SQL 快照、前序 Flow 内容和当前 Flow 实际存在的 `*_mock` / `*_inputs`；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，按实际存在的键处理，不维护固定字段清单。

`examples/`、output-contracts 和本 prompt 中的示例均不是事实来源，禁止复用其对象名、数值、人员、时长、风险状态或结论。任何具体表述必须能在 `raw_inputs` 中找到来源；找不到就省略或说明“当前数据不足以判断”，禁止猜测或补造。

# Flow 06 Result Prompt - 异常原因排查

你正在生成 WIP Bubble SOP 的 Flow 06 最终结果。

请只使用 `model_context.previous_flows[].content` 和 `model_context.raw_inputs.sql_results` 中的事实。不要使用未在这些输入中出现的既定业务字段 数据、字段或指标。

## 分析方向

最终每个 section 只保留支撑当前判断的事实、指标和结论；不重复前序结果，不展开通用过程描述。

## 当前阶段对话

### 系统 / 用户触发

说明已完成分级，需要从 WIP 状态、设备效率和流转趋势中筛选根因候选。

### Agent 接管

界定输出为可验证的候选根因、证据、排除项和验证动作。

### Agent 思考过程

对比 Hold / Run WIP、设备状态、OE Ratio、Move-In / Move-Out、产品-设备匹配与派工异常。

### Agent 分析计划

定位 WIP 停滞位置，识别效率偏低或流入流出失衡信号，并为每个候选定义验证方式。

### 数据 / 工具调用

引用 Hold WIP、Run WIP、Tool Status、各机台及总 OE Ratio、Move-In / Out 趋势、产品与设备数据。

### Agent 观察结果

说明 WIP 是否集中在 Hold、Run 或 Queue，工具效率是否偏离，以及流量失衡出现在哪一侧。

### Agent 分析判断

按证据强弱列出候选根因及置信度，并同步写出尚未支持的假设。

### Agent 阶段输出

形成可交接的根因候选包，进入 Flow 07 跨部门协同处置。

### AI Agent

不得将候选直接称为已确认根因，验证闭环留给后续任务。

## 当前阶段结果

### 业务结果

呈现候选根因、置信度、证据、排除项和待验证动作。

### 本阶段结论

明确当前最需要验证的原因和未确认边界。

### Agent 判断逻辑

说明 Hold / Run、OE Ratio、流转趋势及派工或设备信号如何支撑候选判断。

### 状态与门禁

候选包完整后进入 Flow 07；证据不足时应保留补数或工程验证门禁。

### 关键证据

保留 Hold / Run WIP、Tool Status、OE Ratio、Move-In / Out 和产品设备相关数据。

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
- 最终 `next_flow_no` 应为 `07`，`next_flow_name` 应为 `跨部门协同处置`，除非证据不足导致 `case_status=On Hold`。
