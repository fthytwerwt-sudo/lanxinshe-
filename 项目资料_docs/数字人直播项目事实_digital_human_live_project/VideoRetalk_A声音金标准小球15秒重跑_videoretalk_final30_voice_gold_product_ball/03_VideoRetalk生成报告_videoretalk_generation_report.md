# 03_VideoRetalk生成报告_videoretalk_generation_report

`已确认`：最终 VideoRetalk 任务已成功，结果视频已下载到本地输出目录。

| 字段 | 值 |
|---|---|
| model | `videoretalk` |
| final_task_id | `e72e8957-4064-4eec-8b40-a48eceb2624d` |
| final_status | `SUCCEEDED` |
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/videoretalk_final30_voice_gold_product_ball_15s.mp4` |
| result_duration_sec | `15.06` |
| has_audio | `True` |
| video_extension | `False` |
| payload_audio_source_file | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/input_audio_voiceclone_product_ball_final15.wav` |
| output_audio_from_input_audio | `confirmed_by_videoretalk_payload_and_model_transcode; result audio is AAC 44.1k stereo in MP4 and extracted to 16k mono for checking` |
| postprocess_used | `no_local_mouth_or_video_postprocess` |

## 任务记录

| 字段 | 值 |
|---|---|
| first_voice_clone_videoretalk_attempt | `FAILED / 85eee58c-a5dd-456d-8d4b-70e33254026b / contained 200-jin actual-weak comparative sentence; removed for retry` |
| short_success_not_final | `SUCCEEDED / 865357bd-449d-4a12-8845-9674c16cdb9e / succeeded but too short for complete 15s requirement` |
| final_15s_success | `SUCCEEDED / e72e8957-4064-4eec-8b40-a48eceb2624d / final selected output` |

## 音轨来源判断

`已确认`：最终任务 payload 的 `audio_url` 来源于本地文件 `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/input_audio_voiceclone_product_ball_final15.wav`。输出 MP4 音轨为模型端封装后的 AAC 44.1k stereo；本地只做了解析抽取，没有替换或后处理视频音轨。
