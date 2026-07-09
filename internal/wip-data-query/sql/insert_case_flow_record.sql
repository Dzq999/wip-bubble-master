INSERT INTO vfab_agent.fab_case_flow_record
  (case_id, issue_type, flow_status, case_status, current_flow_no, current_flow_name,
   next_flow_no, next_flow_name, flow_data_json, save_time)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
