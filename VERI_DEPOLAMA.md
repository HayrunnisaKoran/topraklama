# 📊 Veri Depolama Yapısı - Topraklama İzleme Sistemi

## 🗂️ Veri Depolama Yerleri

### 1. **CSV Dosyaları** (`data/` klasörü)

#### `data/sensor_data.csv`
- **Açıklama**: 1 yıllık eğitim verisi (tarihsel veri)
- **Boyut**: ~438,050 kayıt
- **Oluşturma**: `veri_uret.py` scripti ile
- **İçerik**:
  - `timestamp` - Zaman damgası
  - `transformer_id` - Trafo ID (1-50)
  - `toprak_direnci` - Toprak direnci (Ohm)
  - `kacak_akim` - Kaçak akım (mA)
  - `toprak_potansiyel` - Toprak potansiyeli (V)
  - `toprak_nemi` - Toprak nemi (%)
  - `toprak_sicakligi` - Toprak sıcaklığı (°C)
  - `korozyon_seviyesi` - Korozyon seviyesi
  - `anomali` - Anomali etiketi (0/1)

#### `data/realtime_data.csv`
- **Açıklama**: Gerçek zamanlı simülasyon verileri
- **Oluşturma**: `simulasyon.py` veya API çalışırken otomatik
- **İçerik**: `sensor_data.csv` + analiz sonuçları
  - `risk_score` - Risk skoru (0-100)
  - `risk_level` - Risk seviyesi (low/medium/high)
  - `is_anomaly` - Anomali durumu
  - `anomaly_score` - Anomali skoru

### 2. **Model Dosyaları** (`models/` klasörü)

#### `models/anomali_model.pkl`
- **Açıklama**: Eğitilmiş Isolation Forest modeli
- **Oluşturma**: `model_egit.py` scripti ile
- **İçerik**:
  - Model objesi
  - StandardScaler (veri ölçeklendirici)
- **Kullanım**: Anomali tespiti için

### 3. **Bellek (RAM) - Runtime Verileri**

#### Global Değişkenler (`app.py`)
```python
transformers = []  # 50 trafo simülatörü
detection_system = AnomalyDetectionSystem()  # Anomali tespit sistemi
storage = DataStorage()  # Veri depolama sınıfı
```

#### Bildirimler (`detection_system.alerts`)
- **Tip**: Python listesi
- **Boyut**: Son 100 bildirim
- **İçerik**:
  - `timestamp` - Zaman damgası
  - `type` - Bildirim tipi
  - `transformer_id` - Trafo ID
  - `message` - Bildirim mesajı
  - `severity` - Önem seviyesi (low/medium/high)

### 4. **Konfigürasyon Dosyası** (`config.py`)

#### Statik Veriler
- `TRANSFORMER_LOCATIONS` - Trafo lokasyonları (GPS koordinatları)
- `SENSOR_RANGES` - Sensör normal değer aralıkları
- `FAILURE_SCENARIOS` - Arıza senaryoları
- `RISK_SCORING` - Risk skorlama kriterleri
- `ECONOMICS` - Maliyet hesaplamaları

---

## 📈 Veri Akışı

```
1. Veri Üretimi (veri_uret.py)
   └─> data/sensor_data.csv (438,050 kayıt)

2. Model Eğitimi (model_egit.py)
   └─> models/anomali_model.pkl

3. Simülasyon/API (simulasyon.py / app.py)
   └─> data/realtime_data.csv (sürekli güncellenir)
   └─> detection_system.alerts (bellekte, son 100)

4. Frontend (React)
   └─> API'den veri çeker (GET /api/transformers)
   └─> Her 5 saniyede bir güncellenir
```

---

## 🔍 Chat Sistemi İçin Kullanılabilir Veriler

### ✅ Kullanılabilir Veri Kaynakları

1. **CSV Dosyaları**
   - `data/sensor_data.csv` - Tarihsel veri (eğitim için)
   - `data/realtime_data.csv` - Gerçek zamanlı veri (sorgular için)

