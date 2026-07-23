"""Generate the latest-live completion review package.

The script reads the first-pass evidence pack as a read-only baseline and writes
the second-pass review/orchestration package. It does not read raw media, API
keys, signed URLs, or private manifests.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLAN_ROOT = PROJECT_ROOT / "docs" / "直播录屏解析方案_live_recording_analysis" / "新录屏多模态解析规划_new_recording_multimodal_plan"
BASELINE_ROOT = PROJECT_ROOT / "docs" / "直播录屏解析方案_live_recording_analysis" / "最新直播全量取证解析_latest_live_full_evidence_analysis"
OUTPUT_ROOT = PROJECT_ROOT / "docs" / "直播录屏解析方案_live_recording_analysis" / "全量解析补齐复审_full_analysis_completion_review"
LOCAL_RUN_ROOT = PROJECT_ROOT / "_local_runtime" / "最新直播全量解析_latest_live_full_analysis" / "full_20260723_155512"
COURSE_ROOT = PROJECT_ROOT / "项目资料_docs" / "课程解析资料_course_analysis"

BASELINE_COMMIT = "82fdab783aa8384fa428e393368f450fd0d87fdc"
PLANNING_COMMIT = "cea8092f6d20524a516aaea74dd5e2854467c59e"
RUN_STATUS = "approved_for_5_5_remediation"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def git_output(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=PROJECT_ROOT, text=True).strip()


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return max(sum(1 for _ in csv.reader(fh)) - 1, 0)


def load_baseline() -> dict[str, Any]:
    inventory = read_csv(BASELINE_ROOT / "01_素材总清单_source_inventory.csv")
    summary = read_csv(BASELINE_ROOT / "03_场次解析汇总_session_analysis_summary.csv")
    events = read_csv(BASELINE_ROOT / "04_事件时间轴索引_event_timeline_index.csv")
    links = read_csv(BASELINE_ROOT / "05_评论回复候选关系_comment_reply_candidates.csv")
    host = read_csv(BASELINE_ROOT / "06_主播思路动作语气候选_host_logic_action_prosody_candidates.csv")
    course = read_csv(BASELINE_ROOT / "07_课程对应候选_course_alignment_candidates.csv")
    risk = read_csv(BASELINE_ROOT / "08_失败风险与未回复样本_failure_risk_unanswered_samples.csv")
    review = read_csv(BASELINE_ROOT / "09_人工复核队列_manual_review_queue.csv")
    rules = read_csv(BASELINE_ROOT / "10_直播大脑暂定规则_live_brain_provisional_rules.csv")
    manifests = []
    for path in sorted((BASELINE_ROOT / "data" / "session_manifests").glob("latest_live_*_manifest.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    return {
        "inventory": inventory,
        "summary": summary,
        "events": events,
        "links": links,
        "host": host,
        "course": course,
        "risk": risk,
        "review": review,
        "rules": rules,
        "manifests": manifests,
    }


def source_hashes_current(hash_file: str) -> dict[str, str]:
    if hash_file:
        result: dict[str, str] = {}
        for line in Path(hash_file).read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                result[parts[1]] = parts[0]
        return result

    result: dict[str, str] = {}
    for path in sorted((PROJECT_ROOT / "最新直播").glob("*")):
        if not path.is_file() or path.name.startswith("._"):
            continue
        digest = subprocess.check_output(["shasum", "-a", "256", str(path)], text=True).split()[0]
        result[f"最新直播/{path.name}"] = digest
    return result


def build_timeline_rows(data: dict[str, Any], current_hashes: dict[str, str]) -> list[dict[str, Any]]:
    events_by_session = defaultdict(list)
    host_by_session = defaultdict(list)
    course_by_session = defaultdict(list)
    review_by_session = Counter()
    link_by_session = defaultdict(list)
    for row in data["events"]:
        events_by_session[row["session_id"]].append(row)
    for row in data["host"]:
        host_by_session[row["session_id"]].append(row)
    for row in data["course"]:
        course_by_session[row["session_id"]].append(row)
    for row in data["review"]:
        review_by_session[row["session_id"]] += 1
    for row in data["links"]:
        link_by_session[row["session_id"]].append(row)

    rows = []
    for row in data["summary"]:
        session_id = row["session_id"]
        duration_ms = int(round(float(row["duration_min"]) * 60_000))
        vision_windows = int(row["vision_window_count"])
        vision_covered_ms = vision_windows * 8_000
        visual_pct = round(vision_covered_ms / duration_ms * 100, 2) if duration_ms else 0
        host_rows = host_by_session[session_id]
        course_rows = course_by_session[session_id]
        links = link_by_session[session_id]
        action_filled = sum(1 for item in host_rows if item.get("observed_action"))
        prosody_filled = sum(1 for item in host_rows if item.get("prosody_label"))
        determined_links = sum(1 for item in links if item.get("link_status") not in {"candidate_pending_review", ""})
        valid_course = sum(1 for item in course_rows if item.get("alignment_type") not in {"topic_similarity_only", ""})
        source_video = row["source_video"]
        current_hash = current_hashes.get(f"最新直播/{source_video}", "")
        baseline_hash = next((item["source_hash"] for item in data["inventory"] if item["source_video"] == source_video), "")
        rows.append(
            {
                "session_id": session_id,
                "duration_min": row["duration_min"],
                "source_hash_status": "unchanged" if current_hash == baseline_hash else "changed_or_unverified",
                "asr_status": row["asr_status"],
                "asr_sentence_count": row["asr_sentence_count"],
                "asr_coverage_status": "partial_needs_audio_source_classification",
                "host_speech_usable_status": "missing_field",
                "vision_window_count": vision_windows,
                "vision_covered_seconds": round(vision_covered_ms / 1000, 2),
                "vision_coverage_pct": visual_pct,
                "vision_missing_pct": round(100 - visual_pct, 2),
                "base_scan_60s_estimated_windows": math.ceil(duration_ms / 60_000),
                "dense_scan_20s_estimated_windows": math.ceil(duration_ms / 20_000),
                "comment_event_count": row["comment_event_count"],
                "reply_candidate_count": row["reply_candidate_count"],
                "comment_reply_determined_pct": round(determined_links / len(links) * 100, 2) if links else 0,
                "action_field_coverage_pct": round(action_filled / len(host_rows) * 100, 2) if host_rows else 0,
                "prosody_field_coverage_pct": round(prosody_filled / len(host_rows) * 100, 2) if host_rows else 0,
                "course_effective_match_pct": round(valid_course / len(course_rows) * 100, 2) if course_rows else 0,
                "manual_review_count": review_by_session[session_id],
                "coverage_status": "partial",
                "required_remediation": "base_scan_60s,dense_scan_for_comment_motion,audio_source_classification,semantic_event_segmentation",
            }
        )
    return rows


def build_field_matrix(data: dict[str, Any]) -> list[dict[str, Any]]:
    host = data["host"]
    course = data["course"]
    links = data["links"]
    rules = data["rules"]
    review = data["review"]
    action_filled = sum(1 for row in host if row.get("observed_action"))
    prosody_filled = sum(1 for row in host if row.get("prosody_label"))
    topic_only = sum(1 for row in course if row.get("alignment_type") == "topic_similarity_only")
    link_pending = sum(1 for row in links if row.get("link_status") == "candidate_pending_review")
    template_counter = Counter(row.get("response_template_structure", "") for row in rules)
    manual_by_session = Counter(row["session_id"] for row in review)
    rows = [
        {
            "domain": "source",
            "field_or_requirement": "10 source videos, hashes, metadata",
            "planned_standard": "all source videos locked by path/hash/duration",
            "current_evidence": f"inventory_rows={len(data['inventory'])}; manifest_rows={len(data['manifests'])}",
            "status": "passed",
            "gap_id": "",
            "remediation_lane": "",
            "done_when": "source_hash_status remains unchanged for all 10 sessions",
        },
        {
            "domain": "asr",
            "field_or_requirement": "ASR full transcription",
            "planned_standard": "all sessions have ASR evidence and event references",
            "current_evidence": "10/10 asr_status=succeeded; 7296 host_speech events",
            "status": "partial",
            "gap_id": "GAP-AUDIO-001",
            "remediation_lane": "audio_source_classification",
            "done_when": "each ASR segment has audio_source_type, speaker_role, asr_quality, host_speech_usable",
        },
        {
            "domain": "asr",
            "field_or_requirement": "lyrics/background/other speaker separation",
            "planned_standard": "non-host audio excluded from host speech/course/rule layers",
            "current_evidence": "raw ASR exists but no committed classification fields",
            "status": "missing",
            "gap_id": "GAP-AUDIO-002",
            "remediation_lane": "audio_source_classification",
            "done_when": "song/background/platform/other_speaker segments are labelled and excluded from host_speech_usable=true",
        },
        {
            "domain": "event",
            "field_or_requirement": "semantic event segmentation",
            "planned_standard": "events represent topic/comment/reply/course/sales/action transitions",
            "current_evidence": "event_type counts are host_speech=7296, comment=302, multimodal_window=138",
            "status": "partial",
            "gap_id": "GAP-EVENT-001",
            "remediation_lane": "semantic_segmentation",
            "done_when": "ASR sentence events are merged/split into semantic events with transition markers",
        },
        {
            "domain": "schema",
            "field_or_requirement": "event schema compliance and approval gate",
            "planned_standard": "schema_version/source_video/source_hash/source_duration/privacy/manual_review/idempotency and machine approval are present",
            "current_evidence": "baseline event rows predate final schema and first pass skipped 5.6 pilot approval gate",
            "status": "missing",
            "gap_id": "GAP-CONTRACT-001",
            "remediation_lane": "contract_preflight",
            "done_when": "5.5 pilot has locked schema migration, source hashes, checkpoint/resume plan and disjoint write scopes before full remediation",
        },
        {
            "domain": "vision",
            "field_or_requirement": "full timeline visual coverage",
            "planned_standard": "base scan plus dense scan covers comment/action lifecycle",
            "current_evidence": "138 windows * 8s; about 2.7%-3.0% per session",
            "status": "invalid",
            "gap_id": "GAP-VISION-001",
            "remediation_lane": "qwen_vl_base_dense_scan",
            "done_when": "60s base scan exists for all sessions and dense windows cover detected comment/action changes",
        },
        {
            "domain": "comment",
            "field_or_requirement": "comment OCR lifecycle",
            "planned_standard": "first_seen,last_seen,dedup,redacted_text,intent,risk,status",
            "current_evidence": "302 comment events from sparse vision windows; no lifecycle tracking fields",
            "status": "partial",
            "gap_id": "GAP-COMMENT-001",
            "remediation_lane": "comment_tracking_redaction",
            "done_when": "comments have redacted stable ids, first/last seen, dedup group, intent/risk and final_state",
        },
        {
            "domain": "reply",
            "field_or_requirement": "comment-reply causality",
            "planned_standard": "direct/merged/prompted/topic_only/unanswered/insufficient evidence",
            "current_evidence": f"candidate_pending_review={link_pending}/{len(links)}",
            "status": "invalid",
            "gap_id": "GAP-REPLY-001",
            "remediation_lane": "reply_causality_arbitration",
            "done_when": "high-value relations have evidence spans and non-causal topic-only links are downgraded",
        },
        {
            "domain": "action",
            "field_or_requirement": "observable action fields",
            "planned_standard": "action, expression, gaze, posture, gesture, courseware interaction per key event",
            "current_evidence": f"observed_action filled {action_filled}/{len(host)}",
            "status": "missing",
            "gap_id": "GAP-ACTION-001",
            "remediation_lane": "visual_action_extraction",
            "done_when": "key events have observed values or explicit not_observable with evidence_ref",
        },
        {
            "domain": "prosody",
            "field_or_requirement": "pace/pause/volume/emphasis/emotion",
            "planned_standard": "prosody measured or observed with confidence",
            "current_evidence": f"prosody_label filled {prosody_filled}/{len(host)} but pause_before empty across baseline",
            "status": "partial",
            "gap_id": "GAP-PROSODY-001",
            "remediation_lane": "prosody_feature_extraction",
            "done_when": "speaker events include speaking_rate, pause_before/after, emphasis and confidence",
        },
        {
            "domain": "course",
            "field_or_requirement": "course alignment",
            "planned_standard": "source_ref-backed direct/rewritten/case/comment-driven/no_match labels",
            "current_evidence": f"topic_similarity_only={topic_only}/{len(course)}",
            "status": "invalid",
            "gap_id": "GAP-COURSE-001",
            "remediation_lane": "course_alignment_cleanup",
            "done_when": "obvious wrong matches removed; no_match allowed; exact source blocked if full transcript source missing",
        },
        {
            "domain": "brain_rule",
            "field_or_requirement": "live brain rule traceability",
            "planned_standard": "rule binds event_id, trigger evidence, user state, course/action/prosody basis and risk",
            "current_evidence": f"rules={len(rules)}; unique_templates={len(template_counter)}; event_id_field_present={'event_id' in rules[0] if rules else False}",
            "status": "invalid",
            "gap_id": "GAP-RULE-001",
            "remediation_lane": "brain_rule_regeneration",
            "done_when": "rules are regenerated from validated events and no duplicated template batch remains",
        },
        {
            "domain": "manual_review",
            "field_or_requirement": "risk-weighted review queue",
            "planned_standard": "review after agent arbitration, ranked by risk/uncertainty",
            "current_evidence": f"per_session_counts={dict(sorted(manual_by_session.items()))}",
            "status": "invalid",
            "gap_id": "GAP-REVIEW-001",
            "remediation_lane": "manual_review_prioritization",
            "done_when": "review queue is generated from unresolved high-risk gaps, not fixed 80 per session",
        },
    ]
    return rows


def build_invalid_inventory(data: dict[str, Any]) -> list[dict[str, Any]]:
    rules = data["rules"]
    links = data["links"]
    course = data["course"]
    host = data["host"]
    review = data["review"]
    rows: list[dict[str, Any]] = []
    rows.append(
        {
            "invalid_id": "INV-001",
            "scope": "visual_coverage",
            "affected_count": 10,
            "invalid_type": "sparse_sampling_used_as_coverage",
            "evidence": "vision uses 300s interval and 8s clips; <=3.01% visual coverage per session",
            "severity": "critical",
            "required_fix": "run base scan and dense scan before visual/comment/action completion claims",
        }
    )
    rows.append(
        {
            "invalid_id": "INV-002",
            "scope": "course_alignment",
            "affected_count": len(course),
            "invalid_type": "topic_similarity_only",
            "evidence": "all course rows are topic_similarity_only/course_alignment_candidate_only",
            "severity": "high",
            "required_fix": "remove false precision; classify as direct/rewritten/case/comment-driven/no_match/source_blocked",
        }
    )
    rows.append(
        {
            "invalid_id": "INV-003",
            "scope": "brain_rules",
            "affected_count": len(rules),
            "invalid_type": "template_batch",
            "evidence": "all rules share one response_template_structure and lack event_id column",
            "severity": "critical",
            "required_fix": "regenerate only from validated events with rule_event_refs",
        }
    )
    rows.append(
        {
            "invalid_id": "INV-004",
            "scope": "comment_reply",
            "affected_count": len(links),
            "invalid_type": "candidate_without_causality",
            "evidence": "all link_status values are candidate_pending_review",
            "severity": "high",
            "required_fix": "perform causal arbitration and downgrade uncertain/topic-only links",
        }
    )
    rows.append(
        {
            "invalid_id": "INV-005",
            "scope": "action_fields",
            "affected_count": sum(1 for row in host if not row.get("observed_action")),
            "invalid_type": "missing_observable_action",
            "evidence": "observed_action and paired visual fields empty for most host rows",
            "severity": "high",
            "required_fix": "extract from Qwen-VL windows or mark not_observable",
        }
    )
    rows.append(
        {
            "invalid_id": "INV-006",
            "scope": "manual_review",
            "affected_count": len(review),
            "invalid_type": "fixed_quota_queue",
            "evidence": "manual_review_queue is exactly 80 rows per session",
            "severity": "medium",
            "required_fix": "re-rank after arbitration by risk and uncertainty",
        }
    )
    rows.append(
        {
            "invalid_id": "INV-007",
            "scope": "vision_raw_traceability",
            "affected_count": 1,
            "invalid_type": "clip_without_matching_api_raw",
            "evidence": "latest_live_07 has 20 vision clips but 19 non-AppleDouble api_raw files",
            "severity": "high",
            "required_fix": "re-run or mark the missing visual window raw response before using it as evidence",
        }
    )
    return rows


def build_gaps(timeline_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_base = sum(int(row["base_scan_60s_estimated_windows"]) for row in timeline_rows)
    total_dense = sum(int(row["dense_scan_20s_estimated_windows"]) for row in timeline_rows)
    return [
        {
            "gap_id": "GAP-CONTRACT-001",
            "lane": "contract_preflight",
            "severity": "critical",
            "source": "5.6-sol controller review and planning schema",
            "status": "missing",
            "problem": "Baseline full run skipped the pilot approval gate and event rows are not fully compliant with the planning schema.",
            "affected_sessions": "all",
            "task": "lock schema migration, source hash validation, pilot scope, checkpoint/resume and disjoint output directories before any full remediation.",
            "done_when": "machine approval remains full_execution=false until pilot_review_decision=approved and all preflight checks pass.",
        },
        {
            "gap_id": "GAP-AUDIO-001",
            "lane": "audio_source_classification",
            "severity": "critical",
            "source": "baseline ASR events and raw ASR evidence",
            "status": "missing",
            "problem": "ASR succeeded but audio_source_type/speaker_role/asr_quality/host_speech_usable are absent.",
            "affected_sessions": "all",
            "task": "classify each ASR segment as host speech, song/background/platform/other speaker/noise; flag usable host speech.",
            "done_when": "all ASR-derived speaker events have classification fields and non-host audio is excluded from course/rule generation.",
        },
        {
            "gap_id": "GAP-EVENT-001",
            "lane": "semantic_segmentation",
            "severity": "high",
            "source": "04 event timeline",
            "status": "partial",
            "problem": "Timeline is still dominated by ASR sentence rows rather than semantic live events.",
            "affected_sessions": "all",
            "task": "merge/split events around topic switches, comment appearances, replies, course segments, sales nodes and anomalies.",
            "done_when": "each semantic event has source event ids, start/end, event_type, trigger and review status.",
        },
        {
            "gap_id": "GAP-VISION-001",
            "lane": "qwen_vl_base_dense_scan",
            "severity": "critical",
            "source": "session manifests and 03 summary",
            "status": "invalid",
            "problem": f"Sparse visual sampling is the only visual evidence; base_scan_60s_estimated_windows={total_base}, dense20_estimated_windows={total_dense}.",
            "affected_sessions": "all",
            "task": "use Alibaba Qwen-VL for 60s base scan and dense scans on comment/action/transition windows.",
            "done_when": "all sessions have base scan coverage and dense scan task records; uncovered spans are explicitly not_observable/source_limit.",
        },
        {
            "gap_id": "GAP-VISION-002",
            "lane": "qwen_vl_base_dense_scan",
            "severity": "high",
            "source": "local runtime api_raw and vision_clips inventory",
            "status": "missing",
            "problem": "latest_live_07 has a visual clip without a matching non-AppleDouble API raw response.",
            "affected_sessions": ["latest_live_07"],
            "task": "backfill or explicitly invalidate the missing latest_live_07 visual raw response before downstream use.",
            "done_when": "vision_clips and api_raw counts match for every evidence-bearing window, or missing windows are excluded with reason.",
        },
        {
            "gap_id": "GAP-COMMENT-001",
            "lane": "comment_tracking_redaction",
            "severity": "high",
            "source": "Qwen-VL sparse windows and comment event rows",
            "status": "partial",
            "problem": "Comment events do not track lifecycle, dedup group, first/last seen or final state.",
            "affected_sessions": "all",
            "task": "track redacted comments across frames, distinguish username/body/system message, and store lifecycle fields.",
            "done_when": "each observable comment has stable redacted id, first_seen_ms, last_seen_ms, dedup_key, intent, risk, final_state.",
        },
        {
            "gap_id": "GAP-REPLY-001",
            "lane": "reply_causality_arbitration",
            "severity": "high",
            "source": "05 comment reply candidates",
            "status": "invalid",
            "problem": "Candidate rows do not prove direct response, merged response, prompted comment, topic-only, unanswered or insufficient evidence.",
            "affected_sessions": "all",
            "task": "arbitrate high-value relations using comment lifecycle, ASR semantic events and visual windows.",
            "done_when": "each high-value relation has response_link_type, evidence spans, alternatives, confidence and review outcome.",
        },
        {
            "gap_id": "GAP-ACTION-001",
            "lane": "visual_action_extraction",
            "severity": "high",
            "source": "06 host logic/action/prosody candidates",
            "status": "missing",
            "problem": "Most action/expression/gaze/posture/gesture/courseware fields are empty.",
            "affected_sessions": "all",
            "task": "extract observable actions from dense Qwen-VL windows and mark not_observable where needed.",
            "done_when": "key events have action fields or explicit not_observable with evidence_ref and confidence.",
        },
        {
            "gap_id": "GAP-PROSODY-001",
            "lane": "prosody_feature_extraction",
            "severity": "medium",
            "source": "06 host logic/action/prosody candidates",
            "status": "partial",
            "problem": "Text-derived prosody labels exist but pause_before/volume/emphasis evidence is not measured.",
            "affected_sessions": "all",
            "task": "derive speech rate, pause before/after and emphasis from ASR timestamps/audio metadata; keep confidence.",
            "done_when": "usable host speech events include measured/derived prosody features and confidence.",
        },
        {
            "gap_id": "GAP-COURSE-001",
            "lane": "course_alignment_cleanup",
            "severity": "high",
            "source": "07 course candidates and course bridge files",
            "status": "invalid",
            "problem": "All rows are topic_similarity_only; full raw source refs are partly historical previous_pack refs.",
            "affected_sessions": "all",
            "task": "remove false matches, allow no_match, use available bridge/source_quote refs, and mark exact alignment blocked where source is missing.",
            "done_when": "course_alignment contains direct/rewritten/case/comment-driven/no_match/source_blocked with auditable source_ref.",
        },
        {
            "gap_id": "GAP-RULE-001",
            "lane": "brain_rule_regeneration",
            "severity": "critical",
            "source": "10 provisional rules",
            "status": "invalid",
            "problem": "Rules are template-like and not bound to event_id/trigger evidence/action/prosody basis.",
            "affected_sessions": "all",
            "task": "regenerate rules only after reply/course/action/prosody validation.",
            "done_when": "each rule binds event ids, trigger evidence, user state, strategy, course/action/prosody basis and risk.",
        },
        {
            "gap_id": "GAP-REVIEW-001",
            "lane": "manual_review_prioritization",
            "severity": "medium",
            "source": "09 manual review queue",
            "status": "invalid",
            "problem": "Queue is fixed at 80 per session instead of post-arbitration risk ranking.",
            "affected_sessions": "all",
            "task": "rebuild queue after agent arbitration with evidence, alternatives and review action.",
            "done_when": "final queue contains only unresolved high-risk or low-confidence items ranked by priority.",
        },
    ]


def build_tasks(gaps: list[dict[str, Any]], timeline_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    task_specs = {
        "contract_preflight": {
            "agent_goal_id": "AGENT-CONTRACT-PREFLIGHT",
            "parallel_group": "stage_0_required_before_pilot",
            "input_paths": [
                "docs/直播录屏解析方案_live_recording_analysis/新录屏多模态解析规划_new_recording_multimodal_plan/data/event_schema.json",
                "docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/04_缺口清单_gap_manifest.json",
            ],
            "output_contract": "pilot_preflight_contract.json + schema_migration_map.csv",
            "alibaba_api": "capability check only; no raw payload committed",
        },
        "audio_source_classification": {
            "agent_goal_id": "AGENT-AUDIO-ASR",
            "parallel_group": "stage_1_independent",
            "input_paths": [
                "_local_runtime/最新直播全量解析_latest_live_full_analysis/full_20260723_155512/*/asr_raw/",
                "docs/直播录屏解析方案_live_recording_analysis/最新直播全量取证解析_latest_live_full_evidence_analysis/04_事件时间轴索引_event_timeline_index.csv",
            ],
            "output_contract": "audio_segment_classification.jsonl + updated redacted speaker event candidates",
            "alibaba_api": "Fun-ASR existing results; no full ASR rerun unless low-quality spans are identified",
        },
        "semantic_segmentation": {
            "agent_goal_id": "AGENT-EVENT-SEGMENT",
            "parallel_group": "stage_2_after_audio_and_vision_base",
            "input_paths": ["audio classifications", "comment lifecycle", "base visual scan"],
            "output_contract": "semantic_event_timeline.jsonl",
            "alibaba_api": "not required unless missing modality evidence needs Qwen-VL backfill",
        },
        "qwen_vl_base_dense_scan": {
            "agent_goal_id": "AGENT-VISION-COMMENT-ACTION",
            "parallel_group": "stage_1_independent",
            "input_paths": ["最新直播/*.mp4", "session manifests"],
            "output_contract": "redacted visual window observations + local-only raw responses",
            "alibaba_api": "Qwen-VL via existing Alibaba route; estimated_base_scan_windows="
            + str(sum(int(row["base_scan_60s_estimated_windows"]) for row in timeline_rows)),
        },
        "comment_tracking_redaction": {
            "agent_goal_id": "AGENT-VISION-COMMENT-ACTION",
            "parallel_group": "stage_2_after_base_scan",
            "input_paths": ["base/dense visual scan outputs"],
            "output_contract": "comment_lifecycle_redacted.jsonl",
            "alibaba_api": "Qwen-VL for OCR where comments are visible",
        },
        "reply_causality_arbitration": {
            "agent_goal_id": "AGENT-REPLY-ARBITER",
            "parallel_group": "stage_3_after_timeline",
            "input_paths": ["semantic_event_timeline", "comment_lifecycle", "audio classifications"],
            "output_contract": "reply_relation_arbitrated.jsonl",
            "alibaba_api": "not primary; use existing evidence and targeted Qwen-VL only for ambiguous windows",
        },
        "visual_action_extraction": {
            "agent_goal_id": "AGENT-VISION-COMMENT-ACTION",
            "parallel_group": "stage_2_after_dense_scan",
            "input_paths": ["dense visual windows", "semantic event windows"],
            "output_contract": "action_observation_candidates.jsonl",
            "alibaba_api": "Qwen-VL action observation",
        },
        "prosody_feature_extraction": {
            "agent_goal_id": "AGENT-AUDIO-ASR",
            "parallel_group": "stage_2_after_audio",
            "input_paths": ["ASR timestamps", "audio metadata"],
            "output_contract": "prosody_features.jsonl",
            "alibaba_api": "reuse ASR timestamps; no new supplier",
        },
        "course_alignment_cleanup": {
            "agent_goal_id": "AGENT-COURSE-RULES",
            "parallel_group": "stage_2_after_semantic_text",
            "input_paths": ["course bridge CSV/MD", "semantic host speech"],
            "output_contract": "course_alignment_validated.jsonl",
            "alibaba_api": "optional Qwen text structuring only; exact alignment blocked if source missing",
        },
        "brain_rule_regeneration": {
            "agent_goal_id": "AGENT-COURSE-RULES",
            "parallel_group": "stage_4_after_arbitration",
            "input_paths": ["validated reply/course/action/prosody outputs"],
            "output_contract": "live_brain_rules_traceable.jsonl",
            "alibaba_api": "Qwen text structuring allowed after evidence validation",
        },
        "manual_review_prioritization": {
            "agent_goal_id": "AGENT-FINAL-MERGE-QA",
            "parallel_group": "stage_5_final",
            "input_paths": ["all unresolved gap outputs"],
            "output_contract": "risk_weighted_manual_review_queue.csv",
            "alibaba_api": "not required",
        },
    }
    tasks = []
    for index, gap in enumerate(gaps, 1):
        spec = task_specs[gap["lane"]]
        tasks.append(
            {
                "task_id": f"RT-{index:03d}",
                "gap_id": gap["gap_id"],
                "lane": gap["lane"],
                "severity": gap["severity"],
                "agent_goal_id": spec["agent_goal_id"],
                "parallel_group": spec["parallel_group"],
                "task": gap["task"],
                "input_paths": spec["input_paths"],
                "output_contract": spec["output_contract"],
                "alibaba_api_route": spec["alibaba_api"],
                "done_when": gap["done_when"],
                "write_scope": "5.5 remediation output directory only; first-pass baseline remains read-only",
                "blocked_if": [
                    "source_hash_changed",
                    "raw_or_signed_url_would_enter_repo",
                    "api_permission_or_balance_failed",
                    "required_course_source_missing_for_exact_alignment",
                ],
            }
        )
    return tasks


def build_agent_goals(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_agent = defaultdict(list)
    for task in tasks:
        by_agent[task["agent_goal_id"]].append(task["task_id"])
    return [
        {
            "agent_goal_id": "AGENT-CONTRACT-PREFLIGHT",
            "model": "gpt-5.6-sol",
            "role": "contract_preflight_and_pilot_gate",
            "goal": "lock schema migration, source hash validation, pilot scope, checkpoint/resume and full-execution stop line",
            "owned_tasks": by_agent["AGENT-CONTRACT-PREFLIGHT"],
            "write_scope": "remediation/contract_preflight/",
            "must_not_write": ["baseline evidence directory", "_local_runtime raw private manifests", "source videos"],
            "done_when": "pilot_remediation_only is ready and full remediation remains blocked until 5.6 approves pilot results",
        },
        {
            "agent_goal_id": "AGENT-AUDIO-ASR",
            "model": "gpt-5.5",
            "role": "audio_asr_prosody_lane",
            "goal": "classify ASR/audio source, mark usable host speech, derive prosody features and low-quality spans",
            "owned_tasks": by_agent["AGENT-AUDIO-ASR"],
            "write_scope": "remediation/audio_asr_prosody/",
            "must_not_write": ["baseline evidence directory", "_local_runtime raw private manifests", "source videos"],
            "done_when": "all ASR-derived events have source classification and prosody confidence where observable",
        },
        {
            "agent_goal_id": "AGENT-VISION-COMMENT-ACTION",
            "model": "gpt-5.5",
            "role": "qwen_vl_visual_comment_action_lane",
            "goal": "run Alibaba Qwen-VL base/dense visual scan, track redacted comments and observable actions",
            "owned_tasks": by_agent["AGENT-VISION-COMMENT-ACTION"],
            "write_scope": "remediation/vision_comment_action/",
            "must_not_write": ["baseline evidence directory", "raw media into Git", "unredacted comments"],
            "done_when": "base/dense scan outputs exist and comment/action gaps are either filled or not_observable/source_limit",
        },
        {
            "agent_goal_id": "AGENT-EVENT-SEGMENT",
            "model": "gpt-5.5",
            "role": "semantic_timeline_lane",
            "goal": "merge raw ASR/comment/visual records into semantic live events with transition markers",
            "owned_tasks": by_agent["AGENT-EVENT-SEGMENT"],
            "write_scope": "remediation/semantic_timeline/",
            "must_not_write": ["baseline evidence directory"],
            "done_when": "timeline events are semantically segmented and preserve source event ids",
        },
        {
            "agent_goal_id": "AGENT-REPLY-ARBITER",
            "model": "gpt-5.5",
            "role": "comment_reply_causality_lane",
            "goal": "arbitrate comment-reply relations without treating temporal proximity as causality",
            "owned_tasks": by_agent["AGENT-REPLY-ARBITER"],
            "write_scope": "remediation/reply_arbitration/",
            "must_not_write": ["unredacted comments", "baseline evidence directory"],
            "done_when": "high-value links are direct/merged/prompted/topic_only/unanswered/insufficient_evidence",
        },
        {
            "agent_goal_id": "AGENT-COURSE-RULES",
            "model": "gpt-5.5",
            "role": "course_alignment_and_rules_lane",
            "goal": "clean course alignment and regenerate traceable live-brain rules from validated evidence",
            "owned_tasks": by_agent["AGENT-COURSE-RULES"],
            "write_scope": "remediation/course_rules/",
            "must_not_write": ["baseline evidence directory"],
            "done_when": "false course matches are removed and rules bind real event evidence",
        },
        {
            "agent_goal_id": "AGENT-FINAL-MERGE-QA",
            "model": "gpt-5.6-sol",
            "role": "final_merge_and_acceptance_lane",
            "goal": "merge 5.5 outputs, validate contracts, generate final acceptance evidence for 5.6 review",
            "owned_tasks": by_agent["AGENT-FINAL-MERGE-QA"],
            "write_scope": "remediation/final_merge/",
            "must_not_write": ["raw media", "private manifests", "unredacted comments"],
            "done_when": "machine acceptance checks pass and residual blocked items are explicit",
        },
    ]


def build_dependencies(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "version": "1.0",
        "execution_order": [
            "preflight_source_hash_and_api_check",
            "stage_0_contract_preflight_pilot_gate",
            "stage_1_independent_audio_and_visual_base",
            "stage_2_comment_action_prosody_course_cleanup",
            "stage_3_semantic_timeline_and_reply_arbitration",
            "stage_4_brain_rule_regeneration",
            "stage_5_final_merge_and_5_6_acceptance",
        ],
        "parallel_groups": {
            "stage_0_required_before_pilot": ["AGENT-CONTRACT-PREFLIGHT"],
            "stage_1_independent": ["AGENT-AUDIO-ASR", "AGENT-VISION-COMMENT-ACTION"],
            "stage_2_after_base_scan": ["AGENT-VISION-COMMENT-ACTION", "AGENT-COURSE-RULES"],
            "stage_3_after_timeline": ["AGENT-REPLY-ARBITER"],
            "stage_4_after_arbitration": ["AGENT-COURSE-RULES"],
            "stage_5_final": ["AGENT-FINAL-MERGE-QA"],
        },
        "hard_dependencies": [
            {
                "before": "course_alignment_cleanup",
                "after": "audio_source_classification",
                "reason": "non-host audio must not enter course matching",
            },
            {
                "before": "reply_causality_arbitration",
                "after": "comment_tracking_redaction",
                "reason": "reply relation needs comment lifecycle",
            },
            {
                "before": "brain_rule_regeneration",
                "after": "reply_causality_arbitration,course_alignment_cleanup,visual_action_extraction,prosody_feature_extraction",
                "reason": "rules must be generated from validated evidence, not templates",
            },
        ],
        "write_conflict_policy": "one agent owns one remediation subdirectory; final merge is serial",
        "tasks": [{k: task[k] for k in ["task_id", "gap_id", "lane", "agent_goal_id", "parallel_group"]} for task in tasks],
    }


def build_acceptance_contract(timeline_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "contract_version": "1.0",
        "final_review_owner": "gpt-5.6-sol",
        "baseline_commit": BASELINE_COMMIT,
        "required_status_values": ["passed", "partial", "missing", "invalid", "blocked_source_limit", "not_applicable"],
        "hard_gates": [
            "10/10 source videos hash unchanged",
            "all JSON/JSONL/CSV parse",
            "no raw media, raw comments, signed URLs, API keys, or private manifests in Git",
            "visual coverage no longer relies only on 300s/8s sparse windows",
            "ASR host speech excludes song/background/platform/other-speaker segments",
            "comment-reply relations have evidence or are explicitly insufficient_evidence/unanswered/topic_only",
            "course alignment does not count topic_similarity_only as valid",
            "live brain rules bind real event ids and are not duplicated templates",
            "manual review queue is risk-ranked after arbitration",
        ],
        "quantitative_minimums": {
            "source_sessions": 10,
            "base_scan_60s_estimated_windows": sum(int(row["base_scan_60s_estimated_windows"]) for row in timeline_rows),
            "dense_scan_20s_estimated_windows_reference": sum(int(row["dense_scan_20s_estimated_windows"]) for row in timeline_rows),
            "duplicate_event_ids": 0,
            "topic_similarity_only_valid_course_match_allowed": 0,
            "template_rule_batch_allowed": 0,
        },
        "completion_boundary": "Passing this contract means full analysis evidence is ready for human/project review; it does not mean customer acceptance, business outcome, or digital-human production readiness.",
        "blocked_policy": {
            "course_exact_alignment_source_missing": "lane may be blocked_source_limit while other lanes continue",
            "comment_unobservable": "write source_limit/not_observable, never invent comments",
            "action_unobservable": "write not_observable with evidence_ref",
            "api_failure": "blocked_api_permission_or_balance, no local fallback impersonation",
        },
    }


def build_approval(gaps: list[dict[str, Any]], tasks: list[dict[str, Any]], agent_goals: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    pilot_allowed = bool(args.supports_5_6_sol and args.supports_5_5 and args.alibaba_multimodal_authorized)
    return {
        "review_status": "request_changes_pilot_remediation_only" if pilot_allowed else "blocked_requires_model_or_api_authorization",
        "baseline_commit": BASELINE_COMMIT,
        "planning_commit": PLANNING_COMMIT,
        "gap_manifest_path": str((OUTPUT_ROOT / "04_缺口清单_gap_manifest.json").relative_to(PROJECT_ROOT)),
        "remediation_tasks_path": str((OUTPUT_ROOT / "05_补跑任务清单_remediation_tasks.json").relative_to(PROJECT_ROOT)),
        "agent_goals_path": str((OUTPUT_ROOT / "06_Agent目标分工_agent_goals.json").relative_to(PROJECT_ROOT)),
        "allowed_execution": False,
        "allowed_execution_scope": "full_remediation_blocked_until_5_6_pilot_review_approved",
        "pilot_remediation_allowed": pilot_allowed,
        "supports_5_6_sol": bool(args.supports_5_6_sol),
        "supports_5_5_multi_agent": bool(args.supports_5_5),
        "alibaba_multimodal_authorized": bool(args.alibaba_multimodal_authorized),
        "alibaba_route": {
            "asr": "existing Alibaba Fun-ASR route; first-pass 10/10 succeeded",
            "multimodal": "Alibaba Qwen-VL route authorized by user for this task",
            "new_supplier_allowed": False,
        },
        "spawned_agents": [
            {"agent_id": "019f8e36-8d13-7643-b389-df586f909427", "model": "gpt-5.6-sol", "role": "review_controller"},
            {"agent_id": "019f8e36-f330-7751-a8af-2252844324b9", "model": "gpt-5.5", "role": "audio_asr_gap_review"},
            {"agent_id": "019f8e36-f414-7aa0-bc30-2bdebc155c4a", "model": "gpt-5.5", "role": "vision_comment_reply_gap_review"},
            {"agent_id": "019f8e36-f654-7773-9c76-3d50b69ae2d1", "model": "gpt-5.5", "role": "course_rules_review_queue_gap_review"},
        ],
        "approved_gaps": [gap["gap_id"] for gap in gaps],
        "approved_tasks": [task["task_id"] for task in tasks],
        "preconditions": [
            "source hashes unchanged",
            "raw_local and redacted_repo remain physically separated",
            "5.5 agents write only to disjoint remediation subdirectories",
            "5.6 final merge is serial and validates parse/security gates",
            "pilot_review_decision=approved before any 10-session full remediation",
        ],
        "blocked_lanes": [
            {
                "lane": "course_exact_alignment",
                "status": "blocked_source_limit_if_full_transcript_clean_jsonl_missing",
                "continue_other_lanes": True,
            }
        ],
    }


def render_prompt(tasks: list[dict[str, Any]], agent_goals: list[dict[str, Any]], approval: dict[str, Any]) -> str:
    return f"""# Codex 5.5 多 Agent 补齐执行单

