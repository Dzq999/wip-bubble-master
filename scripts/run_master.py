#!/usr/bin/env python
"""Master router for the WIP Bubble SOP demo skills."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


SKILL_DIR = Path(__file__).resolve().parents[1]
DATA_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-data-query" / "scripts"
FLOW01_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-01-anomaly-detection" / "scripts"
FLOW02_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-02-anomaly-confirmation" / "scripts"
FLOW03_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-03-containment" / "scripts"
FLOW04_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-04-impact-assessment" / "scripts"
FLOW05_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-05-case-classification" / "scripts"
FLOW06_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-06-root-cause-analysis" / "scripts"
FLOW07_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-flow-07-collaboration-package" / "scripts"
SNAPSHOT_SCRIPT_DIR = SKILL_DIR / "internal" / "wip-case-snapshot" / "scripts"
sys.path.insert(0, str(DATA_SCRIPT_DIR))
sys.path.insert(0, str(FLOW01_SCRIPT_DIR))
sys.path.insert(0, str(FLOW02_SCRIPT_DIR))
sys.path.insert(0, str(FLOW03_SCRIPT_DIR))
sys.path.insert(0, str(FLOW04_SCRIPT_DIR))
sys.path.insert(0, str(FLOW05_SCRIPT_DIR))
sys.path.insert(0, str(FLOW06_SCRIPT_DIR))
sys.path.insert(0, str(FLOW07_SCRIPT_DIR))
sys.path.insert(0, str(SNAPSHOT_SCRIPT_DIR))

from query_data import dumps, get_case_flow_record, get_latest_active_case, locate_downstream_starvation, locate_high_wip_stage  # noqa: E402
from run_flow01 import run as run_flow01  # noqa: E402
from run_flow02 import run as run_flow02  # noqa: E402
from run_flow03 import run as run_flow03  # noqa: E402
from run_flow04 import run as run_flow04  # noqa: E402
from run_flow05 import run as run_flow05  # noqa: E402
from run_flow06 import run as run_flow06  # noqa: E402
from run_flow07 import run as run_flow07  # noqa: E402
from build_snapshot import build_case_snapshot  # noqa: E402


UNRELATED_TEXT = "你的问题与 WIP Bubble / WIP 异常原因分析无关，当前智能体仅支持 Fab WIP Case 排查流程。"
VALID_RETURN_TYPES = {"text", "json", "both"}
VALID_ACTIONS = {"auto", "start", "continue"}
VALID_INTENTS = {"auto", "wip_analysis", "continue_flow", "unrelated"}


def load_request_json(value: str) -> Dict[str, Any]:
    """Load request JSON from a literal string, @file path, or stdin marker '-'."""
    if value == "-":
        raw = sys.stdin.read()
    elif value.startswith("@"):
        raw = Path(value[1:]).read_text(encoding="utf-8-sig")
    else:
        raw = value
    data = json.loads(raw.lstrip("\ufeff"))
    if not isinstance(data, dict):
        raise ValueError("request JSON must be an object")
    return data


def normalize_request(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize model-produced JSON into the deterministic router contract."""
    message = str(raw.get("message") or raw.get("user_message") or "").strip()
    case_id = str(raw.get("case_id") or "").strip() or None
    flow_no = str(raw.get("flow_no") or raw.get("previous_flow_no") or "").strip() or None
    if flow_no and flow_no.isdigit():
        flow_no = flow_no.zfill(2)
    action = str(raw.get("action") or "auto").strip().lower()
    intent = str(raw.get("intent") or "auto").strip().lower()
    return_type_provided = "return_type" in raw and raw.get("return_type") not in (None, "")
    return_type = str(raw.get("return_type") or "text").strip().lower()

    if action not in VALID_ACTIONS:
        action = "auto"
    if intent not in VALID_INTENTS:
        intent = "auto"
    if return_type not in VALID_RETURN_TYPES:
        return_type = "text"
    if intent == "continue_flow":
        action = "continue"

    return {
        "message": message,
        "case_id": case_id,
        "flow_no": flow_no,
        "action": None if action == "auto" else action,
        "intent": intent,
        "return_type": return_type,
        "return_type_provided": return_type_provided,
    }


def is_continue(message: str, action: Optional[str]) -> bool:
    if action == "continue":
        return True
    normalized = message.strip().lower()
    return normalized in {"是", "继续", "下一步", "进入下一流程", "确认", "yes", "y", "ok"}


def is_wip_related(message: str) -> bool:
    normalized = message.lower()
    keywords = [
        "wip",
        "在制品",
        "bubble",
        "异常",
        "stage",
        "最高",
        "原因",
        "排查",
        "报警",
        "流程",
    ]
    return any(keyword in normalized for keyword in keywords)


