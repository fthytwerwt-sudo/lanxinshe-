# 后台运行与续跑说明

本交付包由桌面工作区内的本地流水线生成，原始课程目录只读，不会修改、移动、删除原素材。

## 当前工作区

- 桌面工作区：`C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152`
- 交付包目录：`C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack`
- 后台进度文件：`data\transcription_run_state.json`
- 中区间 worker 进度文件：`data\transcription_run_state_worker_mid.json`
- 高区间 worker 进度文件：`data\transcription_run_state_worker_high.json`
- 状态表：`data\transcription_status.csv`
- 后台日志：`_logs\background_full_transcription.log`

## 当前后台并行策略

当前为了加快全量转写，已启用五路本地 worker：

- 主线 worker：从低 lesson_id 顺序续跑。
- 低中区间 worker：处理 `L0250-L0499`。
- 中区间 worker：处理 `L0500-L0899`。
- 高区间 worker：处理 `L0900-L1200`。
- 超高区间 worker：处理 `L1201-L1610`。

辅助 worker 只写每节课自己的逐字稿与状态 JSON，不直接写全局汇总文件；全局 `csv/md/json/docx/zip` 由重建脚本统一刷新。

后台还会执行安全重复素材复用：

- 规则：媒体类型一致、规范化文件名一致、时长四舍五入到 0.1 秒一致。
- 只复用已完成逐字稿到未处理素材。
- 正在 running 或存在 lock 的素材不会被复用覆盖。
- 复用报告：`_logs\safe_duplicate_reuse_report.md` 和 `_logs\safe_duplicate_reuse_report.json`。

## 查看后台是否还在运行

```powershell
Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -like '*课程逐字稿解析工作区_所有课程_20260630_170152*' -and
  ($_.CommandLine -like '*run_full_background.ps1*' -or $_.CommandLine -like '*run_transcription_pipeline_persistent.py*' -or $_.CommandLine -like '*run_watchdog.ps1*')
} | Select-Object ProcessId,ProcessName,CommandLine
```

## 查看当前进度

```powershell
Get-Content -LiteralPath 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack\data\transcription_run_state.json' -Raw -Encoding UTF8
Get-Content -LiteralPath 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack\data\transcription_run_state_worker_lowmid.json' -Raw -Encoding UTF8
Get-Content -LiteralPath 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack\data\transcription_run_state_worker_mid.json' -Raw -Encoding UTF8
Get-Content -LiteralPath 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack\data\transcription_run_state_worker_high.json' -Raw -Encoding UTF8
Get-Content -LiteralPath 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack\data\transcription_run_state_worker_veryhigh.json' -Raw -Encoding UTF8
Import-Csv -LiteralPath 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\课程逐字稿解析交付包_course_transcript_analysis_pack\data\transcription_status.csv' | Group-Object status | Select-Object Name,Count
```

## 重新启动后台续跑

如果后台进程不存在，可以执行下面命令续跑。已完成的素材会自动跳过，失败或未完成的素材会继续处理。

```powershell
Start-Process -FilePath 'powershell.exe' -ArgumentList @(
  '-NoProfile',
  '-ExecutionPolicy',
  'Bypass',
  '-File',
  'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152\_scripts\run_full_background.ps1'
) -WindowStyle Hidden
```

如果需要手动恢复辅助 worker，可分别执行：

```powershell
$work = 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152'
$pack = Join-Path $work '课程逐字稿解析交付包_course_transcript_analysis_pack'
$py = Join-Path $work '.venv_course_transcript\Scripts\python.exe'
$script = Join-Path $work '_scripts\run_transcription_pipeline_persistent.py'

Start-Process -FilePath $py -ArgumentList @(
  $script, '--model', 'small', '--device', 'cuda', '--compute-type', 'float16',
  '--language', 'zh', '--beam-size', '1', '--vad-filter',
  '--lesson-start', '250', '--lesson-end', '499',
  '--worker-id', 'worker_lowmid', '--no-global-refresh'
) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $pack '_logs\worker_lowmid_stdout.log') -RedirectStandardError (Join-Path $pack '_logs\worker_lowmid_stderr.log')

Start-Process -FilePath $py -ArgumentList @(
  $script, '--model', 'small', '--device', 'cuda', '--compute-type', 'float16',
  '--language', 'zh', '--beam-size', '1', '--vad-filter',
  '--lesson-start', '500', '--lesson-end', '899',
  '--worker-id', 'worker_mid', '--no-global-refresh'
) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $pack '_logs\worker_mid_stdout.log') -RedirectStandardError (Join-Path $pack '_logs\worker_mid_stderr.log')

Start-Process -FilePath $py -ArgumentList @(
  $script, '--model', 'small', '--device', 'cuda', '--compute-type', 'float16',
  '--language', 'zh', '--beam-size', '1', '--vad-filter',
  '--lesson-start', '900', '--lesson-end', '1200',
  '--worker-id', 'worker_high', '--no-global-refresh'
) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $pack '_logs\worker_high_stdout.log') -RedirectStandardError (Join-Path $pack '_logs\worker_high_stderr.log')

Start-Process -FilePath $py -ArgumentList @(
  $script, '--model', 'small', '--device', 'cuda', '--compute-type', 'float16',
  '--language', 'zh', '--beam-size', '1', '--vad-filter',
  '--lesson-start', '1201', '--lesson-end', '1610',
  '--worker-id', 'worker_veryhigh', '--no-global-refresh'
) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $pack '_logs\worker_veryhigh_stdout.log') -RedirectStandardError (Join-Path $pack '_logs\worker_veryhigh_stderr.log')
```

## 手动刷新阶段性交付包

后台跑完前，也可以手动刷新阶段包。刷新不会读取正在写入的半成品，只会合并状态为 completed / completed_text / completed_reused 的素材。

```powershell
$work = 'C:\Users\Cooler\Desktop\课程逐字稿解析工作区_所有课程_20260630_170152'
$py = Join-Path $work '.venv_course_transcript\Scripts\python.exe'
& $py (Join-Path $work '_scripts\run_transcription_pipeline.py') --rebuild-only --vad-filter
& $py (Join-Path $work '_scripts\build_analysis_pack.py')
```

## 注意

- 不要删除 `_cache`，后台运行时会临时放置音频切出文件。
- 不要复制 `_cache` 到其他项目。
- 不要移动或重命名原始课程素材。
- 最终判断是否全量完成，以 `data\transcription_status.csv` 中没有 `pending_asr` 为准。
