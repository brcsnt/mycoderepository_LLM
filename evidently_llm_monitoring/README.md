# 🚀 Evidently LLM Monitoring Sistemi

Açık kaynaklı LLM'leri API üzerinden kullanıp **Evidently** ile izleyen, analiz eden ve raporlayan komple bir sistem.

## 📋 Özellikler

- ✅ Çoklu LLM provider desteği (Ollama, OpenAI, Groq, Together, Hugging Face)
- ✅ Real-time monitoring ve metrik toplama
- ✅ Evidently ile otomatik rapor oluşturma
- ✅ Response kalitesi analizi
- ✅ İnteraktif sohbet modu
- ✅ Batch processing desteği
- ✅ HTML ve JSON rapor çıktıları

## 🏗️ Mimari

```
evidently_llm_monitoring/
├── config.py          # Konfigürasyon ayarları
├── llm_client.py      # LLM API client'ı
├── monitoring.py      # Evidently monitoring modülü
├── main.py           # Ana uygulama
├── .env.example      # Environment variables örneği
└── README.md         # Bu dosya
```

## 📦 Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install evidently requests pandas python-dotenv
```

### 2. Environment Variables Ayarla

`.env.example` dosyasını `.env` olarak kopyalayın:

```bash
cp .env.example .env
```

Ardından `.env` dosyasını düzenleyin:

```bash
# Yerel ve ücretsiz başlangıç için
LLM_PROVIDER=ollama

# veya cloud API için
# LLM_PROVIDER=groq
# GROQ_API_KEY=your-api-key
```

### 3. LLM Provider Kurulumu

#### Option A: Ollama (Önerilen - Ücretsiz & Yerel)

```bash
# Ollama'yı indirin: https://ollama.ai
# Model çekin
ollama pull llama2

# Ollama'yı başlatın
ollama serve
```

#### Option B: Groq (Hızlı & Ucuz Cloud)

```bash
# https://console.groq.com adresinden API key alın
# .env dosyasına ekleyin
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-api-key-here
```

#### Option C: OpenAI

```bash
# https://platform.openai.com adresinden API key alın
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
```

## 🚀 Kullanım

### İnteraktif Mod (Önerilen)

```bash
cd evidently_llm_monitoring
python main.py --mode interactive
```

İnteraktif modda:
- Soru sorun ve cevaplar alın
- `stats` yazarak istatistikleri görün
- `report` yazarak Evidently raporu oluşturun
- `save` yazarak veriyi kaydedin
- `exit` ile çıkın

### Demo Mod

Hazır sorularla hızlı test:

```bash
python main.py --mode demo
```

### Batch Mod

Toplu soru işleme:

```bash
python main.py --mode batch --prompts "Python nedir?" "Machine learning nedir?" "Docker nedir?"
```

### Programatik Kullanım

```python
from llm_client import LLMClient
from monitoring import LLMMonitor

# Client ve monitor başlat
client = LLMClient()
monitor = LLMMonitor()

# LLM'den cevap al
result = client.generate("Python'da liste comprehension nedir?")

# Monitoring sistemine kaydet
monitor.add_interaction(result)

# İstatistikleri göster
monitor.print_statistics()

# Rapor oluştur
monitor.generate_report()
```

## 📊 Evidently Raporları

Raporlar `./evidently_reports/` dizinine kaydedilir:

- **HTML Rapor**: Tarayıcıda görselleştirme
- **JSON Rapor**: Programatik erişim için

### Rapor İçeriği

- ✅ **Text Evaluations**: Sentiment, toxicity, text quality
- ✅ **Response Metrics**: Uzunluk, kelime sayısı, cümle sayısı
- ✅ **Performance Metrics**: Response time, throughput
- ✅ **Quality Analysis**: Çok kısa/uzun cevaplar, hatalar

## 🔧 Konfigürasyon

### Desteklenen LLM Provider'lar

| Provider | Tip | Maliyet | Hız | Kurulum |
|----------|-----|---------|-----|---------|
| **Ollama** | Yerel | Ücretsiz | Orta | Kolay |
| **Groq** | Cloud | Çok Ucuz | Çok Hızlı | Çok Kolay |
| **OpenAI** | Cloud | Orta | Hızlı | Kolay |
| **Together** | Cloud | Ucuz | Hızlı | Kolay |
| **Hugging Face** | Cloud | Ücretsiz/Ücretli | Yavaş | Orta |

### Model Örnekleri

```bash
# Ollama
LLM_MODEL=llama2
LLM_MODEL=mistral
LLM_MODEL=codellama

# Groq
LLM_MODEL=mixtral-8x7b-32768
LLM_MODEL=llama2-70b-4096

# OpenAI
LLM_MODEL=gpt-3.5-turbo
LLM_MODEL=gpt-4

# Together
LLM_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

## 📈 Metrikler ve İzleme

Sistem otomatik olarak şu metrikleri toplar:

1. **Response Quality**
   - Text length
   - Word count
   - Sentence count
   - Sentiment score

2. **Performance**
   - Response time
   - Throughput (requests/second)
   - Error rate

3. **Usage Statistics**
   - Total interactions
   - Provider distribution
   - Model usage

## 🎯 Kullanım Senaryoları

### 1. Model Karşılaştırma

Farklı modelleri test edin ve karşılaştırın:

```bash
# Model 1
LLM_PROVIDER=ollama LLM_MODEL=llama2 python main.py --mode demo

# Model 2
LLM_PROVIDER=groq LLM_MODEL=mixtral-8x7b-32768 python main.py --mode demo
```

### 2. Production Monitoring

Canlı sistemdeki LLM'i izleyin:

```python
from monitoring import LLMMonitor

monitor = LLMMonitor()

# Her API çağrısında
monitor.add_interaction(llm_result)

# Periyodik rapor
if interaction_count % 100 == 0:
    monitor.generate_report()
```

### 3. Quality Assurance

Yanıt kalitesini kontrol edin:

```python
quality = monitor.analyze_quality()

if quality['error_rate'] > 5.0:
    send_alert("LLM error rate too high!")
```

## 🛠️ Troubleshooting

### Ollama Bağlantı Hatası

```bash
# Ollama'nın çalıştığından emin olun
ollama list

# Yeniden başlatın
ollama serve
```

### API Key Hatası

```bash
# .env dosyasını kontrol edin
cat .env

# Doğru key'in ayarlandığından emin olun
echo $OPENAI_API_KEY
```

### Evidently Import Hatası

```bash
# Evidently'yi yükleyin
pip install evidently

# Versiyon kontrolü
python -c "import evidently; print(evidently.__version__)"
```

## 📚 Ek Kaynaklar

- [Evidently Dokümantasyonu](https://docs.evidentlyai.com/)
- [Ollama](https://ollama.ai)
- [Groq API](https://console.groq.com)
- [OpenAI API](https://platform.openai.com)

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için önce bir issue açın.

## 📄 Lisans

MIT

## 🎉 Başarılı Kullanımlar İçin İpuçları

1. **Başlangıç**: Ollama ile yerel olarak başlayın
2. **Prodüksiyon**: Groq gibi hızlı cloud servislere geçin
3. **Monitoring**: Her 50-100 interaction'da rapor oluşturun
4. **Optimizasyon**: Evidently raporlarını kullanarak prompt'larınızı iyileştirin
5. **Backup**: Periyodik olarak veriyi kaydedin (`monitor.save_data()`)

---

**Not**: Bu sistem açık kaynaklı LLM'lerin izlenmesi ve değerlendirilmesi için tasarlanmıştır. Production kullanımı için ek güvenlik önlemleri almanız önerilir.
