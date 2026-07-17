# 渐进式披露规则

本 Skill 的所有模块均采用渐进式披露，避免无关资源进入当前上下文。

## 执行顺序

1. 总控阶段只读取总控 `SKILL.md`、请求参数和路由所需最小信息；不预加载任何 Flow 的知识库、提示、契约、示例或数据文件。
2. 路由确定后，只读取目标子 Skill 的 `SKILL.md`。
3. 仅在当前任务确有需要时，再读取该子 Skill 本目录的 `knowledge/`、`prompts/`、`output-contracts/`、`data/` 与 `examples/`；按具体问题选择文件，不批量加载整个目录。
4. 不读取兄弟 Flow 的资源。前序 Flow 只能通过已保存的 `content` / `text` 和 `case_data_snapshot.sql_results` 传递事实。
5. `wip-data-query` 与 `wip-case-snapshot` 仅在 Flow 01 启动、离线快照加载或明确的数据访问任务中读取；后续 Flow 不重新加载或查询它们。
6. `examples/` 仅用于维护或核对当前 Flow 的结构，永远不是运行时输入或业务事实来源。

这样既保留当前流程所需信息，也避免无关流程、示例和知识内容消耗上下文。
