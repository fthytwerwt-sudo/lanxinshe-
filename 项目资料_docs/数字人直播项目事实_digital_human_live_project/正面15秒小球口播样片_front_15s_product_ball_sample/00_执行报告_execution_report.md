# 00_执行报告

状态：`generated_but_mouth_open_failed_threshold`

## 执行结果

| 字段 | 值 |
| --- | --- |
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| front_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/front_15s_product_ball_mouth_control/front_15s_product_ball_mouth_control.mp4` |
| spoken_copy | `品质真是不一样。便宜小球软塌塌，塑料材质。我家三层加厚、防爆防压，承重400斤，母婴级PVC，没有异味，用着更放心。` |
| tts_duration | `14.823125` |
| reference_frame_path | `/Volumes/WD_BLACK/澜心社直播/outputs/front_15s_product_ball_mouth_control/input_front_reference_frame.jpg` |
| background_source | `outputs/two_15s_avatar_samples_front_side/01_front_15s_sample.mp4` |
| wan_task_id | `b6dfe981-2b12-4e8e-b492-9603dcf8802b` |
| wan_status | `SUCCEEDED` |
| resolution | `720x1280` |
| video_duration | `14.633333` |
| has_audio | `True` |
| max_mouth_open_ratio | `0.5365898708061552` |
| p90_mouth_open_ratio | `0.2891281092255942` |
| fail_frame_percent | `2.9914529914529915` |
| longest_fail_streak | `4` |
| mouth_face_ratio_p90 | `0.08985602706670762` |
| mouth_threshold_passed | `False` |
| media_committed | `no` |
| secret_printed | `no` |

## 模型调用

| label | model | status | request_id |
| --- | --- | --- | --- |
| reference_frame | qwen-vl-max | connected | c5c21da0-bba1-985e-83f8-5cd2d53208a4 |
| reference_frame_recheck | qwen-vl-plus | connected | 2215c904-67ed-9175-9398-6a37d2d0bde6 |
| generated_video | qwen-vl-max | connected | 04fd7175-c1fe-9359-a11d-2128f512a57c |
| report_field_normalization | qwen-plus | connected | 245beccd-7b48-9e71-b33a-94f828f7e6d5 |
| copy_compression | qwen-max | connected | 438e31b2-df4c-965f-88b8-ef102cdb87be |

## 边界

- 本轮只生成一个正面 15 秒左右口播视频，不做 30 秒、不做侧面、不做 embedding/rerank/RAG。
- `wan2.2-s2v` 无公开 `mouth_open_range` 参数，本轮通过参考帧闭嘴、TTS 音量/语速和生成后 landmark 检测间接控制。
- 技术生成和口型指标通过不等于用户人审、供应商验收或直播长期稳定通过。
