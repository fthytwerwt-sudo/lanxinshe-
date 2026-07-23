# 新直播录屏多模态解析总体规划

## 1. Requirements Summary

本规划把 10 个新直播录屏转成一条可执行、可验证、可暂停恢复的解析路线。目标不是总结视频，而是形成：

`源录屏证据 → 多模态事件 → 评论/回复关系 → 课程对齐 → 真人表达决策链 → 数字人候选动作/语气 → 直播大脑 V0 规则单元`

强制阶段：

1. Codex 5.6 sol：本规划和合同。
2. Codex 5.5：三个代表性 180 秒窗口小样。
3. Codex 5.6 sol：复审、改 schema/标签/阈值并签发 `pilot_review_decision=approved`。
4. Codex 5.5：全量分批执行。

本规划继承既有方案的 intake/弱标签/证据边界，但把“固定表格”和“300 秒管理分块”升级为事件级时间轴。既有方案证据见 `../01_直播录屏解析方案详细版_live_recording_analysis_plan.md:116-168`、`:240-257`。

## 2. 设计原则

1. **证据先于解释**：保留源视频、时间码和证据引用；观察、计算、推测、人工确认分栏。
2. **管理分块不等于语义事件**：固定窗口只服务调度和续跑，最终事件由评论出现、回复开始、主题/动作/语气变化重新切分。
3. **不确定性可交付**：无法确认的关系保留候选、置信度和复核队列，不强制选唯一答案。
4. **隐私 fail-closed**：原始评论/账号只在 `raw_local`；仓库只接收脱敏文本和匿名 ID。
5. **pilot 先于规模化**：自动化指标、字段和阈值必须由小样证据校准。
6. **V0 只消费规则单元**：V0 不直接消费故事性总结，也不把受控 demo 等同正式直播链路通过。

## 3. 当前能力与事实锚点

### 已确认

- 新录屏目录 `最新直播/` 有 10 个可 `ffprobe` 的竖屏 MP4，均含 AAC 音轨。
- 既有直播录屏方案已建立 intake 和 5 Sheet 资料结构，但明确不是实际解析结果：`../01_直播录屏解析方案详细版_live_recording_analysis_plan.md:14-21`、`:281-304`。
- 课程包有 1,610 lesson 映射、19,424 chunk/桥接行。
- 课程动作 19,424 个窗口均为低置信，语气基于文本关键词推测：`../../../项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/16_质量检查报告_quality_review_report.md:3-10`。

### 部分成立

- 评论、主播动作和商品/权益视觉元素在抽样帧中可观察。
- 课程摘要和 `source_ref` 可用于候选定位，但完整原文不在当前 workspace。
- `ffmpeg/ffprobe/cv2/Pillow` 可用于只读检测和输入准备；不是最终模型能力。

### 待验证 / blocked

- 本地 ASR/OCR 引擎不可用；不得因此假装自动转写或 OCR 已通过。
- 评论—回复因果、语气/停顿、动作识别、课程逐句匹配、长视频续跑均待 pilot。

详细矩阵见 `02_素材与能力缺口清单_asset_capability_gaps.csv`。

## 4. primary_route

### 4.1 Intake 与 session 锁定

对每个源视频建立只读清单：

- `source_video`：workspace 相对路径。
- `source_hash`：进入 pilot/full 前计算 SHA-256；规划阶段不得用文件名代替 hash。
- `session_id`：`LXR-{YYYYMMDD}-{source_hash前8位}`。
- `source_metadata`：容器、时长、分辨率、音视频 codec、stream start/duration。
- `weak_label`：只记录来源目录或人工给定的主观标签，不写业务效果。

源视频不移动、不改名、不转码。

### 4.2 调度窗口

长视频按可配置的 20 分钟管理窗口调度，默认前后各重叠 30 秒：

- `management_window_ms=1200000`
- `overlap_ms=30000`

这只用于资源控制、重试和并行；不得直接成为最终事件边界。

### 4.3 四路独立证据抽取

可并行：

1. `audio_lane`：ASR raw/clean、词/句时间戳、音量、停顿、语速候选。
2. `comment_lane`：评论区关键窗口、OCR、跨帧去重、匿名化、出现/消失时间。
3. `visual_lane`：可观察动作、表情、视线、姿态、道具/课件交互。
4. `course_candidate_lane`：基于 clean text、topic、lesson/chunk 摘要检索候选。

每一路只写自己的 lane 输出和 checkpoint，不直接写最终事件表。

### 4.4 统一时间轴

串行合并：

1. 将所有时间统一为相对源视频的整数毫秒。
2. 校验 `0 <= start_ms < end_ms <= source_duration_ms`。
3. 对重叠管理窗口去重。
4. 基于变化点生成语义事件：
   - 评论新增/快速滚动/停止。
   - 主播开始/结束回答。
   - 主题或直播阶段变化。
   - 课程知识点变化。
   - 异议、权益、促单、风险表达。
   - 动作/表情/视线显著变化。
   - 停顿、语速、音量显著变化。
   - 异常或人工接管。

