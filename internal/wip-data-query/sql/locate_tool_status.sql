-- active / down / pm 
select concat(sum(if(state_name = '正常生产', 1, 0)), ' / ', count(1))       as `active`           -- active
     , sum(if(state_name in ('计划宕机', '非计划宕机', '非计划时间'), 1, 0)) as hard_down          -- hard_down
     , sum(if(original_state = 'PM', 1, 0))                                  as `pm`               --   pm
     , ifnull(group_concat(if(state_name in ('计划宕机', '非计划宕机', '非计划时间'), eqp_name, null)),
              '无机台Down')                                                  as hard_dwon_eqp_list -- hard_down机台列表
     , ifnull(group_concat(if(original_state = 'PM', eqp_name, null)),
              '无机台PM')                                                    as pm_eqp_list        -- pm机台列表
from (select eqp_name
           , state_name
           , original_state
      from aifab.dim_eqp_all_rt eqp
      where construct_type = 'Normal'
        and name <> 'DUMMY'
        and eqp.capability in (select capability from aifab.dim_conf_flow_manu where stage_name = %s)) t;

