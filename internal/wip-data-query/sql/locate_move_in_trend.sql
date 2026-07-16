-- move in
select lot_count_this_week,
       lot_count_last_week,
       concat(round(move_in_ratio * 100, 2), '%')  move_in_ratio ,  -- 本周 / 上周 move in
       if(move_in_ratio < 1.15, '未明显突增', '有明显突增') move_in_comment, -- move_in 是否明显突增
       concat(round(move_in_ratio * 100, 2) - 100, '%')  move_in_inc_ratio  -- 本周 / 上周 move in 变化率
from (select max(lot_count_this_week)                            as lot_count_this_week,
             max(lot_count_last_week)                            as lot_count_last_week,
             max(lot_count_this_week) / max(lot_count_last_week) as move_in_ratio
      from (select count(distinct lot_name) as lot_count_this_week,
                   null                     as lot_count_last_week
            from aifab.dwd_wip_lot_step_his_rt
            where 1 = 1
              and step_in_time is not null
              and stage_name = %s
              and last_updated_time >= current_timestamp - interval 1 week
            union
            select null                     as lot_count_this_week,
                   count(distinct lot_name) as lot_count_last_week
            from aifab.dwd_wip_lot_step_his_rt
            where 1 = 1
              and step_in_time is not null
              and stage_name = %s
              and last_updated_time >= current_timestamp - interval 2 week
              and last_updated_time
                < current_timestamp - interval 1 week) t1) t2;

