# 🚀 Hızlı Başlangıç Kılavuzu

## VS Code'da Python ile Çalışma

### 1. Sanal Ortamı Aktifleştirme

VS Code terminalinde (PowerShell):

```powershell
# Sanal ortamı aktifleştir
.\venv\Scripts\Activate.ps1
```

Eğer hata alırsanız:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Paketleri Yükleme

```powershell
pip install -r requirements.txt
```

Bu işlem birkaç dakika sürebilir. Tüm paketler yüklendikten sonra devam edin.

### 3. İlk Adım: Veri Üretimi

```powershell
python veri_uret.py
```

**Ne yapar?**
- 50 trafo için 1 yıllık veri üretir
- Normal günlük değişimleri simüle eder
- Arıza senaryolarını ekler
- `data/sensor_data.csv` dosyasına kaydeder

**Beklenen süre:** 2-5 dakika (bilgisayarınıza bağlı)

**Başarılı çıktı:**
```
✅ Veri üretimi başarıyla tamamlandı!
💾 Veri kaydedildi: data/sensor_data.csv
```

### 4. İkinci Adım: Model Eğitimi

```powershell
python model_egit.py
```

**Ne yapar?**
- Üretilen veriyi yükler
- Isolation Forest modelini eğitir
- Model performansını değerlendirir
- `models/anomali_model.pkl` dosyasına kaydeder

**Beklenen süre:** 1-3 dakika

**Başarılı çıktı:**
```
✅ Model eğitimi başarıyla tamamlandı!
💾 Model kaydedildi: models/anomali_model.pkl
```

### 5. Üçüncü Adım: Simülasyon

```powershell
python simulasyon.py
```

**Ne yapar?**
- Gerçek zamanlı veri akışını simüle eder
- Her 5 saniyede bir veri üretir
- Model ile anomali tespiti yapar
- Risk skorlarını hesaplar
- Bildirimleri gösterir

**Durdurmak için:** `Ctrl + C`

**Örnek çıktı:**
```
🔄 İterasyon 1 - 14:30:15
⚠️ Trafo 5: Yüksek risk tespit edildi! (Risk: 85.3)
📈 Özet:
   • Yüksek Risk: 2 trafo
   • Orta Risk: 5 trafo
```

## ⚠️ Sorun Giderme

### "ModuleNotFoundError" hatası alıyorsanız:

1. Sanal ortamın aktif olduğundan emin olun (terminalde `(venv)` görünmeli)
2. Paketleri tekrar yükleyin:
   ```powershell
   pip install -r requirements.txt
   ```

### "FileNotFoundError" hatası alıyorsanız:

1. Önce `veri_uret.py` çalıştırın
2. Sonra `model_egit.py` çalıştırın
3. En son `simulasyon.py` çalıştırın

### VS Code Python interpreter seçimi:

1. `Ctrl + Shift + P` tuşlarına basın
2. "Python: Select Interpreter" yazın
3. `.\venv\Scripts\python.exe` seçin

## 📊 Veri Dosyalarını Kontrol Etme

Üretilen verileri görmek için:

```powershell
# CSV dosyasını aç (Excel veya VS Code ile)
code data/sensor_data.csv
```

## 🎯 Sonraki Adımlar

1. ✅ Veri üretimi tamamlandı
2. ✅ Model eğitimi tamamlandı
3. ✅ Simülasyon çalışıyor
4. 🔜 Web Dashboard geliştirme (React.js)
5. 🔜 Harita entegrasyonu
6. 🔜 Firebase/MongoDB entegrasyonu

## 💡 İpuçları

- Simülasyonu kısa süreli çalıştırmak için: `python simulasyon.py --duration 5`
- Demo modunu kapatmak için: `python simulasyon.py --no-demo`
- Veri dosyaları `data/` klasöründe
- Model dosyası `models/` klasöründe

## 🆘 Yardım

Sorun yaşıyorsanız:
1. README.md dosyasını okuyun
2. Hata mesajını kontrol edin
3. Sanal ortamın aktif olduğundan emin olun
4. Tüm paketlerin yüklü olduğunu kontrol edin: `pip list`

---

**Başarılar! 🎉**

