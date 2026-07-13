select `unique_eqp_code#v1` as eqp_name,
       `cur_state#v1`       as cur_state,
       `last_state#v1`      as last_state,
       round(sum(`run_dur_h#v1`), 2)  as run_dur_h,
       round(sum(`idle_dur_h#v1`), 2) as idle_dur_h,
       concat(round(sum(`run_dur_h#v1`) / greatest(sum(`run_dur_h#v1`) + sum(`idle_dur_h#v1`), 1) * 100, 2), '%%') as oe_ratio
from ffs_vfab_1.ads_ffs_feature_fact_eqp_rti
where `unique_eqp_code#v1` in (
    select eqp_name
    from aifab.dim_eqp_all_rt eqp
    where construct_type = 'Normal'
      and name <> 'DUMMY'
      and eqp.capability in (select capability
                             from aifab.dim_conf_flow_manu
                             where stage_name = %s)
)
  and `_biz_ts_#v1` >= (unix_timestamp(timestamp(date(current_timestamp - interval 7 hour - interval 30 minute)) + interval 7 hour + interval 30 minute) * 1000)
group by `unique_eqp_code#v1`, `cur_state#v1`, `last_state#v1`
order by `unique_eqp_code#v1`;


