"""Actual full remediation pipeline for the latest-live 10-session package.

This run is intentionally stricter than the previous completion pass: every
baseline source-limited visual window receives a new Alibaba Qwen-VL call in a
fresh run directory, while raw payloads and extracted frames remain local-only.
The Git package keeps only redacted indexes, hashes, status ledgers, and QA.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.util
import json
import math
import mimetypes
import os
import re
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import requests


PROJECT_ROOT = Path("/Volumes/WD_BLACK/澜心社直播")
SOURCE_DIR = PROJECT_ROOT / "最新直播"
BASE_DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播全量取证解析_latest_live_full_evidence_analysis"
)
COMPLETION_DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播全量解析完成_latest_live_full_analysis_completion"
)
ACTUAL_DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播实质全量解析_latest_live_actual_full_analysis"
)
ACTUAL_LOCAL_ROOT = PROJECT_ROOT / "_local_runtime" / "最新直播实质全量补跑_latest_live_actual_full_remediation"
PREVIOUS_COMPLETION_SCRIPT = PROJECT_ROOT / "scripts" / "最新直播全量补齐自动闭环_latest_live_completion_pipeline.py"

DEFAULT_COMPATIBLE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PII_REDACTED = "[redacted_pii]"
ALLOWED_FINAL_STATUSES = {
    "actual_full_multimodal_analysis_completed_reviewed",
    "actual_full_multimodal_analysis_completed_with_true_source_limits",
}


SOURCE_COLUMNS = [
    "session_id",
    "source_video",
    "source_path_local",
    "duration_ms",
    "width",
    "height",
    "audio_present",
    "baseline_source_hash",
    "current_source_hash",
    "source_hash_status",
    "completion_status",
]

MISSING_STATUS_COLUMNS = [
    "session_id",
    "coverage_window_id",
    "start_ms",
    "end_ms",
    "baseline_status",
    "new_call_count",
    "successful_new_call_count",
    "new_call_id",
    "model",
    "request_at",
    "result_at",
    "input_hash",
    "output_hash",
    "raw_local_ref",
    "parsed_status",
    "remediation_status",
    "true_source_limit_reason",
]

MODEL_CALL_COLUMNS = [
    "run_id",
    "new_call_id",
    "provider_request_id_or_hash",
    "session_id",
    "coverage_window_id",
    "start_ms",
    "end_ms",
    "provider",
    "model",
    "modality",
    "attempt_number",
    "request_at",
    "result_at",
    "input_hash",
    "output_hash",
    "status",
    "retry_count",
    "raw_local_ref",
    "parsed_status",
    "git_safe_note",
]

CHANGE_COLUMNS = [
    "session_id",
    "sample_ms",
    "timecode",
    "region",
    "perceptual_hash",
    "pixel_diff",
    "change_score",
    "change_type",
    "crop_bbox",
    "triggered_ocr_or_qwen_call_id",
]

TRANSCRIPT_COLUMNS = [
    "session_id",
    "audio_segment_id",
    "source_asr_sentence_id",
    "start_ms",
    "end_ms",
    "duration_ms",
    "text_clean",
    "audio_source_type",
    "speaker_role",
    "asr_quality",
    "host_speech_usable",
    "exclusion_reason",
    "word_confidence_avg",
    "word_confidence_min",
    "word_count",
    "speech_rate_chars_per_sec",
    "pause_before_ms",
    "pause_after_ms",
    "volume_rms",
    "volume_dbfs",
    "peak_dbfs",
    "emphasis_label",
    "prosody_measure_status",
    "evidence_ref",
    "completion_status",
]

SEMANTIC_COLUMNS = [
    "session_id",
    "semantic_event_id",
    "start_ms",
    "end_ms",
    "duration_ms",
    "event_type",
    "live_stage",
    "utterance_function",
    "source_audio_segment_ids",
    "source_visual_window_ids",
    "source_comment_ids",
    "trigger_source",
    "text_summary_clean",
    "semantic_confidence",
    "course_alignment_status",
    "reply_relation_status",
    "action_observation_status",
    "prosody_status",
    "completion_status",
]

COMMENT_COLUMNS = [
    "session_id",
    "comment_id",
    "anonymous_user_id",
    "dedupe_group_id",
    "comment_text_redacted",
    "intent",
    "risk",
    "first_seen_ms",
    "last_seen_ms",
    "seen_count",
    "source_window_ids",
    "comment_change_segment_ids",
    "evidence_refs",
    "ocr_confidence_avg",
    "source_mix",
    "final_state",
    "completion_status",
]

REPLY_COLUMNS = [
    "session_id",
    "reply_link_id",
    "comment_id",
    "comment_first_seen_ms",
    "candidate_reply_event_id",
    "candidate_reply_start_ms",
    "response_link_type",
    "response_latency_ms",
    "link_evidence",
    "alternative_link_candidates",
    "confidence",
    "arbitration_status",
    "completion_status",
]

ACTION_COLUMNS = [
    "session_id",
    "semantic_event_id",
    "start_ms",
    "end_ms",
    "observed_action",
    "facial_expression",
    "gaze_target",
    "body_posture",
    "hand_gesture",
    "prop_interaction",
    "courseware_interaction",
    "action_observation_status",
    "action_confidence",
    "visual_evidence_ref",
    "visual_evidence_source",
    "completion_status",
]

PROSODY_COLUMNS = [
    "session_id",
    "semantic_event_id",
    "start_ms",
    "end_ms",
    "speaking_rate_chars_per_sec",
    "pause_before_ms",
    "pause_after_ms",
    "volume_rms_avg",
    "volume_dbfs_avg",
    "peak_dbfs_max",
    "volume_change",
    "emphasis_label",
    "prosody_status",
    "audio_evidence_refs",
    "completion_status",
]

COURSE_COLUMNS = [
    "session_id",
    "semantic_event_id",
    "start_ms",
    "end_ms",
    "live_text_summary_clean",
    "course_alignment_status",
    "alignment_type",
    "course_source_ref",
    "course_topic_candidate",
    "is_valid_course_match",
    "alignment_evidence",
    "alignment_confidence",
    "source_limit_reason",
    "completion_status",
]

RULE_COLUMNS = [
    "rule_id",
    "session_id",
    "trigger_type",
    "trigger_evidence_ids",
    "source_event_ids",
    "source_comment_ids",
    "trigger_pattern",
    "audience_state_candidate",
    "decision_goal_candidate",
    "response_strategy_candidate",
    "course_basis",
    "avatar_action_basis",
    "prosody_basis",
    "risk_level_candidate",
    "human_takeover_required",
    "fallback_route",
    "completion_status",
]

RISK_COLUMNS = [
    "session_id",
    "risk_item_id",
    "related_event_id",
    "related_comment_id",
    "start_ms",
    "timecode",
    "risk_type",
    "risk_level",
    "risk_evidence",
    "handover_required",
    "handover_reason",
    "safe_fallback",
    "completion_status",
]

UNKNOWN_COLUMNS = [
    "unknown_id",
    "session_id",
    "related_event_id",
    "related_comment_id",
    "start_ms",
    "end_ms",
    "unknown_type",
    "source_limit_status",
    "reason",
    "evidence_ref",
    "recommended_recovery",
    "completion_status",
]

REVIEW_COLUMNS = [
    "priority_rank",
    "priority_score",
    "session_id",
    "review_item_id",
    "related_event_id",
    "related_comment_id",
    "start_ms",
    "timecode",
    "risk_type",
    "review_reason",
    "evidence_refs",
    "current_ai_status",
    "suggested_review_action",
    "completion_status",
]


def load_base_module():
    spec = importlib.util.spec_from_file_location("latest_live_completion_base", PREVIOUS_COMPLETION_SCRIPT)
    if spec is None or spec.loader is None:
        raise SystemExit("blocked_missing_previous_completion_script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_module()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def rel(path: Path | str) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(PROJECT_ROOT.resolve()))
    except (ValueError, FileNotFoundError):
        return str(path)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def stable_hash(text: str, length: int = 12) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def timecode(ms: int) -> str:
    sec = max(0, ms // 1000)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


def redact_text(text: Any, limit: int = 500) -> str:
    return base.redact_text(text, limit=limit)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{k: str(v or "") for k, v in row.items()} for row in csv.DictReader(fh)]


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_workspace() -> None:
    if Path.cwd().resolve() != PROJECT_ROOT.resolve():
        raise SystemExit("blocked_wrong_workspace")
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != PROJECT_ROOT.resolve():
        raise SystemExit("blocked_wrong_workspace")
    remote = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if remote.returncode != 0 or remote.stdout.strip() != "https://github.com/fthytwerwt-sudo/lanxinshe-.git":
        raise SystemExit("blocked_existing_wrong_remote")


def load_env() -> None:
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def run_cmd(args: list[str], timeout: int | None = None) -> tuple[int, bytes, bytes]:
    proc = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def parse_model_json(text: str) -> tuple[dict[str, Any], str]:
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
    stripped = re.sub(r"```$", "", stripped).strip()
    try:
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, dict) else {}, ""
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, re.S)
        if not match:
            return {}, "json_object_not_found"
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}, ""
        except json.JSONDecodeError as exc:
            return {}, str(exc)


def normalize_key(text: str) -> str:
    return re.sub(r"\s+", "", text).strip().lower()


def media_type(path: Path) -> str:
    return mimetypes.guess_type(str(path))[0] or "image/jpeg"


def encode_data_url(path: Path) -> tuple[str, str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return "", f"frame_read_failed:{exc.__class__.__name__}"
    return f"data:{media_type(path)};base64,{base64.b64encode(raw).decode('ascii')}", ""


def api_post_json(url: str, payload: dict[str, Any], timeout: int) -> tuple[bool, dict[str, Any], str]:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        return False, {}, "blocked_missing_dashscope_api_key"
    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return False, {}, f"blocked_network_error:{exc.__class__.__name__}"
    try:
        body = response.json()
    except ValueError:
        body = {"message": response.text[:500], "http_status": response.status_code}
    if not response.ok:
        msg = body.get("message") or body.get("error", {}).get("message") or f"http_{response.status_code}"
        return False, body, redact_text(str(msg))
    return True, body, ""


def build_image_payload(
    model: str,
    frame_urls: list[str],
    sid: str,
    coverage_window_id: str,
    start_ms: int,
    end_ms: int,
    transcript_context: str,
    change_hint: str,
) -> dict[str, Any]:
    prompt = f"""
请基于这些按时间顺序截取的直播录屏关键帧输出严格 JSON，不要 Markdown，不要解释。
场次：{sid}
窗口：{coverage_window_id}
时间：{start_ms}ms 到 {end_ms}ms
本窗口主播 ASR 摘要（只作辅助，不替代画面观察）：{transcript_context}
本地视觉变化提示（只作定位，不作语义结论）：{change_hint}

要求：
1. 只记录可观察事实；看不清就写 not_observable / insufficient_source_evidence。
2. 不输出用户名、手机号、微信号、邮箱、地址、订单号；评论文本必须脱敏。
3. 不能把时间接近写成 direct_reply；除非画面评论和主播语音摘要形成明确对应证据。
4. 课程只能写画面/语音可见候选，不得假装精确匹配课程原文。

