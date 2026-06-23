# 阿里大模型连接总探针报告

# 一页结论

- status: `completed_connected_core_models`
- connected 模型: qwen-plus, qwen-max, qwen-vl-max, qwen-vl-plus, qwen2.5-omni-7b, text-embedding-v4, text-embedding-v3, qwen3-rerank
- failed / blocked 模型: 无
- skipped 模型: wan2.2-s2v
- `已确认`：本轮只做低成本最小连接探针；技术连通不等于内容、人感、人审或长视频能力通过。
- `部分成立`：短视频/抽帧探针只能证明账号、模型和输入方式的局部可用性，不能外推 4-5 小时直播稳定。

# 0. 本轮边界与安全确认

- workspace: `/Volumes/WD_BLACK/澜心社直播`
- branch: `main`
- remote: `origin	https://github.com/fthytwerwt-sudo/lanxinshe-.git (fetch)
origin	https://github.com/fthytwerwt-sudo/lanxinshe-.git (push)`
- dry/safe mode: `yes`
- paid API call: `yes_minimal_probe`
- generated video: `no`
- OSS upload: `no`
- committed media: `no`
- printed secret: `no`

# 1. 环境变量与密钥安全检查

- `.env` found: `yes`
- `.env` path: `/Volumes/WD_BLACK/澜心社直播/.env`
- 环境变量只记录 present / missing / empty，不记录值。

| env | status |
| --- | --- |
| DASHSCOPE_API_KEY | present |
| ALIYUN_API_KEY | missing |
| ALIBABA_CLOUD_ACCESS_KEY_ID | present |
| ALIBABA_CLOUD_ACCESS_KEY_SECRET | present |
| ALIYUN_OSS_BUCKET | missing |
| ALIBABA_OSS_BUCKET | present |
| ALIYUN_OSS_ENDPOINT | missing |
| ALIBABA_OSS_ENDPOINT | present |
| ALIYUN_OSS_REGION | missing |
| ALIBABA_REGION_ID | present |
| ALLOW_WAN_GENERATION_PROBE | missing |
| ALLOW_ALIBABA_MODEL_TEST | present |
| ALLOW_QWEN_CHAT_TEST | present |

# 2. 已读取文件

| path | status |
| --- | --- |
| AGENTS.md | present |
| README.md | present |
| docs/alibaba_api_setup.md | present |
| docs/qwen_model_connection.md | present |
| docs/oss_setup.md | present |
| docs/happyhorse_i2v_connection.md | present |
| codex_reports/20260616_数字人直播质量参考解析_video_quality_reference_analysis.md | present |
| local_only_reports/20260619_数字人直播技术路线核实与实现方案_local_only_technical_route_plan.md | present |
| local_only_reports/直播前期总控施工图_live_front_planning_blueprint/00_数字人直播前期规划总控图_live_front_planning_master_blueprint.md | present |

# 3. 模型类别与用途总表

| 类别 | 候选模型 | 直播项目用途 | 本轮结果 |
| --- | --- | --- | --- |
| text | qwen-plus, qwen-max, qwen-turbo | 直播评论判断、回复生成、规则解释、结构化输出 | connected |
| vision_video | qwen-vl-max, qwen-vl-plus, qwen3-vl-plus, qwen3-vl-flash, qwen3-vl-235b-a22b-instruct | 直播录屏、数字人样片、参考视频的视觉/视频理解 | connected |
| omni | qwen2.5-omni-7b, qwen3.5-omni-plus | 音频 + 视频 + 文本综合理解候选 | connected |
| embedding | text-embedding-v4, text-embedding-v3 | 课程资料、价格权益、退款规则、禁说规则的语义检索 | connected |
| rerank | qwen3-rerank, gte-rerank-v2 | 召回结果重排，提升知识库命中顺序 | connected |
| wan_s2v | wan2.2-s2v | 15 秒数字人口型样片生成候选，不用于视频分析 | pending_or_blocked |

# 4. 文本模型连接结果

