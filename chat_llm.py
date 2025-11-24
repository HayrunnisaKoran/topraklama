"""
Dinamik Chat Sistemi - LLM Entegrasyonu
Model eğitimi ve dinamik analiz için
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

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
model = None
scaler = None

# LLM için (Ollama veya OpenAI)
try:
    import ollama
    USE_OLLAMA = True
    print("[OK] Ollama bulundu - Yerel LLM kullanilacak")
except ImportError:
    USE_OLLAMA = False
    try:
        from openai import OpenAI
        client = OpenAI()
        USE_OPENAI = True
        print("[OK] OpenAI bulundu")
    except:
        USE_OPENAI = False
        print("[!] LLM bulunamadi - Basit analiz kullanilacak")


class ChatDataAccess:
    """Chat için veri erişim katmanı - Dinamik veri çekme"""
    
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
                print(f"Tarihsel veri yukleniyor: {self.sensor_data_path}")
                self.sensor_df = pd.read_csv(self.sensor_data_path)
                self.sensor_df['timestamp'] = pd.to_datetime(self.sensor_df['timestamp'])
                print(f"[OK] {len(self.sensor_df):,} kayit yuklendi")
            if os.path.exists(self.realtime_data_path):
                self.realtime_df = pd.read_csv(self.realtime_data_path)
                if 'timestamp' in self.realtime_df.columns:
                    self.realtime_df['timestamp'] = pd.to_datetime(self.realtime_df['timestamp'])
        except Exception as e:
            print(f"Veri yukleme hatasi: {e}")
    
    def get_transformer_current(self, transformer_id):
        """Güncel trafo verisini API'den al - DINAMIK"""
        try:
            response = requests.get(f"{self.api_base}/transformers/{transformer_id}", timeout=5)
            if response.status_code == 200:
                return response.json().get('transformer')
        except Exception as e:
            print(f"API hatasi: {e}")
        return None
    
    def get_all_transformers(self):
        """Tüm trafoları API'den al - DINAMIK"""
        try:
            response = requests.get(f"{self.api_base}/transformers", timeout=5)
            if response.status_code == 200:
                return response.json().get('transformers', [])
        except:
            pass
        return []
    
    def get_dashboard_stats(self):
        """Dashboard istatistiklerini al - DINAMIK"""
        try:
            response = requests.get(f"{self.api_base}/dashboard/stats", timeout=5)
            if response.status_code == 200:
                return response.json().get('stats')
        except:
            pass
        return None
    
    def get_transformer_history(self, transformer_id, days=30):
        """Trafo geçmiş verilerini al"""
        try:
            response = requests.get(f"{self.api_base}/transformers/{transformer_id}/history", timeout=5)
            if response.status_code == 200:
                return response.json().get('history', [])
        except:
            pass
        
        # CSV'den geçmiş veri
        if self.sensor_df is not None:
            df = self.sensor_df[self.sensor_df['transformer_id'] == transformer_id].copy()
            df = df.sort_values('timestamp')
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['timestamp'] >= cutoff_date]
            return df.to_dict('records')
        
        return []
    
    def analyze_trends(self, transformer_id, days=7):
        """Trend analizi yap - DINAMIK"""
        history = self.get_transformer_history(transformer_id, days=days)
        if len(history) < 2:
            return None
        
        # Son ve önceki değerleri al
        current = history[-1].get('risk_score', 0) if isinstance(history[-1], dict) else 0
        previous = history[0].get('risk_score', 0) if isinstance(history[0], dict) else 0
        
        change = current - previous
        trend = 'artış' if change > 0 else 'azalış' if change < 0 else 'stabil'
        
        return {
            'trend': trend,
            'change': abs(change),
            'current': current,
            'previous': previous,
            'days': days
        }
    
    def find_similar_cases(self, transformer_data):
        """Benzer durumları bul - DINAMIK ANALIZ"""
        if self.sensor_df is None:
            return []
        
        sensor_data = transformer_data.get('sensor_data', {})
        risk_score = transformer_data.get('risk_score', 0)
        
        # Benzer risk skorlarına sahip trafoları bul
        similar = []
        for trafo_id in range(1, NUM_TRANSFORMERS + 1):
            if trafo_id == transformer_data.get('id'):
                continue
            
            df = self.sensor_df[self.sensor_df['transformer_id'] == trafo_id]
            if len(df) == 0:
                continue
            
            # Son kayıtları al
            recent = df.tail(100)
            avg_risk = recent['anomali'].mean() * 100  # Yaklaşık risk
            
            if abs(avg_risk - risk_score) < 10:  # ±10 puan içinde
                similar.append({
                    'transformer_id': trafo_id,
                    'similarity': 100 - abs(avg_risk - risk_score),
                    'avg_anomaly_rate': avg_risk
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)[:5]


class DynamicAnalyzer:
    """Dinamik analiz ve yorum yapar - Model kullanarak"""
    
    def __init__(self):
        self.sensor_ranges = SENSOR_RANGES
        self.risk_scoring = RISK_SCORING
        self.model = model
        self.scaler = scaler
    
    def analyze_transformer_detailed(self, transformer_data, history=None, trends=None):
        """Detaylı trafo analizi - DINAMIK"""
        if not transformer_data:
            return None
        
        sensor_data = transformer_data.get('sensor_data', {})
        risk_score = transformer_data.get('risk_score', 0)
        risk_level = transformer_data.get('risk_level', 'unknown')
        is_anomaly = transformer_data.get('is_anomaly', False)
        
        analysis = {
            'status': 'normal',
            'critical_issues': [],
            'warnings': [],
            'root_causes': [],
            'solutions': [],
            'preventive_actions': [],
            'timeline': 'normal'
        }
        
        # Model ile anomali analizi
        if self.model and self.scaler:
            try:
                is_predicted_anomaly, anomaly_score = predict_anomaly(
                    self.model, self.scaler, sensor_data
                )
                if is_predicted_anomaly:
                    analysis['status'] = 'anomaly_detected'
                    analysis['anomaly_confidence'] = abs(anomaly_score)
            except:
                pass
        
        # Detaylı sensör analizi
        resistance = sensor_data.get('toprak_direnci', 0)
        leakage = sensor_data.get('kacak_akim', 0)
        corrosion = sensor_data.get('korozyon_seviyesi', 0)
        potential = sensor_data.get('toprak_potansiyel', 0)
        moisture = sensor_data.get('toprak_nemi', 0)
        temperature = sensor_data.get('toprak_sicakligi', 0)
        
        # Toprak Direnci Analizi
        normal_resistance = self.sensor_ranges['toprak_direnci']
        if resistance > 15:
            analysis['critical_issues'].append({
                'parameter': 'toprak_direnci',
                'value': resistance,
                'normal_range': f"{normal_resistance['min']}-{normal_resistance['max']} {normal_resistance['unit']}",
                'severity': 'critical',
                'description': f"Toprak direnci kritik seviyede ({resistance} Ohm). Bu, topraklama sisteminin etkinliğini ciddi şekilde azaltır."
            })
            analysis['root_causes'].append("Korozyon, gevşek bağlantılar veya toprak kuruluğu")
            analysis['solutions'].append({
                'action': 'Acil topraklama elektrodu kontrolü',
                'steps': [
                    'Topraklama elektrodu görsel kontrol',
                    'Direnç ölçümü yapılmalı',
                    'Gerekirse yeni elektrot takılmalı',
                    'Toprak nemlendirme (kuru toprak durumunda)'
                ],
                'priority': 'high',
                'estimated_time': '2-4 saat'
            })
        elif resistance > 10:
            analysis['warnings'].append({
                'parameter': 'toprak_direnci',
                'value': resistance,
                'description': f"Toprak direnci yüksek ({resistance} Ohm). Önleyici bakım gerekli."
            })
            analysis['preventive_actions'].append({
                'action': 'Önleyici bakım',
                'description': 'Korozyon kontrolü ve toprak nemlendirme yapılmalı',
                'priority': 'medium'
            })
        
        # Kaçak Akım Analizi
        normal_leakage = self.sensor_ranges['kacak_akim']
        if leakage > 30:
            analysis['critical_issues'].append({
                'parameter': 'kacak_akim',
                'value': leakage,
                'normal_range': f"{normal_leakage['min']}-{normal_leakage['max']} {normal_leakage['unit']}",
                'severity': 'critical',
                'description': f"Kaçak akım kritik seviyede ({leakage} mA). Elektrik güvenliği riski var."
            })
            analysis['root_causes'].append("İzolasyon hatası, nem veya hasarlı kablolar")
            analysis['solutions'].append({
                'action': 'Acil izolasyon kontrolü ve trafo izolasyonu',
                'steps': [
                    'Trafo izole edilmeli (otomatik sistem devreye girmeli)',
                    'İzolasyon testi yapılmalı',
                    'Hasarlı kablolar değiştirilmeli',
                    'Nem kontrolü yapılmalı'
                ],
                'priority': 'critical',
                'estimated_time': '1-2 saat'
            })
        elif leakage > 20:
            analysis['warnings'].append({
                'parameter': 'kacak_akim',
                'value': leakage,
                'description': f"Kaçak akım artıyor ({leakage} mA). İzolasyon kontrolü gerekli."
            })
            analysis['preventive_actions'].append({
                'action': 'İzolasyon testi',
                'description': 'Önleyici izolasyon kontrolü yapılmalı',
                'priority': 'high'
            })
        
        # Korozyon Analizi
        if corrosion > 60:
            analysis['critical_issues'].append({
                'parameter': 'korozyon_seviyesi',
                'value': corrosion,
                'severity': 'critical',
                'description': f"Korozyon kritik seviyede ({corrosion}). Topraklama elektrodu değişimi gerekli."
            })
            analysis['root_causes'].append("Nem, tuzlu ortam veya kimyasal etkiler")
            analysis['solutions'].append({
                'action': 'Topraklama elektrodu değişimi',
                'steps': [
                    'Eski elektrot çıkarılmalı',
                    'Yeni korumalı elektrot takılmalı',
                    'Korozyon önleyici kaplama uygulanmalı',
                    'Düzenli kontrol planı oluşturulmalı'
                ],
                'priority': 'high',
                'estimated_time': '4-6 saat'
            })
        elif corrosion > 40:
            analysis['warnings'].append({
                'parameter': 'korozyon_seviyesi',
                'value': corrosion,
                'description': f"Korozyon seviyesi yüksek ({corrosion}). Önleyici bakım planlanmalı."
            })
            analysis['preventive_actions'].append({
                'action': 'Korozyon önleyici bakım',
                'description': 'Koruyucu kaplama ve düzenli temizlik yapılmalı',
                'priority': 'medium'
            })
        
        # Trend analizi
        if trends:
            if trends['trend'] == 'artış' and trends['change'] > 15:
                analysis['warnings'].append({
                    'parameter': 'risk_trend',
                    'description': f"Risk skoru son {trends['days']} günde {trends['change']:.1f} puan arttı. Hızlanan bozulma işareti."
                })
                analysis['preventive_actions'].append({
                    'action': 'Acil önleyici bakım',
                    'description': 'Trend analizi kritik bozulma gösteriyor. Hemen müdahale edilmeli',
                    'priority': 'high'
                })
        
        # Risk seviyesi değerlendirmesi
        if risk_level == 'high':
            analysis['status'] = 'critical'
            analysis['timeline'] = 'immediate_action_required'
        elif risk_level == 'medium':
            analysis['status'] = 'warning'
            analysis['timeline'] = 'preventive_maintenance_recommended'
        
        return analysis


class LLMResponseGenerator:
    """LLM ile dinamik yanıt üretir"""
    
    def __init__(self):
        self.use_ollama = USE_OLLAMA
        self.use_openai = USE_OPENAI if not USE_OLLAMA else False
    
    def generate_response(self, question: str, context: Dict, analysis: Optional[Dict], recommendations: List) -> str:
        """Dinamik yanıt üret - LLM kullanarak"""
        
        # Context'i prompt'a dönüştür
        prompt = self._build_prompt(question, context, analysis, recommendations)
        
        # LLM ile yanıt üret
        if self.use_ollama:
            return self._generate_with_ollama(prompt)
        elif self.use_openai:
            return self._generate_with_openai(prompt)
        else:
            return self._generate_fallback(question, context, analysis, recommendations)
    
    def _build_prompt(self, question: str, context: Dict, analysis: Optional[Dict], recommendations: List) -> str:
        """Prompt oluştur - Dinamik context ile"""
        
        prompt = f"""Sen bir topraklama izleme sistemi uzmanısın. Kullanıcıya teknik analiz ve öneriler sunuyorsun.

SORU: {question}

SİSTEM DURUMU:
"""
        
        if 'system_stats' in context and context['system_stats']:
            stats = context['system_stats']
            prompt += f"- Toplam trafo: {stats.get('total_transformers', 0)}\n"
            prompt += f"- Anomali sayısı: {stats.get('anomaly_count', 0)}\n"
            prompt += f"- İzole trafo: {stats.get('isolated_count', 0)}\n"
            prompt += f"- Ortalama risk: {stats.get('average_risk', 0):.1f}\n"
        
        if 'transformer' in context and context['transformer']:
            tf = context['transformer']
            prompt += f"""
TRAFO BİLGİLERİ:
- İsim: {tf.get('name', 'Bilinmiyor')}
- Bölge: {tf.get('region', 'Bilinmiyor')}
- Risk Skoru: {tf.get('risk_score', 0):.1f} ({tf.get('risk_level', 'unknown')})
- Anomali: {'Evet' if tf.get('is_anomaly') else 'Hayır'}
- Durum: {'İzole' if not tf.get('isolation_status') else 'Aktif'}

SENSÖR VERİLERİ:
- Toprak Direnci: {tf.get('sensor_data', {}).get('toprak_direnci', 0)} Ohm (Normal: 2-5 Ohm)
- Kaçak Akım: {tf.get('sensor_data', {}).get('kacak_akim', 0)} mA (Normal: 0-10 mA)
- Toprak Potansiyeli: {tf.get('sensor_data', {}).get('toprak_potansiyel', 0)} V (Normal: -5-5 V)
- Toprak Nemi: {tf.get('sensor_data', {}).get('toprak_nemi', 0)} % (Normal: 20-60%)
- Toprak Sıcaklığı: {tf.get('sensor_data', {}).get('toprak_sicakligi', 0)} °C (Normal: 5-35°C)
- Korozyon Seviyesi: {tf.get('sensor_data', {}).get('korozyon_seviyesi', 0)} (Normal: 0-30)
"""
        
        if analysis:
            prompt += f"""
DETAYLI ANALİZ:
"""
            if analysis.get('critical_issues'):
                prompt += "KRİTİK SORUNLAR:\n"
                for issue in analysis['critical_issues']:
                    prompt += f"- {issue.get('description', '')}\n"
            
            if analysis.get('warnings'):
                prompt += "UYARILAR:\n"
                for warning in analysis['warnings']:
                    if isinstance(warning, dict):
                        prompt += f"- {warning.get('description', '')}\n"
                    else:
                        prompt += f"- {warning}\n"
            
            if analysis.get('root_causes'):
                prompt += f"MUHTEMEL NEDENLER: {', '.join(analysis['root_causes'])}\n"
            
            if analysis.get('solutions'):
                prompt += "ÇÖZÜM ÖNERİLERİ:\n"
                for solution in analysis['solutions']:
                    prompt += f"- {solution.get('action', '')} (Öncelik: {solution.get('priority', 'medium')}, Süre: {solution.get('estimated_time', 'bilinmiyor')})\n"
                    if solution.get('steps'):
                        for step in solution['steps']:
                            prompt += f"  * {step}\n"
        
        if recommendations:
            prompt += f"\nÖNERİLER:\n"
            for rec in recommendations[:5]:
                prompt += f"- {rec}\n"
        
        prompt += """
GÖREVİN:
1. Kullanıcının sorusunu anla ve dinamik bir yanıt ver
2. Teknik detayları açık ve anlaşılır şekilde açıkla
3. Sorunları önceden tespit et ve öneriler sun
4. Hataların nasıl çözüleceğini adım adım açıkla
5. Önleyici bakım önerileri ver
6. Kodlanmış mesajlar değil, gerçek zamanlı analiz yap

YANIT (Türkçe, teknik ama anlaşılır):
"""
        
        return prompt
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """Ollama ile yanıt üret"""
        try:
            response = ollama.chat(
                model='llama3',  # veya llama3.2, mistral, vb.
                messages=[
                    {
                        'role': 'system',
                        'content': 'Sen bir topraklama izleme sistemi uzmanısın. Teknik analiz ve öneriler sunuyorsun.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            print(f"Ollama hatasi: {e}")
            return self._generate_fallback_simple(prompt)
    
    def _generate_with_openai(self, prompt: str) -> str:
        """OpenAI ile yanıt üret"""
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir topraklama izleme sistemi uzmanısın. Teknik analiz ve öneriler sunuyorsun."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI hatasi: {e}")
            return self._generate_fallback_simple(prompt)
    
    def _generate_fallback(self, question: str, context: Dict, analysis: Optional[Dict], recommendations: List) -> str:
        """LLM yoksa fallback yanıt"""
        response = ""
        
        if 'transformer' in context and context['transformer']:
            tf = context['transformer']
            response = f"{tf.get('name', 'Trafo')} analizi:\n\n"
            
            if analysis:
                if analysis.get('critical_issues'):
                    response += "🔴 KRİTİK SORUNLAR:\n"
                    for issue in analysis['critical_issues']:
                        response += f"• {issue.get('description', '')}\n"
                    response += "\n"
                
                if analysis.get('solutions'):
                    response += "💡 ÇÖZÜM ÖNERİLERİ:\n"
                    for solution in analysis['solutions']:
                        response += f"• {solution.get('action', '')}\n"
                        if solution.get('steps'):
                            for step in solution['steps']:
                                response += f"  - {step}\n"
                    response += "\n"
        
        if recommendations:
            response += "📋 ÖNERİLER:\n"
            for rec in recommendations[:3]:
                response += f"• {rec}\n"
        
        return response if response else "Sistem analizi yapılıyor..."
    
    def _generate_fallback_simple(self, prompt: str) -> str:
        """Basit fallback"""
        return "LLM modeli şu anda kullanılamıyor. Lütfen Ollama veya OpenAI API anahtarı yapılandırın."


# Global instances
data_access = ChatDataAccess()
analyzer = DynamicAnalyzer()
llm_generator = LLMResponseGenerator()

# Verileri yükle
data_access.load_historical_data()

# Model yükle
try:
    model, scaler = load_model()
    analyzer.model = model
    analyzer.scaler = scaler
    print("[OK] Anomali tespit modeli yuklendi")
except Exception as e:
    print(f"[!] Model yuklenemedi: {e}")


@app.route('/api/chat', methods=['POST'])
def chat():
    """Dinamik chat endpoint - LLM ile"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        transformer_id = data.get('transformer_id', None)
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Soru gerekli'
            }), 400
        
        # Context oluştur - DINAMIK VERI
        context = {
            'current_time': datetime.now().isoformat(),
            'question': question,
            'system_stats': data_access.get_dashboard_stats(),
        }
        
        if transformer_id:
            context['transformer'] = data_access.get_transformer_current(transformer_id)
            context['history'] = data_access.get_transformer_history(transformer_id, days=30)
            context['trends'] = data_access.analyze_trends(transformer_id, days=7)
            if context['transformer']:
                context['similar_cases'] = data_access.find_similar_cases(context['transformer'])
        else:
            context['all_transformers'] = data_access.get_all_transformers()
        
        # Detaylı analiz - DINAMIK
        analysis = None
        if transformer_id and 'transformer' in context and context['transformer']:
            analysis = analyzer.analyze_transformer_detailed(
                context['transformer'],
                context.get('history'),
                context.get('trends')
            )
        
        # Öneriler
        recommendations = []
        if analysis:
            if analysis.get('solutions'):
                recommendations.extend([s.get('action', '') for s in analysis['solutions']])
            if analysis.get('preventive_actions'):
                recommendations.extend([a.get('action', '') for a in analysis['preventive_actions']])
        
        # LLM ile dinamik yanıt üret
        response = llm_generator.generate_response(question, context, analysis, recommendations)
        
        return jsonify({
            'success': True,
            'response': response,
            'analysis': analysis,
            'recommendations': recommendations,
            'context': {
                'transformer_id': transformer_id,
                'has_analysis': analysis is not None,
                'has_llm': llm_generator.use_ollama or llm_generator.use_openai
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat/health', methods=['GET'])
def chat_health():
    """Chat sistemi sağlık kontrolü"""
    return jsonify({
        'status': 'ok',
        'llm_available': llm_generator.use_ollama or llm_generator.use_openai,
        'model_loaded': model is not None,
        'data_loaded': data_access.sensor_df is not None,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Dinamik Chat Backend API Baslatiliyor...")
    print("=" * 60)
    print(f"LLM Durumu: {'Ollama' if USE_OLLAMA else 'OpenAI' if USE_OPENAI else 'Yok (Fallback)'}")
    print(f"Model Durumu: {'Yuklu' if model else 'Yuklenemedi'}")
    print(f"Veri Durumu: {'Yuklu' if data_access.sensor_df is not None else 'Yuklenemedi'}")
    print("=" * 60)
    print("Endpoint: POST /api/chat")
    print("Health: GET /api/chat/health")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5001)

