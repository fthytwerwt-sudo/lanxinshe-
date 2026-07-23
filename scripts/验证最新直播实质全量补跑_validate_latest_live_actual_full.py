"""Independent validator for the actual latest-live full remediation package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/Volumes/WD_BLACK/澜心社直播")
COMPLETION_DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播全量解析完成_latest_live_full_analysis_completion"
)
DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播实质全量解析_latest_live_actual_full_analysis"
)
OLD_RUNTIME_REF = "full_20260723_155512"
ALLOWED_FINAL_STATUSES = {
    "actual_full_multimodal_analysis_completed_reviewed",
    "actual_full_multimodal_analysis_completed_with_true_source_limits",
}

REQUIRED_ROOT_FILES = [
    "00_最终执行报告_final_execution_report.md",
    "01_526窗口补跑状态_missing_window_remediation_status.csv",
    "02_新模型调用账本_new_model_call_ledger.csv",
    "03_全时间轴变化检测_full_timeline_change_detection.csv",
    "04_清洗后主播逐字稿_clean_host_transcript.csv",
    "05_语义事件时间轴_semantic_event_timeline.csv",
    "06_完整评论生命周期_full_comment_lifecycle.csv",
    "07_评论回复最终关系_comment_reply_final_links.csv",
    "08_动作表情视线_final_action_expression_gaze.csv",
    "09_真实语气音量_final_prosody_volume.csv",
    "10_课程最终对应_final_course_alignment.csv",
    "11_直播大脑最终规则_final_live_brain_rules.csv",
    "12_风险与人工接管_final_risk_handover.csv",
    "13_真实源限制_unknowns_true_source_limits.csv",
    "14_剩余人工复核_final_manual_review_queue.csv",
    "15_独立QA报告_independent_qa_report.json",
    "16_5.6最终验收_final_5_6_acceptance.json",
    "17_Agent执行报告_agent_execution_summary.md",
]

REQUIRED_DIRS = [
    "data/new_visual_evidence_indexes",
    "data/full_comment_indexes",
    "data/final_event_indexes",
    "data/rule_evidence_links",
]

REQUIRED_LEDGER_COLUMNS = [
    "run_id",
    "new_call_id",
    "provider_request_id_or_hash",
    "session_id",
    "coverage_window_id",
    "start_ms",
    "end_ms",
    "model",
    "input_hash",
    "output_hash",
    "request_at",
    "result_at",
    "raw_local_ref",
    "parsed_status",
    "retry_count",
]

FORBIDDEN_UNKNOWN_REASONS = [
    "no_qwen_vl_observation",
    "no_frame_extraction",
    "no_change_scan",
    "no_comment_crop",
    "cost_or_time_skip",
    "old_result_not_covered",
    "not_measured_without_source_failure",
]

MEDIA_SUFFIXES = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".zip",
}


def rel(path: Path | str) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(PROJECT_ROOT.resolve()))
    except (ValueError, FileNotFoundError):
        return str(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{k: str(v or "") for k, v in row.items()} for row in csv.DictReader(fh)]


def read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh).fieldnames or [])


def parse_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_jsonl(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                json.loads(line)
                count += 1
    return count


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value or ""))


def scan_git_safe_payloads(root: Path) -> dict[str, Any]:
    patterns = {
        "secret": re.compile(r"(?i)(DASHSCOPE_API_KEY|ALIBABA_CLOUD_ACCESS_KEY_SECRET|authorization:\s*bearer|api[_-]?key|secret[_-]?key|access[_-]?key)"),
        "signed_url": re.compile(r"https://[^\s\"']+(Expires=|Signature=|OSSAccessKeyId=|x-oss-signature)", re.I),
        "phone": re.compile(r"(?<![0-9a-fA-F])1[3-9]\d{9}(?![0-9a-fA-F])"),
        "email": re.compile(r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"),
        "wechat": re.compile(r"(?i)(微信|vx|v信|wechat)\s*[:：]\s*[a-z0-9_\-]{5,}"),
    }
    hits: dict[str, Any] = {
        "secret_hit_count": 0,
        "signed_url_hit_count": 0,
        "phone_hit_count": 0,
        "email_hit_count": 0,
        "wechat_hit_count": 0,
        "media_file_count": 0,
        "api_raw_payload_file_count": 0,
        "appledouble_count": 0,
        "hit_samples": [],
    }
    for path in root.rglob("*"):
        if path.name.startswith("._"):
            hits["appledouble_count"] += 1
            hits["hit_samples"].append({"path": rel(path), "type": "appledouble"})
            continue
        if path.is_dir():
            continue
        if path.suffix.lower() in MEDIA_SUFFIXES:
            hits["media_file_count"] += 1
            hits["hit_samples"].append({"path": rel(path), "type": "media"})
            continue
        if "api_raw" in path.parts or "asr_raw" in path.parts or "private_manifests" in path.parts:
            hits["api_raw_payload_file_count"] += 1
            hits["hit_samples"].append({"path": rel(path), "type": "raw_payload"})
        if path.suffix.lower() not in {".md", ".json", ".jsonl", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in patterns.items():
            count = len(pattern.findall(text))
            if count:
                hits[f"{name}_hit_count"] += count
                if len(hits["hit_samples"]) < 30:
                    hits["hit_samples"].append({"path": rel(path), "type": name, "count": count})
    return hits


def baseline_missing_window_ids() -> set[str]:
    rows = read_csv_rows(COMPLETION_DOC_ROOT / "02_全时间轴覆盖报告_full_timeline_coverage.csv")
    return {row["coverage_window_id"] for row in rows if row.get("coverage_status") == "source_limited_unknown"}


def validate_raw_ref(row: dict[str, str]) -> tuple[bool, str]:
    ref = row.get("raw_local_ref", "")
    if not ref:
        return False, "blank_raw_local_ref"
    path = PROJECT_ROOT / ref
    if not path.exists() or path.name.startswith("._"):
        return False, "raw_local_ref_missing"
    try:
        payload = parse_json(path)
    except Exception as exc:  # noqa: BLE001
        return False, f"raw_json_parse_failed:{exc.__class__.__name__}"
    body = payload.get("response", {})
    expected = sha256_text(json.dumps(body, ensure_ascii=False, sort_keys=True))
    if expected != row.get("output_hash"):
        return False, "raw_response_output_hash_mismatch"
    return True, ""


def validate(root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "root": rel(root),
        "missing_root_files": [],
        "missing_dirs": [],
        "parse_errors": [],
        "blockers": [],
        "counts": {},
        "qa": {},
    }
    for name in REQUIRED_ROOT_FILES:
        if not (root / name).exists():
            result["missing_root_files"].append(name)
    for name in REQUIRED_DIRS:
        if not (root / name).is_dir():
            result["missing_dirs"].append(name)
    if result["missing_root_files"] or result["missing_dirs"]:
        result["blockers"].append("required_artifacts_missing")
        return result

    for path in root.rglob("*"):
        if path.name.startswith("._") or not path.is_file():
            continue
        try:
            if path.suffix.lower() == ".json":
                parse_json(path)
            elif path.suffix.lower() == ".jsonl":
                parse_jsonl(path)
            elif path.suffix.lower() == ".csv":
                read_csv_rows(path)
        except Exception as exc:  # noqa: BLE001
            result["parse_errors"].append({"path": rel(path), "error": exc.__class__.__name__})

    baseline_ids = baseline_missing_window_ids()
    missing_rows = read_csv_rows(root / "01_526窗口补跑状态_missing_window_remediation_status.csv")
    ledger_rows = read_csv_rows(root / "02_新模型调用账本_new_model_call_ledger.csv")
    change_rows = read_csv_rows(root / "03_全时间轴变化检测_full_timeline_change_detection.csv")
    transcript_rows = read_csv_rows(root / "04_清洗后主播逐字稿_clean_host_transcript.csv")
    semantic_rows = read_csv_rows(root / "05_语义事件时间轴_semantic_event_timeline.csv")
    comment_rows = read_csv_rows(root / "06_完整评论生命周期_full_comment_lifecycle.csv")
    reply_rows = read_csv_rows(root / "07_评论回复最终关系_comment_reply_final_links.csv")
    action_rows = read_csv_rows(root / "08_动作表情视线_final_action_expression_gaze.csv")
    prosody_rows = read_csv_rows(root / "09_真实语气音量_final_prosody_volume.csv")
    course_rows = read_csv_rows(root / "10_课程最终对应_final_course_alignment.csv")
    rule_rows = read_csv_rows(root / "11_直播大脑最终规则_final_live_brain_rules.csv")
    unknown_rows = read_csv_rows(root / "13_真实源限制_unknowns_true_source_limits.csv")
    final_acceptance = parse_json(root / "16_5.6最终验收_final_5_6_acceptance.json")

    header = read_csv_header(root / "02_新模型调用账本_new_model_call_ledger.csv")
    missing_ledger_columns = [col for col in REQUIRED_LEDGER_COLUMNS if col not in header]
    missing_ids = {row["coverage_window_id"] for row in missing_rows}
    ledger_ids = {row["coverage_window_id"] for row in ledger_rows}
    ledger_call_ids = [row.get("new_call_id", "") for row in ledger_rows]
    invalid_sha = sum(
        1
        for row in ledger_rows
        if not valid_sha256(row.get("input_hash", "")) or not valid_sha256(row.get("output_hash", ""))
    )
    blank_provider = sum(1 for row in ledger_rows if not row.get("provider_request_id_or_hash"))
    raw_failures = []
    for row in ledger_rows:
        if row.get("status") == "succeeded":
            ok, reason = validate_raw_ref(row)
            if not ok:
                raw_failures.append({"new_call_id": row.get("new_call_id", ""), "reason": reason})
    terminal_states = Counter(row.get("remediation_status", "") for row in missing_rows)
    forbidden_unknowns = [
        row
        for row in unknown_rows
        if any(reason in row.get("reason", "") for reason in FORBIDDEN_UNKNOWN_REASONS)
    ]
    event_ids = [row.get("semantic_event_id", "") for row in semantic_rows]
    comment_change_samples = [row for row in change_rows if row.get("region") == "comment_area"]
    direct_reply_without_evidence = sum(1 for row in reply_rows if row.get("response_link_type") == "direct_reply")
    topic_similarity_valid = sum(
        1
        for row in course_rows
        if row.get("is_valid_course_match") == "true" and "topic_similarity" in row.get("alignment_type", "")
    )
    valid_course_without_ref = sum(
        1 for row in course_rows if row.get("is_valid_course_match") == "true" and not row.get("course_source_ref")
    )
    rule_event_ids = set(event_ids)
    rule_comment_ids = {row.get("comment_id", "") for row in comment_rows}
    rules_bad_fk = 0
    for row in rule_rows:
        source_events = [x for x in row.get("source_event_ids", "").split(";") if x]
        source_comments = [x for x in row.get("source_comment_ids", "").split(";") if x]
        if not row.get("trigger_evidence_ids") or not source_events:
            rules_bad_fk += 1
            continue
        if any(event_id not in rule_event_ids for event_id in source_events):
            rules_bad_fk += 1
            continue
        if any(comment_id not in rule_comment_ids for comment_id in source_comments):
            rules_bad_fk += 1
    payload_hits = scan_git_safe_payloads(root)

    result["counts"] = {
        "baseline_missing_window_count": len(baseline_ids),
        "missing_status_rows": len(missing_rows),
        "ledger_rows": len(ledger_rows),
        "unique_missing_windows_with_new_call": len(ledger_ids & baseline_ids),
        "missing_window_set_diff_count": len(baseline_ids ^ missing_ids),
        "ledger_window_set_diff_count": len(baseline_ids ^ ledger_ids),
        "duplicate_new_call_id_count": len(ledger_call_ids) - len(set(ledger_call_ids)),
        "old_call_reuse_for_missing_count": sum(1 for row in ledger_rows if OLD_RUNTIME_REF in row.get("raw_local_ref", "")),
        "blank_provider_request_id_count": blank_provider,
        "invalid_sha256_count": invalid_sha,
        "missing_or_hash_mismatched_raw_response_count": len(raw_failures),
        "terminal_window_states": dict(terminal_states),
        "unknown_with_forbidden_reason_count": len(forbidden_unknowns),
        "semantic_events": len(semantic_rows),
        "semantic_duplicate_event_ids": len(event_ids) - len(set(event_ids)),
        "transcript_rows": len(transcript_rows),
        "comment_change_samples": len(comment_change_samples),
        "comment_rows": len(comment_rows),
        "new_comment_from_missing_window_count": sum(1 for row in comment_rows if "new_526_missing_window" in row.get("source_mix", "")),
        "first_seen_ms_mod_300000_count": sum(1 for row in comment_rows if safe_int(row.get("first_seen_ms")) % 300000 == 0),
        "reply_type_counts": dict(Counter(row.get("response_link_type", "") for row in reply_rows)),
        "direct_reply_without_speech_and_visual_evidence_count": direct_reply_without_evidence,
        "action_source_limited_unknown_count": sum(1 for row in action_rows if row.get("action_observation_status") == "source_limited_unknown"),
        "new_visual_evidence_event_count": sum(1 for row in action_rows if row.get("visual_evidence_source") == "new_actual_remediation_qwen_vl"),
        "volume_measured_count": sum(1 for row in prosody_rows if row.get("prosody_status") == "measured_from_source_audio_rms"),
        "not_measured_source_limit_count": sum(1 for row in prosody_rows if row.get("prosody_status") != "measured_from_source_audio_rms"),
        "valid_course_match_without_source_ref_count": valid_course_without_ref,
        "topic_similarity_only_valid_match_count": topic_similarity_valid,
        "rule_without_valid_evidence_foreign_keys_count": rules_bad_fk,
        "final_status": final_acceptance.get("final_status", ""),
        **payload_hits,
    }
    result["qa"] = {
        "missing_ledger_columns": missing_ledger_columns,
        "raw_failures_sample": raw_failures[:20],
        "forbidden_unknowns_sample": [
            {"unknown_id": row.get("unknown_id", ""), "reason": row.get("reason", "")}
            for row in forbidden_unknowns[:20]
        ],
    }

    checks = result["counts"]
    if result["parse_errors"]:
        result["blockers"].append("parse_errors")
    if missing_ledger_columns:
        result["blockers"].append("ledger_required_columns_missing")
    if checks["baseline_missing_window_count"] != 526:
        result["blockers"].append("baseline_missing_window_count_not_526")
    if checks["missing_status_rows"] != 526:
        result["blockers"].append("missing_status_rows_not_526")
    if checks["unique_missing_windows_with_new_call"] != 526:
        result["blockers"].append("not_all_missing_windows_have_new_calls")
    if checks["missing_window_set_diff_count"] != 0 or checks["ledger_window_set_diff_count"] != 0:
        result["blockers"].append("missing_window_set_mismatch")
    if checks["ledger_rows"] < 526:
        result["blockers"].append("new_qwen_attempt_count_lt_526")
    if checks["terminal_window_states"].get("observed_new_qwen", 0) == 0:
        result["blockers"].append("all_missing_window_model_calls_failed")
    for state in checks["terminal_window_states"]:
        if state not in {"observed_new_qwen", "model_execution_failed_after_full_fallback"}:
            result["blockers"].append("invalid_terminal_window_state")
            break
    if checks["old_call_reuse_for_missing_count"]:
        result["blockers"].append("old_call_reused_for_missing_windows")
    if checks["duplicate_new_call_id_count"]:
        result["blockers"].append("duplicate_new_call_ids")
    if checks["blank_provider_request_id_count"]:
        result["blockers"].append("blank_provider_request_id")
    if checks["invalid_sha256_count"]:
        result["blockers"].append("invalid_sha256")
    if checks["missing_or_hash_mismatched_raw_response_count"]:
        result["blockers"].append("raw_response_hash_mismatch_or_missing")
    if checks["unknown_with_forbidden_reason_count"]:
        result["blockers"].append("unknown_forbidden_reason")
    if checks["comment_change_samples"] == 0:
        result["blockers"].append("comment_change_scan_missing")
    if checks["new_comment_from_missing_window_count"] == 0:
        result["blockers"].append("no_new_comments_from_missing_windows")
    if checks["direct_reply_without_speech_and_visual_evidence_count"]:
        result["blockers"].append("direct_reply_without_hard_evidence")
    if checks["volume_measured_count"] == 0 or checks["not_measured_source_limit_count"]:
        result["blockers"].append("prosody_not_fully_measured")
    if checks["valid_course_match_without_source_ref_count"] or checks["topic_similarity_only_valid_match_count"]:
        result["blockers"].append("course_forced_match")
    if checks["rule_without_valid_evidence_foreign_keys_count"]:
        result["blockers"].append("rule_evidence_fk_invalid")
    if checks["semantic_duplicate_event_ids"]:
        result["blockers"].append("duplicate_semantic_event_ids")
    for key in [
        "secret_hit_count",
        "signed_url_hit_count",
        "phone_hit_count",
        "email_hit_count",
        "wechat_hit_count",
        "media_file_count",
        "api_raw_payload_file_count",
        "appledouble_count",
    ]:
        if checks.get(key):
            result["blockers"].append(f"forbidden_git_payload_{key}")
    if checks["final_status"] not in ALLOWED_FINAL_STATUSES:
        result["blockers"].append("final_status_not_allowed")

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
        write_path = root / "15_独立QA报告_independent_qa_report.json"
        write_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall_status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
