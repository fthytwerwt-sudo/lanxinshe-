# 最终执行报告_final_execution_report

## 主结论

`actual_full_multimodal_analysis_completed_with_true_source_limits`

`已确认`：本轮不是复用上一轮 137 个 Qwen-VL 窗口作终点，而是对上一轮 526 个 `source_limited_unknown` 60 秒窗口创建了新的补跑任务和新模型调用账本。

`部分成立`：全量视觉/评论/动作字段已经由本地全时间轴变化检测 + 本轮 Qwen-VL 关键帧序列补跑补强；评论—回复因果和课程精确原文对应仍按证据不足保留 `true_source_limit`，不写成业务通过。

## 运行信息

- run_id: `actual_full_20260723_182107`
- run_started_at: `2026-07-23T20:39:17+08:00`
- local_runtime: `_local_runtime/最新直播实质全量补跑_latest_live_actual_full_remediation/actual_full_20260723_182107`
- source_dir: `最新直播`
- doc_root: `docs/直播录屏解析方案_live_recording_analysis/最新直播实质全量解析_latest_live_actual_full_analysis`
- Alibaba multimodal credential present: `True`

## 关键计数

- source_sessions: `10`
- source_hash_failures: `0`
- baseline_missing_windows: `526`
- missing_window_task_count: `526`
- new_qwen_call_count: `542`
- remediated_windows: `523`
- model_execution_failed_count: `3`
- old_call_reuse_for_missing_window_count: `0`
- comments_total: `1275`
- new_comment_from_missing_window_count: `1069`
- comment_change_samples: `39566`
- volume_measured_count: `1594`
- valid_course_matches: `0`
- rules_without_evidence_count: `0`
- true_source_limit_count: `1361`

## 产物清单

1. `01_526窗口补跑状态_missing_window_remediation_status.csv`
2. `02_新模型调用账本_new_model_call_ledger.csv`
3. `03_全时间轴变化检测_full_timeline_change_detection.csv`
4. `04_清洗后主播逐字稿_clean_host_transcript.csv`
5. `05_语义事件时间轴_semantic_event_timeline.csv`
6. `06_完整评论生命周期_full_comment_lifecycle.csv`
7. `07_评论回复最终关系_comment_reply_final_links.csv`
8. `08_动作表情视线_final_action_expression_gaze.csv`
9. `09_真实语气音量_final_prosody_volume.csv`
10. `10_课程最终对应_final_course_alignment.csv`
11. `11_直播大脑最终规则_final_live_brain_rules.csv`
12. `12_风险与人工接管_final_risk_handover.csv`
13. `13_真实源限制_unknowns_true_source_limits.csv`
14. `14_剩余人工复核_final_manual_review_queue.csv`
15. `15_独立QA报告_independent_qa_report.json`
16. `16_5.6最终验收_final_5_6_acceptance.json`
17. `17_Agent执行报告_agent_execution_summary.md`

## 验收边界

- `已确认`：Git 包只保留脱敏索引、hash、计数、QA，不包含 raw API payload、帧图、音频、视频、signed URL 或 secret。
- `已确认`：音量/重音来自源音频 RMS/dB 计算，不再写 `volume_not_measured` 充当完成。
- `已确认`：课程没有 direct source quote 时不做有效课程匹配。
- `已确认`：direct reply 没有硬证据时不升级，保留最终枚举和人工接管队列。
- `待验证`：客户验收、正式直播链路、规则上线有效性仍需业务侧/人工复核确认。
