"""Guarded Alibaba VideoRetalk connection probe.

Dry-run mode validates registry/env/payload shape and never creates a paid
generation task. Submit mode requires ALLOW_VIDEORETALK_GENERATION_PROBE=true
plus public URLs or an explicit local-to-OSS upload request.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.alibaba_model_registry import (  # noqa: E402
    MODEL_CATALOG,
    VIDEORETALK_API_SPEC,
    VIDEORETALK_MODEL_CANDIDATES,
    VIDEORETALK_SUBMIT_ENDPOINT,
    VIDEORETALK_TASK_ENDPOINT_TEMPLATE,
)
from config.env_config import (  # noqa: E402
    build_config_report,
    get_bool_env,
    get_env,
    get_int_env,
    load_environment,
)


OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "videoretalk_probe"
ENV_KEYS = (
    "DASHSCOPE_API_KEY",
    "ALIBABA_CLOUD_ACCESS_KEY_ID",
    "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
    "ALIBABA_REGION_ID",
    "ALIBABA_OSS_ENDPOINT",
    "ALIBABA_OSS_BUCKET",
    "ALIBABA_OSS_OBJECT_PREFIX",
    "ALIBABA_OSS_SIGNED_URL_EXPIRES",
    "ALLOW_VIDEORETALK_GENERATION_PROBE",
)
PLACEHOLDER_VIDEO_URL = "https://example.invalid/videoretalk/input_video.mp4"
PLACEHOLDER_AUDIO_URL = "https://example.invalid/videoretalk/input_audio.wav"


class BlockedError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _safe_run_dir(prefix: str = "dry_run") -> Path:
    run_id = datetime.now().strftime(f"%Y%m%d_%H%M%S_{prefix}")
    run_dir = OUTPUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _env_status() -> dict[str, str]:
    report = {}
    for item in build_config_report(ENV_KEYS):
        report[item["name"]] = item["status"]
    return report


def _redact_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url)
    if parts.query:
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "[REDACTED_QUERY]", ""))
    return url


def _redact_text(text: str, api_key: str = "") -> str:
    safe = text
    if api_key:
        safe = safe.replace(api_key, "<masked_api_key>")
    safe = re.sub(r"sk-[A-Za-z0-9_\-]{8,}", "<masked_dashscope_api_key>", safe)
    safe = re.sub(r"Bearer\s+[A-Za-z0-9_\-.]+", "Bearer <masked>", safe, flags=re.I)
    safe = re.sub(r"(https?://[^\s?]+)\?[^\s]+", r"\1?<redacted_query>", safe)
    return safe[:1000]


def _redact_task_body(body: dict[str, Any]) -> dict[str, Any]:
    redacted = json.loads(json.dumps(body, ensure_ascii=False))
    output = redacted.get("output")
    if isinstance(output, dict):
        for key in ("video_url", "url"):
            if isinstance(output.get(key), str):
                output[key] = _redact_url(output[key])
    return redacted


def _is_public_url(url: str) -> bool:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        return False
    if not parts.netloc:
        return False
    if parts.netloc.endswith(".invalid") or parts.netloc in {"localhost", "127.0.0.1"}:
        return False
    return True


def _validate_query_face_threshold(value: int | None) -> None:
    if value is None:
        return
    if not 120 <= value <= 200:
        raise BlockedError(
            "blocked_invalid_query_face_threshold",
            "query_face_threshold must be between 120 and 200",
        )


def _build_payload(
    video_url: str,
    audio_url: str,
    ref_image_url: str = "",
    video_extension: bool = False,
    query_face_threshold: int | None = None,
) -> dict[str, Any]:
    _validate_query_face_threshold(query_face_threshold)
    payload: dict[str, Any] = {
        "model": "videoretalk",
        "input": {
            "video_url": video_url,
            "audio_url": audio_url,
        },
        "parameters": {
            "video_extension": video_extension,
        },
    }
    if ref_image_url:
        payload["input"]["ref_image_url"] = ref_image_url
    if query_face_threshold is not None:
        payload["parameters"]["query_face_threshold"] = query_face_threshold
    return payload


def _redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = json.loads(json.dumps(payload, ensure_ascii=False))
    input_payload = redacted.get("input", {})
    if isinstance(input_payload, dict):
        for key in ("video_url", "audio_url", "ref_image_url"):
            if isinstance(input_payload.get(key), str):
                input_payload[key] = _redact_url(input_payload[key])
    return redacted


def _headers(api_key: str, async_enabled: bool) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if async_enabled:
        headers["X-DashScope-Async"] = "enable"
    return headers


def _classify_api_error(status_code: int, body: dict[str, Any]) -> str:
    code = str(body.get("code") or body.get("error_code") or "").lower()
    message = str(body.get("message") or body.get("error") or body).lower()
    combined = f"{code} {message}"
    if status_code in {401, 403} or "invalidapikey" in combined or "api-key" in combined:
        return "blocked_missing_dashscope_api_key"
    if status_code in {402, 429} or any(word in combined for word in ("quota", "balance", "额度", "余额", "限流")):
        return "blocked_videoretalk_permission_or_balance"
    if any(word in combined for word in ("permission", "not enabled", "未开通", "无权限", "model")):
        return "blocked_videoretalk_permission_or_balance"
    if status_code in {400, 404} or any(word in combined for word in ("url", "endpoint", "region", "地域")):
        return "blocked_upload_url_unavailable"
    return "blocked_api_error"


def _require_local_file(path_value: str) -> Path:
    if not path_value:
        raise BlockedError("blocked_local_asset_missing", "local asset path is missing")
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists() or not path.is_file():
        raise BlockedError("blocked_local_asset_missing", f"local asset not found: {path.name}")
    try:
        path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise BlockedError("blocked_source_outside_workspace", "local asset is outside workspace") from exc
    return path


def _normalize_oss_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    if endpoint.startswith("http://"):
        return "https://" + endpoint[len("http://") :]
    if endpoint and not endpoint.startswith("https://"):
        return "https://" + endpoint
    return endpoint


def _require_oss_config() -> dict[str, Any]:
    config = {
        "access_key_id": (get_env("ALIBABA_CLOUD_ACCESS_KEY_ID", "") or "").strip(),
        "access_key_secret": (get_env("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "") or "").strip(),
        "endpoint": _normalize_oss_endpoint((get_env("ALIBABA_OSS_ENDPOINT", "") or "").strip()),
        "bucket_name": (get_env("ALIBABA_OSS_BUCKET", "") or "").strip(),
        "object_prefix": (get_env("ALIBABA_OSS_OBJECT_PREFIX", "") or "").strip().strip("/"),
        "expires": get_int_env("ALIBABA_OSS_SIGNED_URL_EXPIRES", 0),
    }
    if not config["access_key_id"] or not config["access_key_secret"]:
        raise BlockedError("blocked_upload_url_unavailable", "OSS AccessKey is missing")
    if not config["endpoint"] or not config["bucket_name"] or not config["object_prefix"]:
        raise BlockedError("blocked_upload_url_unavailable", "OSS endpoint, bucket, or prefix is missing")
    if int(config["expires"]) <= 0:
        raise BlockedError("blocked_upload_url_unavailable", "OSS signed URL expiry is invalid")
    return config


def _upload_and_sign(path: Path, object_key: str, oss_config: dict[str, Any], run_dir: Path) -> tuple[str, str, dict[str, Any]]:
    try:
        import oss2
    except Exception as exc:
        raise BlockedError("blocked_upload_url_unavailable", "oss2 is not installed") from exc

    report: dict[str, Any] = {
        "object_key": object_key,
        "source_path": str(path.relative_to(PROJECT_ROOT)),
        "content_type": mimetypes.guess_type(str(path))[0] or "application/octet-stream",
        "upload_success": False,
        "signed_url_generated": False,
        "signed_url_verified": False,
        "signed_url_redacted": "",
        "error": "",
    }
    try:
        auth = oss2.Auth(oss_config["access_key_id"], oss_config["access_key_secret"])
        bucket = oss2.Bucket(auth, oss_config["endpoint"], oss_config["bucket_name"])
        result = bucket.put_object_from_file(
            object_key,
            str(path),
            headers={"Content-Type": report["content_type"]},
        )
        report["upload_success"] = True
        report["upload_status"] = getattr(result, "status", "")
        signed_url = bucket.sign_url("GET", object_key, int(oss_config["expires"]))
        if signed_url.startswith("http://"):
            signed_url = "https://" + signed_url[len("http://") :]
        report["signed_url_generated"] = True
        report["signed_url_redacted"] = _redact_url(signed_url)
        response = requests.get(signed_url, headers={"Range": "bytes=0-0"}, stream=True, timeout=30)
        report["signed_url_verify_status"] = response.status_code
        response.close()
        if report["signed_url_verify_status"] not in {200, 206}:
            report["error"] = f"signed URL verify status={report['signed_url_verify_status']}"
            raise BlockedError("blocked_upload_url_unavailable", report["error"])
        report["signed_url_verified"] = True
        return signed_url, report["signed_url_redacted"], report
    except BlockedError:
        raise
    except Exception as exc:
        report["error"] = str(exc)
        raise BlockedError("blocked_upload_url_unavailable", f"OSS upload/sign failed: {exc}") from exc
    finally:
        _append_jsonl(run_dir / "oss_upload_report.jsonl", report)


def _upload_local_assets(args: argparse.Namespace, run_dir: Path) -> tuple[str, str, str, list[dict[str, Any]]]:
    video_file = _require_local_file(args.video_file)
    audio_file = _require_local_file(args.audio_file)
    ref_image_file = _require_local_file(args.ref_image_file) if args.ref_image_file else None
    oss_config = _require_oss_config()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_key = f"{oss_config['object_prefix']}/videoretalk_probe/{timestamp}"
    reports: list[dict[str, Any]] = []

    video_url, _, report = _upload_and_sign(video_file, f"{base_key}/input_video{video_file.suffix.lower()}", oss_config, run_dir)
    reports.append(report)
    audio_url, _, report = _upload_and_sign(audio_file, f"{base_key}/input_audio{audio_file.suffix.lower()}", oss_config, run_dir)
    reports.append(report)
    ref_url = ""
    if ref_image_file:
        ref_url, _, report = _upload_and_sign(ref_image_file, f"{base_key}/ref_image{ref_image_file.suffix.lower()}", oss_config, run_dir)
        reports.append(report)
    return video_url, audio_url, ref_url, reports


def _create_task(api_key: str, payload: dict[str, Any], run_dir: Path) -> tuple[str, str, dict[str, Any]]:
    try:
        response = requests.post(
            VIDEORETALK_SUBMIT_ENDPOINT,
            headers=_headers(api_key, async_enabled=True),
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise BlockedError("blocked_network_error", f"task submit network error: {exc}") from exc
    try:
        body = response.json()
    except ValueError as exc:
        raise BlockedError("blocked_api_error", f"task submit returned non-json status={response.status_code}") from exc
    _write_json(run_dir / "task_create_response.redacted.json", _redact_task_body(body))
    if not response.ok:
        raise BlockedError(_classify_api_error(response.status_code, body), _redact_text(str(body), api_key))
    output = body.get("output") if isinstance(body, dict) else None
    task_id = output.get("task_id") if isinstance(output, dict) else None
    if not task_id:
        raise BlockedError("blocked_api_error", "task submit response missing output.task_id")
    return str(task_id), str(body.get("request_id") or ""), body


def _poll_task(api_key: str, task_id: str, run_dir: Path, poll_interval: int, timeout_seconds: int) -> tuple[str, str, dict[str, Any]]:
    deadline = time.monotonic() + timeout_seconds
    task_url = VIDEORETALK_TASK_ENDPOINT_TEMPLATE.format(task_id=task_id)
    while True:
        try:
            response = requests.get(task_url, headers=_headers(api_key, async_enabled=False), timeout=60)
            body = response.json()
        except requests.RequestException as exc:
            raise BlockedError("blocked_network_error", f"task poll network error: {exc}") from exc
        except ValueError as exc:
            raise BlockedError("blocked_api_error", "task poll returned non-json") from exc

        output = body.get("output") if isinstance(body, dict) else {}
        task_status = str(output.get("task_status") or "UNKNOWN") if isinstance(output, dict) else "UNKNOWN"
        _append_jsonl(
            run_dir / "task_status_poll.redacted.jsonl",
            {
                "polled_at": datetime.now().isoformat(timespec="seconds"),
                "status_code": response.status_code,
                "task_status": task_status,
                "body": _redact_task_body(body),
            },
        )
        if not response.ok:
            raise BlockedError(_classify_api_error(response.status_code, body), _redact_text(str(body), api_key))
        if task_status == "SUCCEEDED":
            return task_status, str(body.get("request_id") or ""), body
        if task_status in {"FAILED", "CANCELED", "UNKNOWN"}:
            raise BlockedError("blocked_task_failed", _redact_text(str(body), api_key))
        if time.monotonic() >= deadline:
            raise BlockedError("blocked_api_error", f"task polling timed out; last_status={task_status}")
        time.sleep(poll_interval)


def _download_result(video_url: str, run_dir: Path) -> Path:
    if not video_url:
        raise BlockedError("blocked_api_error", "SUCCEEDED task missing output.video_url")
    result_path = run_dir / "result_video.mp4"
    try:
        with requests.get(video_url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with result_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
    except requests.RequestException as exc:
        raise BlockedError("blocked_network_error", f"result download failed: {exc}") from exc
    return result_path


def _registry_present() -> bool:
    return "avatar_video_retalk" in MODEL_CATALOG and "videoretalk" in VIDEORETALK_MODEL_CANDIDATES


def _base_summary(mode: str, run_dir: Path) -> dict[str, Any]:
    env = _env_status()
    return {
        "status": "pending",
        "mode": mode,
        "run_dir": str(run_dir.relative_to(PROJECT_ROOT)),
        "model": "videoretalk",
        "submit_endpoint": VIDEORETALK_SUBMIT_ENDPOINT,
        "task_endpoint": VIDEORETALK_TASK_ENDPOINT_TEMPLATE,
        "dashscope_api_key": env.get("DASHSCOPE_API_KEY", "missing"),
        "env_status": env,
        "videoretalk_registry_present": _registry_present(),
        "api_spec": VIDEORETALK_API_SPEC,
        "would_submit": False,
        "generation_probe_allowed": get_bool_env("ALLOW_VIDEORETALK_GENERATION_PROBE", default=False),
        "generation_probe_submitted": False,
        "task_id": "",
        "task_status": "",
        "request_id": "",
        "result_video_path": "",
        "media_committed": "no",
        "printed_secret": "no",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Alibaba VideoRetalk safely")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Build safe payload only; do not submit")
    mode.add_argument("--submit", action="store_true", help="Submit a real paid task when explicitly enabled")
    parser.add_argument("--safe", action="store_true", help="Compatibility flag; output is always safe")
    parser.add_argument("--video-url", default="", help="Public HTTP/HTTPS source video URL")
    parser.add_argument("--audio-url", default="", help="Public HTTP/HTTPS driving audio URL")
    parser.add_argument("--ref-image-url", default="", help="Optional public HTTP/HTTPS target face image URL")
    parser.add_argument("--upload-local-assets", action="store_true", help="Upload local assets to OSS before submit")
    parser.add_argument("--video-file", default="", help="Local source video to upload when --upload-local-assets is used")
    parser.add_argument("--audio-file", default="", help="Local source audio to upload when --upload-local-assets is used")
    parser.add_argument("--ref-image-file", default="", help="Optional local ref image to upload")
    parser.add_argument("--video-extension", action="store_true", help="Allow video extension when audio is longer")
    parser.add_argument("--query-face-threshold", type=int, default=None)
    parser.add_argument("--poll-interval", type=int, default=15)
    parser.add_argument("--timeout-seconds", type=int, default=20 * 60)
    args = parser.parse_args()

    load_environment()
    dry_run = args.dry_run or not args.submit
    run_dir = _safe_run_dir("dry_run" if dry_run else "submit")
    summary = _base_summary("dry_run" if dry_run else "submit", run_dir)

    try:
        if not _registry_present():
            raise BlockedError("blocked_registry_missing", "videoretalk missing from model registry")

        if dry_run:
            video_url = args.video_url or PLACEHOLDER_VIDEO_URL
            audio_url = args.audio_url or PLACEHOLDER_AUDIO_URL
            payload = _build_payload(
                video_url=video_url,
                audio_url=audio_url,
                ref_image_url=args.ref_image_url,
                video_extension=args.video_extension,
                query_face_threshold=args.query_face_threshold,
            )
            summary.update(
                {
                    "status": "dry_run_passed",
                    "payload_shape_valid": True,
                    "public_urls_provided": bool(args.video_url and args.audio_url),
                    "dry_run_placeholder_urls": not bool(args.video_url and args.audio_url),
                    "would_submit": False,
                    "redacted_payload": _redact_payload(payload),
                    "blocked_reason": "",
                }
            )
            _write_json(run_dir / "videoretalk_dry_run_result.json", summary)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0

        api_key = (get_env("DASHSCOPE_API_KEY", "") or "").strip()
        if not api_key:
            raise BlockedError("blocked_missing_dashscope_api_key", "DASHSCOPE_API_KEY is missing")
        if not get_bool_env("ALLOW_VIDEORETALK_GENERATION_PROBE", default=False):
            raise BlockedError(
                "blocked_generation_probe_not_allowed",
                "ALLOW_VIDEORETALK_GENERATION_PROBE is not true",
            )

        video_url = args.video_url
        audio_url = args.audio_url
        ref_image_url = args.ref_image_url
        oss_reports: list[dict[str, Any]] = []
        if args.upload_local_assets:
            video_url, audio_url, ref_image_url, oss_reports = _upload_local_assets(args, run_dir)
        if not (_is_public_url(video_url) and _is_public_url(audio_url)):
            raise BlockedError("blocked_upload_url_unavailable", "video_url and audio_url must be public HTTP/HTTPS URLs")
        if ref_image_url and not _is_public_url(ref_image_url):
            raise BlockedError("blocked_upload_url_unavailable", "ref_image_url must be a public HTTP/HTTPS URL")

        payload = _build_payload(
            video_url=video_url,
            audio_url=audio_url,
            ref_image_url=ref_image_url,
            video_extension=args.video_extension,
            query_face_threshold=args.query_face_threshold,
        )
        summary.update(
            {
                "status": "submitting",
                "payload_shape_valid": True,
                "public_urls_provided": True,
                "would_submit": True,
                "redacted_payload": _redact_payload(payload),
                "oss_upload_reports": oss_reports,
            }
        )
        _write_json(run_dir / "request_payload.redacted.json", _redact_payload(payload))
        task_id, request_id, _ = _create_task(api_key, payload, run_dir)
        task_status, poll_request_id, task_body = _poll_task(
            api_key=api_key,
            task_id=task_id,
            run_dir=run_dir,
            poll_interval=args.poll_interval,
            timeout_seconds=args.timeout_seconds,
        )
        output = task_body.get("output") if isinstance(task_body, dict) else {}
        result_path = _download_result(str(output.get("video_url") or ""), run_dir)
        summary.update(
            {
                "status": "generation_probe_connected",
                "generation_probe_submitted": True,
                "task_id": task_id,
                "task_status": task_status,
                "request_id": poll_request_id or request_id,
                "result_video_path": str(result_path.relative_to(PROJECT_ROOT)),
                "blocked_reason": "",
            }
        )
        _write_json(run_dir / "videoretalk_submit_result.redacted.json", summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except BlockedError as exc:
        summary.update(
            {
                "status": exc.code,
                "blocked_reason": exc.code,
                "blocked_message": _redact_text(exc.message, get_env("DASHSCOPE_API_KEY", "") or ""),
                "would_submit": False if exc.code == "blocked_generation_probe_not_allowed" else summary.get("would_submit", False),
            }
        )
        _write_json(run_dir / "videoretalk_blocked_result.json", summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
