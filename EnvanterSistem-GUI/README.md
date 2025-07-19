# 📦 Envanter ve Ödünç Takip Uygulaması

Bu proje, Python ve `customtkinter` kullanılarak geliştirilen modern bir masaüstü **envanter yönetim** ve **ödünç verme takibi** uygulamasıdır. Kullanıcılar ürünleri ekleyebilir, güncelleyebilir, silebilir, arayabilir, stokları düzenleyebilir ve ödünç-verme sürecini takip edebilir.

## 🎯 Özellikler

- 🔍 Ürün arama (ID veya isim ile)
- ➕ Ürün ekleme
- 🔁 Stok artırma/azaltma/güncelleme
- 🗑️ Ürün silme (tekli veya tümü)
- 📍 Lokasyon bilgisiyle ürün yönetimi
- 📋 Ödünç verme takibi:
  - Kişi ismi, telefon, iade tarihi ile ödünç kaydı
  - Otomatik stoktan düşme
  - Geciken ürünleri gösterme
  - Bugün iade edilecekleri filtreleme
  - Kaydı düzenleme ve iade alma
- 🎨 Modern ve koyu tema destekli arayüz

## 🖼️ Arayüzden Görünüm

![Envanter Takip Ekranı](demo.gif)  
> Yukarıda örnek arayüzün çalışır hâli gösterilmektedir.

## 🛠 Gereksinimler

- Python 3.8 veya üzeri
- Aşağıdaki pip paketleri:

```bash
pip install customtkinter
