# 输出硬规则与中文语义对齐

## 文件定位

本文件规定当前项目中 GPT / Codex 对用户输出、执行单、报告、日志、状态词和完成度边界的表达规则。

本文件只承载输出机制，不承载项目事实。

## 默认语言

- 默认中文沟通。
- 命令、代码、路径、字段名、配置键、环境变量、报错原文、English 原词保留 English 原词。
- 先给主结论，再给必要说明。
- 少废话，不用空泛企业话术。

## 状态词硬规则

未确认事项必须显式标：

- `已确认`：有当前证据。
- `部分成立`：局部链路成立，但不能外推。
- `待验证`：尚无证据。
- `推测`：基于经验、参考或外部资料。
- `通用建议`：可参考，不是当前承诺。
- `待创建`：应该创建但尚未创建。
- `待补全`：已有入口但字段、内容或验证仍不完整。
- `blocked`：缺关键条件，不能继续。
- `blocked_push_failed`：push（推送）失败。
- `local_only_not_completed`：本地完成但未完成远端验证。
- `no_file_change_completed_readonly`：只读任务无文件改动且已完成。

禁止用“完成了 / 稳定了 / 已解决 / 已经好了”替代上述状态词，尤其不能用模糊中文夸大实际状态。

## 完成度必须分开

- local_file_exists。
- validation_passed。
- committed。
- pushed。
- remote_head_verified。
- user_review_passed。
- business_goal_passed。

## 禁止表达

- 把 local-only 写成 completed。
- 把技术通过写成内容通过。
- 把用户未人审写成审美通过。
- 把 probe 写成稳定能力成立。
- 把外部资料写成当前项目事实。

## 文件命名硬规则

Codex 在当前项目中创建的自定义文件和目录，默认必须使用“中文 + English slug”命名。

推荐格式：

```text
中文说明_english_slug.ext
```

要求：

1. 中文部分说明给用户看的文件用途。
2. English slug 用小写 snake_case，方便脚本、搜索和跨工具识别。
3. 中英文之间使用下划线 `_` 分隔。
4. 不知道如何命名时，先问或标 `待确认`，不得随便创建纯英文文件名。

例外：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `package.json`
- `Dockerfile`
- 其他第三方工具强制要求的固定文件名

## Codex 回报必须包含

- commands。
- result。
- failed_items。
- files_changed。
- validation。
- commit / push / remote status。
- blocked reason。

## 一句话执行口径

中文说清楚，English 原词保关键；状态必须诚实，本地、远端、技术、人审、业务不能混写。
