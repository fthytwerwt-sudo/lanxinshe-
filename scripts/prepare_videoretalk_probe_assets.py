"""Prepare local-only VideoRetalk probe assets from an existing livestream clip."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "参考" / "完整直播录屏" / "今年直播素材" / "C5824.MP4"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "videoretalk_probe"
MEDIA_SUFFIXES = {".mp4", ".mov", ".avi"}


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def _safe_error(value: str) -> str:
    return value.replace(str(PROJECT_ROOT), "<project_root>")[:800]


def _inside_project(path: Path) -> bool:
    try:
        path.resolve().relative_to(PROJECT_ROOT.resolve())
        return True
    except ValueError:
        return False


def _find_fallback_source() -> Path | None:
    roots = [
        PROJECT_ROOT / "参考" / "完整直播录屏" / "今年直播素材",
        PROJECT_ROOT / "参考" / "完整直播录屏",
        PROJECT_ROOT / "参考",
    ]
    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.name.startswith("._"):
                continue
            if path.is_file() and path.suffix.lower() in MEDIA_SUFFIXES:
                candidates.append(path)
    if not candidates:
        return None
    candidates.sort(key=lambda item: (0 if item == DEFAULT_SOURCE else 1, len(item.parts), str(item)))
    return candidates[0]


def _resolve_source(source_arg: str) -> Path | None:
    if source_arg:
        source = Path(source_arg)
        if not source.is_absolute():
            source = PROJECT_ROOT / source
        return source if source.exists() else None
    if DEFAULT_SOURCE.exists():
        return DEFAULT_SOURCE
    return _find_fallback_source()


def _run(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "ffmpeg_not_found"
    if completed.returncode != 0:
        return False, _safe_error(completed.stderr or completed.stdout)
    return True, ""


def _prepare(source: Path, output_dir: Path, start: str, duration_sec: float) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return {"prepared": False, "blocked_reason": "blocked_ffmpeg_missing"}
    if not _inside_project(source):
        return {"prepared": False, "blocked_reason": "blocked_source_outside_workspace"}

    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / "input_video_3s.mp4"
    audio_path = output_dir / "input_audio_3s.wav"
    ref_image_path = output_dir / "ref_image.jpg"

    scale_filter = "scale=if(gt(a\\,1)\\,-2\\,720):if(gt(a\\,1)\\,720\\,-2)"
    commands = [
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-ss",
            start,
            "-i",
            str(source),
            "-t",
            str(duration_sec),
            "-vf",
            scale_filter,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(video_path),
        ],
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-ss",
            start,
            "-i",
            str(source),
            "-t",
            str(duration_sec),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio_path),
        ],
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-ss",
            start,
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(ref_image_path),
        ],
    ]
    for command in commands:
        ok, error = _run(command)
        if not ok:
            return {"prepared": False, "blocked_reason": "blocked_ffmpeg_extract_failed", "error": error}

    return {
        "prepared": True,
        "blocked_reason": "",
        "source_video": _relative_or_absolute(source),
        "start": start,
        "duration_sec": duration_sec,
        "outputs": {
            "video": _relative_or_absolute(video_path),
            "audio": _relative_or_absolute(audio_path),
            "ref_image": _relative_or_absolute(ref_image_path),
        },
        "output_sizes_bytes": {
            "video": video_path.stat().st_size,
            "audio": audio_path.stat().st_size,
            "ref_image": ref_image_path.stat().st_size,
        },
        "media_committed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare local-only VideoRetalk probe assets")
    parser.add_argument("--source-video", default="", help="Optional local source video under the workspace")
    parser.add_argument("--start", default="00:01:00", help="Clip start time")
    parser.add_argument("--duration-sec", type=float, default=3.0, help="Probe duration in seconds")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Local output directory")
    parser.add_argument("--safe", action="store_true", help="Compatibility flag; output is always safe")
    args = parser.parse_args()

    source = _resolve_source(args.source_video)
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    if not source:
        payload = {
            "prepared": False,
            "blocked_reason": "blocked_source_video_missing",
            "preferred_source": _relative_or_absolute(DEFAULT_SOURCE),
            "media_committed": False,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    if args.duration_sec <= 2 or args.duration_sec >= 120:
        payload = {
            "prepared": False,
            "blocked_reason": "blocked_duration_outside_videoretalk_limits",
            "duration_sec": args.duration_sec,
            "media_committed": False,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    payload = _prepare(source, output_dir, args.start, args.duration_sec)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("prepared") else 2


if __name__ == "__main__":
    raise SystemExit(main())
