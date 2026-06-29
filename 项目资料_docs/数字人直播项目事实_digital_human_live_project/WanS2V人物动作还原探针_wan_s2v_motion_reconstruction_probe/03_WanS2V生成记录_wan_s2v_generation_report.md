# WanS2V 生成记录

状态：`three_native_wans2v_candidates_generated`

## API 路线

- provider: `alibaba_dashscope`
- model: `wan2.2-s2v`
- endpoint: `https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis`
- official_doc: `https://help.aliyun.com/zh/model-studio/wan-s2v-api`
- input形式：`image_url + audio_url`
- parameters: `resolution=720P`
- prompt_sent_to_api: `false`
- video_motion_reference_sent_to_api: `false`

## 生成记录

| source_id | candidate_id | task_id | status | 本地输出 |
| --- | --- | --- | --- | --- |
| source_01 | candidate_01_from_source_01 | `97c50297-da02-4551-8e16-4abb893803f3` | SUCCEEDED | `/Volumes/WD_BLACK/澜心社直播/outputs/wan_s2v_motion_reconstruction_probe/candidate_01_from_source_01_wans2v_native.mp4` |
| source_02 | candidate_02_from_source_02 | `d0d775a6-288e-45f0-914d-4c1e123a9e12` | SUCCEEDED | `/Volumes/WD_BLACK/澜心社直播/outputs/wan_s2v_motion_reconstruction_probe/candidate_02_from_source_02_wans2v_native.mp4` |
| source_03 | candidate_03_from_source_03 | `0c7700c5-dd4e-44f7-a5b4-b0afdec06085` | SUCCEEDED | `/Volumes/WD_BLACK/澜心社直播/outputs/wan_s2v_motion_reconstruction_probe/candidate_03_from_source_03_wans2v_native.mp4` |

## 技术校验

| candidate_id | duration_sec | resolution | fps | audio | decode |
| --- | ---: | --- | ---: | --- | --- |
| candidate_01_from_source_01 | 14.8 | 720x1280 | 30 | aac / stereo | passed |
| candidate_02_from_source_02 | 14.8 | 720x1280 | 30 | aac / stereo | passed |
| candidate_03_from_source_03 | 14.8 | 720x1280 | 30 | aac / stereo | passed |

## 安全边界

- signed URL 未写入报告；本报告只记录本地路径、task_id 和 redacted 记录来源。
- generated media committed: `false`
- local_fallback_used: `false`
- fallback_tts_used: `false`
- rescue_retry_count: `0`
