# 🤖 Stateful Complaint Chatbot

Modern LLM yetenekleri ile klasik "Slot Filling" (Alan Doldurma) görevini birleştiren, duruma dayalı (stateful) bir şikayet toplama sistemi.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Mimari](#-mimari)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Konfigürasyon](#-konfigürasyon)
- [Modül Açıklamaları](#-modül-açıklamaları)
- [Örnek Akış](#-örnek-akış)

## ✨ Özellikler

- **LLM Tabanlı Kategorizasyon**: Kullanıcı şikayetlerini otomatik olarak kategorize eder
- **Akıllı Veri Çıkarımı**: Yapılandırılmamış metinden yapılandırılmış veri çıkarır
- **Çok Adımlı Diyalog**: Eksik bilgileri proaktif olarak sorar
- **Parametrik Konfigürasyon**: Excel tabanlı, kolayca güncellenebilir kategori/soru yapısı
- **Session Yönetimi**: Streamlit session_state ile stateful konuşma takibi
- **Excel Loglama**: Tüm etkileşimleri otomatik olarak loglar
- **Gemini API Entegrasyonu**: Google'ın Gemini 3-27b modeli ile çalışır

## 🏗️ Mimari

Sistem 3 ana bileşenden oluşur:

### 1. **Streamlit Arayüzü** (`app.py`)
- Kullanıcı etkileşimi ve UI
- İş akışı (pipeline) yönetimi
- Session state ile durum takibi

### 2. **Bilgi Bankası** (`config_manager.py`)
- Excel'den kategori ve soru tanımları
- Parametrik yapılandırma
- Dinamik alan yönetimi

### 3. **LLM İşleyicisi** (`llm_handler.py`)
İki temel görev:
- **Görev 1**: Kategorizasyon ve ilk veri çıkarımı
- **Görev 2**: Spesifik veri çıkarımı (takip sorularından)

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
cd stateful_complaint_chatbot
pip install -r requirements.txt
```

### 2. Environment Variables Ayarlayın

`.env` dosyası oluşturun:

```bash
# Gemini API Key (zorunlu)
GEMINI_API_KEY=your_gemini_api_key_here

# Model ayarları (opsiyonel, varsayılanlar aşağıda)
MODEL_NAME=gemini-3-27b

# Config dosyası ayarları (opsiyonel)
CONFIG_FILE=config_template.xlsx

# Excel sütun adları (opsiyonel, varsayılanlar aşağıda)
COL_CATEGORY=Kategori
COL_FIELD=Alan
COL_QUESTION=Soru
COL_REQUIRED=Zorunlu

# Log dosyası (opsiyonel)
LOG_FILE=logs.xlsx
```

### 3. Config Template Oluşturun

```bash
python create_config_template.py
```

Bu komut `config_template.xlsx` dosyasını oluşturur. Örnek kategoriler:
- ATM_SORUNU
- KART_SORUNU
- HESAP_SORUNU
- MOBIL_UYGULAMA_SORUNU
- HAVALE_EFT_SORUNU

### 4. Uygulamayı Çalıştırın

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresinde uygulama açılacaktır.

## 📖 Kullanım

### Temel Akış

1. **İlk Şikayet**: Kullanıcı şikayetini serbest metin olarak girer
   ```
   Örnek: "Merhaba, ATM'de param sıkıştı"
   ```

2. **Otomatik Kategorizasyon**: LLM şikayeti kategorize eder
   ```
   Kategori: ATM_SORUNU
   ```

3. **İlk Veri Çıkarımı**: LLM ilk metinden mevcut bilgileri çıkarır
   ```json
   {
     "atm_lokasyonu": null,
     "atm_problemi": "para sıkışması",
     "atm_para_islem_miktari": null,
     "atm_tarih_saat": null
   }
   ```

4. **Takip Soruları**: Sistem null olan alanlar için sırayla soru sorar
   ```
   Soru 1: Problem yaşadığınız ATM'nin lokasyonu nedir?
   Cevap: "sanırım beykoz taraflarıydı"
   → Çıkarılan: "Beykoz"
   ```

5. **Finalizasyon**: Tüm veriler toplandıktan sonra LLM son bir kez kontrol eder ve rafine eder

6. **Loglama**: Oturum otomatik olarak `logs.xlsx` dosyasına kaydedilir

### Örnek Kullanım Senaryosu

```
👤 Kullanıcı: "Kredi kartımdan hatalı çekim yapıldı galiba"

🤖 Sistem:
  ✅ Kategori: KART_SORUNU
  📊 Tespit edilen bilgiler:
    - kart_tipi: "kredi kartı"
    - kart_problemi: "hatalı çekim"

  ❓ Soru 1/2: Kartınızın son 4 hanesi nedir?

👤 Kullanıcı: "1234"

🤖 Sistem:
  ❓ Soru 2/2: Kartı nerede kullanmaya çalıştınız?

👤 Kullanıcı: "Online bir sitede"

🤖 Sistem:
  🎉 Şikayetiniz başarıyla kaydedildi!

  Final Veriler:
  {
    "kart_tipi": "kredi kartı",
    "kart_problemi": "hatalı çekim",
    "kart_son_dort_hane": "1234",
    "kart_kullanim_yeri": "online"
  }
```

## ⚙️ Konfigürasyon

### Excel Yapısı

`config_template.xlsx` dosyası şu sütunları içerir:

| Kategori | Alan | Soru | Zorunlu |
|----------|------|------|---------|
| ATM_SORUNU | atm_lokasyonu | Problem yaşadığınız ATM'nin lokasyonu nedir? | Evet |
| ATM_SORUNU | atm_problemi | ATM'de yaşadığınız sorun nedir? | Evet |
| ATM_SORUNU | atm_para_islem_miktari | İşlem yapmaya çalıştığınız tutar nedir? | Hayır |

### Özel Sütun Adları

Farklı sütun adları kullanmak isterseniz `.env` dosyasında belirtin:

```bash
COL_CATEGORY=Şikayet Kategorisi
COL_FIELD=Veri Alanı
COL_QUESTION=Kullanıcıya Sorulacak Soru
COL_REQUIRED=Zorunlu Alan mı?
```

### Yeni Kategori Eklemek

1. `config_template.xlsx` dosyasını açın
2. Yeni satırlar ekleyin:

```
Kategori: INTERNET_BANKACILIGI
Alan: internet_problemi
Soru: İnternet bankacılığında yaşadığınız sorun nedir?
Zorunlu: Evet
```

3. Dosyayı kaydedin
4. Uygulamayı yeniden başlatın (config otomatik yüklenir)

## 📦 Modül Açıklamaları

### `config_manager.py`
Excel'den konfigürasyon okuma ve yönetimi.

**Temel Metodlar:**
- `get_categories()`: Tüm kategorileri listeler
- `get_category_config(category)`: Belirli bir kategorinin yapısını döndürür
- `get_question_for_field(category, field)`: Belirli bir alan için soruyu getirir
- `reload_config()`: Konfigürasyonu yeniden yükler

### `llm_handler.py`
Gemini API ile LLM etkileşimi.

**Temel Metodlar:**
- `categorize_and_extract(complaint_text, categories)`: İlk şikayeti kategorize et ve veri çıkar
- `extract_field_value(user_answer, field_name, question)`: Kullanıcı cevabından temiz veri çıkar
- `validate_and_refine_data(complaint_data, original_text)`: Final verileri doğrula ve rafine et

### `logger.py`
Excel tabanlı oturum loglama.

**Temel Metodlar:**
- `log_session(session_id, category, initial_complaint, qa_list, final_data)`: Tam oturumu logla
- `get_statistics()`: Genel istatistikler
- `export_to_csv(output_path)`: Logları CSV'ye aktar

### `utils.py`
Yardımcı fonksiyonlar.

**Temel Fonksiyonlar:**
- `generate_session_id()`: Benzersiz oturum ID'si
- `find_null_fields(data)`: None olan alanları bul
- `format_data_for_display(data)`: Veriyi UI için formatla
- `calculate_completion_percentage(data)`: Tamamlanma yüzdesi

### `app.py`
Streamlit ana uygulama.

**Temel Fonksiyonlar:**
- `initialize_session_state()`: Session state'i başlat
- `handle_initial_complaint(text)`: İlk şikayeti işle
- `handle_follow_up_answer(answer)`: Takip sorusuna cevabı işle
- `finalize_complaint()`: Şikayeti finalize et ve logla

## 🔄 Örnek Akış

### Pipeline Diyagramı

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BAŞLANGIÇ (initial_complaint aşaması)                    │
│                                                              │
│ Kullanıcı: "ATM'de param sıkıştı"                           │
│      ↓                                                       │
│ LLM (Görev 1): Kategorize et + İlk veri çıkar              │
│      ↓                                                       │
│ Kategori: ATM_SORUNU                                        │
│ Veriler: {                                                   │
│   "atm_lokasyonu": null,                                    │
│   "atm_problemi": "para sıkışması",                         │
│   "atm_para_islem_miktari": null                            │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TAKİP SORULARI (follow_up aşaması)                       │
│                                                              │
│ Null alanlar tespit edilir: [atm_lokasyonu, ...]           │
│      ↓                                                       │
│ Soru 1: "Problem yaşadığınız ATM lokasyonu nedir?"         │
│ Kullanıcı: "sanırım beykoz taraflarıydı"                   │
│      ↓                                                       │
│ LLM (Görev 2): Veriyi çıkar                                │
│      ↓                                                       │
│ Çıkarılan: "Beykoz"                                         │
│ → atm_lokasyonu güncellenir                                 │
│                                                              │
│ (Tüm null alanlar dolana kadar devam eder)                 │
└─────────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. FİNALİZASYON (completed aşaması)                         │
│                                                              │
│ LLM: Tüm verileri kontrol et ve rafine et                   │
│      ↓                                                       │
│ Final Veriler: {                                             │
│   "atm_lokasyonu": "Beykoz",                                │
│   "atm_problemi": "para sıkışması",                         │
│   "atm_para_islem_miktari": "200 TL"                        │
│ }                                                            │
│      ↓                                                       │
│ Logger: Oturumu logs.xlsx'e kaydet                          │
│      ↓                                                       │
│ 🎉 TAMAMLANDI                                                │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Loglama

Her oturum `logs.xlsx` dosyasına kaydedilir:

| Sütun | Açıklama |
|-------|----------|
| oturum_id | Benzersiz oturum ID'si |
| zaman_damgasi | Oturum zamanı |
| kategori | Tespit edilen kategori |
| ilk_sikayet_metni | Kullanıcının ilk mesajı |
| soru_cevap_listesi | Tüm soru-cevap geçmişi (JSON) |
| final_veriler | Toplanan final veriler (JSON) |
| tamamlanma_durumu | Tamamlandı/Yarım Kaldı |
| toplam_sure_saniye | Oturum süresi |

### İstatistikler

Uygulamadan "İstatistikleri Göster" butonuna tıklayarak:
- Toplam oturum sayısı
- Tamamlanan oturum sayısı
- Kategori dağılımı
- Ortalama süre

## 🐛 Hata Ayıklama

### Yaygın Sorunlar

**1. "GEMINI_API_KEY tanımlı değil"**
```bash
# .env dosyasına ekleyin
GEMINI_API_KEY=your_key_here
```

**2. "Config dosyası bulunamadı"**
```bash
# Config template oluşturun
python create_config_template.py
```

**3. "Modül bulunamadı"**
```bash
# Gereksinimleri yükleyin
pip install -r requirements.txt
```

**4. "LLM geçersiz kategori döndürdü"**
- Config dosyasındaki kategori adlarının Excel'de doğru yazıldığından emin olun
- LLM promptlarını güncelleyebilirsiniz (`llm_handler.py`)

## 🔧 Özelleştirme

### Prompt Güncelleme

`llm_handler.py` dosyasındaki promptları düzenleyebilirsiniz:
- `categorize_and_extract()`: Kategorizasyon promptu
- `extract_field_value()`: Veri çıkarım promptu
- `validate_and_refine_data()`: Validasyon promptu

### UI Özelleştirme

`app.py` dosyasında:
- CSS stilleri (`st.markdown()` bloğu)
- Mesaj formatları
- Renkler ve emojiler (`utils.UIConstants`)

### Farklı LLM Kullanımı

`llm_handler.py` dosyasını düzenleyerek farklı LLM API'leri kullanabilirsiniz:
- OpenAI GPT
- Anthropic Claude
- Cohere
- vb.

## 📝 Lisans

Bu proje MIT lisansı altındadır.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

**Geliştiren**: LLM-Powered Chatbot Team
**Versiyon**: 1.0.0
**Son Güncelleme**: 2024
