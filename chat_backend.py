"""
Chat Backend API
Dinamik, akıllı chat sistemi için backend
RAG (Retrieval-Augmented Generation) yaklaşımı kullanır
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import requests

# Mevcut modülleri import et
from model_egit import load_model, predict_anomaly, calculate_risk_score
from config import (
    NUM_TRANSFORMERS,
    TRANSFORMER_LOCATIONS,
    SENSOR_RANGES,
    RISK_SCORING
)
from simulasyon import TransformerSimulator, AnomalyDetectionSystem

app = Flask(__name__)
CORS(app)

# Global değişkenler
detection_system = None
transformers = []
api_base_url = 'http://localhost:5000/api'

class ChatDataAccess:
    """Chat için veri erişim katmanı"""
    
    def __init__(self):
        self.api_base = api_base_url
        self.sensor_data_path = 'data/sensor_data.csv'
        self.realtime_data_path = 'data/realtime_data.csv'
        self.sensor_df = None
        self.realtime_df = None
        
    def load_historical_data(self):
        """Tarihsel verileri yükle"""
        try:
            if os.path.exists(self.sensor_data_path):
                self.sensor_df = pd.read_csv(self.sensor_data_path)
                self.sensor_df['timestamp'] = pd.to_datetime(self.sensor_df['timestamp'])
            if os.path.exists(self.realtime_data_path):
                self.realtime_df = pd.read_csv(self.realtime_data_path)
                if 'timestamp' in self.realtime_df.columns:
                    self.realtime_df['timestamp'] = pd.to_datetime(self.realtime_df['timestamp'])
        except Exception as e:
            print(f"Veri yukleme hatasi: {e}")
    
    def get_transformer_current(self, transformer_id):
        """Güncel trafo verisini API'den al"""
        try:
            response = requests.get(f"{self.api_base}/transformers/{transformer_id}")
            if response.status_code == 200:
                return response.json().get('transformer')
        except:
            pass
        return None
    
    def get_all_transformers(self):
        """Tüm trafoları API'den al"""
        try:
            response = requests.get(f"{self.api_base}/transformers")
            if response.status_code == 200:
                return response.json().get('transformers', [])
        except:
            pass
        return []
    
    def get_dashboard_stats(self):
        """Dashboard istatistiklerini al"""
        try:
            response = requests.get(f"{self.api_base}/dashboard/stats")
            if response.status_code == 200:
                return response.json().get('stats')
        except:
            pass
        return None
    
    def get_transformer_history(self, transformer_id, days=30):
        """Trafo geçmiş verilerini al"""
        try:
            # API'den geçmiş veri
            response = requests.get(f"{self.api_base}/transformers/{transformer_id}/history")
            if response.status_code == 200:
                return response.json().get('history', [])
            
            # CSV'den geçmiş veri
            if self.sensor_df is not None:
                df = self.sensor_df[self.sensor_df['transformer_id'] == transformer_id].copy()
                df = df.sort_values('timestamp')
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df['timestamp'] >= cutoff_date]
                return df.to_dict('records')
        except Exception as e:
            print(f"Geçmiş veri hatası: {e}")
        return []
    
    def analyze_trends(self, transformer_id, days=7):
        """Trend analizi yap"""
        history = self.get_transformer_history(transformer_id, days)
        if not history:
            return None
        
        # Risk skoru trendi
        risk_scores = [h.get('risk_score', 0) for h in history if 'risk_score' in h]
        if risk_scores:
            trend = 'artış' if risk_scores[-1] > risk_scores[0] else 'azalış'
            change = abs(risk_scores[-1] - risk_scores[0])
            return {
                'trend': trend,
                'change': change,
                'current': risk_scores[-1],
                'previous': risk_scores[0]
            }
        return None
    
    def find_similar_cases(self, transformer_data):
        """Benzer durumları bul"""
        if self.sensor_df is None:
            return []
        
        # Anomali durumlarını bul
        anomalies = self.sensor_df[self.sensor_df['anomali'] == 1].copy()
        
        # Benzer sensör değerlerine sahip durumları bul
        similar = []
        for idx, row in anomalies.iterrows():
            similarity = 0
            for sensor in ['toprak_direnci', 'kacak_akim', 'toprak_potansiyel']:
                if sensor in transformer_data.get('sensor_data', {}):
                    diff = abs(row[sensor] - transformer_data['sensor_data'][sensor])
                    if diff < 2.0:  # Benzer değerler
                        similarity += 1
            if similarity >= 2:
                similar.append({
                    'transformer_id': int(row['transformer_id']),
                    'timestamp': str(row['timestamp']),
                    'sensor_data': {
                        'toprak_direnci': float(row['toprak_direnci']),
                        'kacak_akim': float(row['kacak_akim']),
                        'toprak_potansiyel': float(row['toprak_potansiyel'])
                    }
                })
        
        return similar[:5]  # İlk 5 benzer durum


