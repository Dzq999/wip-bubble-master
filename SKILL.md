---
name: wip-bubble-master
description: WIP Bubble SOP 演示的总控与路由 Skill。用于用户询问 WIP Bubble、高 WIP、WIP 最高原因，或确认是否进入下一流程时；负责创建 UUID case_id、读取 vfab_agent 流程记录、严格按 Flow 顺序推进、加载通用工厂异常处理知识、调用内部流程模块，并返回 text/json/both。
---

# WIP Bubble 总控 Skill

这是前端或 FaaS 平台唯一需要调用的外层 Skill。用户不需要提供 `case_id`；本 Skill 会自动创建 UUID 形式的 `case_id`，并写入 `vfab_agent.fab_case_flow_record`。

需要了解目录结构或后续扩展方式时，读取 `references/directory-structure.md`。


## 当前 Agent 必须完成最终回答

执行本 Skill 时，当前 Agent 自己就是生成结果的主体。脚本输出只允许作为内部数据输入，不是用户可见结果。

- 如果脚本返回 `internal_only=true`、`reason=model_output_required`、`model_context` 或 `prompt`，必须继续根据这些原始数据生成最终业务回答，不能把这些字段、脚本状态或标准输出状态展示给用户。
- 禁止回复“stdout 为空”“脚本原始输出”“上下文已生成”“等待模型生成”等过程性内容。
- 如果需要本地调试脚本，可读取脚本返回的 `model_context.raw_inputs` 和 prompt；面向用户时必须输出当前路由 Flow 的业务文本与前端 JSON 结构。
- 示例输出只用于结构参考，不作为默认回复，也不应被脚本自动套用。
## 运行时事实唯一来源（最高优先级）

所有 Flow 生成最终结果前，必须先遵守 [runtime-fact-policy.md](references/runtime-fact-policy.md) 的固定执行路径。最简规则如下：

1. 先取得目标 Flow 脚本的 `model_context`。
2. 只使用 `model_context.raw_inputs` 中的 SQL 快照、前序结果和当前 Flow 实际存在的补充数据。
3. `examples/`、output-contracts 与 prompt 只说明结构，不提供任何业务事实；运行时禁止读取或复用其中的对象名、数值、人员、时长或结论。
4. 每个具体业务表述都必须能回溯到 `raw_inputs`；无来源则省略或说明数据不足，绝不自行补造。

## 生成、落库与最终返回顺序

正式执行任一 Flow 时，当前 Agent 必须把“本轮新生成的完整 Flow 输出”作为唯一最终答案来源。禁止为了节省步骤，直接读取目标 Flow 已存在的 `flow_data_json` 并返回给用户或前端。

强制顺序：

1. 先按路由读取前序 Flow 记录，只用于构造当前目标 Flow 的上下文。例如执行 Flow 03 时，只读取 Flow 01 / Flow 02 等前序结果；不得把旧 Flow 03 当作输入结论。
2. 当前 Agent 根据 `model_context`、prompt、子 Skill 规则和 output-contracts 生成本次目标 Flow 的完整 `text` 与轻量 `content` JSON。
3. 生成后先用目标 Flow 脚本的校验入口验证该 JSON；校验失败必须修正本轮生成内容，不能回退到数据库旧结果。
4. 校验通过后，必须把同一个本轮生成的 JSON 作为 `--model-output-json` 传入目标 Flow 脚本，更新或插入 `vfab_agent.fab_case_flow_record`。
5. 数据库更新完成后，最终回复只能返回这次刚生成并已落库的结果；即使目标 Flow 行在执行前已经存在，也只能被覆盖/更新，不能作为本次最终回复来源。

当总控脚本返回 `save_required=true`、`must_generate_before_final=true`、`must_save_before_final=true` 或 `must_not_return_existing_flow_data=true` 时，上述顺序是硬约束。只有明确进行本地格式调试且用户要求不落库时，才可以跳过保存；前端 demo / FaaS 正式链路默认必须先保存再返回。
## 离线数据模式

内网未开放数据库权限时，请在结构化请求中传入 `offline_data=true`，或在用户消息中明确写“使用离线数据”。总控会只读取：

```text
internal/wip-data-query/offline-data/production-high-wip-stage/case_data_snapshot.json
```

该文件由外发的 11 个生产 SQL CSV 整理而成，结构与 `case_data_snapshot.sql_results` 一致。离线模式禁止连接或写入 MySQL。

