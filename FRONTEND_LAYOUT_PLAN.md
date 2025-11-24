# 🎨 Frontend Layout ve Sidebar Planı

## 📐 Layout Yapısı

```
┌─────────────────────────────────────────────────────┐
│ HEADER (70px yükseklik)                            │
│ ┌─────┬───────────────────────────┬──────────────┐ │
│ │Logo │      Arama Çubuğu         │ 🔔 👤        │ │
│ └─────┴───────────────────────────┴──────────────┘ │
├──────┬──────────────────────────────────────────────┤
│      │                                              │
│ SIDE │         MAIN CONTENT AREA                   │
│ BAR  │         (Dinamik - Router ile)              │
│(250px│                                              │
│ geniş│                                              │
│)     │                                              │
│      │                                              │
│ 📊   │                                              │
│ İstat│                                              │
│      │                                              │
│ 🗺️   │                                              │
│ Harita│                                             │
│      │                                              │
│ 💬   │                                              │
│ Chat │                                              │
│      │                                              │
│ 📈   │                                              │
│ Graf │                                              │
│      │                                              │
│ ⚙️   │                                              │
│ Ayar │                                              │
│      │                                              │
│ 👤   │                                              │
│ Hesap│                                              │
│      │                                              │
└──────┴──────────────────────────────────────────────┘
```

## 🧩 Komponent Yapısı

### 1. Layout Komponenti (`Layout.jsx`)
```jsx
<Layout>
  <Sidebar />
  <MainContent>
    <Header />
    <Outlet /> {/* React Router outlet */}
  </MainContent>
</Layout>
```

### 2. Sidebar Komponenti (`Sidebar.jsx`)
- Menü öğeleri
- Aktif sayfa göstergesi
- Collapse/Expand
- Logo

### 3. Header Komponenti (`Header.jsx`)
- Arama çubuğu
- Bildirimler
- Profil dropdown

### 4. Sayfalar
- Dashboard (`/`)
- Harita (`/map`)
- Chat (`/chat`)
- Grafikler (`/analytics`)
- Ayarlar (`/settings`)
- Profil (`/profile`)
- Trafo Detay (`/transformer/:id`)

## 📋 Sidebar Menü Öğeleri

```javascript
const menuItems = [
  {
    id: 'dashboard',
    label: 'İstatistikler',
    icon: '📊',
    path: '/',
    badge: null
  },
  {
    id: 'map',
    label: 'Harita',
    icon: '🗺️',
    path: '/map',
    badge: null
  },
  {
    id: 'chat',
    label: 'Chat',
    icon: '💬',
    path: '/chat',
    badge: 3 // Yeni mesaj sayısı
  },
  {
    id: 'analytics',
    label: 'Grafikler',
    icon: '📈',
    path: '/analytics',
    badge: null
  },
  {
    id: 'settings',
    label: 'Ayarlar',
    icon: '⚙️',
    path: '/settings',
    badge: null
  },
  {
    id: 'profile',
    label: 'Hesaplar',
    icon: '👤',
    path: '/profile',
    badge: null
  }
];
```

## 🎯 Özellikler

### Sidebar:
- ✅ Collapse/Expand (küçük ekranlarda)
- ✅ Aktif sayfa vurgulama
- ✅ Badge desteği (bildirim sayısı)
- ✅ Hover efektleri
- ✅ Responsive tasarım

### Header:
- ✅ Arama çubuğu (trafoları arama)
- ✅ Bildirim ikonu (dropdown)
- ✅ Profil dropdown (çıkış yapma)
- ✅ Breadcrumb (opsiyonel)

### Layout:
- ✅ Responsive (mobil uyumlu)
- ✅ Dark mode desteği (gelecek)
- ✅ Smooth transitions
- ✅ Loading states

## 🔄 Dinamik Özellikler

### 1. Badge Güncellemeleri
- Chat: Yeni mesaj sayısı
- Bildirimler: Okunmamış bildirim sayısı
- Real-time güncelleme

### 2. Aktif Sayfa
- URL'e göre otomatik vurgulama
- React Router ile entegre

### 3. Collapse/Expand
- Küçük ekranlarda otomatik collapse
- Kullanıcı tercihi (localStorage)

## 📱 Responsive Tasarım

### Desktop (>1024px):
- Sidebar: 250px genişlik, her zaman görünür
- Main: Kalan alan

### Tablet (768px-1024px):
- Sidebar: 200px genişlik
- Collapse butonu

### Mobil (<768px):
- Sidebar: Drawer (açılır/kapanır)
- Hamburger menü
- Full screen içerik

