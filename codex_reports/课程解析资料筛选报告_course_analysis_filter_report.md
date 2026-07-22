# 课程解析资料筛选报告

## 主结论

- `部分成立`：已找到并筛选两类课程解析资料，已将确认有效且低于 10MB 的轻量文本/CSV/JSON/JSONL 复制到正式资料目录。
- `待验证`：课程内容、动作标注、OCR 结果、神经数字人复刻规则仍需人工复核；本轮不代表业务验收通过。
- `已确认`：原始来源目录未被移动、删除或改写；本轮排除了 zip、媒体、cache、虚拟环境、预览图和 AppleDouble。

## 来源

- 原始待筛选目录：`/Volumes/WD_BLACK/转移文件(直播)`
- 采用课程逐字稿包：`课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack`
- 采用神经数字人包：`神经数字人课程解析交付包_neural_avatar_course_analysis_pack`
- 未采用版本：`神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/`、mojibake 目录、zip 和运行环境目录。

## 包完整性

- 课程逐字稿包命中：15/15；缺失：无。
- 神经数字人包命中：19/19；缺失：无。
- 课程逐字稿包执行报告状态：`partial_completed_needs_review`。
- 神经数字人包执行报告状态：`partial_completed_action_low_confidence_needs_review; partial_completed_ocr_needs_manual_review`。

## 分类统计

| 分类 | 数量 |
|---|---:|
| `local_reference_only` | 12844 |
| `repo_import` | 46 |
| `duplicate_or_obsolete` | 284 |
| `pending_review` | 3225 |

- 正式入库文件数：50
- 仅本地保留文件数：12844
- 重复/旧版文件数：284
- 待复核文件数：3225
- blocked 文件数：0

## 正式入库文件

