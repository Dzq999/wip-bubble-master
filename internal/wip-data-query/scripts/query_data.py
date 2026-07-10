#!/usr/bin/env python
"""Whitelisted MySQL access for the WIP Bubble demo skills."""

from __future__ import annotations

import argparse
import json
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
    "locate_flow03_priority_lots",
    "locate_flow04_impact_lot",
    "locate_flow04_move_out_trend",
    "get_latest_active_case",
    "get_case_record",
    "get_case_flow_record",
    "update_case_flow_record",
    "insert_case_flow_record",
    "get_case_flow_record_by_save_marker",
}


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


def db_config() -> Dict[str, Any]:
    file_config = _load_file_config()
    return {
        "host": str(file_config.get("host", "127.0.0.1")),
        "port": int(file_config.get("port", 3306)),
        "user": str(file_config.get("user", "root")),
        "password": str(file_config.get("password", "1234")),
        "charset": str(file_config.get("charset", "utf8mb4")),
        "autocommit": True,
    }


def load_sql(name: str) -> str:
    if name not in SQL_FILES:
        raise ValueError(f"Unsupported SQL action: {name}")
    path = SQL_DIR / f"{name}.sql"
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8-sig").strip()


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


def locate_flow03_priority_lots(stage_name: str, ensure_demo_data: bool = True) -> list[Dict[str, Any]]:
    """Return Flow 03 Hot Lot / Super Hot Run rows, seeding local demo data if absent."""
    try:
        rows = fetch_all(load_sql("locate_flow03_priority_lots"), (stage_name,))
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow03_demo_data(stage_name)
        rows = fetch_all(load_sql("locate_flow03_priority_lots"), (stage_name,))
    priorities = {str(row.get("priority") or "").strip().lower() for row in rows}
    missing_required_type = "hot lot" not in priorities or "super hot lot" not in priorities
    if ensure_demo_data and (not rows or missing_required_type):
        ensure_flow03_demo_data(stage_name)
        rows = fetch_all(load_sql("locate_flow03_priority_lots"), (stage_name,))
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

            move_out_count = _count_with_cursor(
                cursor,
                """
                SELECT COUNT(1) AS cnt
                FROM aifab.dwd_wip_lot_step_his_rt
                WHERE stage_name = %s
                  AND step_out_time IS NOT NULL
                  AND last_updated_time >= CURRENT_TIMESTAMP - INTERVAL 2 WEEK
                """,
                (current_stage,),
            )
            if move_out_count == 0:
                _insert_move_out_history_rows(cursor, current_stage)
                seeded.append("dwd_wip_lot_step_his_rt.move_out_history")
    return {"stage_name": current_stage, "seeded": seeded}


def locate_flow04_impact_lot(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    """Return Flow 04 impact lot count, seeding local demo data if absent."""
    try:
        row = fetch_one(load_sql("locate_flow04_impact_lot"), (stage_name,))
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_flow04_impact_lot"), (stage_name,))
    if ensure_demo_data and (not row or row.get("impact_lot_count") is None):
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_flow04_impact_lot"), (stage_name,))
    return row


def locate_flow04_move_out_trend(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
    """Return Flow 04 week-over-week move-out trend, seeding local demo data if absent."""
    try:
        row = fetch_one(load_sql("locate_flow04_move_out_trend"), (stage_name, stage_name))
    except Exception:
        if not ensure_demo_data:
            raise
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_flow04_move_out_trend"), (stage_name, stage_name))
    if ensure_demo_data and (not row or row.get("lot_count_this_week") is None or row.get("lot_count_last_week") in (None, 0)):
        ensure_flow04_demo_data(stage_name)
        row = fetch_one(load_sql("locate_flow04_move_out_trend"), (stage_name, stage_name))
    return row

def locate_flow03_downstream_starvation(stage_name: str, ensure_demo_data: bool = True) -> Optional[Dict[str, Any]]:
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
            "locate_flow03_priority_lots",
            "locate_flow04_impact_lot",
            "locate_flow04_move_out_trend",
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
    elif args.action == "locate_flow03_priority_lots":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_flow03_priority_lots")
        result = locate_flow03_priority_lots(args.stage_name)
    elif args.action == "locate_flow04_impact_lot":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_flow04_impact_lot")
        result = locate_flow04_impact_lot(args.stage_name)
    elif args.action == "locate_flow04_move_out_trend":
        if not args.stage_name:
            raise SystemExit("--stage-name is required for locate_flow04_move_out_trend")
        result = locate_flow04_move_out_trend(args.stage_name)
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






