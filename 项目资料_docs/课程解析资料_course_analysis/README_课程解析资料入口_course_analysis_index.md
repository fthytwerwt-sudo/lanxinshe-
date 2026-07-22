# 课程解析资料入口

## 定位

`已确认`：本目录保存从用户本轮提供的原始待筛选目录中筛出的轻量课程解析资料。

- 原始来源目录：`/Volumes/WD_BLACK/转移文件(直播)`
- 本轮导入日期：2026-07-22
- 原始来源是否改动：否，仅复制轻量资料并生成索引。
- 本目录不包含原始视频、音频、zip、cache、虚拟环境、预览图或 AppleDouble 文件。

## 资料层级

- `01_课程逐字稿_course_transcripts/`：课程清单与逐字稿相关轻量索引。全量逐字稿大文件只在来源目录保留。
- `02_课件动作对照_courseware_action_alignment/`：课件画面、逐字稿时间轴、讲师动作时间轴、语气节奏和阅读版三线对照等轻量表。
- `03_课程知识拆解_course_knowledge/`：课程结构、知识点、案例故事、金句术语、问答异议与课程解析总包。
- `04_神经数字人桥接_neural_avatar_bridge/`：神经数字人字段说明、动作触发规则、不适合复刻动作清单和总包说明。
- `05_直播项目桥接_live_project_bridge/`：适合迁入直播项目的桥接字段。
- `06_质量检查与人工复核_quality_review/`：执行报告、质量检查、人工复核和待复核清单。
- `07_来源与迁移索引_source_manifests/`：原始 manifest、source inventory、导入清单和本地大文件引用。

## 事实边界

- 原始逐字稿和清洗逐字稿属于课程解析来源材料；本轮未改写。
- 课程知识、案例、金句、问答、动作和桥接字段是 AI 解析产物，必须保留来源和复核状态。
- 神经数字人相关资料仍有动作低置信度和 OCR 待复核问题，不能写成数字人能力已实现。
- 本目录不代表直播脚本、实时回复、数字人动作规则或业务验收已经完成。

## 优先读取顺序

1. `07_来源与迁移索引_source_manifests/课程解析资料入库清单_course_analysis_import_manifest.json`
2. `06_质量检查与人工复核_quality_review/课程解析资料待复核清单_course_analysis_review_list.md`
3. `03_课程知识拆解_course_knowledge/课程逐字稿解析包_course_transcript_analysis_pack/14_课程解析总包_course_analysis_master.md`
4. `05_直播项目桥接_live_project_bridge/` 下的桥接字段文件
5. `02_课件动作对照_courseware_action_alignment/` 与 `04_神经数字人桥接_neural_avatar_bridge/` 下的动作和三线对照资料

## 大文件说明

全量逐字稿、三线对照主表及部分 JSONL 数据超过本轮 Git 入库阈值。它们保留在来源目录，并记录在 `07_来源与迁移索引_source_manifests/local_reference_only_large_files.md`。
