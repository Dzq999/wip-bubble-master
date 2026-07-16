#!/usr/bin/env python
"""Whitelisted MySQL access for the WIP Bubble demo skills."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
import re
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
CONFIG_PATH = CONFIG_DIR / "db_config.json"
SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
SQL_FILES = {
    "locate_high_wip_stage",
    "locate_downstream_starvation",
    "locate_priority_lots",
    "locate_impact_lot",
    "locate_move_out_trend",
    "locate_wip_hold_run",
    "locate_tool_status",
    "locate_tool_dispatch",
    "locate_tool_efficiency",
    "locate_product_tool_profile",
    "locate_tool_efficiency_detail",
    "locate_move_in_trend",
            "collect_case_data_snapshot",
            "get_latest_active_case",
    "get_case_record",
    "get_case_flow_record",
    "update_case_flow_record",
    "insert_case_flow_record",
    "get_case_flow_record_by_save_marker",
}

CASE_DATA_SNAPSHOT_VERSION = "case-data-snapshot-v1"
OFFLINE_SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "offline-data" / "production-high-wip-stage" / "case_data_snapshot.json"


def load_offline_case_data_snapshot() -> Dict[str, Any]:
    """Load the pre-exported production SQL snapshot without opening a database connection."""
    if not OFFLINE_SNAPSHOT_PATH.exists():
        raise FileNotFoundError(f"Offline case data snapshot not found: {OFFLINE_SNAPSHOT_PATH}")
    raw = json.loads(OFFLINE_SNAPSHOT_PATH.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise ValueError("Offline case data snapshot must be a JSON object")
    snapshot = canonicalize_case_data_snapshot(raw)
    snapshot["data_mode"] = "offline"
    return snapshot

LEGACY_SQL_RESULT_KEYS = {
    "locate_priority_lots": "locate_flow03_priority_lots",
    "locate_impact_lot": "locate_flow04_impact_lot",
    "locate_move_out_trend": "locate_flow04_move_out_trend",
    "locate_wip_hold_run": "locate_flow06_wip_hold_run",
    "locate_tool_status": "locate_flow06_tool_status",
    "locate_tool_dispatch": "locate_flow06_tool_dispatch",
    "locate_tool_efficiency": "locate_flow06_tool_efficiency",
    "locate_product_tool_profile": "locate_flow06_product_tool_profile",
    "locate_tool_efficiency_detail": "locate_flow06_tool_efficiency_detail",
    "locate_move_in_trend": "locate_flow06_move_in_trend",
}

def canonicalize_case_data_snapshot(snapshot: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Read legacy Flow-grouped snapshots while persisting only the canonical sql_results shape."""
    if not isinstance(snapshot, dict):
        return {}
    normalized = dict(snapshot)
    sql_results = dict(snapshot.get("sql_results") or {})
    for canonical_key, legacy_key in LEGACY_SQL_RESULT_KEYS.items():
        if canonical_key not in sql_results and legacy_key in sql_results:
            sql_results[canonical_key] = sql_results[legacy_key]
    legacy_groups = {key: value for key, value in snapshot.items() if isinstance(value, dict)}
    flow01 = legacy_groups.get("flow01", {})
    flow03 = legacy_groups.get("flow03", {})
    flow04 = legacy_groups.get("flow04", {})
    flow06 = legacy_groups.get("flow06", {})
    fallbacks = {
        "locate_high_wip_stage": flow01.get("warehouse_high_wip"),
        "locate_downstream_starvation": flow01.get("downstream_starvation") or flow03.get("downstream_starvation"),
        "locate_priority_lots": flow03.get("priority_lots"),
        "locate_impact_lot": flow04.get("impact_lot"),
        "locate_move_out_trend": flow04.get("move_out_trend") or flow06.get("move_out_trend"),
        "locate_wip_hold_run": flow06.get("wip_hold_run"),
        "locate_tool_status": flow06.get("tool_status"),
        "locate_tool_efficiency": flow06.get("tool_efficiency"),
        "locate_tool_dispatch": flow06.get("tool_dispatch"),
        "locate_product_tool_profile": flow06.get("product_tool_profile"),
        "locate_move_in_trend": flow06.get("move_in_trend"),
    }
    for key, value in fallbacks.items():
        if key not in sql_results and value not in (None, "", [], {}):
            sql_results[key] = value
    normalized["sql_results"] = sql_results
    return normalized


def _load_pymysql():
    try:
        import pymysql  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "Missing dependency 'pymysql'. Install it in the FaaS/runtime environment "
            "or provide an equivalent MySQL client wrapper."
        ) from exc
    return pymysql


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ")
    return str(value)


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=_json_default, indent=2)


def _load_file_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Database config file not found: {CONFIG_PATH}")
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    return data.get("mysql", data)


def sql_dialect() -> str:
    return str(_load_file_config().get("sql_dialect", "production")).strip().lower()


def is_local_mysql_dialect() -> bool:
    return sql_dialect() == "mysql_local"


def db_config() -> Dict[str, Any]:
    file_config = _load_file_config()
    config = {
        "host": str(file_config.get("host", "127.0.0.1")),
        "port": int(file_config.get("port", 3306)),
        "user": str(file_config.get("user", "root")),
        "password": str(file_config.get("password", "1234")),
        "charset": str(file_config.get("charset", "utf8mb4")),
        "autocommit": True,
    }
    database = str(file_config.get("database") or "").strip()
    if database:
        config["database"] = database
    return config


