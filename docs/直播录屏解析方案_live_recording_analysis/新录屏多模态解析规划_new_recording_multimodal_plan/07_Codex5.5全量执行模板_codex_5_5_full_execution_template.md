# Codex 5.5 新直播录屏多模态解析全量执行模板

> 本模板当前状态：`blocked_until_pilot_review_approved`。没有 Codex 5.6 sol 的书面 machine-readable approval，不得执行。

## 1. 启动令牌

必须存在本地或 repo 复审文件：

```json
{
  "pilot_review_decision": "approved",
  "approved_schema_version": "1.0.0",
  "approved_by": "Codex 5.6 sol",
  "approved_at": "ISO-8601",
  "pilot_run_id": "..."
}
```

缺任一字段即 blocked。

## 2. Goal

对 approval 指定的 source inventory 按 source/batch 分批执行多模态解析，输出可追溯、脱敏、可续跑的事件和人工复核队列。

不做：

- 不修改源媒体。
- 不自动生成最终直播脚本。
- 不训练数字人。
- 不判断成交/客户业务目标。
- 不把未复核规则送入正式直播。

## 3. Context 上下文

- workspace：`/Volumes/WD_BLACK/澜心社直播`
- branch：`main`
- remote：`https://github.com/fthytwerwt-sudo/lanxinshe-.git`
- fact source：当前 GitHub `main` 文件、已批准 pilot review decision、本轮验证与 Git 证据。
- P0：只执行 approval 和 full run manifest 明确列出的 source。
- P1：本规划、pilot 结果、课程资料、既有直播录屏方案。
- P2：历史经验只作参考。
- 冲突：`P0 > P1 > P2`。

## 4. Constraints 边界

允许：

- 只读 allowlist source。
- 在 `local_only_reports/` 写 lane/checkpoint/raw/redacted 工作产物。
- 使用 pilot approval 锁定的 extractor/version/threshold。
- 按批准 parallelism 分批执行。

禁止：

- approval 缺失或 schema major 不一致时启动。
- 修改、移动、删除、改名、转码或修复源视频。
- 安装未授权依赖或调用未授权/付费 API。
- 提交 raw OCR、username/user_id、截图、媒体、缓存、secret。
- 用固定管理窗口替代语义事件。
- 时间邻近即认定评论因果。
- 无完整原文时生成 `direct_course_quote`。
- 自动把 V0 candidate 投产。
- `git add .`。

## 5. 六层需求确认

### 5.1 目标层

按 approval 对 allowlist 源完成可追溯、脱敏、可续跑的事件解析；不判断成交、正式直播或客户验收。

### 5.2 机制层

- 触发：machine-readable approval + manifest + source hash + extractor version 全部一致。
- 禁止：隐私边界、source trace、schema 或 approval 任一缺失。
- 降级：按 pilot 锁定的 ASR/OCR/action/course/manual fallback，不得临时发明路线。

### 5.3 实现设计层

- primary：source registration → four lanes → serial timeline/relation/course/V0 merge → review queue → validation → controlled promotion。
- fallback：lane 级重试/人工标注/chunk-topic course/neutral_idle/quarantine。
- capability_status：只使用 approval 记录，不从历史文件推断。
- probe：full 不重新定义 probe；发现新输入分布时暂停 source，回 5.6。
- autonomy：可调度批准的并行度和 retry；不得改 schema/threshold/core route。

### 5.4 流程层

不同 source 和同 batch 四 lane 可并行；全局 merge、review merge、privacy scan、Git 串行。

### 5.5 判断标准层

技术/内容/动作/V0 分层验收；技术完成不得外推为人工或业务通过。

### 5.6 反馈层

- schema/输入分布不适配：回 5.6。
- extractor failure：按批准 fallback。
- privacy/source/权限：blocked。
- 指标下降：暂停受影响 source，不放宽阈值。

## 6. Impact check 影响面检查

执行前记录：

