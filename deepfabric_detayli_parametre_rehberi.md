# 🔍 DeepFabric Detaylı Parametre Rehberi

## 📚 İçindekiler
1. Topic Tree & Data Engine Kavramları
2. Tüm Parametrelerin Detaylı Açıklaması
3. Notebook Analizi
4. Pratik Örnekler ve İpuçları

---

## 🌳 1. TOPIC TREE (KONU AĞACI) NEDİR?

**Topic Tree**, DeepFabric'in veri üretim sürecinin **ilk aşamasıdır** ve **konu hiyerarşisi oluşturur**.

### 🎯 Amacı:
Rastgele veri üretmek yerine, **yapılandırılmış ve organize** bir konu ağacı oluşturarak çeşitli ama ilgili konularda veri üretmek.

### 🔄 Nasıl Çalışır?

```
Ana Konu: "Python Programlama"
    │
    ├── Alt Konu 1: "Veri Tipleri"
    │   ├── Alt Konu 1.1: "Liste ve Tuple"
    │   ├── Alt Konu 1.2: "Dictionary ve Set"
    │   └── Alt Konu 1.3: "String İşlemleri"
    │
    ├── Alt Konu 2: "Fonksiyonlar"
    │   ├── Alt Konu 2.1: "Lambda Fonksiyonlar"
    │   ├── Alt Konu 2.2: "Decorators"
    │   └── Alt Konu 2.3: "Generators"
    │
    └── Alt Konu 3: "Nesne Yönelimli Programlama"
        ├── Alt Konu 3.1: "Class ve Object"
        ├── Alt Konu 3.2: "Inheritance"
        └── Alt Konu 3.3: "Polymorphism"
```

### 📊 Temel Parametreler:

| Parametre | Ne İşe Yarar | Örnek | Etki |
|-----------|--------------|-------|------|
| **depth** | Ağacın derinliği (kaç seviye) | `depth: 3` | 3 seviyeli hiyerarşi: Ana → Alt → Alt-Alt |
| **degree** | Her düğümden kaç dal çıkacak | `degree: 4` | Her konudan 4 alt konu üretilir |
| **topic_prompt** | Ana konu tanımı | `"Python Programlama"` | Tüm ağacın temel konusu |

### 🧮 Matematiksel İlişki:

**Toplam konu sayısı ≈ degree^depth**

Örnekler:
- `depth: 2, degree: 3` → 3² = 9 konu
- `depth: 3, degree: 4` → 4³ = 64 konu
- `depth: 4, degree: 5` → 5⁴ = 625 konu

### 💡 Neden Topic Tree Kullanılır?

**OLMADAN:**
❌ Rastgele sorular: "Python nedir?", "Matematik problemi", "Java syntax"
❌ İlişkisiz veriler
❌ Tekrarlayan içerik

**İLE:**
✅ Organize konular: Python → Veri Tipleri → Liste İşlemleri
✅ İlişkili ve derinlemesine içerik
✅ Minimal tekrar, maksimum çeşitlilik

---

## ⚙️ 2. DATA ENGINE (VERİ MOTORU) NEDİR?

**Data Engine**, Topic Tree'den üretilen konuları kullanarak **gerçek eğitim verisi (Q&A çiftleri) oluşturur**.

### 🎯 Amacı:
Topic Tree'den gelen konular için somut, kullanılabilir eğitim örnekleri üretmek.

### 🔄 Nasıl Çalışır?

```
Topic Tree'den Gelen Konu: "Liste ve Tuple Farkları"
    ↓
Data Engine işleme alır
    ↓
Çıktı (Q&A):
{
  "messages": [
    {
      "role": "user",
      "content": "Python'da liste ve tuple arasındaki farklar nelerdir?"
    },
    {
      "role": "assistant",
      "content": "Python'da liste ve tuple arasındaki temel farklar:
      1. Değiştirilebilirlik: Listeler mutable, tuple'lar immutable
      2. Syntax: [] vs ()
      3. Performans: Tuple'lar daha hızlı
      ..."
    }
  ]
}
```

