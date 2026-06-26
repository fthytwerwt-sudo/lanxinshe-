# 阿里 VideoRetalk 连接探针报告

状态：`completed_dry_run_connected_generation_skipped_by_cost_guard`

生成时间：`2026-06-26`

## 一页结论

- `已确认`：当前仓库已新增 `videoretalk` registry 配置，类别为 `avatar_video_retalk / video_lip_sync`。
- `已确认`：`scripts/probe_alibaba_videoretalk_connection.py --dry-run --safe` 已通过，只构造 payload，不提交真实任务。
- `已确认`：本地 3 秒 probe 素材已准备到 `outputs/videoretalk_probe/`，并由 `.gitignore` 排除，不进入 GitHub。
- `已确认`：`validate_videoretalk_inputs.py` 校验通过，视频和音频均符合本轮 VideoRetalk 基础输入限制。
- `已确认`：`ALLOW_VIDEORETALK_GENERATION_PROBE` 当前为 `missing`，`--submit` 被费用保护闸门拦截，未创建真实 VideoRetalk 任务。
- `待验证`：未进行 paid generation probe，未上传 OSS 公网 URL，未生成 VideoRetalk 结果视频，未验证口型替换质量。

## 官方能力约束核对

来源：阿里云 Model Studio / DashScope VideoRetalk 官方文档（`https://help.aliyun.com/zh/model-studio/videoretalk-api`）。

- model: `videoretalk`
- submit endpoint: `https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/`
- task endpoint: `https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`
- async header: `X-DashScope-Async: enable`
- required inputs: `input.video_url`, `input.audio_url`
- optional input: `input.ref_image_url`
- optional parameters: `parameters.video_extension`, `parameters.query_face_threshold`
- 重要边界：`video_url / audio_url / ref_image_url` 必须是公网 HTTP / HTTPS URL，本地路径不能直接提交。

## 本轮边界

- paid API call: `no`
- generation task submitted: `false`
- task_id: `n/a`
- result_video_path: `n/a`
- media_committed: `no`
- printed_secret: `no`
- capability claim: `dry_run_entry_ready_only`

## 环境状态

环境变量只记录 `present / missing / empty`，不记录任何值。

| env | status |
| --- | --- |
| `DASHSCOPE_API_KEY` | `present` |
| `ALIBABA_CLOUD_ACCESS_KEY_ID` | `present` |
| `ALIBABA_CLOUD_ACCESS_KEY_SECRET` | `present` |
| `ALIBABA_REGION_ID` | `present` |
| `ALIBABA_OSS_ENDPOINT` | `present` |
| `ALIBABA_OSS_BUCKET` | `present` |
| `ALIBABA_OSS_OBJECT_PREFIX` | `present` |
| `ALIBABA_OSS_SIGNED_URL_EXPIRES` | `present` |
| `ALLOW_VIDEORETALK_GENERATION_PROBE` | `missing` |

## 文件改动

### 修改

- `config/alibaba_model_registry.py`

### 新增

- `scripts/probe_alibaba_videoretalk_connection.py`
- `scripts/prepare_videoretalk_probe_assets.py`
- `scripts/validate_videoretalk_inputs.py`
- `codex_reports/阿里VideoRetalk连接探针_alibaba_videoretalk_connection_probe_report.md`

## Registry 结果

- category: `avatar_video_retalk`
- subcategory: `video_lip_sync`
- model: `videoretalk`
- provider: `alibaba_dashscope`
- api_type: `async_http`
- cost_guard: `default_skip_generation_unless_ALLOW_VIDEORETALK_GENERATION_PROBE_true`
- 中文备注：VideoRetalk 是“视频口型替换”，不是单图数字人生成，也不是实时直播。

## Dry-run 结果

命令：

```bash
python3 scripts/probe_alibaba_videoretalk_connection.py --dry-run --safe
```

结果：

| field | value |
| --- | --- |
| status | `dry_run_passed` |
| run_dir | `outputs/videoretalk_probe/20260626_235827_dry_run` |
| model | `videoretalk` |
| payload_shape_valid | `true` |
| public_urls_provided | `false` |
| dry_run_placeholder_urls | `true` |
| would_submit | `false` |
| generation_probe_allowed | `false` |
| generation_probe_submitted | `false` |

## 本地 probe 素材准备

命令：

```bash
python3 scripts/prepare_videoretalk_probe_assets.py --safe --duration-sec 3
```

结果：

