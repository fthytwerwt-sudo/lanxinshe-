# 人工复核清单_manual_review_list

- OCR 不可用：全量课件画面需人工抽查或后续 OCR 补跑。
- 动作识别低置信度：19424 个 chunk 使用 `low_confidence_action_pending_review`。
- 逐字稿 chunk 级摘要：未复制完整逐字稿，需通过 source_ref 回查上一轮包。
- 视频时长为 0 或不可读 chunk：7。
- 样本关键帧抽取失败：0。

复核顺序：先看三线对照表，再按 `lesson_id/chunk_id` 回看原视频或低清样本帧，最后回填动作与课件文字。
