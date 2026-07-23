# 复审主报告_review_report

## 主结论

`已确认`：第一轮最新直播取证结果已形成可追溯 baseline，但未达到“全量解析完成”。本轮复审只批准进入 5.5 多 Agent `pilot_remediation_only`，当前状态为 `request_changes_pilot_remediation_only`。

`部分成立`：10/10 视频、10/10 ASR、基础事件索引、稀疏视觉窗口、候选课程/规则/复核队列已经存在。

`待补全`：视觉全时间轴、评论生命周期、评论—回复因果、动作观察、语气证据、课程有效匹配、直播大脑规则和人工复核队列仍需要补齐。

## 量化覆盖

- session_count: 10
- total_duration_min: 659.45
- baseline_visual_windows: 138
- visual_coverage_status: sparse_only_invalid
- estimated_base_scan_60s_windows: 663
- dense_scan_20s_reference_windows: 1982
- event_rows: 7736
- comment_reply_candidates: 134
- course_candidates: 7251
- provisional_rules: 133
- manual_review_rows: 800

## 字段达标概览

- passed: 1
- partial: 4
- missing: 3
- invalid: 5
- blocked_source_limit: 0
- not_applicable: 0

## 关键缺口

1. ASR 成功但缺 `audio_source_type`、`speaker_role`、`asr_quality`、`host_speech_usable`，且需要把歌曲/背景/旁人/平台声音从主播话术中分离。
2. 视觉只覆盖约 2.7%-3.0%，不能证明评论、动作和课件互动全程可见。
3. 评论回复关系全部仍是 candidate 层，不能把时间接近写成因果。
4. 动作字段大部分为空；看不清应写 `not_observable`，不能留空或猜。
5. 课程候选全部为 `topic_similarity_only`，不能算有效课程对应。
6. 直播大脑规则全量模板化且缺 `event_id` 绑定。
7. 人工复核队列固定每场 80 条，未按风险和不确定性重排。

## 是否批准 5.5 补跑

- supports_5_6_sol: True
- supports_5_5_multi_agent: True
- alibaba_multimodal_authorized: True
- allowed_execution: False
- pilot_remediation_allowed: True

`已确认`：当前环境已真实启动 `gpt-5.6-sol` 复审 agent 和 `gpt-5.5` lane agent。阿里多模态路线按用户本轮授权进入 pilot 补齐执行计划；10 场 full remediation 仍需 5.6 pilot 终审批准。

## Commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short --branch`
- `git rev-parse HEAD && git ls-remote origin refs/heads/main`
- `python3 scripts/生成全量解析补齐复审_review_package.py --supports-5-6-sol --supports-5-5 --alibaba-multimodal-authorized`

## Result

- gap_manifest: `04_缺口清单_gap_manifest.json`
- remediation_tasks: `05_补跑任务清单_remediation_tasks.json`
- agent_goals: `06_Agent目标分工_agent_goals.json`
- machine_approval: `09_机器可读批准_machine_approval.json`
- final_acceptance_contract: `10_最终验收合同_final_acceptance_contract.json`

## Failed Items

- `blocked_source_limit`: 完整 raw course transcript source_ref 仍存在历史 `previous_pack` 指向；课程 exact alignment lane 必须在源缺失时 blocked，不影响其他 lane 继续。
- `待验证`: 5.5 pilot 补跑输出尚未进入 5.6 终验，本报告不能写“全量解析完成”。

## Git 边界

本轮只写入 `全量解析补齐复审_full_analysis_completion_review/` 和生成脚本；不修改第一轮 baseline，不提交 `_local_runtime/`、媒体、raw API 或 private manifest。
