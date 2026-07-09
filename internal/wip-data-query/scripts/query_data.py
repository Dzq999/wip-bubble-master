#!/usr/bin/env python
"""Whitelisted MySQL access for the WIP Bubble demo skills."""

from __future__ import annotations

import argparse
import json
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
CONFIG_PATH = CONFIG_DIR / "db_config.json"
SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
SQL_FILES = {
    "locate_high_wip_stage",
    "locate_downstream_starvation",
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
    parser.add_argument("action", choices=["locate_high_wip_stage", "locate_downstream_starvation", "get_latest_active_case", "get_case_record"])
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






