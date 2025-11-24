# 🔥 Firebase Kurulum Kılavuzu

## Adım 1: Firebase Projesi Oluşturma

1. [Firebase Console](https://console.firebase.google.com/) adresine gidin
2. "Add project" (Proje Ekle) butonuna tıklayın
3. Proje adını girin (örn: "topraklama-izleme")
4. Google Analytics'i etkinleştirmek isteyip istemediğinizi seçin (opsiyonel)
5. "Create project" (Proje Oluştur) butonuna tıklayın

## Adım 2: Firestore Database Oluşturma

1. Firebase Console'da sol menüden "Firestore Database" seçin
2. "Create database" (Veritabanı Oluştur) butonuna tıklayın
3. "Start in test mode" (Test modunda başlat) seçin (geliştirme için)
4. Location (Konum) seçin (örn: europe-west)
5. "Enable" (Etkinleştir) butonuna tıklayın

## Adım 3: Service Account Key İndirme

1. Firebase Console'da sol üstteki ⚙️ (Settings) ikonuna tıklayın
2. "Project settings" (Proje ayarları) seçin
3. "Service accounts" (Hizmet hesapları) sekmesine gidin
4. "Generate new private key" (Yeni özel anahtar oluştur) butonuna tıklayın
5. JSON dosyasını indirin
6. Dosyayı proje klasörüne `firebase-key.json` olarak kaydedin

## Adım 4: Python Paketlerini Yükleme

```powershell
pip install firebase-admin
```

## Adım 5: Konfigürasyon

`firebase_config.py` dosyasında:

```python
# firebase-key.json dosyasının yolunu belirtin
credential_path = 'firebase-key.json'
project_id = 'topraklama-izleme'  # Firebase proje ID'niz
```

## Adım 6: Test

```powershell
python -c "from firebase_config import init_firebase; init_firebase('firebase-key.json', 'your-project-id'); print('✅ Firebase bağlantısı başarılı!')"
```

## ⚠️ Önemli Notlar

- `firebase-key.json` dosyasını **ASLA** Git'e commit etmeyin!
- `.gitignore` dosyasına `firebase-key.json` ekleyin
- Production'da environment variables kullanın

## 🔒 Güvenlik

Firestore Rules (Güvenlik Kuralları):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /transformer_data/{document=**} {
      allow read, write: if true;  // Test için - Production'da değiştirin!
    }
  }
}
```

---

**Not**: Firebase kullanmak zorunlu değil. Sistem CSV ile de çalışır!