## Goal 目标

基于 `{BASELINE_COMMIT}` 的第一轮取证结果，在不覆盖 baseline、不提交 raw、本地运行层隔离的前提下，先执行 `pilot_remediation_only`。10 场 full remediation 必须等 5.6 对 pilot 签发 `pilot_review_decision=approved` 后再启动。

## Context 上下文

- workspace: `/Volumes/WD_BLACK/澜心社直播`
- baseline evidence: `docs/直播录屏解析方案_live_recording_analysis/最新直播全量取证解析_latest_live_full_evidence_analysis/`
- gap manifest: `docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/04_缺口清单_gap_manifest.json`
- remediation tasks: `docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/05_补跑任务清单_remediation_tasks.json`
- agent goals: `docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/06_Agent目标分工_agent_goals.json`

## Constraints 边界

- 不修改源视频。
- 不覆盖第一轮 baseline 证据目录。
- 不提交 `_local_runtime/`、音频、视频、图片、API raw、signed URL、private manifest。
- 不提交用户名、手机号、微信号或其他身份信息。
- 允许调用 Alibaba Fun-ASR / Qwen-VL；不引入新供应商。
- 不把 `topic_similarity_only` 当课程准确对应。
- 不把时间相近当评论回复因果。
- 不使用 `git add .`。

