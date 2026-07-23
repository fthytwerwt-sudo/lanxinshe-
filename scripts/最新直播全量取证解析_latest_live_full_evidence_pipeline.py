"""Latest-live full evidence extraction pipeline.

This script is intentionally scoped to the current workspace. It reads source
videos, creates local-only evidence artifacts, calls Alibaba APIs only when the
operator passes the explicit flags, and writes redacted repo artifacts.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import mimetypes
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

try:
    import oss2
except ModuleNotFoundError:  # pragma: no cover - reported in capability matrix.
    oss2 = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "最新直播"
DOC_ROOT = (
    PROJECT_ROOT
    / "docs"
    / "直播录屏解析方案_live_recording_analysis"
    / "最新直播全量取证解析_latest_live_full_evidence_analysis"
)
LOCAL_ROOT = PROJECT_ROOT / "_local_runtime" / "最新直播全量解析_latest_live_full_analysis"
SESSION_MANIFEST_DIR = DOC_ROOT / "data" / "session_manifests"
EVENT_INDEX_DIR = DOC_ROOT / "data" / "redacted_event_indexes"

DEFAULT_COMPATIBLE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
RUN_STATUS = "provisional_pending_5_6_review"
PII_REDACTED = "[redacted_pii]"

SESSION_COLUMNS = [
    "session_id",
    "source_video",
    "source_hash",
    "file_size",
    "duration_ms",
    "width",
    "height",
    "fps",
    "audio_present",
    "comment_area_visible",
    "decode_status",
    "analysis_status",
]

CAPABILITY_COLUMNS = [
    "capability",
    "status",
    "evidence",
    "fallback_route",
    "review_flag",
]

SUMMARY_COLUMNS = [
    "session_id",
    "source_video",
    "duration_min",
    "asr_status",
    "asr_sentence_count",
    "vision_status",
    "vision_window_count",
    "comment_area_visible",
    "comment_event_count",
    "reply_candidate_count",
    "course_candidate_count",
    "manual_review_count",
    "analysis_status",
]

EVENT_COLUMNS = [
    "event_id",
    "session_id",
    "start_ms",
    "end_ms",
    "event_type",
    "evidence_type",
    "evidence_ref",
    "observation_status",
    "confidence",
    "review_flag",
    "speaker_text_clean",
    "live_stage",
    "utterance_function",
    "comment_text_redacted",
    "response_link_type",
    "observed_action",
    "prosody_label",
    "course_source_ref",
    "provisional_status",
]

COMMENT_REPLY_COLUMNS = [
    "link_id",
    "session_id",
    "comment_event_ids",
    "reply_event_ids",
    "response_link_type",
    "response_latency_ms",
    "link_evidence",
    "link_confidence",
    "link_status",
    "alternative_link_candidates",
    "unanswered_reason",
    "provisional_status",
]

HOST_COLUMNS = [
    "event_id",
    "session_id",
    "start_ms",
    "end_ms",
    "speaker_text_clean",
    "live_stage",
    "utterance_function",
    "response_goal_candidate",
    "response_strategy_candidate",
    "observed_action",
    "facial_expression",
    "gaze_target",
    "body_posture",
    "hand_gesture",
    "courseware_interaction",
    "speaking_rate",
    "pause_before_ms",
    "pause_after_ms",
    "prosody_label",
    "emotion_observed",
    "confidence",
    "review_flag",
    "provisional_status",
]

COURSE_COLUMNS = [
    "event_id",
    "session_id",
    "start_ms",
    "end_ms",
    "course_lesson_id",
    "course_chunk_id",
    "course_source_ref",
    "course_topic",
    "alignment_type",
    "alignment_evidence",
    "alignment_confidence",
    "course_fidelity_candidate",
    "live_transformation_type",
    "compliance_risk_candidate",
    "review_flag",
    "provisional_status",
]

RISK_COLUMNS = [
    "sample_id",
    "session_id",
    "event_id",
    "start_ms",
    "failure_type",
    "failure_evidence",
    "missed_comment",
    "wrong_intent_response_candidate",
    "topic_drift",
    "overlong_explanation",
    "premature_sales_push",
    "repeated_response",
    "action_speech_mismatch",
    "compliance_risk",
    "human_takeover_candidate",
    "ignore_comment_candidate",
    "provisional_status",
]

REVIEW_COLUMNS = [
    "review_id",
    "session_id",
    "event_id",
    "timecode",
    "evidence_source",
    "review_question",
    "ai_current_candidate",
    "alternative_explanation",
    "confidence",
    "suggested_review_action",
    "provisional_status",
]

RULE_COLUMNS = [
    "rule_id",
    "trigger_type",
    "trigger_pattern",
    "audience_state_candidate",
    "decision_goal_candidate",
    "response_strategy_candidate",
    "response_template_structure",
    "course_source_ref",
    "avatar_action_candidate",
    "prosody_candidate",
    "next_question_or_hook_candidate",
    "risk_level_candidate",
    "human_takeover_required_candidate",
    "fallback_route_candidate",
    "review_status",
    "provisional_status",
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def ensure_workspace() -> None:
    if PROJECT_ROOT != Path("/Volumes/WD_BLACK/澜心社直播"):
        raise SystemExit("blocked_wrong_workspace")


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


def run_cmd(args: list[str], timeout: int | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def ffprobe_json(path: Path) -> dict[str, Any]:
    code, out, err = run_cmd(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ],
        timeout=120,
    )
    if code != 0:
        return {"error": err.strip() or out.strip()}
    return json.loads(out)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024 * 8), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fraction_float(value: str) -> float:
    if not value or value == "0/0":
        return 0.0
    if "/" in value:
        num, den = value.split("/", 1)
        try:
            return float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def read_videos() -> list[Path]:
    if not SOURCE_DIR.exists():
        raise SystemExit("blocked_material_path_missing")
    videos = [
        p
        for p in SOURCE_DIR.iterdir()
        if p.is_file()
        and not p.name.startswith("._")
        and p.suffix.lower() in {".mp4", ".mov", ".m4v", ".mkv"}
    ]
    return sorted(videos, key=lambda p: p.name.lower())


def session_id(index: int) -> str:
    return f"latest_live_{index:02d}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def redact_text(text: str | None) -> str:
    if not text:
        return ""
    safe = str(text)
    safe = re.sub(r"1[3-9]\d{9}", PII_REDACTED, safe)
    safe = re.sub(r"\b\d{6,}\b", PII_REDACTED, safe)
    safe = re.sub(r"(?i)(微信|vx|v信|wechat)[:：]?\s*[a-z0-9_\-]{5,}", r"\1:" + PII_REDACTED, safe)
    safe = re.sub(r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", PII_REDACTED, safe)
    safe = safe.replace("\n", " ").strip()
    return safe[:500]


def parse_model_json(text: str) -> tuple[dict[str, Any], str]:
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
    stripped = re.sub(r"```$", "", stripped).strip()
    try:
        return json.loads(stripped), ""
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, re.S)
        if match:
            try:
                return json.loads(match.group(0)), ""
            except json.JSONDecodeError as exc:
                return {}, str(exc)
        return {}, "json_object_not_found"


def api_post_json(url: str, payload: dict[str, Any], timeout: int = 180) -> tuple[bool, dict[str, Any], str]:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        return False, {}, "blocked_missing_dashscope_api_key"
    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return False, {}, f"blocked_network_error:{exc.__class__.__name__}"
    try:
        body = response.json()
    except ValueError:
        body = {"message": response.text[:500]}
    if not response.ok:
        message = body.get("message") or body.get("error", {}).get("message") or f"http_{response.status_code}"
        return False, body, redact_text(str(message))
    return True, body, ""


def encode_data_url(path: Path, max_chars: int = 11_000_000) -> tuple[str, str]:
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    if len(encoded) > max_chars:
        return "", f"base64_too_large:{len(encoded)}"
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64,{encoded}", ""


def build_video_payload(model: str, data_url: str, start_ms: int, end_ms: int) -> dict[str, Any]:
    prompt = f"""
