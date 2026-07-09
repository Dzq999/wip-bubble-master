SELECT *
FROM vfab_agent.fab_case_flow_record
WHERE case_id = %s
ORDER BY id DESC
LIMIT 1
