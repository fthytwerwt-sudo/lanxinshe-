# 04_口型张嘴幅度检测报告

状态：`generated_but_mouth_open_failed_threshold`

## 阈值

- mouth_open_ratio = mouth_open_height / mouth_width
- mouth_face_ratio = mouth_open_height / face_height
- 通过线：mouth_open_ratio ≤ 0.32，mouth_face_ratio ≤ 0.075
- 强制失败：连续 5 帧以上 mouth_open_ratio > 0.38，或全片超过 15% 帧数 mouth_open_ratio > 0.38

## 检测结果

| 指标 | 值 |
| --- | --- |
| input_count | `234` |
| detected_count | `234` |
| detection_rate | `1.0` |
| max_mouth_open_ratio | `0.5365898708061552` |
| avg_mouth_open_ratio | `0.16750998993695343` |
| p90_mouth_open_ratio | `0.2891281092255942` |
| fail_frame_count | `7` |
| fail_frame_percent | `2.9914529914529915` |
| longest_fail_streak | `4` |
| max_mouth_face_ratio | `0.15824611485004425` |
| p90_mouth_face_ratio | `0.08985602706670762` |
| mouth_threshold_passed | `False` |

## qwen-vl 生成后辅助观察

```text
```json
{
  "analysis": "该视频为一段15秒的正面数字人口播视频，主体为一位女性，坐姿端正，背景为浅色窗帘与装饰物（花瓶、橙色果实枝条等），整体画面稳定，无明显晃动或抖动。以下为详细观察分析：",
  "face_stability": "面部保持相对稳定，无明显偏移或倾斜，头部位置基本固定，符合正面口播的标准要求。",
  "mouth_opening_amplitude": "嘴巴张合幅度适中，符合正常说话节奏，开口程度在自然范围内，未出现过度夸张或闭合过紧的情况。",
  "teeth_visibility": "牙齿在说话过程中偶有露出，但未持续暴露，属于自然状态下的语言表达表现。",
  "corner_of_mouth": "嘴角动作自然，随语音变化呈现微笑或中性表情，无僵硬或不协调现象。",
  "eye_movement": "眼神直视镜头，专注且稳定，未出现频繁游移或偏离焦点的情况。",
  "blinking": "眨眼频率正常，约每3-4秒一次，符合人类自然生理节奏，无异常快速或长时间闭眼。",
  "slight_nodding": "存在轻微点头动作，频率较低，通常伴随语义强调，动作幅度小，不影响整体稳定性。",
  "head_and_shoulder_movement": "头肩动作控制良好，仅在说话时有极微小的上下或左右调整，未出现大幅度晃动或身体前倾后仰。",
  "hand_gesture_obstruction": "双手交叠置于大腿上，偶尔有轻微手势动作（如手指轻动），但未遮挡面部或关键区域，不影响视觉传达。",
  "voice_rhythm": "声音节奏平稳流畅，语速适中，与唇形同步性较高，未发现明显口型与语音不同步的现象。",
  "overall_evaluation": "整体表现自然、专业，符合高质量数字人视频标准。模型辅助观察结果仅供参考，非人工审核通过。"
}
```
```
