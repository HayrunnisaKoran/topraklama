"""
Veri Temizleme Scripti
Eski veri dosyalarını temizler
"""

import os
import shutil

def temizle():
    """Tüm veri dosyalarını temizler"""
    print("🧹 Veri temizleme başlıyor...")
    
    dosyalar = [
        'data/realtime_data.csv',
        'data/sensor_data.csv'
    ]
    
    for dosya in dosyalar:
        if os.path.exists(dosya):
            try:
                os.remove(dosya)
                print(f"✅ Silindi: {dosya}")
            except Exception as e:
                print(f"⚠️  Silinemedi {dosya}: {e}")
        else:
            print(f"ℹ️  Dosya yok: {dosya}")
    
    print("\n✅ Temizleme tamamlandı!")

if __name__ == "__main__":
    temizle()

