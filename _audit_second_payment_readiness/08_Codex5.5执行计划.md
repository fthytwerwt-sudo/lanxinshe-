# Codex 5.5 执行计划

## Goal｜目标

在不提前实现第三阶段能力的前提下，把当前素材、知识、规则和模型底座收敛为一个可重复、可审计、可现场演示的 V0，并形成第二阶段正式验收包。

## Context｜上下文

- 当前判定：`ready_for_second_payment=NO`。
- GitHub `main` 不是可复现的 V0；本地候选代码被 exclude。
- 10 个真实录屏可作为评论回放来源，但评论文字与口播需人工复核。
- 课程资料是 `partial`，不能未经人审直接作为业务事实。
- Qwen/embedding/rerank 有最小连通证据，阿里 3D 动态播报未证实。
- 三类 30 秒样片和客户书面确认未形成统一证据包。

## Constraints｜边界

1. 先受控回放，暂不接真实直播平台评论 API。
2. 不用 ffmpeg/OpenCV/MediaPipe/MoviePy 修最终模型视频或伪装模型原生能力。
3. paid API 先 dry-run、成本上限和人工批准；secret 不入日志/Git。
4. 未经人审的课程内容只能 `needs_review`。
5. 高风险、未知、低置信或第三方失败必须 fail-closed 转人工。
6. 只 stage 明确文件；无明确授权不得处理当前用户脏工作树。
7. V0、客户 demo、书面验收、收款和第三阶段分别记录状态。

## Impact Check｜影响面检查

- Git：需先决定本地 ignored V0 代码是否应纳入事实源；不能静默 force-add。
- 数据：需要新建小型、人工复核的评论/知识/规则 fixtures，不搬运完整视频或 secret。
- 外部服务：Qwen、embedding/rerank、阿里 3D/TTS 调用需成本和配额闸门。
- 客户交付：三类样片与 V0 演示必须一一映射到验收项。
- 回滚：每项任务独立提交；适配器以 feature flag / mock 隔离。

## 公共前置、验证与 Git 闭环

