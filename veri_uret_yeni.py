"""
Yeni Veri Üretim Scripti
Model kullanarak gerçekçi veri üretir ve Firebase'e kaydeder
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from model_egit import load_model, predict_anomaly, calculate_risk_score
from config import (
    NUM_TRANSFORMERS,
    TRANSFORMER_LOCATIONS,
    SENSOR_RANGES,
    DATA_GENERATION
)

def generate_realistic_data(transformer_id, category='normal', num_records=100):
    """
    Model kullanarak gerçekçi veri üretir.
    
    Args:
        transformer_id: Trafo ID
        category: 'normal', 'medium', 'high'
        num_records: Üretilecek kayıt sayısı
    """
    # Modeli yükle
    try:
        model, scaler = load_model()
        print(f"✅ Model yüklendi - Trafo {transformer_id}")
    except Exception as e:
        print(f"⚠️  Model yüklenemedi, varsayılan değerler kullanılacak: {e}")
        model = None
        scaler = None
    
    data = []
    location = TRANSFORMER_LOCATIONS[transformer_id - 1]
    
    # Kategoriye göre temel değerler
    if category == 'normal':
        base_resistance = np.random.uniform(2.5, 4.0)
        base_leakage = np.random.uniform(1.0, 6.0)
        base_corrosion = np.random.uniform(5.0, 15.0)
    elif category == 'medium':
        base_resistance = np.random.uniform(5.0, 8.0)
        base_leakage = np.random.uniform(8.0, 15.0)
        base_corrosion = np.random.uniform(20.0, 40.0)
    else:  # high
        base_resistance = np.random.uniform(10.0, 20.0)
        base_leakage = np.random.uniform(20.0, 50.0)
        base_corrosion = np.random.uniform(50.0, 90.0)
    
    start_date = datetime.now() - timedelta(days=30)  # Son 30 gün
    
    for i in range(num_records):
        timestamp = start_date + timedelta(hours=i * 6)  # Her 6 saatte bir
        
        # Normal dalgalanmalar
        resistance = base_resistance + np.random.normal(0, 0.3)
        leakage = base_leakage + np.random.normal(0, 1.5)
        potential = np.random.uniform(-2.0, 2.0)
        moisture = np.random.uniform(30.0, 50.0)
        temperature = np.random.uniform(15.0, 25.0)
        corrosion = base_corrosion + np.random.normal(0, 2.0)
        
        # Değerleri sınırlar içinde tut
        resistance = np.clip(resistance, 0.5, 25.0)
        leakage = np.clip(leakage, 0.0, 100.0)
        corrosion = np.clip(corrosion, 0.0, 100.0)
        
        sensor_data = {
            'timestamp': timestamp.isoformat(),
            'transformer_id': transformer_id,
            'toprak_direnci': round(resistance, 2),
            'kacak_akim': round(leakage, 2),
            'toprak_potansiyel': round(potential, 2),
            'toprak_nemi': round(moisture, 2),
            'toprak_sicakligi': round(temperature, 2),
            'korozyon_seviyesi': round(corrosion, 2),
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'name': location['name'],
            'region': location['region']
        }
        
        # Model ile analiz (varsa)
        if model and scaler:
            try:
                is_anomaly, anomaly_score = predict_anomaly(model, scaler, sensor_data)
                risk_score = calculate_risk_score(anomaly_score, sensor_data)
                
                # Kategoriye göre risk skorunu ayarla
                if category == 'normal':
                    risk_score = max(15, min(35, risk_score * 0.3))
                elif category == 'medium':
                    risk_score = max(45, min(65, risk_score * 0.6))
                else:
                    risk_score = max(75, min(95, risk_score * 0.9))
            except:
                # Model hatası durumunda kategoriye göre risk ver
                if category == 'normal':
                    risk_score = np.random.uniform(15, 35)
                elif category == 'medium':
                    risk_score = np.random.uniform(45, 65)
                else:
                    risk_score = np.random.uniform(75, 95)
        else:
            # Model yoksa kategoriye göre risk ver
            if category == 'normal':
                risk_score = np.random.uniform(15, 35)
            elif category == 'medium':
                risk_score = np.random.uniform(45, 65)
            else:
                risk_score = np.random.uniform(75, 95)
        
        # Risk seviyesi
        if risk_score < 40:
            risk_level = 'low'
        elif risk_score < 70:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        sensor_data.update({
            'is_anomaly': risk_score >= 80,
            'anomaly_score': round(anomaly_score if model else -0.3, 4),
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'risk_color': 'green' if risk_level == 'low' else ('yellow' if risk_level == 'medium' else 'red'),
            'anomali': 1 if risk_score >= 80 else 0
        })
        
        data.append(sensor_data)
    
    return pd.DataFrame(data)


def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("🔄 Yeni Veri Üretimi Başlıyor")
    print("=" * 60)
    
    # Klasör kontrolü
    os.makedirs('data', exist_ok=True)
    
    # Trafoları kategorilere dağıt
    np.random.seed(42)
    categories = []
    for i in range(NUM_TRANSFORMERS):
        rand = np.random.random()
        if rand < 0.70:  # %70 normal
            categories.append('normal')
        elif rand < 0.90:  # %20 orta risk
            categories.append('medium')
        else:  # %10 yüksek risk
            categories.append('high')
    
    all_data = []
    
    print(f"\n📊 {NUM_TRANSFORMERS} trafo için veri üretiliyor...")
    print(f"   • Normal: {categories.count('normal')} trafo")
    print(f"   • Orta Risk: {categories.count('medium')} trafo")
    print(f"   • Yüksek Risk: {categories.count('high')} trafo")
    print()
    
    for i, category in enumerate(categories, 1):
        print(f"  ⚡ Trafo {i}/{NUM_TRANSFORMERS} ({category})...", end='\r')
        df = generate_realistic_data(i, category, num_records=100)
        all_data.append(df)
    
    print(f"\n✅ Veri üretimi tamamlandı!")
    
    # Tüm verileri birleştir
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df.sort_values(['timestamp', 'transformer_id']).reset_index(drop=True)
    
    # CSV'ye kaydet
    output_file = DATA_GENERATION['output_file']
    combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 Veri kaydedildi: {output_file}")
    print(f"📈 Toplam kayıt: {len(combined_df):,}")
    print(f"📊 Risk Dağılımı:")
    print(f"   • Düşük Risk: {(combined_df['risk_score'] < 40).sum():,} kayıt")
    print(f"   • Orta Risk: {((combined_df['risk_score'] >= 40) & (combined_df['risk_score'] < 70)).sum():,} kayıt")
    print(f"   • Yüksek Risk: {(combined_df['risk_score'] >= 70).sum():,} kayıt")
    
    return combined_df


if __name__ == "__main__":
    try:
        df = main()
        print("\n✅ Veri üretimi başarıyla tamamlandı!")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

