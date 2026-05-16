"""
Müzik sağlayıcısı için soyut arayüz (DIP).

`MoodService`, albüm kapağı / track metadata zenginleştirmesi için bu
sözleşmeye bağımlıdır. Spotify, Deezer, Apple Music gibi sağlayıcılar
bu arayüzü uygulayarak sisteme dahil edilir.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TrackMetadata:
    """Müzik sağlayıcısından dönen track meta verisi DTO."""

    title: str
    artist: str
    album_cover_url: str | None = None
    external_url: str | None = None


class BaseMusicService(ABC):
    """
    Müzik sağlayıcılarının uyduğu sözleşme.

    Bu katman tamamen opsiyoneldir; uygulanmazsa öneriler albüm kapağı
    olmadan döner (frontend zaten bunu nazikçe handle eder).
    """

    @abstractmethod
    def enrich_track(self, title: str, artist: str) -> TrackMetadata:
        """
        Verilen şarkı/sanatçı çifti için meta verileri zenginleştirir.

        Args:
            title: Şarkı adı.
            artist: Sanatçı adı.

        Returns:
            Albüm kapağı, harici link vb. ile zenginleştirilmiş metadata.
            Sağlayıcı bulamazsa boş alanlarla TrackMetadata döner.
        """
        raise NotImplementedError


class MusicServiceError(RuntimeError):
    """Müzik sağlayıcısı tarafında oluşan tüm hatalar için tek tip."""
