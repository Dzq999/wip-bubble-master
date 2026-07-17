## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。

## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。

# WIP Flow 10 - Case 关闭确认


Flow 10 是 WIP Bubble SOP 的“Case 关闭确认”内部模块。它在 Flow 09 影响消除观察通过后执行，用于确认关闭条件是否满足：任务完成、风险解除、指标恢复、受控动作关闭、责任人确认。

## 职责边界

- 默认假设 Flow 09 的影响消除观察通过，且本阶段关闭确认通过。
- 只做关闭条件确认和进入 Flow 11 复盘沉淀的门禁判断。
- 必须覆盖任务完成、风险解除、恢复指标、临时控制关闭、责任人确认。
- 正常预置进入 Flow 11 `Case 复盘沉淀`；只有输入明确任务未完成、风险未解除、指标未恢复、受控动作未关闭或责任人未确认时，才保持 On Hold。
- `WIP Case Snapshot` 仍然只有两段：`Case Header` 和 `Case Closure Checklist｜关闭确认`。
- 不做复盘沉淀，不写已完成案例沉淀，不确认最终根因。

## 必读文件

- Flow 10 Prompt：`prompts/flow10_result_prompt.md`
- 输出契约：`output-contracts/flow10-text-output-contract.md`、`output-contracts/flow10-json-output-contract.md`
- Flow 10 业务规则：`knowledge/flow10-business-rules.md`
- Flow 10 内部补充规则：`data/flow10_mock.json`

## 脚本

生成模型上下文：

```bash
python internal/wip-flow-10-closure-confirmation/scripts/run_flow10.py --case-id <case_id> --emit-model-context
```

校验并保存当前 Agent 生成的最终 JSON：

```bash
python internal/wip-flow-10-closure-confirmation/scripts/run_flow10.py \
  --case-id <case_id> \
  --previous-record-json @previous_records.json \
  --model-output-json <inline-json>
```

脚本只负责准备上下文、校验输出、保存 Flow 10 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：原始 `sql_results` 与 Flow 08/09 的恢复和观察结果。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

