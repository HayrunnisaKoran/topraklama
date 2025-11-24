"""
Simülasyon Scripti
Gerçek zamanlı sensör verisi akışını simüle eder.
IoT cihazlarından gelen verileri taklit eder ve anomali tespiti yapar.
"""

import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
from model_egit import load_model, predict_anomaly, calculate_risk_score
from config import (
    NUM_TRANSFORMERS,
    TRANSFORMER_LOCATIONS,
    SENSOR_RANGES,
    SIMULATION_CONFIG,
    RISK_SCORING,
    ECONOMICS
)

class TransformerSimulator:
    """
    Trafo simülatörü - Her trafo için sensör verisi üretir
    """
    
    def __init__(self, transformer_id, base_values=None):
        self.transformer_id = transformer_id
        self.location = TRANSFORMER_LOCATIONS[transformer_id - 1]
        
        # Her trafo için farklı temel değerler
        if base_values is None:
            self.base_values = {
                'toprak_direnci': np.random.uniform(2.5, 4.5),
                'kacak_akim': np.random.uniform(2.0, 8.0),
                'toprak_potansiyel': np.random.uniform(-2.0, 2.0),
                'toprak_nemi': np.random.uniform(30.0, 50.0),
                'toprak_sicakligi': np.random.uniform(15.0, 25.0),
                'korozyon_seviyesi': np.random.uniform(5.0, 20.0)
            }
        else:
            self.base_values = base_values
        
        self.isolation_status = True  # True = AÇIK, False = KAPALI
        self.risk_score = 0
        self.last_update = datetime.now()
    
    def generate_sensor_data(self):
        """
        Yeni sensör verisi üretir (normal dalgalanmalarla).
        
        Returns:
            dict: Sensör verileri
        """
        # Normal günlük dalgalanmalar
        data = {
            'timestamp': datetime.now().isoformat(),
            'transformer_id': self.transformer_id,
            'toprak_direnci': round(
                self.base_values['toprak_direnci'] + np.random.normal(0, 0.3),
                2
            ),
            'kacak_akim': round(
                self.base_values['kacak_akim'] + np.random.normal(0, 1.5),
                2
            ),
            'toprak_potansiyel': round(
                self.base_values['toprak_potansiyel'] + np.random.normal(0, 1.0),
                2
            ),
            'toprak_nemi': round(
                self.base_values['toprak_nemi'] + np.random.normal(0, 5.0),
                2
            ),
            'toprak_sicakligi': round(
                self.base_values['toprak_sicakligi'] + np.random.normal(0, 3.0),
                2
            ),
            'korozyon_seviyesi': round(
                self.base_values['korozyon_seviyesi'] + np.random.normal(0, 2.0),
                2
            ),
            'latitude': self.location['latitude'],
            'longitude': self.location['longitude'],
            'name': self.location['name'],
            'region': self.location['region']
        }
        
        # Değerleri sınırlar içinde tut
        data['toprak_direnci'] = np.clip(
            data['toprak_direnci'],
            SENSOR_RANGES['toprak_direnci']['min'],
            SENSOR_RANGES['toprak_direnci']['max'] * 5  # Anomali için daha yüksek sınır
        )
        data['kacak_akim'] = np.clip(
            data['kacak_akim'],
            SENSOR_RANGES['kacak_akim']['min'],
            SENSOR_RANGES['kacak_akim']['max'] * 10
        )
        
        return data
    
    def apply_failure_mode(self, failure_type='gradual'):
        """
        Arıza modunu simüle eder (test için).
        
        Args:
            failure_type: 'gradual' (kademeli) veya 'sudden' (ani)
        """
        if failure_type == 'gradual':
            # Kademeli korozyon
            self.base_values['toprak_direnci'] += 0.1
            self.base_values['korozyon_seviyesi'] += 1.0
        elif failure_type == 'sudden':
            # Ani kaçak akım
            self.base_values['kacak_akim'] = 50.0
            self.base_values['toprak_potansiyel'] = 15.0


