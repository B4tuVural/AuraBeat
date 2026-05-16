/**
 * main.js — Uygulamanın giriş noktası.
 *
 * Modülleri birleştirir ve ilk durumu kurar.
 */
import { registerEventHandlers, refreshHistorySilently } from "./events.js";
import { updateCounter } from "./ui.js";

function bootstrap() {
    registerEventHandlers();
    updateCounter("");
    refreshHistorySilently();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrap);
} else {
    bootstrap();
}