继续下一 Flow 时，平台必须将对话中已经生成的完整前序 Flow 结果作为 `conversation_context` 传入，可传数组或 `{ "previous_records": [...] }`。每项可直接使用已返回的 `{case_id, flow_no, content, text, next_flow_no, ...}`；总控会在内存中转换为子 Flow 所需的前序记录。离线模式不读取 `fab_case_flow_record`，也不要求保存当前 Flow，最终结果直接保留并返回在对话上下文中。

## 通用知识库

外层 `knowledge/` 存放所有 Flow 共享的大背景知识。

当前通用知识：

```text
knowledge/factory-exception-process.md
```

这份知识描述真实工厂异常处理闭环：异常发现、异常确认、异常分级、影响评估、原因候选、工程问题包、协同任务、工程师二次分析、恢复验证和案例沉淀。

Flow 专属知识只放在各自内部模块的 `knowledge/` 下，不要把通用大背景复制到每个 Flow 中。

## 输入输出示例

示例统一放在：

```text
examples/
```

当前示例：

- `examples/master/start-request.json`：总控 Skill 启动 WIP 分析的输入示例。
- `examples/master/start-response.json`：总控 Skill 返回结构示例。
- `examples/flow-01/model-context-input.json`：Flow 01 传给模型的上下文输入示例。
- `examples/flow-01/model-output.json`：Flow 01 输出示例，使用轻量 `content.containers[].sections[].items[]` 结构覆盖 Markdown 内容，前端按容器循环渲染。
- `examples/flow-02/model-output.json`：Flow 02 异常确认输出示例，复用 Flow 01 保存快照，只补充成立性校验结果。
- `examples/flow-03/model-output.json`：Flow 03 临时措施输出示例，复用前序快照，只补充短期风险控制动作。
- `examples/flow-04/model-output.json`：Flow 04 影响范围评估输出示例，复用前序快照，只补充 Impact Lot / Impact WO / Hot Lot / Super Hot Run / Q-Time / Move-Out Gap / 下游供料。
- `examples/flow-05/model-output.json`：Flow 05 Case 分级与处置判定输出示例，复用前序快照和影响范围，只补充 Case Level、处置路径、初始主责和进入 Flow 06 的门禁。
- `examples/flow-06/model-output.json`：Flow 06 异常原因排查输出示例，复用前序内容和 Flow 01 保存的 `case_data_snapshot.sql_results`，只补充候选原因排序、证据链和待补证据。
- `examples/flow-07/model-output.json`：Flow 07 工程问题包与协同任务输出示例，复用前序候选原因和处置路径，只补充问题包、角色任务、SLA、反馈要求和恢复验证指标。
- `examples/flow-08/model-output.json`：Flow 08 处置效果确认输出示例，复用前序协同任务和恢复指标口径，动态展示异常值 -> 正常值的 Case Risk Trend，并进入 Flow 09 观察。
- `examples/flow-09/model-output.json`：Flow 09 影响消除观察输出示例，复用 Flow 08 恢复趋势，默认观察通过并进入 Flow 10 关闭确认。
- `examples/flow-10/model-output.json`：Flow 10 Case 关闭确认输出示例，复用 Flow 09 观察通过结果，默认关闭确认通过并进入 Flow 11 复盘沉淀。
- `examples/flow-11/model-output.json`：Flow 11 Case 复盘沉淀输出示例，复用完整闭环结果，默认完成沉淀并关闭 Case。

示例只作为 FaaS 编排和模型输出格式参考，不参与运行。标题可以参考示例保持稳定，但正文话术必须由当前 Agent 根据本次 `case_data_snapshot` 和保留的补充数据重新组织，不要原文照抄示例。

## 前端输出约定

每个 Flow 执行完成后，都必须输出前端 demo 需要的三块主容器；不要再输出重复的 `frontend_payload`、`frontend_demo` 或顶层分散容器。

统一使用轻量 `content`：