1. `pwd`
2. `git rev-parse --show-toplevel`
3. `git branch --show-current`
4. `git remote -v`
5. `git status --short`
6. local/remote HEAD
7. approval 路径、hash 和内容
8. schema/manifest/extractor version
9. source allowlist/hash/metadata
10. 预计 source/batch 数、I/O、磁盘和运行预算
11. raw/repo 目录覆盖风险
12. 用户已有 dirty 文件重叠
13. PII/media/cache/secret 风险
14. 是否需要安装/外部 API

## 7. Must read 必读文件

1. `AGENTS.md` 及其指定机制文件。
2. 本目录 `00`–`09`。
3. `data/event_schema.json`。
4. full run manifest 实例（由 `data/full_batch_manifest_template.json` 生成）。
5. machine-readable pilot review approval。
6. pilot `validation_report.json`、`pilot_execution_report.md`、review decision。
7. `../01_直播录屏解析方案详细版_live_recording_analysis_plan.md`。
8. `../../../项目资料_docs/课程解析资料_course_analysis/README_课程解析资料入口_course_analysis_index.md`。
9. `../../../项目资料_docs/课程解析资料_course_analysis/05_直播项目桥接_live_project_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/live_project_bridge_fields.csv`。
10. `../../../项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/lesson_id_mapping.json`、`previous_transcript_index.json`、`source_inventory.json`。
11. approval 指定的 extractor 实现、配置和测试。

## 8. Inputs

- `data/full_batch_manifest_template.json` 的运行实例。
- 锁定的 `event_schema.json`。
- pilot approval。
- source inventory + SHA-256。
- 课程 lesson/chunk/source index。
- 已批准的 ASR/OCR/action/course extractor 版本。
- privacy/redaction policy。

## 9. Batch design

### 9.1 Batch 层级

```text
run
  source_session
    management_batch
      audio_lane
      comment_lane
      visual_lane
      course_candidate_lane
    serial_merge
    review_queue
```

### 9.2 管理窗口

- 默认 20 分钟。
- overlap 30 秒。
- 可按 GPU/CPU/内存调整，但最终事件仍按语义变化点。
- source video 之间可并行。
- 同一 source 相邻窗口的 merge 串行。

### 9.3 命名

- `run_id=LXR-FULL-{YYYYMMDDTHHMMSSZ}-{schema_version}`
- `session_id=LXR-{source_date}-{source_hash8}`
- `batch_id={session_id}-B{window_start_ms}-{window_end_ms}`
- `event_id` 按数据合同。

## 10. Output

工作层：

```text
local_only_reports/新录屏多模态全量_new_recording_multimodal_full/{run_id}/
  run_manifest.json
  raw_local/
  checkpoints/
  lanes/
  merged_redacted/
  review_queue/
  validation/
```

repo promotion 只能由 5.6/人工复核后执行，采用 allowlist。不得自动把 full raw/merged 全量提交 Git。

## 11. Lane contract

每个 lane 只写自己的 batch：

```json
{
  "run_id": "...",
  "session_id": "...",
  "batch_id": "...",
  "lane": "audio|comment|visual|course_candidate",
  "source_hash": "sha256:...",
  "window_start_ms": 0,
  "window_end_ms": 1200000,
  "input_fingerprint": "...",
  "extractor_name": "...",
  "extractor_version": "...",
  "status": "planned|running|checkpointed|completed|failed|blocked",
  "attempt": 1,
  "output_hash": null,
  "error_code": null
}
```

## 12. Concurrency

允许并行：

- 不同 source session。
- 同 batch 的四 lane。
- 不相邻的只读抽取 batch。

必须串行：

- source hash/session lock。
- 相邻 overlap stitch。
- comment/reply final relation。
- course final alignment。
- V0 rule generation。
- manual review merge。
- repo export/Git。

同一全局文件只允许 merger 写；worker 禁止 append 全局 CSV/JSONL。

## 13. Execution steps 执行步骤

### Phase 0: Preflight

- workspace/remote/dirty。
- approval/schema/manifest。
- source/hash/metadata。
- extractor version。
- disk/compute budget。
- privacy directories。

### Phase 1: Source registration

