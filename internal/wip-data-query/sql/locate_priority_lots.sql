-- 查询受影响的 Hot Lot 和 Super Hot Lot数量
select stage_name,
                             priority,
                             count(1) lot_count
                      from (select stage_name,
                                   case
                                       when priority = 1 then 'Bullet lot'
                                       when priority = 2 then 'Super hot lot'
                                       when priority = 3 then 'Hot lot'
                                       when priority = 4 then 'Normal lot'
                                       when priority = 5 then 'Slow lot' end as priority,
                                   lot_state
                            from aifab.dim_wip_lot_rt) s
                      where stage_name = %s
                        and lot_state IN ('wait', 'reserved', 'finished')
                        and priority in ('Super hot lot', 'Hot lot')
                      group by stage_name, priority;

