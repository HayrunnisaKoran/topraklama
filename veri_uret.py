"""
Veri Üretim Scripti
Topraklama sistemleri için sentetik sensör verisi üretir.
1 yıllık normal veri + arıza senaryoları içerir.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from config import (
    NUM_TRANSFORMERS, 
    TRANSFORMER_LOCATIONS,
    SENSOR_RANGES,
    FAILURE_SCENARIOS,
    DATA_GENERATION
)

def generate_normal_data(transformer_id, start_date, end_date):
    """
    Normal koşullarda sensör verisi üretir.
    
    Args:
        transformer_id: Trafo ID (1-50)
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
    
    Returns:
        DataFrame: Sensör verileri
    """
    # Tarih aralığı oluştur (her saat bir veri)
    date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
    
    # Her trafo için biraz farklı temel değerler (gerçekçilik için)
    base_resistance = np.random.uniform(2.5, 4.5)
    base_leakage = np.random.uniform(2.0, 8.0)
    base_potential = np.random.uniform(-2.0, 2.0)
    base_moisture = np.random.uniform(30.0, 50.0)
    base_temp = np.random.uniform(15.0, 25.0)
    base_corrosion = np.random.uniform(5.0, 20.0)
    
    data = []
    
    for timestamp in date_range:
        # Mevsimsel değişimler (yazın sıcaklık artar, kışın nem değişir)
        month = timestamp.month
        seasonal_temp_factor = 10 * np.sin(2 * np.pi * month / 12)  # Mevsimsel değişim
        seasonal_moisture_factor = 10 * np.cos(2 * np.pi * month / 12)
        
        # Normal günlük dalgalanmalar (rastgele ama mantıklı)
        resistance = base_resistance + np.random.normal(0, 0.3)
        resistance = np.clip(resistance, SENSOR_RANGES['toprak_direnci']['min'], 
                            SENSOR_RANGES['toprak_direnci']['max'])
        
        leakage = base_leakage + np.random.normal(0, 1.5)
        leakage = np.clip(leakage, SENSOR_RANGES['kacak_akim']['min'], 
                          SENSOR_RANGES['kacak_akim']['max'])
        
        potential = base_potential + np.random.normal(0, 1.0)
        potential = np.clip(potential, SENSOR_RANGES['toprak_potansiyel']['min'],
                           SENSOR_RANGES['toprak_potansiyel']['max'])
        
        moisture = base_moisture + seasonal_moisture_factor + np.random.normal(0, 5.0)
        moisture = np.clip(moisture, SENSOR_RANGES['toprak_nemi']['min'],
                          SENSOR_RANGES['toprak_nemi']['max'])
        
        temperature = base_temp + seasonal_temp_factor + np.random.normal(0, 3.0)
        temperature = np.clip(temperature, SENSOR_RANGES['toprak_sicakligi']['min'],
                             SENSOR_RANGES['toprak_sicakligi']['max'])
        
        corrosion = base_corrosion + np.random.normal(0, 2.0)
        corrosion = np.clip(corrosion, SENSOR_RANGES['korozyon_seviyesi']['min'],
                           SENSOR_RANGES['korozyon_seviyesi']['max'])
        
        data.append({
            'timestamp': timestamp,
            'transformer_id': transformer_id,
            'toprak_direnci': round(resistance, 2),
            'kacak_akim': round(leakage, 2),
            'toprak_potansiyel': round(potential, 2),
            'toprak_nemi': round(moisture, 2),
            'toprak_sicakligi': round(temperature, 2),
            'korozyon_seviyesi': round(corrosion, 2),
            'anomali': 0  # Normal veri
        })
    
    return pd.DataFrame(data)


def apply_failure_scenario(df, transformer_id, scenario_name, scenario_config):
    """
    Belirli bir trafo için arıza senaryosu uygular.
    
    Args:
        df: Veri DataFrame'i
        scenario_name: Senaryo adı ('yagmur', 'korozon', 'kaçak_akim')
        scenario_config: Senaryo konfigürasyonu
    """
    scenario_date = pd.to_datetime(scenario_config['date'])
    
    # Senaryo tarihindeki verileri bul
    mask = (df['transformer_id'] == transformer_id) & \
           (df['timestamp'] >= scenario_date) & \
           (df['timestamp'] < scenario_date + timedelta(days=7))  # 7 gün etkisi
    
    if scenario_name == 'yagmur':
        # Yağmur senaryosu: Direnç düşer, nem artar
        df.loc[mask, 'toprak_direnci'] = np.clip(
            df.loc[mask, 'toprak_direnci'] + scenario_config['effect']['toprak_direnci'],
            0.5, 5.0
        )
        df.loc[mask, 'toprak_nemi'] = np.clip(
            df.loc[mask, 'toprak_nemi'] + scenario_config['effect']['toprak_nemi'],
            20.0, 80.0
        )
        df.loc[mask, 'anomali'] = 1  # Anomali işaretle
    
    elif scenario_name == 'korozon':
        # Korozyon senaryosu: Direnç kademeli olarak artar
        duration = scenario_config.get('duration_hours', 100)
        affected_data = df[mask].copy()
        
        for i, idx in enumerate(affected_data.index[:duration]):
            hours_passed = i
            resistance_increase = scenario_config['effect']['toprak_direnci'] * hours_passed
            corrosion_increase = scenario_config['effect']['korozyon_seviyesi'] * hours_passed
            
            df.loc[idx, 'toprak_direnci'] = min(
                df.loc[idx, 'toprak_direnci'] + resistance_increase,
                25.0  # Maksimum 25 Ohm'a çıkar
            )
            df.loc[idx, 'korozyon_seviyesi'] = min(
                df.loc[idx, 'korozyon_seviyesi'] + corrosion_increase,
                100.0
            )
            df.loc[idx, 'anomali'] = 1
    
    elif scenario_name == 'kaçak_akim':
        # Kaçak akım senaryosu: Ani yükseliş
        df.loc[mask, 'kacak_akim'] = scenario_config['effect']['kacak_akim']
        df.loc[mask, 'toprak_potansiyel'] = scenario_config['effect']['toprak_potansiyel']
        df.loc[mask, 'anomali'] = 1


def generate_all_data():
    """
    Tüm trafolar için 1 yıllık veri üretir ve arıza senaryolarını uygular.
    """
    print("🚀 Veri üretimi başlıyor...")
    print(f"📊 {NUM_TRANSFORMERS} trafo için 1 yıllık veri üretilecek")
    
    start_date = DATA_GENERATION['start_date']
    end_date = DATA_GENERATION['end_date']
    
    all_data = []
    
    # Her trafo için veri üret
    for transformer_id in range(1, NUM_TRANSFORMERS + 1):
        print(f"  ⚡ Trafo {transformer_id}/{NUM_TRANSFORMERS} işleniyor...", end='\r')
        
        df = generate_normal_data(transformer_id, start_date, end_date)
        all_data.append(df)
    
    print(f"\n✅ Normal veri üretimi tamamlandı!")
    
    # Tüm verileri birleştir
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"📈 Toplam {len(combined_df):,} kayıt oluşturuldu")
    
    # Arıza senaryolarını uygula
    print("\n🔧 Arıza senaryoları uygulanıyor...")
    
    # Senaryo 1: Yağmur (Trafo 5, 15, 25'te)
    for trafo_id in [5, 15, 25]:
        apply_failure_scenario(combined_df, trafo_id, 'yagmur', FAILURE_SCENARIOS['yagmur'])
        print(f"  🌧️  Trafo {trafo_id}: Yağmur senaryosu uygulandı")
    
    # Senaryo 2: Korozyon (Trafo 10, 20, 30'da)
    for trafo_id in [10, 20, 30]:
        apply_failure_scenario(combined_df, trafo_id, 'korozon', FAILURE_SCENARIOS['korozon'])
        print(f"  ⚠️  Trafo {trafo_id}: Korozyon senaryosu uygulandı")
    
    # Senaryo 3: Kaçak Akım (Trafo 7, 17, 27'de)
    for trafo_id in [7, 17, 27]:
        apply_failure_scenario(combined_df, trafo_id, 'kaçak_akim', FAILURE_SCENARIOS['kaçak_akim'])
        print(f"  ⚡ Trafo {trafo_id}: Kaçak akım senaryosu uygulandı")
    
    # Veriyi sırala (tarih ve trafo ID'ye göre)
    combined_df = combined_df.sort_values(['timestamp', 'transformer_id']).reset_index(drop=True)
    
    # CSV'ye kaydet
    output_dir = os.path.dirname(DATA_GENERATION['output_file'])
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    combined_df.to_csv(DATA_GENERATION['output_file'], index=False, encoding='utf-8-sig')
    print(f"\n💾 Veri kaydedildi: {DATA_GENERATION['output_file']}")
    
    # İstatistikler
    print("\n📊 Veri İstatistikleri:")
    print(f"  • Toplam kayıt: {len(combined_df):,}")
    print(f"  • Anomali kayıt: {combined_df['anomali'].sum():,} ({combined_df['anomali'].mean()*100:.2f}%)")
    print(f"  • Tarih aralığı: {combined_df['timestamp'].min()} - {combined_df['timestamp'].max()}")
    print(f"  • Trafo sayısı: {combined_df['transformer_id'].nunique()}")
    
    # Örnek veri göster
    print("\n📋 Örnek Veri (İlk 5 kayıt):")
    print(combined_df.head().to_string())
    
    return combined_df


if __name__ == "__main__":
    try:
        df = generate_all_data()
        print("\n✅ Veri üretimi başarıyla tamamlandı!")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

