# 🔧 Sorun ve Çözüm: Tüm Trafolar Yüksek Risk Görünüyor

## ❌ Sorun

Haritada **tüm 50 trafo kırmızı (yüksek risk)** görünüyordu. Normal trafoların yeşil/sarı olması gerekiyordu.

## 🔍 Nedenler

### 1. Risk Skorlama Fonksiyonu Çok Agresifti

**Eski Kod:**
- Isolation Forest skorlarını yanlış normalize ediyordu
- Tüm skorları yüksek risk olarak yorumluyordu
- Normal trafolar için bile yüksek risk puanı veriyordu

**Yeni Kod:**
- Skorları doğru aralığa normalize ediyor (-0.6 ile -0.1 arası)
- Normal trafolar için düşük risk (0-40)
- Orta riskli trafolar için (40-70)
- Yüksek riskli trafolar için (70-100)

### 2. Simülasyonda Tüm Trafolar Yüksek Değerler Üretiyordu

**Eski Kod:**
- Tüm trafolar için yüksek değerlere izin veriyordu
- Normal trafolar bile anomali değerleri üretebiliyordu

**Yeni Kod:**
- Normal trafolar için değerler normal aralıkta kalıyor (2-7.5 Ohm)
- Sadece arızalı trafolar yüksek değerler üretiyor

### 3. Çok Fazla Trafoya Arıza Senaryosu Uygulanıyordu

**Eski Kod:**
- Demo modunda sadece 2 trafoya arıza ekliyordu ama risk hesaplama yanlıştı

**Yeni Kod:**
- 4 trafoya arıza ekliyor (Trafo 5, 10, 15, 20)
- Diğer 46 trafo normal durumda

## ✅ Çözüm

### 1. Risk Skorlama Düzeltildi (`model_egit.py`)

```python
# Yeni risk skorlama:
# - Normal trafolar: 0-40 (yeşil)
# - Orta risk: 40-70 (sarı)
# - Yüksek risk: 70-100 (kırmızı)
```

### 2. Simülasyon Düzeltildi (`simulasyon.py`)

```python
# Normal trafolar için değerler sınırlandı:
- Toprak direnci: 2-7.5 Ohm (normal)
- Kaçak akım: 0-15 mA (normal)
- Korozyon: 0-45 (normal)

# Arızalı trafolar için yüksek değerlere izin veriliyor
```

### 3. Arıza Senaryoları Düzenlendi

```python
# Sadece 4 trafoya arıza:
- Trafo 5, 15: Kademeli korozyon
- Trafo 10, 20: Ani kaçak akım
- Diğer 46 trafo: Normal
```

## 🚀 Şimdi Ne Yapmalısınız?

### 1. Simülasyonu Yeniden Başlatın

```powershell
# Eski simülasyonu durdurun (Ctrl+C)
# Yeni simülasyonu başlatın
python simulasyon.py --duration 5
```

### 2. Dashboard'u Yenileyin

Tarayıcıda `F5` tuşuna basın veya sayfayı yenileyin.

### 3. Beklenen Sonuç

Artık haritada:
- 🟢 **Yeşil marker'lar**: Normal trafolar (risk < 40)
- 🟡 **Sarı marker'lar**: Orta riskli trafolar (risk 40-70)
- 🔴 **Kırmızı marker'lar**: Yüksek riskli trafolar (risk > 70)

**Tahmini dağılım:**
- 🟢 Yeşil: ~40-45 trafo
- 🟡 Sarı: ~3-5 trafo
- 🔴 Kırmızı: ~4-5 trafo (arızalı olanlar)

## 📊 Test Etmek İçin

1. Simülasyonu çalıştırın
2. Dashboard'u açın
3. Haritada renk dağılımını kontrol edin
4. Header'daki istatistikleri kontrol edin:
   - Yüksek Risk: ~4-5 olmalı (50 değil!)
   - Orta Risk: ~3-5 olmalı
   - Toplam Trafo: 50

## ⚠️ Hala Sorun Varsa

Eğer hala tüm trafolar kırmızı görünüyorsa:

1. **Modeli yeniden eğitin:**
   ```powershell
   python model_egit.py
   ```

2. **Eski veriyi silin:**
   ```powershell
   # data/realtime_data.csv dosyasını silin
   del data\realtime_data.csv
   ```

3. **Simülasyonu yeniden başlatın**

---

**Not:** Değişiklikler hemen etkili olacaktır. Sadece simülasyonu yeniden başlatmanız yeterli!