### 📊 Temel Parametreler:

| Parametre | Ne İşe Yarar | Değerler | Açıklama |
|-----------|--------------|----------|----------|
| **num_steps** | Kaç veri örneği üretilecek | 1-1000+ | Toplam eğitim örneği sayısı |
| **batch_size** | Aynı anda kaç örnek işlenecek | 1-10 | API çağrısı optimizasyonu |
| **temperature** | Yaratıcılık seviyesi | 0.0-1.0 | 0.0=deterministik, 1.0=yaratıcı |
| **conversation_type** | Veri türü | cot, tool_calling, multi_turn, qa, code | Hangi tür veri üretilecek |

### 💾 Output Format:

Data Engine her zaman **OpenAI Chat Format** kullanır:

```json
{
  "messages": [
    {"role": "system", "content": "Sen bir uzman asistansın"},
    {"role": "user", "content": "Soru"},
    {"role": "assistant", "content": "Cevap"}
  ]
}
```

---

## 🎨 3. TOPIC TREE vs DATA ENGINE: FARKLAR

| Özellik | Topic Tree | Data Engine |
|---------|------------|-------------|
| **Amaç** | Konu yapısı oluşturma | Gerçek veri üretme |
| **Çıktı** | Konu listesi | Q&A çiftleri |
| **Model Kullanımı** | Pahalı model (GPT-4) kullanılabilir | Ucuz model (Mixtral) yeterli |
| **Temperature** | Yüksek (0.7-0.9) yaratıcılık | Düşük (0.3-0.5) tutarlılık |
| **Çalışma Sırası** | 1. Önce çalışır | 2. Sonra çalışır |
| **Örnek** | "Makine Öğrenmesi Algoritmaları" | User: "SVM nedir?" Assistant: "..." |

---

## 📋 4. TÜM PARAMETRELERİN DETAYLI AÇIKLAMASI

### 🔤 A. GENEL SİSTEM PARAMETRELERİ

#### `dataset_system_prompt`
- **Tip:** String
- **Zorunlu:** Hayır (fallback olarak kullanılır)
- **Örnek:** `"Sen bir Python öğretmenisin."`
- **Ne İşe Yarar:** 
  - Tüm pipeline boyunca genel bir context sağlar
  - Eğer alt bölümlerde system prompt yoksa bunu kullanır
  - Modele "kim olduğunu" söyler

**Örnek Kullanım:**
```yaml
dataset_system_prompt: "Sen bir matematik ve bilgisayar bilimi profesörüsün. Öğrencilere karmaşık kavramları basit şekilde anlatırsın."
```

---

### 🌳 B. TOPIC_TREE / TOPIC_GRAPH PARAMETRELERİ

#### `topic_prompt`
- **Tip:** String
- **Zorunlu:** Evet
- **Örnek:** `"Yapay Zeka ve Makine Öğrenmesi Temelleri"`
- **Ne İşe Yarar:** 
  - Ana konu başlığı
  - Tüm alt konular bundan türetilir
  - Ne kadar spesifik olursa o kadar iyi

**İyi vs Kötü Örnekler:**
```yaml
# ❌ KÖTÜ - Çok Geniş
topic_prompt: "Bilgisayar"

# ✅ İYİ - Spesifik
topic_prompt: "Python ile Web Scraping: BeautifulSoup ve Selenium Kullanımı"

# ✅ ÇOK İYİ - Spesifik + Context
topic_prompt: "Veri Bilimi için Python: Pandas, NumPy ve Matplotlib ile Veri Analizi"
```

#### `provider`
- **Tip:** String (enum)
- **Zorunlu:** Evet
- **Değerler:** 
  - `"openai"` - OpenAI API
  - `"anthropic"` - Claude API
  - `"gemini"` - Google Gemini
  - `"ollama"` - Yerel Ollama
  - `"openrouter"` - OpenRouter (çoklu model)
