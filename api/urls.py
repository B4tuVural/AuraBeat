"""AuraBeat API endpoint rotaları."""
from django.urls import path

from .views import (
    MoodAnalysisView,
    MoodDetailView,
    MoodHistoryView,
    MoodStatsView,
)

app_name = "api"

urlpatterns = [
    # POST: yeni mood analizi
    path("mood/analyze/", MoodAnalysisView.as_view(), name="mood-analyze"),
    # GET: sayfalı geçmiş
    path("mood/history/", MoodHistoryView.as_view(), name="mood-history"),
    # GET: dağılım istatistiği
    path("mood/stats/", MoodStatsView.as_view(), name="mood-stats"),
    # GET: tek girdi detay
    path("mood/<uuid:entry_id>/", MoodDetailView.as_view(), name="mood-detail"),
]
