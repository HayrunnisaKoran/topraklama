# 🔌 Topraklama İzleme ve Anomali Tespiti Sistemi

Topraklama sistemlerinin güvenliğini değerlendirmek için yapay zeka tabanlı anomali tespit ve erken uyarı sistemi.

## 📋 Proje Özeti

Bu proje, elektrik dağıtım sistemlerindeki topraklama direnci, kaçak akım, toprak potansiyeli gibi kritik parametreleri sürekli izleyerek, yapay zeka (Isolation Forest) algoritması kullanarak anomali tespiti yapar ve erken uyarı sistemi sağlar.

## 🎯 Özellikler

- ✅ **Sensör Verisi Simülasyonu**: 1 yıllık sentetik veri üretimi
- ✅ **Yapay Zeka Modeli**: Isolation Forest ile anomali tespiti
- ✅ **Gerçek Zamanlı İzleme**: Canlı veri akışı simülasyonu
- ✅ **Risk Skorlama**: 0-100 arası risk puanı hesaplama
- ✅ **Otomatik Yük İzolasyonu**: Yüksek risk durumunda otomatik izolasyon
- ✅ **GPS Entegrasyonu**: Trafo lokasyonları harita üzerinde görüntüleme
- ✅ **Bildirim Sistemi**: Anomali durumlarında otomatik uyarılar

## 🛠️ Teknoloji Yığını

- **Python 3.8+**: Ana programlama dili
- **Pandas & NumPy**: Veri işleme
- **Scikit-learn**: Makine öğrenimi (Isolation Forest)
- **Matplotlib**: Veri görselleştirme
- **Joblib**: Model kaydetme/yükleme

## 📦 Kurulum

### 1. Gereksinimler

Python 3.8 veya üzeri sürüm gerekir.

### 2. Sanal Ortam Oluşturma (Önerilen)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Paketleri Yükleme

```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

### Adım 1: Veri Üretimi

1 yıllık sentetik sensör verisi üretir (normal veri + arıza senaryoları):

```bash
python veri_uret.py
```

Bu komut:
- 50 trafo için 1 yıllık veri üretir
- Normal günlük/haftalık değişimleri simüle eder
- Arıza senaryolarını ekler (yağmur, korozyon, kaçak akım)
- `data/sensor_data.csv` dosyasına kaydeder

**Çıktı:**
```
🚀 Veri üretimi başlıyor...
📊 50 trafo için 1 yıllık veri üretilecek
✅ Normal veri üretimi tamamlandı!
💾 Veri kaydedildi: data/sensor_data.csv
```

### Adım 2: Model Eğitimi

Yapay zeka modelini eğitir:

```bash
python model_egit.py
```

Bu komut:
- CSV dosyasından veriyi yükler
- Isolation Forest modelini eğitir
- Model performansını değerlendirir (F1, Precision, Recall)
- Eğitilmiş modeli `models/anomali_model.pkl` dosyasına kaydeder

**Çıktı:**
```
🤖 Yapay Zeka Model Eğitimi
📂 Veri yükleniyor: data/sensor_data.csv
✅ 438,000 kayıt yüklendi
🔧 Model eğitimi başlıyor...
📊 Model değerlendirmesi yapılıyor...
📈 Performans Metrikleri:
   • F1 Skoru: 0.8523
   • Kesinlik (Precision): 0.8234
   • Duyarlılık (Recall): 0.8832
💾 Model kaydedildi: models/anomali_model.pkl
```

### Adım 3: Simülasyon Çalıştırma

Gerçek zamanlı veri akışını simüle eder:

```bash
python simulasyon.py
```

Veya belirli bir süre için:

```bash
python simulasyon.py --duration 30  # 30 dakika
```

Demo modunu kapatmak için:

```bash
python simulasyon.py --no-demo
```

**Simülasyon Özellikleri:**
- Her 5 saniyede bir tüm trafolar için veri üretir
- Model ile anomali tespiti yapar
- Risk skorlarını hesaplar
- Yüksek risk durumunda otomatik izolasyon yapar
- Bildirimleri `data/realtime_data.csv` dosyasına kaydeder

**Çıktı:**
```
🚀 Topraklama İzleme Simülasyonu Başlatılıyor
📊 50 trafo izleniyor...
⏱️  Güncelleme aralığı: 5 saniye

🔄 İterasyon 1 - 14:30:15
⚠️ Trafo 5 (Trafo 5): Yüksek risk tespit edildi! (Risk: 85.3)
📈 Özet:
   • Yüksek Risk: 2 trafo
   • Orta Risk: 5 trafo
   • İzole Edilmiş: 1 trafo
