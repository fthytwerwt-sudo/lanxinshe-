# 03_语音音色与说话方式总报告

状态：`voice_analysis_partial` / `local_only_analysis_not_committed`

## 主结论

- `已确认`：有音频的视频均生成声音候选记录，共 55 条。
- `已确认`：`qwen2.5-omni-7b` 调用 8 次，用于少量音视频综合辅助观察。
- `部分成立`：本地音频统计可判断音量、活跃比例、停顿密度，但不能替代人工听辨、ASR 转写或声音克隆验收。

## 声音候选摘要

| voice_clip_id | source_video | time_range | 速度 | 音量 | 克隆适配 | 风险 |
| --- | --- | --- | --- | --- | --- | --- |
| V_R01_5_13_C01_opening | 参考/完整直播录屏/今年直播素材/5月13日直播素材.MP4 | 00:01:00-00:01:06 | 偏慢/停顿多/音量低_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R01_5_13_C02_middle | 参考/完整直播录屏/今年直播素材/5月13日直播素材.MP4 | 00:55:10-00:55:16 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R01_5_13_C03_high_motion | 参考/完整直播录屏/今年直播素材/5月13日直播素材.MP4 | 01:23:05-01:23:11 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R01_5_13_C04_high_audio | 参考/完整直播录屏/今年直播素材/5月13日直播素材.MP4 | 00:56:30-00:56:36 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R01_5_13_C05_closing | 参考/完整直播录屏/今年直播素材/5月13日直播素材.MP4 | 01:48:51-01:48:57 | 偏慢/停顿多/音量低_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R02_C5824_C01_opening | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 00:01:00-00:01:06 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R02_C5824_C02_middle | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 00:49:09-00:49:15 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R02_C5824_C03_high_motion | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 01:02:08-01:02:14 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R02_C5824_C04_high_audio | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 01:37:38-01:37:44 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R02_C5824_C05_closing | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 01:36:48-01:36:54 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R03_C5825_C01_opening | 参考/完整直播录屏/今年直播素材/C5825.MP4 | 00:01:00-00:01:06 | 中等稳定_待听辨 | high_volume_or_loud_environment | candidate_need_manual_listening | needs_manual_listening_and_authorization_check |
| V_R03_C5825_C02_middle | 参考/完整直播录屏/今年直播素材/C5825.MP4 | 00:54:45-00:54:51 | 中等稳定_待听辨 | high_volume_or_loud_environment | audio_candidate_visual_face_limited | needs_manual_listening_and_authorization_check |

## 声音字段覆盖

- 已覆盖：音量变化、活跃比例、停顿密度、语速粗估、TTS 节奏参考候选、声音克隆候选风险。
- 待人工/ASR 复核：具体口头禅、语气词、逐句重音、背景噪声、多人重叠说话、真实音色是否适合克隆。
