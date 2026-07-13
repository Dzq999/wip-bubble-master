select s.stage_name,
       SUM(IF(s.lot_state IN ('hold', 'running hold', 'inventory hold'), s.wafer_qty, 0)) as hold_wip,
       SUM(IF(s.lot_state IN ('running'), s.wafer_qty, 0)) as run_wip
from aifab.dim_wip_lot_rt s
         left join
     (select stage_name as stage_code, sum(target_wip) as plan_total_wip_qty
      from aifab.dim_wip_target
      group by stage_name) target
     on s.stage_name = target.stage_code
where s.stage_name = %s
group by s.stage_name;
