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
  --model-output-json @flow07_model_output.json
```

脚本只负责准备上下文、校验输出、保存 Flow 07 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。
