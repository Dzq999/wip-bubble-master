SELECT
  stage_name,
  priority,
  COUNT(1) AS lot_count
FROM (
  SELECT
    stage_name,
    CASE
      WHEN priority = 1 THEN 'Bullet lot'
      WHEN priority = 2 THEN 'Super hot lot'
      WHEN priority = 3 THEN 'Hot lot'
      WHEN priority = 4 THEN 'Normal lot'
      WHEN priority = 5 THEN 'Slow lot'
    END AS priority,
    lot_state
  FROM aifab.dim_wip_lot_rt
) s
WHERE stage_name = %s
  AND lot_state IN ('wait', 'reserved', 'finished')
  AND priority IN ('Super hot lot', 'Hot lot')
GROUP BY stage_name, priority;
