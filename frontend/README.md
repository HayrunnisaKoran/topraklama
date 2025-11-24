# Topraklama İzleme Sistemi - Frontend

React.js ile geliştirilmiş web dashboard.

## Kurulum

```bash
npm install
```

## Çalıştırma

```bash
npm run dev
```

Frontend `http://localhost:5173` adresinde çalışacak.

## Özellikler

- 📊 Dashboard - Genel görünüm ve istatistikler
- 🗺️ Harita Görünümü - Trafo lokasyonları
- 📋 Trafo Listesi - Tüm trafoların listesi
- 🔍 Trafo Detayı - Detaylı bilgiler ve grafikler
- ⚠️ Anomali Tespiti - Gerçek zamanlı uyarılar
- 🔄 Otomatik Güncelleme - Her 5 saniyede bir veri güncelleme

## API Bağlantısı

Backend API'nin `http://localhost:5000` adresinde çalışıyor olması gerekir.

## Teknolojiler

- React 19
- Vite
- React Router
- Leaflet (Harita)
- Recharts (Grafikler)
- Axios (HTTP İstekleri)