- **Ne İşe Yarar:** Hangi API/servis kullanılacağını belirler

**Maliyet Karşılaştırması:**
```yaml
# 💰 EN PAHALI - En kaliteli topic tree için
provider: "openai"
model: "gpt-4-turbo"

# 💵 ORTA - İyi denge
provider: "anthropic"  
model: "claude-3-sonnet"

# 🆓 ÜCRETSİZ - Yerel kullanım
provider: "ollama"
model: "llama3:70b"
```

#### `model`
- **Tip:** String
- **Zorunlu:** Evet
- **Format:** Provider'a göre değişir
  - OpenAI: `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
  - OpenRouter: `"meta-llama/llama-3.1-70b-instruct"`
  - Ollama: `"llama3:70b"`, `"qwen3:32b"`
- **Ne İşe Yarar:** Kullanılacak spesifik modeli seçer

**Model Seçim Stratejisi:**
```yaml
# TOPIC TREE için: Kaliteli model kullan
topic_tree:
  provider: "openai"
  model: "gpt-4-turbo"  # Çeşitli ve organize konular için

# DATA ENGINE için: Ucuz model kullan
data_engine:
  provider: "ollama"
  model: "llama3:70b"  # Bulk üretim için yeterli
```

#### `temperature`
- **Tip:** Float
- **Zorunlu:** Hayır (default: 0.7)
- **Aralık:** 0.0 - 2.0 (pratik: 0.0 - 1.0)
- **Ne İşe Yarar:** Model çıktısının rastgeleliğini/yaratıcılığını kontrol eder

**Temperature Rehberi:**
| Değer | Ne Zaman Kullan | Örnek Senaryo |
|-------|-----------------|---------------|
| **0.0** | Deterministik sonuç | Kod üretimi, doğru cevap |
| **0.3** | Az varyasyon | Matematik problemleri |
| **0.5** | Dengeli | Genel Q&A |
| **0.7** | Yaratıcı + Tutarlı | Topic generation |
| **0.9** | Çok yaratıcı | Yaratıcı yazma, beyin fırtınası |
| **1.0+** | Kaotik | Genelde kullanılmaz |

**Notebook'unuzdan Örnek:**
```python
# Topic Tree için - Yaratıcı konular istiyoruz
'temperature': 0.7  

# Data Engine için - Tutarlı cevaplar istiyoruz
'temperature': 0.5
```

#### `degree`
- **Tip:** Integer
- **Zorunlu:** Evet
- **Aralık:** 1 - 10 (önerilen: 2-5)
- **Ne İşe Yarar:** Her düğümden kaç alt konu dallanacağını belirler

**Degree İlişkisi:**
```
degree: 2
Ana Konu
├── Alt 1
└── Alt 2

degree: 3
Ana Konu
├── Alt 1
├── Alt 2
└── Alt 3

degree: 4
Ana Konu
├── Alt 1
├── Alt 2
├── Alt 3
└── Alt 4
```

**Hesaplama:**
- `degree: 3, depth: 2` → 3¹ + 3² = 3 + 9 = 12 konu
- `degree: 4, depth: 3` → 4¹ + 4² + 4³ = 4 + 16 + 64 = 84 konu

**Notebook'unuzdan:**
```python
'degree': 3  # Her konudan 3 alt konu üretilecek
```

#### `depth`
- **Tip:** Integer
- **Zorunlu:** Evet
- **Aralık:** 1 - 5 (önerilen: 2-3)
- **Ne İşe Yarar:** Ağacın kaç seviye derin olacağını belirler

**Depth Örnekleri:**

```
depth: 1 (Yüzeysel)
Ana Konu
├── Alt 1
├── Alt 2
└── Alt 3

depth: 2 (Dengeli)
Ana Konu
├── Alt 1
│   ├── Alt 1.1
│   └── Alt 1.2
└── Alt 2
    ├── Alt 2.1
    └── Alt 2.2

