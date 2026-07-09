UPDATE vfab_agent.fab_case_flow_record
SET issue_type = %s,
    flow_status = %s,
    case_status = %s,
    current_flow_name = %s,
    next_flow_no = %s,
    next_flow_name = %s,
    flow_data_json = %s,
    save_time = %s
WHERE case_id = %s
  AND current_flow_no = %s
