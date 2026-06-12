# GitHub 事实源读取机制

## 文件定位

本文件规定 GPT 和 Codex 如何把 GitHub `main` 作为当前项目事实源读取。

本文件只承载读取机制，不承载项目事实。

## 触发条件

- 用户要求判断当前项目状态。
- GPT 准备给出执行建议或下发 Codex。
- Codex 准备修改仓库文件。
- GPT Project 机制包、历史记忆、外部资料和仓库事实可能冲突。

## 默认动作

1. 先确认仓库、branch（分支）、remote（Git 远端仓库地址）。
2. 先读取 GitHub `main` 当前文件，再引用项目事实。
3. 如果是 Codex 本地执行，先 `git status`，再按远端状态执行 `git pull --ff-only` 或记录远端 `main` 待创建。
4. 如果引用执行结果，必须说明证据来源：文件、命令输出、commit、push、remote readback（远端回读）。
5. 如果事实不在 GitHub `main`，只能标 `待验证` 或 `推测`，不能写成当前项目事实。

## 默认读取顺序机制

当 GPT / Codex 接手当前仓库任务时，默认按这个顺序建立上下文：

1. 当前用户输入，也就是本轮 `P0`。
2. 当前仓库 `AGENTS.md`，如果存在。
3. GPT Project 机制包中的协作协议、事实源边界、P0/P1/P2、真实意图闸门、六层闸门。
4. 当前仓库的项目事实文件。
5. 当前仓库的执行报告、验证记录、风险记录、决策记录。
6. 本轮 Codex 执行输出和 Git 证据。

如果机制与事实冲突：

- 机制问题回 GPT Project 机制包判断。
- 项目事实问题回 GitHub `main` 当前文件判断。
- 本轮用户输入覆盖前两者。
- 旧项目 `AGENTS.md` 只能作为机制参考，不进入当前事实层。

## Codex 读取事实时必须检查

- `pwd`。
- `git rev-parse --show-toplevel`。
- `git branch --show-current`。
- `git remote -v`。
- 当前分支。
- 当前 remote。
- 工作树是否干净。
- 目标路径是否存在。
- 是否有同名目录或覆盖风险。
- 是否有未提交改动。
- 是否涉及 secret、媒体、缓存、运行产物。

## 不应进入 GPT Project 的事实

- 项目状态。
- 执行报告。
- 阶段结果。
- 验收标准。
- 客户需求。
- API 状态。
- 代码。
- 测试结果。
- 风险记录。
- 决策记录。

这些内容应该留在 GitHub 项目事实区。

## 一句话执行口径

GPT Project 告诉 GPT 怎么读事实；真正事实必须回到 GitHub `main` 当前文件和验证证据。
