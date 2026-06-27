# 01_输入素材与文案锁定_input_lock_report

状态：`input_locked_voice_clone_generated`

## 文案锁定

```text
品质真是不一样，姐妹们看这个便宜小球软塌塌的塑料感很重。我们家三层加厚防爆防压，承重四百斤，母婴级PVC没有异味，我还给你准备一年质量保险，用着更放心。
```

## 声音锁定

| 字段 | 值 |
| --- | --- |
| voice_source | `A_voice_clone_custom_voice_id` |
| voice_id | `cosyvoice-v3-flash-lxsvoice-9c8f0311c79a4b7584033a505cee576b` |
| tts_model | `cosyvoice-v3-flash` |
| input_audio_path | `/Volumes/WD_BLACK/澜心社直播/outputs/wans2v_yoga_ball_product_ball_native_probe/input_audio_A_voiceclone_product_ball.wav` |
| input_audio_duration_sec | `15.309313` |
| fallback_tts_used | `false` |
| forbidden_preset_voice_used | `false` |
| ASR_match | `待验证_asr_not_run; exact_text_was_submitted_to_A_voice_clone_tts` |

`已确认`：本轮重新调用 A voice clone `voice_id` 合成了同款小球文案，未回退 preset voice。

`待验证`：本轮没有额外跑 ASR；因此只能确认 TTS 请求文本与目标文案一致，不能把 ASR_match 写成已通过。

## 参考素材锁定

| 字段 | 值 |
| --- | --- |
| selected_reference_video | `/Volumes/WD_BLACK/澜心社直播/参考/C5835（下）.MP4` |
| selected_reference_sha256 | `59fd8addb96b970d83f2c0de9ed5a2aee083ebf8bf26c40b6071e6adb76761f9` |
| archive_reference_candidate | `/Volumes/WD_BLACK/澜心社直播/参考/完整直播录屏/直播效果一般/C5835（下）.MP4` |
| archive_sha256 | `e3e22684bbf3365952ba6a780c2c9a82a9c86d3ecc23b64d7c4e00eb47ad6b31` |
| selection_reason | `根目录参考短片与用户标识精确匹配；长母带仅作为同名来源旁证，不作为输入。` |

## 输入准备边界

- 抽帧、720x1280 标准化、输入音频 -4dB 版本均属于 `audit_or_input_preparation_not_fallback`。
- 没有对 Wan-S2V 输出视频做换音轨、压嘴、补帧、局部融合或画面修复。
