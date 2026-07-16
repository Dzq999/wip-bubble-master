-- 当前stage 下 所有机台积压的lot 情况
select eqp_name,
       count_if(lot_state IN ('running'))                                                                   as running_lot_cnt,
       count_if(lot_state IN ('wait', 'reserved', 'finished'))                                              as wait_lot_cnt,
       count_if(lot_state IN ('hold', 'running hold', 'inventory hold'))                                    as hold_lot_cnt,
       count(*)                                                                                             as total_queuing_lot_cnt,
       GROUP_CONCAT(DISTINCT product_name SEPARATOR ',')                                                    AS product_list,
       CASE WHEN COUNT(*) >= 30 THEN TRUE ELSE FALSE END                                                    AS is_bottleneck,
       date_trunc('hour', current_timestamp - interval 30 minute) + interval 30 minute                      as etl_time,
       current_timestamp                                                                                       proc_time,
       date_format(date_trunc('day', current_timestamp - interval 7 hour - interval 30 minute), '%Y-%m-%d') as dt
from (
-- 每个lot最后一次派工时间 / 机台 / 状态 / 产品
         select t1.fab_id,
                lot_names,
                eqp_name,
                product_name,
                lot_state
         from (select fab_id,
                      send_time,
                      lot_names,
                      due_time,
                      eqp_name,
                      priority
               from (select fab_id,
                            send_time,
                            lot_names,
                            trim(json_query(lot_list, '$[0].dueTime'), '"') as                 due_time,
                            trim(json_query(lot_list, '$[0].eqpId'), '"')   as                 eqp_name,
                            priority,
                            row_number() over (partition by lot_names order by send_time desc) rn
                     from aifab.dwd_wip_lot_dispatch_rt
                     where 1 = 1
                       -- and send_time <= date_trunc('hour' , current_timestamp - interval 30 minute ) + interval 30 minute
                       and trim(json_query(lot_list, '$[0].eqpId'), '"') is not null
                     order by send_time desc) rnn
               where rnn.rn = 1
                 and lot_names in
                     (select lot_name from aifab.dim_wip_lot_rt where lot_state not in ('shipped', 'scrapped'))) t1
                  join aifab.dim_wip_lot_rt lot
                       on t1.lot_names = lot.lot_name) t2
where eqp_name in (select eqp_name
                   from aifab.dim_eqp_all_rt eqp
                   where construct_type = 'Normal'
                     and name <> 'DUMMY'
                     and eqp.capability in
                         (select capability from aifab.dim_conf_flow_manu where stage_name = %s))
group by eqp_name
;

