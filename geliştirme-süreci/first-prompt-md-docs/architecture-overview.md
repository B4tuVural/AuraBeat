# Mimari Doküman

AuraBeat (Ruh Haline Göre Müzik Senkronizasyonu) projesinin mimari özellikleri aşağıdaki gibidir.

## Backend

Backend tarafı aşağıdaki teknolojileri ve prensipleri kullanır.

| Konu                    | Teknoloji                        | Açıklama                                                                                                                                             |
| :---------------------- | :------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend Mimarisi        | Service-Layer Architecture       | Django'nun MVT yapısı üzerine inşa edilmiş, iş mantığının (Business Logic) servis katmanlarına soyutlandığı Clean Architecture yaklaşımı kullanılır. |
| Framework               | Django & DRF                     | Python tabanlı web framework'ü (Django) ve REST API inşası için Django REST Framework (DRF) kullanılır.                                              |
| Programlama Dili        | Python 3.10+                     | Nesne yönelimli ve SOLID prensiplerine uygun Python geliştirme.                                                                                      |
| Veritabanı              | PostgreSQL                       | İlişkisel veri bütünlüğü, yüksek performanslı indeksleme, JSONB esnekliği ve karmaşık sorgular için tercih edilmiştir.                               |
| Yapay Zeka Entegrasyonu | Gemini Pro (google-generativeai) | Kullanıcı girdilerinden duygu analizi ve yapılandırılmış (JSON) müzik önerileri almak için kullanılır.                                               |
| Client (İstemci)        | REST API                         | Frontend uygulamasının yürütmek istediği işlemler için geldiği API katmanı. Standartlar "API Tasarım Standartları" bölümünde tariflenmiştir.         |

Mutlaka uyulması gereken prensipler:

- **SOLID İlkeleri:** Özellikle Dependency Inversion (Bağımlılıkların Ters Çevrilmesi) prensibi gözetilerek dış servisler (Gemini, Spotify) arayüzler (Interfaces/Abstract Base Classes) üzerinden sisteme entegre edilir.
- **Clean Code Prensipleri:** Fonksiyonlar kısa, isimlendirmeler açıklayıcı olacak ve her fonksiyon tek bir işten (Single Responsibility) sorumlu olacaktır.

## FrontEnd

Önyüz uygulaması aşağıdaki gibidir:

- **Mimari:** Separation of Concerns (İlgilerin Ayrılığı) gözetilerek Modüler JavaScript yapısı kullanılır (API çağrıları, UI güncellemeleri ve Event dinleyicileri ayrı dosyalardadır).
- **Teknoloji:** HTML5, CSS3 ve Vanilla JavaScript.
- **Tasarım:** Bootstrap 5 kütüphanesi kullanılarak responsive (duyarlı) bir arayüz inşa edilir.
- **Haberleşme:** Backend uygulaması ile `fetch` API üzerinden asenkron REST çağrıları ile haberleşir.

## API Tasarım Standartları

- RESTful API prensiplerine tam uyum sağlanır.
- Tüm veri alışverişleri `application/json` formatında yapılır.
- Listeleme yapan endpoint'ler sayfalama _(pagination)_ destekler.
- Veri oluşturma endpoint'leri `HTTP POST`, veri getirme `HTTP GET`, güncelleme `HTTP PUT`, silme `HTTP DELETE` metodunu kullanır.
- Standart HTTP durum kodları (200 OK, 201 Created, 400 Bad Request, 500 Internal Server Error) istisnasız kullanılır.
