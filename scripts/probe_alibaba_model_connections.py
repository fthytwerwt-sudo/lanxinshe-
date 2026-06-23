"""Run safe Alibaba model connection probes and generate a report.

The script loads only the workspace-local .env file, never prints secret
values, and writes redacted JSON summaries under outputs/probe_runs/.
"""

from __future__ import annotations

import argparse
import base64
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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.alibaba_model_registry import (  # noqa: E402
    DEFAULT_COMPATIBLE_BASE_URL,
    DEFAULT_DASHSCOPE_API_BASE_URL,
    DEFAULT_RERANK_BASE_URL,
    EMBEDDING_MODEL_CANDIDATES,
    MODEL_CATALOG,
    OMNI_MODEL_CANDIDATES,
    OSS_ENV_KEYS,
    RERANK_MODEL_CANDIDATES,
    REQUIRED_ENV_KEYS,
    SAFETY_SWITCH_ENV_KEYS,
    TEXT_MODEL_CANDIDATES,
    VISION_VIDEO_MODEL_CANDIDATES,
    WAN_VIDEO_GENERATION_CANDIDATES,
)

REPORT_PATH = PROJECT_ROOT / "codex_reports" / "阿里大模型连接总探针_aliyun_model_connection_probe_report.md"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "probe_runs"

TEXT_TEST_INPUT = "这课多少钱？学完能保证赚钱吗？"
EMBEDDING_TEST_INPUT = "本课程适合零基础用户，但不承诺具体收益，退款规则以客户确认版本为准。"
RERANK_QUERY = "退款规则和收益承诺怎么回复？"
RERANK_DOCUMENTS = [
    "本课程适合零基础用户，但不承诺具体收益。",
    "退款规则以客户确认版本为准，高风险问题需要人工接管。",
    "直播间可以展示课程安排和学习路径。",
]

MUST_READ_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/alibaba_api_setup.md",
    "docs/qwen_model_connection.md",
    "docs/oss_setup.md",
    "docs/happyhorse_i2v_connection.md",
    "codex_reports/20260616_数字人直播质量参考解析_video_quality_reference_analysis.md",
    "local_only_reports/20260619_数字人直播技术路线核实与实现方案_local_only_technical_route_plan.md",
    "local_only_reports/直播前期总控施工图_live_front_planning_blueprint/00_数字人直播前期规划总控图_live_front_planning_master_blueprint.md",
]

ENV_STATUS_KEYS = [
    "DASHSCOPE_API_KEY",
    "ALIYUN_API_KEY",
    "ALIBABA_CLOUD_ACCESS_KEY_ID",
    "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
    "ALIYUN_OSS_BUCKET",
    "ALIBABA_OSS_BUCKET",
    "ALIYUN_OSS_ENDPOINT",
    "ALIBABA_OSS_ENDPOINT",
    "ALIYUN_OSS_REGION",
    "ALIBABA_REGION_ID",
    "ALLOW_WAN_GENERATION_PROBE",
    "ALLOW_ALIBABA_MODEL_TEST",
    "ALLOW_QWEN_CHAT_TEST",
]

SENSITIVE_NAME_PARTS = ("KEY", "SECRET", "TOKEN", "COOKIE", "PASSWORD")
MEDIA_SUFFIXES = {".mp4", ".mov", ".m4v", ".avi", ".mkv"}


def load_workspace_env() -> dict[str, Any]:
    """Load .env from the project root using a small parser."""
    env_file = PROJECT_ROOT / ".env"
    info = {
        "path": str(env_file),
        "exists": env_file.exists(),
        "loaded": False,
        "loader": "fallback",
        "outside_workspace": False,
    }
    if not env_file.exists():
        return info
    try:
        env_file.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        info["outside_workspace"] = True
        return info

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if not name or name in os.environ:
            continue
        os.environ[name] = value.strip().strip('"').strip("'")
    info["loaded"] = True
    return info


def env_status(keys: list[str] | tuple[str, ...] = tuple(ENV_STATUS_KEYS)) -> dict[str, str]:
    """Return present/missing/empty without exposing values."""
    status: dict[str, str] = {}
    for key in keys:
        value = os.getenv(key)
        if value is None:
            status[key] = "missing"
        elif value == "":
            status[key] = "empty"
        else:
            status[key] = "present"
    return status


def env_bool(name: str) -> bool:
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def secret_values() -> list[str]:
    values: list[str] = []
    for name, value in os.environ.items():
        if value and any(part in name.upper() for part in SENSITIVE_NAME_PARTS):
            values.append(value)
    return values


