# Flow 10 Business Rules

Flow 10 用于确认 Case 是否满足关闭条件。它不是复盘沉淀流程，不能输出案例沉淀结论。

## 默认演示口径

- 默认假设 Flow 09 已经确认影响消除观察通过。
- 默认假设本阶段关闭确认通过，进入 Flow 11 Case 复盘沉淀。
- 顶层 `case_status` 保持 `Processing`，以便继续进入 Flow 11；业务字段使用 `closure_confirmation_status=关闭确认通过` 表示关闭条件已确认。

## 关闭确认维度

- 协同任务是否完成：MFG、Module Owner、PE、IE Planning、Area Owner 等反馈闭环。
- 风险是否解除：无复发、无下游转移、无处置副作用。
- 恢复指标是否达标：WIP / Queue / Move-Out / Downstream Supply 稳定。
- 临时控制是否可关闭：Move-In 限制、优先级保护、局部 Hold 或通知动作进入关闭前复核。
- 责任人是否确认：MFG / Case Owner 或 Shift Leader 确认可以进入复盘沉淀。

## 门禁

- 若关闭条件满足，则 `case_status=Processing`，`next_flow_no=11`，`next_flow_name=Case 复盘沉淀`。
- 若任务未完成、风险未解除、指标未恢复、受控动作未关闭或责任人未确认，则 `case_status=On Hold`，`next_flow_no=null`。

## 禁止提前输出

- 不写已完成复盘。
- 不写已完成案例沉淀。
- 不写最终根因已确认。
- 不把 Flow 10 写成 Flow 11 的复盘沉淀。
