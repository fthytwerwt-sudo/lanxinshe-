# 新直播录屏多模态解析规划执行报告

## 1. 主结论

- 本轮状态：规划文件生成与本地验证为 `已确认`；在 commit/push/remote HEAD 完成前保持 `local_only_not_completed`。本报告不提前把本地状态写成远端完成。
- 规划是否完成：以本目录 13 个文件通过验证并完成 Git 闭环为准。
- probe 是否完成：`部分成立`。已完成 10 个候选录屏的只读元数据检查、3 个代表性录屏的 9 帧视觉抽样、3 个 30 秒窗口的音频电平检查；未做 ASR、OCR、评论因果判断和课程逐句匹配。
- Codex 5.5 小样执行是否已具备条件：`部分成立`。输入、窗口、schema、隐私和验收合同已具备；人工 fallback 小样在前置条件满足时允许，自动 ASR/OCR 路线与完整课程原文回查仍为 `blocked / 待补全`。
- 是否允许进入全量执行：否。必须经过 `Codex 5.5 小样 → Codex 5.6 sol 复审`。
- 核心阻断项：
  1. 当前仓库没有可直接复用的本地 ASR/OCR/动作识别/课程检索完整流水线。
  2. `faster_whisper`、`whisper`、`pytesseract`/`tesseract` 当前不可用，且本轮禁止安装新依赖。
  3. 课程 `source_ref` 指向历史 Windows 工作区或网络盘；完整 `full_transcript_clean.jsonl` 不在当前授权 workspace。
  4. 评论截图包含账号标识等个人信息，任何原始 OCR/截图必须停留在 `raw_local`，不得进入 Git。

## 2. 仓库和工作区

| 项目 | 结果 | 状态 |
|---|---|---|
| workspace | `/Volumes/WD_BLACK/澜心社直播` | 已确认 |
| repository | `fthytwerwt-sudo/lanxinshe-` | 已确认 |
| branch | `main` | 已确认 |
| remote | `https://github.com/fthytwerwt-sudo/lanxinshe-.git` | 已确认 |
| `git pull --ff-only` | `Already up to date.` | 已确认 |
| dirty status | 本轮开始前已有一项 tracked PDF 删除、大量 AppleDouble/其他 untracked 文件 | 已确认，均不纳入本轮 |
| 目标路径重叠 | 目标目录原先不存在 | 已确认 |
| 旧事实入口路径 | 两个早期事实文件仍写 `/Users/fan/Documents/澜心社直播` | 待补全；本轮以 P0 和根 `AGENTS.md` 为准 |

事实边界证据：

- 当前 remote/branch/完成定义见 `AGENTS.md`。
- 早期事实入口仍含旧路径：`项目资料_docs/数字人直播项目事实_digital_human_live_project/00_项目总说明_project_brief.md:9-13`、`02_当前任务_current_task.md:7-11`。
- 技术通过不得外推为业务通过：`04_检查标准与完成定义_check_standards.md:7-11`。

## 3. 实际读取情况

已读取：

1. 根 `AGENTS.md` 与其指定的 17 个机制文件。
2. 当前项目事实入口 `00`–`04`。
3. 现有直播录屏解析方案与配套 Excel 入口。
4. 课程资料入口、神经数字人总包、三线对照、可复刻字段、动作触发规则、不适合复刻清单、直播桥接字段、人工复核、质量报告及 source 索引。
5. `scripts/`、`src/`、`tests/`、`requirements.txt`、`package.json` 中与视频、ASR、OCR、动作和检索有关的入口。
6. 相关 Git 提交：
   - `6c89fd63bb338c38c3ca099aba5fe1ce952d437e`：既有直播录屏 intake 方案。
   - `8b6d55abae1fcac72e83ba0c42840f6d5ae4d959`：课程解析资料导入。

关键事实：

- 既有方案明确“不是解析结果”：`docs/直播录屏解析方案_live_recording_analysis/01_直播录屏解析方案详细版_live_recording_analysis_plan.md:14-21`。
- 既有方案已有三层 intake 路线和 5 Sheet 模板：同文件 `116-168`、`281-304`。
- 课程包为阶段性结果：`项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/17_神经数字人课程解析总包_neural_avatar_course_analysis_master.md:24-42`。
- 动作 19,424 个窗口均为低置信，语气来自文本关键词推测：`项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/16_质量检查报告_quality_review_report.md:3-10`。
- 课程资料入口明确不能写成直播脚本、实时回复或数字人能力已实现：`项目资料_docs/课程解析资料_course_analysis/README_课程解析资料入口_course_analysis_index.md:22-27`。

## 4. 新录屏候选与元数据

`最新直播/` 下共 10 个非 AppleDouble 视频，全部可由 `ffprobe` 读取并含视频流和 AAC 音轨：

