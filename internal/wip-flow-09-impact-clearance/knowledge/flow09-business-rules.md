# Flow 09 Business Rules

Flow 09 用于在 Flow 08 初步有效之后继续观察影响是否真正消除。它不是 Case 关闭确认，也不是复盘沉淀。

## 默认演示口径

- 默认假设影响消除观察通过，因为 Flow 08 的恢复数据已经按演示口径形成恢复趋势。
- 观察对象来自 Flow 08 的 `Case Risk Trend` 与恢复证据。
- 本阶段应把恢复趋势转为稳定性观察：无复发、无下游转移、无处置副作用。

## 观察维度

- WIP / Queue 是否保持在正常观察区间。
- Move-Out 是否保持恢复后的计划达成状态。
- 下游供料风险是否没有转移或扩散。
- Hot Lot / Super Hot Run 保护是否没有新增高风险暴露。
- 临时控制动作是否具备进入关闭前复核的条件。

## 门禁

- 若观察期无复发、无转移、无副作用，则 `case_status=Processing`，`next_flow_no=10`，`next_flow_name=Case 关闭确认`。
- 若明确出现复发、风险转移、处置副作用或证据不足，则 `case_status=On Hold`，`next_flow_no=null`。

## 禁止提前输出

- 不写 Case 已关闭。
- 不写已完成复盘或已完成案例沉淀。
- 不写最终根因已确认。
- 不把 Flow 09 写成 Flow 10 的关闭确认。
