/**
 * api.js — Backend ile haberleşmeden SORUMLU tek modül.
 *
 * SoC (Separation of Concerns) gereği bu dosyada DOM güncellemesi,
 * event dinleyici ya da kullanıcı feedback'i bulunmaz.
 */

const DEFAULT_BASE = "http://localhost:8000/api";

/**
 * `<meta name="api-base-url" content="...">` override etmek isteyenler için
 * basit bir esneklik mekanizması. Yoksa default localhost adresi kullanılır.
 */
function resolveBaseUrl() {
    const meta = document.querySelector('meta[name="api-base-url"]');
    return (meta && meta.content) || DEFAULT_BASE;
}

const BASE_URL = resolveBaseUrl();

/**
 * Tek tip hata sınıfı — UI katmanı tek tip hatayla konuşur.
 */
export class ApiError extends Error {
    constructor(message, { status = 0, payload = null } = {}) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.payload = payload;
    }
}

async function request(path, { method = "GET", body = null, signal = null } = {}) {
    let response;
    try {
        response = await fetch(`${BASE_URL}${path}`, {
            method,
            headers: { "Content-Type": "application/json", "Accept": "application/json" },
            body: body ? JSON.stringify(body) : null,
            signal,
        });
    } catch (networkErr) {
        throw new ApiError(
            "Sunucuya ulaşılamıyor. İnternet bağlantını kontrol et.",
            { status: 0 }
        );
    }

    let payload = null;
    try { payload = await response.json(); } catch (_) { /* boş yanıt olabilir */ }

    if (!response.ok) {
        const detail = (payload && (payload.detail || payload.user_text?.[0])) || null;
        throw new ApiError(
            detail || "Beklenmedik bir hata oluştu.",
            { status: response.status, payload }
        );
    }

    return payload;
}

/* -------------------------------------------------------------------------- */
/* Public API                                                                 */
/* -------------------------------------------------------------------------- */

export function analyzeMood(userText, { signal } = {}) {
    return request("/mood/analyze/", {
        method: "POST",
        body: { user_text: userText },
        signal,
    });
}

export function fetchHistory({ page = 1, signal } = {}) {
    return request(`/mood/history/?page=${page}`, { signal });
}

export function fetchMoodById(entryId, { signal } = {}) {
    return request(`/mood/${entryId}/`, { signal });
}