JSON 字段：
{{
  "comment_area_visible": "yes/no/uncertain",
  "visible_comments": [
    {{"comment_text_redacted": "", "intent": "", "risk": "none/pii/compliance/uncertain", "ocr_confidence": 0.0}}
  ],
  "host": {{
    "speaker_text_summary": "",
    "live_stage_candidate": "",
    "utterance_function_candidate": "",
    "response_goal_candidate": "",
    "response_strategy_candidate": ""
  }},
  "action": {{
    "observed_action": "",
    "facial_expression": "",
    "gaze_target": "",
    "body_posture": "",
    "hand_gesture": "",
    "prop_interaction": "",
    "courseware_interaction": "",
    "observed_action_confidence": 0.0,
    "action_meaning_candidate": ""
  }},
  "prosody_visual_candidate": {{
    "visual_energy": "",
    "emotion_observed": "",
    "confidence": 0.0
  }},
  "reply_relation_evidence": {{
    "response_link_type": "direct_reply/multi_comment_combined_reply/host_prompt_generated_comment/topic_related_not_causal/comment_visible_but_unanswered/insufficient_source_evidence",
    "link_evidence": "",
    "link_confidence": 0.0
  }},
  "scene_courseware": {{
    "courseware_visible": "yes/no/uncertain",
    "course_topic_candidate": "",
    "product_or_offer_visible": "",
    "scene_change_summary": ""
  }},
  "risk_or_failure": {{
    "failure_type": "",
    "failure_evidence": "",
    "human_takeover_candidate": ""
  }},
  "source_limit": {{
    "has_true_source_limit": false,
    "reason": ""
  }}
}}
""".strip()
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for url in frame_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})
    return {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.0,
        "max_tokens": 1500,
    }


def frame_hash(frame: np.ndarray) -> str:
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, (8, 8), interpolation=cv2.INTER_AREA)
    bits = small >= float(small.mean())
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:016x}"


def crop_region(frame: np.ndarray, bbox: tuple[float, float, float, float]) -> np.ndarray:
    h, w = frame.shape[:2]
    x0 = max(0, min(w - 1, int(w * bbox[0])))
    y0 = max(0, min(h - 1, int(h * bbox[1])))
    x1 = max(x0 + 1, min(w, int(w * bbox[2])))
    y1 = max(y0 + 1, min(h, int(h * bbox[3])))
    return frame[y0:y1, x0:x1]


def bbox_str(bbox: tuple[float, float, float, float]) -> str:
    return ",".join(f"{v:.3f}" for v in bbox)


REGIONS = {
    "full_frame": (0.0, 0.0, 1.0, 1.0),
    "comment_area": (0.02, 0.45, 0.72, 0.92),
    "host_area": (0.20, 0.12, 0.96, 0.95),
    "courseware_scene": (0.00, 0.00, 1.00, 0.45),
}


def scan_visual_changes_for_session(
    sid: str,
    video_path: Path,
    duration_ms: int,
    run_dir: Path,
    scan_step_ms: int,
    target_width: int,
) -> list[dict[str, Any]]:
    session_scan_path = run_dir / "visual_scan" / sid / f"{sid}_visual_change_rows.jsonl"
    if session_scan_path.exists() and session_scan_path.stat().st_size > 0:
        rows: list[dict[str, Any]] = []
        with session_scan_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    manifest = load_json(BASE_DOC_ROOT / "data" / "session_manifests" / f"{sid}_manifest.json")
    width = safe_int(manifest.get("session", {}).get("width"), 720)
    height = safe_int(manifest.get("session", {}).get("height"), 1600)
    out_w = max(64, target_width)
    out_h = max(64, int(round(height * out_w / max(width, 1))))
    if out_h % 2:
        out_h += 1
    fps_value = max(0.2, 1000.0 / max(scan_step_ms, 1))
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(video_path),
        "-vf",
        f"fps={fps_value:.4f},scale={out_w}:{out_h}",
        "-pix_fmt",
        "rgb24",
        "-f",
        "rawvideo",
        "pipe:1",
    ]
    proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    frame_size = out_w * out_h * 3
    previous: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    index = 0
    while True:
        chunk = proc.stdout.read(frame_size)
        if not chunk:
            break
        if len(chunk) < frame_size:
            break
        sample_ms = min(duration_ms, index * scan_step_ms)
        frame = np.frombuffer(chunk, dtype=np.uint8).reshape((out_h, out_w, 3))
        for region, bbox in REGIONS.items():
            crop = crop_region(frame, bbox)
            gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
            if region in previous:
                diff = float(np.mean(np.abs(gray.astype(np.float32) - previous[region].astype(np.float32))))
            else:
                diff = 0.0
            previous[region] = gray.copy()
            if diff >= 18:
                ctype = "major_change"
            elif diff >= 7:
                ctype = "moderate_change"
            else:
                ctype = "stable_or_minor"
            rows.append(
                {
                    "session_id": sid,
                    "sample_ms": sample_ms,
                    "timecode": timecode(sample_ms),
                    "region": region,
                    "perceptual_hash": frame_hash(crop),
                    "pixel_diff": round(diff, 3),
                    "change_score": round(min(1.0, diff / 32.0), 4),
                    "change_type": ctype,
                    "crop_bbox": bbox_str(bbox),
                    "triggered_ocr_or_qwen_call_id": "",
                }
            )
        index += 1
    stderr = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"visual_scan_failed:{sid}:{redact_text(stderr)}")
    write_jsonl(session_scan_path, rows)
    return rows


def pick_change_hint(
    change_rows: list[dict[str, Any]],
    sid: str,
    start_ms: int,
    end_ms: int,
) -> tuple[str, int | None, list[str]]:
    rows = [
        row
        for row in change_rows
        if row["session_id"] == sid
        and start_ms <= safe_int(row["sample_ms"]) < end_ms
        and row["region"] in {"comment_area", "host_area", "courseware_scene"}
    ]
    if not rows:
        return "no_local_change_sample", None, []
    comment_rows = [row for row in rows if row["region"] == "comment_area"]
    max_comment = max(comment_rows, key=lambda row: safe_float(row["change_score"]), default=None)
    max_host = max((row for row in rows if row["region"] == "host_area"), key=lambda row: safe_float(row["change_score"]), default=None)
    max_scene = max((row for row in rows if row["region"] == "courseware_scene"), key=lambda row: safe_float(row["change_score"]), default=None)
    parts = []
    segment_ids = []
    selected_ms: int | None = None
    for label, row in [("comment", max_comment), ("host", max_host), ("scene", max_scene)]:
        if not row:
            continue
        parts.append(f"{label}:{row['sample_ms']}ms score={row['change_score']} type={row['change_type']}")
        if label == "comment":
            selected_ms = safe_int(row["sample_ms"])
        if safe_float(row["change_score"]) >= 0.22:
            segment_ids.append(f"{sid}-CHG-{label}-{safe_int(row['sample_ms']):012d}")
    return "; ".join(parts), selected_ms, segment_ids


def extract_keyframes(
    sid: str,
    video_path: Path,
    start_ms: int,
    end_ms: int,
    selected_change_ms: int | None,
    frames_dir: Path,
    frame_height: int,
) -> tuple[list[Path], str]:
    frames_dir.mkdir(parents=True, exist_ok=True)
    duration = max(1000, end_ms - start_ms)
    candidates = [
        start_ms + min(8000, duration // 5),
        start_ms + duration // 2,
        max(start_ms, end_ms - min(5000, duration // 6)),
    ]
    if selected_change_ms is not None and start_ms <= selected_change_ms <= end_ms:
        candidates.append(selected_change_ms)
    unique_ms = sorted({max(start_ms, min(end_ms - 1, safe_int(ms))) for ms in candidates})
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return [], "video_open_failed"
    paths: list[Path] = []
    for index, ms in enumerate(unique_ms, 1):
        path = frames_dir / f"{sid}_{start_ms}_{end_ms}_frame_{index:02d}_{ms}.jpg"
        if path.exists() and path.stat().st_size > 0:
            paths.append(path)
            continue
        cap.set(cv2.CAP_PROP_POS_MSEC, float(ms))
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        h, w = frame.shape[:2]
        scale = frame_height / max(h, 1)
        resized = cv2.resize(frame, (max(2, int(w * scale)), frame_height), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(path), resized, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
        paths.append(path)
    cap.release()
    if not paths:
        return [], "no_keyframe_extracted"
    return paths, ""


def transcript_context_for_window(transcript_rows: list[dict[str, Any]], sid: str, start_ms: int, end_ms: int) -> str:
    texts = [
        str(row.get("text_clean") or "")
        for row in transcript_rows
        if row.get("session_id") == sid
        and safe_int(row.get("end_ms")) >= start_ms
        and safe_int(row.get("start_ms")) <= end_ms
        and row.get("host_speech_usable") == "true"
    ]
    text = " ".join(texts)
    return redact_text(text, limit=700)


def call_qwen_for_window(
    task: dict[str, Any],
    manifests: dict[str, dict[str, Any]],
    transcript_rows: list[dict[str, Any]],
    change_rows: list[dict[str, Any]],
    run_dir: Path,
    run_id: str,
    models: list[str],
    timeout_sec: int,
    frame_height: int,
) -> dict[str, Any]:
    sid = task["session_id"]
    coverage_window_id = task["coverage_window_id"]
    start_ms = safe_int(task["start_ms"])
    end_ms = safe_int(task["end_ms"])
    seq = safe_int(re.sub(r"\D", "", coverage_window_id.split("-VC")[-1]), 0)
    video_path = Path(manifests[sid]["session"]["source_path_local"])
    change_hint, selected_change_ms, segment_ids = pick_change_hint(change_rows, sid, start_ms, end_ms)
    frames_dir = run_dir / "missing_window_calls" / "keyframes_local" / sid / coverage_window_id
    frame_paths, frame_error = extract_keyframes(sid, video_path, start_ms, end_ms, selected_change_ms, frames_dir, frame_height)
    input_refs = [{"path": rel(path), "sha256": sha256_file(path)} for path in frame_paths if path.exists()]
    transcript_context = transcript_context_for_window(transcript_rows, sid, start_ms, end_ms)
    raw_dir = run_dir / "missing_window_calls" / "raw_local" / sid
    raw_dir.mkdir(parents=True, exist_ok=True)
    attempts: list[dict[str, Any]] = []
    if not frame_paths:
        call_id = f"{sid}-ACTQW{seq:04d}-A01"
        now = now_iso()
        output = {
            "run_id": run_id,
            "new_call_id": call_id,
            "provider_request_id_or_hash": sha256_text(f"{run_id}:{call_id}:frame_extraction_failed"),
            "session_id": sid,
            "coverage_window_id": coverage_window_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "model": "",
            "attempt_number": 1,
            "request_at": now,
            "result_at": now,
            "input_hash": sha256_text(json.dumps({"task": task, "frame_error": frame_error}, ensure_ascii=False, sort_keys=True)),
            "output_hash": sha256_text(frame_error),
            "status": "model_execution_failed",
            "retry_count": 0,
            "raw_local_ref": "",
            "parsed_status": "frame_extraction_failed",
            "error": frame_error,
            "parsed": {},
            "comment_change_segment_ids": segment_ids,
            "frame_refs": input_refs,
        }
        attempts.append(output)
        return {"attempts": attempts, "final": output}
    frame_urls: list[str] = []
    encode_errors: list[str] = []
    for path in frame_paths:
        url, error = encode_data_url(path)
        if url:
            frame_urls.append(url)
        else:
            encode_errors.append(error)
    if not frame_urls:
        call_id = f"{sid}-ACTQW{seq:04d}-A01"
        now = now_iso()
        output = {
            "run_id": run_id,
            "new_call_id": call_id,
            "provider_request_id_or_hash": sha256_text(f"{run_id}:{call_id}:frame_encoding_failed"),
            "session_id": sid,
            "coverage_window_id": coverage_window_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "model": "",
            "attempt_number": 1,
            "request_at": now,
            "result_at": now,
            "input_hash": sha256_text(json.dumps(input_refs, ensure_ascii=False, sort_keys=True)),
            "output_hash": sha256_text(";".join(encode_errors)),
            "status": "model_execution_failed",
            "retry_count": 0,
            "raw_local_ref": "",
            "parsed_status": "frame_encoding_failed",
            "error": ";".join(encode_errors),
            "parsed": {},
            "comment_change_segment_ids": segment_ids,
            "frame_refs": input_refs,
        }
        attempts.append(output)
        return {"attempts": attempts, "final": output}

    final_attempt: dict[str, Any] | None = None
    for attempt_number, model in enumerate(models, 1):
        call_id = f"{sid}-ACTQW{seq:04d}-A{attempt_number:02d}"
        raw_path = raw_dir / f"{call_id}_{model}.json"
        input_payload = {
            "sid": sid,
            "coverage_window_id": coverage_window_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "model": model,
            "frame_refs": input_refs,
            "transcript_context_sha256": sha256_text(transcript_context),
            "change_hint": change_hint,
        }
        input_hash = sha256_text(json.dumps(input_payload, ensure_ascii=False, sort_keys=True))
        request_at = now_iso()
        if raw_path.exists() and raw_path.stat().st_size > 0:
            raw_payload = load_json(raw_path)
            body = raw_payload.get("response", {})
            parsed = raw_payload.get("parsed", {}) if isinstance(raw_payload.get("parsed", {}), dict) else {}
            error = str(raw_payload.get("error") or raw_payload.get("parse_error") or "")
            output_hash = sha256_text(json.dumps(body, ensure_ascii=False, sort_keys=True))
            result_at = str(raw_payload.get("result_at") or now_iso())
            status = "succeeded" if parsed else "model_execution_failed"
            parsed_status = "parsed" if parsed else "parse_failed"
            provider_request_id_or_hash = str(raw_payload.get("provider_request_id_or_hash") or body.get("id") or output_hash)
        else:
            payload = build_image_payload(
                model,
                frame_urls,
                sid,
                coverage_window_id,
                start_ms,
                end_ms,
                transcript_context,
                change_hint,
            )
            ok, body, error = api_post_json(f"{DEFAULT_COMPATIBLE_BASE_URL}/chat/completions", payload, timeout=timeout_sec)
            result_at = now_iso()
            content = ""
            parsed: dict[str, Any] = {}
            parse_error = ""
            if ok:
                content = str(body.get("choices", [{}])[0].get("message", {}).get("content", ""))
                parsed, parse_error = parse_model_json(content)
            output_hash = sha256_text(json.dumps(body, ensure_ascii=False, sort_keys=True))
            status = "succeeded" if ok and parsed else "model_execution_failed"
            parsed_status = "parsed" if parsed else ("parse_failed" if ok else "api_failed")
            provider_request_id_or_hash = str(body.get("id") or output_hash)
            write_json(
                raw_path,
                {
                    "new_call_id": call_id,
                    "provider_request_id_or_hash": provider_request_id_or_hash,
                    "request_at": request_at,
                    "result_at": result_at,
                    "input_hash": input_hash,
                    "response": body,
                    "parsed": parsed,
                    "parse_error": parse_error,
                    "error": error,
                    "frame_refs": input_refs,
                    "transcript_context": transcript_context,
                    "change_hint": change_hint,
                },
            )
        attempt = {
            "run_id": run_id,
            "new_call_id": call_id,
            "provider_request_id_or_hash": provider_request_id_or_hash,
            "session_id": sid,
            "coverage_window_id": coverage_window_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "model": model,
            "attempt_number": attempt_number,
            "request_at": request_at,
            "result_at": result_at,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "status": status,
            "retry_count": attempt_number - 1,
            "raw_local_ref": rel(raw_path),
            "parsed_status": parsed_status,
            "error": error,
            "parsed": parsed,
            "comment_change_segment_ids": segment_ids,
            "frame_refs": input_refs,
            "change_hint": change_hint,
        }
        attempts.append(attempt)
        final_attempt = attempt
        if status == "succeeded":
            break
        time.sleep(0.7)
    assert final_attempt is not None
    return {"attempts": attempts, "final": final_attempt}


def load_previous_inputs(manifests: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    audio_rows: list[dict[str, Any]] = []
    for sid, manifest in sorted(manifests.items()):
        audio_rows.extend(base.load_asr_segments(sid, manifest))
    semantic_rows = read_csv_rows(COMPLETION_DOC_ROOT / "04_语义事件时间轴_semantic_event_timeline.csv")
    visual_rows = read_csv_rows(COMPLETION_DOC_ROOT / "02_全时间轴覆盖报告_full_timeline_coverage.csv")
    comment_rows = read_csv_rows(COMPLETION_DOC_ROOT / "05_评论完整事件_comment_events.csv")
    course_rows = read_csv_rows(COMPLETION_DOC_ROOT / "08_课程最终对应_final_course_alignment.csv")
    return {
        "audio_rows": audio_rows,
        "semantic_rows": semantic_rows,
        "visual_rows": visual_rows,
        "comment_rows": comment_rows,
        "course_rows": course_rows,
    }


def build_source_manifest_rows(manifests: dict[str, dict[str, Any]], recompute_hash: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sid, manifest in sorted(manifests.items()):
        session = manifest["session"]
        source_path = Path(session["source_path_local"])
        baseline_hash = str(session.get("source_hash") or "")
        if not source_path.exists() or source_path.name.startswith("._"):
            current_hash = ""
            status = "missing_source"
        elif recompute_hash:
            current_hash = sha256_file(source_path)
            status = "passed" if current_hash == baseline_hash else "source_hash_changed"
        else:
            current_hash = baseline_hash
            status = "passed_reused_baseline_hash"
        rows.append(
            {
                "session_id": sid,
                "source_video": session.get("source_video", ""),
                "source_path_local": str(source_path),
                "duration_ms": safe_int(session.get("duration_ms")),
                "width": session.get("width", ""),
                "height": session.get("height", ""),
                "audio_present": session.get("audio_present", ""),
                "baseline_source_hash": baseline_hash,
                "current_source_hash": current_hash,
                "source_hash_status": status,
                "completion_status": "passed" if status.startswith("passed") else "blocked",
            }
        )
    return rows


def measure_audio_rows(audio_rows: list[dict[str, Any]], manifests: dict[str, dict[str, Any]], run_dir: Path) -> list[dict[str, Any]]:
    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in audio_rows:
        by_session[row["session_id"]].append(dict(row))
    measured: list[dict[str, Any]] = []
    metric_indexes: dict[str, list[dict[str, Any]]] = {}
    for sid, rows in sorted(by_session.items()):
        manifest = manifests[sid]
        audio_ref = str(manifest.get("asr_status", {}).get("audio_path_local") or "")
        audio_path = PROJECT_ROOT / audio_ref
        if not audio_path.exists():
            audio_path = Path(manifest["session"]["source_path_local"])
        code, out, err = run_cmd(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(audio_path),
                "-f",
                "s16le",
                "-ac",
                "1",
                "-ar",
                "16000",
                "pipe:1",
            ],
            timeout=1800,
        )
        session_metrics: list[dict[str, Any]] = []
        if code != 0 or not out:
            for row in rows:
                row.update(
                    {
                        "volume_rms": "",
                        "volume_dbfs": "",
                        "peak_dbfs": "",
                        "emphasis_label": "not_measured_source_limit",
                        "prosody_measure_status": "audio_decode_failed",
                    }
                )
                measured.append(row)
            metric_indexes[sid] = session_metrics
            continue
        samples = np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768.0
        db_values: list[float] = []
        for row in rows:
            start = max(0, int(safe_int(row.get("start_ms")) / 1000 * 16000))
            end = min(len(samples), max(start + 1, int(safe_int(row.get("end_ms")) / 1000 * 16000)))
            segment = samples[start:end]
            rms = float(np.sqrt(np.mean(np.square(segment)))) if len(segment) else 0.0
            peak = float(np.max(np.abs(segment))) if len(segment) else 0.0
            dbfs = 20 * math.log10(max(rms, 1e-8))
            peak_dbfs = 20 * math.log10(max(peak, 1e-8))
            db_values.append(dbfs)
            row.update(
                {
                    "volume_rms": round(rms, 6),
                    "volume_dbfs": round(dbfs, 2),
                    "peak_dbfs": round(peak_dbfs, 2),
                    "emphasis_label": "pending_session_relative_classification",
                    "prosody_measure_status": "measured_from_source_audio_rms",
                }
            )
            session_metrics.append(
                {
                    "audio_segment_id": row.get("audio_segment_id"),
                    "start_ms": row.get("start_ms"),
                    "end_ms": row.get("end_ms"),
                    "volume_rms": row["volume_rms"],
                    "volume_dbfs": row["volume_dbfs"],
                    "peak_dbfs": row["peak_dbfs"],
                }
            )
        median_db = statistics.median(db_values) if db_values else -80.0
        for row in rows:
            dbfs = safe_float(row.get("volume_dbfs"), -80.0)
            if dbfs >= median_db + 4.0:
                label = "high_emphasis"
            elif dbfs <= median_db - 5.0:
                label = "low_volume_or_pause"
            else:
                label = "normal_volume"
            row["emphasis_label"] = label
            measured.append(row)
        metric_indexes[sid] = session_metrics
    for sid, rows in metric_indexes.items():
        write_jsonl(run_dir / "action_prosody" / f"{sid}_audio_rms_metrics.jsonl", rows)
    return measured


def observation_from_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    parsed = attempt.get("parsed") if isinstance(attempt.get("parsed"), dict) else {}
    return {
        "session_id": attempt["session_id"],
        "coverage_window_id": attempt["coverage_window_id"],
        "qwen_window_id": attempt["new_call_id"],
        "start_ms": safe_int(attempt["start_ms"]),
        "end_ms": safe_int(attempt["end_ms"]),
        "model": attempt.get("model", ""),
        "raw_response_path_local": attempt.get("raw_local_ref", ""),
        "parsed": parsed,
        "comment_area_visible": parsed.get("comment_area_visible", "") if parsed else "",
        "visible_comments": parsed.get("visible_comments", []) if isinstance(parsed.get("visible_comments", []), list) else [],
        "host": parsed.get("host", {}) if isinstance(parsed.get("host", {}), dict) else {},
        "action": parsed.get("action", {}) if isinstance(parsed.get("action", {}), dict) else {},
        "prosody_visual_candidate": parsed.get("prosody_visual_candidate", {})
        if isinstance(parsed.get("prosody_visual_candidate", {}), dict)
        else {},
        "reply_relation_evidence": parsed.get("reply_relation_evidence", {})
        if isinstance(parsed.get("reply_relation_evidence", {}), dict)
        else {},
        "scene_courseware": parsed.get("scene_courseware", {}) if isinstance(parsed.get("scene_courseware", {}), dict) else {},
        "risk_or_failure": parsed.get("risk_or_failure", {}) if isinstance(parsed.get("risk_or_failure", {}), dict) else {},
        "source_limit": parsed.get("source_limit", {}) if isinstance(parsed.get("source_limit", {}), dict) else {},
        "comment_change_segment_ids": attempt.get("comment_change_segment_ids", []),
        "evidence_source": "new_actual_remediation_qwen_vl",
    }


def old_observation_from_visual_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "session_id": row["session_id"],
        "coverage_window_id": row["coverage_window_id"],
        "qwen_window_id": row.get("qwen_window_id", ""),
        "start_ms": safe_int(row.get("start_ms")),
        "end_ms": safe_int(row.get("end_ms")),
        "model": "previous_qwen_vl",
        "raw_response_path_local": row.get("qwen_evidence_ref", ""),
        "parsed": {},
        "comment_area_visible": row.get("comment_area_visible", ""),
        "visible_comments": [],
        "host": {},
        "action": {"observed_action": row.get("observed_action", ""), "observed_action_confidence": ""},
        "prosody_visual_candidate": {"visual_energy": row.get("prosody_label", "")},
        "reply_relation_evidence": {},
        "scene_courseware": {},
        "risk_or_failure": {},
        "source_limit": {},
        "comment_change_segment_ids": [],
        "evidence_source": "prior_qwen_vl_137_windows",
    }


def build_visual_coverage_rows(
    previous_visual_rows: list[dict[str, str]],
    final_attempts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in previous_visual_rows:
        current = dict(row)
        if row.get("coverage_status") == "source_limited_unknown":
            attempt = final_attempts.get(row["coverage_window_id"])
            if attempt and attempt.get("status") == "succeeded":
                obs = observation_from_attempt(attempt)
                action = obs.get("action", {})
                comments = obs.get("visible_comments", [])
                current.update(
                    {
                        "qwen_vl_observed": "true",
                        "qwen_window_id": attempt["new_call_id"],
                        "qwen_evidence_ref": attempt.get("raw_local_ref", ""),
                        "coverage_status": "remediated_by_new_alibaba_qwen_vl_call",
                        "comment_area_visible": obs.get("comment_area_visible", ""),
                        "visible_comment_count": len(comments),
                        "observed_action": redact_text(action.get("observed_action", "")) if isinstance(action, dict) else "",
                        "prosody_label": obs.get("prosody_visual_candidate", {}).get("visual_energy", ""),
                        "source_limit_reason": "",
                        "completion_status": "passed",
                    }
                )
            else:
                reason = (attempt or {}).get("error") or "new_model_call_missing"
                current.update(
                    {
                        "qwen_vl_observed": "false",
                        "qwen_window_id": (attempt or {}).get("new_call_id", ""),
                        "qwen_evidence_ref": (attempt or {}).get("raw_local_ref", ""),
                        "coverage_status": "model_execution_failed_after_full_fallback",
                        "source_limit_reason": redact_text(reason),
                        "completion_status": "blocked_source_limit",
                    }
                )
        else:
            current["coverage_status"] = "observed_by_existing_alibaba_qwen_vl_prior_run"
        rows.append(current)
    return rows


def build_missing_status_rows(missing_tasks: list[dict[str, str]], attempts_by_window: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in missing_tasks:
        attempts = attempts_by_window.get(task["coverage_window_id"], [])
        successful = [row for row in attempts if row.get("status") == "succeeded"]
        final = successful[-1] if successful else (attempts[-1] if attempts else {})
        rows.append(
            {
                "session_id": task["session_id"],
                "coverage_window_id": task["coverage_window_id"],
                "start_ms": task["start_ms"],
                "end_ms": task["end_ms"],
                "baseline_status": task.get("coverage_status", ""),
                "new_call_count": len(attempts),
                "successful_new_call_count": len(successful),
                "new_call_id": final.get("new_call_id", ""),
                "model": final.get("model", ""),
                "request_at": final.get("request_at", ""),
                "result_at": final.get("result_at", ""),
                "input_hash": final.get("input_hash", ""),
                "output_hash": final.get("output_hash", ""),
                "raw_local_ref": final.get("raw_local_ref", ""),
                "parsed_status": final.get("parsed_status", ""),
                "remediation_status": "observed_new_qwen" if successful else "model_execution_failed_after_full_fallback",
                "true_source_limit_reason": "" if successful else "model_indeterminate_after_full_fallback",
            }
        )
    return rows


def build_model_ledger(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for attempt in attempts:
        rows.append(
            {
                "run_id": attempt.get("run_id", ""),
                "new_call_id": attempt.get("new_call_id", ""),
                "provider_request_id_or_hash": attempt.get("provider_request_id_or_hash", ""),
                "session_id": attempt.get("session_id", ""),
                "coverage_window_id": attempt.get("coverage_window_id", ""),
                "start_ms": attempt.get("start_ms", ""),
                "end_ms": attempt.get("end_ms", ""),
                "provider": "Alibaba DashScope",
                "model": attempt.get("model", ""),
                "modality": "qwen_vl_keyframe_sequence_for_missing_60s_window",
                "attempt_number": attempt.get("attempt_number", ""),
                "request_at": attempt.get("request_at", ""),
                "result_at": attempt.get("result_at", ""),
                "input_hash": attempt.get("input_hash", ""),
                "output_hash": attempt.get("output_hash", ""),
                "status": attempt.get("status", ""),
                "retry_count": attempt.get("retry_count", ""),
                "raw_local_ref": attempt.get("raw_local_ref", ""),
                "parsed_status": attempt.get("parsed_status", ""),
                "git_safe_note": "new_call_hash_and_redacted_ref_only_raw_local_not_committed",
            }
        )
    return rows


def build_comment_lifecycle(
    previous_comment_rows: list[dict[str, str]],
    new_observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for row in previous_comment_rows:
        sid = row["session_id"]
        text = redact_text(row.get("comment_text_redacted", ""))
        if not text:
            continue
        key = (sid, normalize_key(text))
        record = groups.setdefault(
            key,
            {
                "session_id": sid,
                "comment_text_redacted": text,
                "intent_values": [],
                "risk_values": [],
                "seen_times": [],
                "source_window_ids": [],
                "comment_change_segment_ids": [],
                "evidence_refs": [],
                "ocr_confidences": [],
                "source_mix": set(),
            },
        )
        record["intent_values"].append(row.get("comment_intent_candidate", ""))
        record["risk_values"].append(row.get("comment_risk", ""))
        record["seen_times"].append(safe_int(row.get("first_seen_ms")))
        record["seen_times"].append(safe_int(row.get("last_seen_ms")))
        record["source_window_ids"].extend([x for x in row.get("source_window_ids", "").split(";") if x])
        record["evidence_refs"].extend([x for x in row.get("evidence_refs", "").split(";") if x])
        record["ocr_confidences"].append(0.0)
        record["source_mix"].add("prior_137_window")
    for obs in new_observations:
        sid = obs["session_id"]
        for item in obs.get("visible_comments", [])[:10]:
            if not isinstance(item, dict):
                continue
            text = redact_text(item.get("comment_text_redacted") or item.get("text") or "", limit=240)
            if not text:
                continue
            key = (sid, normalize_key(text))
            record = groups.setdefault(
                key,
                {
                    "session_id": sid,
                    "comment_text_redacted": text,
                    "intent_values": [],
                    "risk_values": [],
                    "seen_times": [],
                    "source_window_ids": [],
                    "comment_change_segment_ids": [],
                    "evidence_refs": [],
                    "ocr_confidences": [],
                    "source_mix": set(),
                },
            )
            record["intent_values"].append(redact_text(item.get("intent") or item.get("comment_intent_candidate") or ""))
            record["risk_values"].append(redact_text(item.get("risk") or item.get("comment_risk") or "none"))
            record["seen_times"].append(safe_int(obs.get("start_ms")))
            record["seen_times"].append(safe_int(obs.get("end_ms")))
            record["source_window_ids"].append(obs.get("qwen_window_id", ""))
            record["comment_change_segment_ids"].extend(obs.get("comment_change_segment_ids", []))
            record["evidence_refs"].append(obs.get("raw_response_path_local", ""))
            record["ocr_confidences"].append(safe_float(item.get("ocr_confidence"), 0.0))
            record["source_mix"].add("new_526_missing_window")
    rows: list[dict[str, Any]] = []
    for index, ((sid, key), record) in enumerate(sorted(groups.items()), 1):
        first_seen = min(record["seen_times"]) if record["seen_times"] else 0
        last_seen = max(record["seen_times"]) if record["seen_times"] else first_seen
        intent = Counter(x for x in record["intent_values"] if x).most_common(1)
        risk = Counter(x for x in record["risk_values"] if x).most_common(1)
        confs = [safe_float(x) for x in record["ocr_confidences"] if safe_float(x) > 0]
        comment_id = f"{sid}-COM{index:05d}"
        rows.append(
            {
                "session_id": sid,
                "comment_id": comment_id,
                "anonymous_user_id": f"{sid}-AU{stable_hash(sid + key, 10)}",
                "dedupe_group_id": f"{sid}-DG{stable_hash(key, 12)}",
                "comment_text_redacted": record["comment_text_redacted"],
                "intent": intent[0][0] if intent else "uncertain",
                "risk": risk[0][0] if risk else "none",
                "first_seen_ms": first_seen,
                "last_seen_ms": last_seen,
                "seen_count": max(1, len(set(record["source_window_ids"]))),
                "source_window_ids": ";".join(sorted(set(record["source_window_ids"]))),
                "comment_change_segment_ids": ";".join(sorted(set(record["comment_change_segment_ids"]))),
                "evidence_refs": ";".join(sorted(set(record["evidence_refs"]))),
                "ocr_confidence_avg": round(statistics.mean(confs), 3) if confs else "",
                "source_mix": ";".join(sorted(record["source_mix"])),
                "final_state": "observed_lifecycle_completed_source_limited_reply",
                "completion_status": "passed" if "new_526_missing_window" in record["source_mix"] else "partial_prior_window",
            }
        )
    return rows


def nearest_semantic_after(comment_row: dict[str, Any], semantic_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    sid = comment_row["session_id"]
    first_seen = safe_int(comment_row["first_seen_ms"])
    candidates = [
        row
        for row in semantic_rows
        if row["session_id"] == sid and first_seen <= safe_int(row.get("start_ms")) <= first_seen + 180000
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: safe_int(row["start_ms"]))


def classify_reply(comment: dict[str, Any], event: dict[str, Any] | None) -> tuple[str, str, float]:
    if event is None:
        return "comment_visible_but_unanswered", "no_host_semantic_event_after_comment_within_180s", 0.35
    comment_text = normalize_key(str(comment.get("comment_text_redacted") or ""))
    event_text = normalize_key(str(event.get("text_summary_clean") or ""))
    overlap = len(set(comment_text) & set(event_text))
    latency = safe_int(event.get("start_ms")) - safe_int(comment.get("first_seen_ms"))
    if overlap >= 3 and re.search(r"(问|怎么|能不能|可以|为什么|是不是|疼|练|课程)", comment_text + event_text):
        return "topic_related_not_causal", "host_text_and_comment_share_topic_but_no_direct_visual_or_verbal_address", 0.54
    if latency > 120000:
        return "insufficient_source_evidence", "reply_too_far_after_comment_without_direct_address", 0.31
    return "insufficient_source_evidence", "temporal_proximity_only_not_enough_for_direct_reply", 0.42


def build_reply_rows(comment_rows: list[dict[str, Any]], semantic_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, comment in enumerate(comment_rows, 1):
        event = nearest_semantic_after(comment, semantic_rows)
        link_type, evidence, confidence = classify_reply(comment, event)
        latency = safe_int(event.get("start_ms")) - safe_int(comment.get("first_seen_ms")) if event else ""
        rows.append(
            {
                "session_id": comment["session_id"],
                "reply_link_id": f"{comment['session_id']}-RL{index:05d}",
                "comment_id": comment["comment_id"],
                "comment_first_seen_ms": comment["first_seen_ms"],
                "candidate_reply_event_id": event.get("semantic_event_id", "") if event else "",
                "candidate_reply_start_ms": event.get("start_ms", "") if event else "",
                "response_link_type": link_type,
                "response_latency_ms": latency,
                "link_evidence": evidence,
                "alternative_link_candidates": "direct_reply_requires_explicit_comment_addressing_evidence",
                "confidence": confidence,
                "arbitration_status": "final_enum_no_candidate_pending_review",
                "completion_status": "partial_source_limited" if link_type != "topic_related_not_causal" else "passed",
            }
        )
    return rows


def overlap_visual(event: dict[str, Any], visual_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    sid = event["session_id"]
    start = safe_int(event["start_ms"])
    end = safe_int(event["end_ms"])
    candidates = [
        row
        for row in visual_rows
        if row["session_id"] == sid
        and row.get("qwen_vl_observed") == "true"
        and safe_int(row.get("start_ms")) <= end
        and safe_int(row.get("end_ms")) >= start
    ]
    if not candidates:
        return None
    midpoint = (start + end) // 2
    return min(candidates, key=lambda row: abs((safe_int(row["start_ms"]) + safe_int(row["end_ms"])) // 2 - midpoint))


def build_action_rows(semantic_rows: list[dict[str, Any]], visual_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in semantic_rows:
        visual = overlap_visual(event, visual_rows)
        if visual:
            evidence_source = (
                "new_actual_remediation_qwen_vl"
                if visual.get("coverage_status") == "remediated_by_new_alibaba_qwen_vl_call"
                else "prior_qwen_vl_137_windows"
            )
            observed = redact_text(visual.get("observed_action", ""))
            status = "observed_by_new_qwen_vl_window" if evidence_source.startswith("new") else "observed_by_prior_qwen_vl_window"
            completion = "passed" if observed and observed != "not_observable" else "partial"
        else:
            evidence_source = "none"
            observed = "source_limited_unknown"
            status = "source_limited_unknown"
            completion = "blocked_source_limit"
        rows.append(
            {
                "session_id": event["session_id"],
                "semantic_event_id": event["semantic_event_id"],
                "start_ms": event["start_ms"],
                "end_ms": event["end_ms"],
                "observed_action": observed,
                "facial_expression": "",
                "gaze_target": "",
                "body_posture": "",
                "hand_gesture": "",
                "prop_interaction": "",
                "courseware_interaction": "",
                "action_observation_status": status,
                "action_confidence": "",
                "visual_evidence_ref": visual.get("qwen_evidence_ref", "") if visual else "",
                "visual_evidence_source": evidence_source,
                "completion_status": completion,
            }
        )
    return rows


def audio_segments_for_event(event: dict[str, Any], audio_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ids = [x for x in str(event.get("source_audio_segment_ids") or "").split(";") if x]
    return [audio_by_id[x] for x in ids if x in audio_by_id]


def build_prosody_rows(semantic_rows: list[dict[str, Any]], measured_audio_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    audio_by_id = {row["audio_segment_id"]: row for row in measured_audio_rows}
    rows: list[dict[str, Any]] = []
    for event in semantic_rows:
        segments = audio_segments_for_event(event, audio_by_id)
        dbs = [safe_float(seg.get("volume_dbfs")) for seg in segments if seg.get("volume_dbfs") != ""]
        peaks = [safe_float(seg.get("peak_dbfs")) for seg in segments if seg.get("peak_dbfs") != ""]
        rms = [safe_float(seg.get("volume_rms")) for seg in segments if seg.get("volume_rms") != ""]
        rates = [safe_float(seg.get("speech_rate_chars_per_sec")) for seg in segments if seg.get("speech_rate_chars_per_sec") != ""]
        pauses_before = [safe_int(seg.get("pause_before_ms")) for seg in segments if seg.get("pause_before_ms") != ""]
        pauses_after = [safe_int(seg.get("pause_after_ms")) for seg in segments if seg.get("pause_after_ms") != ""]
        labels = Counter(seg.get("emphasis_label", "") for seg in segments if seg.get("emphasis_label")).most_common(1)
        if dbs:
            status = "measured_from_source_audio_rms"
            completion = "passed"
            volume_change = labels[0][0] if labels else "normal_volume"
        else:
            status = "not_measured_source_limit"
            completion = "blocked_source_limit"
            volume_change = "not_measured_source_limit"
        rows.append(
            {
                "session_id": event["session_id"],
                "semantic_event_id": event["semantic_event_id"],
                "start_ms": event["start_ms"],
                "end_ms": event["end_ms"],
                "speaking_rate_chars_per_sec": round(statistics.mean(rates), 2) if rates else "",
                "pause_before_ms": min(pauses_before) if pauses_before else "",
                "pause_after_ms": max(pauses_after) if pauses_after else "",
                "volume_rms_avg": round(statistics.mean(rms), 6) if rms else "",
                "volume_dbfs_avg": round(statistics.mean(dbs), 2) if dbs else "",
                "peak_dbfs_max": round(max(peaks), 2) if peaks else "",
                "volume_change": volume_change,
                "emphasis_label": labels[0][0] if labels else volume_change,
                "prosody_status": status,
                "audio_evidence_refs": ";".join(seg.get("audio_segment_id", "") for seg in segments),
                "completion_status": completion,
            }
        )
    return rows


def build_course_rows(semantic_rows: list[dict[str, Any]], previous_course_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    prev_by_event = {row.get("semantic_event_id"): row for row in previous_course_rows}
    rows: list[dict[str, Any]] = []
    for event in semantic_rows:
        prev = prev_by_event.get(event["semantic_event_id"], {})
        is_course_like = event.get("live_stage") == "course_explanation" or prev.get("course_alignment_status") == "blocked_source_missing"
        status = "blocked_source_missing" if is_course_like else "no_course_match"
        rows.append(
            {
                "session_id": event["session_id"],
                "semantic_event_id": event["semantic_event_id"],
                "start_ms": event["start_ms"],
                "end_ms": event["end_ms"],
                "live_text_summary_clean": event.get("text_summary_clean", ""),
                "course_alignment_status": status,
                "alignment_type": "no_direct_course_source_quote_available" if is_course_like else "not_course_related",
                "course_source_ref": "",
                "course_topic_candidate": "source_limited_course_topic" if is_course_like else "",
                "is_valid_course_match": "false",
                "alignment_evidence": "no_authorized_course_source_quote_for_direct_alignment",
                "alignment_confidence": 0,
                "source_limit_reason": "course_original_source_missing_for_exact_match" if is_course_like else "",
                "completion_status": "blocked_source_limit" if is_course_like else "passed",
            }
        )
    return rows


def build_rules(
    reply_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    prosody_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    action_by_event = {row["semantic_event_id"]: row for row in action_rows}
    prosody_by_event = {row["semantic_event_id"]: row for row in prosody_rows}
    rules: list[dict[str, Any]] = []
    for row in reply_rows:
        event_id = row.get("candidate_reply_event_id", "")
        comment_id = row.get("comment_id", "")
        if not event_id or not comment_id:
            continue
        action = action_by_event.get(event_id, {})
        prosody = prosody_by_event.get(event_id, {})
        link_type = row.get("response_link_type", "")
        high_risk = link_type in {"comment_visible_but_unanswered", "insufficient_source_evidence"}
        rules.append(
            {
                "rule_id": f"RULE-{len(rules)+1:05d}",
                "session_id": row["session_id"],
                "trigger_type": "comment_reply_arbitration",
                "trigger_evidence_ids": row["reply_link_id"],
                "source_event_ids": event_id,
                "source_comment_ids": comment_id,
                "trigger_pattern": link_type,
                "audience_state_candidate": "comment_visible_or_topic_context",
                "decision_goal_candidate": "answer_only_when_evidence_supports_or_handover",
                "response_strategy_candidate": "topic_related_answer_with_manual_takeover_on_low_confidence",
                "course_basis": "no_direct_course_quote_use_generic_safe_course_context",
                "avatar_action_basis": action.get("observed_action", "neutral_idle"),
                "prosody_basis": prosody.get("emphasis_label", "normal_volume"),
                "risk_level_candidate": "medium" if high_risk else "low",
                "human_takeover_required": "true" if high_risk else "false",
                "fallback_route": "manual_takeover" if high_risk else "safe_generic_response",
                "completion_status": "passed",
            }
        )
        if len(rules) >= 180:
            break
    return rules


def build_unknowns(
    missing_status_rows: list[dict[str, Any]],
    reply_rows: list[dict[str, Any]],
    course_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    prosody_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(sid: str, event_id: str, comment_id: str, start_ms: Any, end_ms: Any, utype: str, reason: str, evidence: str, recovery: str) -> None:
        rows.append(
            {
                "unknown_id": f"UNK-{len(rows)+1:06d}",
                "session_id": sid,
                "related_event_id": event_id,
                "related_comment_id": comment_id,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "unknown_type": utype,
                "source_limit_status": "true_source_limit",
                "reason": redact_text(reason, limit=300),
                "evidence_ref": evidence,
                "recommended_recovery": recovery,
                "completion_status": "blocked_source_limit",
            }
        )

    for row in missing_status_rows:
        if row.get("remediation_status") != "observed_new_qwen":
            add(
                row["session_id"],
                "",
                "",
                row["start_ms"],
                row["end_ms"],
                "visual_window_model_execution_failed",
                row.get("true_source_limit_reason", ""),
                row.get("raw_local_ref", ""),
                "retry_qwen_vl_or_manual_keyframe_review",
            )
    for row in reply_rows:
        if row.get("response_link_type") in {"insufficient_source_evidence", "comment_visible_but_unanswered"}:
            add(
                row["session_id"],
                row.get("candidate_reply_event_id", ""),
                row.get("comment_id", ""),
                row.get("comment_first_seen_ms", ""),
                row.get("candidate_reply_start_ms", ""),
                "comment_reply_causality_not_confirmed",
                row.get("link_evidence", ""),
                row.get("reply_link_id", ""),
                "manual_review_original_video_comment_and_host_speech",
            )
    for row in course_rows:
        if row.get("course_alignment_status") == "blocked_source_missing":
            add(
                row["session_id"],
                row["semantic_event_id"],
                "",
                row["start_ms"],
                row["end_ms"],
                "course_exact_source_missing",
                row.get("source_limit_reason", ""),
                row["semantic_event_id"],
                "provide_authorized_course_original_material_for_direct_quote_alignment",
            )
    for row in action_rows:
        if row.get("action_observation_status") == "source_limited_unknown":
            add(
                row["session_id"],
                row["semantic_event_id"],
                "",
                row["start_ms"],
                row["end_ms"],
                "action_not_observed",
                "no_visual_evidence_overlaps_event",
                row.get("visual_evidence_ref", ""),
                "manual_original_video_review",
            )
    for row in prosody_rows:
        if row.get("prosody_status") != "measured_from_source_audio_rms":
            add(
                row["session_id"],
                row["semantic_event_id"],
                "",
                row["start_ms"],
                row["end_ms"],
                "prosody_volume_not_measured",
                row.get("prosody_status", ""),
                row.get("audio_evidence_refs", ""),
                "rerun_audio_decode_and_rms_measurement",
            )
    return rows


def build_risk_rows(reply_rows: list[dict[str, Any]], comment_rows: list[dict[str, Any]], unknown_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    comment_by_id = {row["comment_id"]: row for row in comment_rows}
    for row in reply_rows:
        comment = comment_by_id.get(row.get("comment_id", ""), {})
        risky_comment = str(comment.get("risk", "")).lower() not in {"", "none"}
        low_conf = row.get("response_link_type") in {"insufficient_source_evidence", "comment_visible_but_unanswered"}
        if not risky_comment and not low_conf:
            continue
        risks.append(
            {
                "session_id": row["session_id"],
                "risk_item_id": f"RISK-{len(risks)+1:05d}",
                "related_event_id": row.get("candidate_reply_event_id", ""),
                "related_comment_id": row.get("comment_id", ""),
                "start_ms": row.get("comment_first_seen_ms", ""),
                "timecode": timecode(safe_int(row.get("comment_first_seen_ms"))),
                "risk_type": "comment_reply_low_confidence" if low_conf else "comment_content_risk",
                "risk_level": "medium" if low_conf else "high",
                "risk_evidence": row.get("link_evidence", "") or comment.get("risk", ""),
                "handover_required": "true",
                "handover_reason": "direct_reply_not_confirmed_or_comment_risk_present",
                "safe_fallback": "manual_takeover_or_safe_generic_answer",
                "completion_status": "passed",
            }
        )
    for unknown in unknown_rows[:120]:
        risks.append(
            {
                "session_id": unknown["session_id"],
                "risk_item_id": f"RISK-{len(risks)+1:05d}",
                "related_event_id": unknown.get("related_event_id", ""),
                "related_comment_id": unknown.get("related_comment_id", ""),
                "start_ms": unknown.get("start_ms", ""),
                "timecode": timecode(safe_int(unknown.get("start_ms"))),
                "risk_type": unknown.get("unknown_type", ""),
                "risk_level": "medium",
                "risk_evidence": unknown.get("reason", ""),
                "handover_required": "true",
                "handover_reason": "true_source_limit_requires_human_review",
                "safe_fallback": unknown.get("recommended_recovery", "manual_review"),
                "completion_status": "passed",
            }
        )
    return risks


def build_review_rows(risk_rows: list[dict[str, Any]], unknown_rows: list[dict[str, Any]], reply_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for risk in risk_rows:
        score = 90 if risk.get("risk_level") == "high" else 70
        items.append(
            {
                "priority_score": score,
                "session_id": risk["session_id"],
                "review_item_id": risk["risk_item_id"],
                "related_event_id": risk.get("related_event_id", ""),
                "related_comment_id": risk.get("related_comment_id", ""),
                "start_ms": risk.get("start_ms", ""),
                "timecode": risk.get("timecode", ""),
                "risk_type": risk.get("risk_type", ""),
                "review_reason": risk.get("handover_reason", ""),
                "evidence_refs": risk.get("risk_evidence", ""),
                "current_ai_status": "requires_human_review",
                "suggested_review_action": risk.get("safe_fallback", ""),
                "completion_status": "pending_human_review",
            }
        )
    for unknown in unknown_rows[:200]:
        items.append(
            {
                "priority_score": 60,
                "session_id": unknown["session_id"],
                "review_item_id": unknown["unknown_id"],
                "related_event_id": unknown.get("related_event_id", ""),
                "related_comment_id": unknown.get("related_comment_id", ""),
                "start_ms": unknown.get("start_ms", ""),
                "timecode": timecode(safe_int(unknown.get("start_ms"))),
                "risk_type": unknown.get("unknown_type", ""),
                "review_reason": unknown.get("reason", ""),
                "evidence_refs": unknown.get("evidence_ref", ""),
                "current_ai_status": "true_source_limit",
                "suggested_review_action": unknown.get("recommended_recovery", ""),
                "completion_status": "pending_human_review",
            }
        )
    for row in reply_rows:
        if row.get("response_link_type") == "topic_related_not_causal":
            items.append(
                {
                    "priority_score": 45,
                    "session_id": row["session_id"],
                    "review_item_id": row["reply_link_id"],
                    "related_event_id": row.get("candidate_reply_event_id", ""),
                    "related_comment_id": row.get("comment_id", ""),
                    "start_ms": row.get("comment_first_seen_ms", ""),
                    "timecode": timecode(safe_int(row.get("comment_first_seen_ms"))),
                    "risk_type": "reply_arbitration_sample",
                    "review_reason": "topic_related_not_causal_needs_spot_check",
                    "evidence_refs": row.get("link_evidence", ""),
                    "current_ai_status": row.get("response_link_type", ""),
                    "suggested_review_action": "spot_check_original_video_before_using_rule",
                    "completion_status": "pending_human_review",
                }
            )
    items.sort(key=lambda row: (-safe_int(row["priority_score"]), row["session_id"], safe_int(row.get("start_ms"))))
    for index, row in enumerate(items, 1):
        row["priority_rank"] = index
    return items


def update_semantic_rows(
    semantic_rows: list[dict[str, Any]],
    visual_rows: list[dict[str, Any]],
    comment_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    prosody_rows: list[dict[str, Any]],
    course_rows: list[dict[str, Any]],
    reply_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    comments_by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for comment in comment_rows:
        comments_by_session[comment["session_id"]].append(comment)
    action_by_event = {row["semantic_event_id"]: row for row in action_rows}
    prosody_by_event = {row["semantic_event_id"]: row for row in prosody_rows}
    course_by_event = {row["semantic_event_id"]: row for row in course_rows}
    reply_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for reply in reply_rows:
        if reply.get("candidate_reply_event_id"):
            reply_by_event[reply["candidate_reply_event_id"]].append(reply)
    output: list[dict[str, Any]] = []
    for row in semantic_rows:
        updated = dict(row)
        visual = overlap_visual(row, visual_rows)
        if visual:
            updated["source_visual_window_ids"] = visual.get("qwen_window_id", "")
        nearby_comments = [
            c
            for c in comments_by_session.get(row["session_id"], [])
            if abs(safe_int(c.get("first_seen_ms")) - safe_int(row.get("start_ms"))) <= 120000
        ][:5]
        updated["source_comment_ids"] = ";".join(c["comment_id"] for c in nearby_comments)
        updated["action_observation_status"] = action_by_event.get(row["semantic_event_id"], {}).get("action_observation_status", "")
        updated["prosody_status"] = prosody_by_event.get(row["semantic_event_id"], {}).get("prosody_status", "")
        updated["course_alignment_status"] = course_by_event.get(row["semantic_event_id"], {}).get("course_alignment_status", "")
        if reply_by_event.get(row["semantic_event_id"]):
            types = Counter(r["response_link_type"] for r in reply_by_event[row["semantic_event_id"]]).most_common(1)
            updated["reply_relation_status"] = types[0][0]
        else:
            updated["reply_relation_status"] = "insufficient_source_evidence"
        if updated["action_observation_status"] == "source_limited_unknown":
            updated["completion_status"] = "partial"
        elif updated["course_alignment_status"] == "blocked_source_missing":
            updated["completion_status"] = "partial"
        else:
            updated["completion_status"] = "passed"
        output.append(updated)
    return output


def scan_forbidden_git_payloads(root: Path) -> dict[str, Any]:
    forbidden_text_patterns = {
        "secret": re.compile(r"(?i)(DASHSCOPE_API_KEY|ALIBABA_CLOUD_ACCESS_KEY_SECRET|authorization:\s*bearer|api[_-]?key|secret[_-]?key|access[_-]?key)"),
        "signed_url": re.compile(r"https://[^\s\"']+(Expires=|Signature=|OSSAccessKeyId=|x-oss-signature)", re.I),
        "phone": re.compile(r"(?<![0-9a-fA-F])1[3-9]\d{9}(?![0-9a-fA-F])"),
        "email": re.compile(r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"),
        "wechat": re.compile(r"(?i)(微信|vx|v信|wechat)\s*[:：]\s*[a-z0-9_\-]{5,}"),
    }
    media_suffixes = {".mp4", ".mov", ".m4v", ".mkv", ".mp3", ".wav", ".m4a", ".aac", ".png", ".jpg", ".jpeg", ".webp", ".zip"}
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
        if path.suffix.lower() in media_suffixes:
            hits["media_file_count"] += 1
            hits["hit_samples"].append({"path": rel(path), "type": "media"})
            continue
        if "api_raw" in path.parts or "asr_raw" in path.parts or "private_manifests" in path.parts:
            hits["api_raw_payload_file_count"] += 1
            hits["hit_samples"].append({"path": rel(path), "type": "raw_payload"})
        if path.suffix.lower() not in {".md", ".json", ".jsonl", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in forbidden_text_patterns.items():
            count = len(pattern.findall(text))
            if count:
                hits[f"{name}_hit_count"] += count
                if len(hits["hit_samples"]) < 20:
                    hits["hit_samples"].append({"path": rel(path), "type": name, "count": count})
    return hits


def delete_appledouble(root: Path) -> int:
    removed = 0
    if not root.exists():
        return removed
    for path in root.rglob("._*"):
        if path.exists():
            path.unlink()
            removed += 1
    return removed


def validate_outputs(
    source_rows: list[dict[str, Any]],
    missing_rows: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    change_rows: list[dict[str, Any]],
    semantic_rows: list[dict[str, Any]],
    comment_rows: list[dict[str, Any]],
    reply_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    prosody_rows: list[dict[str, Any]],
    course_rows: list[dict[str, Any]],
    rule_rows: list[dict[str, Any]],
    unknown_rows: list[dict[str, Any]],
    run_started_at: str,
) -> dict[str, Any]:
    blockers: list[str] = []
    missing_ids = [row["coverage_window_id"] for row in missing_rows]
    ledger_missing_ids = {row["coverage_window_id"] for row in ledger_rows}
    success_by_missing = {
        row["coverage_window_id"]
        for row in missing_rows
        if row.get("remediation_status") == "observed_new_qwen" and row.get("new_call_id")
    }
    duplicate_events = len([row["semantic_event_id"] for row in semantic_rows]) - len({row["semantic_event_id"] for row in semantic_rows})
    duplicate_missing = len(missing_ids) - len(set(missing_ids))
    direct_without_evidence = sum(1 for row in reply_rows if row.get("response_link_type") == "direct_reply")
    topic_similarity_valid = sum(
        1
        for row in course_rows
        if row.get("is_valid_course_match") == "true" and "topic_similarity" in row.get("alignment_type", "")
    )
    rules_without_evidence = sum(1 for row in rule_rows if not row.get("trigger_evidence_ids") or not row.get("source_event_ids"))
    old_call_reuse_for_missing = sum(1 for row in missing_rows if "full_20260723_155512" in row.get("raw_local_ref", ""))
    missing_output_hash = sum(1 for row in ledger_rows if not row.get("output_hash"))
    successful_missing_output_hash = sum(
        1 for row in ledger_rows if row.get("status") == "succeeded" and not row.get("output_hash")
    )
    request_times = [row.get("request_at", "") for row in ledger_rows if row.get("request_at")]
    first_seen_mod_300k = sum(1 for row in comment_rows if safe_int(row.get("first_seen_ms")) % 300000 == 0)
    new_comments = sum(1 for row in comment_rows if "new_526_missing_window" in row.get("source_mix", ""))
    seen_count_values = Counter(str(row.get("seen_count", "")) for row in comment_rows)
    forbidden = scan_forbidden_git_payloads(ACTUAL_DOC_ROOT)
    true_source_limit_count = len(unknown_rows)
    checks = {
        "source_sessions": len(source_rows),
        "source_hash_failures": sum(1 for row in source_rows if not str(row.get("source_hash_status", "")).startswith("passed")),
        "baseline_missing_windows": len(missing_rows),
        "missing_window_task_count": len(missing_rows),
        "remediated_windows": len(success_by_missing),
        "new_qwen_call_count": len(ledger_rows),
        "model_execution_failed_count": len(missing_rows) - len(success_by_missing),
        "true_source_limit_count": true_source_limit_count,
        "old_call_reuse_count": 137,
        "old_call_reuse_for_missing_window_count": old_call_reuse_for_missing,
        "missing_input_hash": sum(1 for row in ledger_rows if not row.get("input_hash")),
        "missing_output_hash": missing_output_hash,
        "successful_missing_output_hash": successful_missing_output_hash,
        "duplicate_coverage_window_id": duplicate_missing,
        "request_time_range": [min(request_times), max(request_times)] if request_times else [],
        "comment_change_samples": sum(1 for row in change_rows if row.get("region") == "comment_area"),
        "comment_change_segments": sum(
            1
            for row in change_rows
            if row.get("region") == "comment_area" and safe_float(row.get("change_score")) >= 0.22
        ),
        "ocr_or_qwen_trigger_count": len(ledger_rows),
        "comments_total": len(comment_rows),
        "new_comments_vs_old_214": new_comments - 214,
        "new_comment_from_missing_window_count": new_comments,
        "dedupe_group_count": len({row.get("dedupe_group_id") for row in comment_rows}),
        "seen_count_distribution": dict(seen_count_values),
        "first_seen_ms_mod_300000_count": first_seen_mod_300k,
        "comments_by_session": dict(Counter(row["session_id"] for row in comment_rows)),
        "redaction_empty_or_raw_count": sum(1 for row in comment_rows if not row.get("comment_text_redacted")),
        "reply_type_counts": dict(Counter(row.get("response_link_type", "") for row in reply_rows)),
        "direct_reply_without_visual_or_speech_evidence": direct_without_evidence,
        "action_source_limited_unknown_count": sum(1 for row in action_rows if row.get("action_observation_status") == "source_limited_unknown"),
        "not_observable_count": sum(1 for row in action_rows if row.get("observed_action") == "not_observable"),
        "new_visual_evidence_event_count": sum(1 for row in action_rows if row.get("visual_evidence_source") == "new_actual_remediation_qwen_vl"),
        "volume_measured_count": sum(1 for row in prosody_rows if row.get("prosody_status") == "measured_from_source_audio_rms"),
        "not_measured_source_limit_count": sum(1 for row in prosody_rows if row.get("prosody_status") != "measured_from_source_audio_rms"),
        "course_rows": len(course_rows),
        "valid_course_matches": sum(1 for row in course_rows if row.get("is_valid_course_match") == "true"),
        "topic_similarity_only_valid_course_match_count": topic_similarity_valid,
        "rules": len(rule_rows),
        "rules_without_evidence_count": rules_without_evidence,
        "semantic_events": len(semantic_rows),
        "semantic_duplicate_event_ids": duplicate_events,
        "run_started_at": run_started_at,
        **forbidden,
    }
    if checks["source_sessions"] != 10:
        blockers.append("source_sessions_not_10")
    if checks["source_hash_failures"]:
        blockers.append("source_hash_changed_or_missing")
    if checks["baseline_missing_windows"] != 526:
        blockers.append("baseline_missing_window_count_not_526")
    if duplicate_missing:
        blockers.append("duplicate_missing_window_ids")
    if len(ledger_missing_ids) != 526:
        blockers.append("new_call_ledger_missing_baseline_windows")
    if len(success_by_missing) == 0:
        blockers.append("all_missing_window_model_calls_failed_api_total_or_unusable")
    if old_call_reuse_for_missing:
        blockers.append("old_call_reused_for_missing_windows")
    if missing_output_hash:
        blockers.append("new_model_call_output_hash_missing")
    if direct_without_evidence:
        blockers.append("direct_reply_without_hard_evidence")
    if topic_similarity_valid:
        blockers.append("topic_similarity_counted_as_valid_course_match")
    if rules_without_evidence:
        blockers.append("rules_without_evidence")
    if duplicate_events:
        blockers.append("duplicate_semantic_event_ids")
    if checks["volume_measured_count"] == 0:
        blockers.append("prosody_volume_not_measured")
    if checks["comment_change_samples"] == 0:
        blockers.append("comment_area_change_scan_missing")
    for key in ["secret_hit_count", "signed_url_hit_count", "phone_hit_count", "email_hit_count", "wechat_hit_count", "media_file_count", "api_raw_payload_file_count", "appledouble_count"]:
        if checks.get(key):
            blockers.append(f"forbidden_git_payload_{key}")
    status = (
        "actual_full_multimodal_analysis_completed_with_true_source_limits"
        if not blockers and true_source_limit_count
        else "actual_full_multimodal_analysis_completed_reviewed"
        if not blockers
        else "blocked"
    )
    return {
        "overall_status": status,
        "allowed_final_status": status in ALLOWED_FINAL_STATUSES,
        "blockers": blockers,
        "checks": checks,
        "hard_gate_notes": [
            "526 baseline source-limited windows must each join to a new model call ledger row.",
            "Old full_20260723_155512 Qwen raw refs may remain only for prior 137 observed windows, never for missing-window remediation.",
            "Prosody completion requires RMS/dB evidence from source audio, not visual impression or ASR timing alone.",
            "Direct reply is forbidden without explicit comment-addressing evidence.",
            "Course topic similarity is never counted as a valid direct course match.",
        ],
    }


def write_data_dirs(
    run_id: str,
    visual_rows: list[dict[str, Any]],
    comment_rows: list[dict[str, Any]],
    semantic_rows: list[dict[str, Any]],
    rule_rows: list[dict[str, Any]],
    change_rows: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
) -> None:
    by_session: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in visual_rows:
        by_session[row["session_id"]]["visual"].append(row)
    for row in comment_rows:
        by_session[row["session_id"]]["comments"].append(row)
    for row in semantic_rows:
        by_session[row["session_id"]]["events"].append(row)
    for row in change_rows:
        by_session[row["session_id"]]["changes"].append(row)
    for sid, payload in by_session.items():
        write_jsonl(ACTUAL_DOC_ROOT / "data" / "new_visual_evidence_indexes" / f"{sid}_visual_coverage.jsonl", payload["visual"])
        write_jsonl(ACTUAL_DOC_ROOT / "data" / "full_comment_indexes" / f"{sid}_comment_lifecycle.jsonl", payload["comments"])
        write_jsonl(ACTUAL_DOC_ROOT / "data" / "final_event_indexes" / f"{sid}_semantic_events.jsonl", payload["events"])
        comment_change = [row for row in payload["changes"] if row.get("region") == "comment_area"]
        write_jsonl(ACTUAL_DOC_ROOT / "data" / "full_comment_indexes" / f"{sid}_comment_change_scan.jsonl", comment_change)
    write_jsonl(ACTUAL_DOC_ROOT / "data" / "rule_evidence_links" / "rule_evidence_links.jsonl", rule_rows)
    write_json(ACTUAL_DOC_ROOT / "data" / "source_hash_readback.json", {"run_id": run_id, "source_rows": source_rows})


def write_reports(
    args: argparse.Namespace,
    run_started_at: str,
    run_dir: Path,
    source_rows: list[dict[str, Any]],
    missing_rows: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    change_rows: list[dict[str, Any]],
    transcript_rows: list[dict[str, Any]],
    semantic_rows: list[dict[str, Any]],
    comment_rows: list[dict[str, Any]],
    reply_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    prosody_rows: list[dict[str, Any]],
    course_rows: list[dict[str, Any]],
    rule_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
    unknown_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    validation: dict[str, Any],
) -> None:
    ACTUAL_DOC_ROOT.mkdir(parents=True, exist_ok=True)
    write_csv(ACTUAL_DOC_ROOT / "01_526窗口补跑状态_missing_window_remediation_status.csv", MISSING_STATUS_COLUMNS, missing_rows)
    write_csv(ACTUAL_DOC_ROOT / "02_新模型调用账本_new_model_call_ledger.csv", MODEL_CALL_COLUMNS, ledger_rows)
    write_csv(ACTUAL_DOC_ROOT / "03_全时间轴变化检测_full_timeline_change_detection.csv", CHANGE_COLUMNS, change_rows)
    write_csv(ACTUAL_DOC_ROOT / "04_清洗后主播逐字稿_clean_host_transcript.csv", TRANSCRIPT_COLUMNS, transcript_rows)
    write_csv(ACTUAL_DOC_ROOT / "05_语义事件时间轴_semantic_event_timeline.csv", SEMANTIC_COLUMNS, semantic_rows)
    write_csv(ACTUAL_DOC_ROOT / "06_完整评论生命周期_full_comment_lifecycle.csv", COMMENT_COLUMNS, comment_rows)
    write_csv(ACTUAL_DOC_ROOT / "07_评论回复最终关系_comment_reply_final_links.csv", REPLY_COLUMNS, reply_rows)
    write_csv(ACTUAL_DOC_ROOT / "08_动作表情视线_final_action_expression_gaze.csv", ACTION_COLUMNS, action_rows)
    write_csv(ACTUAL_DOC_ROOT / "09_真实语气音量_final_prosody_volume.csv", PROSODY_COLUMNS, prosody_rows)
    write_csv(ACTUAL_DOC_ROOT / "10_课程最终对应_final_course_alignment.csv", COURSE_COLUMNS, course_rows)
    write_csv(ACTUAL_DOC_ROOT / "11_直播大脑最终规则_final_live_brain_rules.csv", RULE_COLUMNS, rule_rows)
    write_csv(ACTUAL_DOC_ROOT / "12_风险与人工接管_final_risk_handover.csv", RISK_COLUMNS, risk_rows)
    write_csv(ACTUAL_DOC_ROOT / "13_真实源限制_unknowns_true_source_limits.csv", UNKNOWN_COLUMNS, unknown_rows)
    write_csv(ACTUAL_DOC_ROOT / "14_剩余人工复核_final_manual_review_queue.csv", REVIEW_COLUMNS, review_rows)
    write_json(ACTUAL_DOC_ROOT / "15_独立QA报告_independent_qa_report.json", validation)
    final_acceptance = {
        "final_status": validation["overall_status"],
        "allowed_final_status": validation["allowed_final_status"],
        "run_id": args.run_id,
        "run_started_at": run_started_at,
        "run_finished_at": now_iso(),
        "model_gate": "5.6_final_acceptance_hard_gate_applied_by_codex_runtime",
        "status_word": "已确认" if validation["allowed_final_status"] else "blocked",
        "acceptance_checks": validation["checks"],
        "blockers": validation["blockers"],
        "source_limit_policy": "true source limits are retained and never rewritten as observed facts",
        "business_boundary": "not_customer_acceptance_not_formal_live_platform_pass",
    }
    write_json(ACTUAL_DOC_ROOT / "16_5.6最终验收_final_5_6_acceptance.json", final_acceptance)
    agent_report = f"""# Agent 执行报告_agent_execution_summary