class AnomalyDetectionSystem:
    """
    Anomali tespit sistemi - Model ile gerçek zamanlı analiz
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()
        self.alerts = []  # Bildirimler
    
    def load_model(self):
        """Eğitilmiş modeli yükler"""
        try:
            self.model, self.scaler = load_model()
            print("✅ Model yüklendi")
        except FileNotFoundError:
            print("⚠️  Model bulunamadı! Önce 'python model_egit.py' çalıştırın.")
            self.model = None
    
    def analyze_sensor_data(self, sensor_data):
        """
        Sensör verisini analiz eder ve anomali tespiti yapar.
        
        Args:
            sensor_data: Sensör verisi dict'i
        
        Returns:
            dict: Analiz sonuçları
        """
        if self.model is None:
            return {
                'is_anomaly': False,
                'anomaly_score': 0,
                'risk_score': 0,
                'risk_level': 'unknown'
            }
        
        # Anomali tespiti
        is_anomaly, anomaly_score = predict_anomaly(
            self.model, 
            self.scaler, 
            sensor_data
        )
        
        # Risk skoru hesapla
        risk_score = calculate_risk_score(anomaly_score, sensor_data)
        
        # Risk seviyesi belirle
        if risk_score < RISK_SCORING['low']['max']:
            risk_level = 'low'
        elif risk_score < RISK_SCORING['medium']['max']:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(anomaly_score, 4),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': RISK_SCORING[risk_level]['color']
        }
    
    def check_auto_isolation(self, transformer, analysis_result):
        """
        Otomatik yük izolasyonu kontrolü yapar.
        
        Args:
            transformer: TransformerSimulator objesi
            analysis_result: Analiz sonuçları
        """
        if not SIMULATION_CONFIG['enable_auto_isolation']:
            return
        
        # Yüksek risk durumunda otomatik izolasyon
        if analysis_result['risk_score'] >= 80 and transformer.isolation_status:
            transformer.isolation_status = False
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'auto_isolation',
                'transformer_id': transformer.transformer_id,
                'message': f"⚠️ Trafo {transformer.transformer_id} otomatik olarak izole edildi (Risk: {analysis_result['risk_score']:.1f})",
                'severity': 'high'
            }
            self.alerts.append(alert)
            print(f"🔴 {alert['message']}")
    
    def add_alert(self, transformer_id, message, severity='medium'):
        """Bildirim ekler"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': 'alert',
            'transformer_id': transformer_id,
            'message': message,
            'severity': severity
        }
        self.alerts.append(alert)
        
        # Son 100 bildirimi tut
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]


