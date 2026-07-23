# 主播思路、动作、评论标签体系

## 1. 标签原则

“主播思路”统一表达为**可观察的表达决策链**：

`可观察触发 → 直播阶段 → 表达功能 → 受众状态候选 → 回复目标 → 回复策略 → 结构 → 下一动作`

禁止标签：

- 主播真实内心想法。
- 未观察到的动机。
- “她就是想骗/想逼单/知道用户一定会买”等事实化心理判断。

受众状态、意图、动作含义均可能是 inference，必须保留 confidence/review。

## 2. `live_stage`

- `opening`
- `audience_warmup`
- `topic_entry`
- `course_explanation`
- `demonstration`
- `comment_interaction`
- `objection_handling`
- `benefit_explanation`
- `offer_or_rights`
- `promotion`
- `call_to_action`
- `transition`
- `closing`
- `interruption_or_abnormal`
- `unknown`

## 3. `utterance_function`

- `greeting`
- `attention_hook`
- `agenda_setting`
- `knowledge_definition`
- `step_instruction`
- `demonstration_narration`
- `example_or_story`
- `question_to_audience`
- `comment_readback`
- `direct_answer`
- `aggregated_answer`
- `clarification`
- `empathy_or_validation`
- `risk_disclaimer`
- `benefit_statement`
- `offer_explanation`
- `urgency_or_scarcity`
- `social_proof`
- `objection_response`
- `topic_transition`
- `recap`
- `next_hook`
- `manual_takeover_notice`
- `filler_or_repetition`
- `unknown`

## 4. `audience_state`

只允许候选：

- `new_arrival`
- `curious`
- `needs_basic_context`
- `asking_how_to`
- `asking_suitability`
- `asking_price_or_rights`
- `doubt_or_objection`
- `risk_or_compliance_question`
- `ready_for_action`
- `confused`
- `low_engagement`
- `mixed_or_unknown`

若不是评论明确表达，默认 `observation_status=inferred`。

## 5. `response_goal`

- `orient`
- `retain_attention`
- `explain`
- `teach_step`
- `clarify`
- `answer`
- `reduce_uncertainty`
- `handle_objection`
- `set_boundary`
- `transition_to_offer`
- `prompt_action`
- `invite_comment`
- `route_to_human`
- `recover_flow`
- `unknown`

## 6. `response_strategy`

- `direct_factual_answer`
- `definition_then_example`
- `problem_cause_solution`
- `acknowledge_then_reframe`
- `question_then_tailor`
- `group_similar_questions`
- `course_reference`
- `demonstration`
- `benefit_with_boundary`
- `social_proof_with_source`
- `offer_breakdown`
- `risk_disclaimer`
- `defer_and_takeover`
- `repeat_or_filler`
- `unknown`

## 7. `utterance_structure`

允许数组化结构：

- `hook`
- `acknowledge`
- `restate_question`
- `answer_core`
- `reason`
- `example`
- `step`
- `boundary`
- `course_reference`
- `offer`
- `call_to_action`
- `next_question`
- `recap`

例如：`["acknowledge","restate_question","answer_core","boundary","next_question"]`。

## 8. 评论意图 `comment_intent`

- `greeting_or_presence`
- `request_explanation`
- `how_to`
- `suitability`
- `symptom_or_problem`
- `course_content`
- `price`
- `offer_or_rights`
- `purchase_or_order`
- `refund_or_after_sales`
- `trust_or_evidence`
- `effect_or_outcome`
- `objection`
- `complaint`
- `risk_or_compliance`
- `off_topic`
- `spam_or_duplicate`
- `unreadable`
- `unknown`

## 9. 评论风险 `comment_risk`

- `none`
- `pii`
- `health_or_medical`
- `effect_guarantee`
- `minor_or_sensitive`
- `refund_or_legal`
- `payment_or_account`
- `harassment`
- `platform_compliance`
- `unknown`

`comment_risk != none` 时必须评估 `human_takeover_required`。

## 10. 评论—回复关系 `response_link_type`

