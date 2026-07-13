select cast(concat(count(distinct if(state_name = '正常生产', eqp_name, null)), ' / ', count(distinct eqp_name)) as char) as active,
       count(distinct if(state_name = '正常生产', eqp_name, null))                          as tool_active_count,
       count(distinct eqp_name)                                                            as tool_total_count,
       count(distinct if(state_name in ('计划宕机', '非计划宕机', '非计划时间'), eqp_name, null)) as hard_down,
       count(distinct if(original_state = 'PM', eqp_name, null))                            as pm,
       ifnull(group_concat(distinct if(state_name in ('计划宕机', '非计划宕机', '非计划时间'), eqp_name, null)), '无机台') as hard_down_eqp_list,
       ifnull(group_concat(distinct if(original_state = 'PM', eqp_name, null)), '无机台') as pm_eqp_list,
       concat(round(count(distinct if(state_name = '正常生产', eqp_name, null)) / greatest(count(distinct eqp_name), 1) * 100, 2), '%%') as tool_uptime
from (select eqp_name,
             state_name,
             original_state
      from aifab.dim_eqp_all_rt eqp
      where construct_type = 'Normal'
        and name <> 'DUMMY'
        and eqp.capability in (select capability
                               from aifab.dim_conf_flow_manu
                               where stage_name = %s)) t;
