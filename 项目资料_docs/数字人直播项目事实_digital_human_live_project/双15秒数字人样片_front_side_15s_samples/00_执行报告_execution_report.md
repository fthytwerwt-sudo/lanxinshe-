# 00_执行报告

状态：`two_samples_created` / `technical_validation_passed` / `content_validation_pending_human_review`

## 执行结果

| 字段 | 值 |
| --- | --- |
| status | two_samples_created |
| workspace | `/Volumes/WD_BLACK/澜心社直播` |
| remote | `https://github.com/fthytwerwt-sudo/lanxinshe-.git` |
| branch | `main` |
| local_HEAD_at_generation | `c0807213bbf12d23640ad9d2103a4cf254501ceb` |
| front_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/01_front_15s_sample.mp4` |
| side_video_path | `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/02_side_15s_sample.mp4` |
| front_duration | 14.812500 |
| side_duration | 14.812500 |
| front_resolution | 512x896 |
| side_resolution | 512x896 |
| has_audio_front | true |
| has_audio_side | true |
| wan_called | yes |
| qwen_vl_max_called | yes |
| qwen_vl_plus_called | yes |
| embedding_used | no |
| rerank_used | no |
| media_committed | no |
| secret_printed | no |

## 输入与候选

- 正面候选：`R02_C5824_C01_opening`，源视频 `参考/完整直播录屏/今年直播素材/C5824.MP4`，候选片段 `00:01:00-00:01:15`。
- 偏侧候选：`R06_C5834_C02_middle`，源视频 `参考/完整直播录屏/直播效果一般/C5834（上）.MP4`，候选片段 `00:26:45-00:27:00`。
- 正面参考帧：`00:01:00`，本地 `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/input_front_reference_frame.jpg`。
- 偏侧参考帧：`00:26:51`，本地 `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/input_side_reference_frame.jpg`。
- 正面音频：`00:01:00-00:01:15`，本地 `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/input_front_audio.wav`。
- 偏侧音频：`00:26:45-00:27:00`，本地 `/Volumes/WD_BLACK/澜心社直播/outputs/two_15s_avatar_samples_front_side/input_side_audio.wav`。

## 模型调用状态

| 模型 | 用途 | 状态 |
| --- | --- | --- |
| qwen-vl-max | 正面候选短片分析 | connected |
| qwen-vl-max | 偏侧候选短片分析 | connected |
| qwen-vl-plus | 偏侧参考帧复核 | connected |
| wan2.2-s2v | 正面 15 秒生成 | completed |
| wan2.2-s2v | 偏侧 15 秒生成 | completed |

## 技术验证

- 正面 MP4：`validation_status=passed`，`decodable=true`，`audio_present=true`。
- 偏侧 MP4：`validation_status=passed`，`decodable=true`，`audio_present=true`。
- 技术验证只证明文件可播放、可解码、有音轨、时长约 15 秒；不等于内容、人感、人审或供应商验收通过。

## 降级与风险

- 本轮使用 `480P` 生成，属于控制成本和降低失败面的降级选择。
- 正面参考帧露齿微笑明显，需重点人工复核牙齿和张嘴幅度。
- 偏侧参考帧为侧身回头角度，符合非 90° 纯侧脸要求，但嘴巴开合较明显，需重点复核侧向口型。
- 声音来源于原始直播片段，已做响度统一；未做人工听辨通过、ASR 逐字转写或声音克隆验收。

## 安全边界

- `.env` 只读取 present/missing，不打印值。
- OSS signed URL 只保存 redacted 版本，不保存 query string。
- MP4、WAV、JPG、contact sheet、runtime script 不进入 GitHub 落库目录。
