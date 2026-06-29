# 上一轮片段选择复盘

状态：`selected_segment_review_completed`

## 结论

`已确认`：上一轮一律取 0-15s 不是“身体大幅移动缺失”的主因。`source_01` 后段有更明显的上肢/上身表达，但仍不是严格意义的大幅身体移动；`source_02` / `source_03` 的 0-15s 基本代表源片主体动作。

## 对比表

| source_id | full_video_best_range | previous_selected_range | body_motion_score_gap | was_previous_selection_good | recommended_reselect_range | reason |
| --- | --- | --- | --- | --- | --- | --- |
| source_01 | 50.0-65.0s | 0.0-15.0s | 0.3 | True | 50.0-65.0s_if_testing_upper_body_only_not_true_large_body | not_clip_selection_issue_source_has_only_moderate_upper_body_motion |
| source_02 | 28.0-43.0s | 0.0-15.0s | 0.2 | True | no_reselect_for_large_body_supplement_new_large_motion_sample | not_clip_selection_issue_source_is_bridge_pose_hold |
| source_03 | 0.0-15.0s | 0.0-15.0s | 0.0 | True | 0.0-15.0s_already_representative_not_true_large_body | not_clip_selection_issue_selected_segment_is_representative |

## 复盘判断

- `source_01`：如果只想测试上肢/上身轻动作，可试 `50.0-65.0s`；如果目标是身体大幅移动，重选片收益有限。
- `source_02`：0-15s 基本覆盖桥式主体姿态，不建议把失败主要归因于选片。
- `source_03`：0-15s 基本覆盖坐球动作主体，不建议把失败主要归因于选片。
