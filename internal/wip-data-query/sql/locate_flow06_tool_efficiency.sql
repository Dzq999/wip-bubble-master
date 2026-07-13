select concat(round(sum(`run_dur_h#v1`) / greatest(sum(`run_dur_h#v1`) + sum(`idle_dur_h#v1`), 1) * 100, 2), '%%') as ae_ratio,
       concat(round(sum(`run_dur_h#v1`) / greatest(sum(`run_dur_h#v1`) + sum(`idle_dur_h#v1`), 1) * 100, 2), '%%') as oe_ratio,
       round(sum(`run_dur_h#v1`), 2)                                                                        as current_run_dur_h,
       round(sum(`idle_dur_h#v1`), 2)                                                                       as current_idle_dur_h,
       count(distinct `unique_eqp_code#v1`)                                                                 as eqp_count,
       round(sum(`run_dur_h#v1`) + sum(`idle_dur_h#v1`), 2)                                                  as current_total_dur_h
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
  and `_biz_ts_#v1` >= (unix_timestamp(timestamp(date(current_timestamp - interval 7 hour - interval 30 minute)) + interval 7 hour + interval 30 minute) * 1000);


