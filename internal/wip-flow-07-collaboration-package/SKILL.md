## 运行时事实路径（最高优先级）

最终回答只可依据 `model_context.raw_inputs`，按下面顺序执行：

1. 读取 `case_data_snapshot.sql_results` 中的一次性 SQL 事实，以及 `raw_inputs` 中携带的前序 Flow `content` / `text`。
2. 读取当前 Flow `raw_inputs` 内实际存在的 `*_mock`、`*_inputs` 补充数据；Flow 01 还必须读取 `raw_inputs.snapshot_mock`。键可增删，直接按本轮实际数据使用，不维护固定字段清单。
3. 对每个输出的具体对象、数值、人员、时长、状态或恢复结论做来源核对：没有上述来源就省略，或写“当前数据不足以判断”。

`examples/`、output-contracts 和 prompt 只能参考 JSON/Markdown 结构，运行时禁止读取或复用其中的任何业务数据或结论。完整约束见 [运行时事实来源规则](../../references/runtime-fact-policy.md)。

# WIP Flow 07 - 工程问题包与协同任务


Flow 07 是 WIP Bubble SOP 的“工程问题包与协同任务”内部模块。它在 Flow 06 完成异常原因候选排查后执行，把候选原因、影响范围、临时措施和分级处置路径组织成一个可协同推进的问题包与角色任务清单。

## 职责边界

- 复用 Flow 01/02/03/04/05/06 的保存结果，只读取每条记录 `flow_data_json.content` 下的展示内容。
- 输出工程问题包摘要、任务拆分、角色主责/协同、SLA、恢复指标、反馈要求和进入 Flow 08 的门禁。
- 可以生成“协同任务建议 / 待派发任务清单”，但不能声称已经真实调用外部系统派单、通知或完成处置。
- 不重新确认异常是否成立，不重新做影响范围评估，不宣布最终根因已确认，不判断处置已经生效。
- 若 Flow 06 未给出可用候选原因或缺少必要证据，只能输出 On Hold 和补证要求。

## 输入来源

- 前序 Flow 记录：Flow 01 至 Flow 06 的 `flow_data_json.content`。
- Flow 07 内部补充规则：`data/flow07_mock.json` 中的角色矩阵、任务模板和门禁要求。

## 执行方式

```bash
python internal/wip-flow-07-collaboration-package/scripts/run_flow07.py --case-id <case_id> --emit-model-context
```

当模型已生成完整 `model_output_json` 后：

```bash
python internal/wip-flow-07-collaboration-package/scripts/run_flow07.py \
  --case-id <case_id> \
  --previous-record-json @previous_records.json \
  --model-output-json <inline-json>
```

脚本只负责准备上下文、校验输出、保存 Flow 07 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。

## SQL 快照引用
本 Flow 只从 Flow 01 保存的 `case_data_snapshot.sql_results` 读取 SQL 事实；重点参考：Flow 06 使用的 `sql_results` 原始事实及其候选原因结论。SQL 与本 Flow 补充 mock 都没有的字段必须省略，`examples/` 和 output-contracts 仅用于结构校验，禁止作为数值来源。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

