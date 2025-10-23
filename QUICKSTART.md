# 🚀 Quick Start Guide - Şikayet Yönetim Sistemi

5 dakikada sistemi çalıştırın!

## ⚡ Hızlı Kurulum

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. API Key Ayarlayın
```bash
# .env dosyası oluşturun
cp .env.example .env

# .env dosyasını editörünüzde açın
nano .env
```

**En az şunu ekleyin:**
```env
LLM_API_KEY=your-actual-api-key-here
```

### 3. Uygulamayı Başlatın
```bash
streamlit run app.py
```

🎉 **Tarayıcınızda `http://localhost:8501` otomatik açılacak!**

---

## 📝 İlk Şikayetinizi Test Edin

Arayüz açıldığında şunu yazın:
```
Merhaba, dün akşam Kadıköy'deki ATM'den 500 TL çekerken param sıkıştı
```

Sistem otomatik olarak:
1. ✅ Kategoriyi belirleyecek (ATM)
2. ✅ Mevcut bilgileri çıkaracak
3. ✅ Sadece eksik alanlar için soru soracak
4. ✅ JSON çıktısı üretecek

---

## 🔧 Özelleştirme (Opsiyonel)

### Kendi Kategorilerinizi Ekleyin

`categories.xlsx` dosyasını açın ve yeni satırlar ekleyin:

| kategori_adi | alan_adi | soru | alan_tipi | gerekli_mi | aciklama |
|--------------|----------|------|-----------|------------|----------|
| YeniKategori | yeni_alan | Sorunuz? | string | TRUE | Açıklama |

### Farklı Excel Sütunları Kullanın

1. `excel_config.json.example` → `excel_config.json` olarak kopyalayın
2. Sütun adlarınızı düzenleyin
3. Uygulamayı yeniden başlatın

---

## 🐛 Sorun mu var?

### "API hatası" alıyorsanız
- `.env` dosyasında `LLM_API_KEY` doğru mu?
- API krediniz yeterli mi?

### "Excel bulunamadı" hatası
- İlk çalıştırmada otomatik oluşacak
- Manuel oluşturmak için README.md'ye bakın

### Kategori çalışmıyor
- Debug mode'u açın: `config.py` → `DEBUG_MODE=True`
- Terminal çıktılarını kontrol edin

---

## 📚 Daha Fazlası

- 📖 Detaylı dokümantasyon: `README.md`
- 💡 Örnekler: `README.md` → "Örnek Senaryolar"
- ⚙️ Parametrik Excel: `README.md` → "Excel Parametrik Yapı"

---

**Başarılar! 🎉**