## 六层需求确认

1. 目标层：先用 pilot 补齐验证 audio/comment/action/prosody/course/rule/review 路线，使 5.6 可以决定是否放行 full remediation。
2. 机制层：每个字段只能是 passed/partial/missing/invalid/blocked_source_limit/not_applicable。
3. 实现设计层：按 `execution_dependencies.json` 分 stage 并行，最终串行 merge。
4. 流程层：preflight -> stage 1 并行 -> stage 2 补齐 -> stage 3 仲裁 -> stage 4 规则 -> stage 5 终验包。
5. 判断标准层：以 `10_最终验收合同_final_acceptance_contract.json` 为硬门槛。
6. 反馈层：API/课程源/不可观察项必须 blocked 或 not_observable，不脑补。

## Agent Goals

```json
{json.dumps(agent_goals, ensure_ascii=False, indent=2)}
```

## Remediation Tasks

```json
{json.dumps(tasks, ensure_ascii=False, indent=2)}
```

## Machine Approval

```json
{json.dumps(approval, ensure_ascii=False, indent=2)}
```

## Done When

- 所有任务输出 JSON/JSONL/CSV 可解析。
- pilot 输出通过 schema/隐私/引用/质量 gates。
- 所有 pilot 缺口有 passed/partial/missing/invalid/blocked_source_limit/not_applicable 状态。
- 5.6 对 pilot 生成 `pilot_review_decision=approved` 后，才允许 full remediation。
- local HEAD、remote HEAD 完成回读一致。
"""


def render_final_review_prompt() -> str:
    return f"""# Codex 5.6-sol 最终验收执行单

