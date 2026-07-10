---
name: wip-flow-03-containment
description: WIP Bubble SOP 的 Flow 03 内部模块。用于“临时措施”：复用 Flow 02 保存结果，在根因完全确认前生成局部、可控、可回退的风险遏制动作，保护 Hot Lot / Super Hot Run、控制非关键 Move-In、通知下游并避免不必要的全量 Hold。
---

# WIP Flow 03 - 临时措施

本模块只实现 SOP Flow 03。目标是在异常已经成立、但根因尚未完全确认前，先控制生产风险，避免 Q-Time、Hot Lot、Super Hot Run、下游供料和 Move-In 风险继续扩大。

## 设计原则

- 优先读取一个或多个前序 Flow 保存结果的 `content`，并复用其中的 `content.containers` 与 WIP Case Snapshot；不要把前序全文 `text` 放进模型上下文。
- Flow 03 不重新执行 `wip-case-snapshot`，也不做最终根因排查。
- Python 只准备上下文、校验模型输出和保存结果；不构造最终文本、前端容器或业务结论。
- 临时措施必须是局部、可控、可回退的建议、通知或草案；高风险生产动作不能被写成 Agent 已直接操作主系统。
- 最终展示禁止出现 `mock`、`model_context`、`prompt`、stdout 等内部信息。
- 示例只参考结构，正文必须由当前 Agent 根据本次上下文生成。

## 输出契约

执行前读取：

```text
output-contracts/flow03-text-output-contract.md
output-contracts/flow03-json-output-contract.md
```

Flow 03 输出仍使用三块主容器：

- `WIP Case Snapshot`：复用前序快照，必要时仅更新 Current Stage / Status。
- `当前阶段对话`：固定 9 个 section。
- `当前阶段结果`：固定 5 个 section。

## Prompt

```text
prompts/flow03_result_prompt.md
```

## 数据来源

- 一个或多个前序 Flow：从 `vfab_agent.fab_case_flow_record.flow_data_json` 中只提取 `content` 和少量流程元数据。
- Flow 03 SQL 数据：Hot Lot / Super Hot Run 数量来自 `locate_flow03_priority_lots.sql`；下游 stage 与 starvation 来自 `locate_downstream_starvation.sql`。如果本地 `aifab` 表或 demo 数据缺失，数据层会补齐最小可运行数据。
- Flow 03 补充数据：仅补充 SQL 和前序 `content` 都没有的数据，如 Move-In 控制建议、Hold 建议、回退条件等；下游通知对象优先来自 SQL 查询结果，SQL 无结果时继承前序 Downstream / Next Stage。
- 后续 Flow 04 才量化影响范围；Flow 03 只输出短期风险控制动作和门禁。

## 脚本调用

生成上下文：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-03-containment/scripts/run_flow03.py --case-id <uuid> --previous-record-json @tmp/flow02_record.json --emit-model-context
```

校验并保存模型结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-03-containment/scripts/run_flow03.py --case-id <uuid> --previous-record-json @tmp/flow02_record.json --model-output-json @examples/flow-03/model-output.json --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-03-containment/scripts/run_flow03.py --case-id <uuid> --previous-record-json @tmp/flow02_record.json --model-output-json @examples/flow-03/model-output.json --return-type json
```