- `direct_explicit`
- `likely_direct`
- `aggregated`
- `topic_only`
- `prompted_by_host`
- `unanswered`
- `uncertain`
- `none`

规则：

- 时间接近但无语义证据：`topic_only/uncertain`。
- 主播读出或复述评论：`direct_explicit`。
- 多条同类评论合答：`aggregated`。
- 评论无回复：`unanswered` + reason。

`unanswered_reason`：

- `not_seen`
- `duplicate_or_spam`
- `out_of_scope`
- `risk_requires_human`
- `time_limit`
- `host_changed_topic`
- `unreadable`
- `unknown`

## 11. 可观察动作

### `observed_action`

- `neutral_idle`
- `head_nod`
- `head_shake`
- `lean_forward`
- `lean_back`
- `open_palm`
- `pointing`
- `counting_gesture`
- `hands_together`
- `clap`
- `hold_prop`
- `demonstrate_with_prop`
- `touch_courseware_or_screen`
- `stand_or_sit_transition`
- `large_body_demonstration`
- `off_camera`
- `unclear`

### `facial_expression`

- `neutral`
- `smile`
- `serious`
- `surprised`
- `questioning`
- `emphasis`
- `unclear`

这里只描述可见表情，不命名内心情绪。

### `gaze_target`

- `camera`
- `comment_area`
- `courseware`
- `prop`
- `off_screen_person_or_device`
- `unknown`

### `body_posture`

- `seated_upright`
- `seated_leaning`
- `standing`
- `demonstration_posture`
- `partially_occluded`
- `off_camera`
- `unknown`

### `hand_gesture`

- `none`
- `open_hand`
- `single_finger_point`
- `counting`
- `shape_or_size`
- `hold_object`
- `two_hand_emphasis`
- `unknown`

## 12. 数字人动作候选

- `neutral_idle`
- `small_nod`
- `small_open_palm`
- `single_emphasis`
- `question_prompt`
- `serious_emphasis`
- `courseware_point`
- `product_or_prop_reference`
- `manual_takeover_idle`
- `unsuitable_for_avatar`

规则：

- 默认 `neutral_idle`。
- `large_body_demonstration` 不自动复刻，优先转为课件/真人片段/人工接管。
- action trigger 必须绑定 live stage/utterance function，不绑定单一关键词。
- 默认 duration 1,000–3,000ms；cooldown 至少 4,000ms，pilot 后再校准。
- 同时只能激活一个主动作；安全/人工接管优先级最高。

## 13. 语气节奏

### `prosody_label`

- `normal_explain`
- `slow_step_instruction`
- `question_prompt`
- `emphasis`
- `warning_or_boundary`
- `empathetic_acknowledgement`
- `offer_explanation`
- `call_to_action`
- `transition`
- `conclusion_summary`
- `unclear`

### `emotion_observed`

- `neutral_expression`
- `smiling_expression`
- `serious_expression`
- `raised_volume`
- `softened_volume`
- `faster_delivery`
- `slower_delivery`
- `unclear`

## 14. 课程与直播转译

沿用 `04_课程与直播表达对齐设计_course_live_alignment_design.md`：

- `direct_course_quote`
- `spoken_paraphrase`
- `example_or_story`
- `comment_driven_extension`
- `course_to_sales_transition`
- `unrelated`
- `possible_insufficient_evidence`

## 15. 风险与人工接管

`risk_level`：

- `low`
- `medium`
- `high`
- `blocked`

必须人工接管：

- PII/账号/支付。
- 健康/医疗/效果保证。
- 退款/法律/投诉。
- 未成年人或敏感场景。
- 课程来源不可确认且可能造成错误指导。
- OCR/ASR 低置信导致无法理解。
- 平台合规风险。

## 16. review 状态

- `unreviewed`
- `needs_review`
- `in_review`
- `approved`
- `revised`
- `rejected`
- `blocked`

只有 `approved` 的 brain rule candidate 能进入 V0 受控 demo。