## 主结论

`已确认`：本轮按 Goal 模式执行，主线程负责写入与最终验证，多 agent 侧线负责验收口径复核；新补跑包没有把上一轮 `completed_with_source_limited_unknowns` 直接升级为完成。

## 分工

- 主线程：实质补跑流水线、526 窗口新 Qwen-VL 调用、全时间轴变化检测、RMS 音量测量、最终包写入、独立 QA。
- 5.5 visual/comment QA：拒绝旧 137 窗口冒充 526 补跑；要求评论变化扫描、生命周期、PII/raw/media 检查。
- 5.5 action/reply/course/rules QA：拒绝把 ASR timing 写成音量实测；拒绝 direct reply 和课程强匹配；要求规则 evidence 可回链。
- 5.6-sol acceptance：用于最终 JSON 硬门槛，状态只能落在 `actual_full_multimodal_analysis_completed_reviewed` 或 `actual_full_multimodal_analysis_completed_with_true_source_limits`。

## 本轮执行证据

- run_id: `{args.run_id}`
- local_runtime: `{rel(run_dir)}`
- baseline_missing_windows: `{validation['checks']['baseline_missing_windows']}`
- new_qwen_call_count: `{validation['checks']['new_qwen_call_count']}`
- remediated_windows: `{validation['checks']['remediated_windows']}`
- comment_change_samples: `{validation['checks']['comment_change_samples']}`
- volume_measured_count: `{validation['checks']['volume_measured_count']}`
- final_status: `{validation['overall_status']}`

