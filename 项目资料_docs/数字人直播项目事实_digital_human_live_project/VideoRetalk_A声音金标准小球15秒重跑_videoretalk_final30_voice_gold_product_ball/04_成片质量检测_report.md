# 04_成片质量检测_report

`部分成立`：成片技术层通过，可播放、有声音、时长约 15 秒；Qwen-VL 观察为口型基本同步、表情自然。但嘴部开合硬指标未完全通过。

| 字段 | 值 |
|---|---|
| result_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_final30_voice_gold_product_ball_rerun/videoretalk_final30_voice_gold_product_ball_15s.mp4` |
| duration_sec | `15.06` |
| has_audio | `True` |
| p90_mouth_open_ratio | `0.355425` |
| mouth_face_ratio_p90 | `0.11274` |
| fail_frame_percent | `7.054` |
| longest_fail_streak | `4` |
| lipsync_metric_passed | `False` |
| threshold_note | `p90_mouth_open_ratio and mouth_face_ratio_p90 exceeded prior hard thresholds` |

## Qwen-VL 辅助观察

- `qwen-vl-max` / `connected`：{
  "visible_scene": "室内直播场景，背景为浅色窗帘，右侧有装饰花瓶和鼓状道具，左侧可见粉色气球。",
  "anchor_action": "主播坐在椅子上，双手不断做出手势动作，包括合十、指向头部、比划数字等，表情丰富，口型与语言同步，似乎在讲解或引导观众。",
  "product_or_prop": "无明显展示商品，但背景中有装饰性花瓶（橙色果实）、鼓状道具和粉色气球，可能用于营造氛围。",
  "live_ui_visible": "未见直播界面元素（如弹幕、点赞按钮、礼物图标等）。",
  "comment_area_visible": "未见评论区或互动区域。",
  "lip_sync_risk_observation": "主播口型与语音基本匹配，无明显唇形错位或延迟现象，同步性良好。",
  "blink_or_expression_observation": "主播表情自然，频繁眨眼，
- `qwen-vl-plus` / `connected`：{
  "visible_scene": "室内环境，背景为浅色窗帘，右侧有一个装饰有橙色花朵的花瓶，左侧可见部分粉色瑜伽球。",
  "anchor_action": "一位穿着灰色无袖上衣和粉色宽松裤子的女性坐在椅子上，面带微笑，双手在胸前做着各种手势，包括合掌、轻拍大腿、比划数字等，表情生动，似乎在进行讲解或演示。",
  "product_or_prop": "右侧的花瓶内插有橙色花朵，左侧可见一个粉色瑜伽球。",
  "live_ui_visible": "未观察到明显的直播UI元素，如点赞数、礼物打赏界面等。",
  "comment_area_visible": "未观察到评论区。",
  "lip_sync_risk_observation": "口型与声音同步，无明显不同步现象。",
  "blink_or_expression_observation": "女性眨眼自然，面部表情丰富，包括微笑、张嘴说话时的表

## 质量结论

`已确认`：底片动作、背景和直播场景被保留；没有本地嘴部后处理。

`部分成立`：模型主观复核认为口型基本同步，但本地指标显示嘴部开合偏大风险，因此需要用户人工看最终 MP4 后再判断是否进入下一轮正式样片。
