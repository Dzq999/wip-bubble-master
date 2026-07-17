---
name: wip-flow-02-anomaly-confirmation
description: WIP Bubble SOP 的 Flow 02 内部模块。用于“异常确认”：复用 Flow 01 保存结果，校验数据刷新、指标口径、Target 有效性、异常持续时间和重复 Case。
---

## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。






## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。

# WIP Flow 02 - 异常确认


本模块只实现 SOP Flow 02。目标是确认 Flow 01 发现的 WIP Bubble 是否为真实成立异常，排除数据刷新、口径错误、Target 无效、短时波动和重复 Case。

## 设计原则

- 优先读取 Flow 01 保存的 `flow_data_json`，尤其是其中的 `content.containers` 和 `WIP Case Snapshot`。
- Flow 02 不重新执行 `wip-case-snapshot`；只有前序结果拿不到的数据，才查询 SQL 或读取本 Flow 的 mock。
- Python 只准备上下文、校验模型输出和保存结果；不构造最终文本、展示容器或业务结论。
- 最终展示禁止出现 `mock`、`model_context`、`prompt`、stdout 等内部信息。
- 示例只参考结构，正文必须由当前 Agent 根据本次上下文生成。

## 输出契约

执行前读取：

```text
output-contracts/flow02-text-output-contract.md
output-contracts/flow02-json-output-contract.md
```

Flow 02 输出仍使用三块主容器：

- `WIP Case Snapshot`：复用 Flow 01 快照，必要时仅更新 Current Stage / Status。
- `当前阶段对话`：固定 9 个 section。
- `当前阶段结果`：固定 5 个 section。

## Prompt

```text
prompts/flow02_result_prompt.md
```

## 数据来源

- 前序 Flow 01：`vfab_agent.fab_case_flow_record.flow_data_json`。
- Flow 02 mock：仅补充 SQL 和前序结果都没有的数据，如重复 Case 检查结果、默认确认规则、时间窗口说明等。
- 生产 SQL 参考：`生产环境当前高wip 的stage 定位及排查.md`。Flow 02 当前可直接使用 Flow 01 的 WIP Profile、Target、Queue、更新时间；无须重复查询 WIP Case Snapshot。

## 脚本调用

生成上下文：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-02-anomaly-confirmation/scripts/run_flow02.py --case-id <uuid> --previous-record-json <inline-json> --emit-model-context
```

校验并保存模型结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-02-anomaly-confirmation/scripts/run_flow02.py --case-id <uuid> --previous-record-json <inline-json> --model-output-json <inline-json> --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-02-anomaly-confirmation/scripts/run_flow02.py --case-id <uuid> --previous-record-json <inline-json> --model-output-json <inline-json> --return-type json
```

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：`locate_high_wip_stage`、`locate_downstream_starvation`。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

