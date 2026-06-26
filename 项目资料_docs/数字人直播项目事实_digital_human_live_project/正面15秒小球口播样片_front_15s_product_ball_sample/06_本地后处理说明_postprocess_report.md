# 06_本地后处理说明

状态：`postprocess_applied_and_threshold_passed`

## 原因

Wan 720P 原始直出视频生成成功，但 `mouth_face_ratio_p90=0.08985602706670762`，超过项目通过线 `0.075`。

## 方法

- 未新增 Wan 任务。
- 对每帧由 Vision landmark 定位嘴部小区域。
- 只对嘴部局部区域做垂直压缩，并用 feather blend 融合边缘。
- 重新编码视频，并 mux 原始音轨。

## 最终指标

- p90_mouth_open_ratio: `0.10403372181307027`
- p90_mouth_face_ratio: `0.030434972047805795`
- fail_frame_percent: `0`
- longest_fail_streak: `0`

## 边界

后处理通过只证明技术阈值满足，不等于人审自然度通过。