def _adapt_production_sql_for_local_mysql(name: str, sql: str) -> str:
    """Translate only production-engine functions unsupported by local MySQL."""
    if not is_local_mysql_dialect():
        return sql

    if name == "locate_impact_lot":
        sql = sql.replace(
            "count_if(s.lot_state IN ('wait', 'reserved', 'finished'))",
            "SUM(IF(s.lot_state IN ('wait', 'reserved', 'finished'), 1, 0))",
        )
    if name == "locate_tool_dispatch":
        replacements = {
            "count_if(lot_state IN ('running'))": "SUM(IF(lot_state IN ('running'), 1, 0))",
            "count_if(lot_state IN ('wait', 'reserved', 'finished'))": "SUM(IF(lot_state IN ('wait', 'reserved', 'finished'), 1, 0))",
            "count_if(lot_state IN ('hold', 'running hold', 'inventory hold'))": "SUM(IF(lot_state IN ('hold', 'running hold', 'inventory hold'), 1, 0))",
            "trim(json_query(lot_list, '$[0].dueTime'), '\"')": "JSON_UNQUOTE(JSON_EXTRACT(lot_list, '$[0].dueTime'))",
            "trim(json_query(lot_list, '$[0].eqpId'), '\"')": "JSON_UNQUOTE(JSON_EXTRACT(lot_list, '$[0].eqpId'))",
            "date_trunc('hour', current_timestamp - interval 30 minute)": "TIMESTAMP(DATE_FORMAT(CURRENT_TIMESTAMP - INTERVAL 30 MINUTE, '%Y-%m-%d %H:00:00'))",
            "date_trunc('day', current_timestamp - interval 7 hour - interval 30 minute)": "TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 7 HOUR - INTERVAL 30 MINUTE))",
        }
        for source, target in replacements.items():
            sql = sql.replace(source, target)
    if name == "locate_tool_efficiency":
        # The production aggregate references aliases and date_trunc semantics that MySQL does not support.
        # This local-only equivalent preserves the same six output fields for the demo database.
        return """
SELECT
  CONCAT(ROUND((SUM(COALESCE(r.run_dur_h, 0)) + SUM(COALESCE(r.idle_dur_h, 0))) /
    GREATEST(COUNT(DISTINCT e.eqp_name) * (TIMESTAMPDIFF(SECOND,
      TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 7 HOUR - INTERVAL 30 MINUTE)) + INTERVAL 7 HOUR + INTERVAL 30 MINUTE,
      CURRENT_TIMESTAMP) / 3600), 1) * 100, 2), '%') AS ae_ratio,
  CONCAT(ROUND(SUM(COALESCE(r.run_dur_h, 0)) /
    GREATEST(COUNT(DISTINCT e.eqp_name) * (TIMESTAMPDIFF(SECOND,
      TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 7 HOUR - INTERVAL 30 MINUTE)) + INTERVAL 7 HOUR + INTERVAL 30 MINUTE,
      CURRENT_TIMESTAMP) / 3600), 1) * 100, 2), '%') AS oe_ratio,
  ROUND(SUM(COALESCE(r.run_dur_h, 0))) AS current_run_dur_h,
  ROUND(SUM(COALESCE(r.idle_dur_h, 0))) AS current_idle_dur_h,
  COUNT(DISTINCT e.eqp_name) AS eqp_count,
  COUNT(DISTINCT e.eqp_name) * ROUND(TIMESTAMPDIFF(SECOND,
    TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 7 HOUR - INTERVAL 30 MINUTE)) + INTERVAL 7 HOUR + INTERVAL 30 MINUTE,
    CURRENT_TIMESTAMP) / 3600) AS current_total_dur_h
FROM aifab.dim_eqp_all_rt e
LEFT JOIN (
  SELECT `unique_eqp_code#v1` AS eqp_name, `run_dur_h#v1` AS run_dur_h, `idle_dur_h#v1` AS idle_dur_h
  FROM (
    SELECT `unique_eqp_code#v1`, `run_dur_h#v1`, `idle_dur_h#v1`,
           ROW_NUMBER() OVER (PARTITION BY `unique_eqp_code#v1` ORDER BY `_biz_ts_#v1` DESC) AS rn
    FROM ffs_vfab_1.ads_ffs_feature_fact_eqp_rti
    WHERE `_biz_ts_#v1` >= UNIX_TIMESTAMP(TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 1 DAY))) * 1000
  ) latest
  WHERE rn = 1
) r ON r.eqp_name = e.eqp_name
WHERE e.construct_type = 'Normal'
  AND e.name <> 'DUMMY'
  AND e.capability IN (SELECT capability FROM aifab.dim_conf_flow_manu WHERE stage_name = %s)
""".strip()
    if name in {"locate_tool_efficiency", "locate_tool_efficiency_detail"}:
        replacements = {
            "date_trunc('DAY', current_timestamp - interval 7 hour - interval 30 minute)": "TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 7 HOUR - INTERVAL 30 MINUTE))",
            "date_trunc('DAY', current_timestamp - interval 1 day)": "TIMESTAMP(DATE(CURRENT_TIMESTAMP - INTERVAL 1 DAY))",
        }
        for source, target in replacements.items():
            sql = sql.replace(source, target)
    return sql


def _escape_literal_percent_for_pymysql(sql: str) -> str:
    return re.sub(r"%(?![%s])", "%%", sql)


def load_sql(name: str) -> str:
    if name not in SQL_FILES:
        raise ValueError(f"Unsupported SQL action: {name}")
    path = SQL_DIR / f"{name}.sql"
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    production_sql = path.read_text(encoding="utf-8-sig").strip()
    return _escape_literal_percent_for_pymysql(_adapt_production_sql_for_local_mysql(name, production_sql))


@contextmanager
def connection():
    pymysql = _load_pymysql()
    conn = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config())
    try:
        yield conn
    finally:
        conn.close()


def fetch_one(sql: str, params: Optional[Iterable[Any]] = None) -> Optional[Dict[str, Any]]:
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params or ()))
            return cursor.fetchone()


def fetch_all(sql: str, params: Optional[Iterable[Any]] = None) -> list[Dict[str, Any]]:
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params or ()))
            return list(cursor.fetchall())


def execute(sql: str, params: Optional[Iterable[Any]] = None) -> int:
    with connection() as conn:
        with conn.cursor() as cursor:
            affected = cursor.execute(sql, tuple(params or ()))
            return int(affected)


def locate_high_wip_stage() -> Optional[Dict[str, Any]]:
    """Find the stage with the highest WIP ratio and leave status classification to Flow 01."""
    return fetch_one(load_sql("locate_high_wip_stage"))


def locate_downstream_starvation(stage_name: str) -> Optional[Dict[str, Any]]:
    """Return raw downstream stage WIP/starvation metrics for a stage."""
    return fetch_one(load_sql("locate_downstream_starvation"), (stage_name,))


def _count_with_cursor(cursor: Any, sql: str, params: Iterable[Any] = ()) -> int:
    cursor.execute(sql, tuple(params))
    row = cursor.fetchone() or {}
    value = next(iter(row.values()), 0)
    return int(value or 0)


