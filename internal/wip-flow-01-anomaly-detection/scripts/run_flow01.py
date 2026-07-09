#!/usr/bin/env python
"""Flow 01: prepare raw inputs for agent-generated anomaly discovery output."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


INTERNAL_DIR = Path(__file__).resolve().parents[2]
SKILL_DIR = INTERNAL_DIR.parent
DATA_SCRIPT_DIR = INTERNAL_DIR / "wip-data-query" / "scripts"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "flow01_result_prompt.md"
OUTPUT_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "output-contracts"
TEXT_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow01-text-output-contract.md"
JSON_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow01-json-output-contract.md"
GLOBAL_KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
FLOW_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"
FLOW_MOCK_PATH = Path(__file__).resolve().parents[1] / "data" / "flow01_mock.json"
sys.path.insert(0, str(DATA_SCRIPT_DIR))

from query_data import dumps, save_case_flow_record  # noqa: E402


ISSUE_TYPE = "分析一个WIP报警的处理流程"
FLOW_NO = "01"
FLOW_NAME = "异常发现"
NEXT_FLOW_NO = "02"
NEXT_FLOW_NAME = "异常确认"
BUBBLE_STATUSES = {"WIP Bubble", "严重 WIP Bubble"}


def _drop_empty(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _drop_empty(v) for k, v in value.items() if v not in (None, "", "-", [], {})}
    if isinstance(value, list):
        return [_drop_empty(item) for item in value if item not in (None, "", "-", [], {})]
    return value


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8-sig")


def load_output_contracts() -> Dict[str, Dict[str, str]]:
    return {
        "text": {
            "path": str(TEXT_OUTPUT_CONTRACT_PATH.relative_to(SKILL_DIR)),
            "content": TEXT_OUTPUT_CONTRACT_PATH.read_text(encoding="utf-8-sig"),
        },
        "json": {
            "path": str(JSON_OUTPUT_CONTRACT_PATH.relative_to(SKILL_DIR)),
            "content": JSON_OUTPUT_CONTRACT_PATH.read_text(encoding="utf-8-sig"),
        },
    }


def load_flow_mock() -> Dict[str, Any]:
    if not FLOW_MOCK_PATH.exists():
        return {}
    data = json.loads(FLOW_MOCK_PATH.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def load_knowledge_pack() -> list[Dict[str, str]]:
    knowledge_pack: list[Dict[str, str]] = []
    for scope, directory in (("global", GLOBAL_KNOWLEDGE_DIR), ("flow", FLOW_KNOWLEDGE_DIR)):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            knowledge_pack.append(
                {
                    "scope": scope,
                    "name": path.stem,
                    "path": str(path.relative_to(SKILL_DIR)),
                    "content": path.read_text(encoding="utf-8-sig"),
                }
            )
    return knowledge_pack


def _snapshot_high_wip(case_snapshot: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(case_snapshot, dict):
        return None
    for section_name in ("source_data", "snapshot_inputs"):
        section = case_snapshot.get(section_name)
        if isinstance(section, dict) and isinstance(section.get("warehouse_high_wip"), dict):
            return section["warehouse_high_wip"]
    return None


def build_model_context(
    case_id: str,
    high_wip: Optional[Dict[str, Any]] = None,
    case_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return raw SQL/mock/context only; the agent owns extraction, wording, and decisions."""
    warehouse_high_wip = high_wip if high_wip is not None else _snapshot_high_wip(case_snapshot)
    return {
        "case_id": case_id,
        "flow": {"flow_no": FLOW_NO, "flow_name": FLOW_NAME, "purpose": "异常发现"},
        "has_stage_data": bool(warehouse_high_wip),
        "knowledge_pack": load_knowledge_pack(),
        "output_contracts": load_output_contracts(),
        "raw_inputs": {
            "warehouse_high_wip": warehouse_high_wip or {},
            "case_snapshot": case_snapshot or {},
            "flow_mock": load_flow_mock(),
        },
        "generation_rules": [
            "当前 Agent 自己根据 raw_inputs 提取字段、做业务判断并组织 text/content 轻量结构。",
            "示例输入输出只用于结构参考，标题可以一致，正文不要原文照抄，也不要拼凑字段；内容要围绕本次 raw_inputs 形成连贯分析。",
            "脚本不构造最终展示结构或固定话术。",
            "SQL 和 mock 都没有的字段直接省略，不输出占位值。",
        ],
        "output_language": "zh-CN",
        "prompt_file": str(PROMPT_PATH.relative_to(SKILL_DIR)),
        "output_contract_files": {
            "text": str(TEXT_OUTPUT_CONTRACT_PATH.relative_to(SKILL_DIR)),
            "json": str(JSON_OUTPUT_CONTRACT_PATH.relative_to(SKILL_DIR)),
        },
    }