## Goal

读取 5.5 补齐结果，对照 `10_最终验收合同_final_acceptance_contract.json` 做最终验收。不得把候选、local-only 或技术执行成功写成业务完成。

## Must Read

- `docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/04_缺口清单_gap_manifest.json`
- `docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/05_补跑任务清单_remediation_tasks.json`
- `docs/直播录屏解析方案_live_recording_analysis/全量解析补齐复审_full_analysis_completion_review/10_最终验收合同_final_acceptance_contract.json`
- 5.5 remediation output directory

## Validation

1. Parse all JSON/JSONL/CSV.
2. Verify no raw media/private/signed URL/PII entered Git-safe outputs.
3. Verify source hashes unchanged.
4. Verify visual coverage is no longer sparse-only.
5. Verify course matches exclude topic_similarity_only from passed counts.
6. Verify brain rules bind event evidence and are not duplicated templates.
7. Verify manual review queue is risk-ranked.

## Output Status

Use only: `passed`, `partial`, `missing`, `invalid`, `blocked_source_limit`, `not_applicable`.
"""


def render_report(
    data: dict[str, Any],
    timeline_rows: list[dict[str, Any]],
    field_rows: list[dict[str, Any]],
    invalid_rows: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    approval: dict[str, Any],
) -> str:
    status_counts = Counter(row["status"] for row in field_rows)
    total_duration = sum(float(row["duration_min"]) for row in timeline_rows)
    total_visual_windows = sum(int(row["vision_window_count"]) for row in timeline_rows)
    total_base = sum(int(row["base_scan_60s_estimated_windows"]) for row in timeline_rows)
    total_dense = sum(int(row["dense_scan_20s_estimated_windows"]) for row in timeline_rows)
    commands = [
        "pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short --branch",
        "git rev-parse HEAD && git ls-remote origin refs/heads/main",
        "python3 scripts/生成全量解析补齐复审_review_package.py --supports-5-6-sol --supports-5-5 --alibaba-multimodal-authorized",
    ]
    return f"""# 复审主报告_review_report

