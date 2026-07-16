#!/usr/bin/env python
"""Prepare raw WIP case snapshot inputs for the agent/model."""

from __future__ import annotations

import argparse
import json
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
OUTPUT_CONTRACT_PATH = MODULE_DIR / "output-contracts" / "snapshot-input-contract.md"
FLOW01_MOCK_PATH = INTERNAL_DIR / "wip-flow-01-anomaly-detection" / "data" / "flow01_mock.json"


def load_mock_config(path: Path = MOCK_PATH) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data.get("default", data) if isinstance(data, dict) else {}




def load_flow_mock(flow_no: str) -> tuple[Dict[str, Any], Optional[Path]]:
    if flow_no == "01" and FLOW01_MOCK_PATH.exists():
        data = json.loads(FLOW01_MOCK_PATH.read_text(encoding="utf-8-sig"))
        return (data if isinstance(data, dict) else {}), FLOW01_MOCK_PATH
    return {}, None


def build_case_snapshot(
    case_id: str,
    *,
    flow_no: str = "01",
    flow_name: str = "异常发现",
    warehouse_high_wip: Optional[Dict[str, Any]] = None,
    downstream_starvation: Optional[Dict[str, Any]] = None,
    mock_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return raw SQL and mock inputs; do not construct display fields."""
    snapshot_mock = mock_config or load_mock_config()
    flow_mock, flow_mock_path = load_flow_mock(flow_no)

    return {
        "case_id": case_id,
        "flow": {
            "flow_no": flow_no,
            "flow_name": flow_name,
        },
        "snapshot_inputs": {
            "warehouse_high_wip": warehouse_high_wip or {},
            "downstream_starvation": downstream_starvation or {},
            "snapshot_mock": snapshot_mock,
            "flow_mock": flow_mock,
        },
        "source_data": {
            "warehouse_high_wip": warehouse_high_wip or {},
            "downstream_starvation": downstream_starvation or {},
            "snapshot_mock_file": str(MOCK_PATH),
            "flow_mock_file": str(flow_mock_path) if flow_mock_path else None,
        },
        "output_contract_file": str(OUTPUT_CONTRACT_PATH.relative_to(INTERNAL_DIR.parent)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare raw WIP case snapshot inputs as JSON.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--flow-no", default="01")
    parser.add_argument("--flow-name", default="异常发现")
    args = parser.parse_args()

    print(dumps(build_case_snapshot(args.case_id, flow_no=args.flow_no, flow_name=args.flow_name)))


if __name__ == "__main__":
    main()


