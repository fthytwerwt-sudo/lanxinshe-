"""Probe Qwen text model for structured live-comment risk output."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import probe_alibaba_model_connections as core  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe Qwen structured reply probe.")
    parser.add_argument("--safe", action="store_true")
    parser.add_argument("--max-calls", type=int, default=1)
    args = parser.parse_args()

    core.load_workspace_env()
    api_key = core.os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not args.safe:
        print("status: blocked_safe_flag_required")
        return 2
    if not api_key:
        print("status: blocked_missing_alibaba_api_key")
        return 2

    run_dir = core.build_run_dir("qwen_text_structured_reply")
    results = core.probe_text_models(api_key, args.max_calls)
    core.safe_json_write(run_dir / "qwen_text_structured_reply_summary.json", {"results": results})
    for item in results:
        print(
            f"model={item['model']} | status={item['status']} | "
            f"error={item.get('error_summary') or 'n/a'}"
        )
    print(f"run_dir: {run_dir}")
    return 0 if any(item["status"] == "connected" for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
