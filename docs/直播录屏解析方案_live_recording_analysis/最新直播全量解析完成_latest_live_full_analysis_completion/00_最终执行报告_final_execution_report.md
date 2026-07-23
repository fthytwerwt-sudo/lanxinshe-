# 最新直播 10 场全量多模态解析完成执行报告

## 主结论

`completed_with_source_limited_unknowns`：本轮已经把 10 场最新直播从上一轮候选包推进到完成包：音频来源分类、语义事件、60 秒视觉覆盖索引、评论生命周期、回复仲裁、课程清理、动作/语气补齐、规则证据、人工复核优先队列和机器验收均已落库。

`部分成立`：全量音频/语义基于 10/10 Alibaba Fun-ASR 结果闭环；视觉/评论/动作基于上一轮 Alibaba Qwen-VL 实证窗口加 60 秒覆盖登记闭环。没有 Qwen-VL 实证的窗口全部显式写为 `source_limited_unknown` / `not_observable`，未虚构评论、动作或直接回复。

`待验证`：人工尚未复核；本结果不等于客户验收、业务通过、数字人正式直播链路通过。

## 核心计数

- source sessions: `10`
- ASR/audio segments: `7296`
- semantic events: `1594`
- 60s visual coverage registry windows: `663`
- source-limited visual windows: `526`
- comment lifecycle rows: `214`
- reply arbitration rows: `214`
- valid course matches: `0`
- traceable rules: `126`
- manual review queue rows: `500`
- model-call ledger rows: `147`
- source-limited unknown rows: `2618`

## 关键边界

- `audit_or_input_preparation_not_fallback`：本轮没有用 ffmpeg/OpenCV/本地脚本修复最终视频或冒充模型能力。
- `raw_local_only`：原始视频、音频、API raw、private manifests、signed URLs 均保留在 `_local_runtime/` 或上一轮本地 runtime，不进入 Git。
- `course_alignment`：`topic_similarity_only` 不再计为有效课程匹配；缺 direct source quote 的课程型事件写 `blocked_source_missing`。
- `reply_arbitration`：时间接近不写 direct reply；默认写 `insufficient_source_evidence`、`topic_related_not_causal` 或 `comment_visible_but_unanswered`。

## 机器验收

- validation overall: `passed_with_source_limited_unknowns`
- blockers: `none`
- pilot decision: `approved`

## 完成边界

本包表示“全量解析证据已准备好进入人工/项目复核”，不表示客户验收、付款条件达成或正式直播平台链路可上线。
