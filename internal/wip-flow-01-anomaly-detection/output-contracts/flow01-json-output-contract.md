# Flow 01 JSON Output Contract - 异常发现

本文件只规定 Flow 01 给前端或编排层使用的轻量结构化 JSON。最终可见内容禁止出现 `mock` 字样；来自内部 mock 的字段也必须按业务口径表述为快照输入、补充信号或具体数据名称。禁止只输出摘要 JSON；`json` 或 `both` 中的 JSON 必须包含完整 `text` 和完整 `content.containers`。

## 设计目标

JSON 只需要覆盖 Markdown 文本内容，方便前端按容器循环渲染；不要重复维护一套复杂的前端专用结构。

`content` 不是字段拼盘。每个 section 的 `items` 必须与 Markdown 同一段分析对齐，体现本次数据从触发、观察、判断到门禁的上下文关系。

必须避免：

- 不要输出 `frontend_demo`。
- 不要输出 `frontend_payload`。
- 不要在顶层重复 `current_stage_dialogue`、`current_stage_result`、`wip_case_snapshot`。
- 不要输出 `model_context`、`case_snapshot`、`prompt`、`output_contract` 等内部上下文。

## 顶层结构

```json
{
  "ok": true,
  "case_id": "...",
  "flow_no": "01",
  "flow_name": "异常发现",
  "flow_status": "Closed",
  "case_status": "Processing | Closed | On Hold",
  "next_flow_no": "02 或 null",
  "next_flow_name": "异常确认 或 null",
  "bubble_status": "严重 WIP Bubble",
  "text": "完整 Markdown",
  "content": {
    "title": "01 异常发现",
    "containers": [
      {"title": "WIP Case Snapshot", "sections": [
        {"title": "Case Header", "items": ["..."]},
        {"title": "Case Risk Snapshot｜异常发生时（风险快照）", "items": ["..."]}
      ]},
      {"title": "当前阶段对话", "sections": [
        {"title": "系统 / 用户触发", "items": ["..."]},
        {"title": "Agent 接管", "items": ["..."]},
        {"title": "Agent 思考过程", "items": ["..."]},
        {"title": "Agent 分析计划", "items": ["..."]},
        {"title": "数据 / 工具调用", "items": [{"label": "MES / WIP Profile", "value": "Actual WIP = ...", "status": "Done"}, {"label": "Planning Config", "value": "Target WIP = ...", "status": "Done"}, {"label": "BI Trend", "value": "WIP ...", "status": "Done"}]},
        {"title": "Agent 观察结果", "items": ["..."]},
        {"title": "Agent 分析判断", "items": ["..."]},
        {"title": "Agent 阶段输出", "items": ["..."]},
        {"title": "AI Agent", "items": ["..."]}
      ]},
      {"title": "当前阶段结果", "sections": [
        {"title": "业务结果", "items": ["..."]},
        {"title": "本阶段结论", "items": ["..."]},
        {"title": "Agent 判断逻辑", "items": ["..."]},
        {"title": "状态与门禁", "items": ["..."]},
        {"title": "关键证据", "items": ["..."]}
      ]}
    ]
  }
}
```

## content 结构

`content.title` 固定为 `01 异常发现`。

`content.containers` 固定包含 3 个一级容器，顺序固定：

1. `WIP Case Snapshot`
2. `当前阶段对话`
3. `当前阶段结果`

每个容器下使用 `sections` 表示三级标题内容，前端直接循环渲染。最终 JSON 必须一次性输出 3 个容器；只输出 `WIP Case Snapshot` 或缺少任意 section 都是不合格结果。

```json
{
  "title": "WIP Case Snapshot",
  "sections": [
    {
      "title": "Case Header",
      "items": [
        {"label": "Case ID", "value": "..."}
      ]
    }
  ]
}
```

## WIP Case Snapshot JSON

`WIP Case Snapshot` 容器只允许两个 section：

- `Case Header`
- `Case Risk Snapshot｜异常发生时（风险快照）`

示例：

