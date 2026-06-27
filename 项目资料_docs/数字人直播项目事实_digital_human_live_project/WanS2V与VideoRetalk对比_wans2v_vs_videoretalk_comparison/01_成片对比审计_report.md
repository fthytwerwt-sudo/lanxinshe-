# 01_成片对比审计报告

状态：`completed_report_only_comparison_pending_human_review`

## 主结论

`已确认`：当前项目内可分清三类结果：

1. `wan_raw_model_output`：Wan 720P 原始直出已生成，但 `mouth_face_ratio_p90=0.08985602706670762`，超过项目通过线 `0.075`。
2. `wan_local_postprocessed_output`：后处理版指标通过，但使用了本地嘴部区域垂直压缩 + feather 融合，不能代表 Wan-S2V 原生能力。
3. `videoretalk_model_output`：VideoRetalk 使用 A 声音克隆输入，任务 `SUCCEEDED`，无本地嘴部/视频后处理；动作、表情、直播感观察更强，但硬指标仍提示嘴部开合偏大风险。

`待验证`：用户人审、供应商验收、30 秒 / 60 秒扩展稳定性。

## 证据来源

- VideoRetalk：`项目资料_docs/数字人直播项目事实_digital_human_live_project/VideoRetalk_A声音金标准小球15秒重跑_videoretalk_final30_voice_gold_product_ball/`
- Wan / Wan-S2V：`项目资料_docs/数字人直播项目事实_digital_human_live_project/正面15秒小球口播样片_front_15s_product_ball_sample/`
- Wan 探针阶段：commit `a71e223c99673369d8b613ea83811af0601c9b63`
- Wan 原始口型未过线记录：commit `835205b1edc77616d906ab4537ceeefa074c1b1e`
- Wan 本地后处理过线记录：commit `f9a55fd995a876e8b9c3b88d0f97ab4b27ac2e58`
- 本轮结构化数据：`data/comparison_metrics.csv`、`data/comparison_manifest.json`

## 横向对比

| 维度 | Wan 原始模型输出 | Wan 本地后处理输出 | VideoRetalk 模型输出 |
|---|---|---|---|
| 口型幅度 | `部分成立`：`p90_mouth_open_ratio=0.2891281092255942` 低于 0.32，但 `mouth_face_ratio_p90=0.08985602706670762` 超过 0.075，用户指出的“口型偏大”有当前指标证据。 | `已确认`：技术指标被压到 `p90_mouth_open_ratio=0.10403372181307027`、`mouth_face_ratio_p90=0.030434972047805795`，但这是本地压嘴结果。 | `部分成立`：`p90_mouth_open_ratio=0.355425`、`mouth_face_ratio_p90=0.11274` 超阈值；Qwen-VL 观察为基本同步，但硬指标仍有口型偏大风险。 |
| 口型同步 | `待验证`：当前报告主要证明口型幅度和可播放，未证明完整音画同步人审通过。 | `部分成立`：最终版报告写入 Qwen-VL 观察为节奏平稳，但因后处理参与，不能代表原生同步能力。 | `部分成立`：Qwen-VL max/plus 均观察为口型与声音基本同步，无明显错位；但 `lipsync_metric_passed=false`。 |
| 动作自然度 | `部分成立`：Wan 后处理版 Qwen-VL 观察包含正面稳定、轻微点头、手部不遮挡；原始直出单独观感仍需人审。 | `部分成立`：动作看起来较稳，但可能存在局部压缩痕迹，需要用户看最终 MP4。 | `已确认`：报告观察到坐姿、合掌、指向头部、比划数字、微笑、眨眼等直播动作，直播感强于 Wan 正面静态口播样片。 |
| 人脸稳定性 | `部分成立`：正面固定参考帧降低风险，但原始口型比例超线。 | `待验证`：局部嘴部压缩可能引入边缘痕迹，必须人审。 | `部分成立`：Qwen-VL 观察表情自然、动作流畅；未见报告中的明显脸漂或五官变形结论。 |
| 声音一致性 | `待验证`：使用 `longyingxiao_v3` TTS，不是 A 声音克隆。 | `待验证`：同上，不是 A 声音克隆。 | `已确认`：使用 A 音频创建 custom `voice_id` 后合成小球文案；未使用 fallback TTS 和禁用声音。 |
| 可扩展性 | `待验证`：原始口型未过线，继续扩 30/60 秒前需要先解决模型侧/输入侧口型压幅。 | `不作为默认路线`：技术上可扩，但属于本地兜底，不得作为模型能力路线。 | `部分成立`：声音一致性和动作自然度更适合继续测试，但当前硬指标仍需口型风险复核。 |

## Wan-S2V 哪些地方好

- `已确认`：Wan 720P 原始直出真实生成过，不再只是探针配置。
- `部分成立`：正面构图、闭嘴/微闭参考帧、低强度口播路线能让人物保持稳定，后处理版的模型辅助观察显示头肩动作、眼神和手部遮挡风险较低。
- `部分成立`：用户主观方向认为 Wan-S2V 其余部分不错，本轮指标也显示原始输出的 `p90_mouth_open_ratio=0.2891281092255942` 未超过 0.32；主要问题集中在 mouth-to-face 比例偏大。

## Wan-S2V 口型幅度问题在哪里

`已确认`：Wan 原始输出的失败点不是全片大量爆口，而是嘴部相对脸高的比例偏大：

- `raw_p90_mouth_open_ratio=0.2891281092255942`，低于 0.32。
- `raw_fail_frame_percent=2.9914529914529915`，低于 15%。
- `raw_longest_fail_streak=4`，低于连续失败线。
- `raw_p90_mouth_face_ratio=0.08985602706670762`，高于 0.075。

这说明 Wan-S2V 值得继续尝试，但下一步要优先压 `mouth_face_ratio_p90`，而不是盲目做整体修嘴。

## VideoRetalk 哪里更稳

- `已确认`：A 声音克隆链路成立，最终输入音频 `-18.97 LUFS`，接近 A 声音金标准。
- `已确认`：VideoRetalk 最终 MP4 可播放、有声音、时长约 15 秒，没有本地嘴部/视频后处理。
- `部分成立`：Qwen-VL max/plus 都观察到口型基本同步、表情自然、手势丰富，更接近直播间动作状态。
- `待验证`：硬指标 `p90_mouth_open_ratio=0.355425`、`mouth_face_ratio_p90=0.11274` 仍超阈值，不能直接写成口型质量完全通过。

## 不能混写的结论

- `Wan 本地后处理输出` 不能写成 `Wan 原始模型能力通过`。
- `VideoRetalk 任务 SUCCEEDED` 不能写成 `人审通过` 或 `供应商验收通过`。
- `ffprobe 可解码、有音轨` 不能写成内容、审美、人感通过。
- `Qwen-VL 辅助观察` 只能作为模型辅助观察，不是用户人工审核。

## 本轮只读审计边界

本轮没有重新生成 Wan-S2V 视频，没有重新生成 VideoRetalk 视频，没有做本地嘴部压缩、局部修嘴、羽化融合、换音轨、补帧或画面后处理。

本轮使用 `ffprobe/ffmpeg` 的唯一用途是通过 `video-metadata-probe` 做只读元数据和解码验证，标记为：

```text
audit_or_input_preparation_not_fallback
```
