# 源视频身体动作强度审计

状态：`source_body_motion_audit_completed_metric_limited`

## 方法说明

`已确认`：本轮没有使用 MediaPipe；本机可用 `OpenCV`。指标为 `visual_observation_and_frame_diff_metric_limited`，用于辅助判断，不等同于人体关键点真值或用户人审。

评分逻辑：每 0.5 秒抽帧，对相邻帧做画面差分，并结合 contact sheet 目视复核。最终 `body_motion_score` 是严格大幅身体动作评分，重点看身体框/重心/躯干是否有明显变化；3.5/5 以上才算大幅身体移动。原始帧差容易被手臂、嘴部、压缩噪声放大，只作为 `raw_frame_diff_*` 辅助字段，不作为主判断。

`hand_only_motion_ratio` 越高，越说明动作主要来自手部/边缘而非躯干整体。

## 源视频扫描结果

| source_id | full_video_has_large_body_motion | max_body_motion_time_range | max_body_motion_score | selected_segment_body_motion_score | clip_selection_judgement | recommended_reselect_range |
| --- | --- | --- | --- | --- | --- | --- |
| source_01 | False | 50.0-65.0s | 2.5 | 2.2 | not_clip_selection_issue_source_has_only_moderate_upper_body_motion | 50.0-65.0s_if_testing_upper_body_only_not_true_large_body |
| source_02 | False | 28.0-43.0s | 1.8 | 1.6 | not_clip_selection_issue_source_is_bridge_pose_hold | no_reselect_for_large_body_supplement_new_large_motion_sample |
| source_03 | False | 0.0-15.0s | 2.4 | 2.4 | not_clip_selection_issue_selected_segment_is_representative | 0.0-15.0s_already_representative_not_true_large_body |

## 逐条观察

- `source_01`：全片有上身晃动、手势、头肩节奏，50-65s 一带上肢动作更明显；但仍主要是站立讲解中的上半身和手部表达，不是走动/转身/站坐转换。
- `source_02`：桥式躺卧姿态保持为主，身体姿态大结构稳定；动作更多来自手、头和小幅姿态变化。
- `source_03`：坐球姿态保持为主，0-15s 已覆盖主要手臂下压/外展和肩部变化；不是全身位移型大动作。
