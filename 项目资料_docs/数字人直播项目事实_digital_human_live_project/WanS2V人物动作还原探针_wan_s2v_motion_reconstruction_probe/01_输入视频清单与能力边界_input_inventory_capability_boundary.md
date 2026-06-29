# 输入视频清单与能力边界

状态：`source_inventory_completed_capability_boundary_confirmed`

## 输入视频清单

| source_id | 文件名 | 时长 | fps | 编码 | 音轨 | 本轮片段 |
| --- | --- | ---: | ---: | --- | --- | --- |
| source_01 | `7月15下午二号机位.MP4` | 65.022354s | 59.94 | h264 | pcm_s16be stereo | 0-15s |
| source_02 | `25年9.10视频号无违规.MP4` | 50.543160s | 50.0 | h264 | pcm_s16be stereo | 0-15s |
| source_03 | `C5834（上）.MP4` | 26.526680s | 50.0 | h264 | pcm_s16be stereo | 0-15s |

`已确认`：3 个源视频均可读、可解码、有音轨。源文件像素为 1920x1080 且带 `rotation=-90`，显示方向按竖屏处理。

## 本轮输入准备

- 参考帧：每条视频取 0.5 秒附近画面，标准化为 720x1280 JPG。
- 输入音频：每条视频取 0-15 秒原音频，转为 16kHz mono WAV。
- 本地工具标签：`audit_or_input_preparation_not_fallback`
- 说明：上述处理只用于 Wan-S2V 输入准备与审计，不是最终视频修复。

## Wan-S2V 能力边界

`已确认`：当前项目 registry、上一轮真实请求记录和本轮运行脚本均使用：

```json
{
  "model": "wan2.2-s2v",
  "input": {
    "image_url": "public image URL",
    "audio_url": "public audio URL"
  },
  "parameters": {
    "resolution": "720P"
  }
}
```

`已确认`：本轮没有发送 `prompt`、`negative_prompt`、`video_url`、`motion_reference` 或 `video reference` 字段。

`已确认`：本轮真实路线是 `image_url + audio_url + resolution`，不是视频动作参考路线。

`部分成立`：Wan-S2V 可生成短数字人口播候选。

`待验证`：Wan-S2V 是否存在另一个可用 API 路线支持视频动作参考；当前仓库和本轮执行未证实。

## 不能写成的结论

- 不能写 `1_to_1_completed`
- 不能写 `human_review_passed`
- 不能写 `supplier_accepted`
- 不能写 `motion_reconstruction_passed_business`
- 不能把首帧 + 音频近似生成写成源视频动作复刻
