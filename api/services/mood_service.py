"""
Mood orkestrasyon servisi — SRP'ye uyan ince katman.

`MoodService` tek bir iş yapar:
1. Ham metni al.
2. AI sağlayıcısından mood + öneri al.
3. (opsiyonel) Müzik sağlayıcısından albüm kapağı zenginleştir.
4. MoodEntry + N SongRecommendation'ı tek transaction'da kaydet.
5. Sonucu döndür.

Dış servisler constructor üzerinden enjekte edilir — bu sayede testlerde
arayüzlerin mock implementasyonu geçilebilir.
"""
from __future__ import annotations

import logging

from django.db import transaction

from ..interfaces.base_ai_service import BaseAIService
from ..interfaces.base_music_service import BaseMusicService
from ..models import MoodEntry, SongRecommendation

logger = logging.getLogger(__name__)


class MoodService:
    """Mood analizi + öneri kalıcılaştırma için tek yetkili iş mantığı."""

    def __init__(
        self,
        ai_service: BaseAIService,
        music_service: BaseMusicService,
        max_suggestions: int = 6,
    ) -> None:
        # Constructor enjeksiyonu — arayüzlere bağımlıyız, somutlara değil.
        self._ai = ai_service
        self._music = music_service
        self._max_suggestions = max_suggestions

    # ------------------------------------------------------------------ #
    # Public Use-Case
    # ------------------------------------------------------------------ #
    @transaction.atomic
    def analyze_and_persist(self, user_text: str) -> MoodEntry:
        """
        Tam akış: AI çağrısı + (opsiyonel) zenginleştirme + DB yazma.

        Returns:
            Önerilerle birlikte kalıcılaştırılmış `MoodEntry`.
        """
        cleaned_text = self._sanitize_input(user_text)

        ai_result = self._ai.analyze_mood_and_recommend(
            user_text=cleaned_text,
            max_suggestions=self._max_suggestions,
        )

        mood_entry = MoodEntry.objects.create(
            user_text=cleaned_text,
            detected_mood=ai_result.detected_mood,
        )

        SongRecommendation.objects.bulk_create(
            [
                SongRecommendation(
                    mood_entry=mood_entry,
                    title=suggestion.title,
                    artist=suggestion.artist,
                    reason=suggestion.reason,
                    album_cover_url=self._safe_cover_lookup(
                        suggestion.title, suggestion.artist
                    ),
                )
                for suggestion in ai_result.suggestions
            ]
        )
        return mood_entry

    # ------------------------------------------------------------------ #
    # Yardımcılar
    # ------------------------------------------------------------------ #
    @staticmethod
    def _sanitize_input(text: str) -> str:
        cleaned = (text or "").strip().replace("\u0000", "")
        if not cleaned:
            raise ValueError("Kullanıcı metni boş olamaz.")
        return cleaned

    def _safe_cover_lookup(self, title: str, artist: str) -> str | None:
        """
        Müzik servisinin başarısızlığı tüm akışı düşürmemeli.
        """
        try:
            metadata = self._music.enrich_track(title=title, artist=artist)
            return metadata.album_cover_url
        except Exception as exc:  # noqa: BLE001 — bilinçli geniş yakalama
            logger.warning("Müzik zenginleştirme başarısız (%s — %s): %s",
                           title, artist, exc)
            return None
