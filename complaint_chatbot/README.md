# 🤖 Complaint Chatbot - Şikayet Toplama Chatbot

LLM tabanlı akıllı şikayet toplama ve kategorize sistemi. Kullanıcıların şikayetlerini otomatik olarak kategorize eder, eksik bilgileri soru-cevap yöntemiyle tamamlar ve yapılandırılmış JSON formatında çıktı üretir.

## ✨ Özellikler

- **Otomatik Kategorize**: LLM ile şikayetleri otomatik kategorize eder
- **Akıllı Bilgi Çıkarma**: Şikayet metninden ilgili bilgileri çıkarır
- **Etkileşimli Soru-Cevap**: Eksik bilgiler için kullanıcıya sorular sorar
- **Çoklu LLM Desteği**: OpenAI, Anthropic, Google Gemini desteği
- **Streamlit Arayüzü**: Kullanıcı dostu web arayüzü
- **Excel Tabanlı Yapılandırma**: Kategoriler ve sorular Excel'den yönetilir
- **JSON Çıktı**: Yapılandırılmış veri formatı

## 📁 Proje Yapısı

```
complaint_chatbot/
├── data/
│   ├── create_template.py          # Excel template oluşturucu
│   └── categories_template.xlsx    # Kategori, alan ve soru tanımları
├── modules/
│   ├── __init__.py
│   ├── llm_client.py              # LLM API client
│   ├── data_manager.py            # Excel veri yöneticisi
│   ├── categorizer.py             # Şikayet kategorize modülü
│   ├── information_extractor.py   # Bilgi çıkarma modülü
│   └── response_processor.py      # Cevap işleme modülü
├── prompts/
│   ├── categorizer_prompt.py      # Kategorize promptları
│   ├── extractor_prompt.py        # Bilgi çıkarma promptları
│   └── response_prompt.py         # Cevap işleme promptları
├── config.py                      # Yapılandırma ayarları
├── chatbot_pipeline.py            # Ana pipeline
├── streamlit_app.py               # Streamlit arayüzü
├── requirements.txt               # Python bağımlılıkları
├── .env.example                   # Örnek environment dosyası
└── README.md                      # Bu dosya
```

## 🚀 Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Environment Dosyasını Yapılandırın

```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin ve API key'lerinizi ekleyin
nano .env
```

`.env` dosyası örneği:

```env
# LLM Provider seçimi (openai, anthropic, google)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2000

# API Keys
OPENAI_API_KEY=sk-xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...
GOOGLE_API_KEY=xxx...

# Diğer ayarlar
EXCEL_PATH=complaint_chatbot/data/categories_template.xlsx
DEBUG_MODE=False
```

### 3. Excel Template Oluşturun

```bash
cd data
python create_template.py
```

Bu komut `categories_template.xlsx` dosyasını oluşturur. Bu dosyada:
- Kategoriler (ATM, Kredi Kartı, Banka Hesabı, vb.)
- Her kategori için alanlar
- Her alan için sorular

tanımlıdır.

## 📊 Excel Dosyası Formatı

Excel dosyası şu sütunları içermelidir:

| kategori | alan_adi | alan_aciklamasi | soru |
|----------|----------|-----------------|------|
| ATM | atm_lokasyonu | ATM lokasyonu | Problem yaşadığınız ATM lokasyonu nedir? |
| ATM | atm_problemi | Problem türü | ATM'de yaşadığınız sorun nedir? |
| ATM | atm_para_islem_miktari | Para miktarı | Ne kadar paranız sıkıştı? |

## 🎯 Kullanım

### Streamlit Uygulaması (Önerilen)

```bash
cd complaint_chatbot
streamlit run streamlit_app.py
```

Tarayıcınızda `http://localhost:8501` adresini açın.

### Komut Satırı Kullanımı

```python
from chatbot_pipeline import ConversationalChatbot

# Chatbot oluştur
chatbot = ConversationalChatbot()

# İlk şikayet
response = chatbot.chat("ATM'den param sıkıştı")
print(response)
# Output: "Şikayetiniz alındı. Kategori: ATM\n\nProblem yaşadığınız ATM lokasyonu nedir?"

# Cevap ver
response = chatbot.chat("Beykoz'daki ATM")
print(response)
# Output: "ATM'de ne kadar paranız sıkıştı?"

# Son cevap
response = chatbot.chat("200 TL")
print(response)
# Output: "Tüm bilgiler alındı. Teşekkür ederiz!"

# Final veriyi al
final_data = chatbot.get_final_data()
print(final_data)
```

### Programatik Kullanım (Pipeline)

