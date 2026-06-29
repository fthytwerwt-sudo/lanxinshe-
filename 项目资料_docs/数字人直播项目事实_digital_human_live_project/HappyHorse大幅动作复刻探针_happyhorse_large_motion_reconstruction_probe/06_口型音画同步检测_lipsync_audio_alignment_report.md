# 口型音画同步检测

状态：`lipsync_audio_alignment_technical_check_completed_pending_human_review`

## 技术检查

`已确认`：3 条最终候选均有 AAC 双声道音轨，时长约 `15.018s`，可解码。

| source_id | source_audio_duration | candidate_audio_duration | waveform_pearson_corr | rmse |
| --- | --- | --- | --- | --- |
| source_01 | 15.0 | 15.018 | 0.999495 | 0.004637 |
| source_02 | 15.0 | 15.018 | 0.999581 | 0.005842 |
| source_03 | 15.0 | 15.018 | 0.999532 | 0.005549 |

## 判断

`已确认`：候选音频与输入片段音频高度一致，说明 HappyHorse `video-edit` 输出保留了源音频轨道。

`部分成立`：由于音频高度保留且画面动作时间线接近，口型同步技术风险低于单图生成路线；但口型是否自然、微表情是否真实仍必须由用户看视频人审。

`待验证`：没有做本地嘴部修复，也没有用 MediaPipe/OpenCV 做口型后处理；本报告不写 `human_review_passed`。