```json
{
  "content": {
    "title": "01 异常发现",
    "containers": [
      {
        "title": "WIP Case Snapshot",
        "sections": [
          {"title": "Case Header", "items": [{"label": "...", "value": "..."}]},
          {"title": "Case Risk Snapshot｜异常发生时（风险快照）", "items": [{"label": "...", "value": "..."}]}
        ]
      },
      {
        "title": "当前阶段对话",
        "sections": [
          {"title": "系统 / 用户触发", "items": ["..."]},
          {"title": "Agent 接管", "items": ["..."]},
          {"title": "Agent 思考过程", "items": ["..."]},
          {"title": "Agent 分析计划", "items": ["..."]},
          {"title": "数据 / 工具调用", "items": [{"label": "MES / WIP Profile", "value": "Actual WIP = ...", "status": "Done"}, {"label": "Planning Config", "value": "Target WIP = ...", "status": "Done"}, {"label": "BI Trend", "value": "WIP ...", "status": "Done"}]},
          {"title": "Agent 观察结果", "items": ["..."]},
          {"title": "Agent 分析判断", "items": ["..."]},
          {"title": "Agent 阶段输出", "items": ["..."]},
          {"title": "AI Agent", "items": ["..."]}
        ]
      },
      {
        "title": "当前阶段结果",
        "sections": [
          {"title": "业务结果", "items": [{"label": "...", "value": "..."}]},
          {"title": "本阶段结论", "items": ["..."]},
          {"title": "Agent 判断逻辑", "items": ["..."]},
          {"title": "状态与门禁", "items": ["..."]},
          {"title": "关键证据", "items": ["..."]}
        ]
      }
    ]
  }
}
```

`content.containers` 的一级标题固定，二级/三级内容由对应 Flow 的 output-contracts 约束；前端只需要循环 `containers[].sections[].items[]` 动态渲染。

注意：Flow 08 仍然输出两段 `WIP Case Snapshot`，但第二段必须是 `Case Risk Trend｜处置后（恢复趋势）`，用于替代前序 Flow 的 `Case Risk Snapshot｜异常发生时（风险快照）`；不要在 Flow 08 同时输出这两个 risk section。

## 请求归一化

在 FaaS 中建议采用两步模式：

1. 先让模型把用户自然语言转换成标准 request JSON。
2. 以平台结构化参数或内联 JSON 直接调用总控；禁止先生成请求 JSON 文件。

标准 request JSON 结构：

```json
{
  "intent": "wip_analysis | continue_flow | unrelated | auto",
  "action": "start | continue | auto",
  "message": "用户原始问题或确认文本",
  "return_type": "text | json | both"
}
```

默认值：

```json
{
  "intent": "auto",
  "action": "auto",
  "return_type": "text"
}
```

脚本仍然保留简单命令行参数，方便本地调试。`return_type` 只控制总控 Skill 的最终返回格式；如果外部请求中没有带入 `return_type`，不要向内部 Flow 模块传入 `return_type`。

`return_type=text` 是默认值，只输出面向用户阅读的 Markdown 文本，不附加 JSON。该 Markdown 必须按前端 demo 的三个主容器组织：

```text
# 01 异常发现

## WIP Case Snapshot
...
## 当前阶段对话
...
## 当前阶段结果
...
```

只有 `return_type=json` 或 `return_type=both` 才输出结构化 JSON。JSON 必须是完整 Flow 输出，包含 `text` 与 `content.containers` 三大容器；禁止只输出 `ok/case_id/flow_no/status` 这类摘要。

`return_type=both` 必须按两个独立区块依次返回，禁止只返回一个 JSON 代码块：

```text
## 可读 Markdown
<完整 text 字段的 Markdown 内容>

## 结构化 JSON
```json
<完整 Flow JSON>
```
```

其中第一个区块供用户直接阅读；第二个区块供前端/编排消费。虽然完整 JSON 内仍包含 `text` 字段，但不得因此省略第一个可读 Markdown 区块。
## 当前 Agent 执行流程

当用户要求执行本 Skill 时，当前 Agent 必须按路由直接进入对应内部子 Skill，不要把总控脚本或数据脚本的 stdout 当作最终回复。

