# 🚀 Hızlı Başlangıç - Evidently LLM Monitoring

Bu rehber size 5 dakikada sistemi çalıştırmayı gösterecek.

## ⚡ Adım 1: Kurulum (2 dakika)

```bash
# Projeye git
cd evidently_llm_monitoring

# Bağımlılıkları yükle
pip install evidently requests pandas python-dotenv

# Environment dosyası oluştur
cp .env.example .env
```

## 🐳 Adım 2: LLM Seç (2 dakika)

### Seçenek A: Ollama (Önerilen - Ücretsiz)

```bash
# 1. Ollama'yı indirin: https://ollama.ai

# 2. Model çekin
ollama pull llama2

# 3. Ollama'yı başlatın
ollama serve

# 4. .env dosyasında zaten ayarlı:
# LLM_PROVIDER=ollama
```

### Seçenek B: Groq (Hızlı Cloud - Ücretsiz Trial)

```bash
# 1. https://console.groq.com adresinden API key alın

# 2. .env dosyasını düzenleyin:
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-api-key-here
```

## 🎯 Adım 3: Çalıştır! (1 dakika)

### İnteraktif Mod

```bash
python main.py --mode interactive
```

Soru sorun:
```
👤 Siz: Python nedir?
🤖 LLM: Python, yüksek seviyeli bir programlama dilidir...
⏱️  Süre: 1.23s

👤 Siz: stats      # İstatistikleri göster
👤 Siz: report     # Rapor oluştur
👤 Siz: exit       # Çık
```

### Demo Mod

Hazır örneklerle test:

```bash
python main.py --mode demo
```

Bu komut:
- ✅ 5 örnek soru sorar
- ✅ İstatistikleri gösterir
- ✅ Evidently raporu oluşturur
- ✅ HTML rapor açar

## 📊 Adım 4: Raporları İncele

```bash
# Evidently raporlarını görüntüle
cd evidently_reports
open llm_report_*.html  # Mac
xdg-open llm_report_*.html  # Linux
start llm_report_*.html  # Windows
```

## 🎓 İleri Seviye Kullanım

### Örnek Senaryolar

```bash
# Örnekleri çalıştır
python example_usage.py
```

### Programatik Kullanım

```python
from llm_client import LLMClient
from monitoring import LLMMonitor

client = LLMClient()
monitor = LLMMonitor()

# Soru sor
result = client.generate("Machine learning nedir?")

# İzle
monitor.add_interaction(result)

# Rapor
monitor.generate_report()
```

### Batch İşleme

```bash
python main.py --mode batch --prompts \
  "Python nedir?" \
  "Machine learning nedir?" \
  "Docker nedir?"
```

## 🔧 Sorun Giderme

### Ollama bağlanamıyor?

```bash
# Ollama çalışıyor mu kontrol et
ollama list

# Yeniden başlat
ollama serve
```

### API key hatası?

```bash
# .env dosyasını kontrol et
cat .env

# Doğru formatta olduğundan emin ol
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-actual-key-here
```

### Evidently import hatası?

```bash
# Evidently'yi yükle
pip install evidently

# Kontrol et
python -c "import evidently; print('OK')"
```

## 🎉 Başarılı!

Artık sisteminiz hazır. Şunları yapabilirsiniz:

- ✅ Farklı LLM'leri test edin
- ✅ Response kalitesini ölçün
- ✅ Performans metriklerini izleyin
- ✅ Evidently raporları oluşturun

## 📚 Sonraki Adımlar

- [README.md](README.md) - Detaylı dokümantasyon
- [example_usage.py](example_usage.py) - Daha fazla örnek
- [Evidently Docs](https://docs.evidentlyai.com/) - Evidently hakkında

---

**Sorularınız mı var?** Issues bölümünden sorabilirsiniz!
