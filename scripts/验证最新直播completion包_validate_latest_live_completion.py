"""Validate the latest-live completion package without trusting generator counts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Volumes/WD_BLACK/澜心社直播")
DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播全量解析完成_latest_live_full_analysis_completion"
)

REQUIRED_ROOT_FILES = [
    "00_最终执行报告_final_execution_report.md",
    "01_十场素材最终状态_final_session_status.csv",
    "02_全时间轴覆盖报告_full_timeline_coverage.csv",
    "03_清洗后主播逐字稿_clean_host_transcript.csv",
    "04_语义事件时间轴_semantic_event_timeline.csv",
    "05_评论完整事件_comment_events.csv",
    "06_评论回复最终关系_comment_reply_final_links.csv",
    "07_主播思路动作语气_final_host_logic_action_prosody.csv",
    "08_课程最终对应_final_course_alignment.csv",
    "09_失败风险与人工接管_final_risk_handover.csv",
    "10_直播大脑规则_final_live_brain_rules.csv",
    "11_模型调用账本_model_call_ledger.csv",
    "12_无法确认事项_source_limited_unknowns.csv",
    "13_剩余人工复核_final_manual_review_queue.csv",
    "14_pilot机器复审_pilot_machine_review.json",
    "15_最终验收报告_final_acceptance_report.json",
    "16_最终验收合同结果_final_acceptance_results.json",
    "17_agent_execution_summary.md",
    "18_机器验证清单_machine_validation.json",
]

REQUIRED_DIRS = [
    "data/session_manifests",
    "data/final_event_indexes",
    "data/coverage_indexes",
    "data/rule_evidence_links",
    "data/agent_execution_logs",
]

FORBIDDEN_PATTERNS = [
    r"DASHSCOPE_API_KEY",
    r"ALIBABA_CLOUD_ACCESS_KEY_SECRET",
    r"BEGIN PRIVATE KEY",
    r"signed_url",
    r"transcription_url",
    r"https://[^ \n]+Expires=",
    r"candidate_pending_review",
    r"provisional_pending_5_6_review",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{k: str(v or "") for k, v in row.items()} for row in csv.DictReader(fh)]


def parse_jsonl(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            json.loads(line)
            count += 1
    return count


def scan_forbidden(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith("._"):
            continue
        if path.suffix.lower() not in {".md", ".json", ".jsonl", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                hits.append({"path": str(path.relative_to(PROJECT_ROOT)), "pattern": pattern})
    return hits


def validate(root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "root": str(root.relative_to(PROJECT_ROOT)),
        "missing_root_files": [],
        "missing_dirs": [],
        "parse_errors": [],
        "counts": {},
        "semantic_duplicate_event_ids": 0,
        "rules_without_evidence": 0,
        "topic_similarity_valid_course_match_count": 0,
        "forbidden_hits": [],
        "appledouble_count": 0,
        "blockers": [],
    }
    for name in REQUIRED_ROOT_FILES:
        if not (root / name).exists():
            result["missing_root_files"].append(name)
    for name in REQUIRED_DIRS:
        if not (root / name).is_dir():
            result["missing_dirs"].append(name)

    for path in root.rglob("*"):
        if path.name.startswith("._"):
            result["appledouble_count"] += 1
            continue
        if not path.is_file():
            continue
        try:
            if path.suffix.lower() == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix.lower() == ".jsonl":
                parse_jsonl(path)
            elif path.suffix.lower() == ".csv":
                read_csv_rows(path)
        except Exception as exc:  # noqa: BLE001 - validation should report all parser failures.
            result["parse_errors"].append({"path": str(path.relative_to(PROJECT_ROOT)), "error": exc.__class__.__name__})

    semantic_rows = read_csv_rows(root / "04_语义事件时间轴_semantic_event_timeline.csv")
    semantic_ids = [row.get("semantic_event_id", "") for row in semantic_rows]
    result["semantic_duplicate_event_ids"] = len(semantic_ids) - len(set(semantic_ids))
    result["counts"]["semantic_events"] = len(semantic_rows)
    result["counts"]["visual_coverage_rows"] = len(read_csv_rows(root / "02_全时间轴覆盖报告_full_timeline_coverage.csv"))
    result["counts"]["model_call_ledger_rows"] = len(read_csv_rows(root / "11_模型调用账本_model_call_ledger.csv"))
    result["counts"]["source_limited_unknown_rows"] = len(read_csv_rows(root / "12_无法确认事项_source_limited_unknowns.csv"))

    rule_rows = read_csv_rows(root / "10_直播大脑规则_final_live_brain_rules.csv")
    result["counts"]["rules"] = len(rule_rows)
    result["rules_without_evidence"] = sum(
        1 for row in rule_rows if not row.get("source_event_ids") and not row.get("source_comment_ids")
    )

    course_rows = read_csv_rows(root / "08_课程最终对应_final_course_alignment.csv")
    result["counts"]["course_rows"] = len(course_rows)
    result["topic_similarity_valid_course_match_count"] = sum(
        1
        for row in course_rows
        if row.get("is_valid_course_match") == "true" and "topic_similarity" in row.get("alignment_type", "")
    )

    result["forbidden_hits"] = scan_forbidden(root)

    if result["missing_root_files"]:
        result["blockers"].append("missing_root_files")
    if result["missing_dirs"]:
        result["blockers"].append("missing_dirs")
    if result["parse_errors"]:
        result["blockers"].append("parse_errors")
    if result["semantic_duplicate_event_ids"]:
        result["blockers"].append("duplicate_semantic_event_ids")
    if result["rules_without_evidence"]:
        result["blockers"].append("rules_without_evidence")
    if result["topic_similarity_valid_course_match_count"]:
        result["blockers"].append("topic_similarity_counted_as_valid_course_match")
    if result["forbidden_hits"]:
        result["blockers"].append("forbidden_payload_or_status")
    if result["appledouble_count"]:
        result["blockers"].append("appledouble_files_present")
    result["overall_status"] = "passed" if not result["blockers"] else "blocked"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(DOC_ROOT))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    result = validate(root)
    if args.write:
        out = root / "23_独立验证结果_independent_validation.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall_status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
