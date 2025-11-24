# 🚀 Projeyi Başlatma Kılavuzu

## Backend API'yi Başlatma

**Terminal 1'de (PowerShell):**

```powershell
# Ana dizine git
cd C:\Topraklama_Izleme_Sistemi\topraklama

# API'yi başlat
python app.py
```

**Beklenen çıktı:**
```
============================================================
Flask API Server Baslatiliyor...
============================================================
[OK] Sistem baslatildi

API Endpoints:
   GET  /api/health - Sistem saglik kontrolu
   GET  /api/transformers - Tum trafolar
   ...
Server: http://localhost:5000
============================================================
 * Running on http://127.0.0.1:5000
```

## Frontend'i Başlatma

**Terminal 2'de (YENİ TERMİNAL):**

```powershell
# Frontend dizinine git
cd C:\Topraklama_Izleme_Sistemi\topraklama\frontend

# Frontend'i başlat
npm run dev
```

**Beklenen çıktı:**
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## Tarayıcıda Açma

1. Tarayıcınızda `http://localhost:5173` adresine gidin
2. Dashboard görünmelidir

## Sorun Giderme

### API başlamıyorsa:

1. Port 5000 kullanımda mı kontrol edin:
   ```powershell
   netstat -ano | findstr :5000
   ```

2. Model dosyası var mı kontrol edin:
   ```powershell
   dir models\anomali_model.pkl
   ```

3. Veri dosyası var mı kontrol edin:
   ```powershell
   dir data\sensor_data.csv
   ```

### Frontend bağlanamıyorsa:

1. Backend API'nin çalıştığından emin olun
2. Tarayıcı konsolunda (F12) hataları kontrol edin
3. `http://localhost:5000/api/health` adresini tarayıcıda açın - JSON response görmelisiniz

## Notlar

- Backend ve Frontend ayrı terminallerde çalışmalı
- Backend önce başlatılmalı
- Her iki terminal de açık kalmalı