### 4.5 评论—回复关系

先生成候选边，再判断关系：

- 时间窗口：评论出现到主播回复结束。
- 文本/主题相似度。
- 指代词、复述、称呼、数量/价格/课程名等实体重叠。
- 主播是否明确读评论或回应多条同类问题。
- 是否存在更早的主播主动提问。

输出 `direct_explicit / likely_direct / aggregated / topic_only / prompted_by_host / unanswered / uncertain / none`。只有 `direct_explicit` 或人工确认才能进入高置信规则；“时间接近”单独不能证明因果。

### 4.6 课程对齐

两阶段：

1. 当前可执行：lesson/chunk/topic 候选检索。
2. 完整原文可访问后：source quote/segment 级验证。

课程对应必须区分直接讲解、口语改写、案例解释、评论延展、课程转销售、无关、证据不足。详见 `04_课程与直播表达对齐设计_course_live_alignment_design.md`。

### 4.7 真人动作到数字人动作

三层分开：

- `observed_action`：画面中直接看到的真人动作。
- `inferred_action_meaning`：AI 对动作含义的推测，只可进入复核。
- `avatar_action_candidate`：数字人的安全替代动作。

低置信或不适配时使用 `neutral_idle`。数字人候选必须定义 trigger、duration、cooldown、conflict、suitability 和 review flag。课程包已明确低置信动作不得直接自动播：`../../../项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/12_数字人动作触发规则_avatar_action_trigger_rules.csv:2-5`。

### 4.8 直播大脑 V0

只有人工复核通过的事件/规则才能生成：

- trigger pattern。
- audience state。
- decision goal。
- response strategy/template structure。
- course source ref。
- avatar/prosody candidate。
- next hook。
- risk/takeover/fallback。

V0 输出必须保留 `event_id/evidence_ref/review_status`，以支持回放和人工接管。

## 5. fallback_route

| 失败点 | 降级路线 | 不允许的伪装 |
|---|---|---|
| OCR 不稳定 | 只标三个关键窗口；评论内容转人工标注 | 不生成伪全量评论时间轴 |
| ASR 不稳定 | 保留 raw/clean；人工修关键句；低置信入队列 | 不把润色文案当原话 |
| 动作低置信 | 只记可观察动作；数字人默认 `neutral_idle` | 不把文本关键词当真实动作 |
| 课程原文不可访问 | 降级 lesson/chunk/topic；exact quote 标 blocked | 不伪造逐句来源 |
| 隐私脱敏失败 | 停止 repo 写入，隔离到 raw_local quarantine | 不提交用户名/手机号/微信等 |
| 长视频中断 | 从 lane checkpoint 重跑当前管理窗口 | 不重写已完成全局结果 |
| 单视频损坏 | 标 `blocked_source_unreadable`，跳过并保留清单 | 不修改/修复源文件 |
| 因果不确定 | 多候选 + `uncertain` + 人审 | 不按时间邻近强配 |
| 动作冲突 | 保留语义主动作，其余 `suppressed_by_conflict` | 不叠加连续动作 |
| 课程/业务风险 | `human_takeover_required=true` | 不自动输出承诺/医疗效果等 |

## 6. pause/resume 与幂等

状态机：

`planned → running → checkpointed → completed_lane → merge_pending → review_pending → approved/rejected/blocked`

每个 lane 只写：

- `checkpoint_id`
- `source_hash`
- `window_start_ms/window_end_ms`
- `input_fingerprint`
- `output_hash`
- `status`
- `attempt`
- `error_code`
- `updated_at`

`idempotency_key = sha256(schema_version + source_hash + lane + window_start_ms + window_end_ms + extractor_version)`。

恢复规则：

- checkpoint 与 input fingerprint 一致：跳过已完成 lane。
- extractor/schema 版本变化：只使受影响 lane 失效。
- merge 失败：重跑 merge，不重跑四路抽取。
- overlap 冲突：由单线程 timeline merger 决定，不允许 worker 各自覆盖。

## 7. 并行与串行边界

可并行：

- 不同 source video。
- 同一视频的 ASR/OCR/visual/course candidate lanes。
- 不相邻管理窗口的只读抽取。

必须串行：

- session/source hash 锁定。
- 重叠窗口去重和统一时间轴。
- 评论—回复最终因果。
- 课程最终对齐。
- V0 规则沉淀。
- 人工复核结果合并。
- repo 脱敏扫描和 Git stage。

## 8. pilot 选样

三个实际候选窗口已写入 `data/pilot_task_manifest.json`：

1. NR001 约 04:00–07:00：目标槽位 `course_explanation_low_comment`。
2. NR010 约 52:30–55:30：目标槽位 `dense_comment_interaction`。
3. NR005 约 48:00–51:00：目标槽位 `promotion_objection_benefit`。

