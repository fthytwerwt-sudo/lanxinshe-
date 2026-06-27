# 02_参考视频瑜伽球动作拆解_reference_action_breakdown

状态：`reference_video_has_visible_yoga_ball_action_breakdown_completed`

## 参考视频审计

| 字段 | 值 |
| --- | --- |
| reference_video | `/Volumes/WD_BLACK/澜心社直播/参考/C5835（下）.MP4` |
| duration_sec | `43.319250` |
| source_resolution_metadata | `1920x1080 with rotation metadata` |
| extracted_display_frames | `vertical 9:16 frames` |
| yoga_ball_visible | `true` |
| primary_ball | `粉色小瑜伽球，位于主播腿前/手中` |
| scene | `室内瑜伽垫直播讲解场景` |

## 推荐首帧

| candidate | source_frame | reason |
| --- | --- | --- |
| Candidate A | `frame_008` | 球清晰，手势像讲解，嘴部幅度较低。 |
| Candidate B | `frame_002` | 嘴部最闭合，球可见，但手靠近下巴、动作展示感较弱。 |
| Candidate C | `frame_008 tight crop` | 放大脸和球，保留讲解手势，用于排查小脸导致口型比例风险。 |

## 动作文案拆解

详见 `data/action_alignment_timeline.csv`。

`部分成立`：参考视频能提供“坐姿讲解 + 手持/展示小球”的动作底座；但 Wan-S2V 当前输入是单图 + 音频，不是视频动作迁移，因此参考视频只能用于首帧和动作拆解，不能保证模型按原视频动作逐段执行。
