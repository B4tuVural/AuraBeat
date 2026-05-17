# AuraBeat 🎧

> Ruh halini anlat — Gemini sana özel şarkıları seçsin.

AuraBeat, kullanıcının serbest metin ile yazdığı duygusal bağlamı **Gemini Pro** ile analiz edip,
ruh haline uygun altı şarkıyı **"neden"** gerekçesiyle birlikte sunan tam yığın bir uygulamadır.

---
## 🎬 Demo

> AuraBeat'i çalışırken görmek istiyorsan aşağıdaki videoyu izleyebilirsin.
> Ruh halini metin olarak girmen, Gemini'nin analiz etmesi ve sana özel şarkıların
> mood-reactive bir tema eşliğinde sıralanması — tüm akış canlı kayıtta.

🎥 [Demo videosunu YouTube'da izle](https://www.youtube.com/watch?v=ooL79gf3p-c)


---
## 🧰 Teknoloji Yığını

| Katman     | Teknoloji                                                                   |
| :--------- | :-------------------------------------------------------------------------- |
| Backend    | **Django 5.2 LTS**  +  DRF 3.16                                             |
| Veritabanı | **PostgreSQL 17** (Docker ortamında)                                        |
| DB Sürücü  | **psycopg 3** (Django 5.2'nin tercih ettiği modern sürücü)                  |
| AI         | google-generativeai (Gemini 2.5 Flash)                                      |
| Frontend   | Vanilla JS (ES Modules) + Bootstrap 5.3 + Fraunces & Manrope fontları       |
| Python     | 3.10+ (önerilen: 3.12 veya 3.13)                                           |

> 📓 Bu projenin Claude ile nasıl geliştirildiğini merak ediyorsan → [`aurabeat_gelistirme_gunlugu.md`](geliştirme-süreci/aurabeat_gelistirme_gunlugu.md)
> Hangi promptların kullanıldığını, hangi modelin hangi kararı aldığını ve sürecin nasıl ilerlediğini adım adım belgeler.
---

## 🗂️ Proje Yapısı

```
aurabeat/
├── docker-compose.yml         # ← PostgreSQL 17 Docker tanımı
├── docker/
│   └── pg-init/
│       └── 01-init.sql        # ← İlk çalıştırmada otomatik çalışır
├── manage.py
├── requirements.txt
├── .env.example
│
├── aurabeat/                  # Django proje konfigürasyonu
│   ├── settings.py            # ← Docker DB ayarları burada
│   ├── urls.py
│   └── wsgi.py / asgi.py
│
├── api/
│   ├── interfaces/            # SOLID DIP — soyut sözleşmeler
│   │   ├── base_ai_service.py
│   │   └── base_music_service.py
│   ├── services/              # İş mantığı (CUD + external)
│   │   ├── gemini_service.py
│   │   ├── spotify_service.py
│   │   └── mood_service.py
│   ├── selectors/             # Read-only sorgu mantığı
│   │   └── mood_selector.py
│   ├── models.py              # Thin Models
│   ├── serializers.py         # Validation + shape
│   ├── views.py               # Thin Controllers
│   ├── urls.py
│   └── admin.py
│
└── frontend/                  # Bootstrap 5 + Vanilla JS
    ├── index.html
    ├── css/style.css          # Mood-reactive tema
    └── js/                    # Separation of Concerns
        ├── api.js             # — sadece fetch
        ├── ui.js              # — sadece DOM
        ├── events.js          # — sadece listener
        └── main.js            # — bootstrap
```

---

## ✨ Frontend Özellikleri

- **Mood-reactive tema** — tespit edilen ruh haline göre tüm palet (mutlu → kehribar, hüzünlü → mavi, sakin → su yeşili, vb.) yumuşak geçişlerle değişir.
- **Erişilebilir form** — ARIA live region, klavye odaklı odak halkası, `prefers-reduced-motion` desteği.
- **Sıralı fade-in** — kartlar 90 ms aralıklarla sahnelenir.
- **Sayaç & dostane hata mesajları** — anlık geri bildirim.
- **Geçmiş tıklanabilir** — her satır o anki analizi yeniden açar.

---

---

## 🚀 Kurulum

Aşağıda önce her iki platformda da ortak olan **gereksinimler**, ardından
**Windows** ve **Linux / macOS** için ayrı ayrı adımlar anlatılmaktadır.

### Ortak Gereksinimler

| Araç           | Ne için                | Nereden                                              |
| :------------- | :--------------------- | :--------------------------------------------------- |
| **Docker Desktop**  | PostgreSQL 17 container| https://www.docker.com/products/docker-desktop  |
| **Python 3.10+**    | Django backend         | https://www.python.org/downloads/               |
| **Git** (opsiyonel) | Repo klonlama          | https://git-scm.com/downloads                   |
| **Gemini API Key**  | AI analizi             | https://aistudio.google.com/app/apikey          |
| **Spotify API Key** | Uygulama içi öneri     | https://https://developer.spotify.com           |

> **Docker Desktop kurulumu:** Windows'ta kurulum sırasında **"Use WSL 2"** seçeneğinin
> işaretli olduğundan emin ol. Kurulumdan sonra bilgisayarı yeniden başlat. Görev çubuğunda
> balina ikonu (🐳) yeşil olduğunda Docker hazır demektir.

---

### 🪟 Windows Kurulumu (PowerShell)

Tüm komutlar **PowerShell** (veya **Windows Terminal**) içindir.

#### Adım 1 — Projeyi clonela

```powershell
git clone https://github.com/B4tuVural/AuraBeat
cd aurabeat
```

#### Adım 2 — PostgreSQL 17'yi başlat (Docker)

```powershell
# Docker Desktop'un çalıştığından emin ol (görev çubuğunda 🐳 yeşil olmalı)
docker compose up -d
```

İlk çalıştırmada PostgreSQL 17 imajı indirilir (~90 MB) ve `docker/pg-init/01-init.sql`
otomatik çalışır. Aşağıdaki komutla container'ın sağlığını kontrol et:

```powershell
docker compose ps
# STATUS sütununda "Up ... (healthy)" görmelisin.
```

#### Adım 3 — Python sanal ortam

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Hata alıyorsan:** PowerShell'in script çalıştırma politikası engelleyebilir.
> Bu durumda önce şu komutu çalıştır (tek seferlik):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### Adım 4 — `.env` dosyasını set-credentials.py scripti ile oluşturma

```powershell
python set-credentials.py
```

Script çalıştırıldığında terminal açılacak. **`GEMINI_API_KEY=`** zorunlu olacak şekilde **`SPOTIFY_CLIENT_ID=`** ve **`SPOTIFY_CLIENT_SECRET=`** gerekli API anahtarlarını yapıştırın, kaydet ve kapat. Script **`.env.example`** dosyasından **`.env`** ortam dosyanızı üretecektir
Diğer DB değerleri Docker Compose ile birebir eşleştiği için değiştirmeye gerek yok.

#### Adım 5 — Migrate ve sunucuyu başlat

```powershell
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
```

Django `http://127.0.0.1:8000` adresinde açılacak.

#### Adım 6 — Frontend'i çalıştır (yeni PowerShell penceresi)

```powershell
cd aurabeat\frontend
python -m http.server 8080
```

Tarayıcıdan **http://localhost:8080** adresine git. AuraBeat hazır.

---

### 🐧 Linux / macOS Kurulumu (Bash)

#### Adım 1 — Projeyi aç

```bash
git clone https://github.com/B4tuVural/AuraBeat
cd aurabeat
```

#### Adım 2 — PostgreSQL 17'yi başlat (Docker)

```bash
docker compose up -d

# Sağlık kontrolü
docker compose ps
# "Up ... (healthy)" görmelisin.
```

#### Adım 3 — Python sanal ortam

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Adım 4 — `.env` dosyasını oluştur

```bash
python set-credentials.py
```

#### Adım 5 — Migrate ve sunucuyu başlat

```bash
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
```

#### Adım 6 — Frontend (yeni terminal)

```bash
cd frontend/
python -m http.server 8080
```

Tarayıcıdan **http://localhost:8080**

---

## 🐳 Docker Komut Referansı

Geliştirme sırasında sık kullanacağın Docker komutları:

```bash
# ---------- Lifecycle ----------
docker compose up -d          # Arka planda başlat
docker compose down           # Durdur (veri korunur)
docker compose down -v        # Durdur + veriyi SİL (sıfırdan başla)
docker compose restart        # Yeniden başlat

# ---------- İzleme ----------
docker compose ps             # Container durumu + sağlık
docker compose logs db        # PostgreSQL logları
docker compose logs -f db     # Canlı log takibi (Ctrl+C ile çık)

# ---------- Veritabanı erişimi ----------
docker compose exec db psql -U aurabeat -d aurabeat
# Artık SQL yazabilirsin:
#   \dt                      → tabloları listele
#   \d api_moodentry         → tablo yapısı
#   SELECT * FROM api_moodentry ORDER BY created_at DESC LIMIT 5;
#   \q                       → çık

# ---------- Yedek / Geri yükleme ----------
docker compose exec db pg_dump -U aurabeat aurabeat > backup.sql
docker compose exec -T db psql -U aurabeat aurabeat < backup.sql
```

---

## ❓ Sık Karşılaşılan Sorunlar

### "docker compose" komutu bulunamıyor

Docker Desktop'un güncel olduğundan emin ol. Eski sürümlerde `docker-compose` (tire ile)
kullanılıyordu. Güncel Docker Desktop'ta `docker compose` (boşlukla) varsayılan.
Her iki durumda da şunu dene:

```bash
docker-compose up -d     # eski sözdizimi
```

### Windows: Port 5432 zaten kullanılıyor

Yerel makinede zaten bir PostgreSQL kurulu olabilir. Çözüm seçenekleri:

**Seçenek A** — Yerel PostgreSQL servisini durdur:
```powershell
# PowerShell (Yönetici olarak çalıştır)
Stop-Service postgresql-x64-17     # veya hangi sürüm yüklüyse
```

**Seçenek B** — Docker'ı farklı portta çalıştır:
`docker-compose.yml` içinde portu değiştir:
```yaml
    ports:
      - "5433:5432"    # host:container
```
`.env` dosyasında da güncelle:
```
DB_PORT=5433
```

### "Connection refused" veya "could not connect to server"

Container'ın healthy olduğunu kontrol et:
```bash
docker compose ps
```
`STATUS` sütununda `(healthy)` görmüyorsan biraz bekle (ilk başlatmada ~10sn) veya logları incele:
```bash
docker compose logs db
```

### Windows: PowerShell'de `.venv\Scripts\Activate.ps1` çalışmıyor

Execution policy kısıtlaması. Tek seferlik çöz:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "relation does not exist" hatası

Migration'ları çalıştırmayı unutmuş olabilirsin:
```bash
python manage.py makemigrations api
python manage.py migrate
```

### Veritabanını sıfırlamak istiyorum

```bash
docker compose down -v          # Veriyi tamamen sil
docker compose up -d            # Sıfırdan oluştur (init script tekrar çalışır)
python manage.py migrate        # Tabloları yeniden yarat
```

### Gemini API hatası (503 Service Unavailable)

- `.env` dosyasında `GEMINI_API_KEY` doğru mu kontrol et.
- API anahtarının kotası dolmuş olabilir → [AI Studio](https://aistudio.google.com/) üzerinden kontrol et.
- Frontend'de dostane bir hata mesajı gösterilir; tekrar denemek yeterlidir.

---

## 🔌 REST API

Tüm yanıtlar `application/json`. Standart HTTP durum kodları kullanılır.

| Method | Endpoint                    | Açıklama                                  |
| :----: | :-------------------------- | :---------------------------------------- |
| POST   | `/api/mood/analyze/`        | Yeni analiz oluştur (201 Created)         |
| GET    | `/api/mood/history/?page=1` | Sayfalı geçmiş (PageNumberPagination)     |
| GET    | `/api/mood/<uuid>/`         | Tek girdi detayı                          |
| GET    | `/api/mood/stats/`          | Son 30 günün ruh hali dağılımı            |

### Örnek istek (curl — Linux/macOS & Windows)

```bash
curl -X POST http://localhost:8000/api/mood/analyze/ ^
     -H "Content-Type: application/json" ^
     -d "{\"user_text\": \"Bugün biraz dağınığım, kahve içerken yağmuru izlemek istiyorum.\"}"
```

> Windows CMD'de satır devam karakteri `^`, PowerShell'de `` ` `` (backtick).
> Linux/macOS'ta `\` kullanılır.

### Örnek yanıt

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


## 🧪 Geliştirme Notları

### psycopg 3 vs psycopg2

Bu proje **psycopg 3** kullanır. Eğer zorunlu nedenlerle psycopg2 lazımsa:

```diff
# requirements.txt
- psycopg[binary]==3.2.3
+ psycopg2-binary==2.9.10
```

`settings.py`'de hiçbir değişiklik gerekmez — `django.db.backends.postgresql` her iki sürücüyü otomatik tanır.

### Sürüm Uyumluluk Matrisi

| Bileşen              | Sürüm     | Destek Bitişi  |
| :------------------- | :-------- | :------------- |
| Django               | 5.2.x LTS | Nisan 2028     |
| PostgreSQL           | 17.x      | Kasım 2029     |
| psycopg              | 3.2.x     | aktif          |
| Python               | 3.10–3.13 | PY 3.10: Eki 2026 |
| djangorestframework  | 3.16.x    | aktif          |
