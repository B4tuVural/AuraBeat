"""
AI sağlayıcısı için soyut arayüz (DIP).

Üst seviye `MoodService`, somut bir AI istemcisi (Gemini, OpenAI, vb.) yerine
bu sözleşmeye bağımlıdır. Bu sayede sağlayıcı değişimi maliyetsiz olur.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SongSuggestion:
    """AI'dan gelen tek bir şarkı önerisinin saf veri taşıyıcısı (DTO)."""

    title: str
    artist: str
    reason: str


@dataclass(frozen=True)
class MoodAnalysisResult:
    """AI duygu analizi ve öneri çıktısının saf veri taşıyıcısı (DTO)."""

    detected_mood: str
    suggestions: list[SongSuggestion]


class BaseAIService(ABC):
    """
    Tüm AI sağlayıcıları bu sözleşmeyi uygular.

    Open/Closed: Yeni sağlayıcı eklemek için bu sınıftan miras al, içeri
    enjekte et. `MoodService` koduna asla dokunma.
    """

    @abstractmethod
    def analyze_mood_and_recommend(
        self, user_text: str, max_suggestions: int = 6
    ) -> MoodAnalysisResult:
        """
        Verilen ham metni analiz et ve şarkı önerileri döndür.

        Args:
            user_text: Kullanıcının ruh halini tarif eden serbest metin.
            max_suggestions: Geri döndürülecek en fazla öneri sayısı.

        Returns:
            Tespit edilen ruh hali etiketi ve önerilerin listesi.

        Raises:
            AIServiceError: Sağlayıcıya ulaşılamadığında veya çıktı geçersiz olduğunda.
        """
        raise NotImplementedError


class AIServiceError(RuntimeError):
    """AI sağlayıcısı tarafında oluşan tüm hatalar için tek bir alan tipi."""
