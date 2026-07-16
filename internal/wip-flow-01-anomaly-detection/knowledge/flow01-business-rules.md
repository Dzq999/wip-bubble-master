# Flow 01 异常发现业务规则

## 名称

- SOP 流程名称：Flow 01 异常发现。
- 业务工艺段字段仍称为 stage，例如 `stage_name`。
- 不要把 SOP 流程写成 Stage 01。

## 输入事实

模型主要使用 `model_context` 中的事实：

- `facts.stage_name`：当前 WIP 比例最高的业务 stage。
- `facts.actual_wip`：Actual WIP。
- `facts.target_wip`：Target WIP。
- `facts.warning_wip`：Warning WIP。
- `facts.ucl_wip`：UCL WIP。
- `facts.severe_ucl_wip`：Severe UCL WIP。
- `facts.queue_wip`：Queue WIP。
- `facts.queue_actual_ratio`：Queue / Actual。
- `facts.wip_gap`：Actual 与 Target 的差值。
- `facts.wip_gap_rate`：Actual 相对 Target 的偏差比例。
- `facts.trend`：demo mock 中的趋势描述。
- `facts.trigger_source`：demo mock 中的触发来源。
- `case_snapshot`：前端红框需要的态势快照。

SQL 和 mock 都没有提供的字段，不要编造，不要用 `-` 强行展示；让前端选择不展示。

## WIP 状态判断规则

```text
Actual WIP <= Target WIP               ：正常
Target WIP < Actual WIP <= Warning WIP ：正常偏高
Warning WIP < Actual WIP <= UCL WIP    ：预警
UCL WIP < Actual WIP <= Severe UCL WIP ：WIP Bubble
Actual WIP > Severe UCL WIP            ：严重 WIP Bubble
Target WIP 缺失或 <= 0                 ：Target 缺失
```

阈值计算：

```text
Warning WIP = Target WIP * 1.2
UCL WIP = Target WIP * 1.5
Severe UCL WIP = Target WIP * 2.0
```

## 流程状态规则

- Flow 01 执行完成后，`flow_status` 固定为 `Closed`。
- `bubble_status` 为 `WIP Bubble` 或 `严重 WIP Bubble` 时：
  - `case_status=Processing`
  - `next_flow_no=02`
  - `next_flow_name=异常确认`
  - 文本最后询问是否进入 Flow 02。
- `bubble_status` 为 `Target 缺失` 或 `数据异常` 时：
  - `case_status=On Hold`
  - 不进入下一流程。
- `bubble_status` 为 `正常`、`正常偏高`、`预警` 时：
  - `case_status=Closed`
  - 不进入 WIP Bubble 处置流程。
- 未查询到可进入异常确认的异常 stage 时：
  - `bubble_status=未发现异常`
  - `case_status=Closed`
  - 不进入下一流程，输出默认无异常文本和结构化结果。

## Flow 01 输出重点

输出要体现以下分析步骤，但表达由模型按现场情况组织：

1. 异常触发来源和当前对象。
2. WIP 指标事实与阈值对比。
3. 该现象在工厂流程中的含义：只是发现现象，还需要确认口径。
4. 当前是否满足 WIP Bubble / 严重 WIP Bubble 触发条件。
5. 如果满足，建议进入 Flow 02 异常确认。
