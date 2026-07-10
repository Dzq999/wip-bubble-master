---
name: wip-data-query
description: WIP Bubble 分析的数据查询内部模块。用于流程模块需要从 aifab、ffs_vfab_1 或 vfab_agent 获取 actual_wip、target_wip、queue_wip、case 流程记录时；同时负责读写 vfab_agent.fab_case_flow_record。
---

# WIP 数据查询内部模块

本模块是 `wip-bubble-master` 的唯一数据访问层。流程模块不要直接拼 SQL，也不要直接访问数据库。

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

## SQL 文件

业务 SQL 统一放在：

```text
internal/wip-data-query/sql/
```

当前白名单 SQL：

- `locate_high_wip_stage.sql`：从数仓定位当前 WIP 比例最高的业务 stage。
- `locate_downstream_starvation.sql`：根据当前 stage 查询下游 `next_stage_name`，返回下游 `actual_wip`、`target_wip`、`wip_ratio` 和 `if_starved`，用于判断下游是否 Starvation。
- `locate_flow03_priority_lots.sql`：按当前 stage 查询 Flow 03 使用的 Hot Lot / Super Hot Run 数量。
- `get_latest_active_case.sql`：读取最新未关闭 case，可按 `case_id`、`current_flow_no` 或 `next_flow_no` 过滤。继续流程时优先用 `case_id + current_flow_no` 读取上一流程记录。
- `get_case_record.sql`：按 `case_id` 读取流程运行态记录。
- `update_case_flow_record.sql`：更新已有 case 的流程记录。
- `insert_case_flow_record.sql`：新增 case 的流程记录。

`scripts/query_data.py` 只负责读取配置、按白名单加载 SQL 文件、绑定参数并执行，不在 Python 里内嵌业务 SQL。

## 查询规则

- 不接受用户或流程模块传入任意 SQL。
- 只使用 `scripts/query_data.py` 暴露的白名单查询动作。
- `case_id` 是 Agent 运行态 UUID，保存在 `vfab_agent.fab_case_flow_record`，不是数仓业务字段。
- 数仓表只用于计算业务事实，例如 `actual_wip`、`target_wip`、`queue_wip`、`wip_ratio`。
- 查询脚本只返回 SQL 原始结果或写入模型已经生成的结果，不负责字段展示编排、文本话术、前端容器或业务结论构造。
- 如果后续有阈值计算、状态判断等确定性脚本，必须由模型先取得 SQL 结果后把所需字段作为输入传入；计算/判断脚本不要自行连接数据库取数并直接产出结论。

## 脚本调用

```bash
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py locate_high_wip_stage
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py locate_downstream_starvation --stage-name DNW-ANN
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py locate_flow03_priority_lots --stage-name DNW-ANN
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py get_latest_active_case --case-id <uuid> --current-flow-no 01
python .agents/skills/wip-bubble-master/internal/wip-data-query/scripts/query_data.py get_case_record --case-id <uuid>
```

脚本向标准输出打印 JSON。


