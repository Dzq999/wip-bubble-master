---
name: wip-flow-05-case-classification
description: WIP Bubble SOP 的 Flow 05 内部模块。用于“Case 分级与处置判定”：复用 Flow 01/02/03/04 保存结果，根据影响范围、优先级批次、Q-Time、Move-Out 和下游供料风险判定 Case Level、处置路径、初始主责和进入 Flow 06 的门禁。
---

# WIP Flow 05 - Case 分级与处置判定

本模块只实现 SOP Flow 05。目标是在影响范围评估完成后，基于前序已保存的 `content` 判断 Case 等级、处置路径、初始主责与升级门禁，为 Flow 06 异常原因排查提供分级后的调查边界。

## 设计原则

- 优先读取一个或多个前序 Flow 保存结果的 `content`，并复用其中的 `content.containers` 与 WIP Case Snapshot；不要把前序全文 `text` 放进模型上下文。
- Flow 05 不重新执行 `wip-case-snapshot`，不做最终根因排查，不输出原因候选排序，不派发工程问题包。
- Python 只准备上下文、校验模型输出和保存结果；不构造最终文本、前端容器或业务结论。
- Case 分级只能基于前端 demo / 前序 content 已有字段，例如 Impact Lot / WO、Hot Lot / Super Hot Run、Q-Time Risk、Move-Out、下游 Starvation、临时措施状态。
- 最终展示禁止出现 `mock`、`model_context`、`prompt`、stdout 等内部信息。
- 示例只参考结构，正文必须由当前 Agent 根据本次上下文生成。

## 输出契约

执行前读取：

```text
output-contracts/flow05-text-output-contract.md
output-contracts/flow05-json-output-contract.md
```

Flow 05 输出仍使用三块主容器：

- `WIP Case Snapshot`：复用前序快照，必要时仅更新 Current Stage / Status。
- `当前阶段对话`：固定 9 个 section。
- `当前阶段结果`：固定 5 个 section。

## Prompt

```text
prompts/flow05_result_prompt.md
```

## 数据来源

- 一个或多个前序 Flow：从 `vfab_agent.fab_case_flow_record.flow_data_json` 中只提取 `content` 和少量流程元数据。
- Flow 05 补充数据：仅补充分级矩阵、处置路径、初始主责、升级门禁等前序 `content` 没有的 demo 规则。
- 后续 Flow 06 才进行异常原因排查；Flow 05 只输出 Case 分级与处置判定。

## 脚本调用

生成上下文：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-05-case-classification/scripts/run_flow05.py --case-id <uuid> --previous-record-json @tmp/previous_records.json --emit-model-context
```

校验并保存模型结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-05-case-classification/scripts/run_flow05.py --case-id <uuid> --previous-record-json @tmp/previous_records.json --model-output-json @examples/flow-05/model-output.json --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-05-case-classification/scripts/run_flow05.py --case-id <uuid> --previous-record-json @tmp/previous_records.json --model-output-json @examples/flow-05/model-output.json --return-type json
```
