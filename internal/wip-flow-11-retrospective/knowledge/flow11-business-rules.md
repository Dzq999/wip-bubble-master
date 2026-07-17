# Flow 11 Business Rules

Flow 11 用于完成 Case 复盘沉淀，是 WIP Bubble 的最终流程。

## 默认预置口径

- 默认假设 Flow 10 已经完成关闭确认。
- 默认复盘沉淀完成，顶层 `case_status=Closed`。
- `next_flow_no=null`、`next_flow_name=null`。

## 沉淀维度

- 根因摘要：复用 Flow 06 的候选原因和后续恢复验证结果，形成可沉淀的原因摘要。
- 有效措施：复用 Flow 03 / Flow 07 / Flow 08 / Flow 09 / Flow 10 中已验证有效的控制、协同和恢复措施。
- 无效或需改进措施：说明哪些措施只适合作为临时控制，哪些需要改进监控或协同口径。
- 规则优化：沉淀预警阈值、下游 starvation 联动、Move-In 异常联动、Hot Lot / Super Hot Run 保护等规则建议。
- 案例标签：用于后续检索和相似案例推荐。

## 门禁

- 若复盘沉淀完成，则 `case_status=Closed`，`next_flow_no=null`。
- 若缺少关闭确认或复盘信息不足，则 `case_status=On Hold`，`next_flow_no=null`。

## 禁止输出

- 不输出新的现场处置指令。
- 不重新打开 Case。
- 不声称已经自动更新真实生产规则；只能写规则优化建议或待业务确认。
