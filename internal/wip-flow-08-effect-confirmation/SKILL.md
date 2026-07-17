## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。

## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。

# WIP Flow 08 - 处置效果确认


Flow 08 是 WIP Bubble SOP 的“处置效果确认”内部模块。它在 Flow 07 生成跨部门协同处置后执行，用于判断协同处置是否已经具备初步效果证据，是否需要回退/升级，或是否可以进入 Flow 09 影响消除观察。

## 职责边界

- 复用 Flow 01/02/03/04/05/06/07 的保存结果，只读取每条记录 `flow_data_json.content` 下的展示内容。
- 默认假设 Flow 07 协同处置反馈已返回并完成初步确认；检查 SLA、恢复指标和门禁是否具备进入观察的证据。
- 输出效果确认状态：有效、部分有效、未确认、需回退/升级或证据不足。
- 正常预置进入 Flow 09；只有输入明确缺少反馈、缺少恢复指标或指标仍恶化时，才保持 On Hold。
- Flow 08 的 `WIP Case Snapshot` 仍然只有两段：`Case Header` 和 `Case Risk Trend｜处置后（恢复趋势）`；`Case Risk Trend` 替代前序 Flow 的 `Case Risk Snapshot`。
- 动态生成 `Case Risk Trend｜处置后（恢复趋势）`：只对前序异常指标 mock 恢复值，原本不异常的指标保持原值。
- 不宣布异常已完全恢复，不关闭 Case，不做复盘沉淀。

## 输入来源

- 前序 Flow 记录：Flow 01 至 Flow 07 的 `flow_data_json.content`。
- Flow 08 内部补充规则：`data/flow08_mock.json` 中的效果确认维度、证据要求和门禁规则。

## 执行方式

```bash
python internal/wip-flow-08-effect-confirmation/scripts/run_flow08.py --case-id <case_id> --emit-model-context
```

当模型已生成完整 `model_output_json` 后：

```bash
python internal/wip-flow-08-effect-confirmation/scripts/run_flow08.py \
  --case-id <case_id> \
  --previous-record-json @previous_records.json \
  --model-output-json <inline-json>
```

脚本只负责准备上下文、校验输出、保存 Flow 08 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：`locate_high_wip_stage`、`locate_downstream_starvation`、`locate_move_out_trend`，并与本阶段生成的恢复趋势对照。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

