-- DNW-ANN   各  product数量 /    queue 占比   / 可加工的机台列表
select lot.product_name,
       lot.stage_name,   -- wip的产品
       product_cnt as product_queue_cnt,   -- wip的各产品数量
       eqp.eqp_names as eqp_list,   -- 可加工的机台
       eligible_eqp,   -- 机台 数量
       product_queue_percent  -- queue 占比
from (select product_name,
             stage_name,          -- wip的产品
             count(1) product_cnt, -- wip的各产品数量
             concat( round(count(1) / sum(count(1)) over(partition by stage_name) * 100,2)   , '%' )  product_queue_percent
      from dim_wip_lot_rt lot

      where lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold',
                          'inventory hold')
      group by product_name, stage_name) lot
         join dim_conf_product prd on prd.product_id = lot.product_name
         join dim_conf_flow_manu flow
              on flow.flow_id = prd.flow_id
         join (select group_concat(eqp_name separator ' ') as eqp_names , concat(count(eqp_name) , ' / ' , count(eqp_name)) as eligible_eqp
                    , capability
               from aifab.dim_eqp_all_rt eqp
               where construct_type = 'Normal'
                 and name <> 'DUMMY'
               group by capability) eqp
              on flow.capability = eqp.capability
where lot.stage_name = %s
  and flow.stage_name = %s;

