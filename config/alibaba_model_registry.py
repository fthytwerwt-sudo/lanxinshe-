"""Alibaba model registry for the digital human live project.

Candidate names are not connectivity claims. Probe reports must use API
results as the source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_COMPATIBLE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_RERANK_BASE_URL = "https://dashscope.aliyuncs.com/compatible-api/v1"
DEFAULT_DASHSCOPE_API_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"


@dataclass(frozen=True)
class ModelCandidate:
    """A model candidate plus its project role."""

    name: str
    purpose: str
    input_type: str
    cost_guard: str


# 文本模型：用于直播评论判断、回复生成、规则解释、结构化输出。
TEXT_MODEL_CANDIDATES = [
    "qwen-plus",
    "qwen-max",
    "qwen-turbo",
]

# 视觉/视频理解模型：用于直播录屏、数字人样片、参考视频分析。
VISION_VIDEO_MODEL_CANDIDATES = [
    "qwen-vl-max",
    "qwen-vl-plus",
    "qwen3-vl-plus",
    "qwen3-vl-flash",
    "qwen3-vl-235b-a22b-instruct",
    "qwen2.5-vl-72b-instruct",
    "qwen2.5-vl-32b-instruct",
    "qwen2.5-vl-7b-instruct",
]

# 全模态模型：用于音频 + 视频 + 文本综合理解，账号可用时测试。
OMNI_MODEL_CANDIDATES = [
    "qwen2.5-omni-7b",
    "qwen3.5-omni-plus",
]

# 向量模型：用于课程资料、价格权益、退款规则、禁说规则的知识检索。
EMBEDDING_MODEL_CANDIDATES = [
    "text-embedding-v4",
    "text-embedding-v3",
]

# 重排模型：用于召回后的规则资料、课程资料、权益资料排序。
RERANK_MODEL_CANDIDATES = [
    "qwen3-rerank",
    "gte-rerank-v2",
]

# 视频生成模型：用于后续样片生成，不用于视频分析。
WAN_VIDEO_GENERATION_CANDIDATES = [
    "wan2.2-s2v",
]

# 视频口型替换模型：用于真人视频底片 + 新音频的口型替换，不是单图数字人生成，也不是实时直播。
VIDEORETALK_MODEL_CANDIDATES = [
    "videoretalk",
]

VIDEORETALK_SUBMIT_ENDPOINT = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/"
)
VIDEORETALK_TASK_ENDPOINT_TEMPLATE = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

VIDEORETALK_API_SPEC = {
    "category": "avatar_video_retalk",
    "subcategory": "video_lip_sync",
    "model": "videoretalk",
    "provider": "alibaba_dashscope",
    "api_type": "async_http",
    "submit_endpoint": VIDEORETALK_SUBMIT_ENDPOINT,
    "task_endpoint": VIDEORETALK_TASK_ENDPOINT_TEMPLATE,
    "inputs": {
        "video_url": "required_public_http_or_https_url",
        "audio_url": "required_public_http_or_https_url",
        "ref_image_url": "optional_public_http_or_https_url",
    },
    "parameters": {
        "video_extension": "optional_boolean",
        "query_face_threshold": "optional_integer_120_to_200",
    },
    "cost_guard": "default_skip_generation_unless_ALLOW_VIDEORETALK_GENERATION_PROBE_true",
    "project_note": "VideoRetalk 是视频口型替换，不是单图数字人生成，也不是实时直播。",
}


MODEL_CATALOG = {
    "text": [
        ModelCandidate(
            name=model,
            purpose="直播评论判断、回复生成、规则解释、结构化输出",
            input_type="text",
            cost_guard="safe_minimal_call",
        )
        for model in TEXT_MODEL_CANDIDATES
    ],
    "vision_video": [
        ModelCandidate(
            name=model,
            purpose="直播录屏、数字人样片、参考视频的视觉/视频理解",
            input_type="image_or_video",
            cost_guard="safe_short_clip_or_frame",
        )
        for model in VISION_VIDEO_MODEL_CANDIDATES
    ],
    "omni": [
        ModelCandidate(
            name=model,
            purpose="音频 + 视频 + 文本综合理解候选",
            input_type="text_audio_video",
            cost_guard="safe_minimal_multimodal_call",
        )
        for model in OMNI_MODEL_CANDIDATES
    ],
    "embedding": [
        ModelCandidate(
            name=model,
            purpose="课程资料、价格权益、退款规则、禁说规则的语义检索",
            input_type="text",
            cost_guard="safe_single_embedding",
        )
        for model in EMBEDDING_MODEL_CANDIDATES
    ],
    "rerank": [
        ModelCandidate(
            name=model,
            purpose="召回结果重排，提升知识库命中顺序",
            input_type="query_and_documents",
            cost_guard="safe_small_document_set",
        )
        for model in RERANK_MODEL_CANDIDATES
    ],
    "wan_s2v": [
        ModelCandidate(
            name=model,
            purpose="15 秒数字人口型样片生成候选，不用于视频分析",
            input_type="image_url_and_audio_url",
            cost_guard="generation_disabled_without_ALLOW_WAN_GENERATION_PROBE",
        )
        for model in WAN_VIDEO_GENERATION_CANDIDATES
    ],
    "avatar_video_retalk": [
        ModelCandidate(
            name=model,
            purpose="真人视频底片 + 新音频的原生口型替换；不是单图数字人生成，也不是实时直播",
            input_type="public_video_url_and_public_audio_url",
            cost_guard="generation_disabled_without_ALLOW_VIDEORETALK_GENERATION_PROBE",
        )
        for model in VIDEORETALK_MODEL_CANDIDATES
    ],
}


REQUIRED_ENV_KEYS = [
    "DASHSCOPE_API_KEY",
]

OSS_ENV_KEYS = [
    "ALIBABA_CLOUD_ACCESS_KEY_ID",
    "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
    "ALIBABA_OSS_ENDPOINT",
    "ALIBABA_OSS_BUCKET",
    "ALIBABA_OSS_OBJECT_PREFIX",
    "ALIBABA_OSS_SIGNED_URL_EXPIRES",
    "ALIYUN_OSS_BUCKET",
    "ALIYUN_OSS_ENDPOINT",
    "ALIYUN_OSS_REGION",
]

SAFETY_SWITCH_ENV_KEYS = [
    "ALLOW_ALIBABA_MODEL_TEST",
    "ALLOW_QWEN_CHAT_TEST",
    "ALLOW_WAN_GENERATION_PROBE",
    "ALLOW_VIDEORETALK_GENERATION_PROBE",
]
