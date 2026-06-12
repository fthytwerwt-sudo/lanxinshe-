# Codex 执行桥接包

## 文件定位

本文件是 GPT 下发 Codex 执行任务时的项目事实桥接入口。

## 已确认

- Codex 执行前必须确认 `pwd`、`git rev-parse --show-toplevel`、`git branch --show-current`、`git remote -v`、`git status`。
- Codex 必须按 path-limited stage（按路径限制暂存）提交本轮允许文件，禁止 `git add .`。
- Codex 不得提交 `.env`、secret、token、素材、媒体、缓存、运行产物。

## 待补全

- 当前阶段 Codex 允许修改范围。
- 当前阶段 Codex 禁止修改范围。
- 当前阶段 Must read（必读文件）。
- 当前阶段 validation_commands（验证命令）。
- 当前阶段 report target（报告落点）。

## 执行单最小字段

- Goal 目标。
- Context 上下文。
- Constraints 边界。
- 六层需求确认。
- Impact check 影响面检查。
- Must read 必读文件。
- Execution steps 执行步骤。
- Done when 完成标准。
- Blocked if 阻断条件。
- Output 回报格式。
