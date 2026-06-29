# HappyHorse 生成记录

状态：`happyhorse_generation_completed_pending_human_review`

## 路线

- provider：`alibaba_dashscope`
- model：`happyhorse-1.0-video-edit`
- submit endpoint：`https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- task endpoint：`https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`
- input：`type=video` 15 秒片段 + `type=reference_image` 首帧参考图
- local_fallback_used：`false`

## 任务记录

| source_id | candidate_id | task_id | task_status | selected_final | rescue | output_path |
| --- | --- | --- | --- | --- | --- | --- |
| source_01 | candidate_01_from_source_01 | 552f7c34-d0ed-49b6-9f1a-2af87fbc8e0a | SUCCEEDED | true | false | `/Volumes/WD_BLACK/澜心社直播/outputs/happyhorse_large_motion_reconstruction_probe/candidates/candidate_01_from_source_01_happyhorse_video_edit_native.mp4` |
| source_02 | candidate_02_from_source_02 | 4231a2d2-8b9e-4f27-ad5b-52163b64ba84 | SUCCEEDED | true | false | `/Volumes/WD_BLACK/澜心社直播/outputs/happyhorse_large_motion_reconstruction_probe/candidates/candidate_02_from_source_02_happyhorse_video_edit_native.mp4` |
| source_03 | candidate_03_from_source_03_initial_not_selected | 1d50c8f7-9fff-4a23-8552-a5386a25e939 | SUCCEEDED | false | false | `/Volumes/WD_BLACK/澜心社直播/outputs/happyhorse_large_motion_reconstruction_probe/candidates/candidate_03_from_source_03_happyhorse_video_edit_native.mp4` |
| source_03 | candidate_03_from_source_03_rescue | de8b8cd7-5fca-4262-bb62-e215dd86a498 | SUCCEEDED | true | true | `/Volumes/WD_BLACK/澜心社直播/outputs/happyhorse_large_motion_reconstruction_probe/candidates/candidate_03_from_source_03_rescue_happyhorse_video_edit_native.mp4` |

## rescue 说明

`已确认`：source_03 初始任务因 prompt 误写“绿幕场景”，输出背景明显偏离源视频；这属于输入提示与源片冲突，不是质量抽卡。已使用唯一一次 rescue retry，修正为窗帘/花瓶/瑜伽垫/小球场景，总任务数 `4/4`。