```

## 📁 Proje Yapısı

```
Topraklama Izleme ve Anomali/
│
├── config.py              # Proje konfigürasyonu
├── veri_uret.py           # Veri üretim scripti
├── model_egit.py          # Model eğitim scripti
├── simulasyon.py          # Simülasyon scripti
├── requirements.txt       # Python paketleri
├── README.md             # Bu dosya
│
├── data/                  # Veri dosyaları
│   ├── sensor_data.csv    # 1 yıllık üretilen veri
│   └── realtime_data.csv  # Gerçek zamanlı simülasyon verisi
│
├── models/                # Eğitilmiş modeller
│   └── anomali_model.pkl  # Isolation Forest modeli
│
└── src/                   # Kaynak kodlar (gelecek için)
```

## ⚙️ Konfigürasyon

`config.py` dosyasında aşağıdaki ayarları yapabilirsiniz:

- **Trafo Sayısı**: `NUM_TRANSFORMERS = 50`
- **Sensör Aralıkları**: Normal değer sınırları
- **Arıza Senaryoları**: Tarih ve etkileri
- **Model Parametreleri**: Contamination oranı
- **Simülasyon Ayarları**: Güncelleme aralığı

## 📊 Veri Parametreleri

Sistem aşağıdaki sensör verilerini izler:

| Parametre | Birim | Normal Aralık | Açıklama |
|-----------|-------|---------------|----------|
| Toprak Direnci | Ohm | 2.0 - 5.0 | Topraklama direnci |
| Kaçak Akım | mA | 0.0 - 10.0 | İzole olmayan hatlardan akan akım |
| Toprak Potansiyeli | V | -5.0 - 5.0 | Gerilim dengesizliği |
| Toprak Nemi | % | 20.0 - 60.0 | Çevresel faktör |
| Toprak Sıcaklığı | °C | 5.0 - 35.0 | Çevresel faktör |
| Korozyon Seviyesi | index | 0.0 - 30.0 | Elektrot sağlığı |

## 🎯 Risk Skorlama

Risk puanı 0-100 arasındadır:

- **0-40 (Düşük Risk)**: 🟢 Normal durum
- **40-70 (Orta Risk)**: 🟡 Dikkat gerektirir
- **70-100 (Yüksek Risk)**: 🔴 Acil müdahale gerekli

Risk puanı 80'in üzerine çıktığında otomatik yük izolasyonu devreye girer.

## 🔔 Bildirim Sistemi

Sistem aşağıdaki durumlarda bildirim üretir:

- ⚠️ Yüksek risk tespit edildiğinde
- 🔴 Otomatik izolasyon yapıldığında
- 📊 Anomali tespit edildiğinde

Bildirimler `simulasyon.py` çalışırken konsola yazdırılır ve `data/realtime_data.csv` dosyasına kaydedilir.

## 🧪 Test Senaryoları

Sistem aşağıdaki arıza senaryolarını içerir:

1. **Yağmur Senaryosu** (Kasım 5):
   - Toprak direnci düşer
   - Nem artar

2. **Korozyon Senaryosu** (Aralık 10):
   - Direnç kademeli olarak artar (20 Ohm'a kadar)
   - Korozyon seviyesi yükselir

3. **Kaçak Akım Senaryosu** (Ekim 15):
   - Ani kaçak akım yükselişi
   - Potansiyel farkı artar

## 📈 Model Performans Metrikleri

Model eğitimi sonrası aşağıdaki metrikler hesaplanır:

- **F1 Skoru**: Genel performans
- **Precision (Kesinlik)**: Yanlış pozitif oranı
- **Recall (Duyarlılık)**: Gerçek anomali tespit oranı
- **Confusion Matrix**: Detaylı sınıflandırma tablosu

## 🚧 Gelecek Geliştirmeler

- [ ] Web Dashboard (React.js)
- [ ] Harita entegrasyonu (Leaflet.js)
- [ ] Firebase/MongoDB entegrasyonu
- [ ] LSTM Autoencoder modeli
- [ ] Ekonomi modülü (maliyet hesaplama)
- [ ] SMS bildirim simülasyonu

## 👥 Ekip ve Görev Dağılımı

1. **Veri Bilimcisi & AI Mühendisi**: `veri_uret.py`, `model_egit.py`
2. **Backend & Simülasyon Mimarı**: `simulasyon.py`, veritabanı entegrasyonu
3. **Frontend & UI Geliştirici**: Web dashboard, harita görselleştirme
4. **Ürün Yöneticisi**: Senaryo yazımı, dokümantasyon, sunum

## 📝 Lisans

Bu proje akademik/öğrenim amaçlıdır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Sorularınız için issue açabilirsiniz.

---

**Not**: Bu sistem simülasyon amaçlıdır. Gerçek üretim ortamında kullanılmadan önce kapsamlı testler yapılmalıdır.

