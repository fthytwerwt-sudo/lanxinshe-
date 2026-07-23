# Codex 5.5 新直播录屏多模态解析小样试跑执行单

> 本执行单只允许三个 180 秒窗口的小样。禁止全量解析。

## Goal 目标

任务类型：`multimodal_pilot_execution`

真实目标：

- 按 `event_schema.json` 解析三个代表性窗口。
- 验证 ASR/OCR/动作/课程候选、时间轴、隐私、断点恢复和人工复核合同是否成立。
- 生成供 Codex 5.6 sol 复审的本地脱敏 review pack。

本轮不是：

- 不是全量转写/OCR/动作提取。
- 不是正式直播话术生成。
- 不是数字人训练或视频修改。
- 不是成交/业务效果判断。
- 不是全量任务授权。

## Context 上下文

- workspace：`/Volumes/WD_BLACK/澜心社直播`
- branch：`main`
- remote：`https://github.com/fthytwerwt-sudo/lanxinshe-.git`
- P0：只做 pilot；完成后由 Codex 5.6 sol 复审。
- P1：本规划目录、既有直播录屏方案和课程资料。
- P2：历史经验只作参考。
- 冲突：`P0 > P1 > P2`。

当前能力边界：

- `ffprobe/ffmpeg/cv2/Pillow` 已确认。
- 本地 ASR/OCR 引擎未确认。
- 完整课程逐字稿不可从当前 workspace 回查。
- 课程动作/语气资料不能直接当真人直播事实。

## Constraints 边界

允许：

- 只读三个 source video 的指定窗口。
- 计算三个 source 的 SHA-256。
- 在 `local_only_reports/` 下创建 raw_local、checkpoint 和 redacted review pack。
- 使用本轮已授权、可复现、不收费且无需安装新依赖的 ASR/OCR 能力。
- 无自动引擎时使用人工标注 fallback。

禁止：

- 修改、移动、重命名、转码或修复源视频。
- 安装依赖或调用付费 API。
- 扩大到三个窗口之外。
- 把原始截图、音频、OCR、username/user_id/PII 提交 Git。
- 把时间接近当评论因果。
- 把课程摘要当逐句原文。
- 把推测动作/语气写成 observed。
- 使用 `git add .`。
- 自动启动 full execution。

任何 `ffmpeg` 使用只允许：

`audit_or_input_preparation_not_fallback`

不得用本地后处理伪装模型能力。

## 六层需求确认

### 1. 目标层

输出三窗口事件数据和复审证据，判断 schema/route/gate 是否足够。

### 2. 机制层

开始条件：

- workspace/remote 正确。
- manifest 可解析。
- source 可读且 hash 成功。
- raw_local 与 repo 隔离。
- ASR/OCR 路线已确认；否则明确使用人工 fallback。

禁止条件：

- 无法隔离 PII。
- 需要安装/付费 API。
- 目标窗口与实际内容槽位不匹配且找不到替换窗口。

### 3. 实现设计层

primary：

`preflight → source hash → 30秒内容分类 → ASR/OCR/visual/course candidate lanes → timeline merge → relation inference → manual review sample → validation → redacted review pack`

fallback：

- ASR → 人工转写。
- OCR → 关键评论窗口人工标注。
- action → 只记 observed，数字人 `neutral_idle`。
- course → chunk/topic only。
- causality → `uncertain/topic_only/unanswered`。

### 4. 流程层

四 lanes 可并行；统一时间轴、因果、最终课程对应和 review merge 串行。

### 5. 判断标准层

见 `08_验收人工复核与失败回退_acceptance_review_fallback.md`。技术结果不得外推为业务通过。

### 6. 反馈层

- 槽位不符：替换窗口，不改标签硬套。
- schema 缺字段：停止 merge，回 Codex 5.6。
- 隐私失败：停止 repo export。
- ASR/OCR 无授权路线：切人工或 blocked。

## Impact check

执行前记录：

1. `pwd`
2. `git rev-parse --show-toplevel`
3. `git branch --show-current`
4. `git remote -v`
5. `git status --short`
6. `git rev-parse HEAD`
7. source 文件是否都在 `最新直播/`
8. source 是否与 manifest 一致
9. raw/repo 目录是否存在覆盖风险
10. ASR/OCR engine/version/license/成本
11. 是否会生成 PII/媒体/缓存
12. 是否会碰到用户已有 dirty 文件

## Must read

1. `AGENTS.md`
2. 本目录 `00`–`09`
3. `data/event_schema.json`
4. `data/pilot_task_manifest.json`
5. `../01_直播录屏解析方案详细版_live_recording_analysis_plan.md`
6. `../../../项目资料_docs/课程解析资料_course_analysis/README_课程解析资料入口_course_analysis_index.md`
7. `../../../项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/17_神经数字人课程解析总包_neural_avatar_course_analysis_master.md`
8. `../../../项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/16_质量检查报告_quality_review_report.md`
9. `../../../项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/10_三线对照阅读版_transcript_courseware_action_alignment_readable.md`
10. `../../../项目资料_docs/课程解析资料_course_analysis/05_直播项目桥接_live_project_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/live_project_bridge_fields.csv`
11. `../../../项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/lesson_id_mapping.json`
12. `../../../项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/previous_transcript_index.json`
13. `../../../项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/source_inventory.json`
14. `../../../项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/12_数字人动作触发规则_avatar_action_trigger_rules.csv`
15. `../../../scripts/validate_videoretalk_inputs.py`、`../../../scripts/prepare_videoretalk_probe_assets.py` 及实际选定 ASR/OCR/视觉/检索实现与测试。若实际实现不存在，必须走 manifest 指定的 manual fallback，不得把其他 bridge CSV/source inventory 混作 canonical 输入。