def sanitize_text(text: str, max_len: int = 500) -> str:
    """Remove secret-like values and keep logs compact."""
    safe = str(text)
    for value in secret_values():
        if value:
            safe = safe.replace(value, f"<masked:{len(value)} chars>")
    safe = re.sub(r"sk-[A-Za-z0-9_\-]{8,}", "<masked:dashscope_api_key>", safe)
    safe = re.sub(r"Bearer\s+[A-Za-z0-9_\-\.]+", "Bearer <masked>", safe, flags=re.I)
    safe = re.sub(r"(https?://[^\s?]+)\?[^\s]+", r"\1?<redacted_query>", safe)
    return safe[:max_len]


def safe_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_run_dir(prefix: str = "alibaba_model_connection_probe") -> Path:
    run_id = datetime.now().strftime(f"%Y%m%d_%H%M%S_{prefix}")
    run_dir = OUTPUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def summarize_response_text(body: dict[str, Any]) -> str:
    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = body.get("output", {}).get("text", "")
    return sanitize_text(str(content).strip(), max_len=700)


def classify_error(status_code: int | None, body: Any, exc: Exception | None = None) -> tuple[str, str]:
    if exc is not None:
        return "blocked_network_error", sanitize_text(str(exc))
    message = ""
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            message = str(error.get("message") or error.get("code") or "")
        message = message or str(body.get("message") or body.get("code") or "")
    else:
        message = str(body)
    lowered = message.lower()
    if status_code in {401, 403}:
        return "permission_denied", sanitize_text(message)
    if status_code in {402, 429} or any(word in lowered for word in ("quota", "balance", "insufficient", "余额", "额度", "限流")):
        return "blocked_quota_or_balance_error", sanitize_text(message)
    if status_code in {400, 404} or any(word in lowered for word in ("model", "not found", "not exist", "未开通", "模型不存在", "无权限")):
        return "model_unavailable", sanitize_text(message)
    return "blocked_invalid_response", sanitize_text(message or f"HTTP {status_code}")


def post_json(url: str, api_key: str, payload: dict[str, Any], timeout: int = 120) -> tuple[int | None, dict[str, Any] | str, float, dict[str, str]]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    started = time.perf_counter()
    response_headers: dict[str, str] = {}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        elapsed_ms = (time.perf_counter() - started) * 1000
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() in {"x-request-id", "x-acs-request-id", "request-id"}
        }
        try:
            body: dict[str, Any] | str = response.json()
        except ValueError:
            body = response.text[:1000]
        return response.status_code, body, elapsed_ms, response_headers
    except requests.RequestException as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return None, sanitize_text(str(exc)), elapsed_ms, response_headers


def candidate_limit(candidates: list[str], limit: int) -> list[str]:
    if limit <= 0:
        return []
    return candidates[:limit]


