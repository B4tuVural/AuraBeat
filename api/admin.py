"""Django Admin kayıtları — geliştirme/inceleme kolaylığı için."""
from django.contrib import admin

from .models import MoodEntry, SongRecommendation


class SongRecommendationInline(admin.TabularInline):
    model = SongRecommendation
    extra = 0
    readonly_fields = ("id",)
    fields = ("title", "artist", "reason", "album_cover_url")


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ("preview", "detected_mood", "created_at")
    list_filter = ("detected_mood", "created_at")
    search_fields = ("user_text", "detected_mood")
    readonly_fields = ("id", "created_at")
    inlines = [SongRecommendationInline]
    ordering = ("-created_at",)


@admin.register(SongRecommendation)
class SongRecommendationAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "mood_entry")
    list_filter = ("artist",)
    search_fields = ("title", "artist")
    readonly_fields = ("id",)
