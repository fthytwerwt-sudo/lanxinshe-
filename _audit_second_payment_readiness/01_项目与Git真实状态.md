# 项目与 Git 真实状态

## 审计结论

仓库身份和远端 HEAD `已确认`，但 GitHub `main` 不是可独立复现的 V0 直播大脑；本地候选代码被 `.git/info/exclude` 隐藏且启动脚本明确是 placeholder。Git 同步成功不构成第二阶段收款证据。

## 基础状态

| 项目 | 结果 | 状态 |
|---|---|---|
| workspace / Git root | `/Volumes/WD_BLACK/澜心社直播` | 已确认 |
| branch | `main`，相对 `origin/main` ahead/behind=`0/0` | 已确认 |
| origin | `https://github.com/fthytwerwt-sudo/lanxinshe-.git` | 已确认 |
| local HEAD | `8b6d55abae1fcac72e83ba0c42840f6d5ae4d959` | 已确认 |
| remote `main` | 同上；`gh api` 回读成功 | 已确认 |
| `git ls-remote` | 本轮曾出现 `Recv failure: Connection reset by peer`；由 GitHub API 只读回读补证 | 部分成立 |
| nested Git repo | 仅根目录一个 `.git` | 已确认 |
| 近似项目目录 | 仅 `/Volumes/WD_BLACK/澜心社直播/最新直播`，是 10 个 MP4 的素材目录 | 已确认 |
| 真实运行版本 | 未找到生产服务、部署清单或完整入口 | 待验证 |

## 工作树事实

- tracked deletion：`客户交付文档/客户沟通版_数字人直播系统交付边界费用验收说明_client_scope_fee_acceptance.pdf` 本地缺失；HEAD 中存在。
- untracked/local-only：`contracts/`、`local_only_reports/`、`codex_reports/合作协议重写报告_contract_rewrite_report_20260617.md` 等。
- AppleDouble：workspace 存在大量 `._*` 元数据文件，均不应作为素材或项目事实；本审计清单排除这些文件并记录排除数量。
- 本轮新增：仅 `_audit_second_payment_readiness/`。

## GitHub `main` 与本地候选的边界

### GitHub `main`

- tracked Python 代码主要是 `config/alibaba_model_registry.py` 与模型/视频连接探针脚本。
- 缺 `requirements.txt` / `pyproject.toml`、tracked tests、CI、生产入口和完整依赖链。
- `scripts/probe_alibaba_videoretalk_connection.py` 导入未 tracked 的 `config.env_config`，clean clone 会断依赖。
- 机制包和课程/样片事实资料已 tracked，但资料存在不等于直播大脑实现完成。

### 本地 ignored 候选

- `config/env_config.py`
- `config/qwen_config.py`
- `src/live_brain/qwen_client.py`
- `scripts/check_qwen_chat_connection.py`
- `scripts/run_live_demo.py`
- `tests/*.py`
- `requirements.txt`

这些文件被 `.git/info/exclude` 隐藏。`scripts/run_live_demo.py` 明确写明 `placeholder`、`Real live streaming is not implemented`，没有 stream push、OBS control 或 digital human logic。

## 项目事实入口风险

根目录 `AGENTS.md` 已把当前 workspace 定为 `/Volumes/WD_BLACK/澜心社直播`，但项目事实入口中的 `00_项目总说明_project_brief.md`、`02_当前任务_current_task.md` 和 `执行日志_codex_log/最新摘要_latest.md` 仍保留旧路径 `/Users/fan/Documents/澜心社直播`。因此核心事实入口与当前仓库状态存在滞后。

## 风险判定

1. `已确认`：仓库与 remote 正确。
2. `已确认`：GitHub `main` 不能 clean-clone 复现 V0。
3. `已确认`：本地脚本是模型调用底座/占位框架，不是真实直播运行版本。
4. `待验证`：合同本地文件是否为已签署、已生效版本。
5. `blocked`：在恢复缺失 PDF、清理工作树或补 tracked 代码前，不得擅自归因和修改用户原有脏工作树；这些不属于本轮只读任务。
