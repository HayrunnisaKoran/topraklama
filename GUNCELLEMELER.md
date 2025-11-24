# 🔄 Yapılan Güncellemeler

## ✅ Tamamlanan Değişiklikler

### 1. Trafo Sayısı: 50 → 120
- `config.py` dosyasında `NUM_TRANSFORMERS = 120` olarak güncellendi
- Artık sistem 120 trafoyu izleyebilir

### 2. Trafolar Rastgele Dağıtıldı
- Önceden: Trafolar sıralı grid şeklinde diziliyordu
- Şimdi: Trafolar İzmir bölgesi içinde rastgele koordinatlara yerleştiriliyor
- Her trafo için rastgele bölge atanıyor (20 farklı İzmir bölgesi)

### 3. Risk Dağılımı Düzeltildi
- Önceden: Tüm trafolar yüksek risk gösteriyordu
- Şimdi: Gerçekçi risk dağılımı:
  - **%70 Normal** (Yeşil - Düşük risk)
  - **%20 Orta Risk** (Turuncu)
  - **%10 Yüksek Risk** (Kırmızı)
  - **Arızalı Trafolar** (Koyu kırmızı - Risk >= 80)

### 4. Harita Renkleri İyileştirildi
- 🟢 **Yeşil**: Normal/Düşük risk (0-40)
- 🟡 **Turuncu**: Orta risk (40-70)
- 🔴 **Kırmızı**: Yüksek risk (70-80)
- 🔴 **Koyu Kırmızı**: Arızalı (80+)

## 🚀 Yeni Özellikler

### Trafo Kategorileri
Her trafo artık 3 kategoriden birine ait:
1. **Normal**: İdeal sensör değerleri, düşük risk
2. **Orta Risk**: Biraz yüksek değerler, orta risk
3. **Yüksek Risk**: Anomali değerler, yüksek risk

### Rastgele Lokasyonlar
- Trafolar İzmir'in farklı bölgelerine rastgele dağıtılıyor
- 20 farklı bölge: Alsancak, Bornova, Karşıyaka, Konak, Buca, Çiğli, Bayraklı, Narlıdere, Balçova, Karabağlar, Gaziemir, Kemalpaşa, Urla, Menderes, Torbalı, Selçuk, Foça, Aliağa, Menemen, Bergama

## 📝 Yapmanız Gerekenler

### 1. Veriyi Yeniden Üretin (Opsiyonel)
Eğer tarihsel veri üretmek istiyorsanız:
```powershell
python veri_uret.py
```
Bu komut 120 trafo için veri üretecek (daha uzun sürebilir).

### 2. Modeli Yeniden Eğitin (Önerilen)
Yeni trafo sayısı için modeli yeniden eğitin:
```powershell
python model_egit.py
```

### 3. Simülasyonu Çalıştırın
```powershell
python simulasyon.py --duration 5
```

Artık haritada:
- ✅ 120 trafo görünecek
- ✅ Trafolar rastgele dağıtılmış olacak
- ✅ Farklı renklerde trafolar olacak (yeşil, turuncu, kırmızı)
- ✅ Arızalı trafolar koyu kırmızı olacak

## 🎯 Beklenen Sonuç

Simülasyon çalıştığında:
- **~84 trafo** yeşil (normal)
- **~24 trafo** turuncu (orta risk)
- **~12 trafo** kırmızı (yüksek risk)
- **~6-8 trafo** koyu kırmızı (arızalı)

Bu dağılım gerçekçi bir senaryoyu yansıtır.

---

**Not**: Eğer hala tüm trafolar aynı renkte görünüyorsa, simülasyonu durdurup yeniden başlatın. Yeni kod değişiklikleri uygulanacaktır.