depth: 3 (Derin)
Ana Konu
├── Alt 1
│   ├── Alt 1.1
│   │   ├── Alt 1.1.1
│   │   └── Alt 1.1.2
│   └── Alt 1.2
└── Alt 2
```

**Ne Zaman Hangi Depth:**
- `depth: 1` → Geniş ama yüzeysel (genel bakış)
- `depth: 2` → **EN POPÜLER** - İyi denge
- `depth: 3` → Derinlemesine (uzman seviye)
- `depth: 4+` → Çok spesifik (nadiren gerekir)

**Notebook'unuzdan:**
```python
'depth': 2  # 2 seviyeli hiyerarşi
```

#### `topic_system_prompt`
- **Tip:** String
- **Zorunlu:** Hayır (dataset_system_prompt kullanılır)
- **Örnek:** `"Sen bir müfredat tasarımcısısın"`
- **Ne İşe Yarar:** 
  - SADECE konu üretimi için özel prompt
  - `dataset_system_prompt`'u override eder
  - Topic kalitesini artırır

**Örnek Kullanım:**
```yaml
topic_tree:
  topic_system_prompt: |
    Sen bir eğitim müfredat uzmanısın. 
    Konuları şu kriterlere göre organize et:
    1. Kolay → Zor sıralaması
    2. Önkoşul bilgiler önce gelsin
    3. Pratik örnekler içersin
```

#### `save_as`
- **Tip:** String (dosya yolu)
- **Zorunlu:** Hayır
- **Örnek:** `"topics_python.jsonl"`
- **Ne İşe Yarar:** 
  - Üretilen topic tree'yi kaydeder
  - Debug ve inceleme için kullanışlı
  - JSONL formatında

**Topic Tree Output Örneği:**
```jsonl
{"topic": "Python Veri Tipleri", "level": 0}
{"topic": "Liste İşlemleri", "level": 1, "parent": "Python Veri Tipleri"}
{"topic": "Liste Comprehension", "level": 2, "parent": "Liste İşlemleri"}
```

---

### ⚙️ C. DATA_ENGINE PARAMETRELERİ

#### `generation_system_prompt`
- **Tip:** String
- **Zorunlu:** Hayır
- **Örnek:** `"Her soruyu detaylı açıkla"`
- **Ne İşe Yarar:** 
  - Veri üretimi için özel prompt
  - Cevap formatını ve stilini kontrol eder

**Farklı Türler için Örnekler:**

```yaml
# Code Generation için
generation_system_prompt: |
  Sen bir yazılım mühendisisin.
  - Çalışan kod örnekleri ver
  - Yorumlar ekle
  - Best practices kullan
  - Edge case'leri ele al

# Chain of Thought için
generation_system_prompt: |
  Her problemi adım adım çöz:
  1. Problemi anla
  2. Yaklaşımı belirle
  3. Adım adım çöz
  4. Sonucu doğrula

# Tool Calling için
generation_system_prompt: |
  Kullanıcı isteğini analiz et ve:
  1. Hangi tool gerekli belirle
  2. Parametreleri çıkar
  3. Tool'u çağır
  4. Sonucu yorumla
