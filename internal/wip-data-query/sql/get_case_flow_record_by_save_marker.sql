SELECT *
FROM vfab_agent.fab_case_flow_record
WHERE case_id = %s
  AND current_flow_no = %s
  AND save_time = %s
ORDER BY id DESC
LIMIT 1
