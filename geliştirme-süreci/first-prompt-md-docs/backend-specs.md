# 01-backend-spec.md - Sunucu ve API Spesifikasyonu

## 1. Mimari Prensipler ve SOLID Uyumluluğu

Django'nun varsayılan yapısını (Fat Views / Fat Models) kontrolsüz büyüterek spagetti koda dönüşmesini engellemek için kesin katman ayrımı uygulanır:

- **Single Responsibility Principle (SRP):** \* `views.py` sadece HTTP isteklerini alır, kimlik doğrulama/izin (auth/permission) kontrolü yapar ve HTTP yanıtı döner. Hiçbir iş mantığı (API çağırma, veri işleme, veritabanı yazma) burada bulunamaz.
  - `serializers.py` sadece veri doğrulama (validation) ve serileştirme yapar. İçerisinde harici servis çağrıları veya karmaşık iş mantığı barındıramaz.

- **Open/Closed Principle (OCP) & Dependency Inversion Principle (DIP):** Yapay zeka ve müzik sağlayıcıları soyutlanmalıdır. Python'un `abc` (Abstract Base Classes) modülü kullanılarak arayüzler yaratılır. Sınıflar birbirine sıkı sıkıya bağlı (tightly coupled) olamaz; bağımlılıklar constructor enjeksiyonu ile geçilir.

- **Separation of Write and Read (Service & Selector Pattern):**
  - **Services (`services/`):** Veritabanında değişiklik yapan (CUD - Create, Update, Delete) ve dış servislerle konuşan tüm iş mantığı buradadır.
  - **Selectors (`selectors/`):** Veritabanından karmaşık veri okuma, filtreleme ve raporlama (Read) mantığı buraya izole edilir. Böylece modellerin içi şişmez.

## 2. Klasör Mimarisi (Anti-Spaghetti & Katmanlı Yapı)

```text
/aura_beat
  /api
    /interfaces          # Soyut Sınıflar (SOLID DIP için)
      base_ai_service.py
      base_music_service.py
    /services            # İş Mantığı Katmanı (Yazma ve Dış Servis Operasyonları)
      gemini_service.py  # base_ai_service.py'den miras alır
      spotify_service.py # base_music_service.py'den miras alır
      mood_service.py    # MoodEntry ve öneri oluşturma iş mantığı
    /selectors           # Sadece Okuma ve Filtreleme Mantığı (Okunabilirlik için)
      mood_selector.py   # Geçmiş analizleri getirme, filtreleme sorguları
    /views.py            # Sadece Request/Response yönetimi (İnce Katman)
    /serializers.py      # Gelen/Giden veri doğrulama (DRF)
    /models.py           # Saf ORM Tanımlamaları (Fat model yerine Akıllı Model)
    /urls.py             # Endpoint rotaları
```
