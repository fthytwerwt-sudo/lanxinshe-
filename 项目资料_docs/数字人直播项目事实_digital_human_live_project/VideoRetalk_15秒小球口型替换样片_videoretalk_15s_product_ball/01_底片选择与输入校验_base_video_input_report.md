# 01_底片选择与输入校验

状态：`base_video_input_validated`

## 选择结果

| 字段 | 值 |
| --- | --- |
| clip_id | `R02_C5824_C01_opening` |
| source_video | `参考/完整直播录屏/今年直播素材/C5824.MP4` |
| time_range | `00:01:00-00:01:15` |
| local_base_video | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_15s_product_ball_lipsync/input_base_video_15s.mp4` |
| local_ref_image | `/Volumes/WD_BLACK/澜心社直播/outputs/videoretalk_15s_product_ball_lipsync/input_ref_image.jpg` |
| selection_reason | `R02_C5824_C01_opening 是候选表高优先级 baseline 片段；正面、表情自然、动作连续、无遮挡风险低。` |

## 输入校验

| 字段 | 值 |
| --- | --- |
| input_valid | `True` |
| video_duration_sec | `15.0` |
| video_resolution | `720x1280` |
| video_fps | `50.0` |
| video_codec | `h264` |
| audio_duration_sec | `14.868` |
| audio_codec | `pcm_s16le` |
| audio_sample_rate | `16000` |
| audio_channels | `1` |

## qwen-vl-max 底片观察

```json
{
  "visible_scene": "室内直播场景，背景为浅色窗帘，右侧有装饰花瓶和鼓状物品，左侧可见粉色瑜伽球。",
  "anchor_action": "主播坐在椅子上，双手不断做出手势，包括合十、指向头部、比划数字等动作，表情丰富，口型与语言同步，似乎在讲解或引导观众。",
  "product_or_prop": "无明显展示商品，但背景中存在装饰性花瓶（橙色果实）、鼓状道具及粉色瑜伽球，可能用于健身或冥想类内容。",
  "live_ui_visible": "未见直播界面元素（如点赞、礼物、弹幕等）。",
  "comment_area_visible": "未见评论区域。",
  "lip_sync_risk_observation": "主播口型与语音基本同步，无明显唇形错位或延迟现象，风险较低。",
  "blink_or_expression_observation": "主播眨眼频率正常，表情自然且富有变化，情绪投入，无异常僵硬或重复动作。",
  "human_like_score_note": "主播行为自然，肢体语言流畅，面部表情生动，整体呈现高度拟人化特征，符合真人直播标准。",
  "next_stage_recommendation": "建议继续观察后续内容是否涉及产品展示或互动环节，以判断是否需进行合规性审核；当前阶段可视为正常直播流程。"
}
```

## qwen-vl-plus 复核

```json
{
  "visible_scene": "室内，背景为浅色窗帘，右侧有一个装饰有橙色花朵的花瓶和一个彩色编织篮。",
  "anchor_action": "一位穿着灰色无袖上衣和粉色宽松裤子的女性坐在椅子上，面带微笑，双手合十，随后开始说话并用手指比划数字（1、2、3），最后双手交叉放在胸前。",
  "product_or_prop": "右侧有一个装饰性的花瓶，内插橙色花朵，旁边是一个彩色编织篮。",
  "live_ui_visible": "未观察到直播界面元素。",
  "comment_area_visible": "未观察到评论区。",
  "lip_sync_risk_observation": "口型与声音同步，无明显不同步现象。",
  "blink_or_expression_observation": "表情自然，微笑，眨眼频率正常，面部表情随讲话内容变化。",
  "human_like_score_note": "表现自然，动作流畅，符合真人直播特征。",
  "next_stage_recommendation": "建议增加互动环节，如提问观众或展示产品细节，以提高观众参与度。"
}
```
