# 动作还原对比

状态：`generated_but_motion_reconstruction_insufficient`

## 总体判断

`已确认`：3 条候选都成功生成。

`部分成立`：3 条候选都保留了参考帧的粗姿态、人物身份大致稳定和口播形态。

`已确认`：3 条候选都没有完成源视频动作时间线的 1:1 还原，尤其是手势路径、身体重心、肩颈节奏。

## 逐条对比

### candidate_01_from_source_01

- 源视频：站立绿幕讲解，手势、身体晃动、头部与表情变化明显。
- 生成结果：人物站立和身份保留，但大部分时间为单手在腰/胯附近的轻口播姿态。
- 动作丢失：手势节奏、身体重心变化、肩颈动作明显不足。
- 结论：`failed_motion_reconstruction_not_near_1_to_1`

### candidate_02_from_source_02

- 源视频：躺卧桥式姿态，手部有小幅表达，身体姿态较稳定。
- 生成结果：粗姿态最接近源视频，床、腿部和躺卧构图保留较好。
- 动作丢失：手势变化和桥式动态节奏弱；脸部角度导致嘴部/表情检测可靠性低。
- 结论：`partial_coarse_pose_only_not_motion_reference`

### candidate_03_from_source_03

- 源视频：坐姿小球，双手向下/向外，肩部和脸部表情有节奏变化。
- 生成结果：坐姿、球和人物相对稳定，脸部清晰度最好。
- 动作丢失：双手下压/外展动作基本没有跟随时间线。
- 结论：`partial_static_pose_only_not_near_1_to_1`

## 排名

| 判断项 | 候选 |
| --- | --- |
| 粗姿态最接近 | candidate_02_from_source_02 |
| 脸部和嘴部检测相对最稳 | candidate_03_from_source_03 |
| 动作丢失最严重 | candidate_01_from_source_01 |
| 最值得用户人审 | candidate_03_from_source_03 |

## 路线结论

`通用建议`：如果目标是“人物明显动作还原 / 近 1:1 动作复刻”，当前 Wan-S2V `image_url + audio_url` 路线不适合作为主路线。

`部分成立`：如果目标退回到“真人照片/参考帧 + 原音频生成轻动作口播”，Wan-S2V 仍可继续做短样片候选。