```

#### `instructions`
- **Tip:** String
- **Zorunlu:** Hayır
- **Örnek:** `"Matematik problemleri oluştur"`
- **Ne İşe Yarar:** 
  - Veri üretim sürecine genel talimatlar
  - `generation_system_prompt` ile birlikte çalışır

#### `conversation_type`
- **Tip:** String (enum)
- **Zorunlu:** Hayır
- **Değerler:**
  - `"chain_of_thought"` - Adım adım akıl yürütme
  - `"tool_calling"` - Fonksiyon çağırma
  - `"multi_turn"` - Çok turlu konuşma
  - `"qa"` - Basit soru-cevap
  - `"code"` - Kod üretimi
- **Ne İşe Yarar:** Hangi tür veri üretileceğini belirler

**Conversation Type Detayları:**

##### 1. `chain_of_thought` (CoT)
```json
{
  "messages": [
    {"role": "user", "content": "147 x 23 = ?"},
    {"role": "assistant", "content": 
      "Adım 1: 147 x 20 = 2,940
       Adım 2: 147 x 3 = 441
       Adım 3: 2,940 + 441 = 3,381
       Sonuç: 3,381"
    }
  ]
}
```

**Ne Zaman Kullan:**
- Matematiksel problemler
- Karmaşık akıl yürütme gerektiren sorular
- Step-by-step düşünme

##### 2. `tool_calling`
```json
{
  "messages": [
    {"role": "user", "content": "İstanbul'da hava nasıl?"},
    {"role": "assistant", "content": null, 
     "tool_calls": [
       {
         "id": "call_123",
         "type": "function",
         "function": {
           "name": "get_weather",
           "arguments": "{\"city\":\"Istanbul\"}"
         }
       }
     ]
    },
    {"role": "tool", "content": "{\"temp\":18,\"condition\":\"sunny\"}"},
    {"role": "assistant", "content": "İstanbul'da hava 18°C ve güneşli."}
  ]
}
```

**Ne Zaman Kullan:**
- API entegrasyonu gerektiren tasklar
- Function calling eğitimi
- Agent davranışı öğretme

##### 3. `multi_turn`
```json
{
  "messages": [
    {"role": "user", "content": "Python öğrenmek istiyorum"},
    {"role": "assistant", "content": "Harika! Hangi seviyedesiniz?"},
    {"role": "user", "content": "Yeni başlayan"},
    {"role": "assistant", "content": "O zaman temel syntax ile başlayalım..."}
  ]
}
```

**Ne Zaman Kullan:**
- Konuşma modellerini eğitmek
- Context takibi öğretmek
- Chatbot geliştirmek

##### 4. `qa` (Question-Answer)
```json
{
  "messages": [
    {"role": "user", "content": "Python nedir?"},
    {"role": "assistant", "content": "Python yüksek seviyeli bir programlama dilidir..."}
  ]
}
```

**Ne Zaman Kullan:**
- Basit Q&A veri setleri
- Hızlı üretim gereken durumlarda
- Instruction tuning

##### 5. `code`
```json
{
  "messages": [
    {"role": "user", "content": "Liste tersine çeviren fonksiyon yaz"},
    {"role": "assistant", "content": 
      "```python\ndef reverse_list(lst):\n    return lst[::-1]\n```"
    }
  ]
}
```

**Ne Zaman Kullan:**
- Kod üretimi modelleri için
- Programming assistants
- Code completion

#### `max_retries`
- **Tip:** Integer
- **Zorunlu:** Hayır (default: 3)
- **Aralık:** 1 - 10
- **Ne İşe Yarar:** 
  - API hatalarında kaç kez tekrar deneneceği
  - Rate limiting durumlarında
  - Timeout'larda

**Önerilen Değerler:**
```yaml
# Hızlı üretim - Az retry
max_retries: 1

# Standart - Dengeli
max_retries: 3  # DEFAULT

# Kritik veri - Fazla retry
max_retries: 5
```

---

### 📊 D. DATASET PARAMETRELERİ

#### `creation.num_steps`
- **Tip:** Integer
- **Zorunlu:** Evet
- **Aralık:** 1 - sınırsız
- **Ne İşe Yarar:** 
  - Toplam kaç veri örneği üretileceği
  - Eğitim veri seti boyutunu belirler

**Hesaplama ve Süre:**
```python
# Her örnek ~5 saniye (model bağlı)
num_steps: 10   → ~50 saniye
num_steps: 100  → ~8 dakika
num_steps: 1000 → ~1.5 saat
```

**Notebook'unuzdan:**
```python
'num_steps': 15  # 15 Q&A çifti üretilecek
```

**Öneriler:**
- **Test:** 10-20
- **Küçük dataset:** 100-500
- **Orta dataset:** 1,000-5,000
- **Büyük dataset:** 10,000+

#### `creation.batch_size`
- **Tip:** Integer
- **Zorunlu:** Hayır (default: 1)
- **Aralık:** 1 - 10
- **Ne İşe Yarar:** 
  - Aynı anda kaç örnek işleneceği
  - API rate limit ve paralellik için
  - Memory kullanımını etkiler

**Batch Size Optimizasyonu:**
```yaml
# Rate limit yoksa
batch_size: 5  # 5x daha hızlı