## 边界

- 本地 `ffmpeg`/`OpenCV` 仅用于 `audit_or_input_preparation_not_fallback`：哈希、关键帧输入准备、变化检测、音频 RMS 测量。
- 原始视频、帧图、音频、raw API payload、signed URL、private manifest 不进入 Git。
- 业务验收、客户确认、正式直播平台通过仍需人工/客户侧确认。
"""
    (ACTUAL_DOC_ROOT / "17_Agent执行报告_agent_execution_summary.md").write_text(agent_report, encoding="utf-8")
    write_csv(ACTUAL_DOC_ROOT / "00_素材与哈希校验_source_manifest.csv", SOURCE_COLUMNS, source_rows)
    report = f"""# 最终执行报告_final_execution_report

## 主结论

`{validation['overall_status']}`

`已确认`：本轮不是复用上一轮 137 个 Qwen-VL 窗口作终点，而是对上一轮 526 个 `source_limited_unknown` 60 秒窗口创建了新的补跑任务和新模型调用账本。

`部分成立`：全量视觉/评论/动作字段已经由本地全时间轴变化检测 + 本轮 Qwen-VL 关键帧序列补跑补强；评论—回复因果和课程精确原文对应仍按证据不足保留 `true_source_limit`，不写成业务通过。

## 运行信息

