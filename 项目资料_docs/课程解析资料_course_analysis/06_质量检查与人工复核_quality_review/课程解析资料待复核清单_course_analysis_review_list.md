# 课程解析资料待复核清单

## 状态

- `部分成立`：资料已筛选并入库为可追溯项目资料，但内容仍需人工复核。
- `待验证`：本清单不代表数字人动作规则已接入系统，也不代表直播话术已验收。

## 必查复核项

1. 课程逐字稿包状态为 `partial_completed_needs_review`，仍有 7 个素材 blocked，需确认是否补拷或重跑。
2. 神经数字人包状态为 `partial_completed_action_low_confidence_needs_review; partial_completed_ocr_needs_manual_review`。
3. 神经数字人动作识别为低置信度，执行报告记录 19424 个 chunk 需要人工复核。
4. OCR 不可用，课件画面文字未完成可靠识别，需人工抽查或后续 OCR 补跑。
5. 全量原文逐字稿和清洗版逐字稿单文件约 155MB，未进入 Git；正式目录只保留来源索引。
6. 三线对照主表和多个 JSONL 数据文件超过 10MB，未直接入库；如要用于程序读取，需另行做分块导入设计。
7. `.venv_course_transcript`、`_cache/vision_venv`、zip、图片预览和日志均未入 Git。

## 已知缺失或未完整入库文件

| 项目 | 状态 | 说明 |
|---|---|---|
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/chunk_manifest.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/courseware_frames.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/neural_avatar_bridge_fields.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/presenter_actions.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/transcript_timeline.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/tri_alignment.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/02_全量逐字稿_原文保真_full_transcript_raw.md` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/03_全量逐字稿_清洗版_full_transcript_clean.md` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/full_transcript_clean.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/full_transcript_raw.jsonl` | local_reference_only | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |

## 后续人工判断

- 是否需要将大体量逐字稿按 lesson_id 分块后进入 Git。
- 是否需要对三线对照、动作字段、OCR 缺失项做人工复核后再进入直播运行字段。
- 是否保留 docx/pdf 作为本地查看材料，当前不作为 Git 事实源。
