#!/usr/bin/env python
"""Flow 05: prepare raw inputs for agent-generated case classification output."""

from __future__ import annotations

import argparse
import json
import re
import sys

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any, Dict, Optional


INTERNAL_DIR = Path(__file__).resolve().parents[2]
SKILL_DIR = INTERNAL_DIR.parent
DATA_SCRIPT_DIR = INTERNAL_DIR / "wip-data-query" / "scripts"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "flow05_result_prompt.md"
OUTPUT_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "output-contracts"
TEXT_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow05-text-output-contract.md"
JSON_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow05-json-output-contract.md"
GLOBAL_KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
FLOW_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"
FLOW_MOCK_PATH = Path(__file__).resolve().parents[1] / "data" / "flow05_mock.json"
sys.path.insert(0, str(DATA_SCRIPT_DIR))

from query_data import dumps, save_case_flow_record  # noqa: E402


ISSUE_TYPE = "分析一个WIP报警的处理流程"
FLOW_NO = "05"
FLOW_NAME = "Case 分级与处置判定"
NEXT_FLOW_NO = "06"
NEXT_FLOW_NAME = "异常原因排查"
REQUIRED_TOOL_LABELS = (
    "Impact Severity",
    "Case Level",
    "Disposition Path",
    "Owner Assignment",
    "Next Flow Gate",
)


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


def _extract_json_value(raw: str) -> Any:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        object_start = text.find("{")
        list_start = text.find("[")
        candidates = [index for index in (object_start, list_start) if index >= 0]
        if not candidates:
            raise
        start = min(candidates)
        end_char = "}" if text[start] == "{" else "]"
        end = text.rfind(end_char)
        if end <= start:
            raise
        return json.loads(text[start : end + 1])


def load_json_arg(value: Optional[str]) -> Optional[Any]:
    if not value:
        return None
    if value == "-":
        raw = sys.stdin.read()
    elif value.startswith("@"):
        raise ValueError("File-based JSON inputs are disabled; pass inline JSON or stdin.")
    else:
        raw = value
    return _extract_json_value(raw.lstrip("\ufeff"))


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


def normalize_previous_records(previous_record: Optional[Any]) -> list[Dict[str, Any]]:
    if previous_record is None:
        return []
    if isinstance(previous_record, list):
        return [record for record in previous_record if isinstance(record, dict)]
    if isinstance(previous_record, dict):
        records = previous_record.get("previous_records")
        if isinstance(records, list):
            return [record for record in records if isinstance(record, dict)]
        return [previous_record]
    return []


def previous_content_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    flow_data = parse_flow_data(record)
    return _drop_empty(
        {
            "case_id": record.get("case_id") or flow_data.get("case_id"),
            "flow_no": record.get("current_flow_no") or flow_data.get("flow_no"),
            "flow_name": record.get("current_flow_name") or flow_data.get("flow_name"),
            "flow_status": record.get("flow_status") or flow_data.get("flow_status"),
            "case_status": record.get("case_status") or flow_data.get("case_status"),
            "next_flow_no": record.get("next_flow_no") or flow_data.get("next_flow_no"),
            "next_flow_name": record.get("next_flow_name") or flow_data.get("next_flow_name"),
            "content": flow_data.get("content", {}),
        }
    )


