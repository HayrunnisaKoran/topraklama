"""
Yapay Zeka Model Eğitim Scripti
Isolation Forest algoritması ile anomali tespiti modeli eğitir.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score
import joblib
import os
import sys
from config import MODEL_CONFIG, DATA_GENERATION

def load_and_prepare_data():
    """
    CSV dosyasından veriyi yükler ve model için hazırlar.
    
    Returns:
        X: Özellik matrisi
        y: Gerçek anomali etiketleri (doğrulama için)
    """
    data_file = DATA_GENERATION['output_file']
    
    if not os.path.exists(data_file):
        print(f"[X] Veri dosyasi bulunamadi: {data_file}")
        print("Once 'python veri_uret.py' komutunu calistirin!")
        sys.exit(1)
    
    print(f"Veri yukleniyor: {data_file}")
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"[OK] {len(df):,} kayit yuklendi")
    
    # Model için özellikleri seç (sensör değerleri)
    feature_columns = [
        'toprak_direnci',
        'kacak_akim',
        'toprak_potansiyel',
        'toprak_nemi',
        'toprak_sicakligi',
        'korozyon_seviyesi'
    ]
    
    X = df[feature_columns].values
    y = df['anomali'].values  # Gerçek etiketler (doğrulama için)
    
    return X, y, df


def train_isolation_forest(X_train, contamination=0.1):
    """
    Isolation Forest modeli eğitir.
    
    Args:
        X_train: Eğitim verisi
        contamination: Beklenen anomali oranı (0.1 = %10)
    
    Returns:
        model: Eğitilmiş model
        scaler: Veri ölçeklendirici
    """
    print("\nModel egitimi basliyor...")
    print(f"   Algoritma: Isolation Forest")
    print(f"   Beklenen anomali orani: {contamination*100:.1f}%")
    
    # Veriyi ölçeklendir (normalize et)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # Isolation Forest modeli oluştur
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        n_jobs=-1
    )
    
    # Modeli eğit
    print("   Model egitiliyor...")
    model.fit(X_scaled)
    print("   [OK] Model egitimi tamamlandi!")
    
    return model, scaler


def evaluate_model(model, scaler, X_test, y_test):
    """
    Model performansını değerlendirir.
    
    Args:
        model: Eğitilmiş model
        scaler: Veri ölçeklendirici
        X_test: Test verisi
        y_test: Gerçek etiketler
    """
    print("\nModel degerlendirmesi yapiliyor...")
    
    # Test verisini ölçeklendir
    X_test_scaled = scaler.transform(X_test)
    
    # Tahmin yap
    predictions = model.predict(X_test_scaled)
    
    # Isolation Forest: -1 = anomali, 1 = normal
    # Bizim etiketlerimiz: 1 = anomali, 0 = normal
    # Dönüştürme yap
    predictions_binary = (predictions == -1).astype(int)
    
    # Metrikleri hesapla
    f1 = f1_score(y_test, predictions_binary)
    precision = precision_score(y_test, predictions_binary, zero_division=0)
    recall = recall_score(y_test, predictions_binary, zero_division=0)
    
    print("\nPerformans Metrikleri:")
    print(f"   - F1 Skoru: {f1:.4f}")
    print(f"   - Kesinlik (Precision): {precision:.4f}")
    print(f"   - Duyarlilik (Recall): {recall:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, predictions_binary)
    print("\nConfusion Matrix:")
    print(f"   Gercek Normal / Tahmin Normal: {cm[0,0]}")
    print(f"   Gercek Normal / Tahmin Anomali: {cm[0,1]}")
    print(f"   Gercek Anomali / Tahmin Normal: {cm[1,0]}")
    print(f"   Gercek Anomali / Tahmin Anomali: {cm[1,1]}")
    
    # Detaylı rapor
    print("\nDetayli Siniflandirma Raporu:")
    print(classification_report(y_test, predictions_binary, 
                              target_names=['Normal', 'Anomali'],
                              zero_division=0))
    
    return {
        'f1_score': f1,
        'precision': precision,
        'recall': recall,
        'confusion_matrix': cm
    }


def predict_anomaly(model, scaler, sensor_data):
    """
    Yeni bir sensör verisi için anomali tahmini yapar.
    
    Args:
        model: Eğitilmiş model
        scaler: Veri ölçeklendirici
        sensor_data: Sensör verisi (dict veya array)
    
    Returns:
        is_anomaly: True/False
        anomaly_score: Anomali skoru (-1 ile 1 arası, düşük değer = anomali)
    """
    # Dict ise array'e çevir
    if isinstance(sensor_data, dict):
        feature_columns = [
            'toprak_direnci',
            'kacak_akim',
            'toprak_potansiyel',
            'toprak_nemi',
            'toprak_sicakligi',
            'korozyon_seviyesi'
        ]
        sensor_array = np.array([[sensor_data[col] for col in feature_columns]])
    else:
        sensor_array = sensor_data.reshape(1, -1)
    
    # Ölçeklendir
    sensor_scaled = scaler.transform(sensor_array)
    
    # Tahmin yap
    prediction = model.predict(sensor_scaled)[0]
    anomaly_score = model.score_samples(sensor_scaled)[0]
    
    is_anomaly = (prediction == -1)
    
    return is_anomaly, anomaly_score


def calculate_risk_score(anomaly_score, sensor_data):
    """
    Anomali skorundan risk puanı hesaplar (0-100 arası).
    
    Args:
        anomaly_score: Modelin verdiği anomali skoru
        sensor_data: Sensör verisi (risk hesaplaması için)
    
    Returns:
        risk_score: 0-100 arası risk puanı
    """
    # Anomali skorunu normalize et (düşük skor = yüksek risk)
    # Isolation Forest skorları genellikle -0.5 ile 0.5 arasındadır
    normalized_score = (anomaly_score + 0.5) / 1.0  # 0-1 arasına normalize et
    
    # Risk puanı: Düşük anomaly_score = Yüksek risk
    base_risk = (1 - normalized_score) * 100
    
    # Sensör değerlerine göre ek risk faktörleri
    risk_factors = 0
    
    # Toprak direnci yüksekse risk artar
    if sensor_data.get('toprak_direnci', 0) > 10:
        risk_factors += 20
    
    # Kaçak akım yüksekse risk artar
    if sensor_data.get('kacak_akim', 0) > 20:
        risk_factors += 15
    
    # Korozyon yüksekse risk artar
    if sensor_data.get('korozyon_seviyesi', 0) > 50:
        risk_factors += 10
    
    risk_score = min(base_risk + risk_factors, 100)
    
    return round(risk_score, 2)


def save_model(model, scaler, model_path=None):
    """
    Eğitilmiş modeli ve scaler'ı kaydeder.
    
    Args:
        model: Eğitilmiş model
        scaler: Veri ölçeklendirici
        model_path: Kayıt yolu
    """
    if model_path is None:
        model_path = MODEL_CONFIG['model_path']
    
    # Klasör yoksa oluştur
    model_dir = os.path.dirname(model_path)
    if model_dir and not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    # Modeli kaydet
    joblib.dump({
        'model': model,
        'scaler': scaler
    }, model_path)
    
    print(f"\nModel kaydedildi: {model_path}")


def load_model(model_path=None):
    """
    Kaydedilmiş modeli yükler.
    
    Args:
        model_path: Model yolu
    
    Returns:
        model: Yüklenen model
        scaler: Yüklenen scaler
    """
    if model_path is None:
        model_path = MODEL_CONFIG['model_path']
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")
    
    data = joblib.load(model_path)
    return data['model'], data['scaler']


def main():
    """
    Ana eğitim fonksiyonu
    """
    print("=" * 60)
    print("Yapay Zeka Model Egitimi")
    print("=" * 60)
    
    # Veriyi yükle
    X, y, df = load_and_prepare_data()
    
    # Veriyi eğitim ve test olarak ayır (%80 eğitim, %20 test)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\nVeri Bolunmesi:")
    print(f"   - Egitim: {len(X_train):,} kayit")
    print(f"   - Test: {len(X_test):,} kayit")
    
    # Modeli eğit
    contamination = MODEL_CONFIG['contamination']
    model, scaler = train_isolation_forest(X_train, contamination)
    
    # Modeli değerlendir
    metrics = evaluate_model(model, scaler, X_test, y_test)
    
    # Modeli kaydet
    save_model(model, scaler)
    
    # Örnek tahmin
    print("\nOrnek Tahmin Testi:")
    sample_data = {
        'toprak_direnci': 3.5,
        'kacak_akim': 5.0,
        'toprak_potansiyel': 1.0,
        'toprak_nemi': 40.0,
        'toprak_sicakligi': 20.0,
        'korozyon_seviyesi': 15.0
    }
    is_anomaly, anomaly_score = predict_anomaly(model, scaler, sample_data)
    risk_score = calculate_risk_score(anomaly_score, sample_data)
    
    print(f"   Ornek Veri: {sample_data}")
    print(f"   Anomali Tespiti: {'[!] EVET' if is_anomaly else '[OK] HAYIR'}")
    print(f"   Anomali Skoru: {anomaly_score:.4f}")
    print(f"   Risk Puani: {risk_score:.2f}/100")
    
    print("\n" + "=" * 60)
    print("[OK] Model egitimi basariyla tamamlandi!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[X] Hata olustu: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