## Execution steps

### A. Preflight

1. 执行 Impact check。
2. 解析 manifest/schema。
3. 确认目标：
   - `pilot-course-001`
   - `pilot-comment-001`
   - `pilot-promo-001`
4. 对三个 source 计算 SHA-256，回填本地运行 manifest；不要修改规划 manifest。
5. `ffprobe` 校验 source metadata 和窗口边界。

### B. 30 秒槽位确认

每个窗口只检查前 30 秒：

- ASR 或人工听审：是否匹配目标内容。
- 抽帧人工检查：评论密度、商品/权益/道具/动作。
- 记录 `confirmed/replaced/blocked`。

若不匹配：

- 在同一 source 前后各最多搜索 10 分钟。
- 仍不匹配，从 10 个候选中替换。
- 替换必须记录 `selection_evidence`，不得猜。

### C. lane execution

每个 180 秒窗口：

1. `audio_lane`
   - raw transcript + timestamp。
   - clean transcript。
   - confidence、pause、rate、volume candidate。
2. `comment_lane`
   - 评论出现/消失轨迹。
   - raw 只写 raw_local。
   - redacted text、anonymous ID、intent/risk。
   - 跨帧去重。
3. `visual_lane`
   - observed action/expression/gaze/posture/prop。
   - 只描述可见证据。
4. `course_candidate_lane`
   - top 5 lesson/chunk/topic。
   - source ref。
   - 当前禁止 direct quote。

### D. Timeline merge

1. 统一相对毫秒时间。
2. 按变化点生成事件。
3. 创建 comment/reply candidate edges。
4. 生成课程候选。
5. 生成 action/avatar candidate。
6. 生成 brain rule candidate，但 `review_status=unreviewed`。

### E. Manual review

每窗口至少：

- 60 秒 ASR 金标准。
- 30 个评论事件，数量不足则全部。
- 30 个评论—回复关系，数量不足则全部。
- 20 个课程候选，数量不足则全部。
- 30 个动作事件，数量不足则全部。

### F. Interrupt/resume test

1. 在第二个窗口至少一个 lane 完成后主动中断。
2. 重启同一任务。
3. 证明已完成 lane 被跳过。
4. 检查 event/idempotency 无重复。

### G. Export

只写：

```text
local_only_reports/新录屏多模态解析小样_new_recording_multimodal_pilot/{run_id}/
  run_manifest.json
  raw_local/
  checkpoints/
  redacted_review_pack/
    events.jsonl
    comment_reply_links.jsonl
    course_alignments.jsonl
    brain_rule_candidates.jsonl
    review_queue.csv
    validation_report.json
    pilot_execution_report.md
```

`redacted_review_pack` 仍为本地待审，不得由 Codex 5.5 自动 stage/commit。

## Validation commands

按实际实现补齐，但最低包括：

```bash
jq empty run_manifest.json redacted_review_pack/validation_report.json
python_or_existing_validator event_schema.json redacted_review_pack/events.jsonl
git status --short
git diff --check
```

另验证：

- IDs/时间/source hash/source ref。
- PII/secret/media scan。
- checkpoint/resume。
- raw_local 不在 Git candidate list。

## Done when

Codex 5.5 pilot 只可标：

`local_only_not_completed`

并同时满足：

1. 三个窗口已完成或逐项明确 blocked。
2. review pack 可解析。
3. 所有不确定性标记。
4. raw/PII/media 未进入 Git。
5. 中断恢复已测试。
6. 已生成供 5.6 复审的报告。
7. 未启动 full。

只有 Codex 5.6 复审通过后，pilot 才能作为 full gate 证据。

## Blocked if

- `blocked_wrong_workspace`
- `blocked_existing_wrong_remote`
- source/hash/窗口不可读。
- ASR/OCR 无授权路线且无人工作为 fallback。
- 评论 PII 无法隔离。
- exact course quote 被要求但 source 不可达。
- schema 无法表达实际事件。
- 需要安装依赖/付费 API。
- 用户已有 dirty 文件与 local output 重叠。
- 任何 agent 试图扩展到全量。

## Output 回报

必须包含：

- commands
- result
- failed_items
- files_changed（只列 local_only）
- validation
- source hash
- 三槽位是否确认/替换
- metrics
- privacy/media/secret scan
- resume evidence
- 5.6 review queue
- git status（应无 repo 改动）
- blocked reason

最后一句必须是：

`下一步：交给 Codex 5.6 sol 复审；不得启动全量。`
