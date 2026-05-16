"""
DRF Serializer'lar — sadece doğrulama ve şekillendirme yapar.

SRP gereği bu dosya:
* Asla harici servis çağırmaz.
* Asla DB mutation tetiklemez (servisin işi).
* Asla karmaşık iş mantığı barındırmaz.
"""
from __future__ import annotations

from rest_framework import serializers

from .models import MoodEntry, SongRecommendation


# --------------------------------------------------------------------------- #
# Girdi: Kullanıcıdan gelen ham metin
# --------------------------------------------------------------------------- #
class MoodAnalysisRequestSerializer(serializers.Serializer):
    """`/api/mood/analyze/` endpoint'inin payload doğrulaması."""

    user_text = serializers.CharField(
        min_length=3,
        max_length=2000,
        trim_whitespace=True,
        error_messages={
            "blank": "Lütfen ruh halini birkaç kelimeyle anlat.",
            "min_length": "En az 3 karakter girmelisin.",
            "max_length": "En fazla 2000 karakter girebilirsin.",
        },
    )

    def validate_user_text(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Metin boş olamaz.")
        return cleaned


# --------------------------------------------------------------------------- #
# Çıktı: API'den dönen yapı
# --------------------------------------------------------------------------- #
class SongRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongRecommendation
        fields = ("id", "title", "artist", "reason", "album_cover_url")
        read_only_fields = fields


class MoodEntrySerializer(serializers.ModelSerializer):
    """Tam `MoodEntry` yanıtı — iç içe önerilerle birlikte."""

    recommendations = SongRecommendationSerializer(many=True, read_only=True)
    preview = serializers.CharField(read_only=True)

    class Meta:
        model = MoodEntry
        fields = (
            "id",
            "user_text",
            "preview",
            "detected_mood",
            "created_at",
            "recommendations",
        )
        read_only_fields = fields