这些类别是根据视觉密度、主播/道具和商品卡作的**待验证槽位**。Codex 5.5 开始前，必须用前 30 秒 ASR 或人工听审确认；不匹配则在 10 个候选中替换，不得硬贴标签。

## 9. Acceptance Criteria

pilot 通过必须同时满足：

1. 三个目标槽位各有一个上下文完整窗口。
2. JSON Schema 校验 100% 通过。
3. 核心时间字段合法率 100%，`event_id` 重复数 0。
4. 三个窗口各抽 60 秒人工金标准，ASR normalized CER ≤ 20%；不满足则走人工转写 fallback。
5. 每窗口至少人工核对 30 个可见评论事件；OCR detection recall ≥ 85%，脱敏后 normalized text accuracy ≥ 90%，重复率 ≤ 5%；不满足则关键窗口人工标注。
6. 高置信评论—回复链接人工 precision ≥ 90%；所有不确定关系 100% 标 `uncertain/derived/inferred`。
7. 高置信课程对齐人工 precision ≥ 90%，且 100% 有可回查 source_ref 或明确 blocked。
8. 动作抽检 precision ≥ 90%，所有看不清动作 100% 标 unknown/review。
9. PII/secret/media 进入 repo 的数量为 0。
10. 人为中断后恢复测试无重复事件、无覆盖已确认结果。
11. V0 规则单元必填字段完整率 100%，但不得写成交/正式直播能力通过。
12. Codex 5.6 sol 签发 `pilot_review_decision=approved`。

详细抽样与 fallback 见 `08_验收人工复核与失败回退_acceptance_review_fallback.md`。

## 10. Implementation Steps

### 阶段 A：Codex 5.5 pilot

1. 读取 `06_Codex5.5小样试跑执行单_codex_5_5_pilot_prompt.md` 与 `data/pilot_task_manifest.json`。
2. 只读核验三个 source 与 hash。
3. 先做 30 秒内容分类和隐私预检。
4. 确认 ASR/OCR 执行路线；无授权引擎则切人工 fallback。
5. 四 lane 输出到本地 pilot 工作区。
6. 串行统一时间轴和关系。
7. 生成 `redacted_repo` 小样与 review queue。
8. 运行验收，不触发 full。

### 阶段 B：Codex 5.6 sol 复审

1. 按三类事件抽样。
2. 计算 ASR/OCR/link/course/action 指标。
3. 检查过度推测和隐私。
4. 决定 `approved / revise / rejected`。
5. 如需修改，提升 schema version 并生成 migration note。

### 阶段 C：Codex 5.5 full

只有 approved 后读取 `07_Codex5.5全量执行模板_codex_5_5_full_execution_template.md` 和 `data/full_batch_manifest_template.json`，按 source/batch 分批执行。

## 11. Verification Steps

- `jq empty data/*.json`
- JSON Schema 自检与样例验证。
- CSV header/行数/必填状态验证。
- 时间轴、唯一 ID、source hash/source ref 规则验证。
- `rg` 检查 raw username/手机号/微信/URL/secret 字样，仅允许出现在规则说明，不能有真实值。
- 媒体扩展名和 AppleDouble 扫描。
- `git diff --check`
- `git diff --cached --name-only` 必须只有本目录 13 个文件。
- commit/push 后比较 local HEAD 与 `git ls-remote origin refs/heads/main`。

## 12. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 高分辨率录屏体积大 | I/O 和长时任务失败 | 管理窗口、checkpoint、只读 |
| 评论滚动/遮挡 | OCR 漏检/重复 | 关键帧轨迹 + 时间去重 + 人审 |
| 账号 PII | 合规和误提交 | raw/repo 双层、fail-closed |
| ASR/OCR 引擎缺失 | pilot 自动化 blocked | 先确认授权路线；人工三窗口 fallback |
| 课程原文不可回查 | 误写精确匹配 | 降级 chunk/topic，exact blocked |
| 动作过度解释 | 不自然数字人规则 | observed/inferred/avatar 三层 |
| 管理窗口截断事件 | 因果链断裂 | 30 秒 overlap + 串行 stitch |
| 多 agent 写同一汇总 | 数据竞争/覆盖 | lane 独立写，单 merger |
| 视觉 demo 外推 | 业务夸大 | 状态词和 V0/正式直播边界 |

## 13. Done / Blocked

本规划包完成不等于 pilot 完成。当前阶段完成的唯一含义是：规划、合同、manifest 和验证已落库。

后续 pilot 若遇到以下任一项，保持 `blocked`：

- 未授权 ASR/OCR 且无人工作为 fallback。
- source hash 或路径不可追溯。
- 原始 PII 无法隔离。
- exact course alignment 被要求但完整原文不可访问。
- schema/manifest 与本规划不一致。
- 未经 5.6 复审试图启动 full。
