# 执行合同与验收

## 文件定位

本文件记录当前项目执行合同和验收入口。当前仅建立入口，不写未验证业务结论。

## 已确认

- Codex（本地执行、验证、落库层）执行涉及文件改动时，必须完成 commit（提交）、push（推送）、remote HEAD（远端最新提交指针）验证后，才可写 `completed`。
- GitHub `main`（当前项目事实源）承载项目事实。
- GPT Project（当前项目配合机制层）只承载机制。

## 待补全

- 当前阶段执行合同。
- 当前阶段 Done when（完成标准）。
- 当前阶段 Blocked if（阻断条件）。
- 业务验收标准。
- 用户人审标准。
- API / 工具 / 账号权限验证标准。

## 失败标记

- push 失败：`blocked_push_failed`
- 本地完成但远端未验证：`local_only_not_completed`
- 只读任务无文件改动且完成：`no_file_change_completed_readonly`
- 缺关键条件无法继续：`blocked`