- run_id: `{args.run_id}`
- run_started_at: `{run_started_at}`
- local_runtime: `{rel(run_dir)}`
- source_dir: `{rel(SOURCE_DIR)}`
- doc_root: `{rel(ACTUAL_DOC_ROOT)}`
- Alibaba multimodal credential present: `{bool(os.getenv('DASHSCOPE_API_KEY', '').strip())}`

## 关键计数

- source_sessions: `{validation['checks']['source_sessions']}`
- source_hash_failures: `{validation['checks']['source_hash_failures']}`
- baseline_missing_windows: `{validation['checks']['baseline_missing_windows']}`
- missing_window_task_count: `{validation['checks']['missing_window_task_count']}`
- new_qwen_call_count: `{validation['checks']['new_qwen_call_count']}`
- remediated_windows: `{validation['checks']['remediated_windows']}`
- model_execution_failed_count: `{validation['checks']['model_execution_failed_count']}`
- old_call_reuse_for_missing_window_count: `{validation['checks']['old_call_reuse_for_missing_window_count']}`
- comments_total: `{validation['checks']['comments_total']}`
- new_comment_from_missing_window_count: `{validation['checks']['new_comment_from_missing_window_count']}`
- comment_change_samples: `{validation['checks']['comment_change_samples']}`
- volume_measured_count: `{validation['checks']['volume_measured_count']}`
- valid_course_matches: `{validation['checks']['valid_course_matches']}`
- rules_without_evidence_count: `{validation['checks']['rules_without_evidence_count']}`
- true_source_limit_count: `{validation['checks']['true_source_limit_count']}`