| field | value |
| --- | --- |
| prepared | `true` |
| source_video | `参考/完整直播录屏/今年直播素材/C5824.MP4` |
| start | `00:01:00` |
| duration_sec | `3.0` |
| video | `outputs/videoretalk_probe/input_video_3s.mp4` |
| audio | `outputs/videoretalk_probe/input_audio_3s.wav` |
| ref_image | `outputs/videoretalk_probe/ref_image.jpg` |
| media_committed | `false` |

这些文件只用于本地 probe，禁止提交。

## 输入校验结果

命令：

```bash
python3 scripts/validate_videoretalk_inputs.py \
  --video outputs/videoretalk_probe/input_video_3s.mp4 \
  --audio outputs/videoretalk_probe/input_audio_3s.wav \
  --safe
```

结果：

| field | value |
| --- | --- |
| input_valid | `true` |
| blocked_reason | `` |
| video_format | `mp4` |
| video_size_bytes | `501288` |
| video_duration_sec | `3.0` |
| video_fps | `50.0` |
| video_width | `720` |
| video_height | `1280` |
| video_codec | `h264` |
| audio_format | `wav` |
| audio_size_bytes | `96078` |
| audio_duration_sec | `3.0` |
| audio_codec | `pcm_s16le` |
| audio_sample_rate | `16000` |
| audio_channels | `1` |

## Submit 费用保护验证

命令：

```bash
python3 scripts/probe_alibaba_videoretalk_connection.py \
  --submit \
  --safe \
  --video-url https://example.com/input_video.mp4 \
  --audio-url https://example.com/input_audio.wav
```

结果：

| field | value |
| --- | --- |
| exit_code | `2` |
| status | `blocked_generation_probe_not_allowed` |
| blocked_reason | `blocked_generation_probe_not_allowed` |
| blocked_message | `ALLOW_VIDEORETALK_GENERATION_PROBE is not true` |
| would_submit | `false` |
| generation_probe_submitted | `false` |

## 验证命令

| command | result |
| --- | --- |
| `git pull --ff-only` | `Already up to date.` |
| `python3 -m py_compile config/alibaba_model_registry.py scripts/probe_alibaba_videoretalk_connection.py scripts/prepare_videoretalk_probe_assets.py scripts/validate_videoretalk_inputs.py` | `passed` |
| `python3 scripts/probe_alibaba_videoretalk_connection.py --dry-run --safe` | `dry_run_passed` |
| `python3 scripts/prepare_videoretalk_probe_assets.py --safe --duration-sec 3` | `prepared=true` |
| `python3 scripts/validate_videoretalk_inputs.py --video outputs/videoretalk_probe/input_video_3s.mp4 --audio outputs/videoretalk_probe/input_audio_3s.wav --safe` | `input_valid=true` |
| `python3 scripts/probe_alibaba_videoretalk_connection.py --submit --safe --video-url https://example.com/input_video.mp4 --audio-url https://example.com/input_audio.wav` | `blocked_generation_probe_not_allowed` |
| `python3 -m unittest discover -s tests` | `Ran 7 tests, OK`; note: existing urllib3 LibreSSL warning appeared outside this change |
| `git check-ignore -v outputs/videoretalk_probe/input_video_3s.mp4 outputs/videoretalk_probe/input_audio_3s.wav outputs/videoretalk_probe/ref_image.jpg` | all ignored by `.gitignore:35:outputs/` |

## 后续真实 probe 条件

只有同时满足以下条件，才允许进入 paid generation probe：

1. `.env` 显式设置 `ALLOW_VIDEORETALK_GENERATION_PROBE=true`。
2. 本地视频和音频先通过 `validate_videoretalk_inputs.py`。
3. 提供可访问的公网 `video_url` / `audio_url`，或显式使用 `--upload-local-assets` 上传到 OSS 并生成 signed URL。
4. 报告中只保存 redacted URL，不保存 signed URL query、Authorization header、API key、AccessKey 或 token。
5. 结果视频只保存到 `outputs/videoretalk_probe/`，不提交 GitHub。

## 仍然待验证

- `待验证`：OSS signed URL 上传和访问是否稳定。
- `待验证`：DashScope 是否允许当前账号调用 `videoretalk`。
- `待验证`：真实 `task_id` 创建、轮询和下载链路。
- `待验证`：输出视频的口型、人脸稳定性、牙齿、眼神、肩颈、画面连续性和人审质量。