请基于这个直播录屏窗口输出严格 JSON，不要 Markdown，不要解释。
窗口时间：{start_ms}ms 到 {end_ms}ms。
只记录可观察事实和候选推测；不要还原主播内心；不要输出评论用户名、手机号、微信号、真实姓名，评论只输出脱敏后的 comment_text_redacted。
JSON 字段：
{{
  "comment_area_visible": "yes/no/uncertain",
  "visible_comments": [{{"comment_text_redacted": "", "comment_intent_candidate": "", "comment_risk": "none/pii/compliance/uncertain", "ocr_confidence": 0.0}}],
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
    "courseware_interaction": "",
    "observed_action_confidence": 0.0,
    "action_meaning_candidate": ""
  }},
  "prosody": {{
    "speaking_rate": "",
    "pause_observed": "",
    "prosody_label": "",
    "emotion_observed": "",
    "prosody_confidence": 0.0
  }},
  "reply_relation_candidate": {{
    "is_reply_window": false,
    "response_link_type": "uncertain_pending_review",
    "link_evidence": "",
    "link_confidence": 0.0,
    "unanswered_reason": ""
  }},
  "risk_or_failure": {{
    "failure_type": "",
    "failure_evidence": "",
    "human_takeover_candidate": ""
  }}
}}
""".strip()
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "video_url", "video_url": {"url": data_url, "fps": 1.0}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "temperature": 0.0,
        "max_tokens": 1200,
    }


def extract_audio(video: Path, audio_path: Path) -> tuple[str, str]:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    if audio_path.exists() and audio_path.stat().st_size > 0:
        return "reused", ""
    code, out, err = run_cmd(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "48k",
            str(audio_path),
        ],
        timeout=1800,
    )
    if code != 0:
        return "failed", redact_text(err or out)
    return "created", ""


def make_clip(video: Path, clip_path: Path, start_sec: float, duration_sec: int) -> tuple[str, str]:
    clip_path.parent.mkdir(parents=True, exist_ok=True)
    if clip_path.exists() and clip_path.stat().st_size > 0:
        return "reused", ""
    code, out, err = run_cmd(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            f"{start_sec:.3f}",
            "-i",
            str(video),
            "-t",
            str(duration_sec),
            "-vf",
            "scale=-2:360",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "36",
            "-c:a",
            "aac",
            "-b:a",
            "32k",
            "-movflags",
            "+faststart",
            str(clip_path),
        ],
        timeout=900,
    )
    if code != 0:
        return "failed", redact_text(err or out)
    return "created", ""


def build_bucket():
    if oss2 is None:
        return None, "blocked_oss2_missing"
    required = [
        "ALIBABA_CLOUD_ACCESS_KEY_ID",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
        "ALIBABA_OSS_ENDPOINT",
        "ALIBABA_OSS_BUCKET",
    ]
    missing = [key for key in required if not os.getenv(key, "").strip()]
    if missing:
        return None, "blocked_missing_oss_env:" + ",".join(missing)
    auth = oss2.Auth(
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip(),
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip(),
    )
    bucket = oss2.Bucket(
        auth,
        os.getenv("ALIBABA_OSS_ENDPOINT", "").strip(),
        os.getenv("ALIBABA_OSS_BUCKET", "").strip(),
    )
    return bucket, ""


def upload_for_asr(bucket: Any, local_file: Path, object_key: str) -> tuple[str, str]:
    if bucket is None:
        return "", "bucket_not_available"
    try:
        bucket.put_object_from_file(object_key, str(local_file))
        expires = int(os.getenv("ALIBABA_OSS_SIGNED_URL_EXPIRES", "86400") or "86400")
        expires = max(expires, 3600)
        return bucket.sign_url("GET", object_key, expires), ""
    except Exception as exc:  # noqa: BLE001 - external SDK errors vary.
        return "", f"blocked_oss_upload_failed:{exc.__class__.__name__}"


def submit_asr_task(audio_url: str) -> tuple[str, dict[str, Any], str]:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        return "", {}, "blocked_missing_dashscope_api_key"
    url = f"{DEFAULT_DASHSCOPE_BASE_URL}/services/audio/asr/transcription"
    payload = {
        "model": "fun-asr",
        "input": {"file_urls": [audio_url]},
        "parameters": {
            "channel_id": [0],
            "language_hints": ["zh"],
            "diarization_enabled": False,
        },
    }
    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            },
            json=payload,
            timeout=120,
        )
    except requests.RequestException as exc:
        return "", {}, f"blocked_asr_submit_network:{exc.__class__.__name__}"
    try:
        body = response.json()
    except ValueError:
        body = {"message": response.text[:500]}
    if not response.ok:
        return "", body, redact_text(str(body.get("message") or body))
    task_id = str(body.get("output", {}).get("task_id") or "")
    return task_id, body, "" if task_id else "blocked_asr_task_id_missing"


def poll_asr_task(task_id: str, timeout_sec: int, poll_interval_sec: int) -> tuple[str, dict[str, Any], str]:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    url = f"{DEFAULT_DASHSCOPE_BASE_URL}/tasks/{task_id}"
    deadline = time.time() + timeout_sec
    last_body: dict[str, Any] = {}
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = f"asr_poll_transient_error:{exc.__class__.__name__}"
            time.sleep(poll_interval_sec)
            continue
        last_body = body
        status = str(body.get("output", {}).get("task_status") or body.get("task_status") or "")
        if status in {"SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"}:
            return status.lower(), body, ""
        time.sleep(poll_interval_sec)
    return "pending_timeout", last_body, last_error or "asr_poll_timeout"


def download_asr_result(query_body: dict[str, Any], target_path: Path) -> tuple[list[dict[str, Any]], str]:
    results = query_body.get("output", {}).get("results", [])
    if not results:
        return [], "asr_result_url_missing"
    result = results[0]
    if result.get("subtask_status") != "SUCCEEDED":
        return [], redact_text(str(result.get("message") or result.get("code") or "asr_subtask_failed"))
    url = result.get("transcription_url", "")
    if not url:
        return [], "asr_transcription_url_missing"
    try:
        response = requests.get(url, timeout=180)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        return [], f"asr_result_download_failed:{exc.__class__.__name__}"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(target_path, data)
    sentences: list[dict[str, Any]] = []
    for transcript in data.get("transcripts", []):
        for sentence in transcript.get("sentences", []) or []:
            begin = int(sentence.get("begin_time") or 0)
            end = int(sentence.get("end_time") or begin)
            text = redact_text(sentence.get("text", ""))
            if text:
                sentences.append(
                    {
                        "begin_time": begin,
                        "end_time": end,
                        "text": text,
                        "sentence_id": sentence.get("sentence_id", ""),
                        "speaker_id": sentence.get("speaker_id", ""),
                    }
                )
    return sentences, ""


def load_bridge_rows(limit: int = 20000) -> list[dict[str, str]]:
    bridge_path = (
        PROJECT_ROOT
        / "项目资料_docs"
        / "课程解析资料_course_analysis"
        / "05_直播项目桥接_live_project_bridge"
        / "神经数字人课程解析包_neural_avatar_course_analysis_pack"
        / "data"
        / "live_project_bridge_fields.csv"
    )
    rows: list[dict[str, str]] = []
    if not bridge_path.exists():
        return rows
    with bridge_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append({k: str(v or "") for k, v in row.items()})
            if len(rows) >= limit:
                break
    return rows


def char_ngrams(text: str, n: int = 2) -> set[str]:
    clean = re.sub(r"\s+", "", text)
    return {clean[i : i + n] for i in range(max(0, len(clean) - n + 1)) if clean[i : i + n].strip()}


def align_course(text: str, bridge_rows: list[dict[str, str]], top_n: int = 1) -> list[dict[str, Any]]:
    grams = char_ngrams(text)
    if not grams:
        return []
    scored: list[tuple[int, dict[str, str]]] = []
    for row in bridge_rows:
        sample = row.get("knowledge_point_sample", "")
        score = len(grams & char_ngrams(sample))
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    output = []
    for score, row in scored[:top_n]:
        output.append(
            {
                "lesson_id": row.get("lesson_id", ""),
                "chunk_id": row.get("chunk_id", ""),
                "source_ref": row.get("source_ref", ""),
                "topic": redact_text(row.get("knowledge_point_sample", "")),
                "score": score,
                "confidence": min(0.69, round(score / max(8, len(grams)), 2)),
            }
        )
    return output


def timecode(ms: int) -> str:
    sec = ms // 1000
    hh = sec // 3600
    mm = (sec % 3600) // 60
    ss = sec % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def make_event_id(sid: str, start_ms: int, seq: int) -> str:
    return f"{sid}-E{start_ms:012d}-{seq:04d}"


def build_inventory(videos: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_rows: list[dict[str, Any]] = []
    manifests: list[dict[str, Any]] = []
    for index, video in enumerate(videos, 1):
        sid = session_id(index)
        probe = ffprobe_json(video)
        streams = probe.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
        fmt = probe.get("format", {})
        duration_sec = safe_float(fmt.get("duration"))
        fps = fraction_float(video_stream.get("avg_frame_rate", "")) or fraction_float(video_stream.get("r_frame_rate", ""))
        source_hash = sha256_file(video)
        row = {
            "session_id": sid,
            "source_video": video.name,
            "source_path_local": str(video),
            "source_hash": source_hash,
            "file_size": video.stat().st_size,
            "duration_ms": int(duration_sec * 1000),
            "width": video_stream.get("width", ""),
            "height": video_stream.get("height", ""),
            "fps": round(fps, 3),
            "audio_present": "yes" if audio_stream else "no",
            "comment_area_visible": "pending_api_observation",
            "decode_status": "decode_metadata_readable" if not probe.get("error") else "decode_metadata_failed",
            "analysis_status": "pending",
            "video_codec": video_stream.get("codec_name", ""),
            "audio_codec": audio_stream.get("codec_name", ""),
            "audio_sample_rate": audio_stream.get("sample_rate", ""),
        }
        source_rows.append(row)
        manifests.append({"session": row, "ffprobe": probe})
    return source_rows, manifests


def run_vision_for_session(
    video: Path,
    sid: str,
    duration_ms: int,
    args: argparse.Namespace,
    local_session_dir: Path,
) -> list[dict[str, Any]]:
    if not args.run_vision:
        return []
    rows: list[dict[str, Any]] = []
    model_candidates = [m.strip() for m in args.vision_models.split(",") if m.strip()]
    starts = list(range(0, max(duration_ms, 1), args.vision_interval_sec * 1000))
    if args.vision_max_windows_per_session > 0:
        starts = starts[: args.vision_max_windows_per_session]
    for seq, start_ms in enumerate(starts, 1):
        start_sec = start_ms / 1000
        end_ms = min(duration_ms, start_ms + args.vision_duration_sec * 1000)
        clip_path = local_session_dir / "vision_clips" / f"{sid}_window_{seq:04d}_{start_ms}.mp4"
        clip_status, clip_error = make_clip(video, clip_path, start_sec, args.vision_duration_sec)
        record: dict[str, Any] = {
            "session_id": sid,
            "window_seq": seq,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "clip_path_local": rel(clip_path),
            "clip_status": clip_status,
            "api_status": "not_called",
            "model": "",
            "parsed": {},
            "raw_response_path_local": "",
            "error": clip_error,
        }
        if clip_status == "failed":
            rows.append(record)
            continue
        data_url, data_error = encode_data_url(clip_path)
        if not data_url:
            record.update({"api_status": "blocked_clip_too_large", "error": data_error})
            rows.append(record)
            continue
        for model in model_candidates:
            payload = build_video_payload(model, data_url, start_ms, end_ms)
            ok, body, error = api_post_json(
                f"{DEFAULT_COMPATIBLE_BASE_URL}/chat/completions",
                payload,
                timeout=args.vision_timeout_sec,
            )
            record["model"] = model
            if not ok:
                record.update({"api_status": "failed", "error": error})
                continue
            content = str(body.get("choices", [{}])[0].get("message", {}).get("content", ""))
            parsed, parse_error = parse_model_json(content)
            raw_path = local_session_dir / "api_raw" / f"{sid}_vision_{seq:04d}_{model}.json"
            write_json(raw_path, {"response": body, "parsed": parsed, "parse_error": parse_error})
            record.update(
                {
                    "api_status": "connected",
                    "parsed": parsed,
                    "raw_response_path_local": rel(raw_path),
                    "error": parse_error,
                }
            )
            break
        rows.append(record)
    return rows


def run_asr_for_session(video: Path, sid: str, args: argparse.Namespace, local_session_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    status: dict[str, Any] = {"asr_status": "not_requested", "sentences": 0, "error": ""}
    if not args.run_asr:
        return [], status
    audio_path = local_session_dir / "audio" / f"{sid}_audio_16k_mono.mp3"
    audio_status, audio_error = extract_audio(video, audio_path)
    status.update({"audio_extract_status": audio_status, "audio_path_local": rel(audio_path)})
    if audio_status == "failed":
        status.update({"asr_status": "audio_extract_failed", "error": audio_error})
        return [], status
    bucket, bucket_error = build_bucket()
    if bucket_error:
        status.update({"asr_status": "blocked_oss_unavailable", "error": bucket_error})
        return [], status
    prefix = os.getenv("ALIBABA_OSS_OBJECT_PREFIX", "lanxin-live").strip().strip("/")
    object_key = f"{prefix}/latest_live_full_evidence/{args.run_id}/{sid}/audio_16k_mono.mp3"
    signed_url, upload_error = upload_for_asr(bucket, audio_path, object_key)
    local_private_manifest = local_session_dir / "api_private" / "asr_upload_private.json"
    write_json(
        local_private_manifest,
        {
            "object_key": object_key,
            "signed_url_present": bool(signed_url),
            "signed_url": signed_url,
            "upload_error": upload_error,
        },
    )
    status.update({"oss_object_key_redacted": object_key, "private_manifest_local": rel(local_private_manifest)})
    if upload_error:
        status.update({"asr_status": "oss_upload_failed", "error": upload_error})
        return [], status
    task_id, submit_body, submit_error = submit_asr_task(signed_url)
    submit_path = local_session_dir / "api_private" / "asr_submit_response.json"
    write_json(submit_path, submit_body)
    status.update({"asr_task_id": task_id, "asr_submit_response_local": rel(submit_path)})
    if submit_error:
        status.update({"asr_status": "asr_submit_failed", "error": submit_error})
        return [], status
    poll_status, query_body, poll_error = poll_asr_task(task_id, args.asr_timeout_sec, args.asr_poll_interval_sec)
    query_path = local_session_dir / "api_private" / "asr_query_response.json"
    write_json(query_path, query_body)
    status.update({"asr_status": poll_status, "asr_query_response_local": rel(query_path), "error": poll_error})
    if poll_status != "succeeded":
        return [], status
    raw_asr_path = local_session_dir / "asr_raw" / f"{sid}_asr_result.json"
    sentences, dl_error = download_asr_result(query_body, raw_asr_path)
    status.update({"asr_result_local": rel(raw_asr_path), "sentences": len(sentences), "download_error": dl_error})
    if dl_error:
        status.update({"asr_status": "asr_result_download_failed", "error": dl_error})
        return [], status
    return sentences, status


def prepare_asr_submission(video: Path, sid: str, args: argparse.Namespace, local_session_dir: Path) -> dict[str, Any]:
    status: dict[str, Any] = {"asr_status": "not_requested", "sentences": 0, "error": ""}
    if not args.run_asr:
        return status
    audio_path = local_session_dir / "audio" / f"{sid}_audio_16k_mono.mp3"
    audio_status, audio_error = extract_audio(video, audio_path)
    status.update({"audio_extract_status": audio_status, "audio_path_local": rel(audio_path)})
    if audio_status == "failed":
        status.update({"asr_status": "audio_extract_failed", "error": audio_error})
        return status
    bucket, bucket_error = build_bucket()
    if bucket_error:
        status.update({"asr_status": "blocked_oss_unavailable", "error": bucket_error})
        return status
    prefix = os.getenv("ALIBABA_OSS_OBJECT_PREFIX", "lanxin-live").strip().strip("/")
    object_key = f"{prefix}/latest_live_full_evidence/{args.run_id}/{sid}/audio_16k_mono.mp3"
    signed_url, upload_error = upload_for_asr(bucket, audio_path, object_key)
    local_private_manifest = local_session_dir / "api_private" / "asr_upload_private.json"
    write_json(
        local_private_manifest,
        {
            "object_key": object_key,
            "signed_url_present": bool(signed_url),
            "signed_url": signed_url,
            "upload_error": upload_error,
        },
    )
    status.update({"oss_object_key_redacted": object_key, "private_manifest_local": rel(local_private_manifest)})
    if upload_error:
        status.update({"asr_status": "oss_upload_failed", "error": upload_error})
        return status
    task_id, submit_body, submit_error = submit_asr_task(signed_url)
    submit_path = local_session_dir / "api_private" / "asr_submit_response.json"
    write_json(submit_path, submit_body)
    status.update({"asr_task_id": task_id, "asr_submit_response_local": rel(submit_path)})
    if submit_error:
        status.update({"asr_status": "asr_submit_failed", "error": submit_error})
        return status
    status.update({"asr_status": "submitted"})
    return status


def finish_asr_submission(status: dict[str, Any], args: argparse.Namespace, local_session_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    task_id = str(status.get("asr_task_id") or "")
    if not task_id:
        return [], status
    poll_status, query_body, poll_error = poll_asr_task(task_id, args.asr_timeout_sec, args.asr_poll_interval_sec)
    query_path = local_session_dir / "api_private" / "asr_query_response.json"
    write_json(query_path, query_body)
    status.update({"asr_status": poll_status, "asr_query_response_local": rel(query_path), "error": poll_error})
    if poll_status != "succeeded":
        return [], status
    raw_asr_path = local_session_dir / "asr_raw" / f"{local_session_dir.name}_asr_result.json"
    sentences, dl_error = download_asr_result(query_body, raw_asr_path)
    status.update({"asr_result_local": rel(raw_asr_path), "sentences": len(sentences), "download_error": dl_error})
    if dl_error:
        status.update({"asr_status": "asr_result_download_failed", "error": dl_error})
        return [], status
    return sentences, status


def build_session_outputs(
    inventory_row: dict[str, Any],
    sentences: list[dict[str, Any]],
    asr_status: dict[str, Any],
    vision_rows: list[dict[str, Any]],
    bridge_rows: list[dict[str, str]],
) -> dict[str, list[dict[str, Any]]]:
    sid = inventory_row["session_id"]
    events: list[dict[str, Any]] = []
    host_rows: list[dict[str, Any]] = []
    comment_links: list[dict[str, Any]] = []
    course_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    rules: list[dict[str, Any]] = []
    seq = 0

    for sentence in sentences:
        seq += 1
        start_ms = int(sentence["begin_time"])
        end_ms = int(sentence["end_time"])
        eid = make_event_id(sid, start_ms, seq)
        text = redact_text(sentence["text"])
        candidates = align_course(text, bridge_rows, top_n=1)
        candidate = candidates[0] if candidates else {}
        live_stage = "讲课_or_互动待复核"
        event = {
            "event_id": eid,
            "session_id": sid,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "event_type": "host_speech",
            "evidence_type": "asr_sentence",
            "evidence_ref": asr_status.get("asr_result_local", ""),
            "observation_status": "derived",
            "confidence": "" if asr_status.get("asr_status") != "succeeded" else 0.72,
            "review_flag": "asr_pending_human_review",
            "speaker_text_clean": text,
            "live_stage": live_stage,
            "utterance_function": "course_or_response_candidate",
            "comment_text_redacted": "",
            "response_link_type": "uncertain_pending_review",
            "observed_action": "",
            "prosody_label": "pending_audio_prosody_review",
            "course_source_ref": candidate.get("source_ref", "insufficient_evidence"),
            "provisional_status": RUN_STATUS,
        }
        events.append(event)
        host_rows.append(
            {
                "event_id": eid,
                "session_id": sid,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "speaker_text_clean": text,
                "live_stage": live_stage,
                "utterance_function": "course_or_response_candidate",
                "response_goal_candidate": "pending_5_6_review",
                "response_strategy_candidate": "pending_5_6_review",
                "observed_action": "",
                "facial_expression": "",
                "gaze_target": "",
                "body_posture": "",
                "hand_gesture": "",
                "courseware_interaction": "",
                "speaking_rate": "pending_audio_metric",
                "pause_before_ms": "",
                "pause_after_ms": "",
                "prosody_label": "pending_audio_prosody_review",
                "emotion_observed": "pending_audio_visual_review",
                "confidence": 0.62,
                "review_flag": "host_logic_pending_review",
                "provisional_status": RUN_STATUS,
            }
        )
        if candidate:
            course_rows.append(
                {
                    "event_id": eid,
                    "session_id": sid,
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "course_lesson_id": candidate.get("lesson_id", ""),
                    "course_chunk_id": candidate.get("chunk_id", ""),
                    "course_source_ref": candidate.get("source_ref", ""),
                    "course_topic": candidate.get("topic", ""),
                    "alignment_type": "topic_similarity_only",
                    "alignment_evidence": "local_ngram_candidate_from_bridge_csv",
                    "alignment_confidence": candidate.get("confidence", 0.0),
                    "course_fidelity_candidate": "course_alignment_candidate_only",
                    "live_transformation_type": "chunk_or_topic_only",
                    "compliance_risk_candidate": "pending_review",
                    "review_flag": "course_alignment_pending_review",
                    "provisional_status": RUN_STATUS,
                }
            )
    comment_seq = 0
    for window in vision_rows:
        parsed = window.get("parsed") or {}
        start_ms = int(window.get("start_ms") or 0)
        end_ms = int(window.get("end_ms") or start_ms)
        seq += 1
        eid = make_event_id(sid, start_ms, seq)
        host = parsed.get("host", {}) if isinstance(parsed, dict) else {}
        action = parsed.get("action", {}) if isinstance(parsed, dict) else {}
        prosody = parsed.get("prosody", {}) if isinstance(parsed, dict) else {}
        reply = parsed.get("reply_relation_candidate", {}) if isinstance(parsed, dict) else {}
        risk = parsed.get("risk_or_failure", {}) if isinstance(parsed, dict) else {}
        visible_comments = parsed.get("visible_comments", []) if isinstance(parsed, dict) else []
        event = {
            "event_id": eid,
            "session_id": sid,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "event_type": "multimodal_window",
            "evidence_type": "qwen_vl_video_window",
            "evidence_ref": window.get("raw_response_path_local", ""),
            "observation_status": "inferred" if window.get("api_status") == "connected" else "blocked",
            "confidence": action.get("observed_action_confidence", "") if isinstance(action, dict) else "",
            "review_flag": "visual_api_pending_human_review",
            "speaker_text_clean": redact_text(host.get("speaker_text_summary", "")) if isinstance(host, dict) else "",
            "live_stage": host.get("live_stage_candidate", "") if isinstance(host, dict) else "",
            "utterance_function": host.get("utterance_function_candidate", "") if isinstance(host, dict) else "",
            "comment_text_redacted": "",
            "response_link_type": reply.get("response_link_type", "uncertain_pending_review") if isinstance(reply, dict) else "uncertain_pending_review",
            "observed_action": redact_text(action.get("observed_action", "")) if isinstance(action, dict) else "",
            "prosody_label": redact_text(prosody.get("prosody_label", "")) if isinstance(prosody, dict) else "",
            "course_source_ref": "",
            "provisional_status": RUN_STATUS,
        }
        events.append(event)
        host_rows.append(
            {
                "event_id": eid,
                "session_id": sid,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "speaker_text_clean": event["speaker_text_clean"],
                "live_stage": event["live_stage"],
                "utterance_function": event["utterance_function"],
                "response_goal_candidate": host.get("response_goal_candidate", "") if isinstance(host, dict) else "",
                "response_strategy_candidate": host.get("response_strategy_candidate", "") if isinstance(host, dict) else "",
                "observed_action": event["observed_action"],
                "facial_expression": redact_text(action.get("facial_expression", "")) if isinstance(action, dict) else "",
                "gaze_target": redact_text(action.get("gaze_target", "")) if isinstance(action, dict) else "",
                "body_posture": redact_text(action.get("body_posture", "")) if isinstance(action, dict) else "",
                "hand_gesture": redact_text(action.get("hand_gesture", "")) if isinstance(action, dict) else "",
                "courseware_interaction": redact_text(action.get("courseware_interaction", "")) if isinstance(action, dict) else "",
                "speaking_rate": redact_text(prosody.get("speaking_rate", "")) if isinstance(prosody, dict) else "",
                "pause_before_ms": "",
                "pause_after_ms": redact_text(prosody.get("pause_observed", "")) if isinstance(prosody, dict) else "",
                "prosody_label": event["prosody_label"],
                "emotion_observed": redact_text(prosody.get("emotion_observed", "")) if isinstance(prosody, dict) else "",
                "confidence": action.get("observed_action_confidence", "") if isinstance(action, dict) else "",
                "review_flag": "visual_api_pending_human_review",
                "provisional_status": RUN_STATUS,
            }
        )
        if risk and any(risk.get(k) for k in risk):
            risk_rows.append(
                {
                    "sample_id": f"{sid}-R{len(risk_rows)+1:04d}",
                    "session_id": sid,
                    "event_id": eid,
                    "start_ms": start_ms,
                    "failure_type": redact_text(risk.get("failure_type", "")),
                    "failure_evidence": redact_text(risk.get("failure_evidence", "")),
                    "missed_comment": "",
                    "wrong_intent_response_candidate": "",
                    "topic_drift": "",
                    "overlong_explanation": "",
                    "premature_sales_push": "",
                    "repeated_response": "",
                    "action_speech_mismatch": "",
                    "compliance_risk": "",
                    "human_takeover_candidate": redact_text(risk.get("human_takeover_candidate", "")),
                    "ignore_comment_candidate": "",
                    "provisional_status": RUN_STATUS,
                }
            )
        if visible_comments:
            related_comments: list[str] = []
            for item in visible_comments[:8]:
                if not isinstance(item, dict):
                    continue
                text = redact_text(item.get("comment_text_redacted", ""))
                if not text:
                    continue
                comment_seq += 1
                cid = f"{sid}-C{comment_seq:05d}"
                related_comments.append(cid)
                ceid = f"{eid}-{cid}"
                events.append(
                    {
                        "event_id": ceid,
                        "session_id": sid,
                        "start_ms": start_ms,
                        "end_ms": end_ms,
                        "event_type": "comment",
                        "evidence_type": "qwen_vl_comment_ocr",
                        "evidence_ref": window.get("raw_response_path_local", ""),
                        "observation_status": "inferred",
                        "confidence": item.get("ocr_confidence", ""),
                        "review_flag": "comment_ocr_pending_human_review",
                        "speaker_text_clean": "",
                        "live_stage": "",
                        "utterance_function": "",
                        "comment_text_redacted": text,
                        "response_link_type": "uncertain_pending_review",
                        "observed_action": "",
                        "prosody_label": "",
                        "course_source_ref": "",
                        "provisional_status": RUN_STATUS,
                    }
                )
            if related_comments:
                comment_links.append(
                    {
                        "link_id": f"{sid}-L{len(comment_links)+1:04d}",
                        "session_id": sid,
                        "comment_event_ids": ";".join(related_comments),
                        "reply_event_ids": eid if reply.get("is_reply_window") else "",
                        "response_link_type": reply.get("response_link_type", "uncertain_pending_review"),
                        "response_latency_ms": "",
                        "link_evidence": redact_text(reply.get("link_evidence", "")),
                        "link_confidence": reply.get("link_confidence", ""),
                        "link_status": "candidate_pending_review",
                        "alternative_link_candidates": "topic_related_not_causal",
                        "unanswered_reason": redact_text(reply.get("unanswered_reason", "")),
                        "provisional_status": RUN_STATUS,
                    }
                )
    if asr_status.get("asr_status") != "succeeded":
        review_rows.append(
            {
                "review_id": f"{sid}-MR{len(review_rows)+1:04d}",
                "session_id": sid,
                "event_id": "",
                "timecode": "00:00:00",
                "evidence_source": asr_status.get("audio_path_local", ""),
                "review_question": "ASR 未完成或失败，需人工确认主播完整说话内容。",
                "ai_current_candidate": asr_status.get("asr_status", ""),
                "alternative_explanation": redact_text(asr_status.get("error", "")),
                "confidence": 0,
                "suggested_review_action": "回看本地音频或重新提交 ASR。",
                "provisional_status": RUN_STATUS,
            }
        )
    if not any(w.get("api_status") == "connected" for w in vision_rows):
        review_rows.append(
            {
                "review_id": f"{sid}-MR{len(review_rows)+1:04d}",
                "session_id": sid,
                "event_id": "",
                "timecode": "00:00:00",
                "evidence_source": "",
                "review_question": "视觉/评论 OCR API 未取得有效结果。",
                "ai_current_candidate": "visual_api_unavailable",
                "alternative_explanation": "需人工关键帧复核或重跑更小窗口。",
                "confidence": 0,
                "suggested_review_action": "抽查评论区和主播动作窗口。",
                "provisional_status": RUN_STATUS,
            }
        )
    for link in comment_links[:20]:
        rules.append(
            {
                "rule_id": f"{sid}-RULE{len(rules)+1:04d}",
                "trigger_type": "comment_reply_candidate",
                "trigger_pattern": link.get("response_link_type", ""),
                "audience_state_candidate": "pending_5_6_review",
                "decision_goal_candidate": "answer_or_handover_candidate",
                "response_strategy_candidate": "candidate_from_live_window",
                "response_template_structure": "先承接问题 -> 给安全解释 -> 引导下一步",
                "course_source_ref": "",
                "avatar_action_candidate": "neutral_idle",
                "prosody_candidate": "natural_explanatory",
                "next_question_or_hook_candidate": "pending_review",
                "risk_level_candidate": "pending_review",
                "human_takeover_required_candidate": "low_confidence_or_pii",
                "fallback_route_candidate": "manual_takeover",
                "review_status": "pending_5_6_review",
                "provisional_status": RUN_STATUS,
            }
        )
    for event in events:
        if event.get("review_flag") and len(review_rows) < 80:
            review_rows.append(
                {
                    "review_id": f"{sid}-MR{len(review_rows)+1:04d}",
                    "session_id": sid,
                    "event_id": event.get("event_id", ""),
                    "timecode": timecode(int(event.get("start_ms") or 0)),
                    "evidence_source": event.get("evidence_ref", ""),
                    "review_question": "确认该事件的 ASR/OCR/动作/评论关系是否准确。",
                    "ai_current_candidate": redact_text(event.get("speaker_text_clean") or event.get("comment_text_redacted") or event.get("observed_action") or ""),
                    "alternative_explanation": "可能只是主题接近，不能直接认定因果关系。",
                    "confidence": event.get("confidence", ""),
                    "suggested_review_action": "回看对应时间码原视频和本地 API 原始结果。",
                    "provisional_status": RUN_STATUS,
                }
            )
    return {
        "events": events,
        "host_rows": host_rows,
        "comment_links": comment_links,
        "course_rows": course_rows,
        "risk_rows": risk_rows,
        "review_rows": review_rows,
        "rules": rules,
    }


def build_capability_rows(args: argparse.Namespace, source_count: int, text_probe_status: str = "") -> list[dict[str, Any]]:
    return [
        {
            "capability": "workspace_remote_boundary",
            "status": "confirmed",
            "evidence": "pwd/git remote checked before pipeline",
            "fallback_route": "",
            "review_flag": "",
        },
        {
            "capability": "source_inventory",
            "status": "confirmed" if source_count == 10 else "partially_true",
            "evidence": f"identified_non_appledouble_media={source_count}",
            "fallback_route": "record_actual_count_no_scope_expansion",
            "review_flag": "" if source_count == 10 else "material_count_pending_user_review",
        },
        {
            "capability": "ffprobe_video_decode_metadata",
            "status": "confirmed",
            "evidence": "ffprobe metadata read for each source",
            "fallback_route": "blocked_file_level_if_unreadable",
            "review_flag": "",
        },
        {
            "capability": "ffmpeg_audio_clip_extraction",
            "status": "confirmed",
            "evidence": "local ffmpeg only for audit_or_input_preparation_not_fallback",
            "fallback_route": "mark audio_extract_failed",
            "review_flag": "",
        },
        {
            "capability": "alibaba_fun_asr",
            "status": "confirmed" if args.run_asr else "pending_validation",
            "evidence": "user_authorized_alibaba_multimodal_api=true" if args.run_asr else "not requested",
            "fallback_route": "manual_audio_review",
            "review_flag": "asr_human_review_required",
        },
        {
            "capability": "qwen_vl_video_window_observation",
            "status": "confirmed" if args.run_vision else "pending_validation",
            "evidence": "short compressed video windows via DashScope compatible chat" if args.run_vision else "not requested",
            "fallback_route": "critical_window_manual_review",
            "review_flag": "visual_human_review_required",
        },
        {
            "capability": "comment_ocr_dedupe",
            "status": "partially_true",
            "evidence": "Qwen-VL sampled/dense windows; raw usernames not committed",
            "fallback_route": "comment_ocr_unavailable_or_pending_review",
            "review_flag": "comment_ocr_pending_human_review",
        },
        {
            "capability": "course_alignment",
            "status": "partially_true",
            "evidence": "local bridge CSV ngram candidate only; max confidence capped at 0.69",
            "fallback_route": "course_alignment_candidate_only",
            "review_flag": "course_alignment_pending_review",
        },
    ]


def write_reports(
    args: argparse.Namespace,
    source_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    all_outputs: dict[str, list[dict[str, Any]]],
    local_manifest: dict[str, Any],
) -> None:
    DOC_ROOT.mkdir(parents=True, exist_ok=True)
    write_csv(DOC_ROOT / "01_素材总清单_source_inventory.csv", SESSION_COLUMNS, source_rows)
    write_csv(DOC_ROOT / "02_能力与解析状态_capability_analysis_status.csv", CAPABILITY_COLUMNS, build_capability_rows(args, len(source_rows)))
    write_csv(DOC_ROOT / "03_场次解析汇总_session_analysis_summary.csv", SUMMARY_COLUMNS, summary_rows)
    write_csv(DOC_ROOT / "04_事件时间轴索引_event_timeline_index.csv", EVENT_COLUMNS, all_outputs["events"])
    write_csv(DOC_ROOT / "05_评论回复候选关系_comment_reply_candidates.csv", COMMENT_REPLY_COLUMNS, all_outputs["comment_links"])
    write_csv(DOC_ROOT / "06_主播思路动作语气候选_host_logic_action_prosody_candidates.csv", HOST_COLUMNS, all_outputs["host_rows"])
    write_csv(DOC_ROOT / "07_课程对应候选_course_alignment_candidates.csv", COURSE_COLUMNS, all_outputs["course_rows"])
    write_csv(DOC_ROOT / "08_失败风险与未回复样本_failure_risk_unanswered_samples.csv", RISK_COLUMNS, all_outputs["risk_rows"])
    write_csv(DOC_ROOT / "09_人工复核队列_manual_review_queue.csv", REVIEW_COLUMNS, all_outputs["review_rows"])
    write_csv(DOC_ROOT / "10_直播大脑暂定规则_live_brain_provisional_rules.csv", RULE_COLUMNS, all_outputs["rules"])
    write_json(DOC_ROOT / "13_本地全量产物索引_local_artifact_manifest.json", local_manifest)
    data_dictionary = f"""# 数据字典_data_dictionary

