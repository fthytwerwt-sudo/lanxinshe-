# HappyHorse 大幅动作复刻探针执行报告

状态：`completed_happyhorse_large_motion_probe_pending_human_review`

## 主结论

`已确认`：本轮在 `/Volumes/WD_BLACK/澜心社直播`、branch `main`、remote `https://github.com/fthytwerwt-sudo/lanxinshe-.git` 下执行，生成 3 条最终 HappyHorse 候选，并额外使用 1 次 rescue retry 修正 source_03 初始 prompt 场景错误。总付费任务数：`4`，没有超过 P0 上限。

`已确认`：仓库原有 HappyHorse 本地入口是 `happyhorse-1.0-i2v` 首帧图生视频；该入口不支持本轮 1:1 动作复刻。为满足 P0，实际使用阿里官方 HappyHorse `happyhorse-1.0-video-edit`，输入为 15 秒视频片段 + 首帧参考图。

`部分成立`：HappyHorse `video-edit` 明显比当前 Wan-S2V `image_url + audio_url` 路线更适合动作时间线保留，因为它接收 `type=video` 输入并成功输出接近源视频动作节奏的 15 秒结果。但这不是“从单图生成全新数字人并 1:1 复刻动作”的能力结论。

## 证据边界

- `已确认`：本轮使用 HappyHorse `happyhorse-1.0-video-edit` 生成；没有使用 Wan-S2V、VideoRetalk 或其它模型替代。
- `已确认`：本轮本地工具只用于 `audit_or_input_preparation_not_fallback`，包括 ffprobe、ffmpeg 15 秒输入片段标准化、参考帧抽取、审计 contact sheet、音频波形相似度计算。
- `已确认`：候选视频是 HappyHorse 原生输出；没有对最终候选做本地修嘴、换音轨、补帧、融合、重封装后冒充模型结果。
- `待验证`：用户人审、审美、人感、供应商验收和业务可用性。

## 执行结果

- status：`completed_happyhorse_large_motion_probe_pending_human_review`
- workspace：`/Volumes/WD_BLACK/澜心社直播`
- branch：`main`
- remote：`https://github.com/fthytwerwt-sudo/lanxinshe-.git`
- happyhorse_connection_entry：`docs/happyhorse_i2v_connection.md` / `scripts/check_happyhorse_i2v_connection.py`；本轮实际调用官方 `happyhorse-1.0-video-edit`
- happyhorse_connected：`已确认`，4 个 HappyHorse task 均 `SUCCEEDED`
- happyhorse_capability_summary：`video-edit` 支持视频输入；本轮以输入视频作为 motion/expression reference，不存在单独 `motion_reference` 字段
- source_video_dir：`/Volumes/WD_BLACK/澜心社直播/参考/阿里定版视频/最新动作 3 视频`
- source_video_count：`3`
- output_dir：`/Volumes/WD_BLACK/澜心社直播/outputs/happyhorse_large_motion_reconstruction_probe/`
- report_dir：`项目资料_docs/数字人直播项目事实_digital_human_live_project/HappyHorse大幅动作复刻探针_happyhorse_large_motion_reconstruction_probe/`
- generated_candidate_count：`4 raw outputs / 3 selected final candidates`
- paid_task_count：`4`
- local_fallback_used：`false`
- media_committed：`false`
- user_review_passed：`待验证`

## 候选结果表

| source_id | candidate_id | generation_status | motion_reference_used | expression_reference_used | body_motion_similarity | hand_gesture_similarity | facial_expression_similarity | micro_expression_similarity | lip_sync_quality | naturalness | identity_stability | overall_reconstruction_score | pass_status | failed_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_01 | candidate_01_from_source_01 | SUCCEEDED | True | True | 4.4 | 4.1 | 4.0 | 3.6 | 4.2 | 4.1 | 4.3 | 4.1 | near_1_to_1_reconstruction_partial_pending_human_review |  |
| source_02 | candidate_02_from_source_02 | SUCCEEDED | True | True | 4.0 | 3.7 | 3.2 | 2.8 | 3.3 | 3.8 | 3.8 | 3.5 | partial_motion_reconstruction_oblique_face_risk_pending_human_review |  |
| source_03 | candidate_03_from_source_03_rescue | SUCCEEDED | True | True | 4.2 | 4.0 | 3.8 | 3.4 | 4.1 | 4.0 | 4.2 | 4.0 | near_1_to_1_reconstruction_partial_pending_human_review |  |

## 最终判断

- 哪条候选最接近 1:1：`candidate_01_from_source_01`，动作/手势/头肩/表情整体最稳。
- 哪条候选动作最好：`candidate_01_from_source_01` 与 `candidate_03_from_source_03_rescue` 都较好；source_01 更能体现站姿大幅上身动作。
- 哪条候选表情最好：`candidate_01_from_source_01`。
- 哪条候选问题最大：`candidate_02_from_source_02`，不是生成失败，而是源视频斜脸/躺卧导致微表情、眨眼、口型判断低置信。
- HappyHorse 是否优于 Wan-S2V 当前路线：`部分成立`，在视频输入/动作时间线保留方面明显优于 Wan-S2V 当前 `image_url + audio_url` 路线。
- 是否建议继续 HappyHorse：`通用建议`，建议先由用户人审 3 条候选，再决定 30 秒/60 秒。
- 是否建议进入用户人审：`已确认 yes`。
- 是否可进入 30 秒/60 秒：`待验证`，本轮只验证 15 秒。
