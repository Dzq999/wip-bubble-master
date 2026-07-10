#!/usr/bin/env python
"""Flow 04: prepare raw inputs for agent-generated impact assessment output."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional


INTERNAL_DIR = Path(__file__).resolve().parents[2]
SKILL_DIR = INTERNAL_DIR.parent
DATA_SCRIPT_DIR = INTERNAL_DIR / "wip-data-query" / "scripts"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "flow04_result_prompt.md"
OUTPUT_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "output-contracts"
TEXT_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow04-text-output-contract.md"
JSON_OUTPUT_CONTRACT_PATH = OUTPUT_CONTRACT_DIR / "flow04-json-output-contract.md"
GLOBAL_KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
FLOW_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"
FLOW_MOCK_PATH = Path(__file__).resolve().parents[1] / "data" / "flow04_mock.json"
sys.path.insert(0, str(DATA_SCRIPT_DIR))

from query_data import dumps, locate_flow04_impact_lot, locate_flow04_move_out_trend, save_case_flow_record  # noqa: E402


ISSUE_TYPE = "分析一个WIP报警的处理流程"
FLOW_NO = "04"
FLOW_NAME = "影响范围评估"
NEXT_FLOW_NO = "05"
NEXT_FLOW_NAME = "Case 分级与处置判定"
REQUIRED_TOOL_LABELS = (
    "Lot Impact",
    "Priority Lot",
    "Q-Time Impact",
    "Move-Out Impact",
    "Downstream Supply",
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
        raw = Path(value[1:]).read_text(encoding="utf-8-sig")
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


def parse_downstream_stage(text: str) -> Optional[str]:
    patterns = [
        r"Next Stage\s*[=:：]\s*([^;；,，\s]+)",
        r"Stage\s*[=:：]\s*([^;；,，\s]+)",
        r"下游(?:对象|Stage|stage)?\s*[=:：]\s*([^;；,，\s]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def derive_downstream_context(previous_flow_contents: list[Dict[str, Any]]) -> Dict[str, Any]:
    for summary in reversed(previous_flow_contents):
        content = summary.get("content", {})
        for item in iter_content_items(content):
            label = str(item.get("label") or "")
            if "Downstream" not in label and "下游" not in label:
                continue
            value = str(item.get("value") or "")
            meta = str(item.get("meta") or "")
            combined = "；".join(part for part in (value, meta) if part)
            stage_name = parse_downstream_stage(combined) or value.strip()
            return _drop_empty(
                {
                    "stage_name": stage_name,
                    "status": meta.replace("Status =", "").replace("Status=", "").strip(),
                    "source_flow_no": summary.get("flow_no"),
                    "source_flow_name": summary.get("flow_name"),
                    "source_label": label,
                    "source_value": value,
                    "source_meta": meta,
                }
            )
    return {}


def normalize_stage_name(raw: Any) -> Optional[str]:
    text = str(raw or "").strip()
    if not text:
        return None
    match = re.search(r"([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)", text)
    if match:
        return match.group(1).upper()
    text = re.sub(r"\bStage\b", "", text, flags=re.IGNORECASE).strip(" ：:=;；,，")
    return text.upper() if text else None


def derive_current_stage_context(previous_flow_contents: list[Dict[str, Any]]) -> Dict[str, Any]:
    preferred_labels = {"object", "current stage", "stage", "当前stage", "当前 stage", "当前站点", "对象"}
    for summary in reversed(previous_flow_contents):
        content = summary.get("content", {})
        for item in iter_content_items(content):
            label = str(item.get("label") or "").strip()
            label_key = label.lower().replace("：", ":")
            if "downstream" in label_key or "下游" in label:
                continue
            if label_key not in preferred_labels and not any(token in label_key for token in ("current stage", "object")):
                continue
            stage_name = normalize_stage_name(item.get("value"))
            if stage_name:
                return _drop_empty(
                    {
                        "stage_name": stage_name,
                        "source_flow_no": summary.get("flow_no"),
                        "source_flow_name": summary.get("flow_name"),
                        "source_label": label,
                        "source_value": item.get("value"),
                    }
                )
    return {"stage_name": "DNW-ANN", "source": "default_demo_stage"}


def build_flow04_inputs(previous_flow_contents: list[Dict[str, Any]]) -> Dict[str, Any]:
    flow04_inputs = load_flow_mock()
    current_stage_context = derive_current_stage_context(previous_flow_contents)
    current_stage = current_stage_context.get("stage_name") or "DNW-ANN"
    downstream_context = derive_downstream_context(previous_flow_contents)
    sql_results: Dict[str, Any] = {
        "stage_name": current_stage,
        "impact_lot": None,
        "move_out_trend": None,
        "query_errors": [],
    }

    try:
        impact_lot_row = locate_flow04_impact_lot(current_stage)
        sql_results["impact_lot"] = impact_lot_row
        if impact_lot_row and impact_lot_row.get("impact_lot_count") is not None:
            impact_scope = flow04_inputs.setdefault("impact_scope", {})
            impact_scope["impact_lot"] = str(int(float(impact_lot_row["impact_lot_count"])))
            impact_scope["impact_lot_source"] = "sql.locate_flow04_impact_lot"
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        sql_results["query_errors"].append({"query": "locate_flow04_impact_lot", "error": str(exc)})

    try:
        move_out_row = locate_flow04_move_out_trend(current_stage)
        sql_results["move_out_trend"] = move_out_row
        if move_out_row:
            move_out_impact = flow04_inputs.setdefault("move_out_impact", {})
            move_out_impact["lot_count_this_week"] = move_out_row.get("lot_count_this_week")
            move_out_impact["lot_count_last_week"] = move_out_row.get("lot_count_last_week")
            move_out_impact["move_out_ratio_pct"] = move_out_row.get("move_out_ratio_pct")
            move_out_impact["move_out_comment"] = move_out_row.get("move_out_comment")
            move_out_impact["source"] = "sql.locate_flow04_move_out_trend"
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        sql_results["query_errors"].append({"query": "locate_flow04_move_out_trend", "error": str(exc)})

    downstream_supply = flow04_inputs.get("downstream_supply")
    if isinstance(downstream_supply, dict):
        stage_name = downstream_context.get("stage_name")
        if stage_name:
            downstream_supply["stage_name"] = stage_name
        downstream_supply["stage_source"] = "previous_flow_content.downstream"
    return {
        "flow04_inputs": flow04_inputs,
        "derived_context": {"current_stage": current_stage_context, "downstream": downstream_context},
        "sql_results": _drop_empty(sql_results),
    }

def build_model_context(case_id: str, previous_record: Optional[Any] = None) -> Dict[str, Any]:
    previous_records = normalize_previous_records(previous_record)
    previous_flow_contents = [previous_content_summary(record) for record in previous_records]
    flow04_context = build_flow04_inputs(previous_flow_contents)
    return {
        "case_id": case_id,
        "flow": {"flow_no": FLOW_NO, "flow_name": FLOW_NAME, "purpose": "影响范围评估"},
        "previous_flows": previous_flow_contents,
        "raw_inputs": {
            "previous_flow_contents": previous_flow_contents,
            **flow04_context,
        },
        "knowledge_pack": load_knowledge_pack(),
        "output_contracts": load_output_contracts(),
        "generation_rules": [
            "优先从 previous_flows[].content 获取 Case Header、风险快照、异常确认结论、临时措施和门禁状态；不要读取或依赖前序全文 text。",
            "如果多个前序流程都提供 content，按 Flow 顺序综合使用；距离当前流程最近的内容优先。",
            "Impact Lot 必须优先使用 raw_inputs.sql_results.impact_lot.impact_lot_count；SQL 无结果时才使用 flow04_inputs。",
            "Move-Out Impact 必须优先使用 raw_inputs.sql_results.move_out_trend 的本周/上周 lot_count、move_out_ratio_pct 和 move_out_comment；不要编造 Shift Risk、ETA Risk 或交付承诺字段。",
            "下游对象必须优先使用 derived_context.downstream.stage_name；例如前序风险快照为 Next Stage = PW-PH 时，下游对象就是 PW-PH。",
            "Flow 04 只做影响范围评估：Impact Lot / WO、Hot Lot / Super Hot Run、Q-Time Risk、Move-Out Gap、下游供料和是否超过单点波动。",
            "Flow 04 不做最终根因排查，不做正式 Case 分级，不派发工程问题包。",
            "只允许使用前端 demo / SQL 已有字段；前序 content 和 SQL 都没有的数据才使用 flow04_inputs；仍缺失则省略，不输出占位值。",
            "不要生成 Product 数、Q-Time 高风险 Lot 数、Recommendation、Shift Risk、ETA Risk、Delivery Risk Level、Affected Commitment 等前端 demo 没有的数据。",
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
    status_only_tokens = {"done", "pending"}
    labels_found: set[str] = set()
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
        if isinstance(item, dict):
            label = str(item.get("label") or "").strip()
            value = str(item.get("value") or "").strip()
            if not (label and value):
                raise ValueError(
                    "当前阶段对话.数据 / 工具调用 object items must include label and value; "
                    f"status is optional: index {index}"
                )
            for required_label in REQUIRED_TOOL_LABELS:
                if required_label in label:
                    labels_found.add(required_label)
            continue
        if ":" not in item_text and "：" not in item_text:
            raise ValueError(
                "当前阶段对话.数据 / 工具调用.items must use source/value wording, "
                f"for example 'Lot Impact: Impact Lot = 42，Impact WO = 18 [Done]': index {index}"
            )
        for required_label in REQUIRED_TOOL_LABELS:
            if required_label in item_text:
                labels_found.add(required_label)
    missing = [label for label in REQUIRED_TOOL_LABELS if label not in labels_found]
    if missing:
        raise ValueError("Flow 04 data/tool calls must include impact dimensions: " + ", ".join(missing))


def validate_downstream_stage_consistency(content: Dict[str, Any], expected_stage: Optional[str]) -> None:
    if not expected_stage:
        return
    items = get_section_items(content, "当前阶段对话", "数据 / 工具调用")
    downstream_items = [
        stringify_display_item(item)
        for item in items
        if "Downstream Supply" in stringify_display_item(item) or "下游" in stringify_display_item(item)
    ]
    if not downstream_items:
        raise ValueError("Downstream Supply is required when previous Downstream / Next Stage is known")
    mismatched = [item for item in downstream_items if expected_stage not in item]
    if mismatched:
        raise ValueError(
            "Downstream Supply must use previous Downstream / Next Stage "
            + repr(expected_stage)
            + ", got: "
            + " | ".join(mismatched)
        )


def find_forbidden_display_term(value: Any, path: str = "$") -> Optional[str]:
    if isinstance(value, str):
        lower_value = value.lower()
        if any(term in lower_value for term in ("mock", "model_context", "frontend_payload", "frontend_demo")):
            return path
        unsupported_terms = (
            "recommendation",
            "shift risk",
            "eta risk",
            "delivery risk",
            "affected commitment",
            "affected product",
            "high risk lot",
            "product 数",
            "高风险 lot 数",
        )
        if any(term in lower_value for term in unsupported_terms):
            return path
        if "clean / 下游 shift" in lower_value:
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


def normalize_model_output(model_output: Dict[str, Any], expected_downstream_stage: Optional[str] = None) -> Dict[str, Any]:
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
    validate_downstream_stage_consistency(content, expected_downstream_stage)
    found = find_forbidden_display_term({"text": text, "content": content})
    if found:
        raise ValueError(f"model_output visible text/content contains forbidden internal wording: {found}")
    forbidden = {"frontend_payload", "frontend_demo", "model_context", "case_snapshot", "prompt", "output_contract", "output_contracts"}
    present = sorted(key for key in forbidden if key in model_output)
    if present:
        raise ValueError(f"model_output contains forbidden keys: {', '.join(present)}")
    return {
        "text": text,
        "content": _drop_empty(dict(content)),
        "impact_assessment_status": model_output.get("impact_assessment_status"),
    }


def decision_from_model_output(model_output: Dict[str, Any]) -> Dict[str, Any]:
    impact_status = str(model_output.get("impact_assessment_status") or "")
    blocked_terms = ("无法评估", "未评估", "阻塞", "On Hold", "on hold")
    if any(term in impact_status for term in blocked_terms):
        default = {"flow_status": "Closed", "case_status": "On Hold", "next_flow_no": None, "next_flow_name": None}
    else:
        default = {"flow_status": "Closed", "case_status": "Processing", "next_flow_no": NEXT_FLOW_NO, "next_flow_name": NEXT_FLOW_NAME}
    for key in ("flow_status", "case_status", "next_flow_no", "next_flow_name"):
        if key in model_output:
            default[key] = model_output.get(key)
    return default


def compose_flow04_result(case_id: str, previous_record: Optional[Any] = None, model_output: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
    expected_downstream_stage = (
        context.get("raw_inputs", {})
        .get("derived_context", {})
        .get("downstream", {})
        .get("stage_name")
    )
    generated = normalize_model_output(model_output, expected_downstream_stage=expected_downstream_stage)
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
        "impact_assessment_status": generated.get("impact_assessment_status"),
        "text": generated["text"],
        "content": generated["content"],
    }


def run(case_id: str, previous_record: Optional[Any] = None, model_output: Optional[Dict[str, Any]] = None, save: bool = True) -> Dict[str, Any]:
    result = compose_flow04_result(case_id, previous_record=previous_record, model_output=model_output)
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
        return result["text"] + "\n\n```json\n" + dumps(result) + "\n```"
    return result["text"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run WIP Bubble Flow 04.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--previous-record-json", help="Previous Flow records JSON. Use '-' for stdin or '@path' for a file.")
    parser.add_argument("--model-output-json", help="Agent generated JSON. Use '-' for stdin or '@path' for a file.")
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
        context = build_model_context(args.case_id, previous_record=previous_record)
        expected_downstream_stage = (
            context.get("raw_inputs", {})
            .get("derived_context", {})
            .get("downstream", {})
            .get("stage_name")
        )
        normalize_model_output(model_output, expected_downstream_stage=expected_downstream_stage)
        print(dumps({"ok": True, "validated": True}))
        return

    result = run(args.case_id, previous_record=previous_record, model_output=model_output)
    print(render(result, args.return_type))


if __name__ == "__main__":
    main()