# Rate limit varsa
batch_size: 1  # Güvenli ama yavaş

# Dengeli yaklaşım
batch_size: 3  # İyi denge
```

**Notebook'unuzdan:**
```python
'batch_size': 3  # Aynı anda 3 örnek işle
```

**Avantajlar:**
- ✅ Daha hızlı üretim
- ✅ API çağrısı optimizasyonu

**Dezavantajlar:**
- ❌ Yüksek memory
- ❌ Rate limit riski

#### `creation.sys_msg`
- **Tip:** Boolean
- **Zorunlu:** Hayır (default: true)
- **Ne İşe Yarar:** 
  - Çıktıya system mesajı eklensin mi?
  - OpenAI format uyumluluğu için

**True (default):**
```json
{
  "messages": [
    {"role": "system", "content": "Sen bir yardımcı asistansın"},
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Selam!"}
  ]
}
```

**False:**
```json
{
  "messages": [
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Selam!"}
  ]
}
```

**Ne Zaman False:**
- Some models don't use system messages
- Custom format gerekliyse
- System prompt istemiyorsanız

#### `save_as`
- **Tip:** String (dosya yolu)
- **Zorunlu:** Evet
- **Örnek:** `"dataset_python.jsonl"`
- **Ne İşe Yarar:** Final dataset'in kaydedileceği dosya

---

### 🤗 E. HUGGINGFACE PARAMETRELERİ

#### `huggingface.repository`
- **Tip:** String
- **Format:** `"username/dataset-name"`
- **Örnek:** `"john/python-qa-dataset"`
- **Ne İşe Yarar:** HuggingFace Hub'a otomatik upload

#### `huggingface.token`
- **Tip:** String
- **Kaynak:** Environment variable veya direkt
- **Ne İşe Yarar:** HuggingFace authentication

#### `huggingface.tags`
- **Tip:** List[String]
- **Örnek:** `["synthetic", "qa", "python"]`
- **Ne İşe Yarar:** Dataset'i kategorize etmek

**Otomatik Eklenen:**
- `"deepfabric"`
- `"synthetic"`

---

## 📓 5. NOTEBOOK ANALİZİ

### Chain of Thought (CoT) Konfigürasyonu Analizi

```python
cot_config = {
    'dataset_system_prompt': 'Sen bir matematik ve programlama uzmanısın...',
    
    'topic_graph': {
        'topic_prompt': 'Matematik ve Programlama Problemleri: Algoritmalar, veri yapıları...',
        'provider': 'openrouter',
        'model': 'meta-llama/llama-3.1-70b-instruct',
        'temperature': 0.7,  # 🎲 Yaratıcı konu üretimi için
        'degree': 3,         # 🌳 Her konudan 3 alt konu
        'depth': 2,          # 📊 2 seviye derinlik → 3² = 9 konu
        'save_as': 'topics_cot.jsonl'
    },
    
    'data_engine': {
        'generation_system_prompt': 'Her problemi adım adım çöz...',
        'instructions': 'Adım adım akıl yürütme ile problemler çöz.',
        'conversation_type': 'chain_of_thought',  # 🧠 CoT tipi
        'provider': 'openrouter',
        'model': 'meta-llama/llama-3.1-70b-instruct',
        'temperature': 0.5,  # 🎯 Tutarlı cevaplar için daha düşük
        'max_retries': 3
    },
    
    'dataset': {
        'save_as': 'cot_math_programming.jsonl',
        'creation': {
            'num_steps': 15,     # 📦 15 örnek
            'batch_size': 3,     # ⚡ 3'er 3'er işle
            'sys_msg': True      # 💬 System mesajı dahil
        }
    }
}
```

### Parametrelerin İşleyişi:

#### 1️⃣ Topic Tree Aşaması:
```
Llama-3.1-70B (temp: 0.7) → Yaratıcı konular üretir
↓
degree: 3, depth: 2
↓
Ana: "Matematik ve Programlama"
├── Alt 1: "Arama Algoritmaları"
│   ├── Alt 1.1: "Binary Search"
│   ├── Alt 1.2: "Linear Search"  
│   └── Alt 1.3: "Interpolation Search"
├── Alt 2: "Sıralama Algoritmaları"
│   ├── Alt 2.1: "Quick Sort"
│   ├── Alt 2.2: "Merge Sort"
│   └── Alt 2.3: "Bubble Sort"
└── Alt 3: "Veri Yapıları"
    ├── Alt 3.1: "Stack"
    ├── Alt 3.2: "Queue"
    └── Alt 3.3: "Linked List"

