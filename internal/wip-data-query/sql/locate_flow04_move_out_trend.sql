SELECT
  lot_count_this_week,
  lot_count_last_week,
  CONCAT(ROUND(move_out_ratio * 100, 2), '%%') AS move_out_ratio_pct,
  IF(move_out_ratio < 1.15, '未明显突增', '有明显突增') AS move_out_comment
FROM (
  SELECT
    MAX(lot_count_this_week) AS lot_count_this_week,
    MAX(lot_count_last_week) AS lot_count_last_week,
    MAX(lot_count_this_week) / NULLIF(MAX(lot_count_last_week), 0) AS move_out_ratio
  FROM (
    SELECT
      COUNT(DISTINCT lot_name) AS lot_count_this_week,
      NULL AS lot_count_last_week
    FROM aifab.dwd_wip_lot_step_his_rt
    WHERE step_out_time IS NOT NULL
      AND stage_name = %s
      AND last_updated_time >= CURRENT_TIMESTAMP - INTERVAL 1 WEEK
    UNION ALL
    SELECT
      NULL AS lot_count_this_week,
      COUNT(DISTINCT lot_name) AS lot_count_last_week
    FROM aifab.dwd_wip_lot_step_his_rt
    WHERE step_out_time IS NOT NULL
      AND stage_name = %s
      AND last_updated_time >= CURRENT_TIMESTAMP - INTERVAL 2 WEEK
      AND last_updated_time < CURRENT_TIMESTAMP - INTERVAL 1 WEEK
  ) t1
) t2;
