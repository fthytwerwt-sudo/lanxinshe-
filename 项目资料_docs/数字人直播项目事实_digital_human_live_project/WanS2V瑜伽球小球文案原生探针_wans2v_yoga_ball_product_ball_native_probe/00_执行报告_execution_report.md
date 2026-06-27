# 00_执行报告_execution_report

状态：`generated_but_no_candidate_passed_pending_route_review`

## 执行结果

| 字段 | 值 |
| --- | --- |
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| branch | `main` |
| remote | `https://github.com/fthytwerwt-sudo/lanxinshe-.git` |
| reference_video_path | `/Volumes/WD_BLACK/澜心社直播/参考/C5835（下）.MP4` |
| output_dir | `/Volumes/WD_BLACK/澜心社直播/outputs/wans2v_yoga_ball_product_ball_native_probe` |
| report_dir | `/Volumes/WD_BLACK/澜心社直播/项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V瑜伽球小球文案原生探针_wans2v_yoga_ball_product_ball_native_probe` |
| generated_candidate_count | `3` |
| best_candidate | `candidate_A` |
| best_candidate_status | `best_available_failed_candidate_not_passed` |
| generated_new_video | `yes` |
| local_fallback_used | `false` |
| fallback_tts_used | `false` |
| media_committed | `false` |
| prompt_sent_to_wans2v_api | `false` |
| paid_wans2v_task_count | `3/3` |

## 主结论

`已确认`：本轮成功生成 3 条 Wan-S2V 原生 15 秒竖屏候选，均使用 A 声音克隆同款小球文案音频，均有清晰可见瑜伽球，均没有本地最终成片修复。

`部分成立`：视觉观察上，Candidate A 的瑜伽球可见性和动作讲解感最好，Qwen-VL 辅助评分为 `5/5`；但 Candidate A 的 `mouth_face_ratio_p90=0.08387625366449357`，超过硬阈值 `0.075`。

`待验证`：用户人审、听感、真实音画同步、人脸审美稳定性、供应商验收、30 秒/60 秒扩展能力。

`未通过硬标准`：三条候选都没有同时满足所有口型硬指标，因此不得写 `completed_wans2v_yoga_ball_native_probe_candidate_created_pending_human_review`。

## 候选摘要

| candidate_id | pass_status | duration_sec | has_audio | yoga_ball_visible | action_alignment_score | mouth_face_ratio_p90 | p90_mouth_open_ratio | fail_frame_percent | longest_fail_streak | failed_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_A | failed_hard_threshold | 15.133333 | True | True | 5 | 0.08387625366449357 | 0.26871763138799404 | 0.4132231404958678 | 1 | mouth_face_ratio_p90_above_0.075 |
| candidate_B | failed_hard_threshold | 15.133333 | True | True | 4 | 0.09159099757671357 | 0.31659181841866296 | 1.6528925619834711 | 1 | mouth_face_ratio_p90_above_0.075 |
| candidate_C | failed_hard_threshold | 15.133333 | True | True | 4 | 0.10744787603616715 | 0.352648331699753 | 7.851239669421488 | 4 | p90_mouth_open_ratio_above_0.32;mouth_face_ratio_p90_above_0.075 |

## 边界说明

- 本轮没有重跑 VideoRetalk。
- 本轮没有使用 `longyingxiao_v3`、`longanxuan_v3` 或其它 preset voice。
- 本轮没有使用 ffmpeg/OpenCV/MediaPipe/MoviePy 修最终视频。
- `ffmpeg` 仅用于抽帧、输入图标准化、输入音频降幅、metadata/审计帧，标记为 `audit_or_input_preparation_not_fallback`。
- Wan-S2V 当前调用按官方文档和项目脚本使用 `image_url + audio_url + resolution`，没有可发送的 `prompt/negative_prompt` 字段；报告中的 prompt 是设计约束，不是已发送模型参数。
- 技术生成成功不等于人审通过、业务通过或供应商验收。

## Git 状态

本文件生成于 commit 之前；最终 commit / push / remote HEAD readback 以本轮 Codex 最终回报为准。

## 提交前验证

已执行 / 待执行验证项：

- `python3` JSON/CSV 解析：`passed`。
- credential / signed URL query 扫描：`passed_no_match_in_report_dir`。
- 目标报告目录 `._*` AppleDouble 清理：`passed`。
- `git diff --check`：待执行。
- staged 媒体检查：待执行。
- path-limited stage：待执行，仅暂存本轮报告目录。

已知本地工作区存在本轮无关脏文件：客户交付 PDF 删除状态、仓库根部和其它目录 `._*` AppleDouble、`contracts/`、`local_only_reports/` 等未跟踪文件。本轮不修改、不暂存、不回滚这些无关项。
