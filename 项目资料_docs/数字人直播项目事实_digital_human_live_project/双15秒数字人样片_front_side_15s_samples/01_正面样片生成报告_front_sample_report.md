# 01_正面样片生成报告

状态：`front_video_created` / `technical_validation_passed` / `content_validation_pending_human_review`

## 样片信息

| 字段 | 值 |
| --- | --- |
| output_video | `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/01_front_15s_sample.mp4` |
| source_video | `参考/完整直播录屏/今年直播素材/C5824.MP4` |
| source_time_range | `00:01:00-00:01:15` |
| reference_frame_time | `00:01:00` |
| audio_time_range | `00:01:00-00:01:15` |
| duration | 14.812500 |
| resolution | 512x896 |
| fps | 16.000 |
| video_codec | h264 |
| audio_codec | aac |
| has_audio | true |

## 选择理由

- `R02_C5824_C01_opening` 是项目事实目录中标记为 `baseline_avatar_state_reference` 的高质量 opening 候选，质量分为 `5.0`。
- 候选片段用于验证正脸稳定、眼神、口型、牙齿、眨眼和基础直播口播状态。
- 参考帧为正面、脸部清晰、无遮挡；但存在露齿微笑，因此牙齿和张嘴幅度必须重点复核。

## qwen-vl-max 辅助观察

````json { "face_visibility": "high", "mouth_visibility": "high", "eye_visibility": "high", "mouth_open_state": "variable", "teeth_visibility": "variable", "blink_naturalness": "natural", "head_motion": "moderate", "shoulder_motion": "moderate", "body_motion": "moderate", "gesture_presence": "high", "occlusion_risk": "low", "reference_frame_suitability": "high" } ````

## 生成后本地目视观察

- 正面口型：有连续开合，动态同步需要人工观看完整 MP4 判断。
- 正面张嘴幅度：部分帧张嘴较明显，存在需复核风险。
- 正面眼神：contact sheet 中基本面向镜头。
- 正面眨眼：技术抽帧无法充分判断，待人工观看动态。
- 正面牙齿：部分帧可见，需要重点复核是否自然。
- 正面头肩动作：有轻微头肩和手部动作，不是完全静止。
- 手势 / 遮挡：手部在胸前小幅动作，未见严重挡脸。
- 声音节奏：使用原始直播音频 15 秒，已做响度统一；未做人耳听辨通过。

## 风险

- `content_validation_pending_human_review`：模型与抽帧只能辅助观察，不能替代人审。
- `teeth_visibility_review_needed`：正面参考帧露齿，生成视频牙齿自然度需人工重点看。
- `lip_sync_review_needed`：有音轨和口型动作，但口型同步不能只凭 ffprobe 判断。
