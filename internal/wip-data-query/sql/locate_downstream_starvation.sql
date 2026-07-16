-- 获取下游stage , 判断下游是否存在starvation
select next_stage_name,
       SUM(IF(
               lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
               wafer_qty,
               0))                        as actual_wip,
       max(plan_total_wip_qty)            as `target_wip`,
       SUM(IF(
               lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
               wafer_qty, 0)) /
       max(plan_total_wip_qty)            as `wip_ratio`,
       case
           when SUM(IF(
                   lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
                   wafer_qty, 0)) /
                max(plan_total_wip_qty) <= 1 then 'Starvation'
           else 'Need Further Review' end as if_starved
from (select stage_name,
             lead(stage_name, 1, null) over ( order by stage_sequence) as next_stage_name
      from (select stage_name, min(rn) stage_sequence
            from (select stage_name,
                         seq,
                         row_number() over ( order by seq) rn
                  from aifab.dim_conf_flow_manu) t2
            group by stage_name
            order by min(rn)) t3) t4
         join aifab.dim_wip_lot_rt dim
              on dim.stage_name = t4.next_stage_name
         left join
     (select stage_name as stage_code, sum(target_wip) as plan_total_wip_qty
      from aifab.dim_wip_target
      group by stage_name) target
     on dim.stage_name = target.stage_code
where t4.stage_name = %s
group by next_stage_name;

