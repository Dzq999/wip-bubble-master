SELECT
  next_stage_name,
  SUM(IF(
    lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
    wafer_qty,
    0
  )) AS actual_wip,
  MAX(plan_total_wip_qty) AS target_wip,
  SUM(IF(
    lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
    wafer_qty,
    0
  )) / NULLIF(MAX(plan_total_wip_qty), 0) AS wip_ratio,
  CASE
    WHEN SUM(IF(
      lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
      wafer_qty,
      0
    )) / NULLIF(MAX(plan_total_wip_qty), 0) <= 1 THEN 'Starvation'
    ELSE 'Need Further Review'
  END AS if_starved
FROM (
  SELECT
    stage_name,
    LEAD(stage_name, 1, NULL) OVER (ORDER BY stage_sequence) AS next_stage_name
  FROM (
    SELECT stage_name, MIN(rn) AS stage_sequence
    FROM (
      SELECT
        stage_name,
        seq,
        ROW_NUMBER() OVER (ORDER BY seq) AS rn
      FROM aifab.dim_conf_flow_manu
    ) t2
    GROUP BY stage_name
    ORDER BY MIN(rn)
  ) t3
) t4
JOIN aifab.dim_wip_lot_rt dim
  ON dim.stage_name = t4.next_stage_name
LEFT JOIN (
  SELECT stage_name AS stage_code, SUM(target_wip) AS plan_total_wip_qty
  FROM aifab.dim_wip_target
  GROUP BY stage_name
) target
  ON dim.stage_name = target.stage_code
WHERE t4.stage_name = %s
GROUP BY next_stage_name;
