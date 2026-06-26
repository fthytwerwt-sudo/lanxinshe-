# 04_口型动作微表情检测报告

状态：`generated_but_lipsync_metric_risk`

## 口型数值指标

| 字段 | 值 |
| --- | --- |
| input_count | `237` |
| detected_count | `237` |
| detection_rate | `1.0` |
| p90_mouth_open_ratio | `0.3746717632024776` |
| mouth_face_ratio_p90 | `0.1202669620513916` |
| fail_frame_percent | `8.860759493670885` |
| longest_fail_streak | `7` |
| mouth_threshold_passed | `False` |
| threshold_rule | `p90_mouth_open_ratio <= 0.32, mouth_face_ratio_p90 <= 0.075, fail_frame_percent <= 15, longest_fail_streak < 5` |

## 模型观察

### qwen-vl-max

```json
{
  "visible_scene": "室内直播场景，背景为浅色窗帘，右侧有装饰花瓶和鼓状物体，左侧可见粉色瑜伽球。",
  "anchor_action": "主播坐在椅子上，双手不断做出手势，包括合十、指向头部、比划数字等动作，表情丰富，口型与语言同步，似乎在讲解或引导内容。",
  "product_or_prop": "无明显展示商品，但背景中存在装饰性花瓶（橙色果实）、鼓状物体及粉色瑜伽球，可能用于营造氛围或暗示健身主题。",
  "live_ui_visible": "未见直播界面元素如弹幕、礼物图标、点赞按钮等，画面为纯视频内容。",
  "comment_area_visible": "未显示评论区，画面聚焦于主播本人。",
  "lip_sync_risk_observation": "主播口型与语音基本同步，无明显脱节现象，唇形变化自然，符合正常讲话节奏。",
  "blink_or_expression_observation": "主播眨眼频率正常，面部表情生动，时而微笑、时而严肃，情绪表达清晰，无异常僵硬或夸张表现。",
  "human_like_score_note": "主播行为自然，肢体语言丰富，表情真实，整体呈现高度拟人化特征，符合真人直播标准。",
  "next_stage_recommendation": "建议继续观察后续内容是否涉及产品展示或互动环节，当前阶段可判定为开场介绍或教学类直播，适合推进至内容深化或用户互动阶段。"
}
```

### qwen-vl-plus

```json
{
  "visible_scene": "室内环境，背景为浅色窗帘，右侧有一个装饰有橙色果实的花瓶和一个彩色编织篮。",
  "anchor_action": "一位穿着灰色背心和粉色宽松裤子的女性坐在椅子上，面带微笑，双手在胸前做着各种手势，包括合掌、张开、比划数字等，同时似乎在说话或讲解。",
  "product_or_prop": "右侧有一个装饰性的花瓶，里面插有橙色果实，旁边还有一个彩色编织篮。",
  "live_ui_visible": "未观察到明显的直播界面元素，如礼物、点赞、关注按钮等。",
  "comment_area_visible": "未观察到评论区。",
  "lip_sync_risk_observation": "由于画面中人物在说话，可能存在轻微的口型与声音不同步的风险，但整体表现自然。",
  "blink_or_expression_observation": "人物表情丰富，时而微笑，时而认真，眨眼频率正常，面部表情自然生动。",
  "human_like_score_note": "人物动作流畅自然，表情生动，符合真人直播的特点，整体表现较为真实。",
  "next_stage_recommendation": "建议在接下来的画面中可以展示更多具体的产品细节或进行实际操作演示，以增加观众的参与感和互动性。"
}
```

## 综合判断

- `已确认`：动作、手势、背景和镜头感在模型观察中基本保留。
- `部分成立`：主观模型观察倾向“自然 / 基本同步”，但数值口型阈值未过。
- `待验证`：嘴部边缘、牙齿、微表情真实感需要用户人工观看最终 MP4。
- `已确认`：未做本地嘴部后处理，所以所有风险来自原生 VideoRetalk 输出或输入素材选择。
