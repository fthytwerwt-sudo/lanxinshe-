"""Probe Qwen-VL/Qwen3-VL with a short local live-video clip or frame."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import probe_alibaba_model_connections as core  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe Qwen-VL live video analysis probe.")
    parser.add_argument("--safe", action="store_true")
    parser.add_argument("--max-duration-sec", type=int, default=15)
    parser.add_argument("--max-models", type=int, default=2)
    parser.add_argument("--video-path", default="")
    args = parser.parse_args()

    core.load_workspace_env()
    api_key = core.os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not args.safe:
        print("status: blocked_safe_flag_required")
        return 2
    if not api_key:
        print("status: blocked_missing_alibaba_api_key")
        return 2

    run_dir = core.build_run_dir("qwen_vl_video_analysis")
    results, media = core.probe_vision_video_models(
        api_key,
        args.max_models,
        run_dir,
        max_duration_sec=args.max_duration_sec,
        video_path=args.video_path,
    )
    core.safe_json_write(
        run_dir / "qwen_vl_video_analysis_summary.json",
        {"media": media, "results": results},
    )
    for item in results:
        print(
            f"model={item.get('model') or 'n/a'} | status={item['status']} | "
            f"input={item.get('input_type')} | error={item.get('error_summary') or 'n/a'}"
        )
    print(f"source_video_found: {media.get('source_video_found')}")
    print(f"run_dir: {run_dir}")
    return 0 if any(item["status"] == "connected" for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
