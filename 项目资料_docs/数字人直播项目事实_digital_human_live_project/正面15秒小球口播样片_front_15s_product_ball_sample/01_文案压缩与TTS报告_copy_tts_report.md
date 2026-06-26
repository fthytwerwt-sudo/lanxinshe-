# 01_文案压缩与 TTS 报告

状态：`tts_created`

## 源文案

```text
品质真是不一样，姐妹给你们看一下，这是便宜的小球，我给你们也买回来了，除了便宜一无是处，软软塌塌的，是塑料材质，承重标 200 斤实际只有 180 斤。我们家这个三层加厚、防爆防压，承重能力 400 斤，能用三年，我还给你准备一年质量保险，一年内球有任何问题我都给你解决。材料用的是 PVC 进口母婴级材质，没有异味，用着放心。
```

## 实际 15 秒口播文案

```text
品质真是不一样。便宜小球软塌塌，塑料材质。我家三层加厚、防爆防压，承重400斤，母婴级PVC，没有异味，用着更放心。
```

## 压缩与 TTS

- cut_reason: `保留了关键信息，如价格低廉但质量差、三层加厚、防爆防压、承重能力强、材质安全等，去掉了不必要的细节和承诺。`
- short_spoken_copy_length: `58`
- tts_model: `cosyvoice-v3-flash`
- tts_voice: `longyingxiao_v3`
- speech_rate: `0.88`
- retry_mode: `yes`
- tts_volume: `24`
- raw_tts_duration: `14.823125`
- normalized_tts_duration: `14.823125`
- normalization: `volume=-8dB + light compressor`
- audio_output: `/Volumes/WD_BLACK/澜心社直播/outputs/front_15s_product_ball_mouth_control/input_front_product_audio_normalized.wav`

## 风险

- `一年质量保险` 因 15 秒时长限制未进入实际口播版。
- TTS 通过只表示音频文件生成和时长符合，不等于声音克隆、人声相似度或用户听感通过。