## 主结论

`已确认`：第一轮最新直播取证结果已形成可追溯 baseline，但未达到“全量解析完成”。本轮复审只批准进入 5.5 多 Agent `pilot_remediation_only`，当前状态为 `{approval['review_status']}`。

`部分成立`：10/10 视频、10/10 ASR、基础事件索引、稀疏视觉窗口、候选课程/规则/复核队列已经存在。

`待补全`：视觉全时间轴、评论生命周期、评论—回复因果、动作观察、语气证据、课程有效匹配、直播大脑规则和人工复核队列仍需要补齐。

## 量化覆盖

- session_count: {len(timeline_rows)}
- total_duration_min: {round(total_duration, 2)}
- baseline_visual_windows: {total_visual_windows}
- visual_coverage_status: sparse_only_invalid
- estimated_base_scan_60s_windows: {total_base}
- dense_scan_20s_reference_windows: {total_dense}
- event_rows: {len(data['events'])}
- comment_reply_candidates: {len(data['links'])}
- course_candidates: {len(data['course'])}
- provisional_rules: {len(data['rules'])}
- manual_review_rows: {len(data['review'])}

## 字段达标概览

- passed: {status_counts.get('passed', 0)}
- partial: {status_counts.get('partial', 0)}
- missing: {status_counts.get('missing', 0)}
- invalid: {status_counts.get('invalid', 0)}
- blocked_source_limit: {status_counts.get('blocked_source_limit', 0)}
- not_applicable: {status_counts.get('not_applicable', 0)}