def flow_decision_from_bubble_status(bubble_status: Optional[str]) -> Dict[str, Any]:
    if bubble_status in BUBBLE_STATUSES:
        return {
            "flow_status": "Closed",
            "case_status": "Processing",
            "next_flow_no": NEXT_FLOW_NO,
            "next_flow_name": NEXT_FLOW_NAME,
        }
    if bubble_status in {"Target 缺失", "数据异常"}:
        return {
            "flow_status": "Closed",
            "case_status": "On Hold",
            "next_flow_no": None,
            "next_flow_name": None,
        }
    return {
        "flow_status": "Closed",
        "case_status": "Closed",
        "next_flow_no": None,
        "next_flow_name": None,
    }


def decision_from_model_output(model_output: Dict[str, Any]) -> Dict[str, Any]:
    bubble_status = model_output.get("bubble_status")
    decision = flow_decision_from_bubble_status(str(bubble_status) if bubble_status else None)
    for key in ("flow_status", "case_status", "next_flow_no", "next_flow_name"):
        if key in model_output:
            decision[key] = model_output.get(key)
    return decision


def _extract_json_object(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("model output must be a JSON object")
    return data


def load_model_output(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if not value:
        return None
    if value == "-":
        raw = sys.stdin.read()
    elif value.startswith("@"):
        raw = Path(value[1:]).read_text(encoding="utf-8-sig")
    else:
        raw = value
    return _extract_json_object(raw.lstrip("\ufeff"))



REQUIRED_CONTENT_SHAPE = [
    ("WIP Case Snapshot", ["Case Header", "Case Risk Snapshot｜异常发生时（风险快照）"]),
    (
        "当前阶段对话",
        [
            "系统 / 用户触发",
            "Agent 接管",
            "Agent 思考过程",
            "Agent 分析计划",
            "数据 / 工具调用",
            "Agent 观察结果",
            "Agent 分析判断",
            "Agent 阶段输出",
            "AI Agent",
        ],
    ),
    ("当前阶段结果", ["业务结果", "本阶段结论", "Agent 判断逻辑", "状态与门禁", "关键证据"]),
]


def validate_content_contract(content: Dict[str, Any]) -> None:
    containers = content.get("containers")
    if not isinstance(containers, list):
        raise ValueError("model_output.content.containers is required and must be a list")
    if len(containers) != len(REQUIRED_CONTENT_SHAPE):
        raise ValueError("model_output.content.containers must contain exactly 3 containers")

    for index, (expected_title, expected_sections) in enumerate(REQUIRED_CONTENT_SHAPE):
        container = containers[index]
        if not isinstance(container, dict):
            raise ValueError(f"content.containers[{index}] must be an object")
        if container.get("title") != expected_title:
            raise ValueError(f"content.containers[{index}].title must be {expected_title}")
        sections = container.get("sections")
        if not isinstance(sections, list):
            raise ValueError(f"{expected_title}.sections is required and must be a list")
        if len(sections) != len(expected_sections):
            raise ValueError(f"{expected_title}.sections must contain exactly {len(expected_sections)} sections")
        for section_index, expected_section_title in enumerate(expected_sections):
            section = sections[section_index]
            if not isinstance(section, dict):
                raise ValueError(f"{expected_title}.sections[{section_index}] must be an object")
            if section.get("title") != expected_section_title:
                raise ValueError(
                    f"{expected_title}.sections[{section_index}].title must be {expected_section_title}"
                )
            items = section.get("items")
            if not isinstance(items, list) or not items:
                raise ValueError(f"{expected_title}.{expected_section_title}.items must be a non-empty list")

def stringify_display_item(item: Any) -> str:
    if isinstance(item, dict):
        return " ".join(str(value) for value in item.values() if value not in (None, ""))
    return str(item)


def get_section_items(content: Dict[str, Any], container_title: str, section_title: str) -> list[Any]:
    for container in content.get("containers", []):
        if not isinstance(container, dict) or container.get("title") != container_title:
            continue
        for section in container.get("sections", []):
            if isinstance(section, dict) and section.get("title") == section_title:
                items = section.get("items")
                return items if isinstance(items, list) else []
    return []


def validate_data_tool_call_items(content: Dict[str, Any]) -> None:
    items = get_section_items(content, "当前阶段对话", "数据 / 工具调用")
    forbidden_internal_tokens = ("mock", "warehouse_high_wip")
    status_only_tokens = {"done", "pending"}
    for index, item in enumerate(items):
        item_text = stringify_display_item(item).strip()
        lower_text = item_text.lower()
        if not item_text:
            raise ValueError(f"当前阶段对话.数据 / 工具调用.items[{index}] must not be empty")
        if lower_text in status_only_tokens:
            raise ValueError(
                "当前阶段对话.数据 / 工具调用.items must expose business facts with optional status, "
                f"not status only: index {index}"
            )
        if any(token in lower_text for token in forbidden_internal_tokens):
            raise ValueError(
                "当前阶段对话.数据 / 工具调用.items must expose business facts, "
                f"not internal names: index {index}"
            )
        if isinstance(item, dict):
            has_label = bool(str(item.get("label") or "").strip())
            has_value = bool(str(item.get("value") or "").strip())
            if not (has_label and has_value):
                raise ValueError(
                    "当前阶段对话.数据 / 工具调用 object items must include label and value; "
                    f"status is optional: index {index}"
                )
            continue
        if ":" not in item_text and "：" not in item_text:
            raise ValueError(
                "当前阶段对话.数据 / 工具调用.items must use source/value wording, "
                f"for example 'MES / WIP Profile: Actual WIP = ... [Done]': index {index}"
            )
FORBIDDEN_DISPLAY_TERMS = ("mock",)


def find_forbidden_display_term(value: Any, path: str = "$") -> Optional[str]:
    if isinstance(value, str):
        lower_value = value.lower()
        if any(term in lower_value for term in FORBIDDEN_DISPLAY_TERMS):
            return path
        return None
    if isinstance(value, list):
        for index, item in enumerate(value):
            found = find_forbidden_display_term(item, f"{path}[{index}]")
            if found:
                return found
        return None
    if isinstance(value, dict):
        for key, item in value.items():
            found = find_forbidden_display_term(item, f"{path}.{key}")
            if found:
                return found
    return None


def validate_no_internal_terms_in_display(model_output: Dict[str, Any]) -> None:
    display_payload = {
        "text": model_output.get("text", ""),
        "content": model_output.get("content", {}),
    }
    found = find_forbidden_display_term(display_payload)
    if found:
        raise ValueError(f"model_output visible text/content must not expose internal mock wording: {found}")


def normalize_model_output(model_output: Dict[str, Any]) -> Dict[str, Any]:
    """Validate agent-owned lightweight output without constructing business result content."""
    if not isinstance(model_output, dict):
        raise ValueError("model_output is required and must be a JSON object")

    text = str(model_output.get("text") or "").strip()
    if not text:
        raise ValueError("model_output.text is required")

    content = model_output.get("content") if isinstance(model_output.get("content"), dict) else {}
    if not content:
        raise ValueError("model_output.content is required")
    validate_content_contract(content)
    validate_data_tool_call_items(content)
    validate_no_internal_terms_in_display(model_output)

    forbidden = {"frontend_payload", "frontend_demo", "model_context", "case_snapshot", "prompt", "output_contract", "output_contracts"}
    present_forbidden = sorted(key for key in forbidden if key in model_output)
    if present_forbidden:
        raise ValueError(f"model_output contains forbidden keys: {', '.join(present_forbidden)}")

    return {
        "text": text,
        "content": _drop_empty(dict(content)),
        "bubble_status": model_output.get("bubble_status"),
    }


def compose_flow01_result(
    case_id: str,
    high_wip: Optional[Dict[str, Any]] = None,
    case_snapshot: Optional[Dict[str, Any]] = None,
    model_output: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = build_model_context(case_id, high_wip=high_wip, case_snapshot=case_snapshot)

    if model_output is None:
        return {
            "ok": False,
            "reason": "model_output_required",
            "text": "",
            "internal_only": True,
            "case_id": case_id,
            "flow_no": FLOW_NO,
            "flow_name": FLOW_NAME,
            "flow_status": "Model Pending",
            "case_status": "Model Pending",
            "next_flow_no": None,
            "next_flow_name": None,
            "model_context": context,
            "prompt": load_prompt(),
            "output_contracts": load_output_contracts(),
            "case_snapshot": case_snapshot,
        }

    generated = normalize_model_output(model_output)
    decision = decision_from_model_output(model_output)
    return {
        "ok": True,
        "case_id": case_id,
        "flow_no": FLOW_NO,
        "flow_name": FLOW_NAME,
        "flow_status": decision["flow_status"],
        "case_status": decision["case_status"],
        "next_flow_no": decision["next_flow_no"],
        "next_flow_name": decision["next_flow_name"],
        "bubble_status": generated.get("bubble_status"),
        "text": generated["text"],
        "content": generated["content"],
    }


def run(
    case_id: Optional[str] = None,
    case_snapshot: Optional[Dict[str, Any]] = None,
    high_wip: Optional[Dict[str, Any]] = None,
    model_output: Optional[Dict[str, Any]] = None,
    save: bool = True,
) -> Dict[str, Any]:
    real_case_id = case_id or str(uuid.uuid4())
    result = compose_flow01_result(
        real_case_id,
        high_wip=high_wip,
        case_snapshot=case_snapshot,
        model_output=model_output,
    )
    if save and result.get("ok", True):
        save_result = save_case_flow_record(
            case_id=real_case_id,
            issue_type=ISSUE_TYPE,
            flow_status=result["flow_status"],
            case_status=result["case_status"],
            current_flow_no=result["flow_no"],
            current_flow_name=result["flow_name"],
            next_flow_no=result["next_flow_no"],
            next_flow_name=result["next_flow_name"],
            flow_data_json=result,
        )
        if not save_result.get("saved"):
            raise RuntimeError(f"Failed to save case flow record: {save_result}")
    return result

def render(result: Dict[str, Any], return_type: str) -> str:
    if result.get("reason") == "model_output_required":
        return dumps({
            "internal_only": True,
            "reason": result.get("reason"),
            "model_context": result.get("model_context"),
            "prompt": result.get("prompt"),
            "case_snapshot": result.get("case_snapshot"),
        })
    if return_type == "json":
        return dumps(result)
    if return_type == "both":
        return result["text"] + "\n\n```json\n" + dumps(result) + "\n```"
    return result["text"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run WIP Bubble Flow 01.")
    parser.add_argument("--case-id")
    parser.add_argument("--return-type", choices=["text", "json", "both"], default="text")
    parser.add_argument("--model-output-json", help="Agent generated JSON. Use '-' for stdin or '@path' for a file.")
    parser.add_argument("--emit-model-context", action="store_true", help="Only print model context and prompt; do not save case record.")
    parser.add_argument("--validate-only", action="store_true", help="Validate --model-output-json shape without saving or rendering business output.")
    args = parser.parse_args()

    real_case_id = args.case_id or str(uuid.uuid4())
    if args.emit_model_context:
        context = build_model_context(real_case_id)
        print(dumps({"prompt": load_prompt(),
            "output_contracts": load_output_contracts(), "model_context": context}))
        return

    model_output = load_model_output(args.model_output_json)
    if args.validate_only:
        if model_output is None:
            raise SystemExit("--model-output-json is required with --validate-only")
        normalize_model_output(model_output)
        print(dumps({"ok": True, "validated": True}))
        return

    result = run(real_case_id, model_output=model_output)
    print(render(result, args.return_type))


if __name__ == "__main__":
    main()

















