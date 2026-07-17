# 运行时事实来源规则

本文件是所有 WIP Flow 生成最终回答时的唯一事实来源约束。

## 固定执行路径

1. 调用目标 Flow 脚本，取得该脚本返回的 `model_context`。
2. 只从 `model_context.raw_inputs` 提取本轮事实：
   - `case_data_snapshot.sql_results` 中的一次性 SQL 结果；
   - 前序 Flow 已生成的 `content` / `text`；
   - 当前 Flow 实际存在的 `*_mock` / `*_inputs` 补充数据；
   - Flow 01 还可读取 `raw_inputs.snapshot_mock`。
3. 依据这些事实生成完整 `text` 和 `content`。补充数据按业务名称表述，对外不得出现 `mock`。
4. 每个要输出的具体对象、数值、时长、人员、状态和结论都必须能回溯到上述某个字段；没有来源就省略，或明确写“当前数据不足以判断”。

## 明确禁止

- 禁止在运行时读取或使用 `examples/` 中任何文本、数值、对象名或示例结论。
- 禁止把 `examples/`、output contract、prompt 中的示例当作事实来源。
- 禁止根据常识、历史案例或示例补造业务数值、人员、时长、stage、批次数、风险状态或恢复结果。
- 禁止在 `raw_inputs` 缺字段时输出占位业务事实。

`examples/` 只用于检查 JSON 形状和容器层级，所有示例内容均为模板，不参与运行。

## 对外措辞

最终 `text` 与 `content` 只陈述本轮业务事实、判断和处置；禁止出现实现、展示、测试或内部上下文用语，也不得把规则来源表述为业务依据。
