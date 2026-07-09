---
name: wip-flow-02-anomaly-confirmation
description: WIP Bubble SOP 的 Flow 02 内部模块。用于“异常确认”：复用 Flow 01 保存结果，校验数据刷新、指标口径、Target 有效性、异常持续时间和重复 Case。
---

# WIP Flow 02 - 异常确认

本模块只实现 SOP Flow 02。目标是确认 Flow 01 发现的 WIP Bubble 是否为真实成立异常，排除数据刷新、口径错误、Target 无效、短时波动和重复 Case。

## 设计原则

- 优先读取 Flow 01 保存的 `flow_data_json`，尤其是其中的 `content.containers` 和 `WIP Case Snapshot`。
- Flow 02 不重新执行 `wip-case-snapshot`；只有前序结果拿不到的数据，才查询 SQL 或读取本 Flow 的 mock。
- Python 只准备上下文、校验模型输出和保存结果；不构造最终文本、前端容器或业务结论。
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
python .agents/skills/wip-bubble-master/internal/wip-flow-02-anomaly-confirmation/scripts/run_flow02.py --case-id <uuid> --previous-record-json @tmp/flow01_record.json --emit-model-context
```

校验并保存模型结果：

```bash
python .agents/skills/wip-bubble-master/internal/wip-flow-02-anomaly-confirmation/scripts/run_flow02.py --case-id <uuid> --previous-record-json @tmp/flow01_record.json --model-output-json @examples/flow-02/model-output.json --validate-only
python .agents/skills/wip-bubble-master/internal/wip-flow-02-anomaly-confirmation/scripts/run_flow02.py --case-id <uuid> --previous-record-json @tmp/flow01_record.json --model-output-json @examples/flow-02/model-output.json --return-type json
```
