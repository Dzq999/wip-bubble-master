## 渐进式披露

路由到本 Flow 后，只按需读取本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；禁止预加载兄弟 Flow 或根目录的 Flow 模板。前序事实只从已保存的 `content` / `text` 与 `case_data_snapshot.sql_results` 获取。完整规则见 [渐进式披露规则](../../references/progressive-disclosure.md)。

## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。

# WIP llow 06   异常原因排查

llow 06 是 WIP Bubble SOP 的“异常原因排查”内部模块。它在 llow 05 完成 Case 分级与处置判定后执行，用于结合前序保存的 `content` 和 llow 06 SQL 查询结果，生成候选原因排序、证据链和待补证据。

## 职责边界

  复用 llow 01/02/03/04/05 的保存结果，只读取每条记录 `flow_data_json.content` 下的展示内容。
  查询 llow 06 所需 SQL 数据：Hold / Run WIP、Tool Status、Tool OE / AE、Move In Trend、Move Out Trend。
  输出“候选原因 / 初判原因”，并说明支持证据、排除证据、缺失证据和建议验证动作。
  不宣布最终根因已经确认，不关闭 Case，不派发工程任务。
  若证据不足，只能给出低置信度候选和补证要求。

## 数据来源

  `internal/wip data query/sql/locate_wip_hold_run.sql`
  `internal/wip data query/sql/locate_tool_status.sql`
  `internal/wip data query/sql/locate_tool_efficiency.sql`
  `internal/wip data query/sql/locate_tool_efficiency_detail.sql`
  `internal/wip data query/sql/locate_move_in_trend.sql`
  `internal/wip data query/sql/locate_move_out_trend.sql`

果果本地 MySQL 缺少表或本地数据，`query_data.py` 会按最小本地数据集补齐后重查。

## 执行方式

```bash
python internal/wip flow 06 root cause analysis/scripts/run_flow06.py   case id <case_id>   emit model context
```

当模型已生成完整 `model_output_json` 后：

```bash
python internal/wip flow 06 root cause analysis/scripts/run_flow06.py \
    case id <case_id> \
    previous record json @previous_records.json \
    model output json <inline-json>
```

脚本只负责准备上下文、校验输出、保存 llow 06 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：`locate_wip_hold_run`、`locate_tool_status`、`locate_tool_efficiency`、`locate_tool_dispatch`、`locate_product_tool_profile`、`locate_move_in_trend`、`locate_move_out_trend`。Tool Uptime 与 Tool Run Rate 均取 `locate_tool_efficiency.oe_ratio`。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。


