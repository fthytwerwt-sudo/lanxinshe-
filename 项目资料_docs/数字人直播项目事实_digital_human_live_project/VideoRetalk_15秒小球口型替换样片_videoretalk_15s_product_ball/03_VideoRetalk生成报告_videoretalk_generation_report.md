# 03_VideoRetalk 生成报告

状态：`videoretalk_succeeded_metric_risk`

## 生成任务

| 字段 | 值 |
| --- | --- |
| model | `videoretalk` |
| task_id | `2dc5f7c4-ca3f-452d-ac47-203e237f2228` |
| task_status | `SUCCEEDED` |
| run_dir | `outputs/videoretalk_probe/20260627_002954_submit` |
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_15s_product_ball_lipsync/videoretalk_15s_product_ball_result.mp4` |
| generation_probe_submitted | `True` |
| postprocess_used | `no` |
| printed_secret | `no` |

## OSS 上传状态

| asset | upload_success | signed_url_verified | signed_url_status | redacted_url |
| --- | --- | --- | --- | --- |
| `outputs/videoretalk_15s_product_ball_lipsync/input_base_video_15s.mp4` | `True` | `True` | `206` | `https://zhibo11122.oss-cn-beijing.aliyuncs.com/lanxin-live%2Fhappyhorse%2Fvideoretalk_probe%2F20260627_002954%2Finput_video.mp4?[REDACTED_QUERY]` |
| `outputs/videoretalk_15s_product_ball_lipsync/input_product_ball_audio.wav` | `True` | `True` | `206` | `https://zhibo11122.oss-cn-beijing.aliyuncs.com/lanxin-live%2Fhappyhorse%2Fvideoretalk_probe%2F20260627_002954%2Finput_audio.wav?[REDACTED_QUERY]` |
| `outputs/videoretalk_15s_product_ball_lipsync/input_ref_image.jpg` | `True` | `True` | `206` | `https://zhibo11122.oss-cn-beijing.aliyuncs.com/lanxin-live%2Fhappyhorse%2Fvideoretalk_probe%2F20260627_002954%2Fref_image.jpg?[REDACTED_QUERY]` |

## 结果视频技术验证

| 字段 | 值 |
| --- | --- |
| duration_sec | `14.84` |
| resolution | `720x1280` |
| video_codec | `h264` |
| has_audio | `True` |
| audio_codec | `aac` |
| audio_channels | `2` |
| decode_validation | `passed` |

## 不能外推

- `VideoRetalk` 任务成功只证明本轮离线样片链路可跑，不证明 4-5 小时直播稳定。
- 本轮没有验证实时评论插入、直播推流、供应商正式验收或声音克隆正式通过。