## 关键缺口

1. ASR 成功但缺 `audio_source_type`、`speaker_role`、`asr_quality`、`host_speech_usable`，且需要把歌曲/背景/旁人/平台声音从主播话术中分离。
2. 视觉只覆盖约 2.7%-3.0%，不能证明评论、动作和课件互动全程可见。
3. 评论回复关系全部仍是 candidate 层，不能把时间接近写成因果。
4. 动作字段大部分为空；看不清应写 `not_observable`，不能留空或猜。
5. 课程候选全部为 `topic_similarity_only`，不能算有效课程对应。
6. 直播大脑规则全量模板化且缺 `event_id` 绑定。
7. 人工复核队列固定每场 80 条，未按风险和不确定性重排。

## 是否批准 5.5 补跑

- supports_5_6_sol: {approval['supports_5_6_sol']}
- supports_5_5_multi_agent: {approval['supports_5_5_multi_agent']}
- alibaba_multimodal_authorized: {approval['alibaba_multimodal_authorized']}
- allowed_execution: {approval['allowed_execution']}
- pilot_remediation_allowed: {approval['pilot_remediation_allowed']}

`已确认`：当前环境已真实启动 `gpt-5.6-sol` 复审 agent 和 `gpt-5.5` lane agent。阿里多模态路线按用户本轮授权进入 pilot 补齐执行计划；10 场 full remediation 仍需 5.6 pilot 终审批准。

