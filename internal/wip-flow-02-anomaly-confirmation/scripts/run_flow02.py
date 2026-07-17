#!/usr/bin/env python
"""Flow 02: prepare raw inputs for agent-generated anomaly confirmation output."""

from __future__ import annotations

import argparse
import json
import sys

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any, Dict, Optional


INTERNAL_DIR = Path(__file__).resolve().parents[2]
SKILL_DIR = INTERNAL_DIR.parent
DATA_SCRIPT_DIR = INTERNAL_DIR / "wip-data-query" / "scripts"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "flow02_result_prompt.md"
OUTPUT_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "output-contracts"
TEXT_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow02-text-output-contract.md"
JSON_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow02-json-output-contract.md"
GLOBAL_KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
FLOW_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"
FLOW_MOCK_PATH = Path(__file__).resolve().parents[1] / "data" / "flow02_mock.json"
sys.path.insert(0, str(DATA_SCRIPT_DIR))

from query_data import dumps, save_case_flow_record  # noqa: E402


ISSUE_TYPE = "分析一个WIP报警的处理流程"
FLOW_NO = "02"
FLOW_NAME = "异常确认"
NEXT_FLOW_NO = "03"
NEXT_FLOW_NAME = "临时措施"


def _drop_empty(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _drop_empty(v) for k, v in value.items() if v not in (None, "", "-", [], {})}
    if isinstance(value, list):
        return [_drop_empty(item) for item in value if item not in (None, "", "-", [], {})]
    return value


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def load_prompt() -> str:
    return load_text(PROMPT_PATH)


def load_output_contracts() -> Dict[str, Dict[str, str]]:
    return {
        "text": {"path": str(TEXT_OUTPUT_CONTRACT_PATH.relative_to(SKILL_DIR)), "content": load_text(TEXT_OUTPUT_CONTRACT_PATH)},
        "json": {"path": str(JSON_OUTPUT_CONTRACT_PATH.relative_to(SKILL_DIR)), "content": load_text(JSON_OUTPUT_CONTRACT_PATH)},
    }


def load_flow_mock() -> Dict[str, Any]:
    if not FLOW_MOCK_PATH.exists():
        return {}
    data = json.loads(load_text(FLOW_MOCK_PATH))
    return data if isinstance(data, dict) else {}


def load_knowledge_pack() -> list[Dict[str, str]]:
    knowledge_pack: list[Dict[str, str]] = []
    for scope, directory in (("global", GLOBAL_KNOWLEDGE_DIR), ("flow", FLOW_KNOWLEDGE_DIR)):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            knowledge_pack.append({"scope": scope, "name": path.stem, "path": str(path.relative_to(SKILL_DIR)), "content": load_text(path)})
    return knowledge_pack


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
        raise ValueError("JSON object is required")
    return data