def _fetch_scalar_with_cursor(cursor: Any, sql: str, params: Iterable[Any] = ()) -> Any:
    cursor.execute(sql, tuple(params))
    row = cursor.fetchone() or {}
    return next(iter(row.values()), None)


def _insert_wip_lot_rows(cursor: Any, rows: list[tuple[str, int, str, int]]) -> None:
    cursor.execute("SHOW COLUMNS FROM aifab.dim_wip_lot_rt")
    existing_columns = {str(row.get("Field")) for row in cursor.fetchall()}
    preferred_columns = [
        "fab_id",
        "lot_name",
        "stage_name",
        "lot_state",
        "wafer_qty",
        "priority",
        "product_name",
        "updated_time",
    ]
    insert_columns = [column for column in preferred_columns if column in existing_columns]
    timestamp = datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    values = []
    for index, (stage_name, priority, lot_state, wafer_qty) in enumerate(rows, start=1):
        lot_name = f"DEMO-{stage_name}-{priority}-{lot_state}-{index}-{timestamp.replace(' ', '-') }"
        value_by_column = {
            "fab_id": "FAB1",
            "lot_name": lot_name[:64],
            "stage_name": stage_name,
            "lot_state": lot_state,
            "wafer_qty": wafer_qty,
            "priority": priority,
            "product_name": "DEMO_PRODUCT",
            "updated_time": timestamp,
        }
        values.append(tuple(value_by_column[column] for column in insert_columns))
    column_sql = ", ".join(insert_columns)
    placeholder_sql = ", ".join(["%s"] * len(insert_columns))
    cursor.executemany(
        f"INSERT INTO aifab.dim_wip_lot_rt ({column_sql}) VALUES ({placeholder_sql})",
        values,
    )


