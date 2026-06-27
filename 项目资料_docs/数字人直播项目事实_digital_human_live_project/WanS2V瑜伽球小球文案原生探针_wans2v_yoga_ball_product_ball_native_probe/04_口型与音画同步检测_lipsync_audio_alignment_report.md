# 04_口型与音画同步检测_lipsync_audio_alignment_report

状态：`generated_but_failed_mouth_face_ratio_threshold`

## 检测口径

- metadata：`probe_video.sh` + `ffprobe`。
- 口型幅度：Swift Vision mouth landmark，对生成视频按 16fps 抽帧检测。
- 音频：确认输出视频有 AAC 音轨，输入音频来自 A voice clone。
- 音画同步：本轮没有独立 ASR/phoneme 级 lipsync 工具；Qwen-VL 的“动作/口型同步”只作视觉辅助，不等于严格 lipsync 通过。

## 口型指标

| candidate_id | pass_status | duration_sec | has_audio | yoga_ball_visible | action_alignment_score | mouth_face_ratio_p90 | p90_mouth_open_ratio | fail_frame_percent | longest_fail_streak | failed_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_A | failed_hard_threshold | 15.133333 | True | True | 5 | 0.08387625366449357 | 0.26871763138799404 | 0.4132231404958678 | 1 | mouth_face_ratio_p90_above_0.075 |
| candidate_B | failed_hard_threshold | 15.133333 | True | True | 4 | 0.09159099757671357 | 0.31659181841866296 | 1.6528925619834711 | 1 | mouth_face_ratio_p90_above_0.075 |
| candidate_C | failed_hard_threshold | 15.133333 | True | True | 4 | 0.10744787603616715 | 0.352648331699753 | 7.851239669421488 | 4 | p90_mouth_open_ratio_above_0.32;mouth_face_ratio_p90_above_0.075 |

## 阈值判断

硬阈值：

- `p90_mouth_open_ratio <= 0.32`
- `mouth_face_ratio_p90 <= 0.075`
- `fail_frame_percent <= 15`
- `longest_fail_streak < 5`

结论：

- Candidate A：除 `mouth_face_ratio_p90` 外其余通过。
- Candidate B：除 `mouth_face_ratio_p90` 外其余通过，但整体更差。
- Candidate C：`p90_mouth_open_ratio` 和 `mouth_face_ratio_p90` 均失败。

因此本轮不能标技术通过。
