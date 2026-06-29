# 生成结果身体动作还原对比

状态：`generated_body_motion_comparison_completed`

## 结论

`已确认`：3 条生成候选的身体动作强度均低于或明显偏离上一轮 selected segment；生成结果更接近“参考帧姿态 + 音频驱动的轻动作口播”，不是源视频动作时间线复刻。

`已确认`：由于上一轮 `true_video_motion_reference_used=false`，这些差距不能只写成模型没有学会片段动作，而应写成当前调用路线没有接收动作参考，生成丢动作符合路线预期。

## 对比表

| source_id | candidate_id | selected_segment_body_motion_score | generated_body_motion_score | motion_retention_ratio | stiffness_detected | failure_cause |
| --- | --- | --- | --- | --- | --- | --- |
| source_01 | candidate_01_from_source_01 | 2.2 | 0.8 | 0.3636 | True | source_has_only_moderate_upper_body_motion_plus_model_route_limitation_and_generation_motion_loss |
| source_02 | candidate_02_from_source_02 | 1.6 | 0.7 | 0.4375 | True | source_pose_hold_plus_model_route_limitation_and_generation_motion_loss |
| source_03 | candidate_03_from_source_03 | 2.4 | 1.0 | 0.4167 | True | selected_segment_representative_but_model_route_limitation_and_generation_motion_loss |

## 逐条判断

- `candidate_01_from_source_01`：身体/手势时间线塌缩最明显，接近站立静态口播。
- `candidate_02_from_source_02`：粗躺卧姿态保留，但桥式动态和手势节奏未成为时间线跟随。
- `candidate_03_from_source_03`：坐球构图和人脸较稳，但双手下压/外展和肩部节奏没有跟随源片。
