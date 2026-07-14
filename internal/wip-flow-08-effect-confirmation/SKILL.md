# WIP Flow 08 - 处置效果确认

Flow 08 是 WIP Bubble SOP 的“处置效果确认”内部模块。它在 Flow 07 生成工程问题包与协同任务后执行，用于判断协同处置是否已经具备初步效果证据，是否需要回退/升级，或是否可以进入 Flow 09 影响消除观察。

## 职责边界

- 复用 Flow 01/02/03/04/05/06/07 的保存结果，只读取每条记录 `flow_data_json.content` 下的展示内容。
- 检查 Flow 07 定义的角色反馈、SLA、恢复指标和门禁是否具备可验证证据。
- 输出效果确认状态：有效、部分有效、未确认、需回退/升级或证据不足。
- 正常进入 Flow 09 的前提是存在足够的初步恢复证据；否则保持 On Hold，要求补齐角色反馈或恢复指标。
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
  --model-output-json @flow08_model_output.json
```

脚本只负责准备上下文、校验输出、保存 Flow 08 记录。最终展示内容必须由当前 Agent 基于 `model_context` 生成，保存成功后再返回同一份新结果。