Total: 12 konu oluşturuldu
```

#### 2️⃣ Data Engine Aşaması:
```
12 konudan rastgele seçim
↓
num_steps: 15 örnek üret
↓
batch_size: 3 → 5 batch (15/3)
↓
Her batch için Llama-3.1-70B (temp: 0.5)
↓
15 CoT örneği üretildi
```

### Output Örneği:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sen bir matematik ve programlama uzmanısın..."
    },
    {
      "role": "user",
      "content": "Binary Search algoritmasını Python'da nasıl implement ederim?"
    },
    {
      "role": "assistant",
      "content": "Binary Search'ü adım adım implement edelim:\n\nAdım 1: Listeyi sırala (Binary Search sıralı liste gerektirir)\nAdım 2: Başlangıç ve bitiş pointer'larını belirle (low=0, high=len-1)\nAdım 3: Ortanca elemanı bul (mid = (low + high) // 2)\nAdım 4: Aranan değer ile ortancayı karşılaştır\n  - Eşitse: Bulundu, index döndür\n  - Küçükse: Sol yarıda ara (high = mid - 1)\n  - Büyükse: Sağ yarıda ara (low = mid + 1)\nAdım 5: low <= high olduğu sürece tekrarla\n\nKod:\n```python\ndef binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    \n    while low <= high:\n        mid = (low + high) // 2\n        \n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    \n    return -1\n\n# Test\narr = [1, 3, 5, 7, 9, 11]\nprint(binary_search(arr, 7))  # Output: 3\n```"
    }
  ]
}
```

---

## 💡 6. PRATİK İPUÇLARI

### Maliyet Optimizasyonu:

```yaml
# 💰 PAHALI ama KALİTELİ
topic_tree:
  provider: "openai"
  model: "gpt-4-turbo"
data_engine:
  provider: "openai"
  model: "gpt-4-turbo"
# Maliyet: $$$

# 💵 DENGELI
topic_tree:
  provider: "openai"
  model: "gpt-4-turbo"      # Kaliteli konular
data_engine:
  provider: "ollama"
  model: "llama3:70b"        # Ucuz bulk üretim
# Maliyet: $$

# 🆓 ÜCRETSIZ
topic_tree:
  provider: "ollama"
  model: "llama3:70b"
data_engine:
  provider: "ollama"
  model: "llama3:8b"
# Maliyet: $0
```

### Kalite vs Hız:

| Hedef | depth | degree | num_steps | batch_size | Süre |
|-------|-------|--------|-----------|------------|------|
| **Hızlı Test** | 1 | 2 | 10 | 5 | ~1 dk |
| **Küçük Dataset** | 2 | 3 | 100 | 3 | ~10 dk |
| **Orta Dataset** | 3 | 3 | 1000 | 3 | ~2 saat |
| **Büyük Dataset** | 3 | 4 | 10000 | 5 | ~20 saat |

### Temperature Stratejisi:

```yaml
# Farklı amaçlar için farklı temperature'lar:

