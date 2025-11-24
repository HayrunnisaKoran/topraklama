# 🎯 Şimdi Yapılacaklar - Adım Adım Kılavuz

## ✅ Tamamlananlar
1. ✅ Veri üretimi (`veri_uret.py`)
2. ✅ Model eğitimi (`model_egit.py`)
3. ✅ Flask Backend API (`api_server.py`)
4. ✅ React.js Web Dashboard (`web-dashboard/`)

## 🚀 Şimdi Yapmanız Gerekenler

### Adım 1: Simülasyonu Test Edin (5 dakika)

Terminal 1'de (PowerShell):

```powershell
# Sanal ortamı aktifleştir
.\venv\Scripts\Activate.ps1

# Simülasyonu çalıştır (5 dakika)
python simulasyon.py --duration 5
```

Bu komut:
- Gerçek zamanlı veri üretir
- Model ile anomali tespiti yapar
- `data/realtime_data.csv` dosyasına kaydeder

**Beklenen çıktı:**
```
🔄 İterasyon 1 - 14:30:15
⚠️ Trafo 5: Yüksek risk tespit edildi! (Risk: 85.3)
📈 Özet:
   • Yüksek Risk: 2 trafo
   • Orta Risk: 5 trafo
```

### Adım 2: Backend API'yi Başlatın

Terminal 2'de (YENİ TERMİNAL):

```powershell
# Sanal ortamı aktifleştir
.\venv\Scripts\Activate.ps1

# Flask API'yi başlat
python api_server.py
```

**Beklenen çıktı:**
```
🚀 Flask API Server Başlatılıyor
🌐 Server: http://localhost:5000
```

API çalışıyor olmalı! Bu terminali açık bırakın.

### Adım 3: Web Dashboard'u Başlatın

Terminal 3'te (YENİ TERMİNAL):

```powershell
# web-dashboard klasörüne git
cd web-dashboard

# Node.js paketlerini yükle (İLK SEFER İÇİN)
npm install

# Geliştirme sunucusunu başlat
npm run dev
```

**Beklenen çıktı:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Adım 4: Tarayıcıda Açın

1. Tarayıcınızda `http://localhost:3000` adresine gidin
2. Haritada trafoları görmelisiniz:
   - 🟢 Yeşil: Düşük risk
   - 🟡 Sarı: Orta risk  
   - 🔴 Kırmızı: Yüksek risk
3. Bir trafoya tıklayın → Sağ panelde detaylar açılır
4. Sağ panelde bildirimleri görün

## 📋 Çalışma Senaryosu

### Senaryo 1: Her Şeyi Birlikte Çalıştırma

**3 Terminal Açık Olmalı:**

1. **Terminal 1**: Simülasyon çalışıyor (`python simulasyon.py`)
2. **Terminal 2**: API çalışıyor (`python api_server.py`)
3. **Terminal 3**: Dashboard çalışıyor (`npm run dev`)

**Tarayıcı**: `http://localhost:3000`

Bu şekilde:
- Simülasyon veri üretir
- API veriyi sunar
- Dashboard canlı olarak gösterir

### Senaryo 2: Sadece Dashboard (Test İçin)

Eğer simülasyon çalışmıyorsa, dashboard yine de çalışır ama veri olmayabilir.

## 🎨 Dashboard Özellikleri

### Ana Ekran
- **Sol**: İnteraktif harita (İzmir bölgesi)
- **Sağ**: Bildirim akışı veya trafo detayları
- **Üst**: Özet istatistikler

### Trafo Detayları
Bir trafoya tıkladığınızda:
- Sensör değerleri
- Risk skoru
- Trend grafiği (son 7 gün)

### Bildirimler
- Yüksek riskli trafolar
- Otomatik izolasyon uyarıları
- Anomali tespitleri

## ⚠️ Sorun Giderme

### "npm: command not found"
Node.js yüklü değil. [Node.js indirin](https://nodejs.org/)

### "Port 5000 already in use"
Başka bir program 5000 portunu kullanıyor. `api_server.py` dosyasında portu değiştirin.

### "Port 3000 already in use"
Başka bir program 3000 portunu kullanıyor. Vite otomatik olarak 3001'e geçer.

### Dashboard'da veri görünmüyor
1. Simülasyon çalışıyor mu? (`python simulasyon.py`)
2. API çalışıyor mu? (`python api_server.py`)
3. Tarayıcı konsolunda hata var mı? (F12)

### API'de "Model yüklenemedi" hatası
Önce model eğitimi yapın: `python model_egit.py`

## 🎯 Sonraki Geliştirmeler

- [ ] Firebase/MongoDB entegrasyonu
- [ ] SMS bildirim simülasyonu
- [ ] Ekonomi modülü detaylandırma
- [ ] Daha fazla grafik türü
- [ ] Export/Import özellikleri

## 💡 İpuçları

1. **İlk Çalıştırma**: Tüm adımları sırayla yapın
2. **Geliştirme**: Dashboard kodunu değiştirdiğinizde otomatik yenilenir
3. **Veri**: Simülasyonu uzun süre çalıştırırsanız daha fazla veri olur
4. **Performans**: 50 trafo için sistem rahatlıkla çalışır

---

**Başarılar! 🚀**