2. **API Endpoints**
   - `/api/transformers` - Tüm trafolar
   - `/api/transformers/<id>` - Trafo detayı
   - `/api/transformers/<id>/history` - Trafo geçmişi
   - `/api/dashboard/stats` - İstatistikler
   - `/api/alerts` - Bildirimler
   - `/api/config` - Sistem konfigürasyonu

3. **Model Bilgileri**
   - Model performans metrikleri
   - Anomali tespit sonuçları

4. **Konfigürasyon**
   - Trafo lokasyonları
   - Sensör aralıkları
   - Risk kriterleri

### 🎯 Chat Sistemi İçin Önerilen Veri Kullanımı

#### 1. **Soru-Cevap Veritabanı Oluşturma**
```python
# Chat için veri hazırlama
chat_data = {
    'sensor_data': pd.read_csv('data/sensor_data.csv'),
    'realtime_data': pd.read_csv('data/realtime_data.csv'),
    'transformers': TRANSFORMER_LOCATIONS,
    'config': {
        'sensor_ranges': SENSOR_RANGES,
        'risk_scoring': RISK_SCORING
    },
    'alerts': detection_system.alerts
}
```

#### 2. **Chat İçin Veri Formatı**
```json
{
  "context": {
    "transformer_id": 1,
    "sensor_data": {...},
    "risk_score": 25.5,
    "history": [...]
  },
  "question": "Trafo 1'in durumu nedir?",
  "answer": "Trafo 1 şu anda düşük risk seviyesinde..."
}
```

#### 3. **Dinamik Veri Erişimi**
- Chat sistemi API'yi kullanarak güncel veri çekebilir
- CSV dosyalarından tarihsel analiz yapabilir
- Model sonuçlarını açıklayabilir

---

## ⚠️ Dikkat Edilmesi Gerekenler

### 1. **Veri Boyutu**
- `sensor_data.csv` çok büyük (438K kayıt)
- Chat için örnekleme veya özetleme gerekebilir

### 2. **Gerçek Zamanlı Veri**
- `realtime_data.csv` sürekli güncellenir
- Chat sistemi güncel veriyi API'den almalı

### 3. **Bellek Kullanımı**
- `alerts` listesi sınırlı (100 kayıt)
- Büyük veri setleri için streaming gerekebilir

### 4. **Veri Formatı**
- CSV dosyaları Pandas ile okunur
- JSON formatına dönüştürülmesi gerekebilir

---

## 🚀 Chat Sistemi Entegrasyonu İçin Öneriler

### 1. **Veri Erişim Katmanı**
```python
class ChatDataAccess:
    def __init__(self):
        self.api_base = 'http://localhost:5000/api'
        self.csv_data = None
    
    def get_transformer_info(self, transformer_id):
        # API'den güncel veri
        pass
    
    def get_historical_data(self, transformer_id, days=30):
        # CSV'den tarihsel veri
        pass
    
    def get_statistics(self):
        # Dashboard istatistikleri
        pass
```

### 2. **Context Builder**
```python
def build_chat_context(question, transformer_id=None):
    """Chat için context oluştur"""
    context = {
        'current_time': datetime.now(),
        'system_stats': get_dashboard_stats(),
    }
    
    if transformer_id:
        context['transformer'] = get_transformer(transformer_id)
        context['history'] = get_transformer_history(transformer_id)
    
    return context
```

### 3. **Veri Özetleme**
```python
def summarize_data_for_chat(data):
    """Büyük veri setlerini chat için özetle"""
    # Önemli metrikleri çıkar
    # Trend analizi yap
    # Anomali durumlarını vurgula
    pass
```

---

## 📝 Sonuç

**Veri Depolama Yerleri:**
1. ✅ CSV dosyaları (`data/` klasörü)
2. ✅ Model dosyaları (`models/` klasörü)
3. ✅ Bellek (runtime verileri)
4. ✅ Konfigürasyon (`config.py`)

**Chat Sistemi İçin:**
- API endpoint'lerini kullanarak güncel veri alın
- CSV dosyalarından tarihsel analiz yapın
- Model sonuçlarını açıklayın
- Dinamik veri akışını koruyun