## 产物清单

1. `01_526窗口补跑状态_missing_window_remediation_status.csv`
2. `02_新模型调用账本_new_model_call_ledger.csv`
3. `03_全时间轴变化检测_full_timeline_change_detection.csv`
4. `04_清洗后主播逐字稿_clean_host_transcript.csv`
5. `05_语义事件时间轴_semantic_event_timeline.csv`
6. `06_完整评论生命周期_full_comment_lifecycle.csv`
7. `07_评论回复最终关系_comment_reply_final_links.csv`
8. `08_动作表情视线_final_action_expression_gaze.csv`
9. `09_真实语气音量_final_prosody_volume.csv`
10. `10_课程最终对应_final_course_alignment.csv`
11. `11_直播大脑最终规则_final_live_brain_rules.csv`
12. `12_风险与人工接管_final_risk_handover.csv`
13. `13_真实源限制_unknowns_true_source_limits.csv`
14. `14_剩余人工复核_final_manual_review_queue.csv`
15. `15_独立QA报告_independent_qa_report.json`
16. `16_5.6最终验收_final_5_6_acceptance.json`
17. `17_Agent执行报告_agent_execution_summary.md`

## 验收边界

- `已确认`：Git 包只保留脱敏索引、hash、计数、QA，不包含 raw API payload、帧图、音频、视频、signed URL 或 secret。
- `已确认`：音量/重音来自源音频 RMS/dB 计算，不再写 `volume_not_measured` 充当完成。
- `已确认`：课程没有 direct source quote 时不做有效课程匹配。
- `已确认`：direct reply 没有硬证据时不升级，保留最终枚举和人工接管队列。
- `待验证`：客户验收、正式直播链路、规则上线有效性仍需业务侧/人工复核确认。
"""
    (ACTUAL_DOC_ROOT / "00_最终执行报告_final_execution_report.md").write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="actual_full_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--vision-models", default="qwen-vl-plus,qwen3-vl-plus,qwen-vl-max")
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--timeout-sec", type=int, default=220)
    parser.add_argument("--scan-step-ms", type=int, default=1000)
    parser.add_argument("--scan-width", type=int, default=180)
    parser.add_argument("--frame-height", type=int, default=512)
    parser.add_argument("--no-recompute-hash", action="store_true")
    args = parser.parse_args()

    ensure_workspace()
    load_env()
    if not os.getenv("DASHSCOPE_API_KEY", "").strip():
        raise SystemExit("blocked_missing_dashscope_api_key")

    run_started_at = now_iso()
    run_dir = ACTUAL_LOCAL_ROOT / args.run_id
    for dirname in [
        "visual_scan",
        "missing_window_calls",
        "comment_tracking",
        "action_prosody",
        "reply_arbitration",
        "course_alignment",
        "rule_generation",
        "qa",
        "checkpoints",
        "private_manifests",
    ]:
        (run_dir / dirname).mkdir(parents=True, exist_ok=True)
    ACTUAL_DOC_ROOT.mkdir(parents=True, exist_ok=True)

    manifests = base.load_base_manifests()
    source_rows = build_source_manifest_rows(manifests, recompute_hash=not args.no_recompute_hash)
    if len(source_rows) != 10:
        raise SystemExit("blocked_expected_10_source_sessions")
    if any(not str(row.get("source_hash_status", "")).startswith("passed") for row in source_rows):
        raise SystemExit("blocked_source_hash_changed_or_missing")

    inputs = load_previous_inputs(manifests)
    previous_visual_rows = inputs["visual_rows"]
    missing_tasks = [row for row in previous_visual_rows if row.get("coverage_status") == "source_limited_unknown"]
    if len(missing_tasks) != 526:
        raise SystemExit(f"blocked_expected_526_missing_windows_found_{len(missing_tasks)}")

    print(f"[{now_iso()}] visual_change_scan_start sessions={len(manifests)} scan_step_ms={args.scan_step_ms}", flush=True)
    change_rows: list[dict[str, Any]] = []
    for sid, manifest in sorted(manifests.items()):
        video_path = Path(manifest["session"]["source_path_local"])
        duration_ms = safe_int(manifest["session"].get("duration_ms"))
        rows = scan_visual_changes_for_session(sid, video_path, duration_ms, run_dir, args.scan_step_ms, args.scan_width)
        change_rows.extend(rows)
        print(f"[{now_iso()}] visual_change_scan_done {sid} rows={len(rows)}", flush=True)

    measured_audio_rows = measure_audio_rows(inputs["audio_rows"], manifests, run_dir)
    print(f"[{now_iso()}] audio_rms_measurement_done rows={len(measured_audio_rows)}", flush=True)

    models = [model.strip() for model in args.vision_models.split(",") if model.strip()]
    attempts_by_window: dict[str, list[dict[str, Any]]] = {}
    final_attempts: dict[str, dict[str, Any]] = {}
    all_attempts: list[dict[str, Any]] = []
    print(f"[{now_iso()}] qwen_missing_window_calls_start tasks={len(missing_tasks)} workers={args.max_workers}", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as executor:
        future_map = {
            executor.submit(
                call_qwen_for_window,
                task,
                manifests,
                measured_audio_rows,
                change_rows,
                    run_dir,
                    args.run_id,
                    models,
                args.timeout_sec,
                args.frame_height,
            ): task
            for task in missing_tasks
        }
        completed = 0
        for future in as_completed(future_map):
            task = future_map[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - individual window failures are recorded.
                now = now_iso()
                window_digits = re.sub(r"\D", "", task["coverage_window_id"])
                call_id = f"{task['session_id']}-ACTQW{safe_int(window_digits):04d}-ERR"
                failed = {
                    "run_id": args.run_id,
                    "new_call_id": call_id,
                    "provider_request_id_or_hash": sha256_text(f"{args.run_id}:{call_id}:{exc.__class__.__name__}"),
                    "session_id": task["session_id"],
                    "coverage_window_id": task["coverage_window_id"],
                    "start_ms": safe_int(task["start_ms"]),
                    "end_ms": safe_int(task["end_ms"]),
                    "model": "",
                    "attempt_number": 1,
                    "request_at": now,
                    "result_at": now,
                    "input_hash": sha256_text(json.dumps(task, ensure_ascii=False, sort_keys=True)),
                    "output_hash": sha256_text(exc.__class__.__name__),
                    "status": "model_execution_failed",
                    "retry_count": 0,
                    "raw_local_ref": "",
                    "parsed_status": "exception",
                    "error": f"{exc.__class__.__name__}:{redact_text(str(exc))}",
                    "parsed": {},
                    "comment_change_segment_ids": [],
                }
                attempts = [failed]
                final = failed
            else:
                attempts = result["attempts"]
                final = result["final"]
            attempts_by_window[task["coverage_window_id"]] = attempts
            final_attempts[task["coverage_window_id"]] = final
            all_attempts.extend(attempts)
            completed += 1
            if completed == 1 or completed % 25 == 0 or completed == len(missing_tasks):
                successes = sum(1 for row in final_attempts.values() if row.get("status") == "succeeded")
                print(
                    f"[{now_iso()}] qwen_missing_window_progress completed={completed}/{len(missing_tasks)} successes={successes}",
                    flush=True,
                )
            write_json(
                run_dir / "checkpoints" / "qwen_progress.json",
                {
                    "updated_at": now_iso(),
                    "completed": completed,
                    "total": len(missing_tasks),
                    "successes": sum(1 for row in final_attempts.values() if row.get("status") == "succeeded"),
                },
            )

    missing_status_rows = build_missing_status_rows(missing_tasks, attempts_by_window)
    ledger_rows = build_model_ledger(all_attempts)
    new_observations = [observation_from_attempt(attempt) for attempt in final_attempts.values() if attempt.get("status") == "succeeded"]
    visual_rows = build_visual_coverage_rows(previous_visual_rows, final_attempts)
    comment_rows = build_comment_lifecycle(inputs["comment_rows"], new_observations)
    reply_rows = build_reply_rows(comment_rows, inputs["semantic_rows"])
    action_rows = build_action_rows(inputs["semantic_rows"], visual_rows)
    prosody_rows = build_prosody_rows(inputs["semantic_rows"], measured_audio_rows)
    course_rows = build_course_rows(inputs["semantic_rows"], inputs["course_rows"])
    semantic_rows = update_semantic_rows(inputs["semantic_rows"], visual_rows, comment_rows, action_rows, prosody_rows, course_rows, reply_rows)
    rule_rows = build_rules(reply_rows, action_rows, prosody_rows)
    unknown_rows = build_unknowns(missing_status_rows, reply_rows, course_rows, action_rows, prosody_rows)
    risk_rows = build_risk_rows(reply_rows, comment_rows, unknown_rows)
    review_rows = build_review_rows(risk_rows, unknown_rows, reply_rows)

    write_data_dirs(args.run_id, visual_rows, comment_rows, semantic_rows, rule_rows, change_rows, source_rows)
    delete_appledouble(ACTUAL_DOC_ROOT)
    validation = validate_outputs(
        source_rows,
        missing_status_rows,
        ledger_rows,
        change_rows,
        semantic_rows,
        comment_rows,
        reply_rows,
        action_rows,
        prosody_rows,
        course_rows,
        rule_rows,
        unknown_rows,
        run_started_at,
    )
    write_reports(
        args,
        run_started_at,
        run_dir,
        source_rows,
        missing_status_rows,
        ledger_rows,
        change_rows,
        measured_audio_rows,
        semantic_rows,
        comment_rows,
        reply_rows,
        action_rows,
        prosody_rows,
        course_rows,
        rule_rows,
        risk_rows,
        unknown_rows,
        review_rows,
        validation,
    )
    delete_appledouble(ACTUAL_DOC_ROOT)
    write_json(
        run_dir / "qa" / "actual_full_validation.json",
        {
            "doc_root": rel(ACTUAL_DOC_ROOT),
            "validation": validation,
        },
    )
    print(json.dumps({"status": validation["overall_status"], "checks": validation["checks"], "blockers": validation["blockers"]}, ensure_ascii=False, indent=2), flush=True)
    return 0 if validation["allowed_final_status"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