| 模型 | 状态 | 输入方式 | 输出摘要 | 错误摘要 |
| --- | --- | --- | --- | --- |
| qwen-plus | connected | text | {   "intent_type": "价格咨询与效果承诺质疑",   "risk_level": "中风险",   "knowledge_needed": ["课程定价政策", "收益承诺合规边界", "教育服务广告法限制"],   "handover_required": true,   "auto_reply_allowed": true,   "safe_reply_summary": "课程费用请参考直播间商品链接；学习效果因 |  |
| qwen-max | connected | text | {   "intent_type": "inquiry_pricing_and_effectiveness",   "risk_level": "medium",   "knowledge_needed": "pricing_policy, course_effectiveness_disclaimer",   "handover_required": true,   "auto_reply_allowed": false,   "sa |  |

# 5. 视觉 / 视频理解模型连接结果

| 模型 | 状态 | 输入方式 | 输出摘要 | 错误摘要 |
| --- | --- | --- | --- | --- |
| qwen-vl-max | connected | video_base64_short_clip | ```json {   "visible_scene": "室内直播间，背景为粉色与白色相间的装饰墙，带有拱形门洞和红色条纹元素，右侧有红色堆叠的道具，整体风格温馨可爱。",   "anchor_action": "主播站立于画面中央，双手自然摆动，进行讲解或展示动作，身体轻微晃动，表情生动，时而微笑，时而张嘴说话，动作流畅自然。",   "product_or_prop": "主播身穿白色短款外套搭配灰色百褶裙，脚穿黑色靴子，展示服装 |  |
| qwen-vl-plus | connected | video_base64_short_clip | ```json {   "visible_scene": {     "description": "一位女性主播站在一个装饰有红色和白色元素的室内场景中，背景是一个拱形门洞，两侧有红色装饰物。",     "elements": [       "主播",       "拱形门洞",       "红色装饰物",       "白色墙面"     ]   },   "anchor_action": {     "description |  |

# 6. Omni 全模态模型连接结果

| 模型 | 状态 | 输入方式 | 输出摘要 | 错误摘要 |
| --- | --- | --- | --- | --- |
| qwen2.5-omni-7b | connected | video_with_audio_base64 | 不适合，因为画面中人物一直在动，无法集中注意力看屏幕上的内容。 |  |

# 7. Embedding / Rerank 连接结果

| 模型 | 状态 | 输入方式 | 输出摘要 | 错误摘要 |
| --- | --- | --- | --- | --- |
| text-embedding-v4 | connected | text | embedding_dimension=1024 |  |
| text-embedding-v3 | connected | text | embedding_dimension=1024 |  |
| qwen3-rerank | connected | query_and_documents | rerank_response_received |  |

# 8. Wan 视频生成模型配置 / dry-run 结果

| 模型 | 状态 | 输入方式 | 输出摘要 | 错误摘要 |
| --- | --- | --- | --- | --- |
| wan2.2-s2v | skipped_cost_guard | image_url_and_audio_url | configured_only; actual video generation skipped because ALLOW_WAN_GENERATION_PROBE is not true. |  |

# 9. 视频素材输入方式判断

- source_video_found: `True`
- source_video_path: `参考/直播质量/v2700fgi0000d73l0jvog65n1dmfb190 2.MP4`
- local short clip: `yes`
- frame fallback: `yes`
- OSS URL: `not_used`，本轮短片段 Base64 / 抽帧路径足够；报告未写入 signed URL。

# 10. 当前最推荐的视频分析主模型

- `已确认`：本轮首选视频分析主模型为 `qwen-vl-max`，因为它完成了短直播片段 `video_base64_short_clip` 探针。
- `已确认`：当前备选视频分析模型为 `qwen-vl-plus`；后续可以在同一 15 秒片段上对比稳定性和输出字段一致性。
- `部分成立`：本轮只证明短片段视频理解可调用，不能写成长视频、全量录屏或人审质量通过。
- `通用建议`：真实录屏解析 V0 先用 15 秒片段，保留抽帧 fallback；60 秒和完整录屏必须单独 probe。

# 11. 当前最推荐的直播评论判断模型

- `已确认`：风险更敏感的评论判断首选 `qwen-max`；它本轮返回了更保守的 `auto_reply_allowed=false` 倾向。
- `部分成立`：`qwen-plus` 可作为低成本/常规评论备选，但仍需规则层约束。
- `待验证`：价格、权益、退款和效果承诺仍需客户资料和规则库，不可让模型自由承诺。

# 12. 当前最推荐的知识库检索模型

- `已确认`：知识库向量化首选 `text-embedding-v4`，本轮输出维度为 1024。
- `已确认`：重排首选 `qwen3-rerank`，适合课程资料、权益、退款和禁说规则召回后二次排序。
- `待验证`：这还不是完整 RAG 通过；仍需索引写入、检索 readback、stale cleanup 和命中质量验证。

# 13. 失败项、blocked 和待确认

| 类别 | 模型 | 状态 | 错误摘要 |
| --- | --- | --- | --- |
| 无 | 无 | 无 | 无 |

# 14. 后续 Codex 任务建议

1. 用本轮 connected 的视觉模型做 15 秒真实录屏解析 V0，并保留抽帧 fallback。
2. 如视频模型要求公网 URL，再单独做 OSS signed URL 探针，报告只写 redacted URL。
3. 高成本 Omni / Wan / 长视频解析必须单独开关和单独任务，不并入本轮总探针。
4. 将 connected 的文本模型接入评论规则 dry-run，但价格、退款、收益承诺必须走人工接管。
5. Embedding connected 后再做小型课程资料 RAG probe，确认维度、索引、检索 readback。

# 官方资料参考

- Qwen 视觉/视频理解：https://help.aliyun.com/zh/model-studio/vision
- OpenAI 兼容 Chat / 多模态输入：https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions
- OpenAI 兼容 Embedding：https://help.aliyun.com/zh/model-studio/embedding-interfaces-compatible-with-openai
- Qwen-Omni：https://help.aliyun.com/zh/model-studio/qwen-omni
- Rerank：https://help.aliyun.com/zh/model-studio/text-rerank-api
- wan2.2-s2v：https://help.aliyun.com/zh/model-studio/wan-s2v-api