# 1. Kod Üretimi
topic_tree:
  temperature: 0.6    # Yaratıcı konular
data_engine:
  temperature: 0.2    # Çalışan kod

# 2. Yaratıcı Yazma
topic_tree:
  temperature: 0.8
data_engine:
  temperature: 0.7

# 3. Fact-based QA
topic_tree:
  temperature: 0.7
data_engine:
  temperature: 0.3    # Doğru cevaplar

# 4. Chain of Thought
topic_tree:
  temperature: 0.7
data_engine:
  temperature: 0.5    # Tutarlı adımlar
```

### Batch Size Kılavuzu:

```yaml
# API Rate Limit varsa
batch_size: 1

# OpenRouter (çoğunlukla sınırsız)
batch_size: 5

# Ollama (yerel, hızlı)
batch_size: 10

# OpenAI (rate limit var)
batch_size: 2-3
```

---

## 🎓 7. ÖZET TABLOSU

### Temel Parametreler Özeti:

| Parametre | Kategori | Aralık | Önerilen | Amacı |
|-----------|----------|--------|----------|-------|
| **depth** | Topic | 1-5 | 2-3 | Ağaç derinliği |
| **degree** | Topic | 1-10 | 3-4 | Dallanma sayısı |
| **temperature** | LLM | 0.0-1.0 | 0.3-0.7 | Yaratıcılık |
| **num_steps** | Dataset | 1-∞ | 100-1000 | Örnek sayısı |
| **batch_size** | Dataset | 1-10 | 3-5 | Paralel işlem |
| **max_retries** | Engine | 1-10 | 3 | Hata toleransı |

### Conversation Type Seçim Tablosu:

| İhtiyaç | Type | Use Case |
|---------|------|----------|
| Adım adım düşünme | `chain_of_thought` | Matematik, problem solving |
| API/fonksiyon kullanımı | `tool_calling` | Function calling, agents |
| Konuşma | `multi_turn` | Chatbots, assistants |
| Basit Q&A | `qa` | Knowledge base, instruction |
| Kod | `code` | Code generation, programming |

---

## 🚀 8. SON TAVSİYELER

### Başlangıç için İdeal Konfigürasyon:

```yaml
dataset_system_prompt: "Sen bir uzman asistansın."

topic_tree:
  topic_prompt: "[Spesifik konu]"
  provider: "ollama"          # Ücretsiz başlangıç
  model: "llama3:70b"
  temperature: 0.7
  degree: 3                   # Dengeli
  depth: 2                    # İyi başlangıç
  
data_engine:
  provider: "ollama"
  model: "llama3:70b"
  temperature: 0.5
  max_retries: 3
  
dataset:
  creation:
    num_steps: 100            # Test için yeterli
    batch_size: 3
    sys_msg: true
  save_as: "my_dataset.jsonl"
```

### Debug İpuçları:

1. **İlk önce küçük test:**
   ```yaml
   depth: 1
   degree: 2
   num_steps: 5
   ```

2. **Topic tree'yi kaydet ve incele:**
   ```yaml
   topic_tree:
     save_as: "topics_debug.jsonl"  # İncele!
   ```

3. **Temperature ile oyna:**
   - Çok benzer sonuçlar → Temperature artır
   - Çok alakasız sonuçlar → Temperature azalt

4. **Batch size ile başla:**
   - Önce `batch_size: 1` ile test et
   - Çalışıyorsa artır

---

Bu rehber, DeepFabric'in tüm parametrelerini ve notebook'unuzu detaylıca açıklamaktadır. Herhangi bir soru veya ek açıklama için lütfen sorun! 🎉
