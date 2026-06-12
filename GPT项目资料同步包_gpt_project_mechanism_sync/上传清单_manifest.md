# GPT Project 配合机制上传清单

`已确认`：本清单内文件只允许承载配合机制，不允许承载项目事实。

| 文件名 | 文件作用 | 推荐上传 GPT Project | 是否包含项目事实 | 读取优先级 |
|---|---|---|---|---|
| `00_GPT_Project上传说明_readme.md` | 说明本包用途、事实源边界、旧项目迁移边界 | 是 | 否 | P0 |
| `上传清单_manifest.md` | 列出文件用途、是否可上传、读取优先级 | 是 | 否 | P0 |
| `00_协作协议_collaboration_protocol.md` | 定义 GPT / Codex / Web / Obsidian 分工 | 是 | 否 | P0 |
| `01_三层架构与事实源边界_three_layer_source_boundary.md` | 定义账号记忆、GPT Project、GitHub main、Codex 的职责边界 | 是 | 否 | P0 |
| `02_P0-P1-P2锚点与抗漂移机制_anchor_priority_anti_drift.md` | 定义 P0/P1/P2 优先级和抗漂移规则 | 是 | 否 | P0 |
| `03_GitHub事实源读取机制_github_fact_source_protocol.md` | 规定 GPT 如何从 GitHub 读取项目事实 | 是 | 否 | P1 |
| `04_Codex执行落库机制_codex_execution_to_repo_protocol.md` | 规定 Codex 如何执行、验证、commit、push、回报 | 是 | 否 | P1 |
| `05_外部资料桥接与保真提取机制_external_material_bridge_protocol.md` | 规定外部资料如何保真提取和桥接执行 | 是 | 否 | P1 |
| `06_路线重判与失败后改线机制_goal_revision_replanning.md` | 规定失败后如何分层归因、改线、blocked | 是 | 否 | P1 |
| `07_输出硬规则与中文语义对齐_output_hard_rules.md` | 规定中文输出、状态词、完成度边界 | 是 | 否 | P1 |
| `08_Codex工作区与远端仓库硬边界_codex_workspace_remote_boundary.md` | 规定 Codex 本地工作区和远端仓库硬边界 | 是 | 否 | P0 |
| `20_GPT与Codex自动补全及质量保障机制_gpt_codex_completion_quality_guard.md` | 规定 GPT / Codex 补全字段和质量检查 | 是 | 否 | P1 |
| `21_方向型输入到可执行机制补全协议_direction_to_execution_completion_protocol.md` | 把方向型输入转为可执行合同 | 是 | 否 | P1 |
| `22_真实意图澄清闸门机制_true_intent_clarification_gate.md` | 规定下发 Codex 前的真实意图澄清 | 是 | 否 | P0 |
| `23_六层需求确认与实现设计闸门机制_six_layer_requirement_implementation_gate.md` | 定义目标层、机制层、实现设计层、流程层、判断标准层、反馈层 | 是 | 否 | P0 |
| `24_Codex长期执行单模板_codex_task_template.md` | 提供长期复用的 Codex 下发模板 | 是 | 否 | P1 |
| `25_AGENTS机制迁移说明_agents_mechanism_migration_note.md` | 说明只迁移配合习惯、不迁移旧项目事实的边界 | 是 | 否 | P1 |

## 不进入本包的内容

- 项目状态、阶段结果、客户需求、执行报告、测试结果、风险记录、决策记录。
- 旧项目业务身份、素材路径、模型选择、API 状态、验收结果、能力结论。
- 当前项目具体文件内容、运行产物、媒体文件、缓存、secret。

## 读取建议

GPT Project 应先读 `00`、`01`、`02`、`08`、`22`、`23`，再根据任务类型读取 `03` 到 `07` 和 `20` 到 `25`。
