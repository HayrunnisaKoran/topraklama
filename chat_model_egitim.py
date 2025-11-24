"""
Chat Model Eğitimi
Dinamik yanıtlar için model eğitimi ve fine-tuning
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict

class ChatTrainingDataGenerator:
    """Chat için eğitim verisi oluşturur"""
    
    def __init__(self):
        self.sensor_data_path = 'data/sensor_data.csv'
        self.output_path = 'data/chat_training_data.jsonl'
        
    def generate_training_data(self):
        """Eğitim verisi oluştur - Dinamik soru-cevap çiftleri"""
        
        print("Chat model egitimi icin veri olusturuluyor...")
        
        # CSV verisini yükle
        df = pd.read_csv(self.sensor_data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        training_data = []
        
        # Her trafo için örnek sorular ve cevaplar oluştur
        for trafo_id in range(1, 51):
            trafo_data = df[df['transformer_id'] == trafo_id]
            if len(trafo_data) == 0:
                continue
            
            # Son kayıtları al
            recent = trafo_data.tail(100)
            
            # İstatistikler
            avg_resistance = recent['toprak_direnci'].mean()
            avg_leakage = recent['kacak_akim'].mean()
            avg_corrosion = recent['korozyon_seviyesi'].mean()
            anomaly_rate = recent['anomali'].mean() * 100
            
            # Risk değerlendirmesi
            risk_level = 'low'
            if avg_resistance > 10 or avg_leakage > 20 or avg_corrosion > 50:
                risk_level = 'high'
            elif avg_resistance > 5 or avg_leakage > 10 or avg_corrosion > 30:
                risk_level = 'medium'
            
            # Soru-Cevap çiftleri oluştur
            qa_pairs = self._generate_qa_pairs(trafo_id, recent, avg_resistance, avg_leakage, avg_corrosion, anomaly_rate, risk_level)
            training_data.extend(qa_pairs)
        
        # JSONL formatında kaydet
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for item in training_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"[OK] {len(training_data)} egitim verisi olusturuldu: {self.output_path}")
        return training_data
    
    def _generate_qa_pairs(self, trafo_id, data, avg_resistance, avg_leakage, avg_corrosion, anomaly_rate, risk_level):
        """Trafo için soru-cevap çiftleri oluştur"""
        
        qa_pairs = []
        
        # Durum sorusu
        qa_pairs.append({
            'question': f"Trafo {trafo_id}'in durumu nasıl?",
            'answer': self._generate_status_answer(trafo_id, avg_resistance, avg_leakage, avg_corrosion, risk_level),
            'context': {
                'transformer_id': trafo_id,
                'type': 'status'
            }
        })
        
        # Risk analizi
        if risk_level != 'low':
            qa_pairs.append({
                'question': f"Trafo {trafo_id} için risk analizi yapabilir misin?",
                'answer': self._generate_risk_analysis(trafo_id, avg_resistance, avg_leakage, avg_corrosion, risk_level),
                'context': {
                    'transformer_id': trafo_id,
                    'type': 'risk_analysis'
                }
            })
        
        # Sorun tespiti
        if avg_resistance > 10:
            qa_pairs.append({
                'question': f"Trafo {trafo_id}'de toprak direnci yüksek, ne yapmalıyım?",
                'answer': self._generate_solution_answer('toprak_direnci', avg_resistance),
                'context': {
                    'transformer_id': trafo_id,
                    'type': 'solution',
                    'issue': 'toprak_direnci'
                }
            })
        
        if avg_leakage > 20:
            qa_pairs.append({
                'question': f"Trafo {trafo_id}'de kaçak akım var, nasıl çözebilirim?",
                'answer': self._generate_solution_answer('kacak_akim', avg_leakage),
                'context': {
                    'transformer_id': trafo_id,
                    'type': 'solution',
                    'issue': 'kacak_akim'
                }
            })
        
        if avg_corrosion > 50:
            qa_pairs.append({
                'question': f"Trafo {trafo_id}'de korozyon sorunu var, ne önerirsin?',
                'answer': self._generate_solution_answer('korozyon', avg_corrosion),
                'context': {
                    'transformer_id': trafo_id,
                    'type': 'solution',
                    'issue': 'korozyon'
                }
            })
        
        # Önleyici bakım
        if risk_level == 'medium':
            qa_pairs.append({
                'question': f"Trafo {trafo_id} için önleyici bakım önerilerin neler?",
                'answer': self._generate_preventive_maintenance(trafo_id, avg_resistance, avg_leakage, avg_corrosion),
                'context': {
                    'transformer_id': trafo_id,
                    'type': 'preventive'
                }
            })
        
        return qa_pairs
    
    def _generate_status_answer(self, trafo_id, resistance, leakage, corrosion, risk_level):
        """Durum cevabı oluştur"""
        risk_text = {'low': 'düşük', 'medium': 'orta', 'high': 'yüksek'}[risk_level]
        
        answer = f"Trafo {trafo_id} şu anda {risk_text} risk seviyesinde. "
        
        issues = []
        if resistance > 10:
            issues.append(f"toprak direnci yüksek ({resistance:.1f} Ohm)")
        if leakage > 20:
            issues.append(f"kaçak akım yüksek ({leakage:.1f} mA)")
        if corrosion > 50:
            issues.append(f"korozyon kritik ({corrosion:.1f})")
        
        if issues:
            answer += f"Tespit edilen sorunlar: {', '.join(issues)}. "
            answer += "Acil müdahale önerilir."
        else:
            answer += "Sistem normal çalışıyor."
        
        return answer
    
    def _generate_risk_analysis(self, trafo_id, resistance, leakage, corrosion, risk_level):
        """Risk analizi cevabı"""
        answer = f"Trafo {trafo_id} için risk analizi:\n\n"
        
        if resistance > 10:
            answer += f"🔴 Toprak direnci kritik: {resistance:.1f} Ohm (Normal: 2-5 Ohm). "
            answer += "Bu, topraklama sisteminin etkinliğini ciddi şekilde azaltır. "
            answer += "Korozyon kontrolü ve topraklama elektrodu değişimi gerekli.\n\n"
        
        if leakage > 20:
            answer += f"🔴 Kaçak akım yüksek: {leakage:.1f} mA (Normal: 0-10 mA). "
            answer += "Elektrik güvenliği riski var. İzolasyon kontrolü ve trafo izolasyonu gerekli.\n\n"
        
        if corrosion > 50:
            answer += f"🔴 Korozyon kritik: {corrosion:.1f}. "
            answer += "Topraklama elektrodu değişimi ve koruyucu kaplama uygulanmalı.\n\n"
        
        answer += f"Genel risk seviyesi: {risk_level.upper()}. "
        answer += "Önleyici bakım ve düzenli izleme önerilir."
        
        return answer
    
    def _generate_solution_answer(self, issue_type, value):
        """Çözüm cevabı oluştur"""
        
        if issue_type == 'toprak_direnci':
            return f"""Toprak direnci {value:.1f} Ohm seviyesinde, bu kritik bir durum.