| candidate_id | 相对路径 | 时长 | 分辨率 | 视频/音频 |
|---|---|---:|---:|---|
| NR001 | `最新直播/ScreenRecording_07-18-2026 10-41-09_1.MP4` | 00:41:38.846 | 1320×2868 | HEVC / AAC stereo |
| NR002 | `最新直播/ScreenRecording_07-18-2026 11-27-55_1.MP4` | 00:26:32.563 | 1320×2868 | HEVC / AAC stereo |
| NR003 | `最新直播/ScreenRecording_07-19-2026 10-44-37_1.MP4` | 00:32:22.113 | 1320×2868 | HEVC / AAC stereo |
| NR004 | `最新直播/ScreenRecording_07-19-2026 11-17-44_1.MP4` | 00:56:39.420 | 1320×2868 | HEVC / AAC stereo |
| NR005 | `最新直播/Record_2026-07-20-10-26-37_2332cb9b27b851b548ba47a91682926c.mp4` | 01:38:55.437 | 720×1600 | H.264 / AAC mono |
| NR006 | `最新直播/Record_2026-07-21-10-28-42_2332cb9b27b851b548ba47a91682926c.mp4` | 01:36:51.053 | 720×1600 | H.264 / AAC mono |
| NR007 | `最新直播/SVID_20260721_103042_1.mp4` | 01:35:00.437 | 578×1280 | H.264 / AAC mono |
| NR008 | `最新直播/SVID_20260722_104105_1.mp4` | 01:05:36.201 | 576×1280 | H.264 / AAC mono |
| NR009 | `最新直播/SVID_20260722_104105_2.mp4` | 00:37:58.934 | 576×1280 | H.264 / AAC mono |
| NR010 | `最新直播/SVID_20260722_104154_1.mp4` | 01:47:51.943 | 578×1280 | H.264 / AAC mono |

元数据只证明容器、轨道和解码入口可读；不证明语音清晰、评论 OCR 准确、音画内容同步或内容类别。

## 5. capability_status

### confirmed（已确认）

- 10 个录屏路径在授权 workspace 内，容器可读，均有视频和音频流。
- `ffprobe`、`ffmpeg`、Python `cv2`、Pillow 可用。
- 抽样帧中评论区、主播脸部/视线/上肢动作/道具或商品卡可观察。
- 课程 lesson/chunk 索引和 19,424 行直播桥接字段存在。
- 既有直播录屏方案和 5 Sheet 模板存在。

### partially_true（部分成立）

- 评论文字在抽样帧中肉眼可见，但未验证 OCR 准确率、滚动去重和跨帧跟踪。
- 三个 30 秒窗口音频电平可测，均非静音；这不等于语音清晰或 ASR 可用。
- 课程摘要可用于 topic/chunk 级候选检索；完整逐字稿逐句回查不成立。
- 动作可由人观察；现有课程动作标签不能直接迁入直播自动规则。

### pending_validation（待验证）

- ASR 文字准确率和时间戳漂移。
- 评论 OCR 召回、文本准确率、去重和隐私脱敏。
- 评论与回复因果关系。
- 语气、停顿、音量变化和情绪观察的一致性。
- 动作事件识别与数字人替代动作适配。
- 课程精确对齐。
- 长视频并行、断点恢复和幂等合并。

### blocked

- 自动 ASR/OCR pilot：`blocked_need_authorized_asr_ocr_execution_route`。
- 课程逐句精确回查：`blocked_course_full_transcript_unavailable_in_workspace`。
- 全量执行：`blocked_until_pilot_review_approved`。

## 6. probe 结果

### 选取片段

- NR001：10% / 50% / 90% 抽帧，50% 附近 30 秒音频电平检查。
- NR005：10% / 50% / 90% 抽帧，50% 附近 30 秒音频电平检查。
- NR010：10% / 50% / 90% 抽帧，50% 附近 30 秒音频电平检查。

### 结果

| 检查项 | 结果 | 状态 |
|---|---|---|
| 评论可见性 | 三个样本的抽样帧均可见评论区；密度不同 | 部分成立 |
| 评论隐私 | 抽样帧可见账号标识，必须 fail-closed 脱敏 | 已确认 |
| 主播动作 | 表情、视线、手势、持物/道具可观察 | 部分成立 |
| 商品/权益画面 | 至少一个样本有商品卡/促单视觉元素 | 已确认_视觉层 |
| 音频轨 | 三个样本均有 AAC；30 秒窗口 mean volume 约 -15.3 至 -11.3 dB | 已确认_技术层 |
| ASR | 本轮未执行 | 待验证 |
| OCR | 本轮未执行 | 待验证 |
| 内容类别 | 只能给 pilot 槽位，需 ASR 或人工先确认 | 待验证 |
| 时间同步 | 容器级音视频起始差约 0–0.276 秒；内容级 lip/audio sync 未验证 | 部分成立 |
| 课程匹配 | 索引入口存在；完整原文不可回查 | 部分成立 |

probe 临时抽帧已删除，没有进入本规划目录或 Git。

## 7. 规划产物

本目录包含：

1. 总体规划。
2. 素材与能力缺口 CSV。
3. 多模态事件合同和 JSON Schema。
4. 课程—直播表达对齐设计。
5. 主播逻辑/动作/评论标签体系。
6. Codex 5.5 小样执行单和 manifest。
7. Codex 5.5 全量执行模板和 manifest。
8. 验收、人工复核、失败回退。
9. 风险、隐私、落库边界。

## 8. Git 闭环说明

- 本目录受 `.git/info/exclude` 的 `docs/` 规则影响，必须对 13 个明确文件使用 path-limited `git add -f`。
- 禁止 `git add .`。
- 本报告不嵌入自身 commit hash，避免自引用；最终 commit、push 和 remote HEAD 证据以本轮 Codex 回报和 `git log -- <本目录>` 为准。

## 9. 下一阶段唯一建议

先解决 `ASR/OCR execution route`：在“不安装新依赖、不调用付费 API”的前提下，确认 Codex 5.5 是否有已授权且可复现的 ASR/OCR 能力；若没有，采用人工标注的三窗口小样。完成三个小样后交回 Codex 5.6 sol 复审。不得直接全量解析。
