# Flow 03 临时措施业务规则

Flow 03 的目标是在根因完全确认前做短期风险遏制，不替代后续影响评估、分级、原因排查或跨部门处置。

必须遵守的边界：

- 只制定局部、可控、可回退的临时措施。
- 优先保护 Hot Lot / Super Hot Run 和 Q-Time 高风险批次。
- 可以建议限制非关键 Product / 非关键 Lot 的新增 Move-In，避免 WIP Bubble 继续放大。
- 可以通知下游站点或班组提前关注供料风险；下游站点名称必须优先使用前序风险快照中的 Downstream / Next Stage 实际值。
- 不建议无差别全量 Hold，除非前序数据明确显示质量、设备安全或批量风险已触发；当前 demo 默认不建议全量 Hold。
- 不直接宣称最终根因，不生成工程问题包，不派发跨部门工单。
- 受控动作应以建议、通知、草案、待确认方式表达；不能写成 Agent 已直接修改 Dispatch、Hold 或生产主系统。

建议检查项：

- Hot Lot / Super Hot Run 是否存在。
- Q-Time 风险是否为 High 或存在最短剩余时间压力。
- 下游是否存在 Starvation / 供料风险；如果前序显示 Next Stage = PW-PH，则下游对象就是 PW-PH。
- 是否需要限制非关键 Move-In。
- 是否需要全量 Hold；默认倾向为不建议。
- 是否需要形成 Dispatch 权重或优先级调整草案，但等待 MFG / Shift / Area Owner 确认。

推进条件：

- 临时措施已生成或已确认执行后：
  - `flow_status=Closed`
  - `case_status=Processing`
  - `next_flow_no=04`
  - `next_flow_name=影响范围评估`
- 如果关键风险对象缺失、无法确认执行范围或人工门禁未通过：
  - `flow_status=Closed`
  - `case_status=On Hold`
  - `next_flow_no=null`
  - 说明阻塞原因。