ÇÖZÜM ADIMLARI:
1. Topraklama elektrodu görsel kontrol yapılmalı
2. Direnç ölçümü tekrarlanmalı
3. Korozyon kontrolü yapılmalı
4. Gerekirse yeni elektrot takılmalı (2-4 saat)
5. Toprak nemlendirme (kuru toprak durumunda)

ÖNCELİK: Yüksek
TAHMINI SÜRE: 2-4 saat"""

        elif issue_type == 'kacak_akim':
            return f"""Kaçak akım {value:.1f} mA seviyesinde, bu güvenlik riski oluşturuyor.

ÇÖZÜM ADIMLARI:
1. Trafo izole edilmeli (otomatik sistem devreye girmeli)
2. İzolasyon testi yapılmalı
3. Hasarlı kablolar tespit edilmeli ve değiştirilmeli
4. Nem kontrolü yapılmalı
5. İzolasyon malzemeleri kontrol edilmeli

ÖNCELİK: Kritik
TAHMINI SÜRE: 1-2 saat"""

        elif issue_type == 'korozyon':
            return f"""Korozyon seviyesi {value:.1f}, bu kritik bir durum.

ÇÖZÜM ADIMLARI:
1. Eski elektrot çıkarılmalı
2. Yeni korumalı elektrot takılmalı
3. Korozyon önleyici kaplama uygulanmalı
4. Düzenli kontrol planı oluşturulmalı
5. Çevresel faktörler (nem, tuz) kontrol edilmeli

ÖNCELİK: Yüksek
TAHMINI SÜRE: 4-6 saat"""
        
        return "Çözüm analizi yapılıyor..."
    
    def _generate_preventive_maintenance(self, trafo_id, resistance, leakage, corrosion):
        """Önleyici bakım önerileri"""
        answer = f"Trafo {trafo_id} için önleyici bakım önerileri:\n\n"
        
        recommendations = []
        
        if resistance > 5:
            recommendations.append("• Toprak direnci yüksek - Korozyon kontrolü ve toprak nemlendirme")
        
        if leakage > 10:
            recommendations.append("• Kaçak akım artıyor - İzolasyon testi yapılmalı")
        
        if corrosion > 30:
            recommendations.append("• Korozyon seviyesi yüksek - Koruyucu kaplama uygulanmalı")
        
        if recommendations:
            answer += "\n".join(recommendations)
            answer += "\n\nBu önlemler alınmazsa sistem bozulabilir ve maliyetli onarımlar gerekebilir."
        else:
            answer += "Sistem normal çalışıyor. Düzenli kontroller yeterli."
        
        return answer


if __name__ == '__main__':
    generator = ChatTrainingDataGenerator()
    training_data = generator.generate_training_data()
    print(f"\nToplam {len(training_data)} egitim verisi olusturuldu.")