## Commands

{chr(10).join('- `' + command + '`' for command in commands)}

## Result

- gap_manifest: `04_缺口清单_gap_manifest.json`
- remediation_tasks: `05_补跑任务清单_remediation_tasks.json`
- agent_goals: `06_Agent目标分工_agent_goals.json`
- machine_approval: `09_机器可读批准_machine_approval.json`
- final_acceptance_contract: `10_最终验收合同_final_acceptance_contract.json`

## Failed Items

- `blocked_source_limit`: 完整 raw course transcript source_ref 仍存在历史 `previous_pack` 指向；课程 exact alignment lane 必须在源缺失时 blocked，不影响其他 lane 继续。
- `待验证`: 5.5 pilot 补跑输出尚未进入 5.6 终验，本报告不能写“全量解析完成”。

## Git 边界

本轮只写入 `全量解析补齐复审_full_analysis_completion_review/` 和生成脚本；不修改第一轮 baseline，不提交 `_local_runtime/`、媒体、raw API 或 private manifest。
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supports-5-6-sol", action="store_true")
    parser.add_argument("--supports-5-5", action="store_true")
    parser.add_argument("--alibaba-multimodal-authorized", action="store_true")
    parser.add_argument("--current-hash-file", default="")
    args = parser.parse_args()

    if PROJECT_ROOT != Path("/Volumes/WD_BLACK/澜心社直播"):
        raise SystemExit("blocked_wrong_workspace")
    if not PLAN_ROOT.exists():
        raise SystemExit("blocked_planning_dir_missing")
    if not BASELINE_ROOT.exists():
        raise SystemExit("blocked_baseline_dir_missing")
    if not LOCAL_RUN_ROOT.exists():
        raise SystemExit("blocked_local_runtime_missing")
    if not COURSE_ROOT.exists():
        raise SystemExit("blocked_course_root_missing")

    data = load_baseline()
    current_hashes = source_hashes_current(args.current_hash_file)
    timeline_rows = build_timeline_rows(data, current_hashes)
    field_rows = build_field_matrix(data)
    invalid_rows = build_invalid_inventory(data)
    gaps = build_gaps(timeline_rows)
    tasks = build_tasks(gaps, timeline_rows)
    agent_goals = build_agent_goals(tasks)
    dependencies = build_dependencies(tasks)
    acceptance = build_acceptance_contract(timeline_rows)
    approval = build_approval(gaps, tasks, agent_goals, args)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    write_text(OUTPUT_ROOT / "00_复审主报告_review_report.md", render_report(data, timeline_rows, field_rows, invalid_rows, gaps, tasks, approval))
    write_csv(
        OUTPUT_ROOT / "01_规划字段达标矩阵_plan_compliance_matrix.csv",
        ["domain", "field_or_requirement", "planned_standard", "current_evidence", "status", "gap_id", "remediation_lane", "done_when"],
        field_rows,
    )
    write_csv(
        OUTPUT_ROOT / "02_时间轴覆盖报告_timeline_coverage_report.csv",
        [
            "session_id",
            "duration_min",
            "source_hash_status",
            "asr_status",
            "asr_sentence_count",
            "asr_coverage_status",
            "host_speech_usable_status",
            "vision_window_count",
            "vision_covered_seconds",
            "vision_coverage_pct",
            "vision_missing_pct",
            "base_scan_60s_estimated_windows",
            "dense_scan_20s_estimated_windows",
            "comment_event_count",
            "reply_candidate_count",
            "comment_reply_determined_pct",
            "action_field_coverage_pct",
            "prosody_field_coverage_pct",
            "course_effective_match_pct",
            "manual_review_count",
            "coverage_status",
            "required_remediation",
        ],
        timeline_rows,
    )
    write_csv(
        OUTPUT_ROOT / "03_错误与无效结果清单_invalid_result_inventory.csv",
        ["invalid_id", "scope", "affected_count", "invalid_type", "evidence", "severity", "required_fix"],
        invalid_rows,
    )
    write_json(OUTPUT_ROOT / "04_缺口清单_gap_manifest.json", {"version": "1.0", "created_at": datetime.now().isoformat(), "gaps": gaps})
    write_json(OUTPUT_ROOT / "05_补跑任务清单_remediation_tasks.json", {"version": "1.0", "tasks": tasks})
    write_json(OUTPUT_ROOT / "06_Agent目标分工_agent_goals.json", {"version": "1.0", "agent_goals": agent_goals})
    write_json(OUTPUT_ROOT / "07_执行依赖_execution_dependencies.json", dependencies)
    write_text(OUTPUT_ROOT / "08_5.5多Agent执行单_codex_5_5_multi_agent_prompt.md", render_prompt(tasks, agent_goals, approval))
    write_json(OUTPUT_ROOT / "09_机器可读批准_machine_approval.json", approval)
    write_json(OUTPUT_ROOT / "10_最终验收合同_final_acceptance_contract.json", acceptance)
    write_text(OUTPUT_ROOT / "11_5.6终验执行单_codex_5_6_final_review_prompt.md", render_final_review_prompt())

    print(f"wrote={OUTPUT_ROOT}")
    print(f"gaps={len(gaps)} tasks={len(tasks)} allowed_execution={approval['allowed_execution']}")


if __name__ == "__main__":
    main()
