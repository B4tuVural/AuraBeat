# Frontend_spec.md - UI/UX Spesifikasyonu

## 1. Tasarım Hedefleri

- **Minimalist & Duygusal:** Kullanıcının ruh haline göre dinamik olarak renk değiştiren (örn: hüzünlüyse soft mavi, enerjikse turuncu) bir arayüz.
- **Hızlı Geri Bildirim:** AI işlenirken kullanıcıya "Ruh halin analiz ediliyor..." gibi etkileşimli loader gösterimi.

## 2. Sayfa Modülleri

### 2.1. Ana Ekran (Input)

- **Mood Box:** Büyük, kenarları yuvarlatılmış bir metin alanı.
- **Submit Button:** "Şarkımı Bul" butonu (basıldığında asenkron fetch tetiklenir).

### 2.2. Öneri Kartları (Result Cards)

- **Kart Yapısı:** Şarkı ismi (Bold), Sanatçı, Gemini'nin "Neden" açıklaması (Italic) ve Dinle butonu.
- **Animasyon:** Kartlar ekrana sırayla "fade-in" efektiyle gelmelidir.

## 3. API Haberleşme Mantığı (Vanilla JS)

```javascript
const getMusic = async (text) => {
  // 1. Loader'ı aktif et
  // 2. Django /api/mood/analyze/ endpoint'ine POST at
  // 3. Dönen JSON ile DOM'u güncelle
  // 4. Hata varsa kullanıcıya dostane bir mesaj göster
};
```
