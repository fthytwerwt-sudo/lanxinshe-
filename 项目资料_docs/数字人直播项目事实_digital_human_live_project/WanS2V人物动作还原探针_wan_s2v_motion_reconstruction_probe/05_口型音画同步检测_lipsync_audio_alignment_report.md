# 口型与音画同步检测

状态：`technical_audio_present_mouth_metric_risk_pending_human_review`

## 检测范围

本轮检测只覆盖：

- 生成视频是否有音轨。
- 视频是否可解码。
- 抽帧后嘴部幅度粗指标。
- contact sheet 可见的口播动作观察。

本轮没有做：

- ASR 转写。
- 音素级 lip-sync 对齐。
- 用户人审。
- 本地修嘴或压嘴。

## 技术音轨结果

| candidate_id | duration_sec | has_audio | audio_codec | decode |
| --- | ---: | --- | --- | --- |
| candidate_01_from_source_01 | 14.8 | true | aac | passed |
| candidate_02_from_source_02 | 14.8 | true | aac | passed |
| candidate_03_from_source_03 | 14.8 | true | aac | passed |

## 嘴部粗指标

采样方式：生成视频按 8fps 抽帧，使用 Swift Vision landmark 检测嘴部幅度。

| candidate_id | detected / frames | p90_mouth_open_ratio | p90_mouth_face_ratio | fail_frame_percent | longest_fail_streak | 说明 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| candidate_01_from_source_01 | 118 / 118 | 0.494641 | 0.161177 | 22.881356 | 2 | 嘴部幅度偏大，风险高 |
| candidate_02_from_source_02 | 51 / 118 | 0.427937 | 0.166902 | 9.322034 | 3 | 躺卧角度导致检测失败多，指标可靠性低 |
| candidate_03_from_source_03 | 118 / 118 | 0.312242 | 0.093330 | 3.389831 | 1 | 三条里最好，但 `p90_mouth_face_ratio` 仍高于既有 0.075 参考线 |

## 结论

`已确认`：3 条候选都有音轨且可播放。

`部分成立`：可见口播动作存在，尤其 `candidate_03` 嘴部幅度相对最稳。

`待验证`：音画同步是否达到用户人审标准仍未确认。

`已确认`：本轮不能写 `lip_sync_passed`，只能写 `mouth_metric_risk_pending_human_review`。
