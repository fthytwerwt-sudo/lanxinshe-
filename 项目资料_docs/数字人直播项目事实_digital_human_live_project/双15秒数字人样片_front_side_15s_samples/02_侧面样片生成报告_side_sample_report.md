# 02_侧面样片生成报告

状态：`side_video_created` / `technical_validation_passed` / `content_validation_pending_human_review`

## 样片信息

| 字段 | 值 |
| --- | --- |
| output_video | `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/02_side_15s_sample.mp4` |
| source_video | `参考/完整直播录屏/直播效果一般/C5834（上）.MP4` |
| source_time_range | `00:26:45-00:27:00` |
| reference_frame_time | `00:26:51` |
| side_angle_estimate | `约 30°-45° 偏侧 / 侧身回头，不是 90° 纯侧脸` |
| audio_time_range | `00:26:45-00:27:00` |
| duration | 14.812500 |
| resolution | 512x896 |
| fps | 16.000 |
| video_codec | h264 |
| audio_codec | aac |
| has_audio | true |

## 选择理由

- `R06_C5834_C02_middle` 在项目事实中标记为 `general_live_avatar_reference`，质量分为 `5.0`。
- 模型摘要已记录其存在侧向观众方向、轻微左右转动、头肩动作和手势，更贴合本轮偏侧/轻微转头验证目标。
- 参考帧为侧身回头角度，嘴、眼、脸仍清楚可见；不采用 90° 纯侧脸。

## qwen-vl-max / qwen-vl-plus 辅助观察

- qwen-vl-max：````json { "side_angle_degree_estimate": 45, "face_still_visible": true, "mouth_still_visible": true, "eye_still_visible": true, "head_turn_naturalness": "natural", "profile_distortion_risk": "low", "gesture_presence": "high", "occlusion_risk": "low", "side_reference_frame_suitability": "high" } ````
- qwen-vl-plus 参考帧复核：````json { "is_usable": true, "reason": "The frame shows a clear three-quarter view of the subject's face with visible mouth, eyes, and no severe occlusion. The angle is within the 30-45 degree range, making it suitable for a digital human reference." } ````

## 生成后本地目视观察

- 侧面口型：contact sheet 显示偏侧口型开合，动态同步需人工观看完整 MP4 判断。
- 侧面脸部稳定：抽帧未见严重脸崩，脸部仍清楚可见。
- 侧面转头：保持侧身回头 / 偏侧状态，符合本轮非 90° 纯侧脸要求。
- 侧面头肩动作：有轻微身体和头肩动态。
- 手势 / 遮挡：存在手势动作，未见长期挡脸；手部自然度需人工看动态。
- 声音节奏：使用同段直播音频 15 秒，已做响度统一；未做人耳听辨通过。

## 风险

- `content_validation_pending_human_review`：技术生成成功不等于偏侧口型、人感或供应商验收通过。
- `mouth_open_amplitude_review_needed`：偏侧样片部分帧嘴巴开合偏大，需要重点复核。
- `gesture_naturalness_review_needed`：侧面样片包含手势，需人工看是否有穿帮或僵硬。
