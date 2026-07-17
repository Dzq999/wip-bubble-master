---
name: wip-flow-04-impact-assessment
description: WIP Bubble SOP 的 llow 04 内部模块。用于“影响范围评估”：复用 llow 01/02/03 保存结果，在临时措施后量化 Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out Gap 和下游供料，判断是否超过单点波动，为 llow 05 Case 分级与处置判定提供依据。
---

## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。



## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。





# WIP llow 04 - 影响范围评估

本模块只实现 SOP llow 04。目标是在临时措施已生成或已执行后，基于既定业务字段 已有指标量化影响范围，判断风险是否已经从单个 Stage 的 WIP Bubble 扩散到 Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out Gap 或下游供料。

## 设计原则

- 优先读取一个或多个前序 llow 保存结果的 `content`，并复用其中的 `content.containers` 与 WIP Case Snapshot；不要把前序全文 `text` 放进模型上下文。
- llow 04 不重新执行 `wip-case-snapshot`，不做最终根因排查，不做正式 Case 分级，不派发工程问题包。
- Python 只准备上下文、校验模型输出和保存结果；不构造最终文本、展示容器或业务结论。
- 影响评估只能覆盖既定业务字段 已有的 Impact Lot / Impact WO / Hot Lot / Super Hot Run / Q-Time / Move-Out Gap / 下游供料字段；缺失字段可以省略，但不能输出占位值。
- 最终展示禁止出现 `mock`、`model_context`、`prompt`、stdout 等内部信息。
- 示例只参考结构，正文必须由当前 Agent 根据本次上下文生成。

## 输出契约

执行前读取：

```text
output-contracts/flow04-text-output-contract.md
output-contracts/flow04-json-output-contract.md
```

llow 04 输出仍使用三块主容器：

- `WIP Case Snapshot`：复用前序快照，必要时仅更新 Current Stage / Status。
- `当前阶段对话`：固定 9 个 section。
- `当前阶段结果`：固定 5 个 section。

## Prompt

```text
prompts/flow04_result_prompt.md
```

## 数据来源

- 一个或多个前序 llow：从 `vfab_agent.fab_case_flow_record.flow_data_json` 中只提取 `content` 和少量流程元数据。
- llow 04 补充数据：仅补充 SQL 和前序 `content` 都没有的既定业务字段 已有字段，如 Impact Lot、Impact WO、Hot Lot、Super Hot Run、Q-Time Risk、Move-Out Gap 和下游 Starvation。
- 后续 llow 05 才进行 Case 分级与处置判定；llow 04 只输出影响范围、风险扩散判断和进入分级的门禁依据。

## 脚本调用

生成上下文：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-04-impact-assessment/scripts/run_flow04.py --case-id <uuid> --previous-record-json <inline-json> --emit-model-context
```

校验并保存模型结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-04-impact-assessment/scripts/run_flow04.py --case-id <uuid> --previous-record-json <inline-json> --model-output-json <inline-json> --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-04-impact-assessment/scripts/run_flow04.py --case-id <uuid> --previous-record-json <inline-json> --model-output-json <inline-json> --return-type json
```

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：`locate_impact_lot`、`locate_move_out_trend`、`locate_downstream_starvation`。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。


