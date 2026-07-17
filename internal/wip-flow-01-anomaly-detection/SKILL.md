---
name: wip-flow-01-anomaly-detection
description: WIP Bubble SOP 的 Flow 01 内部模块。仅用于第一个流程“异常发现”：查询或接收 WIP stage 原始数据，读取必要 mock 和知识库，由当前 Agent 生成结构化 JSON 与人工可读文本，并用 Python 做 JSON 修复和结果保存。
---

## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. `raw_inputs.wip_case_snapshot` 非空时，原样使用为最终结果的第一个容器；字段增删和来源由 `wip-case-snapshot/output-contracts/snapshot-display-schema.md` 控制。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。






## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。

# WIP Flow 01 - 异常发现


本内部模块只实现 SOP 的 Flow 01。

## 设计原则

Flow 01 不应由 Python 固定拼接大量分析话术。Python 只负责确定性工作：

- 查询或接收当前最高 WIP 的业务 stage 原始数据。
- 读取 Flow 01 所需 mock 数据；mock 只存放暂时查不到的数据，不存放固定展示文案。最终展示禁止出现 `mock` 字样，内部 mock 数据必须转成业务化数据来源表述。
- 只在当前 Agent 已拿到 SQL 原始结果并显式传入所需数据时，执行确定性计算；脚本不得自行查询 SQL 后直接产出判断结论。
- 构建 `model_context`，并读取外层 `knowledge/*.md`、本 Flow 的 `knowledge/*.md` 和 `prompts/flow01_result_prompt.md`。
- 解析/修复模型返回 JSON，剔除空值并保存模型结果到 `vfab_agent.fab_case_flow_record`。
- 不在 Python 中硬编码最终文本话术、展示容器内容或业务分析结论。

分析表达、展示层结构化内容和用户可读 Markdown 应由当前 Agent 结合 `model_context.raw_inputs` 与知识库生成。示例输入输出只作为结构参考，正文表述不能原文照抄。

## 知识库

通用工厂异常处理背景放在外层：

```text
knowledge/factory-exception-process.md
```

Flow 01 专属知识放在本模块：

```text
internal/wip-flow-01-anomaly-detection/knowledge/flow01-business-rules.md
```

加载进 `model_context.knowledge_pack` 时会带上 `scope`：

- `scope=global`：外层通用知识。
- `scope=flow`：当前 Flow 专属知识。

后续新增 Flow 02-11 时，每个 Flow 都应维护自己的 `knowledge/`，只存放本流程业务规则、判断条件、角色口径和输出约束；通用大背景继续放在外层 `knowledge/`。


## 输出契约

Flow 01 的最终回答格式要求拆分维护在：

```text
output-contracts/flow01-text-output-contract.md
output-contracts/flow01-json-output-contract.md
```

执行本子 skill 时，当前 Agent 必须读取并同时遵守这两个文件。`SKILL.md` 中的格式摘要、prompt 和示例都不能替代输出契约；如有冲突，以 `output-contracts/flow01-text-output-contract.md` 与 `output-contracts/flow01-json-output-contract.md` 为准。

该契约逐段说明：

- `WIP Case Snapshot` 只包含 `Case Header` 与 `Case Risk Snapshot｜异常发生时（风险快照）`。
- `当前阶段对话` 必须包含 9 个子段，并与轻量 JSON 中 `当前阶段对话.sections` 对齐。
- `当前阶段结果` 必须包含业务结果、结论、判断逻辑、状态门禁、关键证据。
- 结构化结果必须是轻量 JSON，使用 `content.containers[].sections[].items[]` 覆盖 Markdown 内容。
## Prompt

模型生成模板放在：

```text
prompts/flow01_result_prompt.md
```

当前 Agent 必须先读取两个输出契约文件，再按 Prompt 输出一个轻量 JSON 对象，包含：

- `text`：面向用户直接阅读的 Markdown 文本。
- `content`：面向展示层循环渲染的轻量结构化 JSON。

不要输出 Markdown 代码围栏；详细输出格式见 `output-contracts/flow01-text-output-contract.md` 和 `output-contracts/flow01-json-output-contract.md`。如果模型输出不规范，Python 会尝试提取和修复 JSON。

## 输入输出示例

示例放在外层：

```text
examples/model-context-input.json
examples/model-output.json
```

这两个文件用于说明 Flow 01 输入上下文和输出结构，不参与运行。其中 `examples/model-output.json` 同时对齐 `WIP Bubble` 展示层输入结构，包含 轻量 `content.containers[].sections[].items[]`，不要把它当作普通 mock 文本清理。

## 输入