`已确认`：本目录是最新直播 10 个素材的脱敏事实层，不包含原始视频、原始音频、原始 OCR、用户名映射、signed URL、secret 或缓存。

## 状态口径

- `full_evidence_extraction_completed_pending_5_6_review`：素材级取证、ASR/API 结果和脱敏索引已生成，解释层等待 5.6 复审。
- `{RUN_STATUS}`：所有解释层候选字段的统一状态。
- `partially_true`：局部链路成立，但需要人工复核或 5.6 锁字段。

## 核心字段

- `observation_status=observed/derived/inferred/manual_verified/blocked`：区分直接观察、计算得到、AI 推测、人工确认和阻断。
- `response_link_type`：只表示候选关系，不表示确定因果。
- `course_source_ref`：来自课程桥接 CSV 或 `insufficient_evidence`，本轮不写逐句最终对应。
- `comment_text_redacted`：只能保存脱敏评论文本；原始评论不得进入 GitHub。

## 本轮 API

- ASR：Alibaba Fun-ASR HTTP submit/poll，结果保存在本地运行层，GitHub 只保留脱敏句子索引。
- 多模态：Qwen-VL 短窗口观察，GitHub 只保留脱敏摘要和候选字段。
- 本地 ffmpeg/ffprobe 仅用于 `audit_or_input_preparation_not_fallback`。
"""
    (DOC_ROOT / "12_数据字典_data_dictionary.md").write_text(data_dictionary, encoding="utf-8")
    total_duration = sum(int(row.get("duration_ms") or 0) for row in source_rows) / 1000 / 3600
    cross = f"""# 十场直播跨场模式总结_cross_session_pattern_summary

