# 02-database-spec.md - Veritabanı Spesifikasyonu

## 1. Domain-Driven Design (DDD) ve Temiz Veri Standartları

- **Açık İsimlendirme:** Modeller ve alan isimleri kısaltma içermez (Örn: `usr_txt` yerine `user_text`).
- **Thin Models, Rich Domain:** Modeller sadece veri şemasını (schema), alan kısıtlamalarını ve o modele ait saf özellikleri (_pure properties_) tutar. Başka bir modeli etkileyen, dış servis çağıran veya karmaşık iş mantığı barındıran hiçbir fonksiyon `models.py` içerisine yazılamaz. Bu tür tüm veri mutasyonları ve dış kaynak işlemleri `services/` katmanına taşınır.
- **PostgreSQL Optimizasyonu:** Birincil anahtarlar için PostgreSQL'in yerel `uuid` veri tipi kullanılır. Sorgu performansını en üst düzeyde tutmak amacıyla, sık filtreleme ve sıralama yapılan alanlara veritabanı indeksleri (`db_index=True`) eklenmiştir.

## 2. Veri Modelleri (Django ORM)

### 2.1. MoodEntry (Domain: Duygu Analizi)

Kullanıcının sisteme sağladığı bağlamı ve analiz edilen ana ruh halini tutar.
| Alan | Tipi (Django) | DDD Karşılığı | Kısıtlamalar / PostgreSQL Yapılandırması |
| :--- | :--- | :--- | :--- |
| `id` | UUIDField | `Entity ID` | Primary Key, default=uuid.uuid4, editable=False |
| `user_text` | TextField | `RawContext` | Null=False, Blank=False |
| `detected_mood` | CharField | `AnalyzedState` | Max_length=50, db_index=True (Filtreleme optimizasyonu için) |
| `created_at` | DateTimeField | `Timestamp` | Auto_now_add=True, db_index=True (Zaman sıralı analiz sorguları için) |

- **Okunabilirlik ve Clean Code Notu (`@property`):** Model içerisinde sadece o modele ait türetilmiş veriler yer alabilir. Örneğin, kullanıcının girdisinin ilk 20 karakterini güvenli bir şekilde veren bir property eklenebilir. Ancak bu property asla yan etki (side-effect) yaratamaz veya ek veritabanı sorgusu tetikleyemez.

### 2.2. SongRecommendation (Domain: Öneri Çıktısı)

Duygu analizi sonucunda yapay zeka tarafından üretilen müzik önerisi varlıklarını tutar.
| Alan | Tipi (Django) | DDD Karşılığı | Kısıtlamalar / PostgreSQL Yapılandırması |
| :--- | :--- | :--- | :--- |
| `id` | UUIDField | `Entity ID` | Primary Key, default=uuid.uuid4, editable=False |
| `mood_entry` | ForeignKey | `ParentAggregate` | on_delete=CASCADE, db_index=True, related_name='recommendations' |
| `title` | CharField | `TrackName` | Max_length=200 |
| `artist` | CharField | `ArtistName` | Max_length=200, db_index=True (Sanatçı bazlı arama optimizasyonu için) |
| `reason` | TextField | `AI_Justification` | Null=False |
| `album_cover_url`| URLField | `MediaAsset` | Blank=True, Null=True |

- **Related Name Standartı (Spagetti Sorgu Önleyici):** Ters ilişkilerde Django'nun varsayılan ve spagetti koda davetiye çıkaran `songrecommendation_set` isimlendirmesini engellemek için `related_name='recommendations'` kullanımı zorunlu kılınmıştır. Bu sayede kodun herhangi bir yerinde `mood_entry.recommendations.all()` şeklinde son derece temiz, okunabilir ve tahmin edilebilir bir API kullanımı sağlanır.
