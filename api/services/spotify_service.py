"""
Müzik sağlayıcısı somut implementasyonları.

* `SpotifyService`: Spotify API ile track arar, albüm kapağı/URL döner.
* `NullMusicService`: Hiçbir dış servis yapılandırılmadığında devreye giren
  "no-op" implementasyon (Null Object Pattern). Bu sayede tüketici kod
  asla `if music_service is None` kontrolü yapmaz.
"""
from __future__ import annotations

import logging

from ..interfaces.base_music_service import (
    BaseMusicService,
    MusicServiceError,
    TrackMetadata,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Null Object — Spotify creds yokken kullanılır
# --------------------------------------------------------------------------- #
class NullMusicService(BaseMusicService):
    """Hiçbir şey yapmayan, sessiz fallback."""

    def enrich_track(self, title: str, artist: str) -> TrackMetadata:
        return TrackMetadata(title=title, artist=artist)


# --------------------------------------------------------------------------- #
# Spotify
# --------------------------------------------------------------------------- #
class SpotifyService(BaseMusicService):
    """
    Spotify Web API ile track arar, en yüksek çözünürlüklü albüm kapağı URL'sini
    ve track'in Spotify üzerindeki açılma linkini döner.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        if not (client_id and client_secret):
            raise MusicServiceError(
                "SPOTIFY_CLIENT_ID ve SPOTIFY_CLIENT_SECRET zorunlu."
            )
        # Lazy import: paket yüklü değilse uygulama çökmesin
        try:
            from spotipy import Spotify
            from spotipy.oauth2 import SpotifyClientCredentials
        except ImportError as exc:  # pragma: no cover
            raise MusicServiceError("spotipy paketi yüklü değil.") from exc

        auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self._client = Spotify(auth_manager=auth)

    def enrich_track(self, title: str, artist: str) -> TrackMetadata:
        query = f'track:"{title}" artist:"{artist}"'
        try:
            results = self._client.search(q=query, type="track", limit=1)
        except Exception as exc:
            logger.warning("Spotify araması başarısız: %s — %s", query, exc)
            return TrackMetadata(title=title, artist=artist)

        items = (results or {}).get("tracks", {}).get("items", [])
        if not items:
            return TrackMetadata(title=title, artist=artist)

        track = items[0]
        album = track.get("album", {}) or {}
        images = album.get("images") or []
        cover_url = images[0]["url"] if images else None
        external_url = (track.get("external_urls") or {}).get("spotify")

        return TrackMetadata(
            title=title,
            artist=artist,
            album_cover_url=cover_url,
            external_url=external_url,
        )
