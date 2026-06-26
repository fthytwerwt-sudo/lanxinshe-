# 02_参考帧检查报告

状态：`reference_frame_selected`

## 参考帧

| 字段 | 值 |
| --- | --- |
| source_video | `参考/完整直播录屏/今年直播素材/C5824.MP4` |
| previous_reference_frame | `outputs/two_15s_avatar_samples_front_side/input_front_reference_frame.jpg` |
| selected_candidate_frame | `/Volumes/WD_BLACK/澜心社直播/outputs/front_15s_product_ball_mouth_control/reference_frame_candidates/candidate_012.jpg` |
| selected_reference_frame | `/Volumes/WD_BLACK/澜心社直播/outputs/front_15s_product_ball_mouth_control/input_front_reference_frame.jpg` |
| reference_frame_time | `00:01:05.500` |
| background_source | `outputs/two_15s_avatar_samples_front_side/01_front_15s_sample.mp4` |

## Vision landmark 指标

| 指标 | 值 |
| --- | --- |
| mouth_open_ratio | `0.035175878536793964` |
| mouth_face_ratio | `0.010045289993286133` |
| detected | `True` |

## 选择理由

上一轮参考帧露齿风险较高，本轮从同一 opening 段重新选择闭嘴/微闭参考帧。

## qwen-vl 辅助观察

```text
```json
{
  "face_visibility": "high",
  "mouth_state": "closed",
  "teeth_visibility": "none",
  "eye_visibility": "high",
  "expression": "neutral",
  "occlusion": "none",
  "background_consistency": "high",
  "reference_frame_suitability": "good",
  "mouth_open_risk": "low"
}
```
```
