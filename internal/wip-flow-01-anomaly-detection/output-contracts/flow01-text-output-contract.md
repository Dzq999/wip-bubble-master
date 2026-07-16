# Flow 01 Text Output Contract - 异常发现

本文件只规定 Flow 01 的用户可读 Markdown 文本输出结构。

## 输出目标

Flow 01 只完成“异常发现”：判断当前最高 WIP stage 是否达到 WIP Bubble / 严重 WIP Bubble 的发现条件，并准备进入 Flow 02 异常确认。

禁止：

- 不要确认最终根因。
- 不要派发工单。
- 不要输出脚本中间态、stdout 状态、`internal_only` 或 `model_output_required`。
- 不要照抄示例正文；标题可以一致，正文必须结合本次数据重新表述。
- 不要把字段、标题和示例句式机械拼接成结果；每段内容要承接本次数据事实，体现 Flow 01 从触发、观察、判断到门禁的连续分析。
- Demo 触发口径是系统监控自动触发。输出中只描述系统监控事件、异常对象和当前 Flow 的分析判断。

## Markdown 主体结构

`text` 必须按以下顺序输出三大主容器，不能只输出摘要：

```text
# 01 异常发现

## WIP Case Snapshot
### Case Header
- ...

### Case Risk Snapshot｜异常发生时（风险快照）
- ...

## 当前阶段对话
### 系统 / 用户触发
...

### Agent 接管
...

### Agent 思考过程
...

### Agent 分析计划
- ...

### 数据 / 工具调用
- ...

### Agent 观察结果
- ...

### Agent 分析判断
...

### Agent 阶段输出
...

### AI Agent
...

## 当前阶段结果
### 业务结果
- ...

### 本阶段结论
- ...

### Agent 判断逻辑
- ...

### 状态与门禁
- ...

### 关键证据
- ...
```

## WIP Case Snapshot

只允许包含两个三级标题：

- `Case Header`
- `Case Risk Snapshot｜异常发生时（风险快照）`

这两个标题之外不新增其他 Snapshot 三级标题。

### Case Header 内容方向

覆盖前端 demo 顶部 Header 与运行态条信息。可包含：

- Case ID
- Priority
- Object
- Case Type
- Occur Time
- Operator
- Current Stage
- Case Age
- Stage Elapsed
- SLA Remaining
- Owner
- Status

### Case Risk Snapshot｜异常发生时（风险快照）内容方向

覆盖前端 demo 的异常发生时风险卡片。可包含：

- WIP
- Queue
- Eligible Tool
- Move-Out
- Q-Time
- Downstream：使用 `downstream_starvation.next_stage_name` 与 `downstream_starvation.if_starved`，例如 `Next Stage = <next_stage_name>; Status = <if_starved>`；`Clean` 只是可能的 stage name 示例，不能当成固定下游或固定状态

## 当前阶段对话

必须包含 9 个三级标题，不能合并、不能缺少、不能改名：

1. `系统 / 用户触发`：说明系统监控自动触发了 Flow 01；内容只描述监控事件和异常对象。
2. `Agent 接管`：说明当前 Agent 进入异常发现，不要写成另一个模型接管。
3. `Agent 思考过程`：说明先核对对象、指标口径、偏差和进入条件。
4. `Agent 分析计划`：列出读取 WIP、读取 Target、计算偏差、判断触发条件等步骤。
5. `数据 / 工具调用`：必须列出事实型数据结果，不展示工具执行状态；格式参考 `MES / WIP Profile: Actual WIP = 8,050 [Done]`、`Planning Config: Target WIP = 258 [Done]`、`BI Trend: WIP 连续升高 [Done]`。允许附带 `Done` 状态；禁止只有 `Done` / `Pending`，也禁止出现内部表名或 `mock` 字样。
6. `Agent 观察结果`：列出 Actual WIP、Target WIP、Gap、Queue、趋势等事实。
7. `Agent 分析判断`：基于事实判断是否达到 WIP Bubble / 严重 WIP Bubble，强调不是最终根因。
8. `Agent 阶段输出`：给出 Flow 01 阶段结论。
9. `AI Agent`：给出门禁问题，限定为是否进入 Flow 02 异常确认；Flow 02 只做数据刷新、指标口径、Target 有效性、异常持续时间和重复 Case 校验。

## 当前阶段结果

必须包含 5 个三级标题：

- `业务结果`：展示 Bubble Status、Actual WIP、Target WIP、Gap、Queue、趋势、触发来源等指标。
- `本阶段结论`：说明是否生成 WIP Bubble 异常发现记录，以及是否建议进入 Flow 02。
- `Agent 判断逻辑`：说明判断依据，例如 Actual 是否超过 Severe UCL、Queue 是否主导、Flow 01 不确认根因。
- `状态与门禁`：只说明 Next Flow 与 Gate；不要重复展示顶层 `flow_status` / `case_status`。
- `关键证据`：列出支撑结论的关键事实。

## 未发现异常时

如果 `model_context.has_stage_data=false`，或没有发现达到 WIP Bubble / 严重 WIP Bubble 的 stage：

- `case_status=Closed`
- `next_flow_no=null`
- 不提示进入 Flow 02
- Markdown 仍保留三大主容器，但内容说明“未发现需要进入异常确认的 WIP Bubble stage”

## 文本输出前自检

最终回答前必须确认：

- Markdown 有 `WIP Case Snapshot`、`当前阶段对话`、`当前阶段结果` 三大主容器。
- `WIP Case Snapshot` 只有 `Case Header` 与 `Case Risk Snapshot｜异常发生时（风险快照）`。
- `当前阶段对话` 有 9 个三级标题。
- `当前阶段结果` 有 `业务结果`、`本阶段结论`、`Agent 判断逻辑`、`状态与门禁`、`关键证据`。













