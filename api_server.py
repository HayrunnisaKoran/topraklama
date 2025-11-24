"""
Flask Backend API Server
Web Dashboard için REST API endpoints sağlar.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from model_egit import load_model, predict_anomaly, calculate_risk_score
from config import (
    NUM_TRANSFORMERS,
    TRANSFORMER_LOCATIONS,
    RISK_SCORING,
    ECONOMICS,
    DATA_GENERATION
)

# Firebase import (opsiyonel)
USE_FIREBASE = os.path.exists('firebase-key.json')
if USE_FIREBASE:
    try:
        from firebase_config import init_firebase, get_firestore, get_latest_by_transformer, FIRESTORE_COLLECTION
        init_firebase('firebase-key.json')
        print("✅ Firebase API için başlatıldı")
    except Exception as e:
        print(f"⚠️  Firebase başlatılamadı: {e}")
        USE_FIREBASE = False
else:
    print("ℹ️  firebase-key.json bulunamadı, CSV kullanılacak")

app = Flask(__name__)
CORS(app)  # Frontend'den istekler için CORS aktif

# Model yükleme (başlangıçta)
model = None
scaler = None

def init_model():
    """Modeli yükler"""
    global model, scaler
    try:
        model, scaler = load_model()
        print("✅ Model API için yüklendi")
    except Exception as e:
        print(f"⚠️  Model yüklenemedi: {e}")
        model = None
        scaler = None

# Uygulama başlarken modeli yükle
init_model()


@app.route('/api/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/transformers', methods=['GET'])
def get_transformers():
    """Tüm trafoların listesini döner"""
    transformers = []
    
    for loc in TRANSFORMER_LOCATIONS:
        transformers.append({
            'id': loc['id'],
            'name': loc['name'],
            'region': loc['region'],
            'latitude': loc['latitude'],
            'longitude': loc['longitude']
        })
    
    return jsonify({
        'transformers': transformers,
        'total': len(transformers)
    })


@app.route('/api/transformer/<int:transformer_id>', methods=['GET'])
def get_transformer_details(transformer_id):
    """Belirli bir trafonun detaylarını döner"""
    if transformer_id < 1 or transformer_id > NUM_TRANSFORMERS:
        return jsonify({'error': 'Geçersiz trafo ID'}), 404
    
    loc = TRANSFORMER_LOCATIONS[transformer_id - 1]
    latest_data = None
    
    # Firebase'den veri çek (birincil)
    if USE_FIREBASE:
        try:
            latest_dict = get_latest_by_transformer(FIRESTORE_COLLECTION, transformer_id)
            if transformer_id in latest_dict:
                data = latest_dict[transformer_id]
                latest_data = {
                    'toprak_direnci': float(data.get('toprak_direnci', 0)),
                    'kacak_akim': float(data.get('kacak_akim', 0)),
                    'toprak_potansiyel': float(data.get('toprak_potansiyel', 0)),
                    'toprak_nemi': float(data.get('toprak_nemi', 0)),
                    'toprak_sicakligi': float(data.get('toprak_sicakligi', 0)),
                    'korozyon_seviyesi': float(data.get('korozyon_seviyesi', 0)),
                    'risk_score': float(data.get('risk_score', 0)),
                    'risk_level': data.get('risk_level', 'unknown'),
                    'risk_color': data.get('risk_color', 'gray'),
                    'is_anomaly': bool(data.get('is_anomaly', False)),
                    'timestamp': data.get('timestamp', datetime.now().isoformat())
                }
        except Exception as e:
            print(f"⚠️ Firebase transformer detay okuma hatası: {e}")
    
    # CSV'den veri çek (fallback)
    if latest_data is None:
        realtime_file = 'data/realtime_data.csv'
        if os.path.exists(realtime_file):
            try:
                df = pd.read_csv(realtime_file)
                transformer_data = df[df['transformer_id'] == transformer_id]
                if not transformer_data.empty:
                    latest = transformer_data.iloc[-1]
                    latest_data = {
                        'toprak_direnci': float(latest.get('toprak_direnci', 0)),
                        'kacak_akim': float(latest.get('kacak_akim', 0)),
                        'toprak_potansiyel': float(latest.get('toprak_potansiyel', 0)),
                        'toprak_nemi': float(latest.get('toprak_nemi', 0)),
                        'toprak_sicakligi': float(latest.get('toprak_sicakligi', 0)),
                        'korozyon_seviyesi': float(latest.get('korozyon_seviyesi', 0)),
                        'risk_score': float(latest.get('risk_score', 0)),
                        'risk_level': latest.get('risk_level', 'unknown'),
                        'risk_color': latest.get('risk_color', 'gray'),
                        'is_anomaly': bool(latest.get('is_anomaly', False)),
                        'timestamp': latest.get('timestamp', datetime.now().isoformat())
                    }
            except Exception as e:
                print(f"⚠️ CSV transformer detay okuma hatası: {e}")
    
    return jsonify({
        'id': loc['id'],
        'name': loc['name'],
        'region': loc['region'],
        'latitude': loc['latitude'],
        'longitude': loc['longitude'],
        'latest_data': latest_data
    })


@app.route('/api/realtime-data', methods=['GET'])
def get_realtime_data():
    """Gerçek zamanlı veriyi döner (Firebase veya CSV)"""
    realtime_file = 'data/realtime_data.csv'
    
    # Tüm trafolar için sonuç listesi oluştur
    result = []
    
    # Önce tüm trafo lokasyonlarını varsayılan değerlerle ekle
    for transformer_id in range(1, NUM_TRANSFORMERS + 1):
        result.append({
            'transformer_id': transformer_id,
            'name': TRANSFORMER_LOCATIONS[transformer_id - 1]['name'],
            'latitude': TRANSFORMER_LOCATIONS[transformer_id - 1]['latitude'],
            'longitude': TRANSFORMER_LOCATIONS[transformer_id - 1]['longitude'],
            'region': TRANSFORMER_LOCATIONS[transformer_id - 1]['region'],
            'toprak_direnci': 0,
            'kacak_akim': 0,
            'toprak_potansiyel': 0,
            'toprak_nemi': 0,
            'toprak_sicakligi': 0,
            'korozyon_seviyesi': 0,
            'risk_score': 0,
            'risk_level': 'unknown',
            'risk_color': 'gray',
            'is_anomaly': False,
            'timestamp': datetime.now().isoformat()
        })
    
    # Firebase'den veri çek (birincil)
    if USE_FIREBASE:
        try:
            latest_data = get_latest_by_transformer(FIRESTORE_COLLECTION)
            
            # Firebase'den gelen verileri result listesine güncelle
            for transformer_id in range(1, NUM_TRANSFORMERS + 1):
                if transformer_id in latest_data:
                    data = latest_data[transformer_id]
                    # Result listesinde bu trafo ID'sine sahip kaydı bul ve güncelle
                    for i, item in enumerate(result):
                        if item['transformer_id'] == transformer_id:
                            result[i] = {
                                'transformer_id': int(data.get('transformer_id', transformer_id)),
                                'name': TRANSFORMER_LOCATIONS[transformer_id - 1]['name'],
                                'latitude': TRANSFORMER_LOCATIONS[transformer_id - 1]['latitude'],
                                'longitude': TRANSFORMER_LOCATIONS[transformer_id - 1]['longitude'],
                                'region': TRANSFORMER_LOCATIONS[transformer_id - 1]['region'],
                                'toprak_direnci': float(data.get('toprak_direnci', 0)),
                                'kacak_akim': float(data.get('kacak_akim', 0)),
                                'toprak_potansiyel': float(data.get('toprak_potansiyel', 0)),
                                'toprak_nemi': float(data.get('toprak_nemi', 0)),
                                'toprak_sicakligi': float(data.get('toprak_sicakligi', 0)),
                                'korozyon_seviyesi': float(data.get('korozyon_seviyesi', 0)),
                                'risk_score': float(data.get('risk_score', 0)),
                                'risk_level': data.get('risk_level', 'unknown'),
                                'risk_color': data.get('risk_color', 'gray'),
                                'is_anomaly': bool(data.get('is_anomaly', False)),
                                'timestamp': data.get('timestamp', datetime.now().isoformat())
                            }
                            break
            
            return jsonify({
                'data': result,
                'count': len(result),
                'timestamp': datetime.now().isoformat(),
                'message': 'Veriler Firebase\'den yüklendi',
                'source': 'firebase'
            })
        except Exception as e:
            print(f"⚠️ Firebase okuma hatası: {e}")
            # Hata durumunda CSV'ye düş
    
    # CSV'den veri çek (fallback)
    if os.path.exists(realtime_file):
        try:
            df = pd.read_csv(realtime_file)
            
            # Son 100 kaydı al
            limit = int(request.args.get('limit', 100))
            df = df.tail(limit)
            
            # Her trafo için son veriyi al ve result listesini güncelle
            for transformer_id in range(1, NUM_TRANSFORMERS + 1):
                trafo_data = df[df['transformer_id'] == transformer_id]
                if not trafo_data.empty:
                    latest = trafo_data.iloc[-1]
                    # Result listesinde bu trafo ID'sine sahip kaydı bul ve güncelle
                    for i, item in enumerate(result):
                        if item['transformer_id'] == transformer_id:
                            result[i] = {
                                'transformer_id': int(latest.get('transformer_id', transformer_id)),
                                'name': TRANSFORMER_LOCATIONS[transformer_id - 1]['name'],
                                'latitude': TRANSFORMER_LOCATIONS[transformer_id - 1]['latitude'],
                                'longitude': TRANSFORMER_LOCATIONS[transformer_id - 1]['longitude'],
                                'region': TRANSFORMER_LOCATIONS[transformer_id - 1]['region'],
                                'toprak_direnci': float(latest.get('toprak_direnci', 0)),
                                'kacak_akim': float(latest.get('kacak_akim', 0)),
                                'toprak_potansiyel': float(latest.get('toprak_potansiyel', 0)),
                                'toprak_nemi': float(latest.get('toprak_nemi', 0)),
                                'toprak_sicakligi': float(latest.get('toprak_sicakligi', 0)),
                                'korozyon_seviyesi': float(latest.get('korozyon_seviyesi', 0)),
                                'risk_score': float(latest.get('risk_score', 0)),
                                'risk_level': latest.get('risk_level', 'unknown'),
                                'risk_color': latest.get('risk_color', 'gray'),
                                'is_anomaly': bool(latest.get('is_anomaly', False)),
                                'timestamp': latest.get('timestamp', datetime.now().isoformat())
                            }
                            break
        
        except Exception as e:
            print(f"⚠️ CSV okuma hatası: {e}")
            # Hata durumunda varsayılan değerlerle devam et
    
    return jsonify({
        'data': result,
        'count': len(result),
        'timestamp': datetime.now().isoformat(),
        'message': 'Veriler yüklendi' if os.path.exists(realtime_file) else 'Simülasyonu başlatın',
        'source': 'csv' if os.path.exists(realtime_file) else 'default'
    })


@app.route('/api/historical-data/<int:transformer_id>', methods=['GET'])
def get_historical_data(transformer_id):
    """Tarihsel veriyi döner (grafik için)"""
    data_file = DATA_GENERATION['output_file']
    
    if not os.path.exists(data_file):
        return jsonify({'error': 'Tarihsel veri bulunamadı'}), 404
    
    try:
        # Tarih aralığı parametreleri
        days = int(request.args.get('days', 7))  # Varsayılan 7 gün
        
        df = pd.read_csv(data_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Belirli trafo için filtrele
        trafo_data = df[df['transformer_id'] == transformer_id].copy()
        
        # Tarih aralığı
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trafo_data = trafo_data[
            (trafo_data['timestamp'] >= start_date) & 
            (trafo_data['timestamp'] <= end_date)
        ]
        
        # JSON formatına çevir
        result = trafo_data[[
            'timestamp', 'toprak_direnci', 'kacak_akim', 
            'toprak_potansiyel', 'toprak_nemi', 'toprak_sicakligi',
            'korozyon_seviyesi', 'anomali'
        ]].to_dict('records')
        
        # Timestamp'i string'e çevir
        for record in result:
            if isinstance(record['timestamp'], pd.Timestamp):
                record['timestamp'] = record['timestamp'].isoformat()
        
        return jsonify({
            'transformer_id': transformer_id,
            'data': result,
            'count': len(result),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Bildirimleri döner"""
    realtime_file = 'data/realtime_data.csv'
    
    if not os.path.exists(realtime_file):
        return jsonify({'alerts': []})
    
    try:
        df = pd.read_csv(realtime_file)
        
        # Yüksek riskli trafoları bul
        alerts = []
        high_risk = df[df['risk_score'] >= 70]
        
        for _, row in high_risk.iterrows():
            alerts.append({
                'timestamp': row.get('timestamp', datetime.now().isoformat()),
                'transformer_id': int(row['transformer_id']),
                'name': TRANSFORMER_LOCATIONS[int(row['transformer_id']) - 1]['name'],
                'risk_score': float(row.get('risk_score', 0)),
                'risk_level': row.get('risk_level', 'high'),
                'message': f"Trafo {int(row['transformer_id'])}: Yüksek risk tespit edildi! (Risk: {float(row.get('risk_score', 0)):.1f})",
                'severity': 'high' if row.get('risk_score', 0) >= 80 else 'medium'
            })
        
        # Tarihe göre sırala (en yeni önce)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Son 50 bildirimi al
        alerts = alerts[:50]
        
        return jsonify({
            'alerts': alerts,
            'count': len(alerts)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Genel istatistikleri döner"""
    realtime_file = 'data/realtime_data.csv'
    
    if not os.path.exists(realtime_file):
        return jsonify({
            'total_transformers': NUM_TRANSFORMERS,
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0,
            'isolated': 0,
            'total_alerts': 0,
            'estimated_savings': 0
        })
    
    try:
        df = pd.read_csv(realtime_file)
        
        # Son verileri al (her trafo için en son kayıt)
        latest_data = []
        for transformer_id in range(1, NUM_TRANSFORMERS + 1):
            trafo_data = df[df['transformer_id'] == transformer_id]
            if not trafo_data.empty:
                latest_data.append(trafo_data.iloc[-1])
        
        if not latest_data:
            return jsonify({
                'total_transformers': NUM_TRANSFORMERS,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'isolated': 0,
                'total_alerts': 0,
                'estimated_savings': 0
            })
        
        # Risk seviyelerine göre say
        high_risk = sum(1 for d in latest_data if d.get('risk_score', 0) >= 70)
        medium_risk = sum(1 for d in latest_data if 40 <= d.get('risk_score', 0) < 70)
        low_risk = sum(1 for d in latest_data if d.get('risk_score', 0) < 40)
        
        # İzole edilmiş trafolar (risk >= 80)
        isolated = sum(1 for d in latest_data if d.get('risk_score', 0) >= 80)
        
        # Toplam bildirim sayısı
        total_alerts = len(df[df['risk_score'] >= 70])
        
        # Tahmini tasarruf hesaplama
        # Her yüksek riskli trafo için önleyici bakım = reaktif bakımdan tasarruf
        estimated_savings = high_risk * (
            ECONOMICS['reactive_maintenance_cost'] - 
            ECONOMICS['preventive_maintenance_cost']
        )
        
        return jsonify({
            'total_transformers': NUM_TRANSFORMERS,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'isolated': isolated,
            'total_alerts': total_alerts,
            'estimated_savings': round(estimated_savings, 2)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """Yeni sensör verisi için anomali tahmini yapar"""
    if model is None:
        return jsonify({'error': 'Model yüklenemedi'}), 500
    
    try:
        data = request.json
        sensor_data = {
            'toprak_direnci': float(data.get('toprak_direnci', 0)),
            'kacak_akim': float(data.get('kacak_akim', 0)),
            'toprak_potansiyel': float(data.get('toprak_potansiyel', 0)),
            'toprak_nemi': float(data.get('toprak_nemi', 0)),
            'toprak_sicakligi': float(data.get('toprak_sicakligi', 0)),
            'korozyon_seviyesi': float(data.get('korozyon_seviyesi', 0))
        }
        
        # Tahmin yap
        is_anomaly, anomaly_score = predict_anomaly(model, scaler, sensor_data)
        risk_score = calculate_risk_score(anomaly_score, sensor_data)
        
        # Risk seviyesi
        if risk_score < RISK_SCORING['low']['max']:
            risk_level = 'low'
        elif risk_score < RISK_SCORING['medium']['max']:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return jsonify({
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': round(anomaly_score, 4),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': RISK_SCORING[risk_level]['color']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Flask API Server Başlatılıyor")
    print("=" * 60)
    print(f"📡 API Endpoints:")
    print(f"   • GET  /api/health - Sağlık kontrolü")
    print(f"   • GET  /api/transformers - Tüm trafolar")
    print(f"   • GET  /api/transformer/<id> - Trafo detayı")
    print(f"   • GET  /api/realtime-data - Gerçek zamanlı veri")
    print(f"   • GET  /api/historical-data/<id> - Tarihsel veri")
    print(f"   • GET  /api/alerts - Bildirimler")
    print(f"   • GET  /api/statistics - İstatistikler")
    print(f"   • POST /api/predict - Anomali tahmini")
    print("=" * 60)
    print(f"🌐 Server: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

