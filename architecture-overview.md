# Mimari Doküman

AuraBeat (Ruh Haline Göre Müzik Senkronizasyonu) projesinin mimari özellikleri aşağıdaki gibidir.

---

## Genel Bakış

AuraBeat, kullanıcının serbest metin ile yazdığı duygusal bağlamı Gemini 2.5 Flash ile analiz edip ruh haline uygun **altı şarkıyı** "neden" gerekçesiyle birlikte sunan tam yığın (full-stack) bir uygulamadır. Sistem; Django tabanlı bir REST API sunucusu, Docker Compose içinde çalışan bir PostgreSQL 17 veritabanı ve Separation of Concerns prensibine göre modüler ES Module dosyalara bölünmüş Vanilla JavaScript önyüzünden oluşur. Django sunucusu yerel makinede (host) çalışırken yalnızca PostgreSQL konteynerde çalıştırılır.

---

## Backend

Backend tarafı aşağıdaki teknolojileri ve prensipleri kullanır.

| Konu                    | Teknoloji                                      | Sürüm / Detay                                                                                                                                                                                                                                             |
| :---------------------- | :--------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend Mimarisi        | Service-Layer Architecture                     | Django'nun MVT yapısı üzerine inşa edilmiş, iş mantığının servis katmanlarına soyutlandığı, yazma/dış-servis (`services/`) ve okuma (`selectors/`) operasyonlarının birbirinden ayrıştırıldığı (Service & Selector Pattern) Clean Architecture yaklaşımı. |
| Framework               | Django & DRF                                   | Django 5.2.4 LTS (güvenlik desteği Nisan 2028'e kadar) + Django REST Framework 3.16.0.                                                                                                                                                                    |
| Programlama Dili        | Python 3.10+                                   | Nesne yönelimli, SOLID prensiplerine uygun. Önerilen: Python 3.12 veya 3.13.                                                                                                                                                                              |
| Veritabanı              | PostgreSQL 17                                  | Docker Compose (`docker-compose.yml`) ile konteynerize edilmiş. Türkçe locale (`tr_TR.UTF-8`), named volume (`aurabeat-pgdata`) ile kalıcı veri, `pg_isready` healthcheck ile sağlık kontrolü.                                                            |
| DB Sürücü               | psycopg 3.2.3                                  | Django 5.2'nin tercih ettiği modern sürücü. `[binary]` extra'sı ile libpq wheel'a gömülüdür; ayrı sistem paketi (`libpq-dev`) gerekmez.                                                                                                                   |
| Yapay Zeka Entegrasyonu | Gemini 2.5 Flash (`google-generativeai` 0.8.3) | Kullanıcı girdisinden duygu analizi ve yapılandırılmış (JSON) müzik önerileri üretmek için kullanılır. `BaseAIService` soyut arayüzü üzerinden DIP ile entegre edilir. Model adı `.env` → `GEMINI_MODEL_NAME` ile yapılandırılır.                         |
| Müzik Zenginleştirme    | Spotify Web API (`spotipy` 2.24.0) — opsiyonel | Albüm kapağı URL'si ve harici dinleme linki zenginleştirmesi. `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` boş bırakılırsa `NullMusicService` (Null Object Pattern) devreye girer. `BaseMusicService` soyut arayüzü üzerinden DIP ile entegre edilir.    |
| CORS                    | django-cors-headers 4.4.0                      | İzin verilen origin `.env` → `FRONTEND_ORIGIN` ile yapılandırılır. Varsayılan: `http://localhost:8080`.                                                                                                                                                   |
| Konfigürasyon           | python-dotenv 1.0.1 + `.env`                   | Tüm sırlar ve ortam değişkenleri `.env` dosyasından okunur. Kurulum yardımcısı `set-credentials.py`: `.env.example`'ı okuyup Gemini / Spotify anahtarlarını interaktif olarak doldurarak `.env` üretir.                                                   |
| Client (İstemci)        | REST API                                       | Önyüz uygulamasının `fetch` API üzerinden asenkron olarak eriştiği HTTP katmanı.                                                                                                                                                                          |

### Proje Dizin Yapısı

```
AuraBeat/
├── docker-compose.yml              # PostgreSQL 17 Docker tanımı
├── docker/
│   └── pg-init/
│       └── 01-init.sql             # İlk oluşturmada otomatik çalışır
├── manage.py
├── requirements.txt
├── .env.example
├── set-credentials.py              # Kurulum yardımcısı
│
├── aurabeat/                       # Django proje konfigürasyonu
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
│
├── api/                            # Django uygulaması
│   ├── interfaces/                 # DIP — soyut sözleşmeler
│   │   ├── base_ai_service.py      # BaseAIService (abc.ABC)
│   │   └── base_music_service.py   # BaseMusicService (abc.ABC)
│   ├── services/                   # İş mantığı — yazma + dış servis
│   │   ├── gemini_service.py       # GeminiService → BaseAIService
│   │   ├── spotify_service.py      # SpotifyService + NullMusicService
│   │   └── mood_service.py         # MoodService — orchestrator
│   ├── selectors/                  # Read-only sorgu mantığı
│   │   └── mood_selector.py
│   ├── models.py                   # Thin Models
│   ├── serializers.py              # Validation + shape
│   ├── views.py                    # Thin Controllers + _build_mood_service()
│   ├── urls.py
│   └── admin.py
│
└── frontend/                       # Bootstrap 5 + Vanilla JS
    ├── index.html
    ├── css/
    │   └── style.css               # Mood-reactive tema, animasyonlu orb'lar
    └── js/                         # ES Modules — Separation of Concerns
        ├── api.js                  # Sadece fetch + ApiError
        ├── ui.js                   # Sadece DOM güncellemeleri
        ├── events.js               # Sadece event listener'lar
        └── main.js                 # Bootstrap / başlatma
```

### Uyulan Prensipler

- **SOLID İlkeleri:**
  - **Single Responsibility (SRP):** `views.py` sadece HTTP I/O, `serializers.py` sadece doğrulama/şekillendirme, `services/` sadece yazma + dış servis, `selectors/` sadece okuma işlemi yapar.
  - **Open/Closed (OCP):** Yeni AI sağlayıcı eklemek için mevcut kodu değiştirmeye gerek yoktur; `BaseAIService`'ten miras alınıp constructor injection ile enjekte edilir.
  - **Dependency Inversion (DIP):** Dış servisler (Gemini, Spotify) soyut arayüzler (`abc.ABC`) üzerinden sisteme entegre edilir. `MoodService` somut sınıfları bilmez; yalnızca `BaseAIService` ve `BaseMusicService` sözleşmelerine bağımlıdır.
- **Clean Code Prensipleri:** Kısa fonksiyonlar, açıklayıcı isimlendirme, her fonksiyon tek işe sorumlu.
- **Null Object Pattern:** Spotify yapılandırılmamışsa `NullMusicService` sessiz fallback üretir; tüketici kod `if service is None` kontrolü yapmaz.
- **Constructor Injection:** Tüm dış bağımlılıklar `__init__` parametreleri ile geçilir; Composition Root `views.py`'deki `_build_mood_service()` fonksiyonudur.

---

## Frontend

Önyüz uygulaması aşağıdaki gibidir:

| Konu            | Detay                                                                                                                                                                                                                                  |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mimari          | Separation of Concerns — API çağrıları (`api.js`), DOM güncellemeleri (`ui.js`), event dinleyicileri (`events.js`) ve başlatma (`main.js`) tamamen ayrı ES Module dosyalarındadır.                                                     |
| Teknoloji       | HTML5, CSS3 ve Vanilla JavaScript (ES Modules). Harici bundler / framework yoktur.                                                                                                                                                     |
| UI Kütüphanesi  | Bootstrap 5.3.3 + Bootstrap Icons 1.11.3.                                                                                                                                                                                              |
| Tipografi       | Fraunces (variable, display/başlık) + Manrope (variable, gövde metin) — Google Fonts üzerinden.                                                                                                                                        |
| Tasarım         | Mood-Reactive tema: tespit edilen ruh haline göre tüm renk paleti (orb'lar, vurgu rengi, glow efekti) yumuşak CSS `transition` ile değişir. 7 farklı mood paleti tanımlıdır (mutlu → kehribar, hüzünlü → mavi, sakin → su yeşili vb.). |
| Arka Plan       | Gradient mesh: 3 adet animasyonlu blur orb + film grain overlay.                                                                                                                                                                       |
| Animasyon       | Şarkı kartları 90 ms aralıklarla sıralı `fade-in` ile sahnelenir. `prefers-reduced-motion` medya sorgusu ile hareket azaltma desteği.                                                                                                  |
| Erişilebilirlik | ARIA `role="alert"` ve `aria-live="polite"` ile canlı geri bildirim, klavye odaklı navigasyon, odak halkası.                                                                                                                           |
| Hata Yönetimi   | Tek tip `ApiError` sınıfı; kullanıcıya dostane hata mesajları gösterilir.                                                                                                                                                              |
| Haberleşme      | Backend ile `fetch` API üzerinden asenkron REST çağrıları (`http://localhost:8000`).                                                                                                                                                   |
| Çalıştırma      | `python -m http.server 8080` — ek araç gerekmez.                                                                                                                                                                                       |

---

## Veritabanı Altyapısı (Docker)

| Konu                    | Detay                                                                                                                                                                             |
| :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Konteynerizasyon        | Docker Compose v2 (`docker-compose.yml`) — tek servis tanımı (`db`). Django sunucusu host'ta çalışır; yalnızca PostgreSQL konteynerde çalışır.                                    |
| İmaj                    | `postgres:17-alpine` (küçük boyut, production-grade). Konteyner adı: `aurabeat-pg`.                                                                                               |
| Veri Kalıcılığı         | Named volume (`aurabeat-pgdata`) — container silinse bile veriler korunur.                                                                                                        |
| Sağlık Kontrolü         | `pg_isready -U aurabeat -d aurabeat` ile 5sn aralıklarla healthcheck; 10sn start_period + 10 deneme.                                                                              |
| Init Script             | `docker/pg-init/01-init.sql` — `read-only` bağlı; ilk oluşturmada `uuid-ossp` ve `pg_trgm` extension'larını kurar.                                                                |
| Locale                  | `tr_TR.UTF-8` encoding ve collation (Türkçe sıralama ve karakter desteği). Zaman dilimi: `Europe/Istanbul`.                                                                       |
| Kimlik Bilgileri        | DB adı, kullanıcı adı ve şifre docker-compose ortam değişkenleri ile `.env` arasında birebir eşleşir (varsayılan: `aurabeat/aurabeat/aurabeat`).                                  |
| Port                    | `5432:5432` (host:container). Yerel PostgreSQL çakışması varsa host portu `5433`'e alınabilir.                                                                                    |
| Performans (Geliştirme) | `shared_buffers=128MB`, `work_mem=8MB`, `maintenance_work_mem=64MB`, `effective_cache_size=256MB`, `max_connections=50`, `log_statement=mod`, `log_min_duration_statement=200ms`. |

---

## Konfigürasyon ve Ortam Değişkenleri

Tüm yapılandırma `.env` dosyasından okunur (python-dotenv). Kurulum için `set-credentials.py` scripti çalıştırılır.

| Değişken                | Zorunlu | Açıklama                                                       |
| :---------------------- | :-----: | :------------------------------------------------------------- |
| `DJANGO_SECRET_KEY`     |   ✅    | Django gizli anahtarı                                          |
| `DJANGO_DEBUG`          |   ✅    | `True` (geliştirme) / `False` (üretim)                         |
| `DJANGO_ALLOWED_HOSTS`  |   ✅    | İzin verilen host'lar (virgülle ayrılmış)                      |
| `DB_NAME`               |   ✅    | PostgreSQL veritabanı adı                                      |
| `DB_USER`               |   ✅    | PostgreSQL kullanıcısı                                         |
| `DB_PASSWORD`           |   ✅    | PostgreSQL şifresi                                             |
| `DB_HOST`               |   ✅    | Veritabanı host'u (Docker için `localhost`)                    |
| `DB_PORT`               |   ✅    | Veritabanı portu (varsayılan: `5432`)                          |
| `GEMINI_API_KEY`        |   ✅    | Google AI Studio'dan alınan API anahtarı                       |
| `GEMINI_MODEL_NAME`     |   ✅    | Kullanılacak model (varsayılan: `gemini-2.5-flash`)            |
| `SPOTIFY_CLIENT_ID`     |   ❌    | Spotify Developer Dashboard'dan (boş → NullMusicService)       |
| `SPOTIFY_CLIENT_SECRET` |   ❌    | Spotify Developer Dashboard'dan                                |
| `FRONTEND_ORIGIN`       |   ✅    | CORS izin verilen origin (varsayılan: `http://localhost:8080`) |

---

## API Tasarım Standartları

- RESTful API prensiplerine tam uyum sağlanır.
- Tüm veri alışverişleri `application/json` formatında yapılır.
- Listeleme yapan endpoint'ler sayfalama (`PageNumberPagination`) destekler.
- Standart HTTP durum kodları kullanılır: `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`, `503 Service Unavailable`.
- CORS politikası `django-cors-headers` ile yönetilir; izin verilen origin `.env` → `FRONTEND_ORIGIN` üzerinden yapılandırılır.

### Endpoint Tablosu

| Metod  | Endpoint                    | Açıklama                                                          | Durum Kodu       |
| :----: | :-------------------------- | :---------------------------------------------------------------- | :--------------- |
| `POST` | `/api/mood/analyze/`        | Yeni mood analizi oluştur; Gemini'ye gönderir, önerileri kaydeder | `201 Created`    |
| `GET`  | `/api/mood/history/?page=N` | Sayfalı geçmiş listesi (`PageNumberPagination`)                   | `200 OK`         |
| `GET`  | `/api/mood/<uuid>/`         | Tek girdi detayı (UUID tabanlı lookup)                            | `200 OK` / `404` |
| `GET`  | `/api/mood/stats/`          | Son 30 günün ruh hali dağılımı istatistiği                        | `200 OK`         |

### Örnek Yanıt (`POST /api/mood/analyze/`)

```json
{
  "id": "a1f8...",
  "user_text": "Bugün biraz dağınığım...",
  "preview": "Bugün biraz dağınığım…",
  "detected_mood": "melankolik",
  "created_at": "2026-05-16T14:32:00+03:00",
  "recommendations": [
    {
      "id": "b2...",
      "title": "Holocene",
      "artist": "Bon Iver",
      "reason": "Yağmurlu, içe dönük bir akşamla mükemmel uyumlu kırılgan dokular taşır.",
      "album_cover_url": null
    }
  ]
}
```

---

## Teknoloji Yığını Özet Tablosu

| Bileşen           | Teknoloji                              | Sürüm        |
| :---------------- | :------------------------------------- | :----------- |
| Backend Framework | Django LTS                             | 5.2.4        |
| REST API          | Django REST Framework                  | 3.16.0       |
| CORS              | django-cors-headers                    | 4.4.0        |
| Veritabanı        | PostgreSQL (Docker)                    | 17-alpine    |
| DB Sürücü         | psycopg (binary extra)                 | 3.2.3        |
| AI Sağlayıcı      | google-generativeai (Gemini 2.5 Flash) | 0.8.3        |
| Müzik Sağlayıcı   | spotipy (opsiyonel)                    | 2.24.0       |
| Konfigürasyon     | python-dotenv                          | 1.0.1        |
| Frontend UI       | Bootstrap                              | 5.3.3        |
| İkon Seti         | Bootstrap Icons                        | 1.11.3       |
| Display Fontu     | Fraunces (variable)                    | Google Fonts |
| Gövde Fontu       | Manrope (variable)                     | Google Fonts |
| JavaScript        | Vanilla JS (ES Modules)                | —            |
| Konteyner         | Docker Compose                         | v2           |
| Python            | 3.10+ (önerilen 3.12/3.13)             | —            |

---

## Geliştirme Sürüm Uyumluluk Matrisi

| Bileşen             | Sürüm       | Destek Bitişi      |
| :------------------ | :---------- | :----------------- |
| Django              | 5.2.x LTS   | Nisan 2028         |
| PostgreSQL          | 17.x        | Kasım 2029         |
| psycopg             | 3.2.x       | Aktif              |
| Python              | 3.10 – 3.13 | PY 3.10: Ekim 2026 |
| djangorestframework | 3.16.x      | Aktif              |
| google-generativeai | 0.8.3       | Aktif              |
