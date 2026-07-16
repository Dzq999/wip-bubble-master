-- wip占比
select s.stage_name                                                                                          -- 1. 异常对象(Stage)名称
     , SUM(IF(s.lot_state IN ('hold', 'running hold', 'inventory hold'), s.wafer_qty, 0)) hold_wip           -- hold
     , SUM(IF(s.lot_state IN ('running'), s.wafer_qty, 0))                                run_wip            -- run
from aifab.dim_wip_lot_rt s
         left join
     (select stage_name as stage_code, sum(target_wip) as plan_total_wip_qty
      from aifab.dim_wip_target
      group by stage_name) target
     on s.stage_name = target.stage_code
where stage_name = %s
group by s.stage_name;

