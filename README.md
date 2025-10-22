# 💬 Şikayet Yönetim Sistemi

LLM tabanlı akıllı şikayet yönetim ve kategorizasyon sistemi.

## 🎯 Özellikler

- ✅ Otomatik şikayet kategorizasyonu
- ✅ Akıllı alan çıkarma (NLP ile)
- ✅ Dinamik soru-cevap akışı
- ✅ Excel tabanlı kategori yönetimi
- ✅ JSON formatında çıktı
- ✅ Streamlit ile kullanıcı dostu arayüz
- ✅ Modüler ve genişletilebilir mimari

## 📁 Proje Yapısı

```
complaint-chatbot/
├── app.py                    # Streamlit arayüzü
├── pipeline.py               # Ana işlem pipeline'ı
├── config.py                 # Konfigürasyon dosyası
├── models.py                 # Veri modelleri
├── excel_manager.py          # Excel okuma/yazma
├── llm_service.py           # LLM API servisi
├── categorization.py         # Kategorizasyon servisi
├── field_extraction.py       # Alan çıkarma servisi
├── question_handler.py       # Soru yönetimi
├── requirements.txt          # Python bağımlılıkları
├── .env.example             # Örnek environment dosyası
├── categories.xlsx          # Kategori tanımları (otomatik oluşur)
└── README.md                # Bu dosya
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

## 📊 Excel Formatı

### Gerekli Sütunlar

1. **kategori_adi**: Kategori adı (örn: ATM, Kart, Hesap)
2. **alan_adi**: Çıkarılacak alan adı (örn: atm_lokasyonu)
3. **soru**: Kullanıcıya sorulacak soru
4. **alan_tipi**: Alan tipi (string, number, date, vb.)
5. **gerekli_mi**: Bu alan zorunlu mu? (TRUE/FALSE)
6. **aciklama**: Kategori açıklaması (opsiyonel)

### Örnek Satırlar

```
ATM, atm_lokasyonu, Problem yaşadığınız ATM lokasyonu nedir?, string, TRUE, ATM ile ilgili şikayetler
ATM, atm_problemi, ATM de sorun yaşadığınız durum nedir?, string, TRUE, 
ATM, atm_para_miktari, ATM de ne kadar paranız sıkıştı?, string, TRUE,
```

## 🔧 Modüller

### 1. config.py
Tüm konfigürasyon ayarları (API keys, model seçimi, vb.)

### 2. models.py
Veri yapıları ve modeller:
- `CategoryField`: Kategori alanı
- `Category`: Kategori modeli
- `ExtractedData`: Çıkarılan veri
- `ConversationState`: Sohbet durumu
- `ChatMessage`: Chat mesajı

### 3. excel_manager.py
Excel dosyasından kategori bilgilerini okur ve yönetir.

### 4. llm_service.py
LLM API çağrılarını yönetir. Prompt'ları gönderir ve yanıtları parse eder.

### 5. categorization.py
Şikayet metnini kategorize eder.

### 6. field_extraction.py
Şikayet metninden alan bilgilerini çıkarır ve eksik alanları belirler.

### 7. question_handler.py
Kullanıcıya soru sorma ve cevap işleme mantığı.

### 8. pipeline.py
Tüm servisleri birleştiren ana pipeline.

### 9. app.py
Streamlit arayüzü.

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
