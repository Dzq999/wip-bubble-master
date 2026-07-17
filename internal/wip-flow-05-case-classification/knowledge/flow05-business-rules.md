# Flow 05 Business Rules - Case 分级与处置判定

Flow 05 的目标是把 Flow 04 的影响范围转换成可执行的 Case 等级、处置路径和初始主责，不替代 Flow 06 的原因排查。

## 分级输入

优先使用前序 `content` 中的事实：

- Impact Lot / Impact WO。
- Hot Lot / Super Hot Run 是否受影响。
- Q-Time Risk 是否为 High。
- Move-Out Gap 或 Move-Out Trend。
- 下游是否 Starvation。
- Flow 03 临时措施是否已生成/执行。

## 默认分级规则

- 若影响范围超过单点波动，且同时存在 Q-Time High、Hot Lot / Super Hot Run 或下游 Starvation，建议 `Case Level = P1 / Major`。
- 若只影响当前 Stage 且无下游或 Q-Time 风险，建议 `Case Level = P2 / Standard`。
- 若证据不足以分级，应 `case_status=On Hold`，并要求补齐影响范围证据。

## 处置路径

- P1 / Major：MFG Lead 牵头，Module Owner / PE / IE 参与，保持临时措施，进入 Flow 06 原因排查。
- P2 / Standard：MFG 与模块工程师跟进，按班次节奏复核影响范围后进入原因排查。

## 输出边界

- 可以输出 Case Level、Disposition Path、Initial Owner、Escalation Gate、Next Flow。
- 不输出最终根因、原因候选排序、工程问题包结论或任务派发结果。