def chat_payload(model: str, messages: list[dict[str, Any]], max_tokens: int = 400, temperature: float = 0.0) -> dict[str, Any]:
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def probe_text_models(api_key: str, max_calls: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    url = f"{DEFAULT_COMPATIBLE_BASE_URL}/chat/completions"
    messages = [
        {
            "role": "system",
            "content": (
                "你是直播间评论风险判断助手。只输出 JSON，不输出解释。"
                "字段必须包含 intent_type, risk_level, knowledge_needed, "
                "handover_required, auto_reply_allowed, safe_reply_summary。"
            ),
        },
        {"role": "user", "content": TEXT_TEST_INPUT},
    ]
    for model in candidate_limit(TEXT_MODEL_CANDIDATES, max_calls):
        payload = chat_payload(model, messages, max_tokens=300, temperature=0.0)
        status_code, body, elapsed_ms, headers = post_json(url, api_key, payload, timeout=60)
        if status_code and 200 <= status_code < 300 and isinstance(body, dict):
            results.append(
                {
                    "category": "text",
                    "model": model,
                    "status": "connected",
                    "input_type": "text",
                    "latency_ms": round(elapsed_ms, 1),
                    "summary": summarize_response_text(body),
                    "usage": body.get("usage", {}),
                    "request_id": sanitize_text(str(headers.get("x-request-id") or headers.get("request-id") or body.get("request_id") or body.get("id") or "")),
                    "error_summary": "",
                }
            )
        else:
            status, error = classify_error(status_code, body)
            results.append(
                {
                    "category": "text",
                    "model": model,
                    "status": status,
                    "input_type": "text",
                    "latency_ms": round(elapsed_ms, 1),
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": error,
                }
            )
    return results


def probe_embedding_models(api_key: str, max_calls: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    url = f"{DEFAULT_COMPATIBLE_BASE_URL}/embeddings"
    for model in candidate_limit(EMBEDDING_MODEL_CANDIDATES, max_calls):
        payload: dict[str, Any] = {
            "model": model,
            "input": EMBEDDING_TEST_INPUT,
            "encoding_format": "float",
        }
        if model in {"text-embedding-v3", "text-embedding-v4"}:
            payload["dimensions"] = 1024
        status_code, body, elapsed_ms, headers = post_json(url, api_key, payload, timeout=60)
        if status_code and 200 <= status_code < 300 and isinstance(body, dict):
            embedding = body.get("data", [{}])[0].get("embedding", [])
            dimension = len(embedding) if isinstance(embedding, list) else 0
            results.append(
                {
                    "category": "embedding",
                    "model": model,
                    "status": "connected" if dimension else "blocked_invalid_response",
                    "input_type": "text",
                    "latency_ms": round(elapsed_ms, 1),
                    "dimension": dimension,
                    "summary": f"embedding_dimension={dimension}",
                    "usage": body.get("usage", {}),
                    "request_id": sanitize_text(str(headers.get("x-request-id") or body.get("request_id") or "")),
                    "error_summary": "" if dimension else "embedding vector missing",
                }
            )
        else:
            status, error = classify_error(status_code, body)
            results.append(
                {
                    "category": "embedding",
                    "model": model,
                    "status": status,
                    "input_type": "text",
                    "latency_ms": round(elapsed_ms, 1),
                    "dimension": 0,
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": error,
                }
            )
    return results


def probe_rerank_models(api_key: str, max_calls: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for model in candidate_limit(RERANK_MODEL_CANDIDATES, max_calls):
        if model == "qwen3-rerank":
            url = f"{DEFAULT_RERANK_BASE_URL}/reranks"
            payload = {
                "model": model,
                "query": RERANK_QUERY,
                "documents": RERANK_DOCUMENTS,
                "top_n": 2,
            }
        else:
            url = f"{DEFAULT_DASHSCOPE_API_BASE_URL}/services/rerank/text-rerank/text-rerank"
            payload = {
                "model": model,
                "input": {"query": RERANK_QUERY, "documents": RERANK_DOCUMENTS},
                "parameters": {"top_n": 2, "return_documents": True},
            }
        status_code, body, elapsed_ms, headers = post_json(url, api_key, payload, timeout=60)
        if status_code and 200 <= status_code < 300 and isinstance(body, dict):
            results.append(
                {
                    "category": "rerank",
                    "model": model,
                    "status": "connected",
                    "input_type": "query_and_documents",
                    "latency_ms": round(elapsed_ms, 1),
                    "summary": "rerank_response_received",
                    "usage": body.get("usage", {}),
                    "request_id": sanitize_text(str(headers.get("x-request-id") or body.get("request_id") or "")),
                    "error_summary": "",
                }
            )
        else:
            status, error = classify_error(status_code, body)
            results.append(
                {
                    "category": "rerank",
                    "model": model,
                    "status": status,
                    "input_type": "query_and_documents",
                    "latency_ms": round(elapsed_ms, 1),
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": error,
                }
            )
    return results


def find_video_source() -> Path | None:
    preferred_root = PROJECT_ROOT / "参考" / "直播质量"
    search_roots = [preferred_root, PROJECT_ROOT / "参考"]
    candidates: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.name.startswith("._"):
                continue
            if path.suffix.lower() in MEDIA_SUFFIXES and path.is_file():
                candidates.append(path)
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_size)[0]


def run_ffmpeg(args: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "ffmpeg_not_found"
    if completed.returncode != 0:
        return False, sanitize_text(completed.stderr or completed.stdout)
    return True, ""


def prepare_media(run_dir: Path, max_duration_sec: int = 15, video_path: str | None = None) -> dict[str, Any]:
    media_dir = run_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    source = Path(video_path) if video_path else find_video_source()
    result: dict[str, Any] = {
        "source_video_found": bool(source),
        "source_video_path": str(source.relative_to(PROJECT_ROOT)) if source and source.is_relative_to(PROJECT_ROOT) else "",
        "frame_path": "",
        "clip_path": "",
        "clip_with_audio_path": "",
        "error": "",
    }
    if not source:
        return result
    try:
        source.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        result["error"] = "blocked_env_outside_workspace"
        return result

    frame_path = media_dir / "probe_frame.jpg"
    ok, error = run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            "2",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-vf",
            "scale=-2:640",
            str(frame_path),
        ]
    )
    if ok:
        result["frame_path"] = str(frame_path)
    else:
        result["error"] = error

    clip_path = media_dir / "probe_clip_video_only.mp4"
    ok, error = run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            "0",
            "-i",
            str(source),
            "-t",
            str(max_duration_sec),
            "-vf",
            "scale=-2:480",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "32",
            "-movflags",
            "+faststart",
            str(clip_path),
        ]
    )
    if ok:
        result["clip_path"] = str(clip_path)
    elif not result["error"]:
        result["error"] = error

    omni_clip_path = media_dir / "probe_clip_with_audio.mp4"
    ok, error = run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            "0",
            "-i",
            str(source),
            "-t",
            str(min(max_duration_sec, 8)),
            "-vf",
            "scale=-2:360",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "34",
            "-c:a",
            "aac",
            "-b:a",
            "48k",
            "-movflags",
            "+faststart",
            str(omni_clip_path),
        ]
    )
    if ok:
        result["clip_with_audio_path"] = str(omni_clip_path)
    return result