| 来源 | 正式路径 | 大小(bytes) | 依据 |
|---|---|---:|---|
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/00_执行报告_execution_report.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/00_执行报告_execution_report.md` | 1828 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/01_课程素材总清单_course_material_inventory.csv` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/01_课程素材总清单_course_material_inventory.csv` | 1115620 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/02_视频分块清单_video_chunk_manifest.csv` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/02_视频分块清单_video_chunk_manifest.csv` | 7022970 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/03_课件画面对照表_courseware_visual_alignment.csv` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/03_课件画面对照表_courseware_visual_alignment.csv` | 8868108 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/04_课件画面摘要_courseware_visual_summary.md` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/04_课件画面摘要_courseware_visual_summary.md` | 520 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/05_逐字稿时间轴_transcript_timeline.csv` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/05_逐字稿时间轴_transcript_timeline.csv` | 6399518 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/06_讲师动作时间轴_presenter_action_timeline.csv` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/06_讲师动作时间轴_presenter_action_timeline.csv` | 6643074 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/07_动作标签库_action_label_library.md` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/07_动作标签库_action_label_library.md` | 1205 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/08_语气节奏时间轴_prosody_pacing_timeline.csv` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/08_语气节奏时间轴_prosody_pacing_timeline.csv` | 4480641 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/10_三线对照阅读版_transcript_courseware_action_alignment_readable.md` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/10_三线对照阅读版_transcript_courseware_action_alignment_readable.md` | 102477 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/11_神经数字人可复刻字段_neural_avatar_reproduction_fields.md` | `项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/11_神经数字人可复刻字段_neural_avatar_reproduction_fields.md` | 522 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/12_数字人动作触发规则_avatar_action_trigger_rules.csv` | `项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/12_数字人动作触发规则_avatar_action_trigger_rules.csv` | 547 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/13_不适合数字人复刻动作清单_avatar_unsuitable_actions.md` | `项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/13_不适合数字人复刻动作清单_avatar_unsuitable_actions.md` | 641 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/14_适合迁入直播项目的桥接字段_live_project_bridge_fields.md` | `项目资料_docs/课程解析资料_course_analysis/05_直播项目桥接_live_project_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/14_适合迁入直播项目的桥接字段_live_project_bridge_fields.md` | 341 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/15_人工复核清单_manual_review_list.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/15_人工复核清单_manual_review_list.md` | 543 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/16_质量检查报告_quality_review_report.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/神经数字人课程解析包_neural_avatar_course_analysis_pack/16_质量检查报告_quality_review_report.md` | 976 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/17_神经数字人课程解析总包_neural_avatar_course_analysis_master.md` | `项目资料_docs/课程解析资料_course_analysis/04_神经数字人桥接_neural_avatar_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/17_神经数字人课程解析总包_neural_avatar_course_analysis_master.md` | 1525 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/18_迁移索引_manifest_for_copy.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/18_迁移索引_manifest_for_copy.json` | 18247 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/lesson_id_mapping.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/lesson_id_mapping.json` | 874653 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/live_project_bridge_fields.csv` | `项目资料_docs/课程解析资料_course_analysis/05_直播项目桥接_live_project_bridge/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/live_project_bridge_fields.csv` | 7022863 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/previous_transcript_index.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/previous_transcript_index.json` | 1278140 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/prosody_pacing.jsonl` | `项目资料_docs/课程解析资料_course_analysis/02_课件动作对照_courseware_action_alignment/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/prosody_pacing.jsonl` | 8209926 | lightweight structured/text source file selected for formal project materials |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/source_inventory.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/神经数字人课程解析包_neural_avatar_course_analysis_pack/data/source_inventory.json` | 2144069 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/00_执行报告_execution_report.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/00_执行报告_execution_report.md` | 1133 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/01_课程文件清单_course_inventory.csv` | `项目资料_docs/课程解析资料_course_analysis/01_课程逐字稿_course_transcripts/课程逐字稿解析包_course_transcript_analysis_pack/01_课程文件清单_course_inventory.csv` | 462967 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/04_课程结构总览_course_structure_overview.md` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/04_课程结构总览_course_structure_overview.md` | 190446 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/05_章节知识点拆解_chapter_knowledge_breakdown.md` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/05_章节知识点拆解_chapter_knowledge_breakdown.md` | 3315312 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/06_案例与故事素材库_cases_story_bank.csv` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/06_案例与故事素材库_cases_story_bank.csv` | 5874918 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/07_金句与可复用表达_reusable_quotes.md` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/07_金句与可复用表达_reusable_quotes.md` | 686988 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/08_关键词术语表_terms_glossary.csv` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/08_关键词术语表_terms_glossary.csv` | 492325 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/09_问题_答案_异议_回应_QA_objection_response_bank.csv` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/09_问题_答案_异议_回应_QA_objection_response_bank.csv` | 9659558 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/10_适合迁入直播项目的桥接字段_live_project_bridge_fields.md` | `项目资料_docs/课程解析资料_course_analysis/05_直播项目桥接_live_project_bridge/课程逐字稿解析包_course_transcript_analysis_pack/10_适合迁入直播项目的桥接字段_live_project_bridge_fields.md` | 100535 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/11_待人工复核清单_manual_review_list.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/11_待人工复核清单_manual_review_list.md` | 1356363 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/12_质量检查报告_quality_review_report.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/12_质量检查报告_quality_review_report.md` | 2495 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/13_导入索引_manifest_for_copy.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/课程逐字稿解析包_course_transcript_analysis_pack/13_导入索引_manifest_for_copy.json` | 586557 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/14_课程解析总包_course_analysis_master.md` | `项目资料_docs/课程解析资料_course_analysis/03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/14_课程解析总包_course_analysis_master.md` | 5659257 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/15_后台运行与续跑说明_resume_instructions.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/15_后台运行与续跑说明_resume_instructions.md` | 7075 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/16_当前进度快照_current_progress_snapshot.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/16_当前进度快照_current_progress_snapshot.md` | 1624 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/17_原始素材完整性检查_source_integrity_check.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/17_原始素材完整性检查_source_integrity_check.md` | 1024 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/18_阻塞素材恢复建议_blocked_media_recovery_notes.md` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/18_阻塞素材恢复建议_blocked_media_recovery_notes.md` | 3096 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/live_bridge_fields.csv` | `项目资料_docs/课程解析资料_course_analysis/05_直播项目桥接_live_project_bridge/课程逐字稿解析包_course_transcript_analysis_pack/data/live_bridge_fields.csv` | 2860833 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/source_integrity_check.csv` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/课程逐字稿解析包_course_transcript_analysis_pack/data/source_integrity_check.csv` | 422863 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/source_integrity_check.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/课程逐字稿解析包_course_transcript_analysis_pack/data/source_integrity_check.json` | 336 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/source_inventory.json` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/课程逐字稿解析包_course_transcript_analysis_pack/data/source_inventory.json` | 1127653 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/transcription_status.csv` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/data/transcription_status.csv` | 354030 | lightweight structured/text source file selected for formal project materials |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/transcription_status_snapshot.csv` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程逐字稿解析包_course_transcript_analysis_pack/data/transcription_status_snapshot.csv` | 354030 | lightweight structured/text source file selected for formal project materials |
| `generated:local_reference_only_large_files` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/local_reference_only_large_files.md` | 3100 | generated local-only index for oversized core materials |
| `generated:course_analysis_review_list` | `项目资料_docs/课程解析资料_course_analysis/06_质量检查与人工复核_quality_review/课程解析资料待复核清单_course_analysis_review_list.md` | 4353 | generated review checklist for import limitations |
| `generated:course_analysis_index` | `项目资料_docs/课程解析资料_course_analysis/README_课程解析资料入口_course_analysis_index.md` | 2696 | generated course analysis entry index |
| `generated:course_analysis_import_manifest` | `项目资料_docs/课程解析资料_course_analysis/07_来源与迁移索引_source_manifests/课程解析资料入库清单_course_analysis_import_manifest.json` | 410901 | generated source/import manifest |

## 仅本地保留重点项

| 来源 | 大小(bytes) | 原因 |
|---|---:|---|
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv` | 11221457 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/chunk_manifest.jsonl` | 10763343 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/courseware_frames.jsonl` | 14317713 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/neural_avatar_bridge_fields.jsonl` | 14436837 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/presenter_actions.jsonl` | 11013324 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/transcript_timeline.jsonl` | 12229439 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/tri_alignment.jsonl` | 17105217 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/02_全量逐字稿_原文保真_full_transcript_raw.md` | 155296157 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/03_全量逐字稿_清洗版_full_transcript_clean.md` | 155296004 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/full_transcript_clean.jsonl` | 1470970736 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |
| `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/full_transcript_raw.jsonl` | 1364699757 | single file exceeds 10MB repo import threshold; keep local reference and review for future chunking |

## 重复或旧版判断

- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/` 体积约 25G，包含工作区、cache、frames_preview、state 等运行材料；本轮采用 183M 的正式交付包目录。
- `神经数字人课程解析交付包_neural_avatar_course_analysis_pack.zip` 与工作区 zip 均仅本地保留。
- mojibake 课程目录仅 4M，路径编码异常，本轮不作为采用版本。

## 风险与边界

- `已确认`：未读取或提交 `.env`、API key、secret、token、cookie。文件名中的 tokenizer/cookies.py 等位于 venv/cache，仅作为本地运行依赖排除。
- `已确认`：大体量逐字稿和关键 JSONL/CSV 数据未入 Git，已记录在 local reference index。
- `待验证`：动作字段、课件 OCR 和直播桥接字段仍需人工或后续模型复核。
- `待验证`：本轮只完成资料入库，不代表直播脚本、实时回复或数字人动作规则已接入。

## 验证补充

- `已确认`：正式资料目录清理后无 `._*`、`.DS_Store`、zip、媒体、图片或 cache 文件。
- `已确认`：secret 扫描命中均为课程原文普通词、依赖包文件名或“不要复制 secret/token/cookie”的排除说明，未发现 API key、Authorization header 或私钥格式。
- `待验证`：commit SHA 和 remote HEAD 以本轮最终 Git 回报为准，manifest 内保留 pending 说明。
