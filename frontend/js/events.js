/**
 * events.js — Sadece event listener kayıtlarından SORUMLU modül.
 *
 * Bu modül `api.js` ve `ui.js`'i birbirine bağlayan tek noktadır.
 * Spec gereği "API çağrıları, UI güncellemeleri ve Event dinleyicileri ayrı
 * dosyalardadır" prensibine birebir uyar.
 */
import { analyzeMood, fetchHistory, fetchMoodById, ApiError } from "./api.js";
import {
    els,
    applyMoodTheme,
    setSubmitting,
    showError,
    clearError,
    updateCounter,
    showLoader,
    hideLoader,
    renderResults,
    renderHistory,
} from "./ui.js";

/* -------------------------------------------------------------------------- */
/* Form submit                                                                */
/* -------------------------------------------------------------------------- */
function attachFormHandler() {
    els.form.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearError();

        const userText = (els.input.value || "").trim();
        if (userText.length < 3) {
            showError("Lütfen en az 3 karakter yaz.");
            els.input.focus();
            return;
        }

        setSubmitting(true);
        showLoader();

        try {
            const moodEntry = await analyzeMood(userText);
            applyMoodTheme(moodEntry.detected_mood);
            hideLoader();
            renderResults(moodEntry);
            await refreshHistorySilently();
        } catch (err) {
            hideLoader();
            const msg = (err instanceof ApiError)
                ? err.message
                : "Beklenmedik bir hata oluştu. Lütfen tekrar dene.";
            showError(msg);
        } finally {
            setSubmitting(false);
        }
    });
}

/* -------------------------------------------------------------------------- */
/* Karakter sayacı                                                            */
/* -------------------------------------------------------------------------- */
function attachCounterHandler() {
    els.input.addEventListener("input", (event) => {
        updateCounter(event.target.value);
        if (els.error.textContent) clearError();
    });
}

/* -------------------------------------------------------------------------- */
/* Geçmiş yenile butonu                                                       */
/* -------------------------------------------------------------------------- */
function attachRefreshHandler() {
    els.refreshBtn.addEventListener("click", () => refreshHistorySilently());
}

async function refreshHistorySilently() {
    try {
        const data = await fetchHistory({ page: 1 });
        renderHistory((data && data.results) || []);
    } catch (_) {
        /* sessiz geç: ana akış zaten çalıştı, geçmiş ikincil */
    }
}

/* -------------------------------------------------------------------------- */
/* Geçmiş satırına tıklama                                                    */
/* -------------------------------------------------------------------------- */
function attachHistoryItemHandler() {
    els.historyList.addEventListener("click", async (event) => {
        const row = event.target.closest(".aura-history-item");
        if (!row) return;

        const entryId = row.dataset.moodEntryId;
        if (!entryId) return;

        showLoader();
        try {
            const moodEntry = await fetchMoodById(entryId);
            applyMoodTheme(moodEntry.detected_mood);
            hideLoader();
            renderResults(moodEntry);
        } catch (err) {
            hideLoader();
            const msg = (err instanceof ApiError)
                ? err.message
                : "Geçmiş yüklenemedi.";
            showError(msg);
        }
    });
}

/* -------------------------------------------------------------------------- */
/* Public                                                                     */
/* -------------------------------------------------------------------------- */
export function registerEventHandlers() {
    attachFormHandler();
    attachCounterHandler();
    attachRefreshHandler();
    attachHistoryItemHandler();
}

export { refreshHistorySilently };
