# 03_Wan 生成报告

状态：`SUCCEEDED_WITH_LOCAL_POSTPROCESS`

| 字段 | 值 |
| --- | --- |
| model | `wan2.2-s2v` |
| task_id | `b6dfe981-2b12-4e8e-b492-9603dcf8802b` |
| requested_resolution | `720P` |
| resolution_fallback | `no` |
| final_output_video | `/Volumes/WD_BLACK/澜心社直播/outputs/front_15s_product_ball_mouth_control/front_15s_product_ball_mouth_control.mp4` |
| final_duration | `14.581995` |
| final_resolution | `720x1280` |
| has_audio | `True` |
| video_codec | `h264` |
| audio_codec | `aac` |

## 输入 URL 安全

- image_url: `https://zhibo11122.oss-cn-beijing.aliyuncs.com/lanxin-live%2Fhappyhorse%2Ffront_15s_product_ball_mouth_control%2F20260626_193017%2Finput_front_reference_frame.jpg?[REDACTED_QUERY]`
- audio_url: `https://zhibo11122.oss-cn-beijing.aliyuncs.com/lanxin-live%2Fhappyhorse%2Ffront_15s_product_ball_mouth_control%2F20260626_193018%2Finput_front_product_audio_normalized.wav?[REDACTED_QUERY]`
- full_signed_url_saved: `no`

## 后处理说明

- Wan 原始输出未过 `mouth_face_ratio_p90`。
- 本轮没有继续创建新的 Wan 任务，而是在本地对嘴部小区域做垂直压缩和羽化融合。
- 最终视频仍保留原音轨，并通过 ffprobe 技术验证。
