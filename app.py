"""
Flask API Server
Frontend ile backend arasında iletişim sağlar.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime, timedelta
import json

# Mevcut modülleri import et
from model_egit import load_model, predict_anomaly, calculate_risk_score
from config import (
    NUM_TRANSFORMERS,
    TRANSFORMER_LOCATIONS,
    SENSOR_RANGES,
    RISK_SCORING
)

# Simülasyon sınıflarını import et
from simulasyon import TransformerSimulator, AnomalyDetectionSystem, DataStorage

app = Flask(__name__)
CORS(app)  # Frontend'den gelen isteklere izin ver

# Global değişkenler
detection_system = None
transformers = []
storage = None

def initialize_system():
    """Sistemi başlatır"""
    global detection_system, transformers, storage
    
    # Anomali tespit sistemini başlat
    detection_system = AnomalyDetectionSystem()
    
    # Trafoları oluştur
    transformers = [
        TransformerSimulator(i+1) 
        for i in range(NUM_TRANSFORMERS)
    ]
    
    # Veri depolama
    storage = DataStorage()
    
    print("[OK] Sistem baslatildi")

# API Endpoints

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sistem sağlık kontrolü"""
    return jsonify({
        'status': 'ok',
        'message': 'API çalışıyor',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/transformers', methods=['GET'])
def get_transformers():
    """Tüm trafoların listesini döndürür"""
    try:
        transformers_list = []
        
        for transformer in transformers:
            # Son sensör verisini al
            sensor_data = transformer.generate_sensor_data()
            
            # Anomali analizi yap
            analysis = detection_system.analyze_sensor_data(sensor_data)
            transformer.risk_score = analysis['risk_score']
            
            transformers_list.append({
                'id': transformer.transformer_id,
                'name': transformer.location['name'],
                'region': transformer.location['region'],
                'latitude': float(transformer.location['latitude']),
                'longitude': float(transformer.location['longitude']),
                'risk_score': round(analysis['risk_score'], 2),
                'risk_level': analysis['risk_level'],
                'is_anomaly': bool(analysis['is_anomaly']),
                'isolation_status': bool(transformer.isolation_status),
                'last_update': str(transformer.last_update.isoformat()),
                'sensor_data': {
                    'toprak_direnci': float(sensor_data['toprak_direnci']),
                    'kacak_akim': float(sensor_data['kacak_akim']),
                    'toprak_potansiyel': float(sensor_data['toprak_potansiyel']),
                    'toprak_nemi': float(sensor_data['toprak_nemi']),
                    'toprak_sicakligi': float(sensor_data['toprak_sicakligi']),
                    'korozyon_seviyesi': float(sensor_data['korozyon_seviyesi'])
                }
            })
        
        return jsonify({
            'success': True,
            'count': len(transformers_list),
            'transformers': transformers_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transformers/<int:transformer_id>', methods=['GET'])
def get_transformer(transformer_id):
    """Belirli bir trafo bilgisini döndürür"""
    try:
        if transformer_id < 1 or transformer_id > NUM_TRANSFORMERS:
            return jsonify({
                'success': False,
                'error': 'Geçersiz trafo ID'
            }), 404
        
        transformer = transformers[transformer_id - 1]
        sensor_data = transformer.generate_sensor_data()
        analysis = detection_system.analyze_sensor_data(sensor_data)
        transformer.risk_score = analysis['risk_score']
        
        return jsonify({
            'success': True,
            'transformer': {
                'id': transformer.transformer_id,
                'name': transformer.location['name'],
                'region': transformer.location['region'],
                'latitude': float(transformer.location['latitude']),
                'longitude': float(transformer.location['longitude']),
                'risk_score': round(analysis['risk_score'], 2),
                'risk_level': analysis['risk_level'],
                'is_anomaly': bool(analysis['is_anomaly']),
                'anomaly_score': float(analysis['anomaly_score']),
                'isolation_status': bool(transformer.isolation_status),
                'last_update': str(transformer.last_update.isoformat()),
                'sensor_data': {
                    'toprak_direnci': float(sensor_data['toprak_direnci']),
                    'kacak_akim': float(sensor_data['kacak_akim']),
                    'toprak_potansiyel': float(sensor_data['toprak_potansiyel']),
                    'toprak_nemi': float(sensor_data['toprak_nemi']),
                    'toprak_sicakligi': float(sensor_data['toprak_sicakligi']),
                    'korozyon_seviyesi': float(sensor_data['korozyon_seviyesi'])
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transformers/<int:transformer_id>/history', methods=['GET'])
def get_transformer_history(transformer_id):
    """Trafo geçmiş verilerini döndürür"""
    try:
        # CSV dosyasından veri oku
        data_file = 'data/realtime_data.csv'
        
        if not os.path.exists(data_file):
            return jsonify({
                'success': True,
                'history': []
            })
        
        df = pd.read_csv(data_file)
        df = df[df['transformer_id'] == transformer_id]
        
        # Son 100 kaydı al
        df = df.tail(100)
        
        history = []
        for _, row in df.iterrows():
            history.append({
                'timestamp': row['timestamp'],
                'toprak_direnci': float(row.get('toprak_direnci', 0)),
                'kacak_akim': float(row.get('kacak_akim', 0)),
                'toprak_potansiyel': float(row.get('toprak_potansiyel', 0)),
                'toprak_nemi': float(row.get('toprak_nemi', 0)),
                'toprak_sicakligi': float(row.get('toprak_sicakligi', 0)),
                'korozyon_seviyesi': float(row.get('korozyon_seviyesi', 0)),
                'risk_score': float(row.get('risk_score', 0)),
                'is_anomaly': bool(row.get('is_anomaly', False))
            })
        
        return jsonify({
            'success': True,
            'count': len(history),
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Dashboard için istatistikleri döndürür"""
    try:
        # Tüm trafoları güncelle
        risk_scores = []
        anomaly_count = 0
        isolated_count = 0
        
        for transformer in transformers:
            sensor_data = transformer.generate_sensor_data()
            analysis = detection_system.analyze_sensor_data(sensor_data)
            transformer.risk_score = analysis['risk_score']
            
            risk_scores.append(analysis['risk_score'])
            if analysis['is_anomaly']:
                anomaly_count += 1
            if not transformer.isolation_status:
                isolated_count += 1
        
        # Risk seviyelerine göre sayılar
        high_risk = sum(1 for r in risk_scores if r >= 70)
        medium_risk = sum(1 for r in risk_scores if 40 <= r < 70)
        low_risk = sum(1 for r in risk_scores if r < 40)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_transformers': NUM_TRANSFORMERS,
                'anomaly_count': anomaly_count,
                'isolated_count': isolated_count,
                'risk_distribution': {
                    'high': high_risk,
                    'medium': medium_risk,
                    'low': low_risk
                },
                'average_risk': round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0,
                'max_risk': round(max(risk_scores), 2) if risk_scores else 0,
                'min_risk': round(min(risk_scores), 2) if risk_scores else 0
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transformers/<int:transformer_id>/isolate', methods=['POST'])
def isolate_transformer(transformer_id):
    """Trafo izolasyonu yapar"""
    try:
        if transformer_id < 1 or transformer_id > NUM_TRANSFORMERS:
            return jsonify({
                'success': False,
                'error': 'Geçersiz trafo ID'
            }), 404
        
        transformer = transformers[transformer_id - 1]
        data = request.get_json() or {}
        action = data.get('action', 'isolate')  # 'isolate' veya 'restore'
        
        if action == 'isolate':
            transformer.isolation_status = False
            message = f"Trafo {transformer_id} izole edildi"
        else:
            transformer.isolation_status = True
            message = f"Trafo {transformer_id} izolasyondan çıkarıldı"
        
        return jsonify({
            'success': True,
            'message': message,
            'transformer_id': transformer_id,
            'isolation_status': transformer.isolation_status
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Bildirimleri döndürür"""
    try:
        # Son 50 bildirimi al
        alerts = detection_system.alerts[-50:] if detection_system.alerts else []
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': alerts
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Sistem konfigürasyonunu döndürür"""
    try:
        return jsonify({
            'success': True,
            'config': {
                'num_transformers': NUM_TRANSFORMERS,
                'sensor_ranges': SENSOR_RANGES,
                'risk_scoring': RISK_SCORING
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Hata yakalama
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint bulunamadı'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Sunucu hatası'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Flask API Server Baslatiliyor...")
    print("=" * 60)
    
    # Sistemi başlat
    initialize_system()
    
    print("\nAPI Endpoints:")
    print("   GET  /api/health - Sistem saglik kontrolu")
    print("   GET  /api/transformers - Tum trafolar")
    print("   GET  /api/transformers/<id> - Trafo detayi")
    print("   GET  /api/transformers/<id>/history - Trafo gecmisi")
    print("   GET  /api/dashboard/stats - Dashboard istatistikleri")
    print("   POST /api/transformers/<id>/isolate - Trafo izolasyonu")
    print("   GET  /api/alerts - Bildirimler")
    print("   GET  /api/config - Sistem konfigurasyonu")
    print("\nServer: http://localhost:5000")
    print("=" * 60)
    
    # Development modunda çalıştır
    app.run(debug=True, host='0.0.0.0', port=5000)