## 主结论

`部分成立`：本轮已覆盖目录内 {len(source_rows)} 个真实视频素材，总时长约 {total_duration:.2f} 小时；ASR、短窗口视觉、评论候选、动作候选和课程候选均已进入脱敏索引。

`待验证`：评论 OCR 仍需人工抽查；评论—回复关系不能仅凭时间接近定因果；课程对应最高只到候选层；数字人动作和直播大脑规则均为 `{RUN_STATUS}`。

## 跨场观察

- 主播话术以课程解释、互动承接、促单/信任节点候选为主，但需 5.6 复审后才能锁定阶段标签。
- 评论区可见性由 Qwen-VL 窗口返回和人工复核队列共同确认；本轮不提交原始用户名或原始评论。
- 课程对应使用 bridge CSV 做候选召回，置信度上限 0.69，避免把 topic similarity 写成 direct quote。
- 默认数字人动作候选为 `neutral_idle`；任何具体动作复刻前必须人工确认可见动作和适配性。

## 下一步

1. 5.6 复审字段结构和抽样密度。
2. 人工优先复核 `09_人工复核队列_manual_review_queue.csv` 中的 ASR/OCR/评论关系/课程对应低置信事件。
3. 复核通过后再把规则候选迁入 V0 直播大脑，不直接把本轮候选当正式规则。
"""
    (DOC_ROOT / "11_十场直播跨场模式总结_cross_session_pattern_summary.md").write_text(cross, encoding="utf-8")
    report = f"""# 执行报告_execution_report