1. 先做意图判断：WIP 分析启动请求路由到 `internal/wip-flow-01-anomaly-detection`；继续下一流程必须用上一流程编号 `flow_no` 读取前序记录，并路由到该记录 `next_flow_no` 对应子 Skill。
2. 路由到子 Skill 后，直接读取并遵守该子 Skill 的 `SKILL.md`、`knowledge/` 和 `prompts/`，由当前 Agent 生成最终 `text` 与轻量 `content`；示例只能参考结构，正文不能照抄。
3. Python 脚本只作为一次性数据快照、补充数据读取、确定性计算和落库工具。SQL 只能由 `wip-data-query` 在 Case 启动时统一收集为 `case_data_snapshot`；脚本返回的 `internal_only`、`model_context`、`prompt`、`reason=model_output_required` 都是内部中间态，禁止展示给用户。
4. 最终面向用户或前端展示的 `text` / `content` 禁止出现 `mock` 字样；来自内部 mock 的字段必须按业务口径表述为“快照输入”“补充信号”或具体数据名称。
5. 正式执行时必须先把当前 Agent 本轮生成的完整 JSON 作为 `--model-output-json` 传入目标 Flow 脚本保存或更新，再返回同一个新生成结果；禁止从数据库读取目标 Flow 的旧 `flow_data_json` 当作最终答案。
6. 最终回复用户时只返回业务结论和按 `return_type` 要求的内容，不输出“执行脚本”“原始输出”“上下文已生成”“请模型生成”等过程性文本。
7. `case_data_snapshot` 是仅供数据库保存与后续 Flow 读取的内部 SQL 快照；最终 `text`、`json`、`both` 和 FaaS 对外结果均不得包含该字段。
8. 对外最终 JSON 必须直接采用目标 Flow 脚本保存后返回的完整公开结果，禁止保存后由 Agent 重新拼装 `content` 或只摘取其中一个 `containers`。Flow 01 返回前必须确认 `content.containers` 完整且顺序为 `WIP Case Snapshot`、`当前阶段对话`、`当前阶段结果`；否则不得返回。
9. 输出示例、output-contracts 和 `examples/` 中的具体数值永远不是数据源；SQL 与该 Flow 的补充 mock 都没有某字段时，必须省略该字段或表述为证据不足，禁止抄写示例数值。
10. 子 Flow 的 mock 是可变补充数据，当前 Agent 只读取 `model_context.raw_inputs` 中实际存在的键并结合本次流程自行决定展示；禁止在 Python 中维护固定 mock 字段清单，键缺失时省略即可。
11. `return_type=both` 的最终回复必须先输出标题为“可读 Markdown”的完整 Markdown，再输出标题为“结构化 JSON”的 JSON 代码块；不得把两种形态仅封装在一个 JSON 对象或一个 JSON 代码块中。

## 路由规则

1. 如果 `intent=unrelated`，直接返回：
   `你的问题与 WIP Bubble / WIP 异常原因分析无关，当前智能体仅支持 Fab WIP Case 排查流程。`