每个未来实施任务先执行：

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git status --short
git fetch origin main
git rev-list --left-right --count HEAD...origin/main
```

只有 workspace/remote 正确且本地与远端不存在未处理分叉时继续。当前已存在的客户 PDF deletion、`contracts/`、`local_only_reports/` 和 `._*` 不得被混入任务。

每项任务结束时执行本任务测试、`git diff --check`，只用精确路径 stage，按 Lore protocol commit、push，并用 `gh api .../commits/main --jq .sha` 或等价只读方式验证 remote HEAD。若 remote HEAD 不等于 local HEAD，状态只能是 `blocked_push_failed`。回滚使用 `git revert <task_commit>`，不得 `reset --hard`。

各任务的精确命令、测试和文件字段见 `09_Codex5.5执行任务.json`。

## Execution Steps｜执行步骤

### `C55-P0-01` 建立可复核评论输入集

- 从录屏选择至少 10 条，人工逐字复核并记录时间戳、场景、期望分类/风险。
- 产出 JSONL + schema + redacted review sheet。
- 测试非法字段、重复 event_id、未复核内容拒绝进入验收集。

### `C55-P0-02` 建立最小知识库与规则包

- 只选已人工确认的课程/商品/售后事实。
- 建分类、回复、异议、促销、禁限表达、人工接管六类版本化规则。
- 每条回复记录 source_id；无来源或冲突时转人工。

### `C55-P0-03` 实现确定性编排与审计日志

- 事件状态：received → classified → retrieved/rule → generated → safety_checked → broadcasted 或 manual_takeover。
- 日志 append-only、脱敏，记录延迟、模型、规则版本和失败原因。
- 先用 fake provider 完成离线集成测试。

### `C55-P0-04` 接入 Qwen 动态回复

- 使用受约束 prompt/schema；禁止固定单回复冒充动态。
- 相同输入可重复、不同输入响应不同，且可追溯知识来源。
- API 失败/超时/结构错误一律转人工。

### `C55-P0-05` 建阿里 3D 表现层适配器

- 先确认官方 API/账号/配额/返回回执。
- 适配器必须支持 dry-run/fake 和真实 provider 两种模式。
- 若阿里 3D 能力或账号阻断，形成精确阻断报告，不用离线 Wan/VideoRetalk 假装实时 3D。

### `C55-P0-06` 三评论端到端演示与失败降级

- 连续回放知识咨询、促销/异议、高风险三类评论。
- 展示分类、引用、回复、转人工、播报/回执和日志。
- 故障时展示 manual takeover，不临时切换未审方案。

### `C55-P0-07` 收敛三类样片与验收包

- 明确讲解/回复/促销各一个约 30 秒最终文件，不重复指向同一模糊样片。
- 标记 model_native_output / local_fallback_used；本地 fallback 不计模型原生通过。
- 归档声音、视觉、知识/规则版本、V0 演示日志、已知限制和验收表。

### `C55-P0-08` 客户演示与书面确认

- 先内部彩排，后客户受控演示。
- 逐项勾选验收表；保留签字/盖章、授权邮件或明确聊天确认。
- 只有合同生效、阶段条件满足、书面确认可回读后，才把收款状态改为 YES。

## P1｜建议收款前完成

### `C55-P1-01` 客户友好型本地演示台与扩展回放

- Goal：把稳定的 CLI pipeline 显示为本地只读演示台，用 30–50 条脱敏评论做回归。
- Context：P0 能证明闭环，但客户需要直观看到评论、分类、来源、回复、风险、接管和播报回执。
- Constraints：不复制业务逻辑、不引入新依赖、不接真实平台；UI 漂亮不等于验收。
- Impact Check：只消费 P0 schema；新增 view/console 和回归测试。
- Files：读取 P0 pipeline/log schema/SOP；新增 `src/live_brain/demo_view.py`、`scripts/run_live_brain_v0_demo_console.py`、相关 tests。
- Commands：`PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/run_live_brain_v0_demo_console.py --offline`；运行 30–50 条 replay regression 和全量 unittest。
- Done When：非技术人员能看懂每条处理路径；UI 与底层日志一致；高风险显著标识。
- Blocked If：P0 pipeline/schema 不稳定。
- Rollback：revert 独立 commit；CLI 保持可用。

### `C55-P1-02` 同步项目事实并验证 clean clone

- Goal：让 GitHub `main` 成为可复现事实源，并清除旧 workspace/初始化任务陈述。
- Context：当前 README/事实入口过期，核心本地代码 ignored，clean clone 缺依赖。
- Constraints：只有 P0 证据通过后更新状态；客户未签字不得写业务验收完成；临时 clone 只能在授权 workspace 内。
- Impact Check：影响 README、项目事实入口、依赖清单、tests/CI；需保护现有用户脏工作树。
- Files：读取并按证据更新 `README.md` 与项目事实 00–04/最新摘要；新增 clean-clone 报告。
- Commands：精确 stage 本任务路径；在 `mktemp -d "/Volumes/WD_BLACK/澜心社直播/.tmp-clean-clone.XXXXXX"` 中 clone/install/test/smoke；验证 local/remote HEAD。
- Done When：新 clone 可无 secret 地运行 offline V0，测试全过，事实文档与实际状态一致。
- Blocked If：用户变更重叠、依赖缺失、测试失败或需把媒体/secret 入 Git。
- Rollback：`git revert` 独立 commit；安全清理已核验临时目录。

## P2｜进入后续阶段，不阻断第二次收款

### `C55-P2-01` 真实平台评论与 20–30 分钟试播

- Goal：在第三阶段用正式授权渠道接入实时评论并完成 20–30 分钟受控试播。
- Constraints：只用官方 API、授权后台或 webhook；不绕过平台，不把 Computer Use 作为核心链路；阶段二未验收/未付款前不实施。
- Impact Check：账号、隐私、平台规则、OBS/RTMP、断线重连、费用和人工值守。
- Files：待创建平台 adapter、stage3 runner、integration tests、试播日志与报告。
- Commands：先官方 sandbox/dry-run；书面授权后执行 stage3 trial；验证重连、去重、限流和人工接管。
- Done When：20–30 分钟连续可复盘，评论/回复/接管/播报日志完整。
- Blocked If：无官方授权、需绕过限制或阶段二状态未关闭。
- Rollback：撤销 token/adapter 部署并 revert 软件 commit；保留供应商审计记录。

### `C55-P2-02` 短视频切片 MVP

- Goal：把第三阶段试播素材进入独立切片 MVP。
- Constraints：运动/讲解与纯口播分路线；候选先人审；可解码不等于编辑通过；媒体不入 Git。
- Impact Check：媒体存储、来源时间码、人工审核、导出和复盘。
- Files：待创建 `src/live_clip/`、runner、tests、manifest 和复盘表。
- Commands：只读媒体探测、MVP dry-run、route/manifest tests。
- Done When：至少一组经人工确认、可追源、可复跑的短视频样片。
- Blocked If：阶段三录屏、路线标准或人工审核缺失。
- Rollback：revert 代码/manifest，不删除原媒体。

### `C55-P2-03` LangGraph/飞书工作流变更评估

- Goal：只在实际瓶颈出现后评估工作流编排和人工审核后台。
- Constraints：先 ADR 和成本/权限评估；新依赖、飞书权限和范围必须书面批准，未批准不安装/实施。
- Impact Check：依赖、权限、数据留存、幂等、重试、人工闸门和运维成本。
- Files：先新增 ADR、数据流、成本/范围表和验收标准；实现文件待验证。
- Commands：官方文档/依赖许可证只读核验，不执行安装。
- Done When：形成明确采用/拒绝决策及签署范围。
- Blocked If：无量化痛点、授权或变更预算。
- Rollback：设计阶段无运行影响；实现阶段独立 revert。

### `C55-P2-04` 4–5 小时 Beta 稳定性验收

- Goal：第四阶段完成长时直播、故障演练和交接培训。
- Constraints：保留人工中控；不能从短 demo/20 分钟试播外推稳定性。
- Impact Check：高账号、平台、费用、数据和业务风险。
- Files：待创建 stability runner、observability、runbook、长时报告和培训资料。
- Commands：预演和故障注入通过后，经书面授权执行 4–5 小时 Beta。
- Done When：不少于 4 小时连续证据、完整日志/录屏、客户可按 SOP 操作。
- Blocked If：阶段三未通过或账号、费用、值守人员未确认。
- Rollback：终止会话、恢复安全配置、revert 软件变更；不删外部审计记录。

## Done When｜完成标准

1. 至少 10 条人工复核评论，至少 3 类，包含一条高风险转人工。
2. 六类规则和最小知识库版本化且引用可回读。
3. 3 条不同评论连续运行两次，无事件丢失；输入、分类、知识、回复、风险、接管/播报均有日志。
4. 阿里 3D 真实 provider 有播报回执，或明确形成外部账号/能力阻断并由合同双方确认替代验收方式。
5. 三类 30 秒样片、声音、视觉、知识/规则、V0 日志和限制说明齐全。
6. 客户书面阶段确认可回读。

## Blocked If｜阻断条件

- 没有已生效合同/第二阶段验收口径。
- 评论或课程内容无法获得人工复核。
- 阿里 3D 官方 API/账号/配额不可用且没有书面替代方案。
- paid API 未批准或缺成本上限。
- 需要覆盖用户脏工作树、secret 或素材原件。
- 只能靠本地后处理伪装模型输出。

## Output｜回报格式

每个任务回报：`task_id`、`status`、`commands`、`result`、`failed_items`、`files_changed`、`tests`、`evidence_paths`、`commit`、`push`、`remote_head`、`blocked_reason`、`human_review_status`、`customer_acceptance_status`。

## 推荐顺序

收款前主链：`C55-P0-01 → C55-P0-02 → C55-P0-03 → C55-P0-04 → C55-P0-05 → C55-P0-06 → C55-P0-07 → C55-P0-08`。

P1 可在 P0-06 后并行准备，但不得掩盖 P0 失败。P2 只有阶段二关闭后再下发。
