# 执行报告_execution_report

## 执行概览

- 创建时间：2026-07-03 18:10:46
- 状态：partial_completed_action_low_confidence_needs_review; partial_completed_ocr_needs_manual_review
- 当前 workspace：\\192.168.10.102\市场营销中心\品牌部\所有课程
- 输出目录：C:\Users\Cooler\Desktop\神经数字人课程解析交付包_neural_avatar_course_analysis_pack
- 是否 Git 仓库：no_git_standalone_workspace
- 是否读取上一轮逐字稿包：True
- AGENTS.md：AGENTS_not_found_continue_with_user_prompt
- README.md：README_not_found_continue_with_user_prompt
- 系统 Python：3.12.13 (main, Mar  3 2026, 15:01:35) [MSC v.1944 64 bit (AMD64)]
- 本地 ffmpeg：{'ok': True, 'first_line': 'ffmpeg version 8.1.2-essentials_build-www.gyan.dev Copyright (c) 2000-2026 the FFmpeg developers', 'returncode': 0}
- 本地 ffprobe：{'ok': True, 'first_line': 'ffprobe version 8.1.2-essentials_build-www.gyan.dev Copyright (c) 2007-2026 the FFmpeg developers', 'returncode': 0}
- OCR：pytesseract/PIL 不可用，已降级为关键帧索引 + 人工复核。
- OpenCV：不可用，动作识别降级为 chunk 级低置信度动作窗口。
- pandoc：不可用；本轮不生成 docx，保留 md/csv/json/jsonl。
- 桌面剩余空间：100.65 GB

## 输入规模

- 文件总数：2436
- 视频数量：1610
- 课件/图片素材数量：292
- 字幕/逐字稿/结构化文本数量：1
- 视频总时长：1546:59:35.615
- chunk 数量：19424
- 逐字稿时间轴窗口数：18630
- 三线对照行数：19424

## 边界确认

- 未修改原始课程目录。
- 未复制原始大视频/大音频进入交付包。
- 未 commit。
- 未 push。
- 未读取 secret/token/cookie/.env。
- 本轮只在桌面交付包目录写入过程文件和结果文件。
