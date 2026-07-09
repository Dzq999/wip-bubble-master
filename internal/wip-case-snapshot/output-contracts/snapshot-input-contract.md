# WIP Case Snapshot Input Contract

本文件是 `wip-case-snapshot` 的原始数据包契约。该模块不是最终展示生成器，只负责把 SQL 原始结果和 mock 数据整理成稳定输入包，供 Flow Agent 生成最终 `WIP Case Snapshot`、文本和前端 JSON。

## 1. 模块职责

`wip-case-snapshot` 只做三件事：

1. 接收或透传数仓查询出的 `warehouse_high_wip` 原始行。
2. 读取 `internal/wip-case-snapshot/data/snapshot_mock.json` 中的通用 mock 数据。
3. 读取当前 Flow 自己的 mock 数据，例如 Flow 01 的 `internal/wip-flow-01-anomaly-detection/data/flow01_mock.json`。

本模块禁止：

- 不生成用户可读 Markdown。
- 不生成 `frontend_payload`。
- 不构造最终展示结构。
- 不计算 `bubble_status`。
- 不生成固定系统话术、门禁文案、标题文案。
- 不把示例输出或前端 demo 文本写入 mock。

## 2. 输出 JSON 结构

脚本输出必须保持为原始输入包：

```json
{
  "case_id": "总控 Skill 创建的 UUID",
  "flow": {
    "flow_no": "01",
    "flow_name": "异常发现"
  },
  "snapshot_inputs": {
    "warehouse_high_wip": {},
    "downstream_starvation": {},
    "snapshot_mock": {},
    "flow_mock": {}
  },
  "source_data": {
    "warehouse_high_wip": {},
    "downstream_starvation": {},
    "snapshot_mock_file": "internal/wip-case-snapshot/data/snapshot_mock.json",
    "flow_mock_file": "internal/wip-flow-01-anomaly-detection/data/flow01_mock.json"
  },
  "output_contract_file": "internal/wip-case-snapshot/output-contracts/snapshot-input-contract.md"
}
```

`output_contract_file` 只给出契约文件路径，不嵌入整份契约内容，避免原始数据包膨胀。

## 3. snapshot_inputs 字段说明

### 3.1 warehouse_high_wip

用途：数仓 SQL 查询出的原始最高 WIP stage 行。

典型字段：

- `stage_name`
- `actual_wip`
- `target_wip`
- `queue_wip`
- `queue_actual_ratio`
- `wip_gap`
- `wip_ratio`
- `wip_gap_rate`
- `biz_time`
- `update_time`

约束：

- 原样透传，不在脚本里改名成展示字段。
- 不在脚本里格式化数字、百分比或 Gap 文案。
- 不在脚本里判断是否为最终根因。

### 3.2 snapshot_mock

用途：补足前端 demo 或 Case Snapshot 所需、但当前 SQL 尚不能查询的数据。

允许存放的数据类型：

- `occur_time`
- `operator`
- `demo_mode`
- `case_age`
- `flow_elapsed` / `stage_elapsed`
- `sla_remaining`
- `owner`
- `run_status`
- `priority_by_status`
- `risk_snapshot` 下的 raw metric 数据，例如 `eligible_tool`、`move_out`、`q_time`。Downstream 不再放在 mock 中，来自 `downstream_starvation` SQL 原始结果。
- `additional_case_metrics` 这类补充数据

禁止存放：

- `system_message`
- `business_result_title`
- `status_gate`
- 固定 Markdown 文本
- 前端标题话术
- Agent 分析结论

### 3.3 flow_mock

用途：当前 Flow 专属但 SQL 暂时查不到的数据，例如 Flow 01 的：

- `trend`
- `trigger_source`

禁止存放固定展示文本和结论话术。

## 4. 与最终 WIP Case Snapshot 的关系

本模块输出不是最终前端展示结构。

Flow Agent 应根据本模块输出与自己的输出契约生成最终 `content` 中的 `WIP Case Snapshot` 容器。当前 Flow 01 只允许生成两个 section：

```json
{
  "title": "WIP Case Snapshot",
  "sections": [
    {"title": "Case Header", "items": []},
    {"title": "Case Risk Snapshot｜异常发生时（风险快照）", "items": []}
  ]
}
```

其中：

- `Case Header` section 可使用 `case_id`、`flow`、`warehouse_high_wip`、`snapshot_mock` 中的数据生成。
- `Case Risk Snapshot｜异常发生时（风险快照）` section 可使用 `warehouse_high_wip`、`downstream_starvation` 与 `snapshot_mock.risk_snapshot` 中的数据生成。

## 5. 缺失字段处理

如果 SQL 和 mock 都没有某字段：

- 脚本不补占位值。
- Flow Agent 生成最终展示时省略该字段行或对应 JSON 字段。
- 不输出 `N/A`、`-`、`待补` 这类占位内容，除非业务明确要求。

## 6. 后续 Flow 使用规则

Flow 01 保存最终结果后，后续 Flow 默认读取 Flow 01 保存的 `wip_case_snapshot`。

- WIP、Queue、Tool Uptime、Q-Time 等风险指标：属于异常触发瞬间历史快照。
- Case Age、Stage Elapsed、SLA Remaining 等：属于动态字段，可在打开界面时重新计算或刷新。
- Flow 02 及以后不要为了拿快照而重新执行 `wip-case-snapshot`。
- 后续 Flow 只有在分析所需字段无法从前序保存结果中取得时，才查询对应 SQL 或读取自己的 mock。

## 7. 输出前自检

脚本或调用方应确认：

- 输出包含 `case_id`、`flow`、`snapshot_inputs`、`source_data`。
- `snapshot_inputs` 包含 `warehouse_high_wip`、`downstream_starvation`、`snapshot_mock`、`flow_mock`。
- 输出不包含最终展示结构。
- mock 数据中不包含固定展示话术。
- `output_contract_file` 指向本文件。





