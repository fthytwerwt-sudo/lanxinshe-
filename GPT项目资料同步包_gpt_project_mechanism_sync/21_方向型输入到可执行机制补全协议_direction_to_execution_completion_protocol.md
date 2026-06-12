# 方向型输入到可执行机制补全协议

## 文件定位

本文件规定如何把“想要某种感觉 / 能不能做 / 参考这个 / 让 Codex 做一下”这类方向型输入补成可执行合同。

本文件只承载方向转执行机制，不承载项目事实。

## 触发条件

- 用户只描述方向，没有执行字段。
- 用户同时在问方向判断和执行。
- GPT 给出方案，但缺入口、输出、验证。
- 能力还没 probe，却准备进入完整任务。
- 用户反馈“不对 / 怪怪的 / 差点意思”。

## 默认动作

先把方向补成可执行合同：

1. 真实意图。
2. 任务类型。
3. 六层需求确认。
4. Implementation design（实现设计）。
5. 输入字段。
6. 输出字段。
7. 执行入口。
8. 验证方式。
9. Done when。
10. Blocked if。

## 任务类型示例

- `mechanism_sync`
- `read_only_audit`
- `documentation_export`
- `component_probe`
- `technical_sample`
- `toolchain_completion`
- `review_pack`
- `route_replanning`

这些只是任务类型，不代表能力已验证。

## Codex 下发前必须确认

- 本轮真正要判断什么。
- 本轮不判断什么。
- primary_route。
- fallback_route。
- capability_status。
- probe_required。
- allowed_codex_autonomy。
- forbidden_codex_guessing。
- validation_commands。
- blocked_if_missing。

## 停止线

- 缺关键输入字段，不编造。
- 缺实现设计层，返回 `blocked_need_implementation_design_layer`。
- 未验证能力标 `待验证`。
- 禁止 API / render / 安装依赖时，只停在机制或合同层。
- 外部资料未保真，不进入执行。

## 一句话执行口径

方向型输入不能直接变成 Codex prompt；先合同化，再执行。
