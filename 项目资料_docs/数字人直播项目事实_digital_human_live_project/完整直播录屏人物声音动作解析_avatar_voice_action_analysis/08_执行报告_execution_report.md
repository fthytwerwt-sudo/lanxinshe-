# 08_执行报告

状态：`local_only_analysis_not_committed`

## commands

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git status --short
python3 outputs/full_live_recording_avatar_voice_action_analysis/_runtime_scripts/run_avatar_voice_action_analysis.py
```

## result

- workspace: `/Volumes/WD_BLACK/澜心社直播`
- reference_dir: `参考/完整直播录屏`
- requested_reference_dir: `参考-完整直播录屏` -> `部分成立`，同名目录不存在；使用仓库内真实目录 `参考/完整直播录屏`。
- video_count: 11
- qwen-vl-max calls: 33
- qwen-vl-plus calls: 11
- qwen2.5-omni-7b calls: 8
- used_embedding: no
- used_rerank: no
- called_wan2.2-s2v: no
- committed: no
- pushed: no
- secret_printed: no
- media_staged: no

## files_changed

- `outputs/full_live_recording_avatar_voice_action_analysis/00_阿里模型分工暂定表_model_role_map.md`
- `outputs/full_live_recording_avatar_voice_action_analysis/01_完整直播录屏素材清单_recording_inventory.md`
- `outputs/full_live_recording_avatar_voice_action_analysis/02_人物形象与动作总报告_avatar_action_master_report.md`
- `outputs/full_live_recording_avatar_voice_action_analysis/03_语音音色与说话方式总报告_voice_speech_master_report.md`
- `outputs/full_live_recording_avatar_voice_action_analysis/04_人物动作素材候选库_action_clip_candidates.csv`
- `outputs/full_live_recording_avatar_voice_action_analysis/05_语音素材候选库_voice_clip_candidates.csv`
- `outputs/full_live_recording_avatar_voice_action_analysis/06_形象表情姿态字段表_avatar_expression_pose_table.csv`
- `outputs/full_live_recording_avatar_voice_action_analysis/07_数字人定制与样片微调建议_digital_human_asset_recommendations.md`
- `outputs/full_live_recording_avatar_voice_action_analysis/08_执行报告_execution_report.md`
- `outputs/full_live_recording_avatar_voice_action_analysis/data/recording_manifest.json`
- `outputs/full_live_recording_avatar_voice_action_analysis/data/model_role_map.json`
- `outputs/full_live_recording_avatar_voice_action_analysis/data/clip_candidates.json`
- `outputs/full_live_recording_avatar_voice_action_analysis/media_review/`

## failed_items

- `参考-完整直播录屏`：同名目录不存在，已按 `部分成立` 使用 `参考/完整直播录屏`。
- 口头禅/逐字重音：未做 ASR 逐字转写，标 `待验证`。
- 人审通过：本轮未做人审，禁止写通过。

## validation

- `ffprobe` 已读取每场视频元数据。
- 每场生成 5 个代表片段记录。
- 生成动作 CSV、声音 CSV、表情姿态 CSV、Markdown 总报告、JSON manifest。
- 模型调用没有超过 P0 上限。
- 没有调用 embedding / rerank / wan2.2-s2v。
- 按长度 >= 8 的 secret-like `.env` 值复扫文本输出，未发现泄露。
- 没有 stage / commit / push。

## blocked reason

- blocked: none for local analysis package.
- pending_validation: 人工听辨、ASR 转写、供应商样片人审、声音授权。
