# HappyHorse 连接与能力边界

状态：`happyhorse_video_edit_connected_i2v_motion_boundary_confirmed`

## 本地入口

`已确认`：当前仓库已有 HappyHorse 本地入口：

- `docs/happyhorse_i2v_connection.md`
- `scripts/check_happyhorse_i2v_connection.py`
- `.env` 中 `HAPPYHORSE_VIDEO_MODEL=happyhorse-1.0-i2v`

`已确认`：该入口是首帧图生视频 `i2v`，请求体为 `first_frame` 图片 + prompt + duration，不是 video/motion reference。

## 官方能力入口

`已确认`：本轮额外查阅阿里官方 HappyHorse 文档：

- https://help.aliyun.com/zh/model-studio/happyhorse-image-to-video-api-reference
- https://help.aliyun.com/zh/model-studio/happyhorse-video-edit-api-reference

`已确认`：`happyhorse-1.0-video-edit` 使用同类 DashScope 异步视频生成接口，输入媒体包含 `type=video`，可附加 `type=reference_image`。

## 本轮实际能力边界

- 是否支持 video reference：`已确认`，本轮发送 `type=video` 输入并成功。
- 是否支持 motion reference：`部分成立`，没有字段名叫 `motion_reference`，但输入视频实际承担动作时间线参考。
- 是否支持 expression reference：`部分成立`，没有单独 `expression_reference` 字段，但输入视频 + 首帧参考承担表情/身份参考。
- 是否支持 audio reference：`部分成立`，没有单独 `audio_reference` 字段；源音频嵌在输入视频中，输出音轨与源音频波形高度一致。
- 是否支持 prompt：`已确认`。
- 是否支持 15 秒：`已确认`，输出 15.018s。
- 是否需要公网 URL / OSS：`已确认`，本地 clip 和首帧通过 OSS signed URL 上传；报告只保留 redacted URL。
- generation_cost_guard：`已确认`，P0 授权上限 4 次；实际 3 次主任务 + 1 次 rescue。

## 能否称为 1:1 动作复刻

`部分成立`：可以称为 `near_1_to_1_reconstruction_partial_pending_human_review`，不能称为 `1_to_1_completed`。

原因：本轮是 HappyHorse `video-edit` 使用源视频作为输入，动作保留明显优于单图生成；但它不是“单图数字人 + motion transfer 到新身份”的完整能力证明，也未经过用户人审。
