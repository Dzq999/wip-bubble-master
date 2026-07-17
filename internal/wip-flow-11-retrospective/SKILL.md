## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。

## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。

# WIP Flow 11 - Case 复盘沉淀


Flow 11 是 WIP Bubble SOP 的最终“Case 复盘沉淀”内部模块。它在 Flow 10 关闭确认通过后执行，用于沉淀根因摘要、有效措施、无效或需改进措施、规则优化建议和案例标签，并关闭 Case。

## 职责边界

- 默认假设 Flow 10 已经完成 Case 关闭确认，本阶段复盘沉淀完成。
- 输出复盘沉淀结果，并将顶层 `case_status` 置为 `Closed`。
- 必须覆盖根因摘要、有效措施、无效或需改进措施、规则优化、案例标签和案例归档。
- 正常预置没有下一流程：`next_flow_no=null`、`next_flow_name=null`。
- `WIP Case Snapshot` 仍然只有两段：`Case Header` 和 `Case Retrospective Summary｜复盘沉淀`。
- 不输出新的处置动作，不重新开启 Case，不把沉淀内容写成新的现场指令。

## 必读文件

- Flow 11 Prompt：`prompts/flow11_result_prompt.md`
- 输出契约：`output-contracts/flow11-text-output-contract.md`、`output-contracts/flow11-json-output-contract.md`
- Flow 11 业务规则：`knowledge/flow11-business-rules.md`
- Flow 11 内部补充规则：`data/flow11_mock.json`

## 脚本

生成模型上下文：

```bash
python internal/wip-flow-11-retrospective/scripts/run_flow11.py --case-id <case_id> --emit-model-context
```

校验并保存当前 Agent 生成的最终 JSON：

```bash
python internal/wip-flow-11-retrospective/scripts/run_flow11.py \
  --case-id <case_id> \
  --previous-record-json @previous_records.json \
  --model-output-json <inline-json>
```

脚本只负责准备上下文、校验输出、保存 Flow 11 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：原始 `sql_results` 与 Flow 08 至 Flow 10 的恢复、观察和关闭结果。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