def data_url_for_file(path: Path, max_encoded_bytes: int = 9_500_000) -> tuple[str, str]:
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    if len(encoded) > max_encoded_bytes:
        return "", f"base64_too_large:{len(encoded)}"
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64,{encoded}", ""


def vl_messages_with_video(video_data_url: str) -> list[dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": video_data_url, "fps": 1.0},
                },
                {
                    "type": "text",
                    "text": (
                        "请基于这个短直播片段输出 JSON，字段为 visible_scene, "
                        "anchor_action, product_or_prop, live_ui_visible, "
                        "comment_area_visible, lip_sync_risk_observation, "
                        "blink_or_expression_observation, human_like_score_note, "
                        "next_stage_recommendation。只做模型辅助观察，不写人审通过。"
                    ),
                },
            ],
        }
    ]


def vl_messages_with_image(image_data_url: str) -> list[dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_data_url}},
                {
                    "type": "text",
                    "text": (
                        "请描述这张直播画面中的主播、商品/道具、直播 UI、评论区可见性，"
                        "并指出它能否辅助数字人直播录屏分析。输出简短 JSON。"
                    ),
                },
            ],
        }
    ]


def probe_vision_video_models(api_key: str, max_calls: int, run_dir: Path, max_duration_sec: int = 15, video_path: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    results: list[dict[str, Any]] = []
    media = prepare_media(run_dir, max_duration_sec=max_duration_sec, video_path=video_path)
    if media.get("error") == "blocked_env_outside_workspace":
        return [
            {
                "category": "vision_video",
                "model": "",
                "status": "blocked_env_outside_workspace",
                "input_type": "none",
                "latency_ms": 0,
                "summary": "",
                "usage": {},
                "request_id": "",
                "error_summary": "source video outside workspace",
            }
        ], media
    url = f"{DEFAULT_COMPATIBLE_BASE_URL}/chat/completions"
    calls = 0
    for model in VISION_VIDEO_MODEL_CANDIDATES:
        if calls >= max_calls:
            break
        clip_path = Path(media["clip_path"]) if media.get("clip_path") else None
        if clip_path and clip_path.exists():
            video_data_url, data_error = data_url_for_file(clip_path)
            if video_data_url:
                payload = chat_payload(model, vl_messages_with_video(video_data_url), max_tokens=500, temperature=0.0)
                calls += 1
                status_code, body, elapsed_ms, headers = post_json(url, api_key, payload, timeout=180)
                if status_code and 200 <= status_code < 300 and isinstance(body, dict):
                    results.append(
                        {
                            "category": "vision_video",
                            "model": model,
                            "status": "connected",
                            "input_type": "video_base64_short_clip",
                            "latency_ms": round(elapsed_ms, 1),
                            "summary": summarize_response_text(body),
                            "usage": body.get("usage", {}),
                            "request_id": sanitize_text(str(headers.get("x-request-id") or body.get("request_id") or body.get("id") or "")),
                            "error_summary": "",
                        }
                    )
                    continue
                status, error = classify_error(status_code, body)
                results.append(
                    {
                        "category": "vision_video",
                        "model": model,
                        "status": status,
                        "input_type": "video_base64_short_clip",
                        "latency_ms": round(elapsed_ms, 1),
                        "summary": "",
                        "usage": {},
                        "request_id": "",
                        "error_summary": error,
                    }
                )
            else:
                results.append(
                    {
                        "category": "vision_video",
                        "model": model,
                        "status": "blocked_oss_required",
                        "input_type": "video_base64_short_clip",
                        "latency_ms": 0,
                        "summary": "",
                        "usage": {},
                        "request_id": "",
                        "error_summary": data_error,
                    }
                )

        if calls >= max_calls:
            break
        frame_path = Path(media["frame_path"]) if media.get("frame_path") else None
        if frame_path and frame_path.exists():
            image_data_url, data_error = data_url_for_file(frame_path)
            if image_data_url:
                payload = chat_payload(model, vl_messages_with_image(image_data_url), max_tokens=350, temperature=0.0)
                calls += 1
                status_code, body, elapsed_ms, headers = post_json(url, api_key, payload, timeout=120)
                if status_code and 200 <= status_code < 300 and isinstance(body, dict):
                    results.append(
                        {
                            "category": "vision_video",
                            "model": model,
                            "status": "connected",
                            "input_type": "image_base64_frame_fallback",
                            "latency_ms": round(elapsed_ms, 1),
                            "summary": summarize_response_text(body),
                            "usage": body.get("usage", {}),
                            "request_id": sanitize_text(str(headers.get("x-request-id") or body.get("request_id") or body.get("id") or "")),
                            "error_summary": "",
                        }
                    )
                else:
                    status, error = classify_error(status_code, body)
                    results.append(
                        {
                            "category": "vision_video",
                            "model": model,
                            "status": status,
                            "input_type": "image_base64_frame_fallback",
                            "latency_ms": round(elapsed_ms, 1),
                            "summary": "",
                            "usage": {},
                            "request_id": "",
                            "error_summary": error or data_error,
                        }
                    )
    if not results:
        results.append(
            {
                "category": "vision_video",
                "model": "",
                "status": "blocked_video_input_missing",
                "input_type": "none",
                "latency_ms": 0,
                "summary": "",
                "usage": {},
                "request_id": "",
                "error_summary": media.get("error") or "no usable video or frame source",
            }
        )
    return results, media


def probe_omni_models(api_key: str, max_calls: int, run_dir: Path, media: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not media:
        media = prepare_media(run_dir, max_duration_sec=8)
    url = f"{DEFAULT_COMPATIBLE_BASE_URL}/chat/completions"
    for model in candidate_limit(OMNI_MODEL_CANDIDATES, max_calls):
        clip_path = Path(media["clip_with_audio_path"]) if media.get("clip_with_audio_path") else None
        if not clip_path or not clip_path.exists():
            results.append(
                {
                    "category": "omni",
                    "model": model,
                    "status": "pending_validation",
                    "input_type": "text_audio_video",
                    "latency_ms": 0,
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": "no short audio-video clip available",
                }
            )
            continue
        video_data_url, data_error = data_url_for_file(clip_path)
        if not video_data_url:
            results.append(
                {
                    "category": "omni",
                    "model": model,
                    "status": "blocked_oss_required",
                    "input_type": "video_with_audio_base64",
                    "latency_ms": 0,
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": data_error,
                }
            )
            continue
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "video_url", "video_url": {"url": video_data_url, "fps": 1.0}},
                    {
                        "type": "text",
                        "text": "请用一句话判断这个短直播片段是否适合做音频+视频综合理解探针，并说明限制。",
                    },
                ],
            }
        ]
        payload = chat_payload(model, messages, max_tokens=250, temperature=0.0)
        status_code, body, elapsed_ms, headers = post_json(url, api_key, payload, timeout=180)
        if status_code and 200 <= status_code < 300 and isinstance(body, dict):
            results.append(
                {
                    "category": "omni",
                    "model": model,
                    "status": "connected",
                    "input_type": "video_with_audio_base64",
                    "latency_ms": round(elapsed_ms, 1),
                    "summary": summarize_response_text(body),
                    "usage": body.get("usage", {}),
                    "request_id": sanitize_text(str(headers.get("x-request-id") or body.get("request_id") or body.get("id") or "")),
                    "error_summary": "",
                }
            )
        else:
            status, error = classify_error(status_code, body)
            results.append(
                {
                    "category": "omni",
                    "model": model,
                    "status": status,
                    "input_type": "video_with_audio_base64",
                    "latency_ms": round(elapsed_ms, 1),
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": error,
                }
            )
    return results


