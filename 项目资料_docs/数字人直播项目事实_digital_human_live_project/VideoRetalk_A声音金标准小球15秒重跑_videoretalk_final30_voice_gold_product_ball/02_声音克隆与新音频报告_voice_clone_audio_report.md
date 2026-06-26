# 02_声音克隆与新音频报告_voice_clone_audio_report

`已确认`：本轮没有使用 fallback TTS，没有使用 `longanxuan_v3`，也没有使用 `longyingxiao_v3`。最终音频由 A 声音克隆 voice_id 生成。

| 字段 | 值 |
|---|---|
| voice_clone_service | `Alibaba DashScope VoiceEnrollmentService` |
| target_model | `cosyvoice-v3-flash` |
| voice_id | `cosyvoice-v3-flash-lxsvoice-9c8f0311c79a4b7584033a505cee576b` |
| voice_clone_source_audio | `/Volumes/WD_BLACK/澜心社直播/outputs/audio_source_comparison_final30_vs_videoretalk/A_final30_audio_extracted.wav` |
| fallback_tts_used | `False` |
| forbidden_voices_used | `none` |
| spoken_copy | `品质真是不一样，姐妹们看这个便宜小球软塌塌的塑料感很重。我们家三层加厚防爆防压，承重四百斤，母婴级PVC没有异味，我还给你准备一年质量保险，用着更放心。` |
| input_audio_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/input_audio_voiceclone_product_ball_final15.wav` |
| input_audio_duration_sec | `15.309313` |
| input_audio_integrated_lufs | `-18.97` |
| true_peak_dbfs | `-2.0` |
| pause_density_minus30db_percent | `9.498` |

## 处理说明

- 做了：声音克隆合成、`loudnorm` 响度归一化、16kHz 单声道 PCM WAV 重采样/转码。
- 未做：低匹配 fallback TTS、`longanxuan_v3`、`longyingxiao_v3`、本地嘴部后处理、局部修嘴、羽化融合。
- 文案调整原因：第一次 VideoRetalk 任务因 `DataInspectionFailed` 失败，最终版删除“200 斤实际偏弱”高风险对比句，保留三层加厚、防爆防压、400斤、母婴级 PVC、无异味、一年质量保险等核心卖点。
