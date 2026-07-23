# 多模态事件数据合同

## 1. 合同定位

本合同定义 Codex 5.5 pilot 和后续 full batch 的唯一事件交换格式。机器约束见 `data/event_schema.json`。

设计目标：

- 每个结论可回到 source video + hash + 时间码 + evidence。
- 观察事实、计算结果、AI 推测和人工确认不混写。
- 支持一对多、多对一、未回复、主播主动提问、仅主题相似等评论关系。
- 真人动作、动作含义推测、数字人候选动作分离。
- 课程原文、直播改写、销售转译和无关内容分离。
- `raw_local` 与 `redacted_repo` 物理和字段双重隔离。

## 2. 版本与兼容

- 当前版本：`1.0.0`
- 兼容规则：新增 optional 字段可升 minor；修改枚举语义/required 字段升 major。
- 每个输出文件必须写 `schema_version`。
- 不同 major 版本不得直接 merge，必须先生成 migration note。

## 3. 标识与时间

### 3.1 ID

- `session_id`：`LXR-{YYYYMMDD}-{source_hash前8位}`。
- `event_id`：`{session_id}-E{start_ms补12位}-{event_sequence补4位}`。
- `comment_event_id`：评论自身 event_id；没有评论时为 `null`。
- `idempotency_key`：由 schema/source_hash/lane/window/extractor version 计算。

同一 session 内 `event_id` 必须唯一；重跑不得产生第二套 ID。

### 3.2 时间

- 时间基准：源视频起点，单位整数毫秒。
- 约束：`0 <= start_ms < end_ms <= source_duration_ms`。
- `response_latency_ms` 从被链接评论首次出现到主播回复开始；关系不确定时仍可计算，但必须标 `derived`，不得当成因果证据。
- 管理窗口 overlap 内的重复事件由 timeline merger 串行去重。

## 4. evidence 与判断状态

### 4.1 `observation_status`

| 值 | 含义 | 允许来源 |
|---|---|---|
| `observed` | 画面或声音中直接观察 | 原视频、人工回看、原始 ASR/OCR 证据 |
| `derived` | 从时间码、音量、速度、规则计算 | 可重跑计算 |
| `inferred` | AI/规则对意图、关系、含义的推测 | 必须有 confidence 和 review flag |
| `manual_verified` | 人工看/听原证据后确认 | 必须记录 reviewer/result |

禁止将 `inferred` 直接改写成 `observed`。人工确认后保留原 inference，并把最终字段的状态写为 `manual_verified`。

### 4.2 `evidence_type`

允许：

- `video_frame`
- `audio_segment`
- `asr_segment`
- `comment_frame_track`
- `manual_annotation`
- `derived_timeline`
- `course_chunk`
- `course_source_quote`

### 4.3 `evidence_ref`

`evidence_ref` 只保存可追溯引用，不保存截图、原始音频或真实用户名。例如：

`video:sha256:<hash>#t=3150000-3154200`

`course:previous_pack:data/full_transcript_clean.jsonl:L0041:segments=120-144`

引用不可访问时：

- 保留原字符串。
- `course_fidelity=source_unavailable`
- `review_flag=true`
- `review_status=blocked`

## 5. 事件类型

`event_type`：

- `speaker_utterance`
- `comment`
- `response_link`
- `visual_action`
- `prosody`
- `course_alignment`
- `live_stage_transition`
- `risk_or_takeover`
- `brain_rule_candidate`
- `composite`

`composite` 仅用于最终事件视图；lane 原始输出应使用单一事件类型。

## 6. 基础证据字段

| 字段 | 类型 | 规则 |
|---|---|---|
| `session_id` | string | required |
| `source_video` | string | workspace 相对路径，不得是签名 URL |
| `source_hash` | string | `sha256:` + 64 位 hex |
| `event_id` | string | required + unique |
| `start_ms` | integer | required，非负 |
| `end_ms` | integer | required，大于 start |
| `evidence_type` | enum | required |
| `evidence_ref` | string | required，不含 PII |
| `observation_status` | enum | required |
| `confidence` | number | 0–1 |
| `review_flag` | boolean | required |
| `manual_review_result` | enum/null | `approved/revised/rejected/unreviewed` |
| `privacy_tier` | enum | `raw_local/redacted_repo` |
| `processing_level` | enum | `pilot/full/fallback/failed` |

## 7. 主播说话字段

- `speaker_text_raw`：ASR 原始文本；仅在不含未脱敏 PII 时进入 repo。
- `speaker_text_clean`：轻量断句/明显口误标记；不得改写含义。
- `asr_confidence`：0–1；引擎无置信度时为 `null` 并 review。
- `live_stage`：见标签体系。
- `utterance_function`
- `audience_state`
- `response_goal`
- `response_strategy`
- `utterance_structure`

规则：

- raw 与 clean 必须同时保留；clean 不能替代 raw。
- “主播思路”只能由上述可观察字段构成决策链，不允许字段名 `inner_thought/motivation_true`。
- 如果字段来自 AI 推测，`observation_status=inferred`。

## 8. 评论与回复字段

- `comment_event_id`
- `comment_text_redacted`
- `comment_intent`
- `comment_risk`
- `response_link_type`
- `response_latency_ms`
- `reply_target`
- `link_confidence`
- `unanswered_reason`
- `related_comment_event_ids[]`
- `reply_event_ids[]`

