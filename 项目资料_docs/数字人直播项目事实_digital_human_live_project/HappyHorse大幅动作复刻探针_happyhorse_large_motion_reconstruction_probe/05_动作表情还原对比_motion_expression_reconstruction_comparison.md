# 动作表情还原对比

状态：`motion_expression_comparison_completed_pending_human_review`

## 评分说明

1-5 分为 Codex 基于 contact sheet 的视觉辅助评分，不是用户人审。`4` 以上表示可进入人审；`3-3.9` 表示部分成立；低于 `3` 表示不建议继续同路线。

| source_id | candidate_id | generation_status | motion_reference_used | expression_reference_used | body_motion_similarity | hand_gesture_similarity | facial_expression_similarity | micro_expression_similarity | lip_sync_quality | naturalness | identity_stability | overall_reconstruction_score | pass_status | failed_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_01 | candidate_01_from_source_01 | SUCCEEDED | True | True | 4.4 | 4.1 | 4.0 | 3.6 | 4.2 | 4.1 | 4.3 | 4.1 | near_1_to_1_reconstruction_partial_pending_human_review |  |
| source_02 | candidate_02_from_source_02 | SUCCEEDED | True | True | 4.0 | 3.7 | 3.2 | 2.8 | 3.3 | 3.8 | 3.8 | 3.5 | partial_motion_reconstruction_oblique_face_risk_pending_human_review |  |
| source_03 | candidate_03_from_source_03_rescue | SUCCEEDED | True | True | 4.2 | 4.0 | 3.8 | 3.4 | 4.1 | 4.0 | 4.2 | 4.0 | near_1_to_1_reconstruction_partial_pending_human_review |  |
| source_03 | candidate_03_from_source_03_initial_not_selected | SUCCEEDED | True | True | 4.0 | 3.8 | 3.6 | 3.2 | 4.0 | 3.2 | 3.5 | 3.4 | not_selected_prompt_scene_mismatch | initial prompt incorrectly requested green-screen scene, causing background mismatch |

## 观察结论

- source_01：`near_1_to_1_reconstruction_partial_pending_human_review`。站姿、腰胯手位、头肩和表情节奏最接近。
- source_02：`partial_motion_reconstruction_oblique_face_risk_pending_human_review`。桥式姿态和腿部结构保留，但微表情/口型低置信。
- source_03：纠错版进入最终候选，坐姿、小球、双手动作和背景道具保留较好。
- source_03 初版：不作为最终候选，原因是 prompt 场景错误导致背景变绿。

## 与 Wan-S2V 当前路线对比

`部分成立`：HappyHorse `video-edit` 比 Wan-S2V 当前 `image_url + audio_url` 路线更适合保留动作时间线。关键差异不是模型审美，而是本轮 HappyHorse 实际接收了源视频输入。
