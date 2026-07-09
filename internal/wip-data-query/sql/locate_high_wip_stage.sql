SELECT
  s.stage_name,
  SUM(CASE WHEN s.lot_state IN ('wait', 'reserved', 'finished') THEN s.wafer_qty ELSE 0 END) AS queue_wip,
  SUM(CASE WHEN s.lot_state IN ('wait', 'reserved', 'finished') THEN s.wafer_qty ELSE 0 END) /
    NULLIF(SUM(CASE WHEN s.lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold') THEN s.wafer_qty ELSE 0 END), 0)
    AS queue_actual_ratio,
  SUM(CASE WHEN s.lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold') THEN s.wafer_qty ELSE 0 END) AS actual_wip,
  MAX(target.plan_total_wip_qty) AS target_wip,
  SUM(CASE WHEN s.lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold') THEN s.wafer_qty ELSE 0 END) /
    NULLIF(MAX(target.plan_total_wip_qty), 0) AS wip_ratio,
  SUM(CASE WHEN s.lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold') THEN s.wafer_qty ELSE 0 END) -
    MAX(target.plan_total_wip_qty) AS wip_gap,
  SUM(CASE WHEN s.lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold') THEN s.wafer_qty ELSE 0 END) /
    NULLIF(MAX(target.plan_total_wip_qty), 0) - 1 AS wip_gap_rate,
  NOW() AS update_time,
  MAX(s.updated_time) AS biz_time
FROM aifab.dim_wip_lot_rt s
LEFT JOIN (
  SELECT stage_name AS stage_code, SUM(target_wip) AS plan_total_wip_qty
  FROM aifab.dim_wip_target
  GROUP BY stage_name
) target ON s.stage_name = target.stage_code
GROUP BY s.stage_name
ORDER BY wip_ratio DESC, wip_gap DESC
LIMIT 1
