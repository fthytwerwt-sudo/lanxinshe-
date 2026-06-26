# 00_阿里模型分工暂定表

状态：`model_role_map_completed` / `local_only_analysis_not_committed`

本文件只固化本项目当前人物形象、声音、动作解析任务里的临时模型分工。模型 connected 只代表接口可调用，不代表长视频、人审、数字人能力或供应商样片已通过。

| 模型名 | 中文职责 | 本轮是否使用 | 输入类型 | 输出类型 | 适合任务 | 不适合任务 | 是否可直接影响最终结论 | 是否需要人工复核 | Codex 调用方式 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen-vl-max | 主视频/画面/动作/表情分析模型 | True | short video clip or extracted frame | model-assisted visual observation JSON | 人物形象、表情、眼神、头肩身体动作、手势、遮挡、参考帧候选 | 完整长视频一次性判断、声音克隆、人审结论、直播能力通过结论 | no_model_observation_requires_summary_and_human_review | True | Codex extracts short clips, sends redacted Base64 data URL via DashScope compatible chat completions |
| qwen-vl-plus | 视频/画面复核模型 | True | selected short video clip | cross-check visual observation | 复核关键片段、检查主模型不确定动作/表情/遮挡 | 替代主审、人审通过、声音细节判断 | no_review_signal_only | True | Codex calls on at most one selected clip per recording, capped by qwen-vl-plus guard |
| qwen2.5-omni-7b | 音视频综合辅助模型，不做主审 | True | short video clip with audio | auxiliary voice and action observation | 少量代表片段的音色、语速、停顿、情绪和口型风险辅助观察 | 全量音频转写、声音克隆通过、人审结论 | no_auxiliary_only | True | Codex calls on selected high-audio clips, capped at 8 calls |
| qwen-max | 严格判断、素材筛选、微调建议和结论收束 | True | structured local metrics plus model observations | summary recommendations | 把候选片段、风险和后续数字人定制建议收束为可复审报告 | 直接观看完整原视频、替代人审、承诺供应商能力通过 | partial_summary_requires_human_review | True | Codex sends compact structured summary, not raw secrets or complete videos |
| qwen-plus | 低成本整理和文本结构化 | True | structured text summaries | field normalization notes | 报告字段校验、摘要整理、低成本结构化 | 严格风险结论、主视觉判断、长视频理解 | no_formatting_only | True | Codex sends compact field list for report normalization |
| wan2.2-s2v | 视频生成模型 | False | image URL plus audio URL | generated video | 后续 30 秒/60 秒样片生成候选 | 本轮人物解析、录屏理解、声音分析 | no_not_called | True | not called this round |
| text-embedding-v4 / text-embedding-v3 | 知识库检索向量模型 | False | text | embedding vector | 后续课程资料、规则、权益的知识库检索 | 人物形象、声音、动作解析 | no_not_called | False | not called this round |
| qwen3-rerank | 检索结果重排模型 | False | query and documents | reranked results | 后续 RAG 召回排序 | 人物形象、声音、动作解析 | no_not_called | False | not called this round |

## 执行口径

- 所有模型调用、素材解析、报告生成均由 Codex 执行。
- GPT 只做外层复审，不直接跑模型。
- `qwen-vl-max` / `qwen-vl-plus` 的输出是模型辅助观察，不是人审结论。
- `qwen2.5-omni-7b` 只做少量音视频综合辅助，不做主审。
- `wan2.2-s2v`、embedding、rerank 本轮均未调用。
