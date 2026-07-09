SELECT *
FROM vfab_agent.fab_case_flow_record
WHERE case_status IN ('Pending', 'Processing', 'On Hold')
  AND (%s IS NULL OR case_id = %s)
  AND (%s IS NULL OR next_flow_no = %s)
  AND (%s IS NULL OR current_flow_no = %s)
ORDER BY COALESCE(save_time, '1970-01-01') DESC, id DESC
LIMIT 1
