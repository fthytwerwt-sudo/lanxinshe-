# WanS2V 人物动作还原探针执行报告

状态：`completed_wan_s2v_motion_reconstruction_probe_pending_human_review`

## 一页结论

`已确认`：本轮找到用户指定目录下 3 个动作视频，并各取前 15 秒作为输入，使用阿里 `wan2.2-s2v` 生成了 3 条原生候选视频。

`已确认`：3 条候选均为 Wan-S2V 原生输出，均可播放、可解码、带音轨，约 14.8 秒，720x1280，30fps。

`已确认`：本轮没有使用 VideoRetalk，没有使用其它厂商模型，没有本地修嘴 / 修动作 / 补帧 / 换轨来修最终视频。

`部分成立`：Wan-S2V 可以把参考帧人物和源视频原音频生成成轻动作口播候选，但当前路线没有 `video reference / motion reference` 输入，不能称为 1:1 动作复刻。

`待验证`：用户人审、审美、人感、供应商验收、业务可用性均未通过；本报告只给技术生成和动作还原观察。

## 本轮输入与输出

- source_video_dir: `/Volumes/WD_BLACK/澜心社直播/参考/阿里定版视频/最新动作 3 视频`
- output_dir: `/Volumes/WD_BLACK/澜心社直播/outputs/wan_s2v_motion_reconstruction_probe/`
- report_dir: `项目资料_docs/数字人直播项目事实_digital_human_live_project/WanS2V人物动作还原探针_wan_s2v_motion_reconstruction_probe/`
- generated_candidate_count: `3`
- paid_wan_task_count: `3`
- rescue_retry_count: `0`
- local_fallback_used: `false`
- media_committed: `false`

## 候选结果表

| source_id | candidate_id | generation_status | true_video_motion_reference_used | duration_sec | has_audio | overall_reconstruction_score | pass_status |
| --- | --- | --- | --- | ---: | --- | ---: | --- |
| source_01 | candidate_01_from_source_01 | SUCCEEDED | false | 14.8 | true | 2.2/5 | failed_motion_reconstruction_not_near_1_to_1 |
| source_02 | candidate_02_from_source_02 | SUCCEEDED | false | 14.8 | true | 2.5/5 | partial_coarse_pose_only_not_motion_reference |
| source_03 | candidate_03_from_source_03 | SUCCEEDED | false | 14.8 | true | 2.7/5 | partial_static_pose_only_not_near_1_to_1 |

## 最终判断

- 哪条候选最接近原动作：`candidate_02_from_source_02` 粗姿态最接近，因为源视频本身是较稳定的躺卧桥式姿态。
- 哪条候选最适合继续做人审：`candidate_03_from_source_03`，脸部检测和嘴部幅度相对最稳，但动作仍不是复刻。
- 哪条候选动作丢失最严重：`candidate_01_from_source_01`，源视频站立手势和身体动作较多，生成结果基本退化成静态口播。
- 是否值得继续 Wan-S2V 动作路线：`部分成立`，只适合轻动作口播/静态数字人，不建议承担“明显人物动作 1:1 还原”。
- 是否需要换支持 video motion reference 的模型：`通用建议`，如果目标仍是动作复刻，需要找支持视频动作参考 / motion transfer 的路线。

## 验证证据

- workspace / branch / remote 已确认：`/Volumes/WD_BLACK/澜心社直播` / `main` / `https://github.com/fthytwerwt-sudo/lanxinshe-.git`
- `git pull --ff-only`: already up to date
- 3 个源视频：`ffprobe` + `video-metadata-probe` 通过
- 3 条生成候选：`video-metadata-probe` 通过
- 嘴部粗指标：Swift Vision landmark 8fps 抽帧；只作口型幅度粗证据，不作音素级同步结论
- JSON / CSV 见 `data/`

## 失败项 / 风险

- `failed_items`: 近 1:1 动作复刻未通过。
- `risk`: 当前 Wan-S2V 路线不接收源视频动作参考，动作来源主要不是源视频时间线，而是参考图 + 音频驱动。
- `risk`: `candidate_02` 躺卧角度导致人脸检测失败帧较多，嘴部指标可靠性低。
- `risk`: 生成成功不能写成人审通过、供应商验收通过或业务通过。
