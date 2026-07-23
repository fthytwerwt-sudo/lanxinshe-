# 数据字典_data_dictionary

`已确认`：本目录是最新直播 10 个素材的脱敏事实层，不包含原始视频、原始音频、原始 OCR、用户名映射、signed URL、secret 或缓存。

## 状态口径

- `full_evidence_extraction_completed_pending_5_6_review`：素材级取证、ASR/API 结果和脱敏索引已生成，解释层等待 5.6 复审。
- `provisional_pending_5_6_review`：所有解释层候选字段的统一状态。
- `partially_true`：局部链路成立，但需要人工复核或 5.6 锁字段。

## 核心字段

- `observation_status=observed/derived/inferred/manual_verified/blocked`：区分直接观察、计算得到、AI 推测、人工确认和阻断。
- `response_link_type`：只表示候选关系，不表示确定因果。
- `course_source_ref`：来自课程桥接 CSV 或 `insufficient_evidence`，本轮不写逐句最终对应。
- `comment_text_redacted`：只能保存脱敏评论文本；原始评论不得进入 GitHub。

## 本轮 API

- ASR：Alibaba Fun-ASR HTTP submit/poll，结果保存在本地运行层，GitHub 只保留脱敏句子索引。
- 多模态：Qwen-VL 短窗口观察，GitHub 只保留脱敏摘要和候选字段。
- 本地 ffmpeg/ffprobe 仅用于 `audit_or_input_preparation_not_fallback`。
