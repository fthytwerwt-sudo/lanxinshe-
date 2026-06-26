# 04_成片质量检测_report

状态：`generated_but_lipsync_metric_risk`

## 技术验证

| 字段 | 结果 |
|---|---|
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final_product_ball_15s/videoretalk_final_product_ball_15s.mp4` |
| duration | `14.200000` |
| resolution | `720x1280` |
| fps | `50` |
| video_codec | `h264` |
| has_audio | `yes` |
| audio_codec | `aac` |
| audio_channels | `2` |
| decode_validation | `passed` |

## 口型指标

| 指标 | 结果 | 阈值 |
|---|---:|---:|
| p90_mouth_open_ratio | `0.3544261559641013` | `<= 0.32` |
| mouth_face_ratio_p90 | `0.11810598373413086` | `<= 0.075` |
| fail_frame_percent | `5.726872246696035` | `<= 15` |
| longest_fail_streak | `5` | `< 5` |
| detection_rate | `1.0` | `>= 0.95` |
| mouth_threshold_passed | `False` | `true` |

`已确认`：严格口型指标未过线。

## Qwen-VL 观察

### qwen-vl-max

```json
{
  "visible_scene": "室内直播场景，背景为浅色窗帘，右侧有装饰花瓶和鼓状道具，左侧可见粉色气球。",
  "anchor_action": "主播坐在椅子上，双手不断做出手势，包括合十、指向头部、比划数字等动作，表情丰富，口型与语言同步，似乎在讲解或引导观众。",
  "product_or_prop": "无明显商品展示，但背景中有装饰性花瓶（橙色果实）、鼓状道具和粉色气球，可能用于营造氛围。",
  "live_ui_visible": "未见直播界面元素（如弹幕、点赞按钮、购物车等）。",
  "comment_area_visible": "未见评论区或互动区域。",
  "lip_sync_risk_observation": "主播口型与语音基本同步，无明显唇形错位或延迟现象，风险较低。",
  "blink_or_expression_observation": "主播眨眼频率正常，表情自然，时而微笑、时而认真，情绪表达连贯，无异常僵硬或重复动作。",
  "human_like_score_note": "主播行为自然，肢体语言丰富，面部表情生动，整体表现符合真人直播特征，人类相似度高。",
  "next_stage_recommendation": "建议继续观察后续内容是否涉及产品展示或互动环节，以判断是否进入销售或推广阶段。"
}
```

### qwen-vl-plus

```json
{
  "visible_scene": "室内，背景为浅色窗帘，右侧有一个装饰有橙色果实的花瓶和一个彩色编织篮。",
  "anchor_action": "一位穿着灰色无袖上衣和粉色宽松长裤的女性坐在椅子上，面带微笑，双手合十于胸前。她随后张开双手，做出手势，并用手指指向自己，表情生动，似乎在进行讲解或演示。",
  "product_or_prop": "右侧可见一个装饰有橙色果实的花瓶和一个彩色编织篮，左侧隐约可见一个粉色瑜伽球。",
  "live_ui_visible": "未观察到直播界面元素（如点赞数、礼物等）。",
  "comment_area_visible": "未观察到评论区。",
  "lip_sync_risk_observation": "口型与声音同步，无明显不同步现象。",
  "blink_or_expression_observation": "女性眨眼自然，面部表情丰富，包括微笑、张嘴说话时的表情变化。",
  "human_like_score_note": "表现自然，动作流畅，表情生动，具有较高的人类行为特征。",
  "next_stage_recommendation": "建议继续当前讲解内容，可以适当增加手势动作以增强表达效果，同时保持与观众的互动。"
}
```

## 综合判断

`已确认`：视频可播放且有音轨；输出音轨来自 input_audio 的模型端转码封装。

`部分成立`：Qwen-VL 认为动作、表情、眨眼和口型整体自然；但该结论不能覆盖 Vision landmark 严格阈值失败。

`待用户人审`：嘴部边缘是否假、是否有主观不同步、是否能接受 fallback TTS 声音。
