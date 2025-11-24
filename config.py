"""
Proje Konfigürasyon Dosyası
Topraklama İzleme ve Anomali Tespiti Sistemi
"""

import random

# Trafo Sayısı ve Konfigürasyonu
NUM_TRANSFORMERS = 120  # Toplam trafo sayısı

# İzmir Bölgesi Sınırları (Rastgele dağılım için)
IZMIR_BOUNDS = {
    'lat_min': 38.20,   # Güney sınır
    'lat_max': 38.70,   # Kuzey sınır
    'lon_min': 26.80,   # Batı sınır
    'lon_max': 27.50    # Doğu sınır
}

# İzmir Bölgeleri
IZMIR_REGIONS = [
    'Alsancak', 'Bornova', 'Karşıyaka', 'Konak', 'Buca',
    'Çiğli', 'Bayraklı', 'Narlıdere', 'Balçova', 'Karabağlar',
    'Gaziemir', 'Kemalpaşa', 'Urla', 'Menderes', 'Torbalı',
    'Selçuk', 'Foça', 'Aliağa', 'Menemen', 'Bergama'
]

# Trafo Lokasyonları (İzmir bölgesinde rastgele dağıtılmış)
TRANSFORMER_LOCATIONS = []
for i in range(NUM_TRANSFORMERS):
    lat = random.uniform(IZMIR_BOUNDS['lat_min'], IZMIR_BOUNDS['lat_max'])
    lon = random.uniform(IZMIR_BOUNDS['lon_min'], IZMIR_BOUNDS['lon_max'])
    region = random.choice(IZMIR_REGIONS)
    TRANSFORMER_LOCATIONS.append({
        'id': i+1,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'name': f'Trafo {i+1}',
        'region': region
    })

# Sensör Parametreleri - Normal Değer Aralıkları
SENSOR_RANGES = {
    'toprak_direnci': {
        'min': 2.0,      # Ohm - Minimum normal değer
        'max': 5.0,      # Ohm - Maksimum normal değer
        'unit': 'Ohm'
    },
    'kacak_akim': {
        'min': 0.0,      # mA - Minimum normal değer
        'max': 10.0,     # mA - Maksimum normal değer
        'unit': 'mA'
    },
    'toprak_potansiyel': {
        'min': -5.0,     # V - Minimum normal değer
        'max': 5.0,      # V - Maksimum normal değer
        'unit': 'V'
    },
    'toprak_nemi': {
        'min': 20.0,     # % - Minimum normal değer
        'max': 60.0,     # % - Maksimum normal değer
        'unit': '%'
    },
    'toprak_sicakligi': {
        'min': 5.0,      # °C - Minimum normal değer
        'max': 35.0,     # °C - Maksimum normal değer
        'unit': '°C'
    },
    'korozyon_seviyesi': {
        'min': 0.0,      # 0-100 arası skala
        'max': 30.0,     # Normal maksimum değer
        'unit': 'index'
    }
}

# Arıza Senaryoları
FAILURE_SCENARIOS = {
    'yagmur': {
        'date': '2024-11-05',  # Kasım ayının 5'i
        'effect': {
            'toprak_direnci': -0.5,  # Direnç düşer
            'toprak_nemi': +20.0     # Nem artar
        }
    },
    'korozon': {
        'date': '2024-12-10',  # Aralık ayının 10'u
        'effect': {
            'toprak_direnci': 0.1,   # Her saat 0.1 artarak 20 Ohm'a çıkar
            'korozyon_seviyesi': 2.0  # Korozyon artar
        },
        'duration_hours': 100  # 100 saat sürer
    },
    'kaçak_akim': {
        'date': '2024-10-15',
        'effect': {
            'kacak_akim': 50.0,  # Ani yükseliş
            'toprak_potansiyel': 15.0
        }
    }
}

# Veri Üretim Parametreleri
DATA_GENERATION = {
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'frequency': '1H',  # Her saat bir veri
    'output_file': 'data/sensor_data.csv'
}

# Model Parametreleri
MODEL_CONFIG = {
    'algorithm': 'isolation_forest',  # 'isolation_forest' veya 'lstm_autoencoder'
    'contamination': 0.1,  # %10 anomali beklentisi
    'model_path': 'models/anomali_model.pkl'
}

# Simülasyon Parametreleri
SIMULATION_CONFIG = {
    'update_interval': 5,  # Saniye cinsinden (demo için hızlı)
    'real_time_scale': 3600,  # Gerçek hayatta 1 saat = simülasyonda 1 saniye
    'enable_auto_isolation': True  # Otomatik yük izolasyonu aktif mi?
}

# Risk Skorlama
RISK_SCORING = {
    'low': {'min': 0, 'max': 40, 'color': 'green'},
    'medium': {'min': 40, 'max': 70, 'color': 'yellow'},
    'high': {'min': 70, 'max': 100, 'color': 'red'}
}

# Ekonomi Modülü - Maliyet Hesaplamaları
ECONOMICS = {
    'preventive_maintenance_cost': 5000,      # TL - Önleyici bakım maliyeti
    'reactive_maintenance_cost': 50000,       # TL - Reaktif bakım maliyeti
    'downtime_cost_per_hour': 10000,          # TL - Kesinti maliyeti/saat
    'average_downtime_hours': 8                # Ortalama kesinti süresi (saat)
}

