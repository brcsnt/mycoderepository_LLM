# 📁 Proje Yapısı

```
complaint_chatbot/
│
├── 📄 README.md                      # Ana dokümantasyon
├── 📄 SETUP_GUIDE.md                 # Detaylı kurulum rehberi
├── 📄 PROJECT_STRUCTURE.md           # Bu dosya
├── 📄 requirements.txt               # Python bağımlılıkları
├── 📄 .env.example                   # Örnek environment dosyası
├── 📄 __init__.py                    # Package init
│
├── 🔧 config.py                      # Yapılandırma yönetimi
├── 🤖 chatbot_pipeline.py            # Ana pipeline sınıfları
├── 🖥️  streamlit_app.py              # Streamlit web arayüzü
├── 🚀 quick_start.py                 # Hızlı başlangıç scripti
│
├── 📊 data/                          # Veri klasörü
│   ├── create_template.py           # Excel template oluşturucu
│   └── categories_template.xlsx     # Kategori tanımları (oluşturulacak)
│
├── 🧩 modules/                       # Ana modüller
│   ├── __init__.py
│   ├── llm_client.py                # LLM API wrapper
│   ├── data_manager.py              # Excel veri yöneticisi
│   ├── categorizer.py               # Şikayet kategorize modülü
│   ├── information_extractor.py     # Bilgi çıkarma modülü
│   └── response_processor.py        # Cevap işleme modülü
│
└── 📝 prompts/                       # Prompt şablonları
    ├── __init__.py
    ├── categorizer_prompt.py        # Kategorize promptları
    ├── extractor_prompt.py          # Bilgi çıkarma promptları
    └── response_prompt.py           # Cevap işleme promptları
```

## 📂 Klasör ve Dosya Açıklamaları

### Kök Dizin Dosyaları

| Dosya | Açıklama | Öncelik |
|-------|----------|---------|
| `README.md` | Proje dokümantasyonu | ⭐⭐⭐ |
| `SETUP_GUIDE.md` | Adım adım kurulum | ⭐⭐⭐ |
| `requirements.txt` | Python dependencies | ⭐⭐⭐ |
| `.env.example` | Environment template | ⭐⭐⭐ |
| `config.py` | Yapılandırma ayarları | ⭐⭐⭐ |
| `chatbot_pipeline.py` | Ana pipeline | ⭐⭐⭐ |
| `streamlit_app.py` | Web arayüzü | ⭐⭐ |
| `quick_start.py` | Test ve demo scripti | ⭐⭐ |

### data/ Klasörü

**Amaç:** Kategori ve soru tanımlarının saklandığı yer

| Dosya | Açıklama |
|-------|----------|
| `create_template.py` | Excel dosyası oluşturucu |
| `categories_template.xlsx` | Kategori tanımları (script ile oluşturulur) |

**Kullanım:**
```bash
cd data
python create_template.py
```

### modules/ Klasörü

**Amaç:** Ana iş mantığı modülleri

| Modül | Sorumluluk | Input | Output |
|-------|-----------|-------|--------|
| `llm_client.py` | LLM API çağrıları | Prompt | LLM yanıtı |
| `data_manager.py` | Excel veri yönetimi | Excel path | Kategori verileri |
| `categorizer.py` | Şikayet kategorize | Şikayet metni | Kategori |
| `information_extractor.py` | Bilgi çıkarma | Şikayet + kategori | JSON data |
| `response_processor.py` | Cevap işleme | Kullanıcı yanıtı | Normalize değer |

### prompts/ Klasörü

**Amaç:** LLM promptlarının merkezi yönetimi

| Dosya | İçerik |
|-------|--------|
| `categorizer_prompt.py` | Kategorize için sistem ve user promptları |
| `extractor_prompt.py` | Bilgi çıkarma için promptlar |
| `response_prompt.py` | Cevap normalize etme promptları |

**Avantajlar:**
- Merkezi prompt yönetimi
- Kolay güncelleme
- Versiyon kontrolü
- A/B testing için uygun

## 🔄 Veri Akışı