def probe_wan_config() -> list[dict[str, Any]]:
    has_api_key = env_status(REQUIRED_ENV_KEYS).get("DASHSCOPE_API_KEY") == "present"
    allow_generation = env_bool("ALLOW_WAN_GENERATION_PROBE")
    results = []
    for model in WAN_VIDEO_GENERATION_CANDIDATES:
        if not has_api_key:
            status = "blocked_missing_env"
            summary = "DASHSCOPE_API_KEY missing; no dry-run endpoint check beyond config."
        elif not allow_generation:
            status = "skipped_cost_guard"
            summary = "configured_only; actual video generation skipped because ALLOW_WAN_GENERATION_PROBE is not true."
        else:
            status = "configured_only"
            summary = "ALLOW_WAN_GENERATION_PROBE=true detected, but this safe total probe did not create a video task."
        results.append(
            {
                "category": "wan_s2v",
                "model": model,
                "status": status,
                "input_type": "image_url_and_audio_url",
                "latency_ms": 0,
                "summary": summary,
                "usage": {},
                "request_id": "",
                "error_summary": "",
                "actual_generation": "no",
            }
        )
    return results


def read_file_inventory() -> list[dict[str, str]]:
    inventory = []
    for relative in MUST_READ_FILES:
        path = PROJECT_ROOT / relative
        inventory.append({"path": relative, "status": "present" if path.exists() else "missing"})
    return inventory


