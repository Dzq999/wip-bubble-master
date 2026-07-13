select lot_count_this_week,
       lot_count_last_week,
       concat(round(move_out_ratio * 100, 2), '%%') as move_out_ratio,
       if(move_out_ratio < 1.15, '未明显突增', '有明显突增') as move_out_comment
from (select max(lot_count_this_week) / greatest(max(lot_count_last_week), 1) as move_out_ratio,
             max(lot_count_this_week)                                         as lot_count_this_week,
             max(lot_count_last_week)                                         as lot_count_last_week
      from (select count(distinct lot_name) as lot_count_this_week,
                   null                     as lot_count_last_week
            from aifab.dwd_wip_lot_step_his_rt
            where step_out_time is not null
              and stage_name = %s
              and last_updated_time >= current_timestamp - interval 1 week
            union
            select null                     as lot_count_this_week,
                   count(distinct lot_name) as lot_count_last_week
            from aifab.dwd_wip_lot_step_his_rt
            where step_out_time is not null
              and stage_name = %s
              and last_updated_time >= current_timestamp - interval 2 week
              and last_updated_time < current_timestamp - interval 1 week) t1) t2;

