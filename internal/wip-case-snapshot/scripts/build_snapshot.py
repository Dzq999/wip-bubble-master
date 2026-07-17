#!/usr/bin/env python
"""Build the structured Flow 01 WIP Case Snapshot from case_data_snapshot."""

from __future__ import annotations

import argparse
import json
import re
import sys

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any, Dict, Optional

INTERNAL_DIR = Path(__file__).resolve().parents[2]
DATA_SCRIPT_DIR = INTERNAL_DIR / "wip-data-query" / "scripts"
sys.path.insert(0, str(DATA_SCRIPT_DIR))

from query_data import dumps  # noqa: E402

MODULE_DIR = Path(__file__).resolve().parents[1]
MOCK_PATH = MODULE_DIR / "data" / "snapshot_mock.json"
FLOW01_MOCK_PATH = INTERNAL_DIR / "wip-flow-01-anomaly-detection" / "data" / "flow01_mock.json"
DISPLAY_SCHEMA_PATH = MODULE_DIR / "output-contracts" / "snapshot-display-schema.md"
BUBBLE_STATUSES = {"WIP Bubble", "严重 WIP Bubble"}
TEMPLATE_TOKEN = re.compile(r"\$\{([A-Za-z0-9_.]+)(?:\|([A-Za-z0-9_]+))?\}")


def load_mock_config(path: Path = MOCK_PATH) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data.get("default", data) if isinstance(data, dict) else {}


def load_flow_mock(flow_no: str) -> Dict[str, Any]:
    if flow_no == "01" and FLOW01_MOCK_PATH.exists():
        data = json.loads(FLOW01_MOCK_PATH.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else {}
    return {}


def load_display_schema(path: Path = DISPLAY_SCHEMA_PATH) -> Dict[str, list[Dict[str, Any]]]:
    source = path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", source, flags=re.S)
    if not match:
        raise ValueError(f"Snapshot display schema JSON block is missing: {path}")
    data = json.loads(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("Snapshot display schema must be a JSON object")
    for key in ("case_header", "risk_snapshot"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Snapshot display schema.{key} must be a list")
    return data


def _sql_result(case_data_snapshot: Optional[Dict[str, Any]], name: str) -> Dict[str, Any]:
    if not isinstance(case_data_snapshot, dict):
        return {}
    sql_results = case_data_snapshot.get("sql_results")
    if not isinstance(sql_results, dict):
        return {}
    result = sql_results.get(name)
    return result if isinstance(result, dict) else {}


def _number(value: Any) -> Optional[float]:
    try:
        if value is None or isinstance(value, bool):
            return None
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def derive_bubble_status(high_wip: Dict[str, Any]) -> str:
    if not high_wip:
        return "未发现异常"
    actual = _number(high_wip.get("actual_wip"))
    target = _number(high_wip.get("target_wip"))
    if target is None or target <= 0:
        return "Target 缺失"
    if actual is None:
        return "数据异常"
    if actual <= target:
        return "正常"
    if actual <= target * 1.2:
        return "正常偏高"
    if actual <= target * 1.5:
        return "预警"
    if actual <= target * 2:
        return "WIP Bubble"
    return "严重 WIP Bubble"


def derive_case_status(bubble_status: str) -> str:
    if bubble_status in BUBBLE_STATUSES:
        return "Processing"
    if bubble_status in {"Target 缺失", "数据异常"}:
        return "On Hold"
    return "Closed"


def _lookup(context: Dict[str, Any], path: str) -> Any:
    value: Any = context
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _format(value: Any, formatter: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    if formatter == "percent":
        numeric = _number(value)
        if numeric is None:
            return None
        return f"{numeric * 100:.2f}".rstrip("0").rstrip(".") + "%"
    return str(value)


def render_template(template: Any, context: Dict[str, Any]) -> Optional[str]:
    if not isinstance(template, str) or not template.strip():
        return None
    missing = False

    def replace(match: re.Match[str]) -> str:
        nonlocal missing
        rendered = _format(_lookup(context, match.group(1)), match.group(2))
        if rendered is None:
            missing = True
            return ""
        return rendered

    rendered = TEMPLATE_TOKEN.sub(replace, template).strip()
    return None if missing or not rendered else rendered


def build_items(fields: list[Dict[str, Any]], context: Dict[str, Any]) -> list[Dict[str, str]]:
    items: list[Dict[str, str]] = []
    for field in fields:
        if not isinstance(field, dict):
            continue
        label = field.get("label")
        value = render_template(field.get("value_template"), context)
        if not isinstance(label, str) or not label.strip() or value is None:
            continue
        item: Dict[str, str] = {"label": label.strip(), "value": value}
        meta = render_template(field.get("meta_template"), context)
        if meta is not None:
            item["meta"] = meta
        items.append(item)
    return items


def build_case_snapshot(
    case_id: str,
    *,
    case_data_snapshot: Optional[Dict[str, Any]] = None,
    flow_no: str = "01",
    flow_name: str = "异常发现",
    mock_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create the exact WIP Case Snapshot container required by Flow 01."""
    high_wip = _sql_result(case_data_snapshot, "locate_high_wip_stage")
    downstream = _sql_result(case_data_snapshot, "locate_downstream_starvation")
    snapshot_mock = mock_config or load_mock_config()
    bubble_status = derive_bubble_status(high_wip)
    case_status = derive_case_status(bubble_status)
    priority_map = snapshot_mock.get("priority_by_status") if isinstance(snapshot_mock, dict) else {}
    priority = priority_map.get(bubble_status) if isinstance(priority_map, dict) else None
    schema = load_display_schema()
    context = {
        "runtime": {"case_id": case_id, "flow_no": flow_no, "flow_name": flow_name},
        "sql": {"high_wip": high_wip, "downstream": downstream},
        "snapshot": snapshot_mock,
        "flow": load_flow_mock(flow_no),
        "derived": {"bubble_status": bubble_status, "case_status": case_status, "priority": priority},
    }
    header_items = build_items(schema["case_header"], context)
    risk_items = build_items(schema["risk_snapshot"], context)
    has_snapshot = bubble_status in BUBBLE_STATUSES or bubble_status in {"Target 缺失", "数据异常"}
    container = None
    if has_snapshot:
        container = {
            "title": "WIP Case Snapshot",
            "sections": [
                {"title": "Case Header", "items": header_items},
                {"title": "Case Risk Snapshot｜异常发生时（风险快照）", "items": risk_items},
            ],
        }
    return {
        "case_id": case_id,
        "flow": {"flow_no": flow_no, "flow_name": flow_name},
        "bubble_status": bubble_status,
        "case_status": case_status,
        "next_flow_no": "02" if bubble_status in BUBBLE_STATUSES else None,
        "next_flow_name": "异常确认" if bubble_status in BUBBLE_STATUSES else None,
        "wip_case_snapshot": container,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Flow 01 WIP Case Snapshot from case_data_snapshot.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--flow-no", default="01")
    parser.add_argument("--flow-name", default="异常发现")
    args = parser.parse_args()
    print(dumps(build_case_snapshot(args.case_id, flow_no=args.flow_no, flow_name=args.flow_name)))


if __name__ == "__main__":
    main()