### 8.1 关系模型

| 场景 | 表达 |
|---|---|
| 一条评论对应多段回复 | comment 的 `reply_event_ids` 有多个；每条 reply 指向同一 comment |
| 多条评论合并一次回复 | reply 的 `related_comment_event_ids` 有多个；`response_link_type=aggregated` |
| 评论未回复 | `reply_event_ids=[]`，填写 `unanswered_reason` |
| 主播主动提问引发评论 | comment 反向链接 host question；`response_link_type=prompted_by_host` |
| 主题相近但因果不确定 | `response_link_type=topic_only/uncertain` |
| 明确读出/复述评论 | `direct_explicit`，仍保留 evidence |

`link_confidence` 不得由时间距离单独生成。高置信规则候选只接受：

- `direct_explicit`
- `manual_verified`
- 经 pilot 证明 precision 达标的 `likely_direct`

### 8.2 隐私

`redacted_repo` 禁止字段：

- 原始 username/user_id/avatar URL。
- 手机号、微信号、身份证、邮箱、地址。
- 原始评论截图。

匿名 `comment_event_id` 使用 session-local 编号或 HMAC，salt 只保存在 raw_local。

## 9. 真人动作与数字人动作

- `observed_action`
- `observed_action_confidence`
- `facial_expression`
- `gaze_target`
- `body_posture`
- `hand_gesture`
- `prop_or_courseware_interaction`
- `inferred_action_meaning`
- `avatar_action_candidate`
- `avatar_action_trigger`
- `action_duration`
- `action_cooldown`
- `action_conflict`
- `avatar_suitability`
- `action_review_flag`

约束：

1. `observed_action` 只描述画面，例如 `right_hand_open_palm`；不能写“为了说服用户”。
2. `inferred_action_meaning` 必须为 inference，可为空。
3. `avatar_action_candidate` 是替代动作，不等于真人原动作复刻。
4. `action_duration/action_cooldown` 单位毫秒。
5. `avatar_suitability=unknown/unsuitable` 时默认 `neutral_idle`。
6. 每句话都触发动作视为失败；需要 conflict/cooldown 抑制。

## 10. 语气节奏

- `speaking_rate`：字/分钟；无法可靠测量为 null。
- `pause_before_ms`
- `pause_after_ms`
- `emphasis_words[]`
- `volume_change`：dB 或类别，必须注明 derived。
- `prosody_label`
- `emotion_observed`
- `prosody_confidence`

`emotion_observed` 只描述可观察表达，例如 `smiling/serious/raised_volume`，不得写内心状态。

## 11. 课程对应

- `course_lesson_id`
- `course_chunk_id`
- `course_source_ref`
- `course_topic`
- `alignment_type`
- `alignment_confidence`
- `course_fidelity`
- `live_transformation_type`
- `live_example_or_story`
- `omitted_prerequisite`
- `unsupported_addition`
- `compliance_risk`

`alignment_type`：

1. `direct_course_quote`
2. `spoken_paraphrase`
3. `example_or_story`
4. `comment_driven_extension`
5. `course_to_sales_transition`
6. `unrelated`
7. `possible_insufficient_evidence`

当前完整原文不可访问时：

- 禁止 `direct_course_quote`。
- `course_fidelity=chunk_or_topic_only`。
- `alignment_confidence` 上限 0.69。
- `review_flag=true`。

## 12. 直播大脑桥接

- `trigger_type`
- `trigger_pattern`
- `audience_state`
- `decision_goal`
- `response_strategy`
- `response_template_structure`
- `course_source_ref`
- `avatar_action_candidate`
- `prosody_candidate`
- `next_question_or_hook`
- `risk_level`
- `human_takeover_required`
- `fallback_route`
- `review_status`

进入 V0 规则的硬门槛：

- 证据引用可回查或明确 blocked。
- `review_status=approved`。
- risk/takeover/fallback 非空。
- 不包含原始 PII。
- 不包含成交效果结论。

## 13. raw_local / redacted_repo

### raw_local

仅本地、Git ignored：

- 原始 OCR、username/user_id、截图轨迹。
- 原始 ASR 音频片段引用。
- HMAC salt。
- 临时关键帧、模型缓存、运行日志。

### redacted_repo

允许提交：

- 匿名 comment ID。
- 脱敏评论文本。
- 意图/风险/关系/置信度。
- 课程 source_ref。
- 动作/语气候选和 review 状态。

字段虽属于 schema，但 raw-only 值不得出现在 repo 样例。

## 14. 输出文件

pilot 每个 session：

```text
raw_local/{session_id}/
  lanes/
  checkpoints/
  quarantine/

redacted_repo/{session_id}/
  events.jsonl
  comment_reply_links.jsonl
  course_alignments.jsonl
  brain_rule_candidates.jsonl
  review_queue.csv
  validation_report.json
```

本规划不创建上述运行产物；只定义合同。

## 15. Validation

必须检查：

- JSON Schema 解析通过。
- required 字段存在。
- `event_id` 唯一。
- 时间合法。
- `source_hash` 合法。
- 关系引用的 event ID 存在。
- `manual_verified` 有 review result。
- `redacted_repo` 无禁止字段/PII。
- `direct_course_quote` 有可回查 source ref。
- `brain_rule_candidate` 满足 V0 硬门槛。