```json
{
  "title": "WIP Case Snapshot",
  "sections": [
    {
      "title": "Case Header",
      "items": [
        {"label": "Case ID", "value": "..."},
        {"label": "Priority", "value": "P1"},
        {"label": "Object", "value": "DNW-ANN Stage"},
        {"label": "Case Type", "value": "严重 WIP Bubble"},
        {"label": "Occur Time", "value": "..."},
        {"label": "Operator", "value": "Wang Fei"},
        {"label": "Current Stage", "value": "01 异常发现"},
        {"label": "Case Age", "value": "3.5h"},
        {"label": "Stage Elapsed", "value": "22min"},
        {"label": "SLA Remaining", "value": "18min"},
        {"label": "Owner", "value": "MFG / Case Owner"},
        {"label": "Status", "value": "Processing"}
      ]
    },
    {
      "title": "Case Risk Snapshot｜异常发生时（风险快照）",
      "items": [
        {"label": "WIP", "value": "Actual 8,050 / Target 258"},
        {"label": "Queue", "value": "8,000 / 99.4%"},
        {"label": "Eligible Tool", "value": "2 / 8", "meta": "92% Tool Uptime"},
        {"label": "Move-Out", "value": "73% Plan", "meta": "Gap -320"},
        {"label": "Q-Time", "value": "High", "meta": "Min Remain 1.8h"},
        {"label": "Downstream", "value": "Next Stage = <next_stage_name>", "meta": "Status = <if_starved>"}
      ]
    }
  ]
}
```

## 当前阶段对话 JSON

固定 9 个 section，顺序必须与 Markdown 一致；`系统 / 用户触发` 的内容必须按系统监控自动触发书写，只描述监控事件和异常对象：

```json
{
  "title": "当前阶段对话",
  "sections": [
    {"title": "系统 / 用户触发", "items": ["..."]},
    {"title": "Agent 接管", "items": ["..."]},
    {"title": "Agent 思考过程", "items": ["..."]},
    {"title": "Agent 分析计划", "items": ["..."]},
    {"title": "数据 / 工具调用", "items": [{"label": "MES / WIP Profile", "value": "Actual WIP = ...", "status": "Done"}, {"label": "Planning Config", "value": "Target WIP = ...", "status": "Done"}, {"label": "BI Trend", "value": "WIP ...", "status": "Done"}]},
    {"title": "Agent 观察结果", "items": ["..."]},
    {"title": "Agent 分析判断", "items": ["..."]},
    {"title": "Agent 阶段输出", "items": ["..."]},
    {"title": "AI Agent", "items": ["..."]}
  ]
}
```

## 当前阶段结果 JSON

固定 5 个 section，顺序必须与 Markdown 一致：

```json
{
  "title": "当前阶段结果",
  "sections": [
    {"title": "业务结果", "items": ["..."]},
    {"title": "本阶段结论", "items": ["..."]},
    {"title": "Agent 判断逻辑", "items": ["..."]},
    {"title": "状态与门禁", "items": ["..."]},
    {"title": "关键证据", "items": ["..."]}
  ]
}
```

## items 规则

`数据 / 工具调用` 的 items 必须是事实型数据结果，不是单纯工具状态；允许附带 `Done` 状态；禁止只有 `Done` / `Pending`，也禁止出现内部表名或 `mock` 字样。`items` 必须是非空数组，空数组无效；可以使用两种形态：

- 简单字符串：适合自然语言说明。
- `{label, value, meta, tone}` 对象：适合指标展示。

字段说明：

- `label`：指标名或字段名。
- `value`：展示值。
- `meta`：可选补充信息。
- `tone`：可选，`risk | warn | good | neutral`。

Downstream 必须来自 `case_snapshot.snapshot_inputs.downstream_starvation` 的 SQL 原始字段：`next_stage_name`、`actual_wip`、`target_wip`、`wip_ratio`、`if_starved`；不要把 stage 名和状态拼成固定短语；`Clean` 只是示例 stage name，真实值必须来自 SQL。SQL 和 mock 都没有的数据不要输出占位项。

## JSON 输出前自检

最终 JSON 必须确认：

- 顶层没有 `frontend_demo`。
- 顶层没有 `frontend_payload`。
- 顶层没有 `model_context`、`case_snapshot`、`prompt`、`output_contract`。
- `content.containers` 恰好 3 个。
- `WIP Case Snapshot.sections` 恰好 2 个。
- `当前阶段对话.sections` 恰好 9 个。
- `当前阶段结果.sections` 恰好 5 个。
- 三个容器都必须有实际 `items`；不要只填第一个容器。










