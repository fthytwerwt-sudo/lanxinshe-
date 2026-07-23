# 执行报告_execution_report

## 主结论

`full_evidence_extraction_completed_pending_5_6_review`

`已确认`：素材路径 `最新直播` 存在，排除 AppleDouble `._*` 后识别到 10 个媒体素材；本轮输出目录为 `docs/直播录屏解析方案_live_recording_analysis/最新直播全量取证解析_latest_live_full_evidence_analysis`。

`部分成立`：Alibaba API 已按用户本轮授权用于 ASR / 多模态窗口分析；评论 OCR、评论—回复关系、课程对应、数字人动作和直播大脑规则均为候选层，统一标记 `provisional_pending_5_6_review`。

`待验证`：人工尚未复核；不能写成业务通过、客户通过、正式直播平台链路通过或数字人能力已完成。

## 边界

- `audit_or_input_preparation_not_fallback`：ffmpeg / ffprobe 只用于取证、音频提取和短窗口输入准备。
- 未修改、移动、删除、重编码源视频。
- GitHub 只保存脱敏 CSV/JSONL/Markdown；原始音频、短片段、API raw、signed URL 和用户名映射保存在 `_local_runtime/`，不提交。
- 未编辑 5.6 规划目录 `新录屏多模态解析规划_new_recording_multimodal_plan/`。

## 命令与参数

- `run_id`: `full_20260723_155512`
- `run_asr`: `True`
- `run_vision`: `True`
- `vision_interval_sec`: `300`
- `vision_duration_sec`: `8`
- `vision_models`: `qwen-vl-plus,qwen3-vl-plus,qwen-vl-max`
- `asr_timeout_sec`: `5400`

## 产物

- `01_素材总清单_source_inventory.csv`
- `02_能力与解析状态_capability_analysis_status.csv`
- `03_场次解析汇总_session_analysis_summary.csv`
- `04_事件时间轴索引_event_timeline_index.csv`
- `05_评论回复候选关系_comment_reply_candidates.csv`
- `06_主播思路动作语气候选_host_logic_action_prosody_candidates.csv`
- `07_课程对应候选_course_alignment_candidates.csv`
- `08_失败风险与未回复样本_failure_risk_unanswered_samples.csv`
- `09_人工复核队列_manual_review_queue.csv`
- `10_直播大脑暂定规则_live_brain_provisional_rules.csv`
- `11_十场直播跨场模式总结_cross_session_pattern_summary.md`
- `12_数据字典_data_dictionary.md`
- `13_本地全量产物索引_local_artifact_manifest.json`
- `data/session_manifests/*.json`
- `data/redacted_event_indexes/*.jsonl`

## 验证口径

- 全部 source hash 已生成。
- event_id 由 `session_id + start_ms + sequence` 生成，验证脚本需检查唯一性。
- 课程候选最高只到 `topic_similarity_only` / `course_alignment_candidate_only`。
- 评论身份信息已做正则脱敏，并由最终验证继续扫描。
