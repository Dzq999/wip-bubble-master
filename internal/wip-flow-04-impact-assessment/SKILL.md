---
name: wip-flow-04-impact-assessment
description: WIP Bubble SOP 的 Flow 04 内部模块。用于“影响范围评估”：复用 Flow 01/02/03 保存结果，在临时措施后量化 Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out Gap 和下游供料，判断是否超过单点波动，为 Flow 05 Case 分级与处置判定提供依据。
---

# WIP Flow 04 - 影响范围评估

本模块只实现 SOP Flow 04。目标是在临时措施已生成或已执行后，基于前端 demo 已有指标量化影响范围，判断风险是否已经从单个 Stage 的 WIP Bubble 扩散到 Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out Gap 或下游供料。

## 设计原则

- 优先读取一个或多个前序 Flow 保存结果的 `content`，并复用其中的 `content.containers` 与 WIP Case Snapshot；不要把前序全文 `text` 放进模型上下文。
- Flow 04 不重新执行 `wip-case-snapshot`，不做最终根因排查，不做正式 Case 分级，不派发工程问题包。
- Python 只准备上下文、校验模型输出和保存结果；不构造最终文本、前端容器或业务结论。
- 影响评估只能覆盖前端 demo 已有的 Impact Lot / Impact WO / Hot Lot / Super Hot Run / Q-Time / Move-Out Gap / 下游供料字段；缺失字段可以省略，但不能输出占位值。
- 最终展示禁止出现 `mock`、`model_context`、`prompt`、stdout 等内部信息。
- 示例只参考结构，正文必须由当前 Agent 根据本次上下文生成。

## 输出契约

执行前读取：

```text
output-contracts/flow04-text-output-contract.md
output-contracts/flow04-json-output-contract.md
```

Flow 04 输出仍使用三块主容器：

- `WIP Case Snapshot`：复用前序快照，必要时仅更新 Current Stage / Status。
- `当前阶段对话`：固定 9 个 section。
- `当前阶段结果`：固定 5 个 section。

## Prompt

```text
prompts/flow04_result_prompt.md
```

## 数据来源

- 一个或多个前序 Flow：从 `vfab_agent.fab_case_flow_record.flow_data_json` 中只提取 `content` 和少量流程元数据。
- Flow 04 补充数据：仅补充 SQL 和前序 `content` 都没有的前端 demo 已有字段，如 Impact Lot、Impact WO、Hot Lot、Super Hot Run、Q-Time Risk、Move-Out Gap 和下游 Starvation。
- 后续 Flow 05 才进行 Case 分级与处置判定；Flow 04 只输出影响范围、风险扩散判断和进入分级的门禁依据。

## 脚本调用

生成上下文：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-04-impact-assessment/scripts/run_flow04.py --case-id <uuid> --previous-record-json @tmp/previous_records.json --emit-model-context
```

校验并保存模型结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-04-impact-assessment/scripts/run_flow04.py --case-id <uuid> --previous-record-json @tmp/previous_records.json --model-output-json @examples/flow-04/model-output.json --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-04-impact-assessment/scripts/run_flow04.py --case-id <uuid> --previous-record-json @tmp/previous_records.json --model-output-json @examples/flow-04/model-output.json --return-type json
```
