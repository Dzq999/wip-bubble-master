-- 当前stage 下 所有机台当天 操作效率（OE） (生产时间  (run_dur_h) / 运行时间(run_dur_h + idle_dur_h) )
-- 生产时间 : state  =  '正常生产' (BACKUP,ENG,NPW,PW,RECYLE,RUN,TD)
-- 闲置时间 : state  =  '闲置时间' (IDLE,UP)
-- 运行时间 : 没有down机    取 run + idle  的总时间total_hour_h
select concat(100 * round((sum(
                                   `run_dur_h#v1`) +
                           sum(
                                   `idle_dur_h#v1`)) /
                          (count(eqp_name) * timestampdiff(SECOND, (date_trunc('DAY', current_timestamp -
                                                                                      interval 7 hour -
                                                                                      interval 30 minute)) +
                                                                   interval 7 hour + interval 30 minute,
                                                           current_timestamp) / 3600), 2),
              '%')                                                         ae_ratio            -- 可用性效率 , Availability Efficiency
     , concat(100 * round(sum(`run_dur_h#v1`)
                              /
                          (timestampdiff(SECOND, (date_trunc('DAY', current_timestamp -
                                                                    interval 7 hour -
                                                                    interval 30 minute)) +
                                                 interval 7 hour + interval 30 minute,
                                         current_timestamp) / 3600 * count(eqp_name)), 2),
              '%')                                                         oe_ratio            -- 操作效率, Operational Efficiency
     , round(sum(
        `run_dur_h#v1`))                                                   current_run_dur_h   -- 当前所有设备正常生产运行时间总和
     , round(sum(
        `idle_dur_h#v1`))                                                  current_idle_dur_h  -- 当前所有设备闲置时间总和
     , count(eqp_name)                                                     eqp_count           -- 当前stage下相同能力的 eqp 数量
     , count(eqp_name) * round(timestampdiff(SECOND, (date_trunc('DAY', current_timestamp -
                                                                        interval 7 hour -
                                                                        interval 30 minute)) +
                                                     interval 7 hour + interval 30 minute,
                                             current_timestamp) / 3600) as current_total_dur_h -- 当前所有设备总时间加和  =  运行时间
from (select eqp.eqp_name,
             ifnull(`cur_state#v1`, dim.state_name) as `cur_state#v1`,
             if(`cur_state#v1` = '正常生产',
                `run_dur_h#v1` +
                timestampdiff(second, ifnull(dur.biz_time, current_timestamp),
                              current_timestamp) / 3600,
                `run_dur_h#v1`)                     as `run_dur_h#v1`,
             if(`cur_state#v1` = '闲置时间' or `cur_state#v1` = '闲置',
                `idle_dur_h#v1` +
                timestampdiff(second, ifnull(dur.biz_time, current_timestamp),
                              current_timestamp) / 3600,
                `idle_dur_h#v1`)                    as `idle_dur_h#v1`,
             ifnull(concat(100 * round(if(`cur_state#v1` = '正常生产',
                                          `run_dur_h#v1` +
                                          timestampdiff(second, ifnull(dur.biz_time, current_timestamp),
                                                        current_timestamp) / 3600,
                                          `run_dur_h#v1`)
                                           /
                                       (timestampdiff(SECOND, (date_trunc('DAY', current_timestamp -
                                                                                 interval 7 hour -
                                                                                 interval 30 minute)) +
                                                              interval 7 hour + interval 30 minute,
                                                      current_timestamp) / 3600), 4),
                           '%'),
                    0)                                 oe_ratio, -- 每个机台的操作效率, Operational Efficiency
             current_timestamp                      as biz_time
      from (select eqp_name
            from aifab.dim_eqp_all_rt eqp
            where construct_type = 'Normal'
              and name <> 'DUMMY'
              and eqp.capability in
                  (select capability from aifab.dim_conf_flow_manu where stage_name = %s) -- 获取当前stage 能力 所匹配的所有机台
           ) eqp
               left join (select `unique_eqp_code#v1`,
                                 `run_dur_h#v1`,
                                 `idle_dur_h#v1`,
                                 biz_time
                          from (select from_unixtime(`_biz_ts_#v1` / 1000 + 27000)                                       biz_time,
                                       `unique_eqp_code#v1`,
                                       `_biz_ts_#v1`,
                                       `run_dur_h#v1`,  -- 从 th_eqp_state_his 状态累加
                                       `idle_dur_h#v1`, -- 从 th_eqp_state_his 状态累加
                                       row_number() over (partition by `unique_eqp_code#v1` order by `_biz_ts_#v1` desc) rn
                                from ffs_vfab_1.ads_ffs_feature_fact_eqp_rti rti
                                where `_biz_ts_#v1` >=
                                      unix_timestamp(date_trunc('DAY', current_timestamp - interval 1 day)) * 1000
                                  and `run_dur_h#v1` is not null
                                  and `idle_dur_h#v1` is not null) rnn

                          where 1 = 1
                            and rnn.rn = 1) dur
                         on eqp.eqp_name = dur.`unique_eqp_code#v1`
               left join (select `unique_eqp_code#v1`,
                                 `cur_state#v1`,
                                 `last_state#v1`,
                                 biz_time
                          from (select from_unixtime(`_biz_ts_#v1` / 1000 + 27000)                                       biz_time,
                                       `unique_eqp_code#v1`,
                                       `_biz_ts_#v1`,
                                       `cur_state#v1`,  -- 从 th_eqp_state_his 获取, 判断当前状态
                                       `last_state#v1`, -- 从 th_eqp_state_his 获取, 判断当前状态
                                       row_number() over (partition by `unique_eqp_code#v1` order by `_biz_ts_#v1` desc) rn
                                from ffs_vfab_1.ads_ffs_feature_fact_eqp_rti rti
                                where `_biz_ts_#v1` >=
                                      unix_timestamp(date_trunc('DAY', current_timestamp - interval 1 day)) * 1000
                                  and `cur_state#v1` is not null
                                  and `last_state#v1` is not null) rnn

                          where 1 = 1
                            and rnn.rn = 1) `state`
                         on `state`.`unique_eqp_code#v1` = eqp.eqp_name
               left join aifab.dim_eqp_all_rt dim on dim.eqp_name = eqp.eqp_name) uptime_agg
;

