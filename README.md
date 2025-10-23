# 💬 Şikayet Yönetim Sistemi - LLM Tabanlı Stateful Dialog Chatbot

Modern LLM (Büyük Dil Modeli) yeteneklerini klasik "Slot Filling" (Alan Doldurma) göreviyle birleştiren, duruma dayalı (stateful) bir diyalog sistemi.

## 🎯 Özellikler

- ✅ **Otomatik Kategorizasyon**: LLM ile şikayet metni otomatik kategorize edilir
- ✅ **Akıllı Alan Çıkarımı**: İlk metinden çıkarılabilecek tüm bilgiler otomatik tespit edilir
- ✅ **Dinamik Soru Yönetimi**: Sadece eksik alanlar için soru sorulur
- ✅ **Stateful Dialog**: Konuşma durumu `st.session_state` ile korunur
- ✅ **Excel Tabanlı Konfig**: Kategoriler, alanlar ve sorular Excel'den yönetilir
- ✅ **Parametrik Sütun Mapping**: Excel sütun adları tamamen özelleştirilebilir
- ✅ **Modüler Mimari**: Her bileşen ayrı modülde ve bağımsız çalışabilir
- ✅ **Streamlit UI**: Kullanıcı dostu modern arayüz
- ✅ **JSON Export**: Toplanan veriler JSON formatında indirilebilir

## 📁 Proje Yapısı

```
mycoderepository_LLM/
├── app.py                    # Streamlit ana uygulama
├── pipeline.py               # Ana işlem pipeline'ı
├── models.py                 # Veri modelleri (dataclass)
├── config.py                 # Uygulama konfigürasyonu
├── config_loader.py          # ⭐ Excel sütun mapping loader (PARAMETRIK!)
│
├── llm_service.py            # LLM API servisi
├── excel_manager.py          # Excel okuma/yazma (parametrik sütun desteği)
├── categorization.py         # Kategorizasyon modülü
├── field_extraction.py       # Alan çıkarma modülü
├── question_handler.py       # Soru yönetimi modülü
│
├── categories.xlsx           # Kategori/alan veritabanı
├── excel_config.json         # ⭐ Excel sütun mapping (opsiyonel)
│
├── .env                      # Environment variables (GİT'E EKLEMEYİN!)
├── .env.example              # Environment template
├── requirements.txt          # Python bağımlılıkları
└── README.md                 # Bu dosya
```

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Environment Dosyası Oluşturun

`.env.example` dosyasını `.env` olarak kopyalayın ve API key'inizi ekleyin:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
LLM_API_KEY=your-actual-api-key-here
```

### 3. API Ayarlarını Yapılandırın

`config.py` dosyasında LLM modelinizi ve endpoint'inizi ayarlayın:

```python
LLM_MODEL = "gpt-4"  # veya "gpt-3.5-turbo", "claude-3", vb.
LLM_BASE_URL = "https://api.openai.com/v1"  # veya kendi endpoint'iniz
```

### 4. Excel Dosyasını Hazırlayın (Opsiyonel)

İlk çalıştırmada sistem otomatik olarak örnek bir `categories.xlsx` dosyası oluşturacaktır.

Kendi kategorilerinizi eklemek için Excel dosyasını düzenleyin:

| kategori_adi | alan_adi | soru | alan_tipi | gerekli_mi | aciklama |
|--------------|----------|------|-----------|------------|----------|
| ATM | atm_lokasyonu | Problem yaşadığınız ATM lokasyonu nedir? | string | TRUE | ATM ile ilgili şikayetler |

## 🎮 Kullanım

### Streamlit Arayüzü ile Çalıştırma

```bash
streamlit run app.py
```

Tarayıcınızda otomatik olarak açılacak (genellikle http://localhost:8501)

### Programatik Kullanım

```python
from pipeline import ComplaintPipeline

# Pipeline oluştur
pipeline = ComplaintPipeline()

# Şikayet işle
complaint_text = "merhaba, atm de param sıkıştı"
state, response = pipeline.start_new_complaint(complaint_text)

print(response)  # İlk mesajı gösterir

# Kullanıcı cevaplarını işle
while not state.is_complete:
    user_answer = input("Cevabınız: ")
    state, response = pipeline.process_user_answer(state, user_answer)
    print(response)

