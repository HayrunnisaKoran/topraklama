# 📁 Firebase Key Dosyası Konumu

## Dosya Konumu

Firebase service account key dosyanızı (`firebase-key.json`) **proje ana dizinine** koyun:

```
Topraklama Izleme ve Anomali/
├── firebase-key.json          ← BURAYA KOYUN
├── api_server.py
├── simulasyon.py
├── config.py
├── firebase_config.py
├── data/
├── models/
└── web-dashboard/
```

## Dosya Yolu

**Tam yol:**
```
C:\Users\hayru\OneDrive\Masaüstü\Topraklama Izleme ve Anomali\firebase-key.json
```

## Nasıl Koyulur?

### Yöntem 1: Dosya Gezgini ile
1. Firebase Console'dan indirdiğiniz JSON dosyasını bulun
2. Dosyayı kopyalayın
3. Proje klasörüne (`Topraklama Izleme ve Anomali`) yapıştırın
4. Dosya adını `firebase-key.json` olarak değiştirin

### Yöntem 2: Terminal ile
```powershell
# İndirilen dosyayı proje klasörüne kopyalayın
Copy-Item "C:\Users\hayru\Downloads\your-project-firebase-adminsdk-xxxxx.json" `
          "C:\Users\hayru\OneDrive\Masaüstü\Topraklama Izleme ve Anomali\firebase-key.json"
```

## Dosya Adı Önemli!

Dosya adı **tam olarak** `firebase-key.json` olmalıdır:
- ✅ `firebase-key.json` (DOĞRU)
- ❌ `firebase-key (1).json` (YANLIŞ)
- ❌ `firebase-adminsdk-xxxxx.json` (YANLIŞ)
- ❌ `firebase_key.json` (YANLIŞ)

## Kontrol

Dosyanın doğru yerde olduğunu kontrol etmek için:

```powershell
# Proje klasörüne gidin
cd "C:\Users\hayru\OneDrive\Masaüstü\Topraklama Izleme ve Anomali"

# Dosyanın varlığını kontrol edin
Test-Path firebase-key.json
# True dönerse dosya var demektir
```

## Güvenlik ⚠️

**ÖNEMLİ:** Bu dosya hassas bilgiler içerir!

- ✅ `.gitignore` dosyasına eklenmiştir (Git'e commit edilmez)
- ❌ **ASLA** Git repository'sine push etmeyin
- ❌ **ASLA** başkalarıyla paylaşmayın
- ❌ **ASLA** public bir yere yüklemeyin

## Sistem Nasıl Kullanır?

Kod dosyalarımız (`simulasyon.py` ve `api_server.py`) dosyayı şu şekilde arar:

```python
# Proje ana dizininde
if os.path.exists('firebase-key.json'):
    # Firebase kullan
    init_firebase('firebase-key.json')
else:
    # CSV kullan (fallback)
    print("Firebase key bulunamadı, CSV kullanılacak")
```

## Sorun Giderme

### Dosya bulunamıyor hatası alıyorsanız:

1. **Dosya adını kontrol edin:**
   - `firebase-key.json` (tam olarak bu isim)

2. **Dosya konumunu kontrol edin:**
   - Proje ana dizininde olmalı
   - Alt klasörlerde değil

3. **Çalışma dizinini kontrol edin:**
   ```powershell
   # Terminal'de proje klasöründe olduğunuzdan emin olun
   pwd
   # Çıktı: C:\Users\hayru\OneDrive\Masaüstü\Topraklama Izleme ve Anomali
   ```

4. **Dosya izinlerini kontrol edin:**
   - Dosya okunabilir olmalı
   - JSON formatında olmalı

## Örnek Dosya İçeriği

`firebase-key.json` dosyası şuna benzer görünmelidir:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

---

**Not:** Dosya yoksa sistem otomatik olarak CSV kullanır. Firebase kullanmak istiyorsanız dosyayı eklemeniz gerekir.

