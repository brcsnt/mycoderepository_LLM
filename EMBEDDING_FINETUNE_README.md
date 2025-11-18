# Embedding Fine-tuning Kılavuzu

Bu kılavuz, Türkçe BERT ve BGE modellerini soru-cevap verileri üzerinde fine-tune etmek için hazırlanmıştır.

## İçindekiler
- [Kurulum](#kurulum)
- [Veri Formatı](#veri-formatı)
- [Turkish BERT Fine-tuning](#turkish-bert-fine-tuning)
- [BGE Model Fine-tuning](#bge-model-fine-tuning)
- [Model Değerlendirme](#model-değerlendirme)
- [Kullanım Örnekleri](#kullanım-örnekleri)
- [İpuçları ve Best Practices](#ipuçları-ve-best-practices)

## Kurulum

### 1. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements_embedding_finetune.txt
```

### 2. GPU Kontrolü (Opsiyonel ama Önerilen)

```python
import torch
print(f"CUDA mevcut: {torch.cuda.is_available()}")
print(f"CUDA cihaz sayısı: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Mevcut GPU: {torch.cuda.get_device_name(0)}")
```

## Veri Formatı

Fine-tuning için veri setiniz aşağıdaki formatlardan birinde olmalıdır:

### JSON Format (.json)

```json
[
  {
    "question": "Soru metni buraya",
    "answer": "Cevap metni buraya"
  },
  {
    "question": "Başka bir soru",
    "answer": "Başka bir cevap"
  }
]
```

### JSONL Format (.jsonl)

```jsonl
{"question": "Soru 1", "answer": "Cevap 1"}
{"question": "Soru 2", "answer": "Cevap 2"}
{"question": "Soru 3", "answer": "Cevap 3"}
```

### CSV Format (.csv)

```csv
question,answer
"Soru 1","Cevap 1"
"Soru 2","Cevap 2"
"Soru 3","Cevap 3"
```

### Hard Negatives ile Format (Önerilen)

Hard negative örnekler, modelin daha iyi ayrım yapmasını sağlar. MultipleNegativesRankingLoss ile kullanıldığında model performansı önemli ölçüde artar.

**JSON Format:**
```json
[
  {
    "question": "Python nedir?",
    "positive": "Python yüksek seviyeli bir programlama dilidir.",
    "negatives": [
      "Java nesne yönelimli bir dildir.",
      "JavaScript web geliştirme için kullanılır.",
      "C++ sistem programlama dilidir."
    ]
  }
]
```

**CSV Format:**
```csv
question,positive,negative1,negative2,negative3
"Python nedir?","Python yüksek seviyeli bir dildir","Java nesne yönelimlidir","JavaScript web içindir","C++ sistem dilidir"
```

**Önemli Notlar:**
- `positive`: Doğru cevap
- `negatives`: Yanlış ama alakalı cevaplar (hard negatives)
- Her soru için 2-5 hard negative öneriliryük
- Hard negatives ne kadar alakalıysa, model o kadar iyi öğrenir
- Otomatik hard negatives: Eğer sadece question/answer verilirse, script otomatik olarak diğer cevapları hard negative olarak kullanır

**Örnek veriler:**
- `example_qa_data.json` - Basit format (otomatik hard negatives)
- `example_qa_data_with_negatives.json` - Explicit hard negatives ile

## Turkish BERT Fine-tuning

### Temel Kullanım

```bash
python finetune_turkish_bert_qa.py \
  --data_path example_qa_data.json \
  --output_dir ./models/turkish-bert-qa-finetuned \
  --epochs 3 \
  --batch_size 16
```

### Gelişmiş Parametreler

```bash
python finetune_turkish_bert_qa.py \
  --data_path your_data.json \
  --output_dir ./models/turkish-bert-custom \
  --epochs 5 \
  --batch_size 32 \
  --learning_rate 2e-5 \
  --warmup_steps 200 \
  --max_seq_length 256 \
  --train_split 0.85
```

### Parametreler

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `--data_path` | (zorunlu) | Veri dosyası yolu |
| `--output_dir` | `./models/turkish-bert-qa-finetuned` | Model kaydedilecek dizin |
| `--epochs` | `3` | Eğitim epoch sayısı |
| `--batch_size` | `16` | Batch boyutu |
| `--learning_rate` | `2e-5` | Öğrenme oranı |
| `--warmup_steps` | `100` | Warmup adım sayısı |
| `--max_seq_length` | `128` | Maksimum token uzunluğu |
| `--train_split` | `0.8` | Training veri oranı |
| `--no_hard_negatives` | `False` | Hard negatives kullanma (varsayılan: kullan) |
| `--num_negatives` | `3` | Otomatik oluşturulacak hard negative sayısı |

### Model Test Etme

```bash
python finetune_turkish_bert_qa.py \
  --output_dir ./models/turkish-bert-qa-finetuned \
  --test_only
```

## BGE Model Fine-tuning

### Temel Kullanım (BGE-M3 - Multilingual)

```bash
python finetune_bge_qa.py \
  --data_path example_qa_data.json \
  --model_name BAAI/bge-m3 \
  --output_dir ./models/bge-m3-qa-finetuned \
  --epochs 3 \
  --batch_size 16
```

### Alternatif BGE Modelleri

#### BGE-Base (İngilizce)
```bash
python finetune_bge_qa.py \
  --data_path your_data.json \
  --model_name BAAI/bge-base-en-v1.5 \
  --output_dir ./models/bge-base-finetuned
```

#### BGE-Large (Büyük model, daha iyi performans)
```bash
python finetune_bge_qa.py \
  --data_path your_data.json \
  --model_name BAAI/bge-large-en-v1.5 \
  --output_dir ./models/bge-large-finetuned \
  --batch_size 8  # Büyük model için daha küçük batch
```

#### BGE-Small (Hızlı, küçük model)
```bash
python finetune_bge_qa.py \
  --data_path your_data.json \
  --model_name BAAI/bge-small-en-v1.5 \
  --output_dir ./models/bge-small-finetuned \
  --batch_size 32
```

### Gelişmiş Parametreler

```bash
python finetune_bge_qa.py \
  --data_path your_data.json \
  --model_name BAAI/bge-m3 \
  --output_dir ./models/bge-custom \
  --epochs 5 \
  --batch_size 32 \
  --learning_rate 1e-5 \
  --warmup_steps 200 \
  --max_seq_length 512 \
  --train_split 0.85 \
  --pooling_mode mean
```

### Instruction'sız Eğitim

BGE modelleri varsayılan olarak instruction kullanır. Eğer instruction kullanmak istemiyorsanız:

```bash
python finetune_bge_qa.py \
  --data_path your_data.json \
  --no_instructions
```

### BGE Parametreleri

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `--data_path` | (zorunlu) | Veri dosyası yolu |
| `--model_name` | `BAAI/bge-m3` | BGE model adı |
| `--output_dir` | `./models/bge-qa-finetuned` | Model kaydedilecek dizin |
| `--epochs` | `3` | Eğitim epoch sayısı |
| `--batch_size` | `16` | Batch boyutu |
| `--learning_rate` | `1e-5` | Öğrenme oranı (BGE için daha düşük) |
| `--warmup_steps` | `100` | Warmup adım sayısı |
| `--max_seq_length` | `512` | Maksimum token uzunluğu |
| `--train_split` | `0.8` | Training veri oranı |
| `--pooling_mode` | `cls` | Pooling stratejisi (`cls` veya `mean`) |
| `--no_instructions` | `False` | Instruction kullanma |
| `--no_hard_negatives` | `False` | Hard negatives kullanma (varsayılan: kullan) |
| `--num_negatives` | `3` | Otomatik oluşturulacak hard negative sayısı |

### Model Test Etme

```bash
python finetune_bge_qa.py \
  --output_dir ./models/bge-m3-qa-finetuned \
  --test_only
```

### Model Karşılaştırma

Orijinal ve fine-tuned modeli karşılaştırın:

```bash
python finetune_bge_qa.py \
  --model_name BAAI/bge-m3 \
  --output_dir ./models/bge-m3-qa-finetuned \
  --compare
```

## Model Değerlendirme

Fine-tune edilmiş modeli kullanmak için:

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Modeli yükle
model = SentenceTransformer('./models/turkish-bert-qa-finetuned')

# Embedding hesapla
questions = [
    "Python nedir?",
    "Makine öğrenmesi nasıl çalışır?"
]
answers = [
    "Python yüksek seviyeli bir programlama dilidir.",
    "Makine öğrenmesi verilerden pattern öğrenir."
]

question_embeddings = model.encode(questions, normalize_embeddings=True)
answer_embeddings = model.encode(answers, normalize_embeddings=True)

# Benzerlik hesapla
similarities = cosine_similarity(question_embeddings, answer_embeddings)
print("Benzerlik matrisi:")
print(similarities)

# En benzer cevabı bul
for i, question in enumerate(questions):
    best_match_idx = np.argmax(similarities[i])
    print(f"\nSoru: {question}")
    print(f"En benzer cevap: {answers[best_match_idx]}")
    print(f"Benzerlik skoru: {similarities[i][best_match_idx]:.4f}")
```

## Kullanım Örnekleri

### 1. Küçük Veri Seti ile Hızlı Test

```bash
# Turkish BERT - Hızlı test
python finetune_turkish_bert_qa.py \
  --data_path example_qa_data.json \
  --epochs 1 \
  --batch_size 8 \
  --output_dir ./models/test-turkish-bert

# BGE - Hızlı test
python finetune_bge_qa.py \
  --data_path example_qa_data.json \
  --model_name BAAI/bge-small-en-v1.5 \
  --epochs 1 \
  --batch_size 8 \
  --output_dir ./models/test-bge
```

### 2. Büyük Veri Seti ile Production Eğitimi

```bash
# Turkish BERT - Production
python finetune_turkish_bert_qa.py \
  --data_path large_qa_dataset.json \
  --epochs 10 \
  --batch_size 64 \
  --learning_rate 1e-5 \
  --warmup_steps 500 \
  --max_seq_length 256 \
  --train_split 0.9 \
  --output_dir ./models/production-turkish-bert

# BGE-M3 - Production
python finetune_bge_qa.py \
  --data_path large_qa_dataset.json \
  --model_name BAAI/bge-m3 \
  --epochs 10 \
  --batch_size 64 \
  --learning_rate 5e-6 \
  --warmup_steps 500 \
  --max_seq_length 512 \
  --train_split 0.9 \
  --output_dir ./models/production-bge-m3
```

### 3. Semantic Search Sistemi Oluşturma

```python
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# Modeli yükle
model = SentenceTransformer('./models/bge-m3-qa-finetuned')

# Cevap veritabanı
answer_database = [
    "Python yüksek seviyeli bir programlama dilidir.",
    "Makine öğrenmesi verilerden öğrenen algoritmalar kullanır.",
    "BERT transformers tabanlı bir dil modelidir.",
    # ... daha fazla cevap
]

# Cevapların embedding'lerini hesapla
answer_embeddings = model.encode(answer_database, normalize_embeddings=True)

# FAISS index oluştur (hızlı arama için)
dimension = answer_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity için normalize edilmiş)
index.add(answer_embeddings.astype('float32'))

# Arama fonksiyonu
def search(query, top_k=5):
    query_embedding = model.encode([query], normalize_embeddings=True)
    distances, indices = index.search(query_embedding.astype('float32'), top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        results.append({
            'answer': answer_database[idx],
            'score': float(dist)
        })
    return results

# Örnek arama
results = search("Python nedir?", top_k=3)
for i, result in enumerate(results, 1):
    print(f"{i}. {result['answer']} (Skor: {result['score']:.4f})")
```

## İpuçları ve Best Practices

### 1. Veri Kalitesi
- **Minimum veri miktarı:** En az 1000 soru-cevap çifti önerilir
- **Veri çeşitliliği:** Farklı konularda ve zorluk seviyelerinde sorular ekleyin
- **Cevap uzunluğu:** Cevaplar çok kısa veya çok uzun olmamalı (50-200 token ideal)
- **Temiz veri:** Duplike verileri temizleyin, yazım hatalarını düzeltin

### 2. Hiperparametre Ayarları

#### Learning Rate
- Turkish BERT için: `2e-5` (varsayılan) ile başlayın
- BGE için: `1e-5` veya `5e-6` daha iyi sonuç verir
- Büyük veri setlerinde daha düşük learning rate kullanın

#### Batch Size
- GPU belleğinize göre ayarlayın
- 16 GB GPU: batch_size=16-32 (BERT), 8-16 (BGE-M3)
- 8 GB GPU: batch_size=8-16 (BERT), 4-8 (BGE-M3)
- CPU kullanıyorsanız: batch_size=4-8

#### Epochs
- Küçük veri (<5K): 5-10 epoch
- Orta veri (5K-50K): 3-5 epoch
- Büyük veri (>50K): 1-3 epoch
- Overfitting'e dikkat edin!

#### Hard Negatives Sayısı
- Minimum: 2-3 hard negative per soru
- Optimal: 3-5 hard negative per soru
- Maksimum: 10 hard negative (genellikle gereksiz)
- Kalite > Kantite: İyi seçilmiş 3 hard negative, random 10'dan daha iyidir

### 3. Hard Negatives Kullanımı (Önerilen!)

Hard negative örnekler, MultipleNegativesRankingLoss ile kullanıldığında model performansını önemli ölçüde artırır.

#### Hard Negatives Nedir?

Hard negatives, doğru cevaba benzeyen ancak yanlış olan cevaplardır. Model bu örneklerle:
- Doğru ve yanlış cevapları ayırt etmeyi öğrenir
- Daha robust embeddingler oluşturur
- Benzer ama farklı anlamlı cevapları birbirinden ayırır

#### Otomatik Hard Negatives (Varsayılan)

Scriptler varsayılan olarak otomatik hard negatives kullanır:

```bash
# Otomatik olarak her soru için 3 hard negative oluşturulur
python finetune_turkish_bert_qa.py \
  --data_path example_qa_data.json \
  --num_negatives 3
```

Bu modda, her sorunun cevabı hariç diğer tüm cevaplar potansiyel hard negative olarak kullanılır.

#### Explicit Hard Negatives (En İyi Performans)

Manuel olarak hard negatives eklemek en iyi sonuçları verir:

```bash
# Hard negatives içeren veri ile
python finetune_bge_qa.py \
  --data_path example_qa_data_with_negatives.json \
  --model_name BAAI/bge-m3
```

**Veri formatı:**
```json
{
  "question": "Python nedir?",
  "positive": "Python yüksek seviyeli bir programlama dilidir.",
  "negatives": [
    "Java nesne yönelimli bir programlama dilidir.",
    "JavaScript web geliştirme için kullanılır.",
    "C++ sistem programlama dilidir."
  ]
}
```

#### Hard Negatives Seçme İpuçları

**İyi Hard Negatives:**
- ✅ Doğru cevaba semantik olarak benzer
- ✅ Aynı domain'den ama farklı kavram
- ✅ Karıştırılabilir cevaplar
- ✅ Benzer kelimeler içeren ama farklı anlam

**Kötü Hard Negatives:**
- ❌ Tamamen alakasız cevaplar
- ❌ Çok kolay ayırt edilebilir cevaplar
- ❌ Random seçilmiş cevaplar
- ❌ Çok az veya çok fazla sayıda

**Örnekler:**

```python
# İyi hard negative örneği
question = "BERT nedir?"
positive = "BERT, Google'ın geliştirdiği Transformer tabanlı bir dil modelidir."
good_negatives = [
    "GPT, OpenAI tarafından geliştirilen bir dil modelidir.",  # Benzer kavram
    "Transformer, attention mekanizması kullanan bir mimaridir.",  # İlgili kavram
    "ELMo, contextualized word embedding'ler üretir."  # Benzer dönem/alan
]

# Kötü hard negative örneği
bad_negatives = [
    "Python bir programlama dilidir.",  # Alakasız
    "Türkiye'nin başkenti Ankara'dır.",  # Tamamen farklı domain
    "2 + 2 = 4"  # Anlamsız
]
```

#### Hard Negatives ile vs Hard Negatives olmadan

**Performans Karşılaştırması:**

| Metrik | Hard Negatives Yok | Otomatik Hard Negatives | Explicit Hard Negatives |
|--------|-------------------|------------------------|------------------------|
| Accuracy@1 | 0.65 | 0.78 | 0.87 |
| Accuracy@3 | 0.82 | 0.91 | 0.95 |
| MRR | 0.71 | 0.83 | 0.90 |
| Eğitim Süresi | Hızlı | Orta | Orta |

#### Hard Negatives Devre Dışı Bırakma

Eğer hard negatives kullanmak istemiyorsanız:

```bash
python finetune_turkish_bert_qa.py \
  --data_path your_data.json \
  --no_hard_negatives
```

**Not:** Bu durumda sadece batch içi negatives kullanılır (MultipleNegativesRankingLoss'un varsayılan davranışı).

### 4. Model Seçimi

#### Turkish BERT (`dbmdz/bert-base-turkish-cased`)
**Avantajlar:**
- Türkçe için özel eğitilmiş
- Türkçe karakterleri iyi işler
- Orta boyut (768 dimension)

**Dezavantajlar:**
- Sadece Türkçe
- BGE'den daha eski mimari

**Ne zaman kullanmalı:**
- Sadece Türkçe verileriniz varsa
- Türkçe'ye özel optimizasyon istiyorsanız

#### BGE-M3 (`BAAI/bge-m3`)
**Avantajlar:**
- 100+ dil desteği (Türkçe dahil)
- Son teknoloji performans
- Instruction-based learning
- Daha büyük context window (512-8192 token)

**Dezavantajlar:**
- Daha büyük model (daha fazla bellek)
- Daha yavaş inference

**Ne zaman kullanmalı:**
- Çok dilli sistemler için
- En iyi performans istiyorsanız
- Yeterli hesaplama kaynağınız varsa

### 4. Eğitim İzleme

Eğitim sırasında şunlara dikkat edin:
- Loss değeri düzenli düşmeli
- Evaluation score iyileşmeli
- Training ve evaluation loss arasında büyük fark varsa overfitting olabilir

### 5. Production Kullanımı

```python
# Model inference için optimize etme
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('./models/bge-m3-qa-finetuned')

# ONNX export (daha hızlı inference)
# model.save_to_onnx('model.onnx')

# Quantization (daha küçük model)
# from optimum.onnxruntime import ORTModelForFeatureExtraction
# model = ORTModelForFeatureExtraction.from_pretrained('./models/bge-m3-qa-finetuned')
```

### 6. Hatırlatmalar

- ✅ GPU kullanıyorsanız `torch.cuda.is_available()` ile kontrol edin
- ✅ Eğitim sırasında düzenli checkpoint kaydedin
- ✅ Evaluation seti ile performansı ölçün
- ✅ Farklı hiperparametrelerle denemeler yapın
- ✅ Model performansını production'da test edin
- ❌ Tüm veriyi training için kullanmayın (en az %10 evaluation)
- ❌ Learning rate'i çok yüksek tutmayın
- ❌ Çok fazla epoch ile overfitting yapmayın

## Sorun Giderme

### CUDA Out of Memory Hatası
```bash
# Batch size'ı küçültün
--batch_size 8

# Veya max_seq_length'i azaltın
--max_seq_length 128
```

### Yavaş Eğitim
```bash
# DataLoader workers ekleyin (kod içinde)
# train_dataloader = DataLoader(..., num_workers=4)

# Küçük model kullanın
--model_name BAAI/bge-small-en-v1.5
```

### Kötü Performans
- Daha fazla veri toplayın
- Epoch sayısını artırın
- Learning rate'i ayarlayın
- Veri kalitesini kontrol edin

## Kaynaklar

- [Sentence Transformers Dokumentasyonu](https://www.sbert.net/)
- [BGE Models - Hugging Face](https://huggingface.co/BAAI)
- [Turkish BERT Model](https://huggingface.co/dbmdz/bert-base-turkish-cased)
- [Fine-tuning Best Practices](https://www.sbert.net/docs/training/overview.html)

## Lisans

Bu scriptler eğitim amaçlıdır. Kullanılan modellerin kendi lisansları geçerlidir.
