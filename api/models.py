"""
AuraBeat - Domain Modelleri.

Bu modeller "Thin Models, Rich Domain" prensibine uyar:
- Sadece şema, kısıtlama ve saf türetilmiş özellikler (@property) burada bulunur.
- Hiçbir dış servis çağrısı, yan etki üreten metot veya iş mantığı bu dosyada yer almaz.
- Tüm iş mantığı `api/services/` katmanına izole edilmiştir.
"""
from __future__ import annotations

import uuid

from django.db import models


class MoodEntry(models.Model):
    """
    Kullanıcının sisteme sağladığı ham bağlamı ve analiz edilen ruh halini tutar.

    Domain: Duygu Analizi
    Aggregate Root: MoodEntry -> SongRecommendation (1..N)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Entity ID",
    )
    user_text = models.TextField(
        null=False,
        blank=False,
        verbose_name="Ham Kullanıcı Girdisi",
        help_text="Kullanıcının ruh halini tarif eden serbest metin.",
    )
    detected_mood = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Tespit Edilen Ruh Hali",
        help_text="Gemini tarafından çıkarılan ana ruh hali etiketi.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Oluşturulma Zamanı",
    )

    class Meta:
        verbose_name = "Mood Girdisi"
        verbose_name_plural = "Mood Girdileri"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["-created_at"], name="mood_recent_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.detected_mood} :: {self.preview}"

    # ---------------- Saf türetilmiş özellikler ----------------
    @property
    def preview(self) -> str:
        """
        Kullanıcı girdisinin güvenli, kısa önizlemesi (ilk 20 karakter).

        DİKKAT: Bu property yan etki üretmez ve ek sorgu tetiklemez.
        """
        text = (self.user_text or "").strip()
        if len(text) <= 20:
            return text
        return f"{text[:20]}…"


class SongRecommendation(models.Model):
    """
    Bir `MoodEntry` için AI tarafından üretilen bireysel şarkı önerisi.

    Bu, `MoodEntry` aggregate'inin alt varlığıdır (Child Entity).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Entity ID",
    )
    mood_entry = models.ForeignKey(
        MoodEntry,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="recommendations",  # spec gereği zorunlu
        verbose_name="Parent Mood Entry",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Şarkı Adı",
    )
    artist = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Sanatçı",
    )
    reason = models.TextField(
        null=False,
        verbose_name="AI Gerekçesi",
        help_text="Gemini'nin bu şarkıyı önerme sebebi.",
    )
    album_cover_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Albüm Kapağı URL",
    )

    class Meta:
        verbose_name = "Şarkı Önerisi"
        verbose_name_plural = "Şarkı Önerileri"
        ordering = ("title",)

    def __str__(self) -> str:
        return f"{self.title} — {self.artist}"
