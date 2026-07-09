# Flow 04 影响范围评估业务规则

Flow 04 的目标是量化异常影响范围，不替代后续 Case 分级、主责判定、原因排查或工程问题包派发。

必须遵守的边界：

- 只评估影响范围和风险扩散程度，不宣称最终根因。
- 不输出正式 Case 等级；Case 等级、处置路径和主责归属留给 Flow 05。
- 优先复用前序 Flow 的 WIP Case Snapshot、异常确认结论和临时措施结果。
- 只允许使用前端 demo / SQL 已有字段：Impact Lot、Impact WO、Hot Lot、Super Hot Run、Q-Time Risk、Move-Out Gap、Downstream / Starvation，以及前序 WIP / Queue / Tool 等快照字段。
- 不要输出 Product 数、Q-Time 高风险 Lot 数、Recommendation、Shift Risk、ETA Risk、Delivery Risk Level、Affected Commitment 等前端 demo 没有的数据。
- 下游对象必须优先使用前序风险快照中的 Downstream / Next Stage 实际值。
- 如果某个维度没有 SQL、前序 content 或补充输入支撑，省略该维度，不输出 `N/A`、`待补充`、`未知` 等占位内容。
- 影响评估结论可以基于已有字段判断“超过单点波动”或“仍局限于单点波动”，但不能直接给出 P1/P2/P3 等正式分级。

建议检查项：

- Impact Lot 和 Impact WO 数量。
- Hot Lot / Super Hot Run 是否已进入影响范围。
- Q-Time Risk 是否为 High。
- Move-Out Gap 是否明显。
- 下游供料对象是否出现 Starvation。
- 是否满足进入 Flow 05 Case 分级与处置判定的条件。

推进条件：

- 影响范围已评估，且可用于后续分级时：
  - `flow_status=Closed`
  - `case_status=Processing`
  - `next_flow_no=05`
  - `next_flow_name=Case 分级与处置判定`
- 如果前序临时措施未确认、影响对象缺失或关键维度无法评估：
  - `flow_status=Closed`
  - `case_status=On Hold`
  - `next_flow_no=null`
  - 说明阻塞原因。