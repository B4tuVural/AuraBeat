/**
 * ui.js — Sadece DOM ve görsel sunumdan SORUMLU modül.
 *
 * Bu dosya:
 *  - Asla API çağrısı yapmaz.
 *  - Asla event dinleyici eklemez.
 *  - Sadece "şu state'le bu HTML'i yaz" işini görür.
 */

/* -------------------------------------------------------------------------- */
/* Element handle'ları — tek noktadan, sıkı eşleşme için                      */
/* -------------------------------------------------------------------------- */
export const els = {
    body:           document.documentElement,
    form:           document.getElementById("mood-form"),
    input:          document.getElementById("mood-input"),
    submit:         document.getElementById("mood-submit"),
    counter:        document.getElementById("mood-counter"),
    error:          document.getElementById("mood-error"),
    loader:         document.getElementById("loader"),
    results:        document.getElementById("results"),
    moodTag:        document.getElementById("detected-mood"),
    moodContext:    document.getElementById("mood-context"),
    cards:          document.getElementById("cards-container"),
    historyList:    document.getElementById("history-list"),
    refreshBtn:     document.getElementById("refresh-history"),
};

/* -------------------------------------------------------------------------- */
/* Mood → UI tema senkronizasyonu                                             */
/* -------------------------------------------------------------------------- */
export function applyMoodTheme(mood) {
    const slug = (mood || "neutral").toString().trim().toLowerCase();
    els.body.setAttribute("data-mood", slug);
}

/* -------------------------------------------------------------------------- */
/* Form durumları                                                             */
/* -------------------------------------------------------------------------- */
export function setSubmitting(isSubmitting) {
    els.submit.disabled = isSubmitting;
    els.input.disabled = isSubmitting;
    els.submit.querySelector(".aura-btn-label").textContent =
        isSubmitting ? "Analiz ediliyor…" : "Şarkımı Bul";
}

export function showError(message) {
    els.error.textContent = message || "";
}

export function clearError() {
    showError("");
}

export function updateCounter(value) {
    const len = (value || "").length;
    els.counter.textContent = `${len} / 2000`;
}

/* -------------------------------------------------------------------------- */
/* Loader                                                                     */
/* -------------------------------------------------------------------------- */
export function showLoader() {
    els.loader.hidden = false;
    els.results.hidden = true;
}

export function hideLoader() {
    els.loader.hidden = true;
}

/* -------------------------------------------------------------------------- */
/* Sonuç render                                                               */
/* -------------------------------------------------------------------------- */
export function renderResults(moodEntry) {
    els.results.hidden = false;
    els.moodTag.textContent = moodEntry.detected_mood;
    els.moodContext.textContent = moodEntry.preview
        ? `“${moodEntry.preview}”`
        : "";

    els.cards.replaceChildren(
        ...moodEntry.recommendations.map((rec, index) => buildCard(rec, index))
    );

    // sonuçları görünür kıl
    els.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildCard(rec, index) {
    const col = document.createElement("div");
    col.className = "col-12 col-sm-6 col-lg-4";

    const article = document.createElement("article");
    article.className = "aura-card";
    article.style.animationDelay = `${index * 90}ms`;

    /* cover */
    const cover = document.createElement("div");
    cover.className = "aura-card-cover";
    if (rec.album_cover_url) {
        const img = document.createElement("img");
        img.src = rec.album_cover_url;
        img.alt = `${rec.title} albüm kapağı`;
        img.loading = "lazy";
        img.referrerPolicy = "no-referrer";
        cover.appendChild(img);
    } else {
        // güzel bir placeholder: sanatçının baş harfi
        cover.textContent = (rec.artist || "♪").trim().charAt(0).toUpperCase();
    }
    const indexLabel = document.createElement("span");
    indexLabel.className = "aura-card-index";
    indexLabel.textContent = String(index + 1).padStart(2, "0");
    cover.appendChild(indexLabel);
    article.appendChild(cover);

    /* başlık */
    const h3 = document.createElement("h3");
    h3.className = "aura-card-title";
    h3.textContent = rec.title;
    article.appendChild(h3);

    const artist = document.createElement("p");
    artist.className = "aura-card-artist";
    artist.textContent = rec.artist;
    article.appendChild(artist);

    /* reason */
    const reason = document.createElement("p");
    reason.className = "aura-card-reason";
    reason.textContent = rec.reason || "—";
    article.appendChild(reason);

    /* dinle butonu — Spotify/Apple Music olmadan generik bir arama linki */
    const action = document.createElement("a");
    action.className = "aura-card-action";
    action.target = "_blank";
    action.rel = "noopener noreferrer";
    action.href = buildSearchLink(rec.title, rec.artist);
    action.innerHTML = `Dinle <i class="bi bi-arrow-up-right"></i>`;
    article.appendChild(action);

    col.appendChild(article);
    return col;
}

function buildSearchLink(title, artist) {
    const q = encodeURIComponent(`${title} ${artist}`);
    return `https://open.spotify.com/search/${q}`;
}

/* -------------------------------------------------------------------------- */
/* Geçmiş listesi                                                             */
/* -------------------------------------------------------------------------- */
export function renderHistory(items) {
    if (!items || items.length === 0) {
        els.historyList.innerHTML =
            `<p class="aura-history-empty">Henüz analiz yok. İlkini sen yaz.</p>`;
        return;
    }

    els.historyList.replaceChildren(
        ...items.map((entry) => buildHistoryRow(entry))
    );
}

function buildHistoryRow(entry) {
    const row = document.createElement("div");
    row.className = "aura-history-item";
    row.tabIndex = 0;
    row.dataset.moodEntryId = entry.id;

    const mood = document.createElement("span");
    mood.className = "aura-history-mood";
    mood.textContent = entry.detected_mood;

    const preview = document.createElement("span");
    preview.className = "aura-history-preview";
    preview.textContent = entry.preview || entry.user_text;

    const time = document.createElement("span");
    time.className = "aura-history-time";
    time.textContent = formatRelativeTime(entry.created_at);

    row.append(mood, preview, time);
    return row;
}

function formatRelativeTime(isoString) {
    const date = new Date(isoString);
    const diffSec = Math.round((Date.now() - date.getTime()) / 1000);

    if (diffSec < 60)     return "az önce";
    if (diffSec < 3600)   return `${Math.floor(diffSec / 60)} dk önce`;
    if (diffSec < 86400)  return `${Math.floor(diffSec / 3600)} sa önce`;
    if (diffSec < 604800) return `${Math.floor(diffSec / 86400)} gün önce`;

    return date.toLocaleDateString("tr-TR", {
        day: "2-digit", month: "short", year: "numeric",
    });
}
