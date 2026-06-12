# Codex 执行落库机制

## 文件定位

本文件规定 Codex 如何在当前项目中执行任务、生成证据、写入仓库并完成 Git 闭环。

本文件只承载执行机制，不承载项目事实。

## Codex 角色

Codex 是本地执行器，负责：

- 读取文件。
- 检查现状。
- 执行任务。
- 生成报告。
- 写入仓库。
- 运行验证。
- commit（提交）/ push（推送）。
- 回报结果。

Codex 不负责在缺实现设计时自行决定核心路线。

## 执行前必须检查

- `pwd`。
- `git rev-parse --show-toplevel`。
- `git branch --show-current`。
- `git remote -v`。
- workspace（当前工作目录 / 工作区）。
- branch（分支）。
- remote（Git 远端仓库地址）。
- dirty status（未提交状态）。
- allowed files（允许文件）。
- forbidden files（禁止文件）。
- 是否存在覆盖风险。
- 是否涉及 secret、媒体、缓存、运行产物。
- 是否缺真实意图或实现设计层。

如果当前路径不是用户授权 workspace，必须停止并标：

```text
blocked_wrong_workspace
```

如果 remote 不指向用户本轮指定的 GitHub 仓库，必须停止并标：

```text
blocked_existing_wrong_remote
```

## 每次下发必须写清

- Goal 目标。
- Context 上下文。
- Constraints 边界。
- Impact check 影响面检查。
- Execution steps 执行步骤。
- Done when 完成标准。
- Blocked if 阻断条件。
- Output 回报格式。

复杂任务还必须写清六层需求确认，尤其是实现设计层。

## 落库规则

- 配合机制写入 GPT Project 同步包或机制目录。
- 项目事实写入 GitHub 项目事实区。
- 执行报告、验证结果、风险记录、决策记录属于项目事实，不进入 GPT Project 机制包。
- 修改后必须 path-limited stage（按路径限制暂存）本轮相关文件。
- 禁止 `git add .`。
- 禁止提交 `.env`、secret、token、素材、媒体、缓存、运行产物。
- 禁止在授权 workspace 外创建工作区、clone 目录、报告、脚本或临时产物。

## Codex 强制 push 规则

凡产生仓库文件改动，`completed` 必须同时满足：

1. commit 已创建。
2. push 已成功。
3. remote HEAD（远端最新提交指针）已验证。
4. local HEAD（本地最新提交指针）等于 remote HEAD。

本地有文件但未 push，不得写 `completed`。

push 失败必须标记：

```text
blocked_push_failed
```

如果远端 HEAD 未验证，只能写 `local_only_not_completed` 或 `待验证`，不得写 completed。

## 完成度边界

必须分开汇报：

- local 文件存在。
- validation 通过。
- commit 完成。
- push 完成。
- remote HEAD 验证。
- 用户人审通过。
- 业务目标通过。

没有远端 readback，不写 remote completed。没有用户人审，不写审美或业务通过。

## blocked 条件

- 缺真实意图。
- 缺实现设计层。
- 缺目标路径。
- 目标路径存在覆盖风险。
- 权限、API、余额、账号、secret 不清。
- 当前路径不在授权 workspace 内。
- remote 不指向用户本轮指定仓库。
- 继续执行会扩大影响面。
- 无法区分机制和项目事实。

## 一句话执行口径

Codex 按已锁定设计执行、验证、落库、push、readback；缺关键条件就 blocked，不用脑补补齐核心路线。