```json
{
  "case_id": "由总控 Skill 生成的 UUID",
  "case_snapshot": "由 wip-case-snapshot 生成的结构化快照，可选",
  "high_wip": "当前最高 WIP stage 数据，可选",
  "model_output": "模型按 prompt 生成的 JSON，可选"
}
```

`case_id` 是 Agent 运行态 UUID，保存在 `vfab_agent.fab_case_flow_record`。总控 Skill 调用内部 Flow 时只传业务上下文，不要把默认 `return_type` 传入内部 Flow。`return_type` 仅用于脚本本地调试时控制打印格式。

## 数据来源

调用内部 `wip-data-query` 模块，从以下数仓表定位当前最高 WIP 的业务 stage：

- `aifab.dim_wip_lot_rt`
- `aifab.dim_wip_target`

执行 Flow 01 前，总控 Skill 会通过 `wip-data-query.collect_case_data_snapshot` 一次性查询白名单 SQL；`wip-case-snapshot` 再从 `case_data_snapshot.sql_results` 生成结构化 `WIP Case Snapshot`。Flow 01 直接使用该容器，不再自行拼接 Header 或风险快照。

## WIP 状态判断规则

```text
Actual WIP <= Target WIP               ：正常
Target WIP < Actual WIP <= Warning WIP ：正常偏高
Warning WIP < Actual WIP <= UCL WIP    ：预警
UCL WIP < Actual WIP <= Severe UCL WIP ：WIP Bubble
Actual WIP > Severe UCL WIP            ：严重 WIP Bubble
Target WIP 缺失或 <= 0                 ：Target 缺失
```

阈值计算：

```text
Warning WIP = Target WIP * 1.2
UCL WIP = Target WIP * 1.5
Severe UCL WIP = Target WIP * 2.0
```

只有 `bubble_status` 为 `WIP Bubble` 或 `严重 WIP Bubble` 时，才设置 `next_flow_no=02` 并等待 Case Owner / MFG / Shift 确认是否进入 Flow 02。未查询到可进入异常确认的 stage 时，按 `未发现异常` 处理并关闭 Case。

无论是否继续后续流程，Flow 01 本身执行完成后都保存 `flow_status=Closed`。

## 展示容器输出

Flow 01 结果通过轻量 `content.containers` 表达三块展示容器：

- `WIP Case Snapshot`：右上 WIP Case Snapshot，只包含 `Case Header` 与 `Case Risk Snapshot｜异常发生时（风险快照）`。
- `当前阶段对话`：左侧当前阶段对话，固定 9 个 section。
- `当前阶段结果`：右侧当前阶段结果，固定 5 个 section。

当前 Agent 生成当前阶段对话和当前阶段结果；`WIP Case Snapshot` 由快照模块生成并在保存前原样写入。

## 输出约定

最终 Markdown 结构以 `output-contracts/flow01-text-output-contract.md` 为准；最终 JSON 结构以 `output-contracts/flow01-json-output-contract.md` 为准。最终返回 `text`、`json` 还是 `both`，由总控 Skill 根据 `return_type` 决定；默认返回 `text`。

如果没有传入模型结果，脚本只输出 `model_context`、Prompt 和必要数据。当前 Agent 自己就是生成者，必须继续依据这些内容生成最终 `text` 与轻量 `content`；不要把脚本中的中间态提示原文返回给用户。

执行规则：看到 `internal_only=true`、`reason=model_output_required`、`model_context`、`prompt` 或内部上下文时，不能结束回复，也不能把这些中间态或标准输出状态展示给用户；必须继续依据 `model_context.raw_inputs`、`output_contracts` 和 prompt 生成最终结果。生成 JSON 后必须先用 `--validate-only --model-output-json @<file>` 校验 `content` 完整性；校验不通过时先补全三大容器和所有 section，再输出或保存。如果需要落库，再把已通过校验的 JSON 作为 `--model-output-json` 传回脚本保存。

## 脚本调用

生成模型上下文，不保存 case；当前 Agent 随后必须自行生成最终结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-01-anomaly-detection/scripts/run_flow01.py --case-id <uuid> --emit-model-context
```

传入模型生成 JSON 并保存结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-01-anomaly-detection/scripts/run_flow01.py --case-id <uuid> --model-output-json <inline-json> --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-01-anomaly-detection/scripts/run_flow01.py --case-id <uuid> --model-output-json <inline-json> --return-type json
```

## Case Header 时间映射

Case Header 的 `Occur Time` 固定读取 `case_data_snapshot.sql_results.locate_high_wip_stage.update_time`。该值是异常对象 SQL 记录的更新时间；不得使用 `biz_time`、当前时间、快照采集时间或补充数据时间。`update_time` 缺失时省略该展示字段。

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：`locate_high_wip_stage`、`locate_downstream_starvation`。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

