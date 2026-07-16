# Flow 02 异常确认业务规则

Flow 02 的目标是确认异常成立，不定位根因。

确认成立条件：

- Flow 01 已生成 WIP Bubble / 严重 WIP Bubble 事件。
- 数据刷新在可接受窗口内。
- Actual WIP / Target WIP / Queue WIP 口径可解释。
- Target WIP 存在且大于 0。
- 异常持续时间超过最小确认窗口。
- 没有同一 stage 的重复未关闭 Case。

成立后：

- `flow_status=Closed`
- `case_status=Processing`
- `next_flow_no=03`
- `next_flow_name=临时措施`

不成立时：

- `flow_status=Closed`
- `case_status=Closed` 或 `On Hold`
- `next_flow_no=null`
- 说明未成立原因。