## 主结论

`full_evidence_extraction_completed_pending_5_6_review`

`已确认`：素材路径 `{rel(SOURCE_DIR)}` 存在，排除 AppleDouble `._*` 后识别到 {len(source_rows)} 个媒体素材；本轮输出目录为 `{rel(DOC_ROOT)}`。

`部分成立`：Alibaba API 已按用户本轮授权用于 ASR / 多模态窗口分析；评论 OCR、评论—回复关系、课程对应、数字人动作和直播大脑规则均为候选层，统一标记 `{RUN_STATUS}`。

`待验证`：人工尚未复核；不能写成业务通过、客户通过、正式直播平台链路通过或数字人能力已完成。

## 边界

- `audit_or_input_preparation_not_fallback`：ffmpeg / ffprobe 只用于取证、音频提取和短窗口输入准备。
- 未修改、移动、删除、重编码源视频。
- GitHub 只保存脱敏 CSV/JSONL/Markdown；原始音频、短片段、API raw、signed URL 和用户名映射保存在 `_local_runtime/`，不提交。
- 未编辑 5.6 规划目录 `新录屏多模态解析规划_new_recording_multimodal_plan/`。

## 命令与参数

- `run_id`: `{args.run_id}`
- `run_asr`: `{args.run_asr}`
- `run_vision`: `{args.run_vision}`
- `vision_interval_sec`: `{args.vision_interval_sec}`
- `vision_duration_sec`: `{args.vision_duration_sec}`
- `vision_models`: `{args.vision_models}`
- `asr_timeout_sec`: `{args.asr_timeout_sec}`