# Final JSON
final_json = pipeline.get_final_json(state)
print(final_json)
```

## 📊 Excel Parametrik Yapı ⭐

Bu sistem, Excel sütun adlarını **tamamen parametrik** hale getirir. Kendi Excel formatınızı kullanabilirsiniz!

### Varsayılan Sütun Adları
```
kategori_adi | alan_adi | soru | alan_tipi | gerekli_mi | aciklama
```

### ⚙️ Özelleştirme Yöntemleri

#### **Yöntem 1: JSON Config Dosyası** (Önerilen)

1. Proje kök dizininde `excel_config.json` dosyası oluşturun:
```json
{
  "excel_columns": {
    "kategori_adi": "Category",
    "alan_adi": "Field_Name",
    "soru": "Question",
    "alan_tipi": "Type",
    "gerekli_mi": "Required",
    "aciklama": "Description"
  }
}
```

2. Excel dosyanızı bu sütun adlarıyla oluşturun

#### **Yöntem 2: Environment Variables**

`.env` dosyasına ekleyin:
```env
EXCEL_COL_CATEGORY=Category
EXCEL_COL_FIELD=Field_Name
EXCEL_COL_QUESTION=Question
EXCEL_COL_TYPE=Type
EXCEL_COL_REQUIRED=Required
EXCEL_COL_DESCRIPTION=Description
```

#### **Yöntem 3: Kod İçinde** (İleri Seviye)

`config_loader.py` dosyasındaki `ExcelColumnMapping` class'ını düzenleyin.

### 📋 Excel Şablon Örneği

| kategori_adi | alan_adi | soru | alan_tipi | gerekli_mi | aciklama |
|--------------|----------|------|-----------|------------|----------|
| ATM | atm_lokasyonu | Problem yaşadığınız ATM lokasyonu nedir? | string | TRUE | ATM ile ilgili şikayetler |
| ATM | atm_problemi | ATM'de sorun yaşadığınız durum nedir? | string | TRUE | |
| ATM | atm_para_miktari | ATM'de ne kadar paranız sıkıştı? | string | TRUE | |
| Kart | kart_turu | Hangi kart türünü kullanıyorsunuz? | string | TRUE | Kart ile ilgili şikayetler |
| Kart | kart_problemi | Kartınızla ilgili ne gibi bir sorun yaşıyorsunuz? | string | TRUE | |

## 🔧 Modüller

### 1. config.py
Tüm konfigürasyon ayarları (API keys, model seçimi, vb.)

### 2. config_loader.py ⭐ YENİ!
Excel sütun mapping'lerini yönetir:
- `ExcelColumnMapping`: Sütun adları dataclass
- `ConfigLoader`: JSON/env'den config okur
- **3 farklı özelleştirme yöntemi** destekler

### 3. models.py
Veri yapıları ve modeller:
- `CategoryField`: Kategori alanı
- `Category`: Kategori modeli
- `ExtractedData`: Çıkarılan veri
- `ConversationState`: Sohbet durumu (stateful!)
- `ChatMessage`: Chat mesajı

### 4. excel_manager.py (Geliştirildi ⭐)
- Excel dosyasından kategori bilgilerini okur
- **Parametrik sütun adları** desteği
- Otomatik örnek dosya oluşturma

### 5. llm_service.py
LLM API çağrılarını yönetir:
- OpenAI API formatı
- JSON response parsing
- Prompt yönetimi

### 6. categorization.py
Şikayet metnini kategorize eder (LLM kullanarak)

### 7. field_extraction.py
İki ana görev:
- İlk metinden tüm alanları çıkarma
- Kullanıcı cevaplarından spesifik değerleri çıkarma

### 8. question_handler.py
Soru-cevap döngüsü mantığı:
- Sıralı soru sorma
- Cevap kaydetme
- Tamamlanma kontrolü

### 9. pipeline.py
Tüm servisleri orkestre eden ana pipeline

### 10. app.py
Streamlit arayüzü (`st.session_state` ile stateful)

## 🎯 Akış Diyagramı

```
1. Kullanıcı şikayet metni girer
   ↓
2. Kategorizasyon Servisi → LLM ile kategori belirlenir
   ↓
3. Alan Çıkarma Servisi → Mevcut bilgiler çıkarılır
   ↓
4. Eksik alanlar belirlenir
   ↓
5. Her eksik alan için soru sorulur
   ↓
6. Kullanıcı cevaplar → LLM ile standartlaştırılır
   ↓
7. Tüm bilgiler toplandığında JSON oluşturulur
```

## 📝 JSON Çıktı Formatı

```json
{
  "sikayet_metni": "merhaba, atm de param sıkıştı",
  "kategori": "ATM",
  "atm_lokasyonu": "beykoz",
  "atm_problemi": "para sıkışması",
  "atm_para_miktari": "200 TL"
}
```

## 🛠️ Özelleştirme

### Yeni Kategori Eklemek

1. `categories.xlsx` dosyasını açın
2. Yeni kategori için satırlar ekleyin
3. Uygulamayı yeniden başlatın

### Farklı LLM Modeli Kullanmak

`config.py` dosyasında:

```python
# OpenAI için
LLM_MODEL = "gpt-4"
LLM_BASE_URL = "https://api.openai.com/v1"

# Anthropic Claude için
LLM_MODEL = "claude-3-sonnet"
LLM_BASE_URL = "https://api.anthropic.com/v1"

# Kendi modeliniz için
LLM_MODEL = "your-model"
LLM_BASE_URL = "https://your-endpoint.com/v1"
```

### Prompt'ları Güncellemek

Her servis dosyasında (`categorization.py`, `field_extraction.py`, vb.) `system_prompt` ve `prompt` değişkenlerini düzenleyin.

## 🐛 Sorun Giderme

### "Excel dosyası bulunamadı" hatası
→ İlk çalıştırmada otomatik oluşacaktır. Eğer oluşmazsa, Excel dosyasını manuel oluşturun.

### "LLM API hatası"
→ `.env` dosyasındaki API key'i kontrol edin
→ `config.py` dosyasındaki endpoint URL'ini kontrol edin
→ API limitlerini kontrol edin

### Kategori bulunamıyor
→ `categories.xlsx` dosyasının doğru formatta olduğundan emin olun
→ Kategori adlarında Türkçe karakter kullanmaktan çekinmeyin

## 📈 Geliştirme Önerileri

- [ ] Veritabanı entegrasyonu (SQLite, PostgreSQL)
- [ ] Kullanıcı kimlik doğrulama
- [ ] Şikayet geçmişi görüntüleme
- [ ] Dashboard ve analytics
- [ ] E-posta bildirimleri
- [ ] Multi-language desteği
- [ ] Webhook entegrasyonları
- [ ] A/B testing için farklı prompt versiyonları

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Sorularınız için issue açabilirsiniz.

---

**Yapımcı:** AI Powered Complaint Management System
**Versiyon:** 1.0.0
**Son Güncelleme:** 2025