class DataStorage:
    """
    Veri depolama - Firebase Firestore (birincil) ve CSV (yedek)
    """
    
    def __init__(self, storage_type='firebase'):
        self.storage_type = storage_type
        self.data_file = 'data/realtime_data.csv'
        self.use_firebase = False
        self.firestore_db = None
        
        # Firebase başlat (eğer kullanılacaksa)
        if self.storage_type == 'firebase':
            try:
                from firebase_config import init_firebase, get_firestore, FIRESTORE_COLLECTION
                # firebase-key.json dosyası var mı kontrol et
                if os.path.exists('firebase-key.json'):
                    init_firebase('firebase-key.json')
                    self.firestore_db = get_firestore()
                    if self.firestore_db:
                        self.use_firebase = True
                        print("✅ Firebase depolama aktif")
                    else:
                        print("⚠️  Firebase başlatılamadı, CSV kullanılacak")
                        self.storage_type = 'csv'
                else:
                    print("ℹ️  firebase-key.json bulunamadı, CSV kullanılacak")
                    self.storage_type = 'csv'
            except Exception as e:
                print(f"⚠️  Firebase başlatma hatası: {e}")
                print("💡 CSV kullanılacak")
                self.storage_type = 'csv'
        
        # CSV için klasör oluştur
        self.ensure_directory()
    
    def ensure_directory(self):
        """Klasör yoksa oluştur"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def save_data(self, sensor_data, analysis_result):
        """
        Veriyi kaydeder (Firebase ve/veya CSV).
        
        Args:
            sensor_data: Sensör verisi
            analysis_result: Analiz sonuçları
        """
        # Veriyi birleştir
        record = {**sensor_data, **analysis_result}
        
        # Timestamp'i string'e çevir (Firebase için)
        if 'timestamp' in record and isinstance(record['timestamp'], str):
            record['timestamp'] = record['timestamp']
        else:
            record['timestamp'] = datetime.now().isoformat()
        
        # Firebase'e kaydet (birincil)
        if self.use_firebase and self.firestore_db:
            try:
                from firebase_config import save_to_firestore, FIRESTORE_COLLECTION
                # Firestore için timestamp'i datetime'a çevir (opsiyonel)
                firestore_record = record.copy()
                save_to_firestore(firestore_record, FIRESTORE_COLLECTION)
            except Exception as e:
                print(f"⚠️  Firebase kayıt hatası: {e}")
        
        # CSV'ye de kaydet (yedek)
        try:
            df = pd.DataFrame([record])
            if os.path.exists(self.data_file):
                df.to_csv(self.data_file, mode='a', header=False, index=False)
            else:
                df.to_csv(self.data_file, mode='w', header=True, index=False)
        except Exception as e:
            print(f"⚠️  CSV kayıt hatası: {e}")


def run_simulation(duration_minutes=10, demo_mode=True):
    """
    Simülasyonu çalıştırır.
    
    Args:
        duration_minutes: Simülasyon süresi (dakika)
        demo_mode: Demo modu (hızlı güncelleme)
    """
    print("=" * 60)
    print("🚀 Topraklama İzleme Simülasyonu Başlatılıyor")
    print("=" * 60)
    
    # Sistemleri başlat
    transformers = [
        TransformerSimulator(i+1) 
        for i in range(NUM_TRANSFORMERS)
    ]
    
    detection_system = AnomalyDetectionSystem()
    # Firebase kullan (firebase-key.json varsa), yoksa CSV
    storage = DataStorage(storage_type='firebase')
    
    # Test için bazı trafolara arıza modu ekle
    if demo_mode:
        print("\n🔧 Demo modu: Bazı trafolara arıza senaryosu uygulanıyor...")
        transformers[4].apply_failure_mode('gradual')  # Trafo 5
        transformers[9].apply_failure_mode('sudden')   # Trafo 10
        print("   ✅ Trafo 5: Kademeli korozyon")
        print("   ✅ Trafo 10: Ani kaçak akım")
    
    print(f"\n📊 {NUM_TRANSFORMERS} trafo izleniyor...")
    print(f"⏱️  Güncelleme aralığı: {SIMULATION_CONFIG['update_interval']} saniye")
    print(f"🕐 Simülasyon süresi: {duration_minutes} dakika")
    print("\n" + "-" * 60)
    
    start_time = time.time()
    iteration = 0
    isolated_count = 0  # Başlangıç değeri
    
    try:
        while True:
            iteration += 1
            current_time = datetime.now()
            
            print(f"\n🔄 İterasyon {iteration} - {current_time.strftime('%H:%M:%S')}")
            print("-" * 60)
            
            # Her trafo için veri üret ve analiz et
            for transformer in transformers:
                # Sensör verisi üret
                sensor_data = transformer.generate_sensor_data()
                
                # Anomali analizi
                analysis = detection_system.analyze_sensor_data(sensor_data)
                transformer.risk_score = analysis['risk_score']
                
                # Otomatik izolasyon kontrolü
                detection_system.check_auto_isolation(transformer, analysis)
                
                # Yüksek risk bildirimi
                if analysis['risk_score'] >= 70:
                    message = f"⚠️ Trafo {transformer.transformer_id} ({transformer.location['name']}): Yüksek risk tespit edildi! (Risk: {analysis['risk_score']:.1f})"
                    detection_system.add_alert(
                        transformer.transformer_id,
                        message,
                        'high' if analysis['risk_score'] >= 80 else 'medium'
                    )
                    print(f"   {message}")
                
                # Veriyi kaydet
                storage.save_data(sensor_data, analysis)
            
            # Özet istatistikler
            risk_scores = [t.risk_score for t in transformers]
            high_risk_count = sum(1 for r in risk_scores if r >= 70)
            medium_risk_count = sum(1 for r in risk_scores if 40 <= r < 70)
            isolated_count = sum(1 for t in transformers if not t.isolation_status)
            
            print(f"\n📈 Özet:")
            print(f"   • Yüksek Risk: {high_risk_count} trafo")
            print(f"   • Orta Risk: {medium_risk_count} trafo")
            print(f"   • İzole Edilmiş: {isolated_count} trafo")
            print(f"   • Toplam Bildirim: {len(detection_system.alerts)}")
            
            # Süre kontrolü
            elapsed_minutes = (time.time() - start_time) / 60
            if elapsed_minutes >= duration_minutes:
                print(f"\n⏰ Simülasyon süresi doldu ({duration_minutes} dakika)")
                break
            
            # Bekle
            time.sleep(SIMULATION_CONFIG['update_interval'])
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Simülasyon kullanıcı tarafından durduruldu")
    
    # Final rapor
    print("\n" + "=" * 60)
    print("📊 Simülasyon Raporu")
    print("=" * 60)
    print(f"   • Toplam iterasyon: {iteration}")
    print(f"   • Toplam bildirim: {len(detection_system.alerts)}")
    print(f"   • İzole edilmiş trafo: {isolated_count}")
    print(f"   • Veri dosyası: {storage.data_file}")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Topraklama İzleme Simülasyonu')
    parser.add_argument('--duration', type=int, default=10, 
                       help='Simülasyon süresi (dakika)')
    parser.add_argument('--no-demo', action='store_true',
                       help='Demo modunu kapat (arıza senaryosu yok)')
    
    args = parser.parse_args()
    
    try:
        run_simulation(
            duration_minutes=args.duration,
            demo_mode=not args.no_demo
        )
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()