```
1. Kullanıcı → Şikayet Metni
   ↓
2. Categorizer → Kategori Belirleme
   ↓
3. Data Manager → Kategori Alanlarını Getir
   ↓
4. Information Extractor → Bilgi Çıkarma
   ↓
5. Missing Fields → Eksik Alanları Tespit
   ↓
6. Loop: Her eksik alan için
   - Data Manager → Soruyu Getir
   - Kullanıcı → Cevap
   - Response Processor → Normalize
   - Information Extractor → Güncelle
   ↓
7. Final JSON → Yapılandırılmış Veri
```

## 🧩 Modül Bağımlılıkları

```
streamlit_app.py
└── chatbot_pipeline.py
    ├── modules/categorizer.py
    │   ├── modules/llm_client.py
    │   ├── modules/data_manager.py
    │   └── prompts/categorizer_prompt.py
    │
    ├── modules/information_extractor.py
    │   ├── modules/llm_client.py
    │   ├── modules/data_manager.py
    │   └── prompts/extractor_prompt.py
    │
    └── modules/response_processor.py
        ├── modules/llm_client.py
        └── prompts/response_prompt.py
```

## 📊 Dosya Boyutları (yaklaşık)

| Dosya | Satır | Boyut |
|-------|-------|-------|
| `chatbot_pipeline.py` | ~350 | 12 KB |
| `streamlit_app.py` | ~280 | 10 KB |
| `llm_client.py` | ~200 | 7 KB |
| `information_extractor.py` | ~220 | 8 KB |
| `categorizer.py` | ~180 | 6 KB |
| `data_manager.py` | ~160 | 5 KB |
| `response_processor.py` | ~180 | 6 KB |
| **TOPLAM** | **~1600** | **~55 KB** |

## 🎯 Hangi Dosyayı Ne Zaman Düzenlersiniz?

### Yeni Kategori Eklemek
→ `data/categories_template.xlsx`

### Promptları İyileştirmek
→ `prompts/categorizer_prompt.py`
→ `prompts/extractor_prompt.py`
→ `prompts/response_prompt.py`

### LLM Provider Değiştirmek
→ `.env` (LLM_PROVIDER değişkeni)

### Yeni Model Eklemek
→ `modules/llm_client.py` (_initialize_client metoduna ekleyin)

### UI Değişiklikleri
→ `streamlit_app.py`

### Pipeline Mantığı Değişiklikleri
→ `chatbot_pipeline.py`

### Yeni Alan Tipi Eklemek
→ `modules/response_processor.py` (özel işleme için)

## 🔐 Güvenlik

**Hassas Dosyalar (commit edilmemeli):**
- `.env` - API keys
- `data/categories_template.xlsx` - İş verisi (opsiyonel)
- `*.pyc`, `__pycache__/` - Python cache

**Güvenli Dosyalar (commit edilebilir):**
- `.env.example` - Template
- `*.py` - Kaynak kod
- `*.md` - Dokümantasyon
- `requirements.txt` - Dependencies

## 📈 Gelecek Geliştirmeler İçin Öneriler

1. **tests/** klasörü ekleyin
   - Unit testler
   - Integration testler
   - Test fixtures

2. **logs/** klasörü ekleyin
   - Uygulama logları
   - Hata logları
   - Kullanıcı aktivite logları

3. **exports/** klasörü ekleyin
   - JSON export'ları
   - CSV export'ları
   - Raporlar

4. **docker/** klasörü ekleyin
   - Dockerfile
   - docker-compose.yml
   - Deployment scripts

## 🎓 Öğrenme Yolu

**Yeni geliştiriciler için önerilen okuma sırası:**

1. `README.md` - Genel bakış
2. `SETUP_GUIDE.md` - Kurulum
3. `config.py` - Yapılandırma
4. `modules/llm_client.py` - LLM temelleri
5. `modules/data_manager.py` - Veri yönetimi
6. `prompts/` - Prompt mühendisliği
7. `chatbot_pipeline.py` - Ana mantık
8. `streamlit_app.py` - UI implementasyonu

## 🤝 Katkıda Bulunma

Yeni dosya eklerken:
- Uygun klasöre koyun
- Docstring ekleyin
- Type hints kullanın
- README'yi güncelleyin
- Bu dosyayı güncelleyin

## 📞 İletişim

Proje hakkında sorularınız için:
- GitHub Issues
- Documentation
- Code comments
