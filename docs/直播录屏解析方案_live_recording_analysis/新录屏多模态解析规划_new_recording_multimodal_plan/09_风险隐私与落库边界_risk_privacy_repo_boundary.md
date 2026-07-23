# 风险、隐私与落库边界

## 1. 核心边界

两层数据必须物理隔离：

```text
local_only_reports/.../raw_local/       # Git ignored，本地原始层
local_only_reports/.../redacted_review_pack/  # 本地脱敏待审
docs/.../approved_redacted/             # 只有5.6/人工批准后可选择性入库
```

当前规划只创建合同，不创建运行层数据。

## 2. raw_local

允许：

- 原始 OCR。
- username/user_id/avatar URL。
- 原始评论时间轨迹。
- 临时截图/关键帧。
- HMAC salt。
- 原始 ASR 中可能含的 PII。
- 运行缓存和详细日志。

要求：

- workspace 内。
- Git ignored。
- 最小权限。
- 按 run/session 隔离。
- 不进入文档示例。

## 3. redacted_repo

只允许：

- `comment_event_id` 匿名 ID。
- `comment_text_redacted`。
- comment intent/risk。
- reply relation/confidence。
- source video 相对路径 + source hash。
- event time/evidence ref。
- course source ref。
- observed/inferred/review 状态。
- 已批准的 V0 候选规则。

禁止：

- 原始 username/user_id。
- 手机号、微信号、邮箱、身份证、地址。
- 头像/截图。
- 签名 URL、token、cookie。
- 原始音视频。
- `.env`。
- 缓存/模型文件。

## 4. 匿名 ID

优先：

`comment_event_id={session_id}-C{sequence}`

需要同 session 内聚合同一用户时：

`anonymous_user_id=HMAC-SHA256(session_salt, normalized_platform_user_id)`

规则：

- salt 只在 raw_local。
- 不允许无 salt 的普通 SHA-256 直接 hash username。
- 不跨 session 追踪用户，除非另有明确授权和合法目的。

## 5. 脱敏规则

至少检测：

- 中国手机号及带空格/连字符变体。
- 微信/社交账号提示词。
- 邮箱。
- 身份证/银行卡候选。
- 地址/精确位置。
- URL/query token。
- 订单/支付/账号编号。

替换：

- `[REDACTED_PHONE]`
- `[REDACTED_SOCIAL_ID]`
- `[REDACTED_EMAIL]`
- `[REDACTED_ACCOUNT]`
- `[REDACTED_ADDRESS]`
- `[REDACTED_URL]`

无法可靠脱敏：

- `comment_text_redacted=null`
- `comment_risk=pii`
- `review_status=blocked`

## 6. 证据引用

repo 中：

- 使用 source hash + time range。
- 不写绝对 Windows/用户目录，除非它是原始不可达 `course_source_ref`，且明确 `source_unavailable`。
- 不复制原始 comment。
- 不写截图路径。

## 7. 风险登记

| risk_id | 风险 | 等级 | 处理 |
|---|---|---|---|
| R001 | 评论 PII 入 Git | blocked | fail-closed + quarantine |
| R002 | 时间邻近误判因果 | high | candidate edge + human review |
| R003 | 课程摘要冒充原文 | high | exact alignment blocked |
| R004 | 动作/情绪过度推测 | high | observed/inferred split |
| R005 | ASR clean 改写原话 | high | raw/clean dual columns |
| R006 | 低置信规则进 V0 | high | approved-only |
| R007 | 媒体/截图误提交 | blocked | extension/MIME/size allowlist |
| R008 | secret/signature URL | blocked | secret scan |
| R009 | 多 worker 覆盖 | high | lane isolation + single merger |
| R010 | dirty worktree 混入提交 | high | exact path stage |
| R011 | V0 外推正式直播 | high | status boundary |
| R012 | 主观标签外推成交 | high | weak label only |

## 8. Repo allowlist

规划阶段仅允许本目录 13 个文件。

pilot/full 后可考虑：

- 脱敏 schema/manifest。
- 聚合指标。
- 不含原文的 review decision。
- 已批准规则候选。
- 执行/验证报告。

任何事件级数据入库前都需 5.6/人工 privacy review。

## 9. Pre-stage scan

必须：

1. 列出 candidate files。
2. 拒绝扩展名：视频、音频、图片、压缩包、模型、数据库、缓存。
3. 拒绝 AppleDouble `._*`。
4. 搜索 `.env/token/secret/cookie/signed URL`。
5. PII pattern scan。
6. 人工抽查所有新增样例。
7. `git diff --check`。
8. `git diff --cached --name-only` 与 allowlist 精确相等。

## 10. Git 纪律

- `docs/` 当前受 local exclude 影响，明确文件需 `git add -f <file...>`。
- 禁止 `git add .`。
- 不 stage 用户已有 PDF 删除、contracts/local reports、AppleDouble 或其他 untracked。
- commit 使用 Lore protocol。
- push 只到 `origin` 当前仓库。
- remote HEAD 回读且等于 local HEAD 才能写远端完成。

## 11. 删除/保留

- 临时抽帧完成判断后删除；本轮 probe 已执行此规则。
- raw_local 的保留期由用户/项目另行确定，本规划不擅自删除真实运行数据。
- 被 quarantine 的 PII 不可通过“改后缀”进入 repo。

## 12. 状态边界

- 规划 Git 闭环：只证明规划包落库。
- pilot local：`local_only_not_completed`，待 5.6 复审。
- pilot approved：只允许 full。
- full 技术完成：不等于人工复核完成。
- V0 受控 demo：不等于正式平台直播。
- 技术/内容/人感：不等于业务成交结果。
