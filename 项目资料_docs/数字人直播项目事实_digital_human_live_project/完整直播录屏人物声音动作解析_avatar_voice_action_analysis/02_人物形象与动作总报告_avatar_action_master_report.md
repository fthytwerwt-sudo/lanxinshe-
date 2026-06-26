# 02_人物形象与动作总报告

状态：`visual_action_analysis_partial` / `local_only_analysis_not_committed`

## 主结论

- `已确认`：本轮覆盖 11 场完整直播录屏，每场抽取 5 个代表片段，共 55 个动作/形象候选片段。
- `已确认`：`qwen-vl-max` 调用 33 次，`qwen-vl-plus` 复核调用 11 次。
- `部分成立`：模型可辅助观察人物画面、动作、表情和遮挡，但不能替代人审，也不能写成数字人能力通过。

## 最高优先级动作候选

| clip_id | source_video | time_range | 用途 | 质量 | 风险 |
| --- | --- | --- | --- | --- | --- |
| R01_5_13_C03_high_motion | 参考/完整直播录屏/今年直播素材/5月13日直播素材.MP4 | 01:23:05-01:23:11 | action_ecology_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R02_C5824_C01_opening | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 00:01:00-00:01:06 | baseline_avatar_state_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R02_C5824_C02_middle | 参考/完整直播录屏/今年直播素材/C5824.MP4 | 00:49:09-00:49:15 | general_live_avatar_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R03_C5825_C01_opening | 参考/完整直播录屏/今年直播素材/C5825.MP4 | 00:01:00-00:01:06 | baseline_avatar_state_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R03_C5825_C03_high_motion | 参考/完整直播录屏/今年直播素材/C5825.MP4 | 01:09:16-01:09:22 | action_ecology_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R04_C5829_C03_high_motion | 参考/完整直播录屏/今年直播素材/C5829.MP4 | 01:23:05-01:23:11 | action_ecology_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R06_C5834_C01_opening | 参考/完整直播录屏/直播效果一般/C5834（上）.MP4 | 00:01:00-00:01:06 | baseline_avatar_state_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |
| R06_C5834_C02_middle | 参考/完整直播录屏/直播效果一般/C5834（上）.MP4 | 00:26:45-00:26:51 | general_live_avatar_reference | 5.0 | needs_human_review_before_training_or_vendor_acceptance |

## 模型辅助收束

以下内容是 `qwen-max` 基于抽样片段、本地指标和模型观察做的辅助归纳，状态一律按 `待人工复核` 处理。凡是“稳定”“自然”“适合”等词，只表示候选方向，不表示人审通过、训练可直接使用或供应商样片验收通过。

### 人物形象稳定特征
- 人物在室内直播环境中表现较为一致，面部表情丰富且自然。
- 面部可见度高，眼神直视镜头，眨眼频率正常。
- 表情生动，微笑、专注且富有感染力。

### 最自然动作片段
- **R01_5_13_C03_high_motion** (01:23:05-01:23:11)：动作明显阶段，身体和头部动作自然，表情投入。
- **R02_C5824_C01_opening** (00:01:00-00:01:06)：开头阶段，动作自然，表情愉悦。
- **R02_C5824_C02_middle** (00:49:09-00:49:15)：中段讲解阶段，动作自然，表情投入。
- **R03_C5825_C01_opening** (00:01:00-00:01:06)：开头阶段，动作自然，表情愉悦。
- **R03_C5825_C03_high_motion** (01:09:16-01:09:22)：动作明显阶段，身体和头部动作自然，表情投入。
- **R04_C5829_C03_high_motion** (01:23:05-01:23:11)：动作明显阶段，身体和头部动作自然，表情投入。
- **R06_C5834_C01_opening** (00:01:00-00:01:06)：开头阶段，动作自然，表情愉悦。
- **R06_C5834_C02_middle** (00:26:45-00:26:51)：中段讲解阶段，动作自然，表情投入。
- **R07_C5835_C02_middle** (00:25:54-00:26:00)：中段讲解阶段，动作自然，表情专注。
- **R10_7_23_2_C03_high_motion** (00:33:49-00:33:55)：动作明显阶段，身体和头部动作自然，表情投入。

### 声音风格
- 语音风格总体稳定，语速适中，停顿适中，适合TTS节奏参考。
- 情绪变化不明显，整体流畅自然。

### 适合参考帧/声音克隆/样片微调的片段
- **视频片段**：
  - R01_5_13_C03_high_motion (01:23:05-01:23:11)
  - R02_C5824_C01_opening (00:01:00-00:01:06)
  - R02_C5824_C02_middle (00:49:09-00:49:15)
  - R03_C5825_C01_opening (00:01:00-00:01:06)
  - R03_C5825_C03_high_motion (01:09:16-01:09:22)
  - R04_C5829_C03_high_motion (01:23:05-01:23:11)
  - R06_C5834_C01_opening (00:01:00-00:01:06)
  - R06_C5834_C02_middle (00:26:45-00:26:51)
  - R07_C5835_C02_middle (00:25:54-00:26:00)
  - R10_7_23_2_C03_high_motion (00:33:49-00:33:55)

- **声音片段**：
  - V_R01_5_13_C02_middle (00:55:10-00:55:16)
  - V_R01_5_13_C03_high_motion (01:23:05-01:23:11)
  - V_R01_5_13_C04_high_audio (00:56:30-00:56:36)
  - V_R02_C5824_C02_middle (00:49:09-00:49:15)
  - V_R02_C5824_C03_high_motion (01:02:08-01:02:14)
  - V_R02_C5824_C04_high_audio (01:37:38-01:37:44)
  - V_R03_C5825_C02_middle (00:54:45-00:54:51)

### 不适合素材类型
- 动作过于剧烈或不自然的片段。
- 面部细节有限或遮挡严重的片段。
- 背景噪音较大或有重叠语音的片段。

### 下一轮需人工复核点
- 需要人工听辨所有候选声音片段，确认情感、语速、背景噪音等情况。
- 需要人工审查所有候选视频片段，确认面部、眼睛、嘴巴等细节是否符合要求。
- 确认所有候选片段是否适合用于训练或供应商接受。

## 人物形象与动作字段覆盖

- 已覆盖：脸部清晰度、脸部面积、眼神/嘴部可见性粗标记、头肩/身体/手势模型观察、动作强度、遮挡风险、数字人用途建议。
- 待人工复核：真实眨眼频率、微表情细节、口型准确度、手部穿帮、是否适合训练或供应商验收。
