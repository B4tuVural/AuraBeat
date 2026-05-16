"""
View katmanı — HTTP boyutu kabinetiyle çalışan ince katman.

SRP gereği bu view'lar SADECE:
* Request payload'ını alır → serializer'a verir,
* Servis/selector'ı çağırır,
* HTTP yanıtı (uygun status code ile) döner.

Hiçbir iş mantığı, hiçbir dış servis çağrısı, hiçbir DB mutation burada YOKTUR.
"""
from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .interfaces.base_ai_service import AIServiceError
from .selectors import MoodSelector
from .serializers import (
    MoodAnalysisRequestSerializer,
    MoodEntrySerializer,
)
from .services import (
    GeminiService,
    MoodService,
    NullMusicService,
    SpotifyService,
)
from .services.spotify_service import MusicServiceError

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Dependency Composition (Composition Root)
# --------------------------------------------------------------------------- #
def _build_mood_service() -> MoodService:
    """
    Composition root — bağımlılıkları burada bir araya getiriyoruz.

    View'a saf bir `MoodService` veriyoruz; view AI ya da Spotify hakkında
    HİÇBİR şey bilmiyor.
    """
    ai_service = GeminiService(
        api_key=settings.GEMINI_API_KEY,
        model_name=settings.GEMINI_MODEL_NAME,
    )

    music_service = NullMusicService()
    if settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET:
        try:
            music_service = SpotifyService(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
            )
        except MusicServiceError as exc:
            logger.warning("Spotify devre dışı, NullMusicService kullanılıyor: %s", exc)

    return MoodService(ai_service=ai_service, music_service=music_service)


# --------------------------------------------------------------------------- #
# POST /api/mood/analyze/
# --------------------------------------------------------------------------- #
class MoodAnalysisView(APIView):
    """Yeni bir ruh hali girdisi oluşturur ve önerileri döner."""

    def post(self, request: Request) -> Response:
        serializer = MoodAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = _build_mood_service()
            mood_entry = service.analyze_and_persist(
                user_text=serializer.validated_data["user_text"]
            )
        except AIServiceError as exc:
            logger.warning("AI servis hatası: %s", exc)
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Beklenmeyen sunucu hatası")
            return Response(
                {"detail": "Beklenmeyen bir hata oluştu."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        output = MoodEntrySerializer(mood_entry).data
        return Response(output, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------- #
# GET /api/mood/history/
# --------------------------------------------------------------------------- #
class MoodHistoryView(ListAPIView):
    """
    Geçmiş mood girdilerini sayfalı şekilde döner.

    Opsiyonel query param: `?mood=<etiket>` → ruh haline göre filtre.
    """

    serializer_class = MoodEntrySerializer

    def get_queryset(self):
        mood_filter = self.request.query_params.get("mood")
        if mood_filter:
            return MoodSelector.filter_by_mood(mood_filter)
        return MoodSelector.list_recent()


# --------------------------------------------------------------------------- #
# GET /api/mood/<uuid>/
# --------------------------------------------------------------------------- #
class MoodDetailView(APIView):
    """Tek bir mood girdisinin tam detayı."""

    def get(self, request: Request, entry_id) -> Response:
        entry = MoodSelector.get_by_id(entry_id)
        if entry is None:
            return Response(
                {"detail": "Mood girdisi bulunamadı."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MoodEntrySerializer(entry).data, status=status.HTTP_200_OK)


# --------------------------------------------------------------------------- #
# GET /api/mood/stats/
# --------------------------------------------------------------------------- #
class MoodStatsView(APIView):
    """Son 30 gün için ruh hali dağılımı."""

    def get(self, request: Request) -> Response:
        distribution = MoodSelector.mood_distribution(days=30)
        return Response(
            {"window_days": 30, "distribution": distribution},
            status=status.HTTP_200_OK,
        )
