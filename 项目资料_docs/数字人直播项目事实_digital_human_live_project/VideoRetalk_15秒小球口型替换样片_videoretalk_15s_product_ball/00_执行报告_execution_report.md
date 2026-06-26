# 00_执行报告

状态：`部分成立 / generated_but_lipsync_metric_risk`

## 主结论

- `已确认`：本轮真实提交了 VideoRetalk 任务并得到 MP4。
- `部分成立`：结果视频可播放、有声音、约 15 秒，但严格口型数值阈值未通过。
- `待验证`：用户人审、供应商验收、直播长期稳定能力。
- `已确认`：未做本地嘴部后处理，未使用 wan2.2-s2v，媒体未提交 GitHub。

## 核心字段

| 字段 | 值 |
| --- | --- |
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| base_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_15s_product_ball_lipsync/input_base_video_15s.mp4` |
| base_video_source | `参考/完整直播录屏/今年直播素材/C5824.MP4` |
| base_video_time_range | `00:01:00-00:01:15` |
| spoken_copy | `品质真是不一样。便宜小球软塌塌，塑料感重。我们家三层加厚、防爆防压，承重 400 斤，母婴级 PVC，没有异味，用着放心。` |
| audio_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_15s_product_ball_lipsync/input_product_ball_audio.wav` |
| tts_duration | `14.867563` |
| videoretalk_task_id | `2dc5f7c4-ca3f-452d-ac47-203e237f2228` |
| videoretalk_status | `SUCCEEDED` |
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_15s_product_ball_lipsync/videoretalk_15s_product_ball_result.mp4` |
| result_duration | `14.84` |
| has_audio | `True` |
| postprocess_used | `no` |
| mouth_open_ratio_p90 | `0.3746717632024776` |
| mouth_face_ratio_p90 | `0.1202669620513916` |
| fail_frame_percent | `8.860759493670885` |
| longest_fail_streak | `7` |
| mouth_threshold_passed | `False` |
| media_committed | `no` |
| secret_scan | `passed` |

## 边界说明

- 本轮是 `VideoRetalk` 原生口型替换样片，不是 `wan2.2-s2v` 单图数字人生成。
- 本轮没有本地嘴部压缩、羽化融合、局部修嘴或后处理。
- VideoRetalk 样片生成成功不等于实时直播能力成立。
- 技术可播放、有音轨不等于用户人审通过。

## 失败项 / 风险项

- `strict_lipsync_metric_threshold_failed`：`p90_mouth_open_ratio=0.3746717632024776`，目标 `<=0.32`；`mouth_face_ratio_p90=0.1202669620513916`，目标 `<=0.075`；`longest_fail_streak=7`，目标 `<5`。
- `qwen-vl-plus` 对结果视频提示可能存在轻微口型同步风险；`qwen-vl-max` 判断整体基本同步。

## 下一步

- 优先人工观看本地 MP4，判断嘴部边缘、牙齿、微表情和同步感。
- 如果继续做第二轮，建议换嘴巴原始动作更小的底片，或降低 TTS 音量/重音后重新跑一个正式候选；不要做本地修嘴。
