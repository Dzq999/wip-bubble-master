# WIP Bubble 总控 Skill 目录结构

本 Skill 使用一个总控入口与多个按 Flow 隔离的内部模块。所有模块遵守 [渐进式披露规则](progressive-disclosure.md)：总控不预加载 Flow 资源，路由后只按需读取当前子 Skill 的本地资源。

```text
wip-bubble-master/
  SKILL.md
  knowledge/
    factory-exception-process.md
  examples/
    README.md
    master/
      start-request.json
      start-response.json
  scripts/
    run_master.py
  references/
    directory-structure.md
    progressive-disclosure.md
    runtime-fact-policy.md
  internal/
    config/
    wip-data-query/
      SKILL.md
      sql/
      scripts/
      offline-data/
    wip-case-snapshot/
      SKILL.md
      data/
      output-contracts/
      scripts/
    wip-flow-01-anomaly-detection/
      SKILL.md
      data/
      knowledge/
      output-contracts/
      prompts/
      examples/
        model-context-input.json
        model-output.json
      scripts/
        run_flow01.py
    wip-flow-02-anomaly-confirmation/
      ...
      examples/
        model-output.json
    ...
    wip-flow-11-retrospective/
      ...
      examples/
        model-output.json
```

## 外部入口

`scripts/run_master.py` 是唯一外部执行入口。

它支持两种调用方式。

本地调试可直接传自然语言：

```bash
python .agents/skills/wip-bubble-master/scripts/run_master.py --message "WIP最高的原因是什么"
```

FaaS 中推荐让模型先把自然语言归一化为 JSON，再传入脚本：

```bash
python .agents/skills/wip-bubble-master/scripts/run_master.py --request-json <inline-json>
```

## 外层资源

### `knowledge`

存放所有 Flow 共享的通用业务背景。

当前文件：

- `factory-exception-process.md`：工厂异常处理 10 步闭环和关键原则。

通用背景不要复制到每个 Flow 目录中；Flow 内部只存放本流程专属知识。

### `examples`

根目录只保留总控示例。每个 Flow 的结构模板位于对应 `internal/wip-flow-*/examples/`，总控不预加载这些模板；仅在维护或核对当前 Flow 的结构时按需读取当前子 Skill 的本地 `examples/`。

## 内部模块

### `internal/config`

存放数据库连接配置。运行态读取 `db_config.json`。

`db_config.example.json` 只是模板，不参与运行读取。FaaS 环境没有环境变量时，直接替换或挂载 `db_config.json`。

### `internal/wip-data-query`

负责所有 MySQL 数据访问。

职责：

- 从 `aifab` 和 `ffs_vfab_1` 读取数仓 mock 数据。
- 从 `vfab_agent.fab_case_flow_record` 读取和写入流程运行态记录。
- SQL 统一放在 `sql/*.sql`，Python 不内嵌业务 SQL。
- 只暴露白名单查询函数，不接受任意 SQL。
- 明确 `case_id` 是 Agent 运行态 UUID，不是数仓字段。

### `internal/wip-case-snapshot`

负责构建 Flow 执行前的 Case 态势快照。

职责：

- 基于唯一的 `case_data_snapshot.sql_results` 提取 Flow 01 所需 SQL 字段，并合并必要补充数据。
- 直接输出结构化 `WIP Case Snapshot` 容器；字段、标签与模板由 `wip-case-snapshot/output-contracts/snapshot-display-schema.md` 控制，Flow 01 原样使用。
- 通用快照 mock 放在 `internal/wip-case-snapshot/data/snapshot_mock.json`；Flow 专属补充数据分别放在各自 `data/` 目录，例如 `flow01_mock.json`、`flow02_mock.json`。
- 如果 SQL 和 mock 都没有某字段，则不在输出 JSON 中提供该字段，展示层选择不展示。

### `internal/wip-flow-01-anomaly-detection`

负责 Flow 01：`异常发现`。

职责：

- 定位当前 WIP 最高的业务 stage。
- 按 Target / Warning / UCL / Severe UCL 规则输出 `bubble_status`。
- 构建 `model_context`，把事实、阈值、快照、流程决策、外层通用知识和 Flow 专属知识交给模型。
- 让当前 Agent 根据 `prompts/flow01_result_prompt.md` 与 `output-contracts/` 生成 `text` 和轻量 `content`。
- Python 只做 JSON 解析、字段补齐、空值剔除和兜底。
- 通过数据模块保存 Flow 01 结果。
- Flow 01 执行完成后保存 `flow_status=Closed`；是否继续由 `case_status` 和 `next_flow_no` 决定。

### `internal/wip-flow-03-containment`

负责 Flow 03：`临时措施`。

职责：

- 复用 Flow 02 保存结果和前序 WIP Case Snapshot。
- 在根因完全确认前生成局部、可控、可回退的临时措施。
- 保护 Hot Lot / Super Hot Run，建议限制非关键 Move-In，通知下游风险，并给出 Hold 建议。
- 不重新执行 `wip-case-snapshot`，不做最终根因排查、影响范围量化或正式 Case 分级。
- Python 只做上下文构建、输出校验和状态保存。
- Flow 03 执行完成后保存 `flow_status=Closed`；是否继续由 `case_status` 和 `next_flow_no` 决定。

### `internal/wip-flow-04-impact-assessment`

负责 Flow 04：`影响范围评估`。

职责：

- 复用 Flow 01 / Flow 02 / Flow 03 保存结果和前序 WIP Case Snapshot。
- 评估 Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out Gap 和下游供料。
- 判断影响是否超过单点波动，为 Flow 05 Case 分级与处置判定提供依据。
- 不重新执行 `wip-case-snapshot`，不做最终根因排查、正式 Case 分级或工程问题包派发。
- Python 只做上下文构建、输出校验和状态保存。
- Flow 04 执行完成后保存 `flow_status=Closed`；是否继续由 `case_status` 和 `next_flow_no` 决定。
## Flow 模块约定

后续每个 Flow 都按相同结构组织：

```text
internal/wip-flow-xx-name/
  SKILL.md
  knowledge/
    *.md
  prompts/
    *.md
  scripts/
    run_flowxx.py
```

约定：

- 外层 `knowledge/` 存放所有 Flow 共享的工厂异常处理大背景。
- Flow 内部 `knowledge/` 存放本流程业务知识、判断条件、角色口径和 输出约束。
- `prompts/` 存放模型生成提示词；`output-contracts/` 单独存放每个 Flow 的最终回答格式契约，或内部数据模块的原始输入包契约。
- `scripts/` 只做查询、计算、上下文构建、模型 JSON 修复和状态保存。
- 大量自然语言分析不要写死在 Python 中。

## 命名规则

SOP 流程统一叫 `Flow 01`、`Flow 02` 等。

数仓或 Fab 业务里的工艺段字段才叫 `stage_name`，例如 `DNW-ANN`。

不要把 SOP 流程叫成 `Stage 01`，否则容易和业务 stage 混淆。

## 后续扩展

新增流程时，继续放在 `internal/` 下：

```text
internal/wip-flow-02-anomaly-confirmation/
internal/wip-flow-03-containment/
...
internal/wip-flow-11-knowledge-archive/
```

然后更新 `scripts/run_master.py`，让 `next_flow_no` 能分发到新的 Flow 模块。






