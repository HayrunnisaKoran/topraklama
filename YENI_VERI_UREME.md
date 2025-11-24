# 🔄 Yeni Veri Üretimi ve Firebase Entegrasyonu

## Adım 1: Eski Verileri Temizle

```powershell
python veri_temizle.py
```

Bu komut:
- `data/realtime_data.csv` dosyasını siler
- `data/sensor_data.csv` dosyasını siler

## Adım 2: Yeni Veri Üret (Model ile)

```powershell
python veri_uret_yeni.py
```

Bu komut:
- Model kullanarak gerçekçi veri üretir
- Her trafo için kategoriye göre risk skorları hesaplar
- %70 normal, %20 orta risk, %10 yüksek risk dağılımı
- `data/sensor_data.csv` dosyasına kaydeder

**Beklenen süre:** 5-10 dakika (120 trafo × 100 kayıt)

## Adım 3: Modeli Yeniden Eğit

```powershell
python model_egit.py
```

Yeni verilerle modeli eğitin.

## Adım 4: Firebase Kurulumu (Opsiyonel)

### 4.1 Firebase Projesi Oluştur

1. [Firebase Console](https://console.firebase.google.com/) → "Add project"
2. Proje adı: `topraklama-izleme` (veya istediğiniz)
3. Firestore Database oluştur (Test mode)

### 4.2 Service Account Key İndir

1. Firebase Console → ⚙️ Settings → Project settings
2. "Service accounts" sekmesi
3. "Generate new private key" → JSON indir
4. Dosyayı `firebase-key.json` olarak proje klasörüne kaydedin

### 4.3 Firebase Paketini Yükle

```powershell
pip install firebase-admin
```

## Adım 5: Simülasyonu Firebase ile Çalıştır

```powershell
# Firebase ile
python simulasyon.py --duration 5 --firebase

# Veya Firebase olmadan (sadece CSV)
python simulasyon.py --duration 5
```

## Beklenen Sonuç

Yeni veri üretimi sonrası:
- ✅ Doğru risk dağılımı (yeşil, turuncu, kırmızı)
- ✅ Model ile gerçekçi veriler
- ✅ Firebase entegrasyonu (opsiyonel)

## Firebase Kullanmadan da Çalışır

Firebase kurulumu yapmazsanız:
- Sistem CSV dosyalarını kullanır
- Tüm özellikler çalışır
- Sadece gerçek zamanlı senkronizasyon olmaz

---

**Not**: Firebase kullanmak istemiyorsanız, sadece Adım 1-3'ü yapın.

