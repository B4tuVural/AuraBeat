"""
Soyut arayüzler (Abstract Base Classes) — SOLID Dependency Inversion için.

Bu modül, üst seviye iş mantığının (services) somut dış sağlayıcılara
(Gemini, Spotify, vb.) doğrudan bağımlı olmasını engeller.
"""
from .base_ai_service import BaseAIService, MoodAnalysisResult, SongSuggestion
from .base_music_service import BaseMusicService, TrackMetadata

__all__ = [
    "BaseAIService",
    "BaseMusicService",
    "MoodAnalysisResult",
    "SongSuggestion",
    "TrackMetadata",
]