class ChatContextBuilder:
    """Chat için context oluşturur"""
    
    def __init__(self, data_access):
        self.data_access = data_access
    
    def build_context(self, question, transformer_id=None):
        """Soru için context oluştur"""
        context = {
            'current_time': datetime.now().isoformat(),
            'question': question,
            'system_stats': self.data_access.get_dashboard_stats(),
        }
        
        if transformer_id:
            context['transformer'] = self.data_access.get_transformer_current(transformer_id)
            context['history'] = self.data_access.get_transformer_history(transformer_id, days=30)
            context['trends'] = self.data_access.analyze_trends(transformer_id, days=7)
            
            if context['transformer']:
                context['similar_cases'] = self.data_access.find_similar_cases(context['transformer'])
        else:
            context['all_transformers'] = self.data_access.get_all_transformers()
        
        return context


class ChatAnalyzer:
    """Chat için analiz ve yorum yapar"""
    
    def __init__(self):
        self.sensor_ranges = SENSOR_RANGES
        self.risk_scoring = RISK_SCORING
    
    def analyze_transformer_status(self, transformer_data):
        """Trafo durumunu analiz et"""
        if not transformer_data:
            return None
        
        sensor_data = transformer_data.get('sensor_data', {})
        risk_score = transformer_data.get('risk_score', 0)
        risk_level = transformer_data.get('risk_level', 'unknown')
        
        analysis = {
            'status': 'normal',
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Toprak direnci kontrolü
        resistance = sensor_data.get('toprak_direnci', 0)
        if resistance > 10:
            analysis['issues'].append(f"Toprak direnci çok yüksek ({resistance} Ohm). Normal aralık: 2-5 Ohm")
            analysis['recommendations'].append("Korozyon kontrolü yapılmalı, gerekirse topraklama elektrodu değiştirilmeli")
        elif resistance > 5:
            analysis['warnings'].append(f"Toprak direnci yüksek ({resistance} Ohm)")
            analysis['recommendations'].append("Önleyici bakım önerilir")
        
        # Kaçak akım kontrolü
        leakage = sensor_data.get('kacak_akim', 0)
        if leakage > 20:
            analysis['issues'].append(f"Kaçak akım yüksek ({leakage} mA). Normal aralık: 0-10 mA")
            analysis['recommendations'].append("İzolasyon kontrolü yapılmalı, gerekirse trafo izole edilmeli")
        elif leakage > 10:
            analysis['warnings'].append(f"Kaçak akım artıyor ({leakage} mA)")
            analysis['recommendations'].append("İzolasyon testi yapılmalı")
        
        # Korozyon kontrolü
        corrosion = sensor_data.get('korozyon_seviyesi', 0)
        if corrosion > 50:
            analysis['issues'].append(f"Korozyon seviyesi kritik ({corrosion})")
            analysis['recommendations'].append("Acil bakım gerekli, topraklama elektrodu değiştirilmeli")
        elif corrosion > 30:
            analysis['warnings'].append(f"Korozyon seviyesi yüksek ({corrosion})")
            analysis['recommendations'].append("Önleyici bakım planlanmalı")
        
        # Risk seviyesi
        if risk_level == 'high':
            analysis['status'] = 'critical'
            analysis['recommendations'].append("Acil müdahale gerekli, trafo izole edilmeli")
        elif risk_level == 'medium':
            analysis['status'] = 'warning'
            analysis['recommendations'].append("Dikkatli izleme ve önleyici bakım önerilir")
        
        return analysis
    
    def generate_recommendations(self, context):
        """Öneriler üret"""
        recommendations = []
        
        if 'transformer' in context:
            analysis = self.analyze_transformer_status(context['transformer'])
            if analysis:
                recommendations.extend(analysis.get('recommendations', []))
        
        if 'trends' in context and context['trends']:
            trend = context['trends']
            if trend['trend'] == 'artış' and trend['change'] > 20:
                recommendations.append(f"Risk skoru {trend['change']:.1f} puan arttı. Önleyici bakım yapılmalı")
        
        if 'similar_cases' in context and context['similar_cases']:
            recommendations.append(f"Geçmişte {len(context['similar_cases'])} benzer durum görüldü. Bu durumlar için izolasyon kontrolü yapılmıştı")
        
        return recommendations


# Global instance
data_access = ChatDataAccess()
context_builder = ChatContextBuilder(data_access)
analyzer = ChatAnalyzer()

# Verileri yükle
data_access.load_historical_data()


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        transformer_id = data.get('transformer_id', None)
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Soru gerekli'
            }), 400
        
        # Context oluştur
        context = context_builder.build_context(question, transformer_id)
        
        # Analiz yap
        analysis = None
        if transformer_id and 'transformer' in context:
            analysis = analyzer.analyze_transformer_status(context['transformer'])
        
        # Öneriler üret
        recommendations = analyzer.generate_recommendations(context)
        
        # Dinamik yanıt oluştur (şimdilik basit, sonra LLM entegre edilecek)
        response = generate_dynamic_response(question, context, analysis, recommendations)
        
        return jsonify({
            'success': True,
            'response': response,
            'context': {
                'transformer_id': transformer_id,
                'has_analysis': analysis is not None,
                'recommendations_count': len(recommendations)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_dynamic_response(question, context, analysis, recommendations):
    """Dinamik yanıt üret (LLM entegrasyonu öncesi)"""
    
    question_lower = question.lower()
    
    # Trafo durumu sorusu
    if 'durum' in question_lower or 'nasıl' in question_lower:
        if 'transformer' in context and context['transformer']:
            tf = context['transformer']
            response = f"{tf['name']} şu anda {tf['risk_level']} risk seviyesinde (Risk skoru: {tf['risk_score']:.1f}). "
            
            if analysis:
                if analysis['issues']:
                    response += f"\n\nKritik sorunlar: {', '.join(analysis['issues'][:2])}"
                if analysis['warnings']:
                    response += f"\n\nUyarılar: {', '.join(analysis['warnings'][:2])}"
            
            if recommendations:
                response += f"\n\nÖneriler: {recommendations[0]}"
            
            return response
    
    # Risk analizi
    if 'risk' in question_lower or 'tehlikeli' in question_lower:
        if 'all_transformers' in context:
            high_risk = [t for t in context['all_transformers'] if t['risk_level'] == 'high']
            if high_risk:
                names = [t['name'] for t in high_risk[:5]]
                response = f"Yüksek risk altındaki trafolar: {', '.join(names)}. "
                response += f"Toplam {len(high_risk)} trafo yüksek risk seviyesinde."
                return response
    
    # Anomali sorusu
    if 'anomali' in question_lower or 'hata' in question_lower:
        if 'transformer' in context and context['transformer']:
            tf = context['transformer']
            if tf.get('is_anomaly'):
                response = f"{tf['name']} için anomali tespit edildi. "
                if analysis and analysis['issues']:
                    response += f"Sorunlar: {', '.join(analysis['issues'])}. "
                if recommendations:
                    response += f"Çözüm: {recommendations[0]}"
                return response
            else:
                return f"{tf['name']} için anomali tespit edilmedi. Sistem normal çalışıyor."
    
    # Trend sorusu
    if 'trend' in question_lower or 'değişim' in question_lower:
        if 'trends' in context and context['trends']:
            trend = context['trends']
            response = f"Son 7 günde risk skoru {trend['trend']} gösteriyor. "
            response += f"Değişim: {trend['change']:.1f} puan ({trend['previous']:.1f} → {trend['current']:.1f})"
            return response
    
    # Genel yanıt
    return f"Sistem çalışıyor. {len(context.get('all_transformers', []))} trafo izleniyor. Daha spesifik bir soru sorabilirsiniz."


if __name__ == '__main__':
    print("=" * 60)
    print("Chat Backend API Baslatiliyor...")
    print("=" * 60)
    print("Endpoint: POST /api/chat")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5001)

