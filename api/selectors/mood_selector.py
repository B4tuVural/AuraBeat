"""
Mood domain'i için okuma sorguları.

Bu sınıf yalnızca veri okur — asla mutation yapmaz. Karmaşık queryset'ler,
filtreler ve raporlama mantığı buraya izole edilir; bu sayede `models.py`
şişmez ve `views.py` veritabanı detaylarından habersiz kalır.
"""
from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, QuerySet
from django.utils import timezone

from ..models import MoodEntry


class MoodSelector:
    """Mood verilerini okumak için tek yetkili statik araç sınıfı."""

    # ------------------------------------------------------------------ #
    # Tekil
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_by_id(entry_id) -> MoodEntry | None:
        return (
            MoodEntry.objects.prefetch_related("recommendations")
            .filter(id=entry_id)
            .first()
        )

    # ------------------------------------------------------------------ #
    # Listeleme
    # ------------------------------------------------------------------ #
    @staticmethod
    def list_recent(limit: int | None = None) -> QuerySet[MoodEntry]:
        """En yeni mood girdileri (pagination için view tarafında dilimlenir)."""
        qs = MoodEntry.objects.prefetch_related("recommendations").order_by(
            "-created_at"
        )
        if limit is not None:
            return qs[:limit]
        return qs

    @staticmethod
    def filter_by_mood(mood: str) -> QuerySet[MoodEntry]:
        """Belirli bir ruh haline ait tüm girdiler."""
        return (
            MoodEntry.objects.prefetch_related("recommendations")
            .filter(detected_mood__iexact=mood.strip())
            .order_by("-created_at")
        )

    # ------------------------------------------------------------------ #
    # İstatistik
    # ------------------------------------------------------------------ #
    @staticmethod
    def mood_distribution(days: int = 30) -> list[dict[str, int]]:
        """
        Son N gün için ruh hali dağılımı — basit "kişisel istatistik" widget'ı için.
        """
        since = timezone.now() - timedelta(days=days)
        return list(
            MoodEntry.objects.filter(created_at__gte=since)
            .values("detected_mood")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
