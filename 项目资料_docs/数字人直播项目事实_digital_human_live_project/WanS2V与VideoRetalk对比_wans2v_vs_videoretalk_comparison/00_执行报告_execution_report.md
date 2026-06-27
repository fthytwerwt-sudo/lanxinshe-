# 00_执行报告

状态：`completed_report_written_pending_git_closure_at_file_creation_time`

## 执行结果

| 字段 | 值 |
|---|---|
| task_type | `read_only_comparison_audit + route_planning + AGENTS_rule_update` |
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| branch | `main` |
| remote | `https://github.com/fthytwerwt-sudo/lanxinshe-.git` |
| report_dir | `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V与VideoRetalk对比_wans2v_vs_videoretalk_comparison/` |
| AGENTS_updated | `yes` |
| generated_new_video | `no` |
| regenerated_wan_or_videoretalk | `no` |
| local_fallback_used_this_round | `no` |
| read_only_audit | `yes` |
| media_committed | `no` |
| commit_status_at_file_creation | `待验证` |
| push_status_at_file_creation | `待验证` |
| remote_HEAD_status_at_file_creation | `待验证` |

## 已完成事项

`已确认`：已读取仓库 `AGENTS.md`、机制包、VideoRetalk A 声音金标准报告、Wan / Wan-S2V 相关报告和指定 commit 证据。

`已确认`：已分清三类结果：

- `wan_raw_model_output`：Wan 原始模型输出，生成成功但 `mouth_face_ratio_p90` 超线。
- `wan_local_postprocessed_output`：本地嘴部压缩 + feather 融合后处理输出，指标通过但不能代表模型原生能力。
- `videoretalk_model_output`：VideoRetalk 模型输出，A 声音克隆成立，无本地嘴部/视频后处理，但硬指标仍有口型风险。

`已确认`：已在 `AGENTS.md` 新增 `## 禁止本地兜底规则`。

## 核心对比结果

| 路线 | 状态 | 关键指标 / 事实 |
|---|---|---|
| Wan 原始模型输出 | `部分成立` | `p90_mouth_open_ratio=0.2891281092255942` 未超 0.32；`mouth_face_ratio_p90=0.08985602706670762` 超 0.075。 |
| Wan 本地后处理输出 | `部分成立` | 指标通过：`p90_mouth_open_ratio=0.10403372181307027`、`mouth_face_ratio_p90=0.030434972047805795`；但 `local_postprocess_used=true`。 |
| VideoRetalk A 声音金标准输出 | `部分成立` | A 声音克隆成立，动作/表情/直播感观察更强；但 `p90_mouth_open_ratio=0.355425`、`mouth_face_ratio_p90=0.11274` 超阈值。 |

## 只读审计工具使用

本轮使用 `/Users/fan/.codex/skills/video-metadata-probe/scripts/probe_video.sh` 对本地已有 MP4 做技术验证，结果均为可打开、可解码、有音轨。

该使用属于：

```text
audit_or_input_preparation_not_fallback
```

本轮没有用 `ffmpeg`、OpenCV、MediaPipe、MoviePy 或本地脚本修复最终视频 / 音频。

## 新增 / 修改文件

- `AGENTS.md`
- `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V与VideoRetalk对比_wans2v_vs_videoretalk_comparison/00_执行报告_execution_report.md`
- `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V与VideoRetalk对比_wans2v_vs_videoretalk_comparison/01_成片对比审计_report.md`
- `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V与VideoRetalk对比_wans2v_vs_videoretalk_comparison/02_WanS2V口型压幅方案_wans2v_mouth_amplitude_plan.md`
- `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V与VideoRetalk对比_wans2v_vs_videoretalk_comparison/data/comparison_metrics.csv`
- `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V与VideoRetalk对比_wans2v_vs_videoretalk_comparison/data/comparison_manifest.json`

## 待验证 / 未完成在本文件生成时的事项

- `待验证`：用户人审。
- `待验证`：供应商验收。
- `待验证`：Wan-S2V 不依赖本地兜底的口型压幅 probe。
- `待验证`：30 秒 / 60 秒扩展稳定性。
- `待验证`：本文件生成后还需执行 stage、commit、push、remote HEAD readback；最终 live Git 证据以 Codex 本轮最终回报为准。
