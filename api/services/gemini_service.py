"""
Gemini Pro AI sağlayıcısının somut implementasyonu.

`BaseAIService` arayüzünü uygular. `MoodService` bu sınıfa doğrudan değil,
arayüze bağımlıdır (Dependency Inversion).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import google.generativeai as genai

from ..interfaces.base_ai_service import (
    AIServiceError,
    BaseAIService,
    MoodAnalysisResult,
    SongSuggestion,
)

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
Sen bir müzik küratörüsün. Kullanıcının yazdığı serbest metni okuyup:
1) Tek kelimelik ya da kısa (en fazla 2 kelime) bir ruh hali etiketi çıkar.
   Örnekler: "mutlu", "hüzünlü", "enerjik", "sakin", "öfkeli", "romantik",
   "melankolik", "nostaljik", "motive", "kaygılı".
2) {n} adet şarkı öner. Her öneri için Türkçe ve evrensel şarkılar karışık olabilir.
3) Cevabını SADECE aşağıdaki JSON şemasıyla, başka HİÇBİR metin olmadan dön:

{{
  "detected_mood": "<küçük harfle ruh hali>",
  "suggestions": [
    {{
      "title": "<şarkı adı>",
      "artist": "<sanatçı>",
      "reason": "<bu şarkının neden bu ruh haline uyduğunu 1 cümlede Türkçe açıkla>"
    }}
  ]
}}
"""


class GeminiService(BaseAIService):
    """Google Gemini Pro ile duygu analizi + müzik önerisi."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        if not api_key:
            raise AIServiceError(
                "GEMINI_API_KEY tanımlı değil. .env dosyanızı kontrol edin."
            )
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)
        self._model_name = model_name

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze_mood_and_recommend(
        self, user_text: str, max_suggestions: int = 6
    ) -> MoodAnalysisResult:
        prompt = self._build_prompt(user_text, max_suggestions)

        try:
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.8,
                },
            )
        except Exception as exc:  # SDK çeşitli istisnalar fırlatabilir
            logger.exception("Gemini API çağrısı başarısız oldu")
            raise AIServiceError("AI sağlayıcısına ulaşılamadı.") from exc

        raw_text = (response.text or "").strip()
        if not raw_text:
            raise AIServiceError("AI boş yanıt döndü.")

        payload = self._safe_json_loads(raw_text)
        return self._to_dto(payload)

    # ------------------------------------------------------------------ #
    # Yardımcılar (tek sorumluluk)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_prompt(user_text: str, n: int) -> str:
        cleaned = user_text.strip().replace("\u0000", "")
        return f"{_SYSTEM_PROMPT.format(n=n)}\n\nKullanıcı metni:\n\"\"\"\n{cleaned}\n\"\"\""

    @staticmethod
    def _safe_json_loads(raw: str) -> dict[str, Any]:
        """
        Model ara sıra ```json ... ``` fence'i içine sarmalayabiliyor; temizleyip
        güvenli şekilde parse ediyoruz.
        """
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Gemini JSON parse edilemedi: %s", raw[:300])
            raise AIServiceError("AI yanıtı geçerli bir JSON değil.") from exc

    @staticmethod
    def _to_dto(payload: dict[str, Any]) -> MoodAnalysisResult:
        mood = str(payload.get("detected_mood", "")).strip().lower()
        if not mood:
            raise AIServiceError("AI ruh hali etiketi üretemedi.")

        raw_suggestions = payload.get("suggestions") or []
        if not isinstance(raw_suggestions, list) or not raw_suggestions:
            raise AIServiceError("AI hiç şarkı önerisi üretemedi.")

        suggestions: list[SongSuggestion] = []
        for item in raw_suggestions:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            artist = str(item.get("artist", "")).strip()
            reason = str(item.get("reason", "")).strip()
            if title and artist:
                suggestions.append(
                    SongSuggestion(title=title, artist=artist, reason=reason)
                )

        if not suggestions:
            raise AIServiceError("AI geçerli formatta öneri üretemedi.")

        return MoodAnalysisResult(detected_mood=mood, suggestions=suggestions)
