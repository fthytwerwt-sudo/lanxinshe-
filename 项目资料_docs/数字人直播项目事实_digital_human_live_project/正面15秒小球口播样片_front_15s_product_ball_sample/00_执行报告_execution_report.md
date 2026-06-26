# 00_执行报告

状态：`completed`

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
| video_duration | `14.581995` |
| has_audio | `True` |
| max_mouth_open_ratio | `0.22347499783672603` |
| p90_mouth_open_ratio | `0.10403372181307027` |
| fail_frame_percent | `0` |
| longest_fail_streak | `0` |
| mouth_face_ratio_p90 | `0.030434972047805795` |
| mouth_threshold_passed | `True` |
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
| final_postprocessed_video | qwen-vl-max | connected | 492b7e8d-b736-9219-b89d-3dc279828970 |

## 关键说明

- Wan 720P 直出视频已生成，但直出版 `mouth_face_ratio_p90=0.08985602706670762` 未过阈值。
- 本轮没有追加第三次 Wan 生成；采用本地嘴部区域垂直压缩 + feather 融合后处理，最终输出路径仍为 `front_15s_product_ball_mouth_control.mp4`。
- 最终版技术验证通过：可播放、可解码、有音频、时长约 15 秒。
- 技术生成和口型指标通过不等于用户人审、供应商验收或直播长期稳定通过。
