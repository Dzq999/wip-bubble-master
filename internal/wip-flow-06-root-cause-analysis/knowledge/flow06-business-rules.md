# Flow 06 Business Rules

## 目标

Flow 06 的目标是定位 WIP Bubble 的“候选原因”，并为工程师后续确认提供证据链。它不是最终结案流程。

## 判定逻辑

- Move-In 本周较上周明显突增，且 Move-Out 未同步突增时，优先考虑流入压力或派工节奏导致堆积。
- Tool active 偏低、Hard Down / PM 不为 0、Tool Uptime 异常时，优先考虑设备可用性不足。
- OE / AE 偏低、Idle 时间偏高时，优先考虑设备效率或待料 / 派工问题。
- Hold WIP 明显高于 Run WIP 时，优先考虑 Hold / release / hold reason 造成可加工量不足。
- 若下游已 Starvation，但当前 stage 堆积仍高，需要同时关注供应节奏与优先级保护。
- Flow 06 可以输出候选排序和置信度，但必须保留“需工程师确认”的语义。

## 禁止输出

- 不得写“最终根因已确认”。
- 不得写“责任已锁定”。
- 不得写“Case 已关闭原因”。
- 不得写“工程任务已派发”。
