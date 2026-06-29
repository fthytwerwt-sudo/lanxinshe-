# WanS2V 能力边界判断

状态：`capability_boundary_judgement_completed`

## 必答结论

- 是否使用 true video motion reference：`已确认 false`
- 上一轮实际输入：`image_url + audio_url + resolution`
- 是否发送 `video_url` / `motion_reference`：`已确认 false`
- 是否支持 prompt：`当前项目本轮路线未证实`
- 是否发送 prompt：`已确认 false`
- 是否能要求 1:1 身体动作复刻：`已确认 当前路线不能这样要求`

## 归因

`已确认`：本轮应写 `model_route_limitation_not_clip_selection_issue` 作为主判断。原因不是“模型看了视频但没复刻”，而是上一轮根本没有把视频动作作为 motion reference 输入。

`部分成立`：`source_01` 存在上肢/上身轻动作片段可优化空间；但即使重选到最高动作段，只要调用仍是 `image_url + audio_url`，也只能验证“更动态参考帧/音频下是否略有自然动作”，不能验证 1:1 动作复刻。

## 当前路线适合什么

- 轻动作口播。
- 单张参考帧驱动的短数字人候选。
- 粗姿态保持、身份稳定、口播感观察。

## 当前路线不适合什么

- 大幅身体移动 1:1 复刻。
- 按源视频时间线还原手势、肩颈、重心、站坐、转身、侧移。
- 把真人动作视频作为动作模板迁移到新生成视频。

## 是否继续测 Wan-S2V 大动作

`通用建议`：如果目标仍是“身体大幅移动 / 动作复刻”，应优先寻找明确支持 `video motion reference` / `motion transfer` 的路线。只有在找到并证实该输入字段可用，或用户只想看 `image+audio` 路线能否自然生成一点轻动作时，才值得继续生成。
