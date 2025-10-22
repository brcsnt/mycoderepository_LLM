# 🚀 Kurulum Rehberi

Bu rehber adım adım kurulum talimatlarını içerir.

## Adım 1: Gerekli Paketleri Yükleyin

```bash
cd complaint_chatbot
pip install -r requirements.txt
```

## Adım 2: Environment Dosyasını Yapılandırın

```bash
# .env.example'ı kopyalayın
cp .env.example .env

# .env dosyasını bir editörle açın
nano .env  # veya vim, code, vb.
```

### API Key Alma Talimatları

#### OpenAI
1. https://platform.openai.com/api-keys adresine gidin
2. "Create new secret key" butonuna tıklayın
3. Key'i kopyalayın ve `.env` dosyasına yapıştırın

```env
OPENAI_API_KEY=sk-proj-xxx...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

#### Anthropic (Claude)
1. https://console.anthropic.com/settings/keys adresine gidin
2. "Create Key" butonuna tıklayın
3. Key'i kopyalayın

```env
ANTHROPIC_API_KEY=sk-ant-xxx...
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
```

#### Google (Gemini)
1. https://makersuite.google.com/app/apikey adresine gidin
2. "Get API Key" butonuna tıklayın
3. Key'i kopyalayın

```env
GOOGLE_API_KEY=xxx...
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
```

## Adım 3: Excel Template Oluşturun

```bash
cd data
python create_template.py
```

Bu komut `categories_template.xlsx` dosyasını oluşturur.

**Çıktı:**
```
✓ Excel template oluşturuldu: categories_template.xlsx
✓ Toplam 5 kategori
✓ Toplam 20 alan tanımı

Kategoriler:
  - ATM: 4 alan
  - Kredi Kartı: 4 alan
  - Banka Hesabı: 4 alan
  - Müşteri Hizmetleri: 4 alan
  - EFT/Havale: 4 alan
```

## Adım 4: Kurulumu Test Edin

```bash
cd ..
python quick_start.py
```

Menüden "1. Kurulum Kontrolü" seçeneğini seçin.

**Başarılı çıktı:**
```
🔍 Kurulum Kontrolü
============================================================
✓ Config doğrulandı
✓ LLM client başlatıldı
✓ Data manager başlatıldı (5 kategori)

✅ Tüm kontroller başarılı!
```

## Adım 5: Demo Çalıştırın

```bash
python quick_start.py
```

Menüden "2. Demo Çalıştır" seçeneğini seçin.

## Adım 6: Streamlit Uygulamasını Başlatın

```bash
streamlit run streamlit_app.py
```

Tarayıcınızda `http://localhost:8501` adresini açın.

## 🔧 Excel Dosyasını Özelleştirme

1. `data/categories_template.xlsx` dosyasını Excel ile açın
2. Yeni satırlar ekleyin veya mevcut satırları düzenleyin
3. Dosyayı kaydedin
4. Uygulamayı yeniden başlatın

### Excel Sütunları

- **kategori**: Kategori adı (ATM, Kredi Kartı, vb.)
- **alan_adi**: Alan adı (snake_case formatında)
- **alan_aciklamasi**: Alan hakkında açıklama
- **soru**: Kullanıcıya sorulacak soru

### Örnek Satır

| kategori | alan_adi | alan_aciklamasi | soru |
|----------|----------|-----------------|------|
| ATM | atm_lokasyonu | ATM'nin bulunduğu lokasyon | Problem yaşadığınız ATM lokasyonu nedir? |

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install -r requirements.txt
```

### "FileNotFoundError: Excel dosyası bulunamadı"

```bash
cd data
python create_template.py
```

### "ValueError: API key bulunamadı"

`.env` dosyasını kontrol edin:

```bash
cat .env
```

API key'inizin doğru tanımlandığından emin olun.

### "Connection Error" veya "Timeout"

- İnternet bağlantınızı kontrol edin
- VPN kullanıyorsanız kapatmayı deneyin
- API provider'ın servis durumunu kontrol edin

### Import Hataları

Python path'ini ekleyin:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

veya scripti doğrudan çalıştırın:

```bash
cd complaint_chatbot
python -m streamlit run streamlit_app.py
```

## 📚 Önerilen Workflow

1. **Geliştirme Aşaması**
   - Quick start ile test edin
   - Promptları ayarlayın
   - Excel'i özelleştirin

2. **Test Aşaması**
   - Etkileşimli modu kullanın
   - Farklı şikayet örnekleri deneyin
   - JSON çıktılarını kontrol edin

3. **Deployment**
   - Streamlit uygulamasını kullanın
   - Production API key kullanın
   - Rate limit ayarlarını yapın

## 🎯 Hızlı Test Komutları

```bash
# Tüm modülleri test et
python modules/llm_client.py
python modules/data_manager.py
python modules/categorizer.py
python modules/information_extractor.py
python modules/response_processor.py

# Pipeline test
python chatbot_pipeline.py

# Streamlit başlat
streamlit run streamlit_app.py

# Quick start
python quick_start.py
```

## ✅ Başarılı Kurulum Checklist

- [ ] requirements.txt yüklendi
- [ ] .env dosyası oluşturuldu ve API key eklendi
- [ ] Excel template oluşturuldu
- [ ] Quick start kurulum kontrolü başarılı
- [ ] Demo çalıştı
- [ ] Streamlit uygulaması açıldı

## 🆘 Yardım

Sorun yaşıyorsanız:

1. README.md dosyasını okuyun
2. Hata mesajını Google'da arayın
3. GitHub issue açın
4. Debug mode'u açın (.env'de `DEBUG_MODE=True`)

## 🎉 Kurulum Tamamlandı!

Artık chatbot'unuzu kullanmaya hazırsınız!