```python
from chatbot_pipeline import ComplaintChatbot

# Chatbot oluştur
chatbot = ComplaintChatbot()

# Oturum başlat
result = chatbot.start_session("Kredi kartımla işlem yapamıyorum")

print(f"Kategori: {result['kategori']}")
print(f"Eksik alanlar: {result['missing_fields']}")
print(f"İlk soru: {result['next_question']['question']}")

# Cevap işle
result = chatbot.process_answer("Visa kartım")
print(f"Sonraki soru: {result['next_question']['question']}")

# Final veri
final_data = chatbot.get_final_data()
```

## 🔧 Yapılandırma

### LLM Provider Değiştirme

`.env` dosyasında:

```env
# OpenAI için
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# Anthropic (Claude) için
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229

# Google Gemini için
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
```

### Prompt Güncelleme

Promptları güncellemek için `prompts/` dizinindeki dosyaları düzenleyin:

- `categorizer_prompt.py`: Kategorize işlemi için promptlar
- `extractor_prompt.py`: Bilgi çıkarma için promptlar
- `response_prompt.py`: Cevap işleme için promptlar

### Yeni Kategori Ekleme

Excel dosyasını düzenleyerek yeni kategoriler ekleyebilirsiniz:

1. `data/categories_template.xlsx` dosyasını açın
2. Yeni kategori için satırlar ekleyin
3. Uygulamayı yeniden başlatın (Excel otomatik yüklenir)

## 📝 Workflow Akışı

```
1. Kullanıcı şikayeti yazar
   ↓
2. LLM şikayeti kategorize eder
   ↓
3. Şikayetten bilgiler çıkarılır
   ↓
4. Eksik alanlar tespit edilir
   ↓
5. Her eksik alan için soru sorulur
   ↓
6. Kullanıcı cevapları normalize edilir
   ↓
7. JSON formatında final veri üretilir
```

## 🔍 Modül Açıklamaları

### LLMClient
- Çoklu LLM provider desteği
- Birleşik API arayüzü
- JSON mode desteği

### DataManager
- Excel verilerini yükler ve cache'ler
- Kategori ve soru yönetimi
- Schema oluşturma

### Categorizer
- Şikayetleri otomatik kategorize eder
- Güven skoru hesaplar
- Fallback mekanizması

### InformationExtractor
- Şikayetten bilgi çıkarır
- Eksik alanları tespit eder
- Veri validasyonu

### ResponseProcessor
- Kullanıcı cevaplarını normalize eder
- Metin temizleme
- Para birimi, tarih çıkarma

### ChatbotPipeline
- Tüm modülleri koordine eder
- Oturum yönetimi
- Conversation flow

## 🎨 Streamlit Arayüzü Özellikleri

- **Chat Interface**: Mesaj tabanlı etkileşim
- **Real-time Status**: Anlık durum gösterimi
- **Progress Tracking**: İlerleme takibi
- **JSON Export**: Veri indirme
- **Debug Mode**: Geliştirici modu
- **Sidebar Info**: Kategori ve config bilgileri

## 🧪 Test Etme

```python
# Modül testleri
python modules/llm_client.py
python modules/data_manager.py
python modules/categorizer.py
python modules/information_extractor.py
python modules/response_processor.py

# Pipeline testi
python chatbot_pipeline.py
```

## 📊 Örnek Çıktı

```json
{
  "sikayet_metni": "Merhaba, ATM'den param sıkıştı",
  "atm_lokasyonu": "Beykoz",
  "atm_problemi": "Para sıkışması",
  "atm_para_islem_miktari": "200 TL",
  "tarih_saat": "2024-01-20 14:30"
}
```

## 🛠️ Geliştirme

### Kod Formatı

```bash
# Black ile formatlama
black complaint_chatbot/

# Flake8 ile lint
flake8 complaint_chatbot/
```

### Debug Mode

`.env` dosyasında:

```env
DEBUG_MODE=True
```

Bu mod:
- Detaylı hata mesajları
- LLM yanıtlarını gösterir
- Cache bilgileri gösterir

## 🤝 Katkıda Bulunma

1. Yeni kategoriler ekleyin
2. Promptları iyileştirin
3. Yeni modüller ekleyin
4. Bug düzeltmeleri yapın

## 📄 Lisans

Bu proje MIT lisansı altındadır.

## 🆘 Sorun Giderme

### "Module not found" hatası

```bash
# Path'i kontrol edin
export PYTHONPATH="${PYTHONPATH}:/home/user/mycoderepository_LLM/complaint_chatbot"
```

### "API key not found" hatası

`.env` dosyasını kontrol edin ve doğru API key'i ekleyin.

### "Excel file not found" hatası

```bash
cd data
python create_template.py
```

### LLM yanıt vermiyor

- API key'inizi kontrol edin
- İnternet bağlantınızı kontrol edin
- Rate limit'e takılmış olabilirsiniz

## 📞 İletişim

Sorularınız için GitHub issue açabilirsiniz.

## 🎉 Başarılı Kullanımlar!

Projeyi geliştirirken keyif alın!
