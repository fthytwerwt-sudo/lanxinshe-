# WanS2V 身体大幅动作缺失复盘执行报告

状态：`completed_body_motion_failure_audit_pending_user_review`

## 一页结论

`已确认`：本轮没有生成新 Wan-S2V 视频，没有调用付费生成 API，没有修视频，没有本地兜底；本地工具只用于 `audit_or_input_preparation_not_fallback`。

`已确认`：上一轮 3 条源视频和 3 条 Wan-S2V 候选视频均存在、可解码、有音轨；本轮完成了全片、上一轮 0-15s selected segment、生成候选三层动作扫描。

`已确认`：上一轮真实调用路线是 `image_url + audio_url + resolution`，`true_video_motion_reference_used=false`，`prompt_sent_to_api=false`，没有把源视频时间线作为 `video_url` / `motion_reference` 传入模型。

`已确认`：按严格定义，3 个源视频全片都不是站起、走动、转身、侧移、走近/远离镜头这类“身体大幅移动”素材；它们主要是固定机位下的站立讲解、桥式躺卧保持、坐姿小球讲解。

`已确认`：最终归因是 `model_route_limitation_not_clip_selection_issue`。主因是当前 Wan-S2V 调用路线不支持 true video motion reference；次因是源素材/选段本身多为轻动作、手部动作、姿态保持，不足以验证 1:1 大幅身体动作复刻。

`已确认`：本报告的 `body_motion_score` 是严格大幅身体动作评分，3.5/5 以上才算大幅身体移动；原始帧差分数只作辅助字段，已在 CSV 中单独标记为 `raw_frame_diff_*`。

`待验证`：用户人审、审美、人感、供应商验收、业务可用性均未通过；本报告只给技术审计与路线判断。

## 关键表

| source_id | full_video_has_large_body_motion | max_body_motion_time_range | max_body_motion_score | selected_segment_body_motion_score | clip_selection_judgement | recommended_reselect_range |
| --- | --- | --- | --- | --- | --- | --- |
| source_01 | False | 50.0-65.0s | 2.5 | 2.2 | not_clip_selection_issue_source_has_only_moderate_upper_body_motion | 50.0-65.0s_if_testing_upper_body_only_not_true_large_body |
| source_02 | False | 28.0-43.0s | 1.8 | 1.6 | not_clip_selection_issue_source_is_bridge_pose_hold | no_reselect_for_large_body_supplement_new_large_motion_sample |
| source_03 | False | 0.0-15.0s | 2.4 | 2.4 | not_clip_selection_issue_selected_segment_is_representative | 0.0-15.0s_already_representative_not_true_large_body |

| source_id | candidate_id | selected_segment_body_motion_score | generated_body_motion_score | motion_retention_ratio | stiffness_detected | failure_cause |
| --- | --- | --- | --- | --- | --- | --- |
| source_01 | candidate_01_from_source_01 | 2.2 | 0.8 | 0.3636 | True | source_has_only_moderate_upper_body_motion_plus_model_route_limitation_and_generation_motion_loss |
| source_02 | candidate_02_from_source_02 | 1.6 | 0.7 | 0.4375 | True | source_pose_hold_plus_model_route_limitation_and_generation_motion_loss |
| source_03 | candidate_03_from_source_03 | 2.4 | 1.0 | 0.4167 | True | selected_segment_representative_but_model_route_limitation_and_generation_motion_loss |

## 文件和路径

- previous_probe_report_dir: `/Volumes/WD_BLACK/澜心社直播/项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V人物动作还原探针_wan_s2v_motion_reconstruction_probe`
- source_video_dir: `/Volumes/WD_BLACK/澜心社直播/参考/阿里定版视频/最新动作 3 视频`
- generated_candidate_dir: `/Volumes/WD_BLACK/澜心社直播/outputs/wan_s2v_motion_reconstruction_probe`
- contact_sheets_dir: `/Volumes/WD_BLACK/澜心社直播/outputs/wans2v_body_motion_failure_audit/contact_sheets`，只读临时审计图，不提交。

## 安全边界

- new_video_generated: `false`
- paid_api_called: `false`
- local_fallback_used: `false`
- media_committed: `false`
- signed_url_written: `false`
- `.env` touched: `false`
