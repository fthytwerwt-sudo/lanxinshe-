# 03_WanS2V生成报告_wans2v_generation_report

状态：`three_native_candidates_generated_no_local_postprocess`

## API 能力边界

`已确认`：当前项目脚本和官方 Wan-S2V API 文档使用 `image_url`、`audio_url`、`parameters.resolution`。本轮没有发送 `prompt` 或 `negative_prompt` 字段，避免伪造模型控制能力。

- official_doc: `https://help.aliyun.com/zh/model-studio/wan-s2v-api`
- prompt_sent_to_api: `false`
- negative_prompt_sent_to_api: `false`

## 候选生成记录

| candidate_id | pass_status | duration_sec | has_audio | yoga_ball_visible | action_alignment_score | mouth_face_ratio_p90 | p90_mouth_open_ratio | fail_frame_percent | longest_fail_streak | failed_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_A | failed_hard_threshold | 15.133333 | True | True | 5 | 0.08387625366449357 | 0.26871763138799404 | 0.4132231404958678 | 1 | mouth_face_ratio_p90_above_0.075 |
| candidate_B | failed_hard_threshold | 15.133333 | True | True | 4 | 0.09159099757671357 | 0.31659181841866296 | 1.6528925619834711 | 1 | mouth_face_ratio_p90_above_0.075 |
| candidate_C | failed_hard_threshold | 15.133333 | True | True | 4 | 0.10744787603616715 | 0.352648331699753 | 7.851239669421488 | 4 | p90_mouth_open_ratio_above_0.32;mouth_face_ratio_p90_above_0.075 |

## 候选设计差异

| candidate | 设计目的 | 输入差异 |
| --- | --- | --- |
| candidate_A | 基础版：球可见 + 讲解动作 + 低口型参考 | `frame_008` + 原始 A voice clone 音频 |
| candidate_B | 口型压幅版 | `frame_002` + A voice clone 音频整体 -4dB |
| candidate_C | 脸和球放大版 | `frame_008 tight crop` + 原始 A voice clone 音频 |

## 不通过原因

三条候选均生成成功、带音轨、可播放、有瑜伽球，但都没有通过 `mouth_face_ratio_p90 <= 0.075`。

- Candidate A 最接近：`mouth_face_ratio_p90=0.08387625366449357`。
- Candidate B：`mouth_face_ratio_p90=0.09159099757671357`，降音量没有改善比例。
- Candidate C：`p90_mouth_open_ratio=0.352648331699753` 且 `mouth_face_ratio_p90=0.10744787603616715`，紧裁后口型反而更大。
