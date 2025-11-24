# 🚀 Yeni Veri Üretimi ve Firebase - Adım Adım

## ✅ Yapılanlar

1. ✅ Veri temizleme scripti oluşturuldu
2. ✅ Yeni veri üretim scripti oluşturuldu (model ile)
3. ✅ Firebase entegrasyonu eklendi
4. ✅ Simülasyon Firebase desteği eklendi
5. ✅ API server Firebase desteği eklendi

## 📋 Şimdi Yapmanız Gerekenler

### Adım 1: Eski Verileri Temizle

```powershell
python veri_temizle.py
```

Bu komut eski CSV dosyalarını siler.

### Adım 2: Yeni Veri Üret (Model ile)

```powershell
python veri_uret_yeni.py
```

**Ne yapar?**
- Model kullanarak gerçekçi veri üretir
- Her trafo için kategoriye göre risk skorları hesaplar
- %70 normal, %20 orta risk, %10 yüksek risk dağılımı
- `data/sensor_data.csv` dosyasına kaydeder

**Beklenen süre:** 5-10 dakika

### Adım 3: Modeli Yeniden Eğit

```powershell
python model_egit.py
```

Yeni verilerle modeli eğitin.

### Adım 4: Simülasyonu Çalıştır

```powershell
# Firebase olmadan (sadece CSV)
python simulasyon.py --duration 5

# Firebase ile (firebase-key.json gerekli)
python simulasyon.py --duration 5 --firebase
```

## 🔥 Firebase Kurulumu (Opsiyonel)

### Firebase Olmadan da Çalışır!

Firebase kurulumu yapmazsanız:
- ✅ Sistem CSV dosyalarını kullanır
- ✅ Tüm özellikler çalışır
- ✅ Sadece gerçek zamanlı senkronizasyon olmaz

### Firebase Kurmak İsterseniz:

1. **Firebase Projesi Oluştur**
   - [Firebase Console](https://console.firebase.google.com/)
   - "Add project" → Proje adı: `topraklama-izleme`
   - Firestore Database oluştur (Test mode)

2. **Service Account Key İndir**
   - Firebase Console → ⚙️ Settings → Project settings
   - "Service accounts" sekmesi
   - "Generate new private key" → JSON indir
   - Dosyayı `firebase-key.json` olarak proje klasörüne kaydedin

3. **Paketi Yükle**
   ```powershell
   pip install firebase-admin
   ```

4. **Simülasyonu Firebase ile Çalıştır**
   ```powershell
   python simulasyon.py --duration 5 --firebase
   ```

## 📊 Beklenen Sonuç

Yeni veri üretimi sonrası:

| Kategori | Sayı | Renk | Risk Skoru |
|----------|------|------|------------|
| Normal | ~84 | 🟢 Yeşil | 15-38 |
| Orta Risk | ~24 | 🟡 Turuncu | 45-68 |
| Yüksek Risk | ~12 | 🔴 Kırmızı | 75-85 |
| Arızalı | ~6-8 | 🔴 Koyu Kırmızı | 80-98 |

## ⚠️ Önemli Notlar

1. **Firebase Key Dosyası**: `firebase-key.json` dosyasını **ASLA** Git'e commit etmeyin!
2. **İlk Çalıştırma**: Yeni veri üretimi 5-10 dakika sürebilir
3. **Model**: Model eğitimi 1-3 dakika sürebilir
4. **Simülasyon**: Simülasyon çalışırken veriler gerçek zamanlı güncellenir

## 🎯 Hızlı Başlangıç (Firebase Olmadan)

```powershell
# 1. Temizle
python veri_temizle.py

# 2. Yeni veri üret
python veri_uret_yeni.py

# 3. Model eğit
python model_egit.py

# 4. Simülasyon çalıştır
python simulasyon.py --duration 5
```

Artık doğru risk dağılımıyla veriler görünecek! 🎉