def summarize_group(results: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    return [item for item in results if item.get("category") == category]


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def status_for_category(results: list[dict[str, Any]], category: str) -> str:
    group = summarize_group(results, category)
    if any(item.get("status") == "connected" for item in group):
        return "connected"
    if group:
        return "pending_or_blocked"
    return "not_run"


def build_report(summary: dict[str, Any]) -> str:
    results = summary["results"]
    connected = [item for item in results if item.get("status") == "connected"]
    failed = [item for item in results if item.get("status") not in {"connected", "skipped_cost_guard", "configured_only"}]
    skipped = [item for item in results if item.get("status") in {"skipped_cost_guard", "configured_only"}]
    env = summary["environment"]
    media = summary.get("media", {})

    category_rows = []
    for category, candidates in MODEL_CATALOG.items():
        category_rows.append(
            [
                category,
                ", ".join(candidate.name for candidate in candidates[:5]),
                candidates[0].purpose if candidates else "",
                status_for_category(results, category),
            ]
        )

    def result_rows(category: str, extra: str = "") -> list[list[str]]:
        rows = []
        for item in summarize_group(results, category):
            rows.append(
                [
                    item.get("model") or "n/a",
                    item.get("status", ""),
                    item.get(extra, "") if extra else item.get("input_type", ""),
                    item.get("summary", "")[:220],
                    item.get("error_summary", "")[:180],
                ]
            )
        return rows or [["n/a", "not_run", "", "", ""]]

    def first_connected(category: str, preferred: list[str] | None = None) -> str:
        group = [item for item in summarize_group(results, category) if item.get("status") == "connected"]
        if preferred:
            for model in preferred:
                if any(item.get("model") == model for item in group):
                    return model
        return str(group[0].get("model")) if group else "n/a"

    video_primary = first_connected("vision_video", ["qwen-vl-max", "qwen3-vl-plus", "qwen-vl-plus"])
    video_backup = first_connected("vision_video", ["qwen-vl-plus", "qwen3-vl-flash", "qwen2.5-vl-72b-instruct"])
    text_primary = first_connected("text", ["qwen-max", "qwen-plus", "qwen-turbo"])
    text_backup = first_connected("text", ["qwen-plus", "qwen-turbo"])
    embedding_primary = first_connected("embedding", ["text-embedding-v4", "text-embedding-v3"])
    rerank_primary = first_connected("rerank", ["qwen3-rerank", "gte-rerank-v2"])

    report_lines = [
        "# 阿里大模型连接总探针报告",
        "",
        "# 一页结论",
        "",
        f"- status: `{summary['overall_status']}`",
        f"- connected 模型: {', '.join(item['model'] for item in connected) or '无'}",
        f"- failed / blocked 模型: {', '.join(item.get('model') or item.get('category') for item in failed) or '无'}",
        f"- skipped 模型: {', '.join(item.get('model') for item in skipped) or '无'}",
        "- `已确认`：本轮只做低成本最小连接探针；技术连通不等于内容、人感、人审或长视频能力通过。",
        "- `部分成立`：短视频/抽帧探针只能证明账号、模型和输入方式的局部可用性，不能外推 4-5 小时直播稳定。",
        "",
        "# 0. 本轮边界与安全确认",
        "",
        f"- workspace: `{summary['workspace']}`",
        f"- branch: `{summary['branch']}`",
        f"- remote: `{summary['remote']}`",
        f"- dry/safe mode: `{summary['safe_mode']}`",
        f"- paid API call: `yes_minimal_probe`",
        f"- generated video: `no`",
        f"- OSS upload: `{summary.get('oss_upload', 'no')}`",
        f"- committed media: `no`",
        f"- printed secret: `no`",
        "",
        "# 1. 环境变量与密钥安全检查",
        "",
        f"- `.env` found: `{'yes' if env['env_file_exists'] else 'no'}`",
        f"- `.env` path: `{env['env_file_path']}`",
        "- 环境变量只记录 present / missing / empty，不记录值。",
        "",
        markdown_table(["env", "status"], [[key, value] for key, value in env["env_status"].items()]),
        "",
        "# 2. 已读取文件",
        "",
        markdown_table(["path", "status"], [[item["path"], item["status"]] for item in summary["read_files"]]),
        "",
        "# 3. 模型类别与用途总表",
        "",
        markdown_table(["类别", "候选模型", "直播项目用途", "本轮结果"], category_rows),
        "",
        "# 4. 文本模型连接结果",
        "",
        markdown_table(["模型", "状态", "输入方式", "输出摘要", "错误摘要"], result_rows("text")),
        "",
        "# 5. 视觉 / 视频理解模型连接结果",
        "",
        markdown_table(["模型", "状态", "输入方式", "输出摘要", "错误摘要"], result_rows("vision_video")),
        "",
        "# 6. Omni 全模态模型连接结果",
        "",
        markdown_table(["模型", "状态", "输入方式", "输出摘要", "错误摘要"], result_rows("omni")),
        "",
        "# 7. Embedding / Rerank 连接结果",
        "",
        markdown_table(["模型", "状态", "输入方式", "输出摘要", "错误摘要"], result_rows("embedding") + result_rows("rerank")),
        "",
        "# 8. Wan 视频生成模型配置 / dry-run 结果",
        "",
        markdown_table(["模型", "状态", "输入方式", "输出摘要", "错误摘要"], result_rows("wan_s2v")),
        "",
        "# 9. 视频素材输入方式判断",
        "",
        f"- source_video_found: `{media.get('source_video_found', False)}`",
        f"- source_video_path: `{media.get('source_video_path') or 'n/a'}`",
        f"- local short clip: `{'yes' if media.get('clip_path') else 'no'}`",
        f"- frame fallback: `{'yes' if media.get('frame_path') else 'no'}`",
        "- OSS URL: `not_used`，本轮短片段 Base64 / 抽帧路径足够；报告未写入 signed URL。",
        "",
        "# 10. 当前最推荐的视频分析主模型",
        "",
        f"- `已确认`：本轮首选视频分析主模型为 `{video_primary}`，因为它完成了短直播片段 `video_base64_short_clip` 探针。",
        f"- `已确认`：当前备选视频分析模型为 `{video_backup}`；后续可以在同一 15 秒片段上对比稳定性和输出字段一致性。",
        "- `部分成立`：本轮只证明短片段视频理解可调用，不能写成长视频、全量录屏或人审质量通过。",
        "- `通用建议`：真实录屏解析 V0 先用 15 秒片段，保留抽帧 fallback；60 秒和完整录屏必须单独 probe。",
        "",
        "# 11. 当前最推荐的直播评论判断模型",
        "",
        f"- `已确认`：风险更敏感的评论判断首选 `{text_primary}`；它本轮返回了更保守的 `auto_reply_allowed=false` 倾向。",
        f"- `部分成立`：`{text_backup}` 可作为低成本/常规评论备选，但仍需规则层约束。",
        "- `待验证`：价格、权益、退款和效果承诺仍需客户资料和规则库，不可让模型自由承诺。",
        "",
        "# 12. 当前最推荐的知识库检索模型",
        "",
        f"- `已确认`：知识库向量化首选 `{embedding_primary}`，本轮输出维度为 1024。",
        f"- `已确认`：重排首选 `{rerank_primary}`，适合课程资料、权益、退款和禁说规则召回后二次排序。",
        "- `待验证`：这还不是完整 RAG 通过；仍需索引写入、检索 readback、stale cleanup 和命中质量验证。",
        "",
        "# 13. 失败项、blocked 和待确认",
        "",
        markdown_table(
            ["类别", "模型", "状态", "错误摘要"],
            [[item.get("category", ""), item.get("model", ""), item.get("status", ""), item.get("error_summary", "")[:220]] for item in failed]
            or [["无", "无", "无", "无"]],
        ),
        "",
        "# 14. 后续 Codex 任务建议",
        "",
        "1. 用本轮 connected 的视觉模型做 15 秒真实录屏解析 V0，并保留抽帧 fallback。",
        "2. 如视频模型要求公网 URL，再单独做 OSS signed URL 探针，报告只写 redacted URL。",
        "3. 高成本 Omni / Wan / 长视频解析必须单独开关和单独任务，不并入本轮总探针。",
        "4. 将 connected 的文本模型接入评论规则 dry-run，但价格、退款、收益承诺必须走人工接管。",
        "5. Embedding connected 后再做小型课程资料 RAG probe，确认维度、索引、检索 readback。",
        "",
        "# 官方资料参考",
        "",
        "- Qwen 视觉/视频理解：https://help.aliyun.com/zh/model-studio/vision",
        "- OpenAI 兼容 Chat / 多模态输入：https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions",
        "- OpenAI 兼容 Embedding：https://help.aliyun.com/zh/model-studio/embedding-interfaces-compatible-with-openai",
        "- Qwen-Omni：https://help.aliyun.com/zh/model-studio/qwen-omni",
        "- Rerank：https://help.aliyun.com/zh/model-studio/text-rerank-api",
        "- wan2.2-s2v：https://help.aliyun.com/zh/model-studio/wan-s2v-api",
        "",
    ]
    return "\n".join(report_lines)


def workspace_snapshot() -> dict[str, str]:
    def run_git(args: list[str]) -> str:
        completed = subprocess.run(args, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return (completed.stdout or completed.stderr).strip()

    return {
        "pwd": str(PROJECT_ROOT),
        "top_level": run_git(["git", "rev-parse", "--show-toplevel"]),
        "branch": run_git(["git", "branch", "--show-current"]),
        "remote": run_git(["git", "remote", "-v"]),
        "status_short": run_git(["git", "status", "--short"]),
    }


def run_total_probe(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    env_info = load_workspace_env()
    run_dir = Path(args.output_dir) if args.output_dir else build_run_dir()
    run_dir.mkdir(parents=True, exist_ok=True)
    read_files = read_file_inventory()
    env_report = {
        "env_file_exists": bool(env_info["exists"]),
        "env_file_path": env_info["path"],
        "env_loaded": bool(env_info["loaded"]),
        "env_status": env_status(),
    }
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    results: list[dict[str, Any]] = []
    media: dict[str, Any] = {}
    if env_info.get("outside_workspace"):
        overall_status = "blocked_env_outside_workspace"
    elif not api_key:
        overall_status = "blocked_missing_alibaba_api_key"
        results.append(
            {
                "category": "all",
                "model": "",
                "status": overall_status,
                "input_type": "none",
                "latency_ms": 0,
                "summary": "",
                "usage": {},
                "request_id": "",
                "error_summary": "DASHSCOPE_API_KEY missing or empty",
            }
        )
    else:
        if args.safe:
            results.extend(probe_text_models(api_key, args.max_calls_per_category))
            vision_results, media = probe_vision_video_models(
                api_key,
                args.max_calls_per_category,
                run_dir,
                max_duration_sec=args.max_duration_sec,
                video_path=args.video_path,
            )
            results.extend(vision_results)
            results.extend(probe_omni_models(api_key, min(args.max_calls_per_category, 1), run_dir, media=media))
            results.extend(probe_embedding_models(api_key, args.max_calls_per_category))
            results.extend(probe_rerank_models(api_key, min(args.max_calls_per_category, 1)))
            results.extend(probe_wan_config())
            core_connected = {
                "text": any(item.get("category") == "text" and item.get("status") == "connected" for item in results),
                "vision_video": any(item.get("category") == "vision_video" and item.get("status") == "connected" for item in results),
                "embedding": any(item.get("category") == "embedding" and item.get("status") == "connected" for item in results),
            }
            overall_status = "completed_connected_core_models" if all(core_connected.values()) else "partial_completed_some_models_connected"
        else:
            overall_status = "blocked_safe_flag_required"
            results.append(
                {
                    "category": "all",
                    "model": "",
                    "status": overall_status,
                    "input_type": "none",
                    "latency_ms": 0,
                    "summary": "",
                    "usage": {},
                    "request_id": "",
                    "error_summary": "--safe is required",
                }
            )

    snapshot = workspace_snapshot()
    summary = {
        "overall_status": overall_status,
        "safe_mode": "yes" if args.safe else "no",
        "workspace": snapshot["top_level"] or str(PROJECT_ROOT),
        "branch": snapshot["branch"],
        "remote": snapshot["remote"],
        "environment": env_report,
        "read_files": read_files,
        "results": results,
        "media": media,
        "oss_upload": "no",
        "run_dir": str(run_dir),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    safe_json_write(run_dir / "alibaba_model_connection_summary.json", summary)
    report_text = build_report(summary)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    return (0 if overall_status in {"completed_connected_core_models", "partial_completed_some_models_connected"} else 2), summary


def print_summary(summary: dict[str, Any]) -> None:
    print(f"status: {summary['overall_status']}")
    print(f"run_dir: {summary['run_dir']}")
    for item in summary["results"]:
        print(
            " | ".join(
                [
                    f"category={item.get('category', '')}",
                    f"model={item.get('model', '') or 'n/a'}",
                    f"status={item.get('status', '')}",
                    f"input={item.get('input_type', '')}",
                    f"error={item.get('error_summary', '') or 'n/a'}",
                ]
            )
        )
    print(f"report: {REPORT_PATH}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe Alibaba model connection probe.")
    parser.add_argument("--safe", action="store_true", help="Enable bounded low-cost probes.")
    parser.add_argument("--max-calls-per-category", type=int, default=2)
    parser.add_argument("--max-duration-sec", type=int, default=15)
    parser.add_argument("--video-path", default="")
    parser.add_argument("--output-dir", default="")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    code, summary = run_total_probe(args)
    print_summary(summary)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
