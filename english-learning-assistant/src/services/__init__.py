"""服务模块初始化"""

from .translation import translation_service, TranslationService
from .writing import writing_service, WritingService
from .speaking import speaking_service, SpeakingService
from .multimodal import multimodal_service, MultimodalService

__all__ = [
    "translation_service", "TranslationService",
    "writing_service", "WritingService",
    "speaking_service", "SpeakingService",
    "multimodal_service", "MultimodalService"
]
