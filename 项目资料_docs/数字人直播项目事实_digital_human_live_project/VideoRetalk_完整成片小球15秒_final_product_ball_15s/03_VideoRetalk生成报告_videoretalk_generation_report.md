# 03_VideoRetalk生成报告_videoretalk_generation_report

状态：`videoretalk_succeeded_after_one_retry`

## 第一次提交

| 字段 | 结果 |
|---|---|
| run_dir | `outputs/videoretalk_probe/20260627_010527_submit` |
| status | `blocked_task_failed` |
| failure_code | `DataInspectionFailed` |
| message | `Input data may contain inappropriate content.` |
| retry_used | `yes` |

第一次使用含“承重标 200 斤实际偏弱”的音频，任务很快失败。OSS 上传和 signed URL 验证均通过，失败发生在 VideoRetalk 任务侧内容检查。

## 最终提交

| 字段 | 结果 |
|---|---|
| run_dir | `outputs/videoretalk_probe/20260627_010633_submit` |
| task_id | `ffe21ac4-a25a-4436-8397-830017a724d1` |
| task_status | `SUCCEEDED` |
| request_id | `6e9651de-fc9c-95d9-9be8-a7ca48126f02` |
| result_probe_path | `outputs/videoretalk_probe/20260627_010633_submit/result_video.mp4` |
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/videoretalk_final_product_ball_15s.mp4` |
| video_extension | `False` |
| media_committed | `no` |
| printed_secret | `no` |

## 输入 URL 来源

- `video_url` 对应本地源文件：`/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_base_video_15s.mp4`
- `audio_url` 对应本地源文件：`/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_audio_for_videoretalk.wav`
- `ref_image_url` 对应本地源文件：`/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/input_ref_image.jpg`

报告中只保留 redacted URL，不保存 signed URL query。
