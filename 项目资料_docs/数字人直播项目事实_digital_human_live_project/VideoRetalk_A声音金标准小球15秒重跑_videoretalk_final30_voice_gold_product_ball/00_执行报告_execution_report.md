# 00_执行报告_execution_report

状态：`completed_videoretalk_15s_sample_created_voice_clone_from_A_lipsync_metric_risk`

`已确认`：本轮已用 `final_30s_alibaba_fixed_template` 的 A 音频作为声音金标准，完成 ASR、声音克隆、目标小球文案音频生成，并用 VideoRetalk 生成最终 15 秒左右 MP4。

`部分成立`：成片可播放且有声音，Qwen-VL 主观观察为口型基本同步；但本地嘴部 landmark 指标未完全过线，因此不能写成“口型质量完全通过”。

| 字段 | 值 |
|---|---|
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/videoretalk_final30_voice_gold_product_ball_15s.mp4` |
| input_audio_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/input_audio_voiceclone_product_ball_final15.wav` |
| input_audio_source | `A_final30_voice_clone_generated_target_copy_audio` |
| voice_clone_enabled | `yes` |
| tts_fallback_used | `no` |
| forbidden_voices_used | `none` |
| videoretalk_task_id | `e72e8957-4064-4eec-8b40-a48eceb2624d` |
| videoretalk_status | `SUCCEEDED` |
| result_duration_sec | `15.06` |
| has_audio | `True` |
| postprocess_used | `no local mouth/video postprocess` |
| media_committed | `no` |

## 关键结论

1. A 音频不是小球文案，不能直接作为 `audio_url` 使用。
2. 已启用阿里 DashScope 声音克隆能力，以 A 音频创建自定义 voice_id，再生成小球文案音频。
3. 最终输入音频约 `-18.97 LUFS`，接近 A 的 `-19 LUFS`，明显不是 B 的 `-30.4 LUFS`。
4. 最终输入音频 -30dB 停顿比例约 `9.498%`，接近 A 的节奏层级，远低于 B 的 `47.37%`。
5. 第一条 VideoRetalk 因 `DataInspectionFailed` 失败；最终成功版本删除了“200 斤实际偏弱”这句高风险对比表述，保留核心卖点。
