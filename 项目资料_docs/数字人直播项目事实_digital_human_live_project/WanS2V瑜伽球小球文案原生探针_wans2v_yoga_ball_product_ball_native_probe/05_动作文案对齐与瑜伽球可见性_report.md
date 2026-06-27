# 05_动作文案对齐与瑜伽球可见性_report

状态：`visual_alignment_partial_but_mouth_threshold_failed`

## Qwen-VL 辅助观察

| candidate | yoga_ball_visible | action_alignment_score | face_stability_risk | mouth_amplitude_visual_risk | hand_or_product_error_risk |
| --- | --- | --- | --- | --- | --- |
| candidate_A | `True` | `5` | `low` | `low` | `low` |
| candidate_B | `True` | `4` | `low` | `low` | `low` |
| candidate_C | `True` | `4` | `low` | `medium` | `low` |

## 观察结论

`已确认`：三条候选抽帧和 Qwen-VL 辅助观察均显示粉色瑜伽球清晰可见，没有出现商品完全消失。

`部分成立`：动作与文案达到“讲解型匹配”，尤其 Candidate A 的视觉动作评分最高；但 Wan-S2V 单图 + 音频不能做精确逐段动作控制，无法保证“软塌塌/三层加厚/保险”每一句都有对应动作。

`待用户人审`：动作自然度、直播感、手部细节、真实商品讲解感、口型一眼假程度。

## 关键风险

- Candidate A 是 best_available，但口型硬指标未过。
- Candidate B 口型没有因降音量改善，动作展示感也弱于 A。
- Candidate C 构图更有商品讲解感，但口型变大，不能作为通过候选。
