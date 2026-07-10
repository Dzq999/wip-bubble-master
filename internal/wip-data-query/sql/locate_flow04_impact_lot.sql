SELECT
  s.stage_name,
  CEIL(
    SUM(IF(s.lot_state IN ('wait', 'reserved', 'finished'), 1, 0))
    - MAX(plan_total_wip_qty) / 25
  ) AS impact_lot_count
FROM aifab.dim_wip_lot_rt s
LEFT JOIN (
  SELECT stage_name AS stage_code, SUM(target_wip) AS plan_total_wip_qty
  FROM aifab.dim_wip_target
  GROUP BY stage_name
) target
  ON s.stage_name = target.stage_code
WHERE s.stage_name = %s
GROUP BY s.stage_name;