def load_json_arg(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if not value:
        return None
    if value == "-":
        raw = sys.stdin.read()
    elif value.startswith("@"):
        raise ValueError("File-based JSON inputs are disabled; pass inline JSON or stdin.")
    else:
        raw = value
    return _extract_json_object(raw.lstrip("\ufeff"))


def parse_flow_data(record: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(record, dict):
        return {}
    raw = record.get("flow_data_json")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def build_model_context(case_id: str, previous_record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    previous_flow_data = parse_flow_data(previous_record)
    return {
        "case_id": case_id,
        "flow": {"flow_no": FLOW_NO, "flow_name": FLOW_NAME, "purpose": "异常确认"},
        "previous_flow": {
            "record": previous_record or {},
            "flow_data_json": previous_flow_data,
            "content": previous_flow_data.get("content", {}),
            "text": previous_flow_data.get("text", ""),
        },
        "raw_inputs": {
            "flow01_saved_result": previous_flow_data,
            "flow02_mock": load_flow_mock(),
        },
        "knowledge_pack": load_knowledge_pack(),
        "output_contracts": load_output_contracts(),
        "generation_rules": [
            "唯一事实源为 model_context.raw_inputs：只可使用 SQL 快照、前序 Flow 内容及当前 Flow 实际存在的补充数据；examples、output-contracts 和 prompt 绝不是事实来源。",
            "生成前逐项核对具体对象、数值、人员、时长、状态和结论是否能回溯到 raw_inputs；无来源则省略或写数据不足，禁止猜测、补造或套用示例。",
            "最终 text 与 content 只能陈述当前业务事实、判断和处置，禁止输出实现、展示、测试或内部上下文术语。",
            "优先从 Flow 01 保存结果中获取 WIP、Target、Queue、Case Header 和风险快照。",
            "Flow 02 只做数据刷新、指标口径、Target 有效性、异常持续时间和重复 Case 校验。",
            "前序结果和 SQL 都没有的数据才使用 flow02_mock；仍缺失则省略。",
            "脚本不构造最终展示结构或固定话术。",
        ],
        "output_language": "zh-CN",
    }


REQUIRED_CONTENT_SHAPE = [
    ("WIP Case Snapshot", ["Case Header", "Case Risk Snapshot｜异常发生时（风险快照）"]),
    (
        "当前阶段对话",
        ["系统 / 用户触发", "Agent 接管", "Agent 思考过程", "Agent 分析计划", "数据 / 工具调用", "Agent 观察结果", "Agent 分析判断", "Agent 阶段输出", "AI Agent"],
    ),
    ("当前阶段结果", ["业务结果", "本阶段结论", "Agent 判断逻辑", "状态与门禁", "关键证据"]),
]


def validate_content_contract(content: Dict[str, Any]) -> None:
    containers = content.get("containers")
    if not isinstance(containers, list) or len(containers) != len(REQUIRED_CONTENT_SHAPE):
        raise ValueError("model_output.content.containers must contain exactly 3 containers")
    for index, (expected_title, expected_sections) in enumerate(REQUIRED_CONTENT_SHAPE):
        container = containers[index]
        if not isinstance(container, dict) or container.get("title") != expected_title:
            raise ValueError(f"content.containers[{index}].title must be {expected_title}")
        sections = container.get("sections")
        if not isinstance(sections, list) or len(sections) != len(expected_sections):
            raise ValueError(f"{expected_title}.sections must contain exactly {len(expected_sections)} sections")
        for section_index, expected_section_title in enumerate(expected_sections):
            section = sections[section_index]
            if not isinstance(section, dict) or section.get("title") != expected_section_title:
                raise ValueError(f"{expected_title}.sections[{section_index}].title must be {expected_section_title}")
            items = section.get("items")
            if not isinstance(items, list) or not items:
                raise ValueError(f"{expected_title}.{expected_section_title}.items must be a non-empty list")


def find_forbidden_display_term(value: Any, path: str = "$") -> Optional[str]:
    if isinstance(value, str):
        lower_value = value.lower()
        if any(term in lower_value for term in ("mock", "model_context", "internal_payload", "internal_render", "前端", "demo", "演示", "本地测试", "样例")):
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


def normalize_model_output(model_output: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(model_output, dict):
        raise ValueError("model_output is required and must be a JSON object")
    text = str(model_output.get("text") or "").strip()
    if not text:
        raise ValueError("model_output.text is required")
    content = model_output.get("content") if isinstance(model_output.get("content"), dict) else {}
    if not content:
        raise ValueError("model_output.content is required")
    validate_content_contract(content)
    found = find_forbidden_display_term({"text": text, "content": content})
    if found:
        raise ValueError(f"model_output visible text/content contains forbidden internal wording: {found}")
    forbidden = {"internal_payload", "internal_render", "model_context", "case_snapshot", "prompt", "output_contract", "output_contracts"}
    present = sorted(key for key in forbidden if key in model_output)
    if present:
        raise ValueError(f"model_output contains forbidden keys: {', '.join(present)}")
    return {
        "text": text,
        "content": _drop_empty(dict(content)),
        "confirmation_status": model_output.get("confirmation_status"),
    }


def decision_from_model_output(model_output: Dict[str, Any]) -> Dict[str, Any]:
    confirmation_status = str(model_output.get("confirmation_status") or "")
    if "成立" in confirmation_status and "不成立" not in confirmation_status:
        default = {"flow_status": "Closed", "case_status": "Processing", "next_flow_no": NEXT_FLOW_NO, "next_flow_name": NEXT_FLOW_NAME}
    else:
        default = {"flow_status": "Closed", "case_status": "Closed", "next_flow_no": None, "next_flow_name": None}
    for key in ("flow_status", "case_status", "next_flow_no", "next_flow_name"):
        if key in model_output:
            default[key] = model_output.get(key)
    return default


def compose_flow02_result(case_id: str, previous_record: Optional[Dict[str, Any]] = None, model_output: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    context = build_model_context(case_id, previous_record=previous_record)
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
        "confirmation_status": generated.get("confirmation_status"),
        "text": generated["text"],
        "content": generated["content"],
    }


def run(case_id: str, previous_record: Optional[Dict[str, Any]] = None, model_output: Optional[Dict[str, Any]] = None, save: bool = True) -> Dict[str, Any]:
    result = compose_flow02_result(case_id, previous_record=previous_record, model_output=model_output)
    if save and result.get("ok", True):
        save_result = save_case_flow_record(
            case_id=case_id,
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
            "output_contracts": result.get("output_contracts"),
        })
    if return_type == "json":
        return dumps(result)
    if return_type == "both":
        return "## 可读 Markdown\n\n" + result["text"] + "\n\n## 结构化 JSON\n\n```json\n" + dumps(result) + "\n```"
    return result["text"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run WIP Bubble Flow 02.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--previous-record-json", help="Previous Flow 01 record JSON. Use '-' for stdin; file paths are disabled.")
    parser.add_argument("--model-output-json", help="Agent generated JSON. Use '-' for stdin; file paths are disabled.")
    parser.add_argument("--return-type", choices=["text", "json", "both"], default="text")
    parser.add_argument("--emit-model-context", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    previous_record = load_json_arg(args.previous_record_json)
    if args.emit_model_context:
        context = build_model_context(args.case_id, previous_record=previous_record)
        print(dumps({"prompt": load_prompt(), "output_contracts": load_output_contracts(), "model_context": context}))
        return

    model_output = load_json_arg(args.model_output_json)
    if args.validate_only:
        if model_output is None:
            raise SystemExit("--model-output-json is required with --validate-only")
        normalize_model_output(model_output)
        print(dumps({"ok": True, "validated": True}))
        return

    result = run(args.case_id, previous_record=previous_record, model_output=model_output)
    print(render(result, args.return_type))


if __name__ == "__main__":
    main()
