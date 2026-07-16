-- 受影响的lot数量( queue - target)
select s.stage_name                                           -- 1. 异常对象(Stage)名称
     -- , ceil(SUM(IF(s.lot_state IN ('wait', 'reserved', 'finished'), wafer_qty, 0)) -
     --        max(plan_total_wip_qty)) as impact_lot_count -- 受影响的wafer数量( queue - target)
     , ceil(count_if(s.lot_state IN ('wait', 'reserved', 'finished')) -
            max(plan_total_wip_qty) / 25) as impact_lot_count -- 受影响的lot数量( queue - target)
from aifab.dim_wip_lot_rt s
         left join
     (select stage_name as stage_code, sum(target_wip) as plan_total_wip_qty
      from aifab.dim_wip_target
      group by stage_name) target
     on s.stage_name = target.stage_code
where stage_name = %s
group by s.stage_name;

