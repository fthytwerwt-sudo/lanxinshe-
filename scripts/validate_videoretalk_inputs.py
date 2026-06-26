"""Validate local VideoRetalk probe media before any paid task submission."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VIDEO_SUFFIXES = {".mp4", ".avi", ".mov"}
AUDIO_SUFFIXES = {".wav", ".mp3", ".aac"}
VIDEO_CODECS = {"h264", "hevc", "h265"}
MAX_VIDEO_BYTES = 300 * 1024 * 1024
MAX_AUDIO_BYTES = 30 * 1024 * 1024


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def _run_ffprobe(path: Path) -> tuple[dict[str, Any], str]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {}, "ffprobe_not_found"
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return {}, (completed.stderr or completed.stdout).strip()[:500]
    try:
        return json.loads(completed.stdout), ""
    except json.JSONDecodeError as exc:
        return {}, f"ffprobe_json_error:{exc}"


def _duration(metadata: dict[str, Any], stream: dict[str, Any] | None = None) -> float:
    candidates = []
    if stream:
        candidates.append(stream.get("duration"))
    candidates.append(metadata.get("format", {}).get("duration"))
    for value in candidates:
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def _fps(value: str | None) -> float:
    if not value or value == "0/0":
        return 0.0
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return 0.0


def _first_stream(metadata: dict[str, Any], codec_type: str) -> dict[str, Any] | None:
    for stream in metadata.get("streams", []):
        if stream.get("codec_type") == codec_type:
            return stream
    return None


def _validate_video(path: Path) -> tuple[dict[str, Any], list[str]]:
    reasons: list[str] = []
    metadata, error = _run_ffprobe(path)
    video_stream = _first_stream(metadata, "video") if metadata else None
    size_bytes = path.stat().st_size if path.exists() else 0
    duration = _duration(metadata, video_stream)
    fps = _fps((video_stream or {}).get("avg_frame_rate") or (video_stream or {}).get("r_frame_rate"))
    width = int((video_stream or {}).get("width") or 0)
    height = int((video_stream or {}).get("height") or 0)
    codec = str((video_stream or {}).get("codec_name") or "").lower()
    suffix = path.suffix.lower()

    if not path.exists():
        reasons.append("blocked_video_missing")
    if suffix not in VIDEO_SUFFIXES:
        reasons.append("blocked_video_format")
    if size_bytes > MAX_VIDEO_BYTES:
        reasons.append("blocked_video_too_large")
    if not (2 < duration < 120):
        reasons.append("blocked_video_duration")
    if not (15 <= fps <= 60):
        reasons.append("blocked_video_fps")
    if not (640 <= width <= 2048 and 640 <= height <= 2048):
        reasons.append("blocked_video_side_length")
    if codec and codec not in VIDEO_CODECS:
        reasons.append("blocked_video_codec")
    if not video_stream:
        reasons.append("blocked_video_stream_missing")
    if error:
        reasons.append("blocked_video_metadata_unreadable")

    return (
        {
            "path": _relative_or_absolute(path),
            "format": suffix.lstrip("."),
            "size_bytes": size_bytes,
            "duration_sec": round(duration, 3),
            "fps": round(fps, 3),
            "width": width,
            "height": height,
            "codec": codec,
            "metadata_error": error,
        },
        reasons,
    )


def _validate_audio(path: Path) -> tuple[dict[str, Any], list[str]]:
    reasons: list[str] = []
    metadata, error = _run_ffprobe(path)
    audio_stream = _first_stream(metadata, "audio") if metadata else None
    size_bytes = path.stat().st_size if path.exists() else 0
    duration = _duration(metadata, audio_stream)
    suffix = path.suffix.lower()

    if not path.exists():
        reasons.append("blocked_audio_missing")
    if suffix not in AUDIO_SUFFIXES:
        reasons.append("blocked_audio_format")
    if size_bytes > MAX_AUDIO_BYTES:
        reasons.append("blocked_audio_too_large")
    if not (2 < duration < 120):
        reasons.append("blocked_audio_duration")
    if not audio_stream:
        reasons.append("blocked_audio_stream_missing")
    if error:
        reasons.append("blocked_audio_metadata_unreadable")

    return (
        {
            "path": _relative_or_absolute(path),
            "format": suffix.lstrip("."),
            "size_bytes": size_bytes,
            "duration_sec": round(duration, 3),
            "codec": str((audio_stream or {}).get("codec_name") or "").lower(),
            "sample_rate": str((audio_stream or {}).get("sample_rate") or ""),
            "channels": int((audio_stream or {}).get("channels") or 0),
            "metadata_error": error,
        },
        reasons,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VideoRetalk local input media")
    parser.add_argument("--video", required=True, help="Local mp4/avi/mov video path")
    parser.add_argument("--audio", required=True, help="Local wav/mp3/aac audio path")
    parser.add_argument("--safe", action="store_true", help="Compatibility flag; output is always safe")
    args = parser.parse_args()

    video_path = Path(args.video)
    audio_path = Path(args.audio)
    if not video_path.is_absolute():
        video_path = PROJECT_ROOT / video_path
    if not audio_path.is_absolute():
        audio_path = PROJECT_ROOT / audio_path

    video_metadata, video_reasons = _validate_video(video_path)
    audio_metadata, audio_reasons = _validate_audio(audio_path)
    reasons = video_reasons + audio_reasons
    payload = {
        "input_valid": not reasons,
        "blocked_reason": ",".join(reasons),
        "blocked_reasons": reasons,
        "video_metadata": video_metadata,
        "audio_metadata": audio_metadata,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["input_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
