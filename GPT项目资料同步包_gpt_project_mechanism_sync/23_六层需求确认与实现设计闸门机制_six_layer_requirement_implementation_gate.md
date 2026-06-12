# 六层需求确认与实现设计闸门机制

## 文件定位

本文件规定复杂任务、方向不清、机制冲突、反馈失败或 GPT 准备下发 Codex 执行单前，如何先确认六层需求，再决定是否执行。

本文件只承载六层闸门机制，不承载项目事实。

## 触发条件

- 用户需求不清，继续执行会让 Codex 猜。
- 用户反馈“不对 / 怪怪的 / 差点意思 / 没按之前的来”。
- 任务涉及直播、自动化、脚本、工具路线、机制修改、资料桥接、候选产物或 Codex 执行。
- GPT 准备下发 Codex，但目标、机制、实现设计、流程、判断标准、反馈层任一项不清楚。
- Codex 执行单缺少 primary_route、fallback、能力边界、probe 要求或 blocked 条件。

## 六层定义

### 1. 目标层

回答：

- 本轮真正要达成什么。
- 是项目总目标、阶段目标，还是本轮最小目标。
- 本轮不解决什么。
- 是否和用户本轮输入冲突。

### 2. 机制层

回答：

- 什么条件触发。
- 什么条件禁止。
- 什么条件降级。
- 哪些能力仍是 `待验证`。
- 哪些前提不成立必须 blocked。

### 3. 实现设计层

回答：

- primary_route。
- fallback_route。
- capability_status。
- probe_required。
- allowed_codex_autonomy。
- forbidden_codex_guessing。
- required_inputs。
- required_outputs。
- execution_entrypoints。
- validation_commands。
- blocked_if_missing。

缺实现设计层时，必须输出：

```text
blocked_need_implementation_design_layer
```

不得用更长 prompt 代替实现设计层；不得把 Execution steps 当成 route / fallback / capability boundary。

### 4. 流程层

回答：

- 确认后按什么顺序执行。
- 是否需要多候选、最小测试、用户回审。
- 哪些交给 GPT 判断。
- 哪些交给 Codex 执行。
- 哪些需要用户确认。

Execution steps 只能承载执行步骤，不能替代实现设计。

### 5. 判断标准层

回答：

- 技术通过标准。
- 内容通过标准。
- 审美 / 人感通过标准。
- 失败标准。
- 哪些不能因为技术完成就写成整体通过。

### 6. 反馈层

回答：

- 方向错回目标层或机制层。
- 实现路线错回实现设计层。
- 执行粗糙回流程层。
- 审美不清补 reference 或用户判断。
- 权限、账号、API、余额、依赖失败进入 blocked。
- 能力未 probe，不得写 `已确认`。

## 逻辑串联检查

GPT 必须检查：

1. 目标层和机制层是否一致。
2. 机制层和实现设计层是否一致。
3. 实现设计层是否能支撑流程层。
4. 流程层是否能产出判断标准层要验收的结果。
5. 判断标准层是否覆盖技术、内容、审美、人感和风险。
6. 反馈层是否能把失败送回正确位置。

## 停止线

- 缺实现设计层，不下发 Codex。
- 缺 primary_route / fallback / capability boundary / probe decision，不下发 Codex。
- 不能用更长 prompt 代替实现设计。
- 不能让 Codex 边执行边决定核心路线。
- Codex 收到缺实现设计层的执行单时，必须 `blocked_need_implementation_design_layer`，不得自行补核心路线。

## 一句话执行口径

复杂任务先过六层；实现设计层没锁，Codex 就不该开始执行。
