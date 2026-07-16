-- 数仓按stage查询当前actual wip/ target wip 及比率
select s.stage_name                                                                                   -- 1. 异常对象(Stage)名称
                       , SUM(IF(s.lot_state IN ('wait', 'reserved', 'finished'), s.wafer_qty, 0)) as `queue_wip`        -- 5. Queue值(mes中等待分为'wait', 'reserved', 'finished')
                       , SUM(IF(s.lot_state IN ('wait', 'reserved', 'finished'), s.wafer_qty, 0)) /
                         SUM(IF(lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold',
                                              'inventory hold'),
                                wafer_qty,
                                0))                                                               as queue_actual_ratio -- 5. Queue值占比     Queue / actual
                       , SUM(IF(
            lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
            wafer_qty,
            0))                                                                                   as actual_wip         -- 2. 实际在制品晶圆数
                       , max(plan_total_wip_qty)                                                  as `target_wip`       -- 3. 理论在制品晶圆数
                       , SUM(IF(
            lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
            wafer_qty, 0)) /
                         max(plan_total_wip_qty)                                                  as `wip_ratio`        -- 4. WIP 在制品晶圆数实际与理论比
                       , SUM(IF(
            lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
            wafer_qty, 0)) -
                         max(plan_total_wip_qty)                                                  as wip_gap            -- 4. WIP Gap值 实际 - 理论
                       , SUM(IF(
            lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold'),
            wafer_qty, 0)) / max(plan_total_wip_qty) - 1                                          as wip_gap_rate
                       , now()                                                                    as `update_time`      -- 6. 当前查询时间
                       , max(s.updated_time)                                                      as `biz_time`
                  from aifab.dim_wip_lot_rt s
                           left join
                       (select stage_name as stage_code, sum(target_wip) as plan_total_wip_qty
                        from aifab.dim_wip_target
                        group by stage_name) target
                       on s.stage_name = target.stage_code
                  group by s.stage_name
                  having (SUM(IF(lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold',
                                               'inventory hold'),
                                 wafer_qty, 0)) / max(plan_total_wip_qty)) > 1.5
                  order by (SUM(IF(lot_state IN
                                   ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold',
                                    'inventory hold'),
                                   wafer_qty, 0)) / max(plan_total_wip_qty)) desc
                  limit 1;

