# 🤖 Dinamik Chat Sistemi - Kullanım Kılavuzu

## 🎯 Özellikler

✅ **Dinamik Analiz** - Gerçek zamanlı veri analizi
✅ **LLM Entegrasyonu** - Ollama veya OpenAI ile akıllı yanıtlar
✅ **Model Eğitimi** - Özel eğitim verisi ile fine-tuning
✅ **Hata Analizi** - Detaylı sorun tespiti ve çözüm önerileri
✅ **Önleyici Bakım** - Sorunları önceden tespit edip öneriler sunma

## 📋 Kurulum

### 1. LLM Kurulumu (Seçenek 1: Ollama - Ücretsiz)

```bash
# Ollama'yı indir ve kur: https://ollama.ai
# Model indir
ollama pull llama3
# veya
ollama pull mistral
```

### 2. LLM Kurulumu (Seçenek 2: OpenAI)

```bash
# OpenAI API anahtarı gerekli
export OPENAI_API_KEY="your-api-key"
```

### 3. Chat Paketlerini Yükle

```bash
pip install -r requirements_chat.txt
```

## 🚀 Kullanım

### 1. Model Eğitimi (İlk Sefer)

```bash
python chat_model_egitim.py
```

Bu komut:
- CSV verilerinden eğitim verisi oluşturur
- `data/chat_training_data.jsonl` dosyasına kaydeder
- Dinamik soru-cevap çiftleri üretir

### 2. Chat Backend'i Başlat

```bash
python chat_llm.py
```

Chat API `http://localhost:5001` adresinde çalışacak.

### 3. API Kullanımı

**POST** `/api/chat`

```json
{
  "question": "Trafo 5'in durumu nasıl?",
  "transformer_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "response": "Trafo 5 analizi:\n\n🔴 KRİTİK SORUNLAR:\n• Toprak direnci kritik seviyede...",
  "analysis": {
    "status": "critical",
    "critical_issues": [...],
    "solutions": [...]
  },
  "recommendations": [...]
}
```

## 💡 Örnek Sorular

### Durum Sorguları
- "Trafo 5'in durumu nasıl?"
- "Hangi trafolar yüksek risk altında?"
- "Sistem genel durumu nedir?"

### Analiz Sorguları
- "Trafo 10 için risk analizi yapabilir misin?"
- "Trafo 7'de ne gibi sorunlar var?"
- "Anomali tespit edilen trafolar hangileri?"

### Çözüm Sorguları
- "Trafo 5'te toprak direnci yüksek, ne yapmalıyım?"
- "Kaçak akım sorunu nasıl çözülür?"
- "Korozyon problemi için önerilerin neler?"

### Önleyici Bakım
- "Trafo 3 için önleyici bakım önerilerin neler?"
- "Hangi trafolar bakım gerektiriyor?"
- "Sorunları önceden nasıl tespit edebilirim?"

## 🔧 Sistem Mimarisi

```
Kullanıcı Sorusu
    ↓
Chat API (/api/chat)
    ↓
Veri Çekme (API + CSV) - DINAMIK
    ↓
Detaylı Analiz (DynamicAnalyzer)
    ↓
LLM Prompt Oluşturma
    ↓
LLM Yanıt Üretimi (Ollama/OpenAI)
    ↓
Dinamik Yanıt
```

## 📊 Analiz Özellikleri

### 1. Detaylı Hata Analizi
- Kritik sorunların tespiti
- Kök neden analizi
- Çözüm adımları (adım adım)
- Öncelik ve süre tahmini

### 2. Önleyici Bakım
- Trend analizi
- Risk artışı tespiti
- Önleyici öneriler
- Benzer durum analizi

### 3. Dinamik Yorumlar
- Gerçek zamanlı veri analizi
- Model sonuçlarını yorumlama
- Sensör değerlerini açıklama
- Risk skorlarını değerlendirme

## ⚙️ Konfigürasyon

### LLM Model Seçimi

`chat_llm.py` dosyasında:

```python
# Ollama için
response = ollama.chat(
    model='llama3',  # veya 'mistral', 'llama3.2'
    ...
)

# OpenAI için
response = client.chat.completions.create(
    model="gpt-4",  # veya "gpt-3.5-turbo"
    ...
)
```

## 🎓 Model Eğitimi

### Eğitim Verisi Oluşturma

```bash
python chat_model_egitim.py
```

Oluşturulan veri:
- `data/chat_training_data.jsonl`
- Her trafo için dinamik soru-cevap çiftleri
- Farklı senaryolar (durum, risk, çözüm, önleyici bakım)

### Fine-Tuning (İsteğe Bağlı)

Eğitim verisi ile model fine-tuning yapılabilir:

```python
# Ollama fine-tuning
ollama create my-chat-model -f Modelfile

# OpenAI fine-tuning
openai api fine_tunes.create -t chat_training_data.jsonl -m gpt-3.5-turbo
```

## 🔍 Dinamik Özellikler

### ✅ Gerçek Zamanlı Veri
- API'den güncel trafo verileri
- CSV'den tarihsel analiz
- Trend analizi

### ✅ Akıllı Analiz
- Model ile anomali tespiti
- Sensör değer analizi
- Risk değerlendirmesi

### ✅ Çözüm Önerileri
- Adım adım çözüm planı
- Öncelik sıralaması
- Süre tahmini
- Benzer durum analizi

### ✅ Önleyici Bakım
- Trend analizi
- Risk artışı tespiti
- Önleyici öneriler

## 📝 Notlar

1. **LLM Gerekli**: Dinamik yanıtlar için Ollama veya OpenAI gerekli
2. **Model Eğitimi**: İlk kullanımda `chat_model_egitim.py` çalıştırılmalı
3. **API Bağlantısı**: Ana API (`app.py`) çalışıyor olmalı
4. **Veri Güncelliği**: Chat sistemi her zaman güncel veriyi çeker

## 🚨 Sorun Giderme

### LLM çalışmıyorsa:
- Ollama kurulu mu kontrol edin: `ollama list`
- OpenAI API anahtarı doğru mu kontrol edin
- Fallback modu kullanılır (basit analiz)

### Model yüklenemiyorsa:
- `models/anomali_model.pkl` dosyası var mı?
- `python model_egit.py` çalıştırın

### Veri bulunamıyorsa:
- `data/sensor_data.csv` var mı?
- `python veri_uret.py` çalıştırın