def ensure_flow03_demo_data(stage_name: str, downstream_stage_name: str = "PW-PH") -> Dict[str, Any]:
    """Create the minimal local aifab demo tables/data used by Flow 03 when absent."""
    current_stage = (stage_name or "DNW-ANN").strip() or "DNW-ANN"
    downstream_stage = (downstream_stage_name or "PW-PH").strip() or "PW-PH"
    seeded: list[str] = []
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS aifab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aifab.dim_wip_lot_rt (
                  stage_name VARCHAR(128) NOT NULL,
                  priority INT NULL,
                  lot_state VARCHAR(64) NULL,
                  wafer_qty DECIMAL(18,4) DEFAULT 0,
                  updated_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                  KEY idx_dim_wip_lot_rt_stage (stage_name),
                  KEY idx_dim_wip_lot_rt_priority_state (priority, lot_state)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aifab.dim_conf_flow_manu (
                  stage_name VARCHAR(128) NOT NULL,
                  seq INT NOT NULL,
                  KEY idx_dim_conf_flow_manu_stage (stage_name),
                  KEY idx_dim_conf_flow_manu_seq (seq)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aifab.dim_wip_target (
                  stage_name VARCHAR(128) NOT NULL,
                  target_wip DECIMAL(18,4) DEFAULT 0,
                  KEY idx_dim_wip_target_stage (stage_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            flow_count = _count_with_cursor(cursor, "SELECT COUNT(1) AS cnt FROM aifab.dim_conf_flow_manu")
            if flow_count == 0:
                cursor.execute(
                    "INSERT INTO aifab.dim_conf_flow_manu (stage_name, seq) VALUES (%s, %s), (%s, %s)",
                    (current_stage, 100, downstream_stage, 110),
                )
                seeded.append("dim_conf_flow_manu")
            else:
                stage_route_count = _count_with_cursor(
                    cursor,
                    "SELECT COUNT(1) AS cnt FROM aifab.dim_conf_flow_manu WHERE stage_name IN (%s, %s)",
                    (current_stage, downstream_stage),
                )
                if stage_route_count == 0:
                    max_seq = _fetch_scalar_with_cursor(cursor, "SELECT COALESCE(MAX(seq), 0) AS max_seq FROM aifab.dim_conf_flow_manu")
                    base_seq = int(max_seq or 0) + 10
                    cursor.execute(
                        "INSERT INTO aifab.dim_conf_flow_manu (stage_name, seq) VALUES (%s, %s), (%s, %s)",
                        (current_stage, base_seq, downstream_stage, base_seq + 10),
                    )
                    seeded.append("dim_conf_flow_manu")

            super_hot_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(1) AS cnt
                FROM aifab.dim_wip_lot_rt
                WHERE stage_name = %s
                  AND lot_state IN ('wait', 'reserved', 'finished')
                  AND priority = 2
                """,
                (current_stage,),
            )
            if super_hot_count == 0:
                _insert_wip_lot_rows(
                    cursor,
                    [
                        (current_stage, 2, "wait", 25),
                        (current_stage, 2, "reserved", 25),
                        (current_stage, 2, "finished", 25),
                    ],
                )
                seeded.append("dim_wip_lot_rt.super_hot_lots")

            hot_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(1) AS cnt
                FROM aifab.dim_wip_lot_rt
                WHERE stage_name = %s
                  AND lot_state IN ('wait', 'reserved', 'finished')
                  AND priority = 3
                """,
                (current_stage,),
            )
            if hot_count == 0:
                _insert_wip_lot_rows(
                    cursor,
                    [
                        (current_stage, 3, "wait", 25),
                        (current_stage, 3, "reserved", 25),
                    ],
                )
                seeded.append("dim_wip_lot_rt.hot_lots")

            downstream_wip_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(1) AS cnt
                FROM aifab.dim_wip_lot_rt
                WHERE stage_name = %s
                  AND lot_state IN ('running', 'wait', 'reserved', 'finished', 'hold', 'running hold', 'inventory hold')
                """,
                (downstream_stage,),
            )
            if downstream_wip_count == 0:
                downstream_rows = [
                    (downstream_stage, 4, "wait", 120),
                    (downstream_stage, 4, "reserved", 80),
                    (downstream_stage, 4, "running", 50),
                ]
                _insert_wip_lot_rows(cursor, downstream_rows)
                seeded.append("dim_wip_lot_rt.downstream_wip")

            target_count = _count_with_cursor(
                cursor,
                "SELECT COUNT(1) AS cnt FROM aifab.dim_wip_target WHERE stage_name = %s",
                (downstream_stage,),
            )
            if target_count == 0:
                cursor.execute(
                    "INSERT INTO aifab.dim_wip_target (stage_name, target_wip) VALUES (%s, %s)",
                    (downstream_stage, 1500),
                )
                seeded.append("dim_wip_target")
    return {"stage_name": current_stage, "downstream_stage_name": downstream_stage, "seeded": seeded}


def locate_priority_lots(stage_name: str, ensure_demo_data: bool = True) -> list[Dict[str, Any]]:
    """Return Flow 03 Hot Lot / Super Hot Run rows, seeding local demo data if absent."""
    try:
        rows = fetch_all(load_sql("locate_priority_lots"), (stage_name,))
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow03_demo_data(stage_name)
        rows = fetch_all(load_sql("locate_priority_lots"), (stage_name,))
    priorities = {str(row.get("priority") or "").strip().lower() for row in rows}
    missing_required_type = "hot lot" not in priorities or "super hot lot" not in priorities
    if ensure_demo_data and (not rows or missing_required_type):
        ensure_flow03_demo_data(stage_name)
        rows = fetch_all(load_sql("locate_priority_lots"), (stage_name,))
    return rows


def _insert_move_out_history_rows(cursor: Any, stage_name: str, this_week_count: int = 12, last_week_count: int = 10) -> None:
    cursor.execute("SHOW COLUMNS FROM aifab.dwd_wip_lot_step_his_rt")
    existing_columns = {str(row.get("Field")) for row in cursor.fetchall()}
    preferred_columns = ["lot_name", "stage_name", "step_in_time", "step_out_time", "last_updated_time"]
    insert_columns = [column for column in preferred_columns if column in existing_columns]
    now = datetime.now().replace(microsecond=0)
    rows: list[tuple[Any, ...]] = []
    for index in range(1, this_week_count + 1):
        timestamp = now.replace(microsecond=0)
        value_by_column = {
            "lot_name": f"DEMO-MO-{stage_name}-TW-{index}",
            "stage_name": stage_name,
            "step_in_time": timestamp,
            "step_out_time": timestamp,
            "last_updated_time": timestamp,
        }
        rows.append(tuple(value_by_column[column] for column in insert_columns))
    last_week_time = now - timedelta(days=10)
    for index in range(1, last_week_count + 1):
        value_by_column = {
            "lot_name": f"DEMO-MO-{stage_name}-LW-{index}",
            "stage_name": stage_name,
            "step_in_time": last_week_time,
            "step_out_time": last_week_time,
            "last_updated_time": last_week_time,
        }
        rows.append(tuple(value_by_column[column] for column in insert_columns))
    column_sql = ", ".join(insert_columns)
    placeholder_sql = ", ".join(["%s"] * len(insert_columns))
    cursor.executemany(
        f"INSERT INTO aifab.dwd_wip_lot_step_his_rt ({column_sql}) VALUES ({placeholder_sql})",
        rows,
    )


def ensure_flow04_demo_data(stage_name: str) -> Dict[str, Any]:
    """Create the minimal local aifab demo tables/data used by Flow 04 when absent."""
    current_stage = (stage_name or "DNW-ANN").strip() or "DNW-ANN"
    seeded: list[str] = []
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS aifab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aifab.dim_wip_lot_rt (
                  stage_name VARCHAR(128) NOT NULL,
                  priority INT NULL,
                  lot_state VARCHAR(64) NULL,
                  wafer_qty DECIMAL(18,4) DEFAULT 0,
                  updated_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                  KEY idx_dim_wip_lot_rt_stage (stage_name),
                  KEY idx_dim_wip_lot_rt_priority_state (priority, lot_state)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aifab.dim_wip_target (
                  stage_name VARCHAR(128) NOT NULL,
                  target_wip DECIMAL(18,4) DEFAULT 0,
                  KEY idx_dim_wip_target_stage (stage_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS aifab.dwd_wip_lot_step_his_rt (
                  lot_name VARCHAR(64) NOT NULL,
                  stage_name VARCHAR(128) NOT NULL,
                  step_in_time DATETIME NULL,
                  step_out_time DATETIME NULL,
                  last_updated_time DATETIME NOT NULL,
                  KEY idx_dwd_wip_lot_step_stage_time (stage_name, last_updated_time),
                  KEY idx_dwd_wip_lot_step_lot (lot_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            queue_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(1) AS cnt
                FROM aifab.dim_wip_lot_rt
                WHERE stage_name = %s
                  AND lot_state IN ('wait', 'reserved', 'finished')
                """,
                (current_stage,),
            )
            if queue_count == 0:
                _insert_wip_lot_rows(cursor, [(current_stage, 4, "wait", 25) for _ in range(50)])
                seeded.append("dim_wip_lot_rt.flow04_queue")
                queue_count = 50

            target_count = _count_with_cursor(
                cursor,
                "SELECT COUNT(1) AS cnt FROM aifab.dim_wip_target WHERE stage_name = %s",
                (current_stage,),
            )
            if target_count == 0:
                target_wip = max((queue_count - 42) * 25, 25)
                cursor.execute(
                    "INSERT INTO aifab.dim_wip_target (stage_name, target_wip) VALUES (%s, %s)",
                    (current_stage, target_wip),
                )
                seeded.append("dim_wip_target.flow04_stage_target")

            this_week_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(DISTINCT lot_name) AS cnt
                FROM aifab.dwd_wip_lot_step_his_rt
                WHERE stage_name = %s
                  AND step_out_time IS NOT NULL
                  AND last_updated_time >= CURRENT_TIMESTAMP - INTERVAL 1 WEEK
                """,
                (current_stage,),
            )
            last_week_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(DISTINCT lot_name) AS cnt
                FROM aifab.dwd_wip_lot_step_his_rt
                WHERE stage_name = %s
                  AND step_out_time IS NOT NULL
                  AND last_updated_time >= CURRENT_TIMESTAMP - INTERVAL 2 WEEK
                  AND last_updated_time < CURRENT_TIMESTAMP - INTERVAL 1 WEEK
                """,
                (current_stage,),
            )
            if this_week_count == 0 or last_week_count == 0:
                _insert_move_out_history_rows(
                    cursor,
                    current_stage,
                    this_week_count=12 if this_week_count == 0 else 0,
                    last_week_count=10 if last_week_count == 0 else 0,
                )
                seeded.append("dwd_wip_lot_step_his_rt.weekly_history")
    return {"stage_name": current_stage, "seeded": seeded}


def locate_impact_lot(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    """Return Flow 04 impact lot count, seeding local demo data if absent."""
    try:
        row = fetch_one(load_sql("locate_impact_lot"), (stage_name,))
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_impact_lot"), (stage_name,))
    if ensure_demo_data and (not row or row.get("impact_lot_count") is None):
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_impact_lot"), (stage_name,))
    return row


def locate_move_out_trend(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    """Return Flow 04 week-over-week move-out trend, seeding local demo data if absent."""
    try:
        row = fetch_one(load_sql("locate_move_out_trend"), (stage_name, stage_name))
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_move_out_trend"), (stage_name, stage_name))
    if ensure_demo_data and (not row or row.get("lot_count_this_week") is None or row.get("lot_count_last_week") in (None, 0)):
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_move_out_trend"), (stage_name, stage_name))
    return row

def locate_downstream_starvation_with_demo(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    """Return Flow 03 downstream starvation row, seeding local demo data if absent."""
    try:
        row = locate_downstream_starvation(stage_name)
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow03_demo_data(stage_name)
        row = locate_downstream_starvation(stage_name)
    if not row and ensure_demo_data:
        ensure_flow03_demo_data(stage_name)
        row = locate_downstream_starvation(stage_name)
    return row


def _ensure_column(cursor: Any, table_name: str, column_name: str, column_definition: str) -> None:
    cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE %s", (column_name,))
    if cursor.fetchone() is None:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")


def _stage_capability(stage_name: str) -> str:
    normalized = "".join(ch if ch.isalnum() else "_" for ch in stage_name.upper()).strip("_")
    return f"CAP_{normalized or 'STAGE'}"


def _insert_step_history_rows(cursor: Any, stage_name: str, prefix: str, this_week_count: int, last_week_count: int) -> None:
    cursor.execute("SHOW COLUMNS FROM aifab.dwd_wip_lot_step_his_rt")
    existing_columns = {str(row.get("Field")) for row in cursor.fetchall()}
    preferred_columns = ["lot_name", "stage_name", "step_in_time", "step_out_time", "last_updated_time"]
    insert_columns = [column for column in preferred_columns if column in existing_columns]
    now = datetime.now().replace(microsecond=0)
    rows: list[tuple[Any, ...]] = []
    for index in range(1, this_week_count + 1):
        value_by_column = {"lot_name": f"DEMO-{prefix}-{stage_name}-TW-{index}", "stage_name": stage_name, "step_in_time": now, "step_out_time": now, "last_updated_time": now}
        rows.append(tuple(value_by_column[column] for column in insert_columns))
    last_week_time = now - timedelta(days=10)
    for index in range(1, last_week_count + 1):
        value_by_column = {"lot_name": f"DEMO-{prefix}-{stage_name}-LW-{index}", "stage_name": stage_name, "step_in_time": last_week_time, "step_out_time": last_week_time, "last_updated_time": last_week_time}
        rows.append(tuple(value_by_column[column] for column in insert_columns))
    if not rows or not insert_columns:
        return
    column_sql = ", ".join(insert_columns)
    placeholder_sql = ", ".join(["%s"] * len(insert_columns))
    cursor.executemany(f"INSERT INTO aifab.dwd_wip_lot_step_his_rt ({column_sql}) VALUES ({placeholder_sql})", rows)


def ensure_flow06_demo_data(stage_name: str) -> Dict[str, Any]:
    """Create the minimal local demo data used by Flow 06 when source tables are absent."""
    current_stage = (stage_name or "DNW-ANN").strip() or "DNW-ANN"
    capability = _stage_capability(current_stage)
    seeded: list[str] = []
    ensure_flow04_demo_data(current_stage)
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS aifab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("CREATE DATABASE IF NOT EXISTS ffs_vfab_1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aifab.dim_conf_flow_manu (
                  stage_name VARCHAR(128) NOT NULL,
                  seq INT NOT NULL,
                  capability VARCHAR(128) NULL,
                  KEY idx_dim_conf_flow_manu_stage (stage_name),
                  KEY idx_dim_conf_flow_manu_seq (seq),
                  KEY idx_dim_conf_flow_manu_capability (capability)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            _ensure_column(cursor, "aifab.dim_conf_flow_manu", "capability", "capability VARCHAR(128) NULL")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aifab.dim_eqp_all_rt (
                  eqp_name VARCHAR(128) NOT NULL,
                  state_name VARCHAR(64) NULL,
                  original_state VARCHAR(64) NULL,
                  construct_type VARCHAR(64) NULL,
                  name VARCHAR(128) NULL,
                  capability VARCHAR(128) NULL,
                  KEY idx_dim_eqp_all_rt_capability (capability),
                  KEY idx_dim_eqp_all_rt_eqp (eqp_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            for column_name, definition in (("eqp_name", "eqp_name VARCHAR(128) NULL"), ("state_name", "state_name VARCHAR(64) NULL"), ("original_state", "original_state VARCHAR(64) NULL"), ("construct_type", "construct_type VARCHAR(64) NULL"), ("name", "name VARCHAR(128) NULL"), ("capability", "capability VARCHAR(128) NULL"), ("updated_time", "updated_time DATETIME NULL")):
                _ensure_column(cursor, "aifab.dim_eqp_all_rt", column_name, definition)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ffs_vfab_1.ads_ffs_feature_fact_eqp_rti (
                  `unique_eqp_code#v1` VARCHAR(128) NOT NULL,
                  `_biz_ts_#v1` DATETIME NOT NULL,
                  `run_dur_h#v1` DECIMAL(18,4) DEFAULT 0,
                  `idle_dur_h#v1` DECIMAL(18,4) DEFAULT 0,
                  `cur_state#v1` VARCHAR(64) NULL,
                  `last_state#v1` VARCHAR(64) NULL,
                  KEY idx_ads_eqp_rti_eqp_ts (`unique_eqp_code#v1`, `_biz_ts_#v1`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)

            route_count = _count_with_cursor(cursor, "SELECT COUNT(1) AS cnt FROM aifab.dim_conf_flow_manu WHERE stage_name = %s", (current_stage,))
            if route_count == 0:
                max_seq = _fetch_scalar_with_cursor(cursor, "SELECT COALESCE(MAX(seq), 0) AS max_seq FROM aifab.dim_conf_flow_manu")
                cursor.execute("INSERT INTO aifab.dim_conf_flow_manu (stage_name, seq, capability) VALUES (%s, %s, %s)", (current_stage, int(max_seq or 0) + 10, capability))
                seeded.append("dim_conf_flow_manu.flow06_stage")
            else:
                cursor.execute("UPDATE aifab.dim_conf_flow_manu SET capability = COALESCE(capability, %s) WHERE stage_name = %s", (capability, current_stage))

            active_tool_count = _count_with_cursor(cursor, "SELECT COUNT(1) AS cnt FROM aifab.dim_eqp_all_rt WHERE capability = %s AND construct_type = 'Normal' AND name <> 'DUMMY'", (capability,))
            if active_tool_count == 0:
                now = datetime.now().replace(microsecond=0)
                cursor.executemany("""
                    INSERT INTO aifab.dim_eqp_all_rt
                      (eqp_name, state_name, original_state, construct_type, name, capability, updated_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [("PRTAA01", "正常生产", "RUN", "Normal", "PRTAA01", capability, now), ("PRTAA02", "正常生产", "RUN", "Normal", "PRTAA02", capability, now)])
                seeded.append("dim_eqp_all_rt.flow06_tools")

            rti_count = _count_with_cursor(cursor, """
                SELECT COUNT(1) AS cnt
                FROM ffs_vfab_1.ads_ffs_feature_fact_eqp_rti
                WHERE `unique_eqp_code#v1` IN ('PRTAA01', 'PRTAA02')
                  AND `_biz_ts_#v1` >= (unix_timestamp(timestamp(date(current_timestamp - interval 7 hour - interval 30 minute)) + interval 7 hour + interval 30 minute) * 1000)
                """)
            if rti_count == 0:
                now = int(datetime.now().timestamp() * 1000)
                cursor.executemany("""
                    INSERT INTO ffs_vfab_1.ads_ffs_feature_fact_eqp_rti
                      (`unique_eqp_code#v1`, `_biz_ts_#v1`, `run_dur_h#v1`, `idle_dur_h#v1`, `cur_state#v1`, `last_state#v1`)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, [("PRTAA01", now, 6, 0, "正常生产", "RUN"), ("PRTAA02", now, 6, 0, "正常生产", "RUN")])
                seeded.append("ads_ffs_feature_fact_eqp_rti.flow06_runtime")

            hold_run_count = _count_with_cursor(cursor, """
                SELECT COUNT(1) AS cnt
                FROM aifab.dim_wip_lot_rt
                WHERE stage_name = %s
                  AND lot_state IN ('hold', 'running hold', 'inventory hold', 'running')
                """, (current_stage,))
            if hold_run_count == 0:
                _insert_wip_lot_rows(cursor, [(current_stage, 4, "running", 25), (current_stage, 4, "running", 25), (current_stage, 4, "hold", 25)])
                seeded.append("dim_wip_lot_rt.flow06_hold_run")

            step_history_count = _count_with_cursor(cursor, """
                SELECT COUNT(1) AS cnt
                FROM aifab.dwd_wip_lot_step_his_rt
                WHERE stage_name = %s
                  AND last_updated_time >= current_timestamp - interval 2 week
                """, (current_stage,))
            if step_history_count == 0:
                _insert_step_history_rows(cursor, current_stage, "FLOW06-STEP", this_week_count=18, last_week_count=12)
                seeded.append("dwd_wip_lot_step_his_rt.flow06_step_history")
    return {"stage_name": current_stage, "capability": capability, "seeded": seeded}


def ensure_flow06_production_dependencies(stage_name: str) -> Dict[str, Any]:
    """Create only the local MySQL fields and rows required by production SQL 6 and 10."""
    if not is_local_mysql_dialect():
        return {"stage_name": stage_name, "seeded": []}

    current_stage = (stage_name or "DNW-ANN").strip() or "DNW-ANN"
    capability = _stage_capability(current_stage)
    flow_id = f"FLOW_{current_stage.replace('-', '_')}"
    seeded: list[str] = []
    ensure_flow06_demo_data(current_stage)
    with connection() as conn:
        with conn.cursor() as cursor:
            _ensure_column(cursor, "aifab.dim_conf_flow_manu", "flow_id", "flow_id VARCHAR(128) NULL")
            cursor.execute("UPDATE aifab.dim_conf_flow_manu SET flow_id = COALESCE(flow_id, %s), capability = COALESCE(capability, %s) WHERE stage_name = %s", (flow_id, capability, current_stage))
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aifab.dim_conf_product (
                  product_id VARCHAR(128) NOT NULL,
                  flow_id VARCHAR(128) NOT NULL,
                  PRIMARY KEY (product_id),
                  KEY idx_dim_conf_product_flow (flow_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("SELECT DISTINCT product_name FROM aifab.dim_wip_lot_rt WHERE stage_name = %s AND product_name IS NOT NULL", (current_stage,))
            products = [str(row.get("product_name")) for row in cursor.fetchall() if row.get("product_name")]
            if not products:
                products = ["DEMO_PRODUCT"]
            cursor.executemany("INSERT IGNORE INTO aifab.dim_conf_product (product_id, flow_id) VALUES (%s, %s)", [(product, flow_id) for product in products])
            seeded.append("dim_conf_product")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aifab.dwd_wip_lot_dispatch_rt (
                  fab_id VARCHAR(64) NOT NULL,
                  send_time DATETIME NOT NULL,
                  lot_names VARCHAR(128) NOT NULL,
                  lot_list JSON NOT NULL,
                  priority INT NULL,
                  KEY idx_dispatch_lot (lot_names),
                  KEY idx_dispatch_send_time (send_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("SELECT lot_name FROM aifab.dim_wip_lot_rt WHERE stage_name = %s ORDER BY lot_name LIMIT 64", (current_stage,))
            lot_names = [str(row.get("lot_name")) for row in cursor.fetchall() if row.get("lot_name")]
            now = datetime.now().replace(microsecond=0)
            rows = []
            for index, lot_name in enumerate(lot_names):
                if _count_with_cursor(cursor, "SELECT COUNT(1) AS cnt FROM aifab.dwd_wip_lot_dispatch_rt WHERE lot_names = %s", (lot_name,)):
                    continue
                eqp_name = "PRTAA01" if index % 2 == 0 else "PRTAA02"
                lot_list = json.dumps([{"dueTime": now.strftime("%Y-%m-%d %H:%M:%S"), "eqpId": eqp_name}])
                rows.append(("FAB1", now, lot_name, lot_list, 4))
            if rows:
                cursor.executemany("INSERT INTO aifab.dwd_wip_lot_dispatch_rt (fab_id, send_time, lot_names, lot_list, priority) VALUES (%s, %s, %s, %s, %s)", rows)
                seeded.append("dwd_wip_lot_dispatch_rt")
    return {"stage_name": current_stage, "seeded": seeded}

def _fetch_flow06_one(sql_name: str, stage_name: str, params: Iterable[Any], ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    try:
        row = fetch_one(load_sql(sql_name), params)
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow06_demo_data(stage_name)
        row = fetch_one(load_sql(sql_name), params)
    if ensure_demo_data and not row:
        ensure_flow06_demo_data(stage_name)
        row = fetch_one(load_sql(sql_name), params)
    if ensure_demo_data and sql_name == "locate_tool_efficiency" and row and int(row.get("eqp_count") or 0) == 0:
        ensure_flow06_demo_data(stage_name)
        row = fetch_one(load_sql(sql_name), params)
    return row


def _fetch_flow06_all(sql_name: str, stage_name: str, params: Iterable[Any], ensure_demo_data: bool = True) -> list[Dict[str, Any]]:
    try:
        rows = fetch_all(load_sql(sql_name), params)
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow06_demo_data(stage_name)
        rows = fetch_all(load_sql(sql_name), params)
    if ensure_demo_data and not rows:
        ensure_flow06_demo_data(stage_name)
        rows = fetch_all(load_sql(sql_name), params)
    return rows


def locate_wip_hold_run(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    return _fetch_flow06_one("locate_wip_hold_run", stage_name, (stage_name,), ensure_demo_data)


def locate_tool_status(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    return _fetch_flow06_one("locate_tool_status", stage_name, (stage_name,), ensure_demo_data)


def locate_tool_dispatch(stage_name: str, ensure_demo_data: bool = True) -> list[Dict[str, Any]]:
    local_demo = ensure_demo_data and is_local_mysql_dialect()
    if local_demo:
        ensure_flow06_production_dependencies(stage_name)
    return _fetch_flow06_all("locate_tool_dispatch", stage_name, (stage_name,), local_demo)


def locate_product_tool_profile(stage_name: str, ensure_demo_data: bool = True) -> list[Dict[str, Any]]:
    local_demo = ensure_demo_data and is_local_mysql_dialect()
    if local_demo:
        ensure_flow06_production_dependencies(stage_name)
    return _fetch_flow06_all("locate_product_tool_profile", stage_name, (stage_name, stage_name), local_demo)


def locate_tool_efficiency(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    return _fetch_flow06_one("locate_tool_efficiency", stage_name, (stage_name,), ensure_demo_data)


def locate_tool_efficiency_detail(stage_name: str, ensure_demo_data: bool = True) -> list[Dict[str, Any]]:
    return _fetch_flow06_all("locate_tool_efficiency_detail", stage_name, (stage_name,), ensure_demo_data)


def locate_move_in_trend(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    return _fetch_flow06_one("locate_move_in_trend", stage_name, (stage_name, stage_name), ensure_demo_data)


def collect_case_data_snapshot(
    stage_name: Optional[str] = None,
    high_wip: Optional[Dict[str, Any]] = None,
    ensure_demo_data: bool = True,
) -> Dict[str, Any]:
    """Collect all whitelisted SQL facts once for a case and reuse them in later flows."""
    captured_at = datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    query_errors: list[Dict[str, str]] = []

    warehouse_high_wip = high_wip
    if warehouse_high_wip is None:
        try:
            warehouse_high_wip = locate_high_wip_stage()
        except Exception as exc:  # pragma: no cover - depends on local MySQL availability
            query_errors.append({"query": "locate_high_wip_stage", "error": str(exc)})
            warehouse_high_wip = None

    resolved_stage = stage_name or (warehouse_high_wip or {}).get("stage_name") or "DNW-ANN"
    resolved_stage = str(resolved_stage).strip() or "DNW-ANN"

    def capture(query_name: str, fn: Any) -> Any:
        try:
            return fn()
        except Exception as exc:  # pragma: no cover - depends on local MySQL availability
            query_errors.append({"query": query_name, "error": str(exc)})
            return None

    downstream_starvation = capture(
        "locate_downstream_starvation",
        lambda: locate_downstream_starvation_with_demo(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    priority_lots = capture(
        "locate_priority_lots",
        lambda: locate_priority_lots(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    impact_lot = capture(
        "locate_impact_lot",
        lambda: locate_impact_lot(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    move_out_trend = capture(
        "locate_move_out_trend",
        lambda: locate_move_out_trend(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    flow06_wip_hold_run = capture(
        "locate_wip_hold_run",
        lambda: locate_wip_hold_run(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    flow06_tool_status = capture(
        "locate_tool_status",
        lambda: locate_tool_status(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    flow06_tool_efficiency = capture(
        "locate_tool_efficiency",
        lambda: locate_tool_efficiency(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    flow06_tool_dispatch = capture(
        "locate_tool_dispatch",
        lambda: locate_tool_dispatch(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    flow06_product_tool_profile = capture(
        "locate_product_tool_profile",
        lambda: locate_product_tool_profile(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    flow06_move_in_trend = capture(
        "locate_move_in_trend",
        lambda: locate_move_in_trend(resolved_stage, ensure_demo_data=ensure_demo_data),
    )
    sql_results = {
        "locate_high_wip_stage": warehouse_high_wip,
        "locate_downstream_starvation": downstream_starvation,
        "locate_priority_lots": priority_lots,
        "locate_impact_lot": impact_lot,
        "locate_move_out_trend": move_out_trend,
        "locate_wip_hold_run": flow06_wip_hold_run,
        "locate_tool_status": flow06_tool_status,
        "locate_tool_efficiency": flow06_tool_efficiency,
        "locate_tool_dispatch": flow06_tool_dispatch,
        "locate_product_tool_profile": flow06_product_tool_profile,
        "locate_move_in_trend": flow06_move_in_trend,
    }
    return {
        "schema_version": CASE_DATA_SNAPSHOT_VERSION,
        "captured_at": captured_at,
        "stage_name": resolved_stage,
        "sql_results": sql_results,
        "query_errors": query_errors,
        "usage_rule": "SQL facts are collected once when the case starts; later flows must read this saved snapshot instead of querying SQL again.",
    }
def get_latest_active_case(
    case_id: Optional[str] = None,
    next_flow_no: Optional[str] = None,
    current_flow_no: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    return fetch_one(
        load_sql("get_latest_active_case"),
        (case_id, case_id, next_flow_no, next_flow_no, current_flow_no, current_flow_no),
    )


def get_case_record(case_id: str) -> Optional[Dict[str, Any]]:
    return fetch_one(load_sql("get_case_record"), (case_id,))


def get_case_flow_record(case_id: str, current_flow_no: str) -> Optional[Dict[str, Any]]:
    return fetch_one(load_sql("get_case_flow_record"), (case_id, current_flow_no))


def get_case_flow_record_by_save_marker(
    case_id: str,
    current_flow_no: str,
    save_time: str,
) -> Optional[Dict[str, Any]]:
    return fetch_one(load_sql("get_case_flow_record_by_save_marker"), (case_id, current_flow_no, save_time))


def save_case_flow_record(
    *,
    case_id: str,
    issue_type: str,
    flow_status: str,
    case_status: str,
    current_flow_no: str,
    current_flow_name: str,
    next_flow_no: Optional[str],
    next_flow_name: Optional[str],
    flow_data_json: Dict[str, Any],
) -> Dict[str, Any]:
    existing = get_case_flow_record(case_id, current_flow_no)
    payload = dumps(flow_data_json)
    save_time = datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    if existing:
        affected_rows = execute(
            load_sql("update_case_flow_record"),
            (
                issue_type,
                flow_status,
                case_status,
                current_flow_name,
                next_flow_no,
                next_flow_name,
                payload,
                save_time,
                case_id,
                current_flow_no,
            ),
        )
        verified_record = get_case_flow_record_by_save_marker(case_id, current_flow_no, save_time)
        verified = verified_record is not None
        return {
            "saved": bool(verified and affected_rows >= 1),
            "operation": "update",
            "affected_rows": affected_rows,
            "case_id": case_id,
            "current_flow_no": current_flow_no,
            "save_time": save_time,
            "verified": verified,
        }

    affected_rows = execute(
        load_sql("insert_case_flow_record"),
        (
            case_id,
            issue_type,
            flow_status,
            case_status,
            current_flow_no,
            current_flow_name,
            next_flow_no,
            next_flow_name,
            payload,
            save_time,
        ),
    )
    verified_record = get_case_flow_record_by_save_marker(case_id, current_flow_no, save_time)
    verified = verified_record is not None
    return {
        "saved": bool(verified and affected_rows == 1),
        "operation": "insert",
        "affected_rows": affected_rows,
        "case_id": case_id,
        "current_flow_no": current_flow_no,
        "save_time": save_time,
        "verified": verified,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a whitelisted WIP data query.")
    parser.add_argument(
        "action",
        choices=[
            "locate_high_wip_stage",
            "locate_downstream_starvation",
            "locate_priority_lots",
            "locate_impact_lot",
            "locate_move_out_trend",
    "locate_wip_hold_run",
    "locate_tool_status",
    "locate_tool_dispatch",
    "locate_tool_efficiency",
    "locate_product_tool_profile",
    "locate_tool_efficiency_detail",
    "locate_move_in_trend",
            "collect_case_data_snapshot",
            "get_latest_active_case",
            "get_case_record",
        ],
    )
    parser.add_argument("--case-id")
    parser.add_argument("--next-flow-no")
    parser.add_argument("--current-flow-no")
    parser.add_argument("--stage-name")
    args = parser.parse_args()

    if args.action == "locate_high_wip_stage":
        result = locate_high_wip_stage()
    elif args.action == "locate_downstream_starvation":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_downstream_starvation")
        result = locate_downstream_starvation(args.stage_name)
    elif args.action == "locate_priority_lots":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_priority_lots")
        result = locate_priority_lots(args.stage_name)
    elif args.action == "locate_impact_lot":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_impact_lot")
        result = locate_impact_lot(args.stage_name)
    elif args.action == "locate_wip_hold_run":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_wip_hold_run")
        result = locate_wip_hold_run(args.stage_name)
    elif args.action == "locate_tool_status":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_tool_status")
        result = locate_tool_status(args.stage_name)
    elif args.action == "locate_tool_dispatch":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_tool_dispatch")
        result = locate_tool_dispatch(args.stage_name)
    elif args.action == "locate_product_tool_profile":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_product_tool_profile")
        result = locate_product_tool_profile(args.stage_name)
    elif args.action == "locate_tool_efficiency":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_tool_efficiency")
        result = locate_tool_efficiency(args.stage_name)
    elif args.action == "locate_tool_efficiency_detail":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_tool_efficiency_detail")
        result = locate_tool_efficiency_detail(args.stage_name)
    elif args.action == "locate_move_in_trend":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_move_in_trend")
        result = locate_move_in_trend(args.stage_name)
    elif args.action == "locate_move_out_trend":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_move_out_trend")
        result = locate_move_out_trend(args.stage_name)
    elif args.action == "collect_case_data_snapshot":
        result = collect_case_data_snapshot(stage_name=args.stage_name)
    elif args.action == "get_latest_active_case":
        result = get_latest_active_case(
            case_id=args.case_id,
            next_flow_no=args.next_flow_no,
            current_flow_no=args.current_flow_no,
        )
    elif args.action == "get_case_record":
        if not args.case_id:
            raise SystemExit("--case-id is required for get_case_record")
        result = get_case_record(args.case_id)
    else:  # pragma: no cover
        raise SystemExit(f"Unsupported action: {args.action}")

    print(dumps({"ok": True, "data": result}))

if __name__ == "__main__":
    main()



























