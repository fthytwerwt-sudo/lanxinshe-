# 01_声音来源与文案报告_voice_and_copy_report

状态：`fallback_generated_tts_used`

## 源文案

```text
不一样，姐妹给你们看一下，这是便宜的小球，我给你们也买回来了，除了便宜一无是处，软软塌塌的，是塑料材质，承重标 200 斤实际只有 180 斤。我们家这个三层加厚、防爆防压，承重能力 400 斤，能用三年，我还给你准备一年质量保险，一年内球有任何问题我都给你解决。材料用的是 PVC 进口母婴级材质，没有异味，用着放心。
```

## 实际播报文案

```text
品质真是不一样。姐妹们看这个便宜小球，软塌塌的，塑料感很重。我们家三层加厚、防爆防压，承重 400 斤，母婴级 PVC，没有异味，用着放心。
```

## 声音来源判断

| 字段 | 结果 |
|---|---|
| input_audio_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_audio_for_videoretalk.wav` |
| input_audio_source | `fallback_generated_tts` |
| audio_source_level | `C` |
| voice_match_level | `low_not_user_voice` |
| voice_mismatch_reason | `generated_tts_used_instead_of_user_provided_voice` |
| TTS model | `cosyvoice-v3-flash` |
| TTS voice | `longanxuan_v3` |
| speech_rate | `0.65` |
| pitch_rate | `0.98` |
| tts_volume | `22` |
| input_audio_duration | `14.210625` |

## 为什么不是用户声音

`已确认`：附件目录只有文本，没有音频文件。

`已确认`：仓库中存在直播录屏抽取声样和火山音色候选声样，但这些不是“小球文案”的目标音频。

`待验证`：火山候选声样是否已经上传并创建可调用音色；当前仓库未发现可直接调用的 voice clone `voice_id` 或 API 路径。

因此本轮按执行单 C 路线生成完整视频，但必须标：`voice_match_level=low_not_user_voice`。

## 音频处理

- TTS 原始音频：`outputs/videoretalk_final_product_ball_15s/tts_attempt_longanxuan_v3_inspection_retry_no_weight_r065.wav`
- 最终输入音频：`/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_audio_for_videoretalk.wav`
- 处理：`ffmpeg volume=-3dB, acompressor threshold=-18dB ratio=1.6, mono 16kHz pcm_s16le wav`
- 输出视频音轨：AAC stereo 44.1kHz，由 VideoRetalk 对输入 WAV 转码封装。
- 输入/输出音轨追踪：零延迟粗相关 `0.967707231255033`，非字节一致，原因是输出视频音轨为 AAC stereo 44.1kHz。

## 下一轮强制使用用户指定声音

1. 把用户本人按小球文案录好的目标音频放到明确路径，例如 `inputs/user_voice/product_ball_15s.wav`。
2. 生成前必须先 `ffprobe` 该音频，并把 `input_audio_source=user_provided_target_copy_audio` 写入 manifest。
3. VideoRetalk 命令只允许使用这个音频路径上传，不允许 fallback TTS。
4. 如果只有声样没有目标文案音频，必须先创建/验证 voice clone `voice_id`，再用该 voice clone 合成小球文案；否则 blocked，不再偷偷 fallback。