2. 如果外部请求与 WIP 分析相关，并且不是明确的“继续下一流程”，每次都创建新的 UUID `case_id` 并执行 Flow 01；不要通过 `get_latest_active_case` 复用历史 case。
3. 只有用户明确确认继续时，才从 `vfab_agent.fab_case_flow_record` 读取前序 Flow 记录；请求必须传入上一流程编号 `flow_no`，例如执行 Flow 02 时传 `flow_no=01`，并可选传入 `case_id` 限定 Case。路由依据前序记录中的 `next_flow_no`。
4. 流程必须严格按 SOP 顺序执行。即使用户直接询问最终原因，也不能跳到 Flow 06。
5. 当前已实现 Flow 01、Flow 02、Flow 03、Flow 04、Flow 05、Flow 06、Flow 07、Flow 08、Flow 09、Flow 10 和 Flow 11。内部模块位于 `internal/`：`wip-data-query`、`wip-case-snapshot`、`wip-flow-01-anomaly-detection`、`wip-flow-02-anomaly-confirmation`、`wip-flow-03-containment`、`wip-flow-04-impact-assessment`、`wip-flow-05-case-classification`、`wip-flow-06-root-cause-analysis`、`wip-flow-07-collaboration-package`、`wip-flow-08-effect-confirmation`、`wip-flow-09-impact-clearance`、`wip-flow-10-closure-confirmation` 和 `wip-flow-11-retrospective`。Flow 02 只做异常成立性确认：数据刷新、指标口径、Target 有效性、异常持续时间和同类未关闭 Case。Flow 03 只做临时措施：Hot Lot / Super Hot Run 保护、非关键 Move-In 控制、下游通知和 Hold 建议，不做最终根因排查。Flow 04 只做影响范围评估：Impact Lot、Impact WO、Hot Lot / Super Hot Run、Q-Time、Move-Out Gap 和下游供料，不做正式 Case 分级。Flow 05 只做 Case 分级与处置判定：Case Level、处置路径、初始主责、协作角色和进入 Flow 06 的门禁，不做最终根因排查。Flow 06 只做异常原因排查：候选原因排序、证据链、排除项和待补证据，不宣布最终根因已确认，不关闭 Case，不派发工程任务。Flow 07 只做工程问题包与协同任务：问题包摘要、角色任务、SLA、反馈要求和恢复指标，不声称已真实派单，不判断处置已生效。Flow 08 只做处置效果确认：默认假设处置反馈已返回并完成初步确认，使用动态 mock 展示异常指标从异常值 -> 正常值的 Case Risk Trend；Flow 08 中 Case Risk Trend 替代前序 Case Risk Snapshot，WIP Case Snapshot 仍保持两段；原本不异常的指标保持原值，不宣布异常已完全恢复，不关闭 Case。Flow 09 只做影响消除观察：默认假设观察通过，确认无复发、无下游转移风险和无处置副作用，进入 Flow 10 Case 关闭确认，不直接关闭 Case。Flow 10 只做 Case 关闭确认：默认假设关闭确认通过，确认任务完成、风险解除、指标恢复、受控动作关闭和责任人确认，进入 Flow 11 Case 复盘沉淀，不做复盘沉淀。Flow 11 只做 Case 复盘沉淀：默认假设沉淀完成，沉淀根因摘要、有效措施、改进项、规则优化建议和案例标签，并关闭 Case。
6. 单个 Flow 执行结束后，`flow_status` 应保存为 `Closed`。是否继续下一个 Flow 由 `case_status`、`next_flow_no` 和用户确认共同决定。
7. Flow 01 负责生成并保存 WIP Case Snapshot，同时保存 `case_data_snapshot`。其中 `case_data_snapshot` 由 `wip-data-query` 在 Case 启动时一次性跑完当前 demo 已配置的白名单 SQL，所有结果只保存在唯一的 `case_data_snapshot.sql_results` 对象中，不再按 Flow 复制。后续 Flow 默认读取 Flow 01 保存的 `wip_case_snapshot` 和 `case_data_snapshot.sql_results`：其中 WIP、Queue、Tool Uptime、Q-Time 等风险指标是异常触发瞬间的历史快照；Case Age、Stage Elapsed、SLA Remaining 等是打开界面时的动态值，可按当前时间重新计算或刷新。Flow 02 及以后不要为了拿快照而重新执行 `wip-case-snapshot`，也不要为了业务字段再次连接数据库。
8. 后续 Flow 需要 SQL 事实时，只能从 Flow 01 已保存的 `case_data_snapshot.sql_results` 获取；不得在子 Flow 中再次查询 SQL。若 `case_data_snapshot` 和前序 `content` 都没有所需字段，才读取该 Flow 保留的补充数据；仍缺失则忽略该内容，不输出占位值。
9. 每个 Flow 都维护自己的 `knowledge/` 和 `prompts/`：
   - 外层 `knowledge/` 存放所有 Flow 共享的工厂异常处理大背景。
   - Flow 内部 `knowledge/` 存放本 Flow 的业务知识、判断条件、角色口径和 demo 约束。
   - prompts/ 存放模型生成提示词。
   - 每个内部 Flow 子 skill 都应维护 output-contracts/，单独存放最终回答格式契约；契约文件要拆分说明 Markdown 文本结构和轻量 JSON 结构。
   - Python 脚本只负责 Case 启动时的一次性 SQL 快照、读取保留的补充数据、执行模型显式要求的确定性计算、解析/修复模型 JSON 和保存模型结果；不要在脚本里硬编码最终文本话术、前端容器内容或业务分析结论。
   - 如果计算或判断依赖 SQL 结果，先让模型从 `case_data_snapshot` 拿到 SQL 原始结果，再把相关数据传给计算脚本；不要让计算/判断脚本自行查询 SQL 并直接产出结论。

## 脚本调用

脚本只用于 FaaS 编排或本地调试，不是当前 Agent 的最终回复来源。当前 Agent 执行 Skill 时应按路由直接进入内部子 Skill。

FaaS / 本地调试可以调用：

```bash
python -B .agents/skills/wip-bubble-master/scripts/run_master.py --message "WIP最高的原因是什么" --return-type json
```

如果脚本输出内部中间态，调用方必须继续按子 Skill 生成最终结果，不得原样展示 stdout。

## 无文件执行约束

- 正式 FaaS / 内网平台运行时禁止创建、写入、上传或打包任何临时文件、请求 JSON、模型输出 JSON、日志文件、压缩包或下载链接。
- 输入必须以内联 JSON、平台结构化参数或标准输入传递；禁止使用 `@文件路径`、`tmp/`、`examples/` 作为运行参数。
- 最终结果必须直接以内联 `text` / `json` / `both` 返回；唯一允许的持久化写入是 MySQL 的 `vfab_agent.fab_case_flow_record`。
- 不得在用户回复中报告文件、压缩包、下载链接、stdout 文件日志或要求下载结果。

