# 课程与直播表达对齐设计

## 1. 当前事实

- 课程 lesson 映射：1,610。
- 课程直播桥接字段：19,424 行。
- 三线阅读版只展示前 200 行，完整主表属于大文件引用。
- 完整逐字稿通过 `previous_pack:data/full_transcript_clean.jsonl` 引用，但文件当前不在授权 workspace。
- 课程动作全量低置信；语气主要为文本关键词推测。

证据：

- `../../../项目资料_docs/课程解析资料_course_analysis/README_课程解析资料入口_course_analysis_index.md:12-27`
- `../../../项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/17_神经数字人课程解析总包_neural_avatar_course_analysis_master.md:24-42`
- `../../../项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/16_质量检查报告_quality_review_report.md:3-10`

结论：

- `已确认`：lesson/chunk/topic 候选入口存在。
- `部分成立`：chunk 摘要可支持候选检索。
- `blocked`：逐句 quote 级精确对齐，直到完整原文可回查。

## 2. 对齐目标

不是判断“主播有没有背课程”，而是回答：

1. 这段直播表达可能来自哪个 lesson/chunk/topic。
2. 主播如何把课程知识转成直播表达。
3. 哪些前提被省略、哪些内容新增、是否有合规风险。
4. 课程知识何时转入案例、互动、促单或销售。
5. 证据强度和人工复核状态是什么。

## 3. 对齐对象

### 3.1 直播侧

- `speaker_text_raw/clean`
- `live_stage`
- `utterance_function`
- 评论意图/回复目标
- 前后 30–90 秒上下文
- 可观察道具/课件

### 3.2 课程侧

- `lesson_id`
- `chunk_id`
- `source_time`
- `source_ref`
- `knowledge_point_sample`
- `course_topic`
- 课程结构/案例/问答/桥接字段

动作和语气只作辅助候选，不进入课程文本真实性评分。

## 4. 双阶段路线

### 阶段 A：当前可执行的候选检索

1. 对 `speaker_text_clean` 只做保真规范化：
   - 统一空白/标点。
   - 统一明显同义写法。
   - 保留数字、课程名、器材名、专有词。
2. 生成检索单元：
   - 当前 utterance。
   - 前后 utterance。
   - 评论意图。
   - 直播阶段。
3. 从 bridge CSV / course knowledge 中检索 top 5 candidate。
4. 使用可审计特征重排：
   - 专有词/课程名重叠。
   - 核心概念重叠。
   - 顺序/前提一致。
   - 示例/道具一致。
   - 评论意图是否解释了直播延展。
5. 只输出 candidate，不直接写最终对应。

### 阶段 B：完整原文可访问后的 source 验证

1. 解析 `source_ref` 定位 lesson/segments。
2. 读取原始 quote 和上下文。
3. 对比课程原文、直播 raw、直播 clean。
4. 标注省略、新增、例子、销售转入。
5. 人工确认高价值/高风险对齐。

若阶段 B 不可用，阶段 A 的 `alignment_confidence` 不得高于 0.69。

## 5. `alignment_type`

| 值 | 判断 | 必要证据 |
|---|---|---|
| `direct_course_quote` | 直播基本复述课程原文 | 可访问 quote + source_ref |
| `spoken_paraphrase` | 核心命题一致，口语化改写 | source quote + 语义/前提一致 |
| `example_or_story` | 用案例/故事解释课程 | 课程知识点 + 直播例子 |
| `comment_driven_extension` | 评论触发临时延展 | comment link + course candidate |
| `course_to_sales_transition` | 从知识转入课程/商品销售 | 前后事件 + 销售视觉/话术证据 |
| `unrelated` | 无直接课程关系 | 人工或充分负证据 |
| `possible_insufficient_evidence` | 可能对应但证据不足 | candidate + blocked/review |

## 6. `course_fidelity`

- `exact_source_verified`
- `meaning_preserved`
- `partial_with_omissions`
- `expanded_with_supported_content`
- `expanded_unsupported`
- `chunk_or_topic_only`
- `source_unavailable`
- `not_applicable`

## 7. 直播转译类型

`live_transformation_type`：

- `definition_to_plain_language`
- `step_to_demonstration`
- `principle_to_example`
- `knowledge_to_answer`
- `knowledge_to_objection_handling`
- `knowledge_to_benefit`
- `knowledge_to_sales`
- `knowledge_to_hook`
- `unrelated`

## 8. 对齐评分

评分只排序 candidate，不自动代表事实：

```text
candidate_score =
  0.30 * key_term_overlap
  + 0.25 * concept_similarity
  + 0.15 * prerequisite_consistency
  + 0.10 * example_or_prop_match
  + 0.10 * live_stage_compatibility
  + 0.10 * context_continuity
```

约束：

- 任一特征来源和版本必须记录。
- 没有 source quote 时，score 上限 0.69。
- `course_to_sales_transition` 不因商品卡出现就自动成立；需要前后表达证据。
- 涉及健康/效果/承诺的内容即使高分，也必须 `compliance_risk` + 人审。

## 9. 人工复核

优先级：

1. 进入 V0 的规则。
2. 高风险/健康/效果/退款/价格/权益。
3. `alignment_confidence >= 0.7` 但 source 不可达。
4. 多个候选分差 < 0.1。
5. `unsupported_addition` 非空。
6. comment-driven extension。

复核输出：

- candidate accepted/rejected/replaced。
- course lesson/chunk/source ref。
- alignment type/fidelity。
- omitted prerequisite。
- unsupported addition。
- compliance risk。

## 10. fallback

| 缺口 | 处理 |
|---|---|
| 完整逐字稿不可访问 | 只到 chunk/topic；exact quote blocked |
| lesson/chunk 摘要太短 | 扩大到相邻 chunk；仍不足转人工 |
| 多候选相近 | 保留 top 3，不强行唯一 |
| 课程索引缺失 | `course_fidelity=source_unavailable` |
| 直播 ASR 低置信 | 先人工修 raw，不使用 clean 猜课程 |
| 评论关系不确定 | 不标 comment-driven extension |
| 高风险表达 | 人工合规审查，不进入自动 V0 |

## 11. pilot 通过标准

- 三窗口每个至少 20 个可对齐 utterance 或按实际数量全量复核。
- 高置信 candidate 人工 precision ≥ 90%。
- 100% 对齐有 source_ref 或明确 blocked。
- 无 source quote 时 `direct_course_quote` 数量为 0。
- 100% unsupported additions 有 review flag。
- 与评论有关的课程延展 100% 有评论关系证据。