- 对所有 source 计算/验证 SHA-256。
- 建 session。
- 检查重复 source hash。
- source 相同只建一个 canonical session；别名写 manifest。

### Phase 2: Lane extraction

- 四 lane 独立。
- 每完成一个 batch 写 checkpoint/output hash。
- 单 lane 失败不覆盖其他 lane。

### Phase 3: Timeline merge

- 去 overlap duplicates。
- 事件分割。
- relation candidates。
- course candidates。
- action/prosody candidates。

### Phase 4: Review queue

自动进入人审：

- PII/risk。
- 低 ASR/OCR。
- uncertain relation。
- course source unavailable。
- action/prosody inference。
- V0 candidate。

### Phase 5: Validation

- schema/time/ID/ref。
- privacy/media/secret。
- resume/idempotency。
- source coverage。
- review coverage。

### Phase 6: Controlled promotion

- 只提升审核通过的 redacted summaries/rules/metrics。
- 原始 media/OCR/PII/cache 永不进 Git。
- path-limited stage。

## 14. Retry/recovery

| 错误 | 自动重试 | 处理 |
|---|---:|---|
| transient read | 2 | 同 batch/lane |
| extractor crash | 2 | 从 checkpoint |
| deterministic parse error | 0 | blocked + review |
| source corrupted | 0 | source blocked |
| privacy scan fail | 0 | quarantine |
| merge reference missing | 0 | 回 lane completeness |
| schema mismatch | 0 | 回 5.6 |
| Git/push fail | 按 Git 安全策略 | `blocked_push_failed` |

重试只允许覆盖相同 idempotency key 的未完成临时输出；approved 输出不可覆盖。

## 15. Quality sampling

每 source 至少：

- ASR：每 30 分钟抽 60 秒，至少 3 段/source。
- OCR：每 30 分钟抽 30 个评论事件；少于则全检。
- reply links：高置信关系至少抽 30 个/source。
- course alignment：高置信至少抽 20 个/source。
- actions：至少抽 30 个/source。
- V0 rules：100% 人审。

若 source 数量/事件不足，记录实际基数，不补造。

## 16. Full gate

每个 source 只有全部满足才可 `approved_for_redacted_promotion`：

- required/time/ID validation 100%。
- PII leak 0。
- unresolved critical error 0。
- resume/idempotency 通过。
- 抽样指标不低于 pilot 锁定阈值。
- V0 candidates 仍为 review queue；未自动投产。

## 17. Done when

全量执行完成仍只代表：

- 技术解析完成。
- 脱敏/验证完成。
- review queue 完整。

不代表：

- 用户人审全部通过。
- 数字人正式直播通过。
- 成交提升。
- 客户正式验收。

如产生 repo 文件改动，必须 commit/push/remote HEAD readback；否则只能 `local_only_not_completed`。

## 18. Blocked if 阻断条件

- `blocked_wrong_workspace`
- `blocked_existing_wrong_remote`
- pilot approval 不是 `approved`。
- schema/manifest/extractor major/version 不匹配。
- source path/hash/metadata 变化。
- raw/repo 隔离或 quarantine 不可用。
- ASR/OCR/action/course route 未在 approval 锁定。
- exact course alignment 被要求但 full source 不可访问。
- 指标低于 pilot 阈值且需要临时放宽标准。
- 新 source 分布超出 pilot，需重新 probe。
- 需要安装依赖或调用未授权/付费 API。
- dirty worktree 与输出/提交路径重叠。
- 继续执行会把 PII、媒体、缓存或 secret 写入 repo。
- push 失败：`blocked_push_failed`。
- remote HEAD 未验证：`local_only_not_completed`。

## 19. Output 回报格式

每次回报：

- commands。
- result。
- failed_items。
- files_changed。
- validation。
- run/source/batch 数。
- completed/failed/blocked lanes。
- resume/retry。
- ASR/OCR/link/course/action metrics。
- privacy/media/secret。
- review queue。
- promoted file allowlist。
- Git evidence。
- blocked reason。
- 不能证明的内容。