def iter_content_items(value: Any) -> list[Dict[str, Any]]:
    found: list[Dict[str, Any]] = []
    if isinstance(value, dict):
        if "label" in value or "value" in value or "meta" in value:
            found.append(value)
        for item in value.values():
            found.extend(iter_content_items(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(iter_content_items(item))
    return found


def extract_flow04_business_results(previous_flow_contents: list[Dict[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for summary in reversed(previous_flow_contents):
        if str(summary.get("flow_no") or "") != "04":
            continue
        for item in iter_content_items(summary.get("content", {})):
            label = str(item.get("label") or "").strip()
            value = str(item.get("value") or "").strip()
            if not label or not value:
                continue
            lower_label = label.lower()
            if "impact scope" in lower_label:
                result["impact_scope"] = value
            elif "priority lot" in lower_label:
                result["priority_lot"] = value
            elif "q-time" in lower_label or "q time" in lower_label:
                result["q_time"] = value
            elif "move-out" in lower_label or "move out" in lower_label:
                result["move_out"] = value
            elif "downstream" in lower_label:
                result["downstream"] = value
            elif "spread" in lower_label:
                result["spread_assessment"] = value
        if result:
            result["source_flow_no"] = summary.get("flow_no")
            result["source_flow_name"] = summary.get("flow_name")
            break
    return _drop_empty(result)


def build_flow05_inputs(previous_flow_contents: list[Dict[str, Any]]) -> Dict[str, Any]:
    flow05_inputs = load_flow_mock()
    flow04_results = extract_flow04_business_results(previous_flow_contents)
    return {
        "flow05_inputs": flow05_inputs,
        "derived_context": {"flow04_business_results": flow04_results},
    }


def build_model_context(case_id: str, previous_record: Optional[Any] = None) -> Dict[str, Any]:
    previous_records = normalize_previous_records(previous_record)
    previous_flow_contents = [previous_content_summary(record) for record in previous_records]
    flow05_context = build_flow05_inputs(previous_flow_contents)
    return {
        "case_id": case_id,
        "flow": {"flow_no": FLOW_NO, "flow_name": FLOW_NAME, "purpose": "Case 分级与处置判定"},
        "previous_flows": previous_flow_contents,
        "raw_inputs": {
            "previous_flow_contents": previous_flow_contents,
            **flow05_context,
        },
        "knowledge_pack": load_knowledge_pack(),
        "output_contracts": load_output_contracts(),
        "generation_rules": [
            "唯一事实源为 model_context.raw_inputs：只可使用 SQL 快照、前序 Flow 内容及当前 Flow 实际存在的补充数据；examples、output-contracts 和 prompt 绝不是事实来源。",
            "生成前逐项核对具体对象、数值、人员、时长、状态和结论是否能回溯到 raw_inputs；无来源则省略或写数据不足，禁止猜测、补造或套用示例。",
            "最终 text 与 content 只能陈述当前业务事实、判断和处置，禁止输出实现、展示、测试或内部上下文术语。",
            "优先从 previous_flows[].content 获取 Case Header、风险快照、临时措施和 Flow 04 影响范围结论；不要读取或依赖前序全文 text。",
            "Flow 05 只做 Case 分级与处置判定：Case Level、处置路径、初始主责、升级/门禁和是否进入 Flow 06。",
            "Case 等级必须基于 Flow 04 已有影响范围证据，例如 Impact Lot / WO、Hot Lot / Super Hot Run、Q-Time、Move-Out 和下游 Starvation。",
            "不能输出最终根因、详细原因候选排序、工程问题包结论或已派发任务；这些留给 Flow 06 及后续流程。",
            "如果前序 content 无法支持分级，可使用 flow05_inputs 中的 local_fixture 分级规则；仍缺失则设置 case_status=On Hold、next_flow_no=null。",
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
    labels_found: set[str] = set()
    for index, item in enumerate(items):
        item_text = stringify_display_item(item).strip()
        if not item_text or item_text.lower() in {"done", "pending"}:
            raise ValueError(f"当前阶段对话.数据 / 工具调用.items[{index}] must expose business facts")
        if isinstance(item, dict):
            label = str(item.get("label") or "").strip()
            value = str(item.get("value") or "").strip()
            if not (label and value):
                raise ValueError(f"数据 / 工具调用 object item must include label and value: index {index}")
            for required_label in REQUIRED_TOOL_LABELS:
                if required_label in label:
                    labels_found.add(required_label)
            continue
        if ":" not in item_text and "：" not in item_text:
            raise ValueError(f"数据 / 工具调用 item must use source/value wording: index {index}")
        for required_label in REQUIRED_TOOL_LABELS:
            if required_label in item_text:
                labels_found.add(required_label)
    missing = [label for label in REQUIRED_TOOL_LABELS if label not in labels_found]
    if missing:
        raise ValueError("Flow 05 data/tool calls must include classification dimensions: " + ", ".join(missing))


def find_forbidden_display_term(value: Any, path: str = "$") -> Optional[str]:
    if isinstance(value, str):
        lower_value = value.lower()
        if any(term in lower_value for term in ("mock", "model_context", "internal_payload", "internal_render", "前端", "demo", "演示", "本地测试", "样例")):
            return path
        forbidden_terms = ("最终根因为", "root cause is", "root cause:", "原因候选排序", "工程问题包已派发", "已派发任务")
        if any(term in lower_value for term in forbidden_terms):
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
    validate_data_tool_call_items(content)
    found = find_forbidden_display_term({"text": text, "content": content})
    if found:
        raise ValueError(f"model_output visible text/content contains forbidden wording: {found}")
    forbidden = {"internal_payload", "internal_render", "model_context", "case_snapshot", "prompt", "output_contract", "output_contracts"}
    present = sorted(key for key in forbidden if key in model_output)
    if present:
        raise ValueError(f"model_output contains forbidden keys: {', '.join(present)}")
    return {
        "text": text,
        "content": _drop_empty(dict(content)),
        "case_classification_status": model_output.get("case_classification_status"),
    }


def decision_from_model_output(model_output: Dict[str, Any]) -> Dict[str, Any]:
    classification_status = str(model_output.get("case_classification_status") or "")
    blocked_terms = ("无法分级", "未分级", "阻塞", "On Hold", "on hold")
    if any(term in classification_status for term in blocked_terms):
        default = {"flow_status": "Closed", "case_status": "On Hold", "next_flow_no": None, "next_flow_name": None}
    else:
        default = {"flow_status": "Closed", "case_status": "Processing", "next_flow_no": NEXT_FLOW_NO, "next_flow_name": NEXT_FLOW_NAME}
    for key in ("flow_status", "case_status", "next_flow_no", "next_flow_name"):
        if key in model_output:
            default[key] = model_output.get(key)
    return default


def compose_flow05_result(case_id: str, previous_record: Optional[Any] = None, model_output: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        "case_classification_status": generated.get("case_classification_status"),
        "text": generated["text"],
        "content": generated["content"],
    }


def run(case_id: str, previous_record: Optional[Any] = None, model_output: Optional[Dict[str, Any]] = None, save: bool = True) -> Dict[str, Any]:
    result = compose_flow05_result(case_id, previous_record=previous_record, model_output=model_output)
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
    parser = argparse.ArgumentParser(description="Run WIP Bubble Flow 05.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--previous-record-json", help="Previous Flow records JSON. Use '-' for stdin; file paths are disabled.")
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
