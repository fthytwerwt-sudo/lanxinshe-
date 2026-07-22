# 阻塞素材恢复建议

- 生成时间：2026-07-03T17:13:31
- 检查范围：当前 7 个 `blocked_probe_failed` 素材及其候选有效副本。
- 检查结论：这些 blocked 源素材不是路径不存在、权限不足、扩展名误判或 ffprobe 缺失造成；主要失败原因是 MP4 缺少 `moov atom`，其中 L0816 为 0 字节文件。
- 处理原则：保持原始课程文件不变；损坏源文件继续保留 `blocked_probe_failed`；候选副本只作为人工复核/补转线索，不把非严格重复素材自动覆盖为同一课。

| blocked lesson_id | blocked 当前状态 | 失败原因 | 候选副本当前状态 | 恢复/复核建议 |
|---|---|---|---|---|
| L0816 | L0816；blocked_probe_failed；第一课；解谜私密瑜伽2020-04-20212104(2).mp4 | 0 字节文件，ffprobe 报 moov atom not found | L1187；completed；时长 01:04:41.796；第一课；解谜私密瑜伽2020-04-20212104.mp4<br>L1560；completed_reused；时长 01:04:41.796；第一课；解谜私密瑜伽2020-04-20212104(3).mp4 | 当前源文件本地不可恢复；候选副本完成后人工确认是否同课。 |
| L0873 | L0873；blocked_probe_failed；第3课 阴道垂吊术.mp4 | MP4 缺 moov atom | L1032；completed；时长 00:41:48.656；第3课 阴道垂吊术.mp4 | 人工确认同名有效副本内容是否能补足缺口。 |
| L0875 | L0875；blocked_probe_failed；第6课 激情美臀舞 Mp4.mp4 | MP4 缺 moov atom | L0921；completed；时长 00:50:32.162；第6课 激情美臀舞 mp4.mp4<br>L1035；completed_reused；时长 00:50:32.162；第6课 激情美臀舞 mp4.mp4 | 优先参考已完成/已复用副本，人工核对课程内容。 |
| L0877 | L0877；blocked_probe_failed；第8课 伴侣身体开发.mp4 | MP4 缺 moov atom | L1037；completed；时长 01:02:13.267；第8课 伴侣身体开发.mp4 | 人工确认同名有效副本内容是否能补足缺口。 |
| L0878 | L0878；blocked_probe_failed；第9课 伴侣共修.mp4 | MP4 缺 moov atom | L1038；completed；时长 00:57:07.160；第9课 伴侣共修.mp4 | 人工确认同名有效副本内容是否能补足缺口。 |
| L0879 | L0879；blocked_probe_failed；第10课 性养生十六式.mp4 | MP4 缺 moov atom | L1039；completed；时长 00:54:31.468；第10课 性养生十六式.mp4 | 人工确认同名有效副本内容是否能补足缺口。 |
| L0880 | L0880；blocked_probe_failed；魅力女神提升班 先导课.mp4 | MP4 缺 moov atom | L1040；completed_reused；时长 00:03:52.249；魅力女神提升班 先导课.mp4 | 人工确认同名有效副本内容是否能补足缺口。 |

## 后续动作

1. 后台 ASR 会继续处理候选副本；每次构建交付包时，本文件会按 `data/transcription_status.csv` 自动刷新候选状态。
2. 候选副本完成后，应由人工根据课程标题、内容开头、时长和上下文确认是否能填补对应 blocked 课的缺口。
3. 不建议对损坏 MP4 做自动修复写回；如需尝试修复，应复制到工作区另存为副本后处理，原始文件保持不变。
