---
name: wip-data-query
description: WIP Bubble 分析的数据查询内部模块。用于流程模块需要从 aifab、ffs_vfab_1 或 vfab_agent 获取 actual_wip、target_wip、queue_wip、case 流程记录时；同时负责读写 vfab_agent.fab_case_flow_record。
---

# WIP 数据查询内部模块

本模块是 `wip-bubble-master` 的唯一数据访问层。流程模块不要直接拼 SQL，也不要直接访问数据库。正式流程中，SQL 事实必须在 Case 启动时通过 `collect_case_data_snapshot` 一次性收集，并随 Flow 01 结果保存；后续 Flow 只读取这份快照。

## 数据库

- `aifab`：数仓 mock 业务数据，包括 WIP lot、Target WIP、工艺路线、dispatch、机台等表。
- `ffs_vfab_1`：mock 的机台 RTI / feature 数据。
- `vfab_agent`：Agent 自建运行态数据库，包括 `fab_case_flow_record`。

数据库运行配置文件：

```text
internal/config/db_config.json
```

`db_config.example.json` 只是模板，不作为运行配置读取。FaaS 环境没有环境变量时，直接替换或挂载 `db_config.json`。

当前 demo 默认配置：

```text
host=127.0.0.1
port=3306
user=root
password=1234
```

## 离线快照

预置离线数据文件：

```text
offline-data/production-high-wip-stage/case_data_snapshot.json
```

它由仓库根目录 `生产环境当前高wip的stage定位及排查csv_外发/` 的 11 个 CSV 整理而来，键名与当前 `sql_results` 白名单一致。调用 `load_offline_case_data_snapshot()` 只读取该 JSON，不创建数据库连接。

## SQL 文件

业务 SQL 统一放在：

```text
internal/wip-data-query/sql/
```

当前白名单 SQL：

- `locate_high_wip_stage.sql`：从数仓定位当前 WIP 比例最高的业务 stage。
- `locate_downstream_starvation.sql`：根据当前 stage 查询下游 `next_stage_name`，返回下游 `actual_wip`、`target_wip`、`wip_ratio` 和 `if_starved`，用于判断下游是否 Starvation。
- `locate_priority_lots.sql`：按当前 stage 查询 Flow 03 使用的 Hot Lot / Super Hot Run 数量。
- `get_latest_active_case.sql`：读取最新未关闭 case，可按 `case_id`、`current_flow_no` 或 `next_flow_no` 过滤。继续流程时优先用 `case_id + current_flow_no` 读取上一流程记录。
- `get_case_record.sql`：按 `case_id` 读取流程运行态记录。
- `update_case_flow_record.sql`：更新已有 case 的流程记录。
- `insert_case_flow_record.sql`：新增 case 的流程记录。

`scripts/query_data.py` 只负责读取配置、按白名单加载 SQL 文件、绑定参数并执行，不在 Python 里内嵌业务 SQL。

正式入口：

- `collect_case_data_snapshot`：在 Case 启动时一次性执行当前 demo 已配置的白名单 SQL，返回 `schema_version=case-data-snapshot-v1` 的快照。快照会保存到 Flow 01 的 `flow_data_json.case_data_snapshot`，供 Flow 03 / Flow 04 / Flow 06 及后续流程复用。
- 单项 `locate_*` 查询仅保留给 `collect_case_data_snapshot`、本地调试或补数据脚本使用；内部子 Flow 不应直接调用这些单项 SQL 查询。
## 生产 SQL 对齐

业务白名单 SQL 已逐条对齐项目根目录的 `生产环境当前高wip 的stage 定位及排查.md`：高 WIP、Hot / Super Hot Lot、下游 Starvation、Impact Lot、Tool Status、Tool Dispatch、Tool OE / AE、Move-In、Move-Out、Product / Queue / Eligible Tool、Hold / Run WIP。

- 文档中标注为变量的 `stage_name = 'DNW-ANN'` 统一参数化为 `%s`；除此以外，SQL 文件保留生产文档原文。
- Move-Out 生产 SQL 只执行一次，Flow 04 与 Flow 06 共用同一原始结果。
- `case_data_snapshot.sql_results` 额外保存 `tool_dispatch` 与 `product_tool_profile`；原先没有生产文档对应项的 `tool_efficiency_detail` 不再采集。
- `db_config.json` 的 `sql_dialect=mysql_local` 仅用于本地 MySQL 方言兼容及表/数据补齐；生产环境省略该字段或设为 `production` 时，直接执行生产 SQL，且不会自动造数。

## 查询规则

- 不接受用户或流程模块传入任意 SQL。
- 只使用 `scripts/query_data.py` 暴露的白名单查询动作；正式链路由 `collect_case_data_snapshot` 一次性调用这些动作。
- `case_id` 是 Agent 运行态 UUID，保存在 `vfab_agent.fab_case_flow_record`，不是数仓业务字段。
- 数仓表只用于计算业务事实，例如 `actual_wip`、`target_wip`、`queue_wip`、`wip_ratio`。
- 查询脚本只返回 SQL 原始结果快照或写入模型已经生成的结果，不负责字段展示编排、文本话术、前端容器或业务结论构造。
- 如果后续有阈值计算、状态判断等确定性脚本，必须由模型先从 `case_data_snapshot` 取得 SQL 结果后把所需字段作为输入传入；计算/判断脚本不要自行连接数据库取数并直接产出结论。

## 脚本调用

```bash
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py collect_case_data_snapshot
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py locate_downstream_starvation --stage-name DNW-ANN
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py locate_priority_lots --stage-name DNW-ANN
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py get_latest_active_case --case-id <uuid> --current-flow-no 01
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py get_case_record --case-id <uuid>
```

脚本向标准输出打印 JSON。

## 无文件执行约束

- 禁止创建或输出临时文件、请求 JSON、结果 JSON、压缩包、下载链接或文件日志。
- 只读取已部署的配置、SQL、知识库和 mock 文件；唯一允许的持久化写入是 MySQL Case 记录。
- 运行结果必须直接返回内联数据，不得以文件形式交付。
