# 01_A声音金标准与ASR报告_voice_gold_asr_report

`已确认`：A 来自 `final_30s_alibaba_fixed_template` 的原声抽取，不是 TTS。

| 字段 | 值 |
|---|---|
| A_source_video | `/Volumes/WD_BLACK/澜心社直播/outputs/alibaba_fixed_template_30s_video/final_30s_alibaba_fixed_template.mp4` |
| A_extracted_audio | `/Volumes/WD_BLACK/澜心社直播/outputs/audio_source_comparison_final30_vs_videoretalk/A_final30_audio_extracted.wav` |
| A_source_type | `reference_video_original_audio_extraction_not_tts` |
| A_reference_loudness_lufs | `-19.0` |
| A_reference_pause_density_minus30db_percent | `6.7` |
| ASR_model | `Alibaba DashScope paraformer-v1` |
| ASR_task_id | `47bbd7aa-c9c5-471d-bc86-5591e0363df0` |
| ASR_matches_target_product_ball_copy | `False` |

## A 音频 ASR 摘要

```text
女性要收紧很重要的。所以说他们这方面的手法，我上次去学习的时候，那个六十多岁的妈妈她都做了三十多年，专门就给人家生了孩子的女人做这个。所以这套手法老师学习完过后啊，如果说大家想学习的，我可以教给你们怎么在家里面去做好，有没有？如果想学手法的姐妹可以扣个响Q了，响过后我们让小助理单独给你教你怎么进怎么学习手法课啊。好，站着怎么练习。我们的内部直播有站着练习的。
女性要收紧很重要的。
女性
要
收紧
很
重要
的
所以说他们这方面的手法，我上次去学习的时候，那个六十多岁的妈妈她都做了三十多年，专门就给人家生了孩子的女人做这个。
所以说
他们
这方面
手法
我
上次
去
学习
时候
那个
六十多岁
妈妈
她
都
做了
三十多年
专门
就
给
人家
生
了
孩子
女人
做
这个
所以这套手法老师学习完过后啊，如果说大家想学习的，我可以教给你们怎么在家里面去做好，有没有？
所以
这套
老师
完
过后
啊
如果说
大家
想
我可以
教给
你们
怎么
在家
里面
做好
有没有
如果想学手法的姐妹可以扣个响Q了，响过后我们让小助理单独给你教你怎么进怎么学习手法课啊。
如果
学
姐妹
可以
扣
个
响
Q
我们
让
小
助理
单独
给你
教
你
进
课
好，站着怎么练习。
好
站
着
练习
我们的内部直播有站着练习的。
我们的
内部
直播
有
```

## 判断

`已确认`：A 的 ASR 内容是女性护理/手法课口播，不是小球产品文案。因此不能直接把 A 原音频作为本次 VideoRetalk 的 `audio_url`。