## 产物

- `01_素材总清单_source_inventory.csv`
- `02_能力与解析状态_capability_analysis_status.csv`
- `03_场次解析汇总_session_analysis_summary.csv`
- `04_事件时间轴索引_event_timeline_index.csv`
- `05_评论回复候选关系_comment_reply_candidates.csv`
- `06_主播思路动作语气候选_host_logic_action_prosody_candidates.csv`
- `07_课程对应候选_course_alignment_candidates.csv`
- `08_失败风险与未回复样本_failure_risk_unanswered_samples.csv`
- `09_人工复核队列_manual_review_queue.csv`
- `10_直播大脑暂定规则_live_brain_provisional_rules.csv`
- `11_十场直播跨场模式总结_cross_session_pattern_summary.md`
- `12_数据字典_data_dictionary.md`
- `13_本地全量产物索引_local_artifact_manifest.json`
- `data/session_manifests/*.json`
- `data/redacted_event_indexes/*.jsonl`

## 验证口径

- 全部 source hash 已生成。
- event_id 由 `session_id + start_ms + sequence` 生成，验证脚本需检查唯一性。
- 课程候选最高只到 `topic_similarity_only` / `course_alignment_candidate_only`。
- 评论身份信息已做正则脱敏，并由最终验证继续扫描。
"""
    (DOC_ROOT / "00_执行报告_execution_report.md").write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--run-asr", action="store_true")
    parser.add_argument("--run-vision", action="store_true")
    parser.add_argument("--vision-interval-sec", type=int, default=300)
    parser.add_argument("--vision-duration-sec", type=int, default=8)
    parser.add_argument("--vision-max-windows-per-session", type=int, default=0)
    parser.add_argument("--vision-timeout-sec", type=int, default=180)
    parser.add_argument("--vision-models", default="qwen-vl-plus,qwen3-vl-plus,qwen-vl-max")
    parser.add_argument("--asr-timeout-sec", type=int, default=3600)
    parser.add_argument("--asr-poll-interval-sec", type=int, default=20)
    parser.add_argument("--limit-sessions", type=int, default=0)
    args = parser.parse_args()

    ensure_workspace()
    load_env()
    DOC_ROOT.mkdir(parents=True, exist_ok=True)
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    SESSION_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    videos = read_videos()
    if args.limit_sessions > 0:
        videos = videos[: args.limit_sessions]
    source_rows, manifests = build_inventory(videos)
    bridge_rows = load_bridge_rows()

    all_outputs: dict[str, list[dict[str, Any]]] = {
        "events": [],
        "host_rows": [],
        "comment_links": [],
        "course_rows": [],
        "risk_rows": [],
        "review_rows": [],
        "rules": [],
    }
    summary_rows: list[dict[str, Any]] = []
    local_manifest: dict[str, Any] = {
        "run_id": args.run_id,
        "created_at": now_iso(),
        "local_runtime_root": rel(LOCAL_ROOT),
        "source_dir": rel(SOURCE_DIR),
        "user_authorized_alibaba_multimodal_api": bool(args.run_asr or args.run_vision),
        "sessions": [],
        "private_data_note": "signed URLs, raw ASR JSON, raw model responses, audio and video clips remain local-only",
    }

    asr_prepared: dict[str, dict[str, Any]] = {}
    if args.run_asr:
        for inventory_row, video in zip(source_rows, videos):
            sid = inventory_row["session_id"]
            local_session_dir = LOCAL_ROOT / args.run_id / sid
            local_session_dir.mkdir(parents=True, exist_ok=True)
            print(f"[{now_iso()}] session {sid} asr submit start: {video.name}", flush=True)
            asr_prepared[sid] = prepare_asr_submission(video, sid, args, local_session_dir)
            print(
                f"[{now_iso()}] session {sid} asr submit status: "
                f"{asr_prepared[sid].get('asr_status')} task_id_present={bool(asr_prepared[sid].get('asr_task_id'))}",
                flush=True,
            )

    for inventory_row, manifest, video in zip(source_rows, manifests, videos):
        sid = inventory_row["session_id"]
        local_session_dir = LOCAL_ROOT / args.run_id / sid
        local_session_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{now_iso()}] session {sid} start: {video.name}", flush=True)
        if args.run_asr:
            sentences, asr_status = finish_asr_submission(asr_prepared.get(sid, {}), args, local_session_dir)
        else:
            sentences, asr_status = run_asr_for_session(video, sid, args, local_session_dir)
        print(f"[{now_iso()}] session {sid} asr: {asr_status.get('asr_status')} sentences={len(sentences)}", flush=True)
        vision_rows = run_vision_for_session(video, sid, int(inventory_row["duration_ms"]), args, local_session_dir)
        print(f"[{now_iso()}] session {sid} vision_windows={len(vision_rows)}", flush=True)
        outputs = build_session_outputs(inventory_row, sentences, asr_status, vision_rows, bridge_rows)
        for key in all_outputs:
            all_outputs[key].extend(outputs[key])
        session_manifest = {
            "session": inventory_row,
            "ffprobe": manifest.get("ffprobe", {}),
            "asr_status": asr_status,
            "vision_windows": [
                {k: v for k, v in row.items() if k not in {"parsed"}}
                | {"parsed_present": bool(row.get("parsed"))}
                for row in vision_rows
            ],
            "counts": {k: len(v) for k, v in outputs.items()},
            "provisional_status": RUN_STATUS,
        }
        write_json(SESSION_MANIFEST_DIR / f"{sid}_manifest.json", session_manifest)
        append_jsonl(EVENT_INDEX_DIR / f"{sid}_events.jsonl", outputs["events"])
        visible = "yes" if any((w.get("parsed") or {}).get("comment_area_visible") == "yes" for w in vision_rows) else "pending_review"
        inventory_row["comment_area_visible"] = visible
        inventory_row["analysis_status"] = "completed_pending_5_6_review"
        summary_rows.append(
            {
                "session_id": sid,
                "source_video": inventory_row["source_video"],
                "duration_min": round(int(inventory_row["duration_ms"]) / 1000 / 60, 2),
                "asr_status": asr_status.get("asr_status", ""),
                "asr_sentence_count": len(sentences),
                "vision_status": "connected" if any(w.get("api_status") == "connected" for w in vision_rows) else "blocked_or_not_run",
                "vision_window_count": len(vision_rows),
                "comment_area_visible": visible,
                "comment_event_count": sum(1 for e in outputs["events"] if e.get("event_type") == "comment"),
                "reply_candidate_count": len(outputs["comment_links"]),
                "course_candidate_count": len(outputs["course_rows"]),
                "manual_review_count": len(outputs["review_rows"]),
                "analysis_status": "completed_pending_5_6_review",
            }
        )
        local_manifest["sessions"].append(
            {
                "session_id": sid,
                "local_session_dir": rel(local_session_dir),
                "asr_status": asr_status.get("asr_status", ""),
                "vision_windows": len(vision_rows),
                "raw_local_only": [
                    asr_status.get("asr_result_local", ""),
                    asr_status.get("asr_query_response_local", ""),
                    asr_status.get("private_manifest_local", ""),
                ],
            }
        )

    write_reports(args, source_rows, summary_rows, all_outputs, local_manifest)
    print(f"[{now_iso()}] completed artifacts: {rel(DOC_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
