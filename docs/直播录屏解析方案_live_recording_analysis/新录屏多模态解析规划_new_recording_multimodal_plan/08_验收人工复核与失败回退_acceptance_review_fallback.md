# 验收、人工复核与失败回退

## 1. 验收分层

### 1.1 技术层

- source/hash/时间轴可追溯。
- schema/ID/ref 完整。
- 断点恢复和幂等通过。
- raw/repo 隔离。

### 1.2 内容层

- raw/clean 分开。
- 评论—回复关系有证据。
- 课程对齐有 source ref 或 blocked。
- 推测显式标记。

### 1.3 动作与人感层

- observed/inferred/avatar candidate 分开。
- 动作不过度、可抑制、有 cooldown/conflict。
- 看不清不猜。

### 1.4 V0 桥接层

- 规则单元字段完整。
- risk/takeover/fallback 完整。
- 仍是受控 demo 资料，不是正式直播验收。

## 2. pilot 指标

| 指标 | 抽样 | 通过阈值 | 失败处理 |
|---|---|---:|---|
| Schema validation | 全部事件 | 100% | 回数据合同 |
| 时间合法 | 全部事件 | 100% | 回 timeline merge |
| event_id unique | 全部事件 | duplicate=0 | 回幂等/merge |
| source trace | 全部事件 | 100% hash+ref | blocked |
| ASR CER | 每窗口 60 秒金标准 | ≤20% | 人工转写 fallback |
| ASR timestamp drift | 同一金标准 | median≤500ms；P95≤1200ms | 人工校时 |
| OCR detection recall | 每窗口 30 comments | ≥85% | 关键窗口人工标注 |
| OCR redacted text accuracy | 同一抽样 | ≥90% | 人工修订 |
| OCR duplicate rate | 同一抽样 | ≤5% | 调整跨帧去重 |
| high-confidence reply link precision | 每窗口 30 links | ≥90% | 降低 confidence/转人审 |
| uncertain link labeling | 全部 uncertain | 100% | 拒绝 pilot |
| high-confidence course precision | 每窗口 20 candidates | ≥90% | 只留 candidates |
| course source trace | 全部 alignment | 100% source_ref 或 blocked | 拒绝 promotion |
| observed action precision | 每窗口 30 actions | ≥90% | 只记人工 observed |
| unclear action marking | 全部不清晰动作 | 100% unknown/review | 拒绝 pilot |
| PII leak | 全 repo candidate | 0 | quarantine + blocked |
| media/cache/secret leak | 全 repo candidate | 0 | blocked |
| resume duplicate | 中断恢复测试 | 0 | 回 checkpoint/idempotency |
| V0 required fields | 全 candidates | 100% | 不进入 V0 review |

阈值是 pilot 初版，应由 5.6 根据金标准和业务风险复审；调整必须写 decision record，不能在 5.5 执行时悄悄放宽。

## 3. 人工复核队列

### P0：立即阻断

- PII 脱敏失败。
- 健康/医疗/效果保证。
- 退款/法律/支付/账号。
- 未成年人/敏感风险。
- source/hash 丢失。
- 规则可能进入 V0 但无 evidence。

### P1：进入 5.6 复审

- 评论—回复 uncertain/aggregated。
- 课程 source 不可达。
- 高置信课程候选。
- 动作/语气推测。
- course-to-sales transition。
- unsupported addition。

### P2：抽样

- 一般 ASR/OCR。
- 低风险普通讲解。
- neutral_idle 动作。

## 4. 复核记录

每条 review item：

- `review_item_id`
- `event_id`
- `reason_code`
- `priority`
- `evidence_ref`
- `model_or_rule_result`
- `reviewer_result`
- `corrected_value`
- `reviewer_id_or_role`
- `reviewed_at`
- `notes_redacted`

禁止把 reviewer 的自由文本写入真实 username/PII。

## 5. Codex 5.6 pilot 复审决策

### approved

仅当所有 hard gate 通过，且：

- schema 无缺字段。
- 三槽位代表性成立。
- 失败 fallback 可复现。
- V0 候选可被安全审核。

### revise

- 某 lane 指标未达标，但可通过 schema/标签/阈值/route 修正。
- 修订后必须重跑受影响 pilot lane。

### rejected

- 大量错配。
- 无法保护隐私。
- 无 source trace。
- 自动化需要边执行边猜核心路线。
- 无法断点恢复。

复审决策必须 machine-readable，见全量模板启动令牌。

## 6. fallback 详细规则

### 6.1 OCR

触发：

- recall/accuracy 未达标。
- 评论滚动过快、遮挡、字号过小。

处理：

- 只标事件关键窗口。
- 人工记录匿名评论与时间。
- 保留 `ocr_status=manual_fallback`。

禁止：

- 补造不可见评论。
- 用相似评论填满时间轴。

### 6.2 ASR

触发：

- CER/时间戳未达标。
- 噪声、重叠语音、音乐。

处理：

- raw 保留。
- 人工修关键 180 秒。
- clean 只做标点/断句。
- `asr_confidence=null/low`。

### 6.3 动作

触发：

- 遮挡、画面模糊、置信低。

处理：

- `observed_action=unclear`。
- avatar `neutral_idle`。
- 高价值动作转人工。

### 6.4 课程

触发：

- full transcript 不可访问。
- 多候选接近。

处理：

- chunk/topic only。
- top 3 candidates。
- exact quote blocked。

### 6.5 因果

触发：

- 仅时间接近。
- 多评论同时滚动。
- 主播未明确读评论。

处理：

- `topic_only/uncertain/aggregated`。
- 不生成 direct V0 trigger。

### 6.6 中断/损坏

- lane crash：重跑 lane/window。
- merge crash：只重跑 merge。
- source unreadable：blocked，不修源。
- overlap conflict：单 merger 决定。

### 6.7 隐私

- 任一 raw identifier 进入 repo candidate：移动到 quarantine、清空 export allowlist、重新脱敏、全量重扫。
- 无法证明 0 leak：不得 stage。

## 7. 失败标准

pilot 不通过：

- 评论和回复大量错配。
- 课程没有来源或 exact quote 伪造。
- 低置信动作直接写规则。
- PII 进入 repo candidate。
- 只有总结，没有事件数据。
- 只用固定管理分块，没有语义事件。
- 中断后重复/覆盖。
- 5.5 需自行决定核心路线。
- 技术结果写成成交/正式直播结论。

## 8. 5.6 复审清单

- [ ] 三槽位真实成立。
- [ ] source/hash/time/evidence。
- [ ] schema/ID/ref。
- [ ] ASR raw/clean。
- [ ] OCR 去重/脱敏。
- [ ] comment/reply evidence。
- [ ] course source/fidelity。
- [ ] observed/inferred/avatar。
- [ ] prosody evidence。
- [ ] V0 risk/takeover/fallback。
- [ ] PII/media/secret 0。
- [ ] resume/idempotency。
- [ ] 未外推业务结果。
- [ ] approval/revise/rejected 已写入。
