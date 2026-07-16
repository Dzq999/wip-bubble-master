# 离线 Case 数据快照

`case_data_snapshot.json` 由仓库根目录 `生产环境当前高wip的stage定位及排查csv_外发/` 的 11 个 CSV 整理而来。

该文件保持 `case_data_snapshot.sql_results` 结构，可用于无数据库权限的内网离线测试。运行请求携带 `offline_data=true`，或消息包含“使用离线数据”时，总控只读取该文件，不连接 MySQL。
