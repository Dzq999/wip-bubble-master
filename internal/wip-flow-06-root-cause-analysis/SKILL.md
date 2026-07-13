# WIP Flow 06 - 异常原因排查

Flow 06 是 WIP Bubble SOP 的“异常原因排查”内部模块。它在 Flow 05 完成 Case 分级与处置判定后执行，用于结合前序保存的 `content` 和 Flow 06 SQL 查询结果，生成候选原因排序、证据链和待补证据。

## 职责边界

- 复用 Flow 01/02/03/04/05 的保存结果，只读取每条记录 `flow_data_json.content` 下的展示内容。
- 查询 Flow 06 所需 SQL 数据：Hold / Run WIP、Tool Status、Tool OE / AE、Move-In Trend、Move-Out Trend。
- 输出“候选原因 / 初判原因”，并说明支持证据、排除证据、缺失证据和建议验证动作。
- 不宣布最终根因已经确认，不关闭 Case，不派发工程任务。
- 若证据不足，只能给出低置信度候选和补证要求。

## 数据来源

- `internal/wip-data-query/sql/locate_flow06_wip_hold_run.sql`
- `internal/wip-data-query/sql/locate_flow06_tool_status.sql`
- `internal/wip-data-query/sql/locate_flow06_tool_efficiency.sql`
- `internal/wip-data-query/sql/locate_flow06_tool_efficiency_detail.sql`
- `internal/wip-data-query/sql/locate_flow06_move_in_trend.sql`
- `internal/wip-data-query/sql/locate_flow06_move_out_trend.sql`

如果本地 MySQL 缺少表或演示数据，`query_data.py` 会按最小 demo 数据集补齐后重查。

## 执行方式

```bash
python internal/wip-flow-06-root-cause-analysis/scripts/run_flow06.py --case-id <case_id> --emit-model-context
```

当模型已生成完整 `model_output_json` 后：

```bash
python internal/wip-flow-06-root-cause-analysis/scripts/run_flow06.py \
  --case-id <case_id> \
  --previous-record-json @previous_records.json \
  --model-output-json @flow06_model_output.json
```

脚本只负责准备上下文、校验输出、保存 Flow 06 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。