def parse_flow_json(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    raw = record.get("flow_data_json")
    if not raw:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def current_case_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    payload = parse_flow_json(record)
    return {
        "case_id": record.get("case_id"),
        "flow_status": record.get("flow_status"),
        "case_status": record.get("case_status"),
        "current_flow_no": record.get("current_flow_no"),
        "current_flow_name": record.get("current_flow_name"),
        "next_flow_no": record.get("next_flow_no"),
        "next_flow_name": record.get("next_flow_name"),
        "flow_data": payload,
    }



def model_output_required_response(
    flow_result: Dict[str, Any],
    case_payload: Dict[str, Any],
    target_flow_no: str,
    target_flow_name: str,
) -> Dict[str, Any]:
    return {
        "ok": False,
        "reason": flow_result.get("reason", "model_output_required"),
        "text": flow_result.get("text", ""),
        "internal_only": True,
        "model_context": flow_result.get("model_context"),
        "prompt": flow_result.get("prompt"),
        "output_contracts": flow_result.get("output_contracts"),
        "case": case_payload,
        "target_flow_no": target_flow_no,
        "target_flow_name": target_flow_name,
        "save_required": True,
        "must_generate_before_final": True,
        "must_save_before_final": True,
        "must_not_return_existing_flow_data": True,
        "final_answer_source": "current_turn_generated_model_output",
        "persistence_order": [
            "generate_complete_text_and_content_from_model_context",
            "validate_model_output_with_target_flow_script",
            "save_or_update_target_flow_record_with_model_output_json",
            "return_the_same_newly_generated_result",
        ],
        "save_instruction": (
            f"Generate the complete Flow {target_flow_no} {target_flow_name} model_output_json, "
            "validate it with the target Flow script, save/update that target Flow row, "
            "then return this newly generated result. Do not read an existing target Flow "
            "flow_data_json as the final answer."
        ),
    }

def not_implemented_next_flow(record: Dict[str, Any]) -> Dict[str, Any]:
    summary = current_case_summary(record)
    text = (
        "## 流程推进\n\n"
        f"当前 Case `{summary['case_id']}` 已完成 {summary['current_flow_no']} {summary['current_flow_name']}。\n\n"
        f"下一流程是 {summary['next_flow_no']} {summary['next_flow_name']}，当前本地版本尚未实现该后续流程。\n"
        "请先补充对应 Flow 后再继续推进。"
    )
    return {
        "ok": False,
        "reason": "next_flow_not_implemented",
        "text": text,
        "case": summary,
    }

def run_next_flow_02(record: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(record.get("case_id") or "")
    flow_result = run_flow02(case_id, previous_record=record)
    if not flow_result.get("ok", True):
        return model_output_required_response(flow_result, current_case_summary(record), "02", "异常确认")
    result = dict(flow_result)
    result["reason"] = "continued_case_and_ran_flow_02"
    return result


def run_next_flow_03(record: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(record.get("case_id") or "")
    previous_records = []
    flow01_record = get_case_flow_record(case_id, "01")
    if flow01_record:
        previous_records.append(flow01_record)
    previous_records.append(record)
    flow_result = run_flow03(case_id, previous_record=previous_records)
    if not flow_result.get("ok", True):
        return model_output_required_response(flow_result, current_case_summary(record), "03", "临时措施")
    result = dict(flow_result)
    result["reason"] = "continued_case_and_ran_flow_03"
    return result


def run_next_flow_04(record: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(record.get("case_id") or "")
    previous_records = []
    for flow_no in ("01", "02"):
        previous = get_case_flow_record(case_id, flow_no)
        if previous:
            previous_records.append(previous)
    previous_records.append(record)
    flow_result = run_flow04(case_id, previous_record=previous_records)
    if not flow_result.get("ok", True):
        return model_output_required_response(flow_result, current_case_summary(record), "04", "影响范围评估")
    result = dict(flow_result)
    result["reason"] = "continued_case_and_ran_flow_04"
    return result

def run_next_flow_05(record: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(record.get("case_id") or "")
    previous_records = []
    for flow_no in ("01", "02", "03"):
        previous = get_case_flow_record(case_id, flow_no)
        if previous:
            previous_records.append(previous)
    previous_records.append(record)
    flow_result = run_flow05(case_id, previous_record=previous_records)
    if not flow_result.get("ok", True):
        return model_output_required_response(flow_result, current_case_summary(record), "05", "Case 分级与处置判定")
    result = dict(flow_result)
    result["reason"] = "continued_case_and_ran_flow_05"
    return result

def run_next_flow_06(record: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(record.get("case_id") or "")
    previous_records = []
    for flow_no in ("01", "02", "03", "04"):
        previous = get_case_flow_record(case_id, flow_no)
        if previous:
            previous_records.append(previous)
    previous_records.append(record)
    flow_result = run_flow06(case_id, previous_record=previous_records)
    if not flow_result.get("ok", True):
        return model_output_required_response(flow_result, current_case_summary(record), "06", "异常原因排查")
    result = dict(flow_result)
    result["reason"] = "continued_case_and_ran_flow_06"
    return result

def run_next_flow_07(record: Dict[str, Any]) -> Dict[str, Any]:
    case_id = str(record.get("case_id") or "")
    previous_records = []
    for flow_no in ("01", "02", "03", "04", "05"):
        previous = get_case_flow_record(case_id, flow_no)
        if previous:
            previous_records.append(previous)
    previous_records.append(record)
    flow_result = run_flow07(case_id, previous_record=previous_records)
    if not flow_result.get("ok", True):
        return model_output_required_response(flow_result, current_case_summary(record), "07", "工程问题包与协同任务")
    result = dict(flow_result)
    result["reason"] = "continued_case_and_ran_flow_07"
    return result
def handle(
    message: str,
    action: Optional[str],
    return_type: str,
    intent: str = "auto",
    case_id: Optional[str] = None,
    flow_no: Optional[str] = None,
) -> Dict[str, Any]:
    if intent == "unrelated":
        return {"ok": False, "reason": "unrelated", "text": UNRELATED_TEXT}

    if is_continue(message, action):
        if not flow_no:
            return {
                "ok": False,
                "reason": "previous_flow_no_required",
                "text": "继续流程时必须传入上一流程编号 flow_no，例如执行 Flow 02 时传 flow_no=01。",
            }
        active_case = get_latest_active_case(case_id=case_id, current_flow_no=flow_no)
        if not active_case:
            return {
                "ok": False,
                "reason": "no_active_case",
                "text": "当前没有进行中的 WIP Case。请先发起 WIP 异常分析。",
            }
        next_flow_no = str(active_case.get("next_flow_no") or "")
        if next_flow_no == "02":
            return run_next_flow_02(active_case)
        if next_flow_no == "03":
            return run_next_flow_03(active_case)
        if next_flow_no == "04":
            return run_next_flow_04(active_case)
        if next_flow_no == "05":
            return run_next_flow_05(active_case)
        if next_flow_no == "06":
            return run_next_flow_06(active_case)
        if next_flow_no == "07":
            return run_next_flow_07(active_case)
        return {
            "ok": False,
            "reason": "no_next_flow",
            "text": "当前 Case 没有可继续执行的下一流程。",
            "case": current_case_summary(active_case),
        }

    if intent != "wip_analysis" and not is_wip_related(message):
        return {"ok": False, "reason": "unrelated", "text": UNRELATED_TEXT}

    # A new WIP analysis request always starts a new case. Historical active
    # cases are only read when the user explicitly confirms "continue".
    case_id = str(uuid.uuid4())
    high_wip = locate_high_wip_stage()
    downstream_starvation = None
    if isinstance(high_wip, dict) and high_wip.get("stage_name"):
        downstream_starvation = locate_downstream_starvation(str(high_wip["stage_name"]))
    case_snapshot = build_case_snapshot(
        case_id,
        flow_no="01",
        flow_name="异常发现",
        warehouse_high_wip=high_wip,
        downstream_starvation=downstream_starvation,
    )
    # return_type 只用于 Master 最终渲染；不要把默认 return_type 传给内部 Flow。
    flow_result = run_flow01(case_id, case_snapshot=case_snapshot, high_wip=high_wip)
    if not flow_result.get("ok", True):
        case_payload = {
            "case_id": case_id,
            "current_flow_no": "01",
            "current_flow_name": "异常发现",
            "case_snapshot": case_snapshot,
        }
        response = model_output_required_response(flow_result, case_payload, "01", "异常发现")
        response["case_snapshot"] = case_snapshot
        return response
    result = dict(flow_result)
    result["reason"] = "created_case_and_ran_flow_01"
    return result


def handle_request(raw_request: Dict[str, Any]) -> Dict[str, Any]:
    request = normalize_request(raw_request)
    return handle(
        request["message"],
        request["action"],
        request["return_type"],
        request["intent"],
        request["case_id"],
        request["flow_no"],
    )




def render(result: Dict[str, Any], return_type: str) -> str:
    if return_type == "json":
        return dumps(result)
    if return_type == "both":
        return result.get("text", "") + "\n\n```json\n" + dumps(result) + "\n```"
    return result.get("text", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run WIP Bubble master router.")
    parser.add_argument("--request-json", help="Normalized request JSON. Use '-' for stdin or '@path' for a file.")
    parser.add_argument("--message")
    parser.add_argument("--action", choices=["auto", "continue"], default="auto")
    parser.add_argument("--case-id")
    parser.add_argument("--flow-no", help="Required for continue: previous completed flow number, such as 01 before running Flow 02.")
    parser.add_argument("--return-type", choices=["text", "json", "both"], default="text")
    args = parser.parse_args()

    if args.request_json:
        request = normalize_request(load_request_json(args.request_json))
    else:
        if not args.message:
            parser.error("--message is required when --request-json is not provided")
        request = normalize_request(
            {
                "message": args.message,
                "action": args.action,
                "case_id": args.case_id,
                "flow_no": args.flow_no,
                "return_type": args.return_type,
            }
        )

    result = handle(
        request["message"],
        request["action"],
        request["return_type"],
        request["intent"],
        request["case_id"],
        request["flow_no"],
    )
    print(render(result, request["return_type"]))


if __name__ == "__main__":
    main()

















