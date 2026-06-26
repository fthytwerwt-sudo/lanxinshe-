# 00_执行报告_execution_report

状态：`completed_final_video_created_voice_not_target_exact_lipsync_metric_risk`

## 主结论

`已确认`：本轮已生成一个 VideoRetalk 原生口型替换 MP4，路径为：

`/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/videoretalk_final_product_ball_15s.mp4`

`部分成立`：视频可播放、有声音、底片动作和背景由真人直播底片保留，且没有做本地嘴部后处理。

`部分成立`：声音不是用户本人目标音频，而是 fallback TTS：`cosyvoice-v3-flash` / `longanxuan_v3`。因此本轮不能写成“用户声音复刻成功”。

`部分成立`：Qwen-VL 观察口型基本同步、动作自然；但 Vision landmark 严格口型指标未过线，仍标记为 `generated_but_lipsync_metric_risk`。

## 关键字段

| 字段 | 结果 |
|---|---|
| status | `completed_final_video_created_voice_not_target_exact_lipsync_metric_risk` |
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/videoretalk_final_product_ball_15s.mp4` |
| base_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_base_video_15s.mp4` |
| base_video_source | `参考/完整直播录屏/今年直播素材/C5824.MP4` |
| base_video_time_range | `00:01:00-00:01:15` |
| input_audio_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_audio_for_videoretalk.wav` |
| input_audio_source | `fallback_generated_tts` |
| voice_match_level | `low_not_user_voice` |
| voice_mismatch_reason | `generated_tts_used_instead_of_user_provided_voice` |
| tts_model | `cosyvoice-v3-flash` |
| tts_voice | `longanxuan_v3` |
| tts_duration | `14.210625` |
| videoretalk_task_id | `ffe21ac4-a25a-4436-8397-830017a724d1` |
| videoretalk_status | `SUCCEEDED` |
| result_duration | `14.200000` |
| has_audio | `yes` |
| postprocess_used | `no` |
| mouth_open_ratio_p90 | `0.3544261559641013` |
| mouth_face_ratio_p90 | `0.11810598373413086` |
| fail_frame_percent | `5.726872246696035` |
| longest_fail_streak | `5` |
| media_committed | `no` |


## 本轮实际路线

1. 复用上一轮已验证底片：`R02_C5824_C01_opening`，`00:01:00-00:01:15`。
2. 未发现“小球文案”的用户本人目标音频，也未发现可直接调用的 voice clone `voice_id`。
3. 排除上一轮 `longyingxiao_v3`，改用 `longanxuan_v3` fallback TTS。
4. 第一次 VideoRetalk 提交因 `DataInspectionFailed` 失败。
5. 按边界只重试一次，删除容易触发审核的“承重标 200 斤实际偏弱”句后重试。
6. 第二次 VideoRetalk 任务 `SUCCEEDED`，结果复制为 final MP4。

## 失败和风险

- `first_videoretalk_attempt_failed_DataInspectionFailed`：第一次任务失败，失败码为 `DataInspectionFailed`。
- `voice_match_low_not_user_voice`：本轮使用 fallback TTS，不是用户本人声音。
- `mouth_threshold_passed=false`：`p90_mouth_open_ratio=0.3544261559641013`，`mouth_face_ratio_p90=0.11810598373413086`，`longest_fail_streak=5`。
- 以上风险不影响“已有可播放 MP4”这个技术事实，但影响口型质量和声音一致性结论。

## 边界确认

- 未使用 `wan2.2-s2v`。
- 未做本地嘴部压缩、羽化融合、局部修嘴或任何本地嘴部后处理。
- 未使用 embedding / rerank / RAG。
- 未提交媒体文件到 GitHub。
- signed URL 仅保存 redacted 版本。
