# 🎭 DeepFabric Conversation Templates - Detaylı Rehber

## 📋 İçindekiler

1. [Tool Calling (Fonksiyon Çağırma)](#1-tool-calling-fonksiyon-çağırma)
2. [Chain of Thought (CoT)](#2-chain-of-thought-cot)
3. [Structured CoT](#3-structured-cot)
4. [Hybrid CoT](#4-hybrid-cot)
5. [Multi-Turn (Çok Turlu Konuşmalar)](#5-multi-turn-çok-turlu-konuşmalar)
6. [System-Prompted](#6-system-prompted)
7. [Single-Turn (Tek Tur)](#7-single-turn-tek-tur)
8. [Karşılaştırma ve Seçim Rehberi](#8-karşılaştırma-ve-seçim-rehberi)

---

## 1. Tool Calling (Fonksiyon Çağırma)

### 🎯 Ne İşe Yarar?

Model'e **API fonksiyonlarını nasıl çağıracağını** öğretir. Agent'ların dış dünya ile etkileşim kurmasını sağlar.

### 💡 Agent Training Değeri

- ✅ Doğru tool seçimi
- ✅ Parameter oluşturma
- ✅ Execution pattern'leri
- ✅ Error handling

### 📝 Format Özellikleri

```json
{
  "messages": [
    {"role": "user", "content": "Kullanıcı isteği"},
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_xyz",
          "type": "function",
          "function": {
            "name": "function_name",
            "arguments": "{\"param1\": \"value1\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_xyz",
      "content": "Tool'un döndürdüğü sonuç"
    },
    {"role": "assistant", "content": "Sonucun yorumlanması"}
  ]
}
```

### 🔥 Gerçek Örnekler

#### Örnek 1: Hava Durumu Sorgulama

```json
{
  "messages": [
    {
      "role": "user",
      "content": "İstanbul'da bugün hava nasıl? Şemsiye almalı mıyım?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_001",
          "type": "function",
          "function": {
            "name": "get_weather",
            "arguments": "{\"city\": \"Istanbul\", \"country\": \"Turkey\", \"units\": \"metric\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_001",
      "content": "{\"temperature\": 18, \"condition\": \"rainy\", \"humidity\": 85, \"precipitation_probability\": 80}"
    },
    {
      "role": "assistant",
      "content": "İstanbul'da bugün hava 18°C ve yağmurlu. Yağış ihtimali %80, nem oranı da yüksek (%85). Evet, kesinlikle şemsiye almanızı öneririm! ☔"
    }
  ]
}
```

#### Örnek 2: Çoklu Tool Kullanımı (Para Çevirme + Bilgi)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "100 USD kaç TL eder ve Türkiye'nin başkenti neresidir?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_002",
          "type": "function",
          "function": {
            "name": "convert_currency",
            "arguments": "{\"amount\": 100, \"from\": \"USD\", \"to\": \"TRY\"}"
          }
        },
        {
          "id": "call_003",
          "type": "function",
          "function": {
            "name": "get_country_info",
            "arguments": "{\"country\": \"Turkey\", \"info_type\": \"capital\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_002",
      "content": "{\"result\": 3415.50, \"rate\": 34.155, \"timestamp\": \"2024-11-09\"}"
    },
    {
      "role": "tool",
      "tool_call_id": "call_003",
      "content": "{\"country\": \"Turkey\", \"capital\": \"Ankara\", \"population\": \"5,700,000\"}"
    },
    {
      "role": "assistant",
      "content": "100 USD = 3,415.50 TL (kur: 34.16)\n\nTürkiye'nin başkenti Ankara'dır. Şehrin nüfusu yaklaşık 5.7 milyon kişidir."
    }
  ]
}
```

#### Örnek 3: Takvim Yönetimi

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Yarın saat 14:00'te Ahmet ile toplantı ayarla, 1 saat sürecek"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_004",
          "type": "function",
          "function": {
            "name": "create_calendar_event",
            "arguments": "{\"title\": \"Ahmet ile Toplantı\", \"date\": \"2024-11-10\", \"start_time\": \"14:00\", \"duration_minutes\": 60, \"participants\": [\"ahmet@example.com\"]}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_004",
      "content": "{\"status\": \"success\", \"event_id\": \"evt_789\", \"calendar_link\": \"https://calendar.app/evt_789\"}"
    },
    {
      "role": "assistant",
      "content": "Toplantı başarıyla oluşturuldu! ✅\n\n📅 Detaylar:\n- Kişi: Ahmet\n- Tarih: 10 Kasım 2024, Pazar\n- Saat: 14:00 - 15:00 (1 saat)\n- Event ID: evt_789\n\nKatılımcılara davet gönderildi."
    }
  ]
}
```

### 🎨 DeepFabric YAML Konfigürasyonu

```yaml
# tool_calling_config.yaml
dataset_system_prompt: "Sen bir API asistanısın. Kullanıcı isteklerini fonksiyonlara çevirirsin."

topic_tree:
  topic_prompt: |
    API Kullanım Senaryoları:
    - Hava durumu servisleri
    - Çeviri ve dil işlemleri
    - Takvim ve zaman yönetimi
    - Dosya işlemleri
    - Veri tabanı sorguları
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  degree: 3
  depth: 2

data_engine:
  conversation_type: "tool_calling"  # 🔑 Önemli!
  generation_system_prompt: |
    Her senaryo için:
    1. Kullanıcı isteğini anla
    2. Doğru fonksiyonu/fonksiyonları seç
    3. Parametreleri çıkar
    4. JSON formatında tool_calls oluştur
    5. Tool sonucunu yorumla
  
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.4  # Düşük = doğru çağrılar

dataset:
  creation:
    num_steps: 100
  save_as: "tool_calling_dataset.jsonl"
```

---

## 2. Chain of Thought (CoT)

### 🎯 Ne İşe Yarar?

Model'e **adım adım düşünmeyi** öğretir. Karmaşık problemleri parçalara ayırıp çözer.

### 💡 Agent Training Değeri

- ✅ Şeffaf karar verme
- ✅ Karmaşık multi-step tasklar
- ✅ Hata ayıklama kolaylığı
- ✅ Reasoning kalitesi

### 📝 Format Özellikleri

```json
{
  "messages": [
    {"role": "user", "content": "Problem"},
    {
      "role": "assistant",
      "content": "Adım 1: ...\nAdım 2: ...\nAdım 3: ...\nSonuç: ..."
    }
  ]
}
```

### 🔥 Gerçek Örnekler

#### Örnek 1: Matematik Problemi

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Bir mağaza %30 indirim yapıyor. 850 TL'lik bir ürünü %30 indirimden sonra 12 ay taksitle alırsam aylık ne kadar öderim?"
    },
    {
      "role": "assistant",
      "content": "Bu problemi adım adım çözelim:\n\n**Adım 1: İndirimli fiyatı hesapla**\nOrijinal fiyat: 850 TL\nİndirim oranı: %30\nİndirim tutarı = 850 × 0.30 = 255 TL\n\n**Adım 2: İndirimli fiyatı bul**\nİndirimli fiyat = 850 - 255 = 595 TL\n\n**Adım 3: Aylık taksit tutarını hesapla**\nToplam tutar: 595 TL\nTaksit sayısı: 12 ay\nAylık ödeme = 595 ÷ 12 = 49.58 TL\n\n**Sonuç:**\nAylık 49.58 TL (yaklaşık 50 TL) ödeyeceksiniz.\n\n✅ Doğrulama: 49.58 × 12 = 594.96 ≈ 595 TL"
    }
  ]
}
```

#### Örnek 2: Algoritma Problemi

```json
{
  "messages": [
    {
      "role": "user",
      "content": "[5, 2, 8, 1, 9] dizisini Binary Search Tree'ye eklemek için hangi sırayla işlem yapmalıyım?"
    },
    {
      "role": "assistant",
      "content": "Binary Search Tree (BST) oluşturma adımlarını inceleyelim:\n\n**Adım 1: Root'u belirle**\nİlk eleman (5) root olur.\n```\n    5\n```\n\n**Adım 2: 2'yi ekle**\n2 < 5 → Sol tarafa git\n```\n    5\n   /\n  2\n```\n\n**Adım 3: 8'i ekle**\n8 > 5 → Sağ tarafa git\n```\n    5\n   / \\\n  2   8\n```\n\n**Adım 4: 1'i ekle**\n1 < 5 → Sol\n1 < 2 → Sol\n```\n    5\n   / \\\n  2   8\n /\n1\n```\n\n**Adım 5: 9'u ekle**\n9 > 5 → Sağ\n9 > 8 → Sağ\n```\n    5\n   / \\\n  2   8\n /     \\\n1       9\n```\n\n**Sonuç:**\nFinal BST yapısı oluşturuldu. In-order traversal: [1, 2, 5, 8, 9] (sıralı)"
    }
  ]
}
```

#### Örnek 3: Mantık Problemi

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Ayşe, Mehmet'ten 5 yaş büyük. Mehmet, Zeynep'ten 3 yaş küçük. Zeynep 25 yaşında. Ayşe kaç yaşında?"
    },
    {
      "role": "assistant",
      "content": "Bu problem için adım adım ilerleyelim:\n\n**Verilen Bilgiler:**\n- Ayşe = Mehmet + 5\n- Mehmet = Zeynep - 3\n- Zeynep = 25\n\n**Adım 1: Mehmet'in yaşını bul**\nMehmet = Zeynep - 3\nMehmet = 25 - 3 = 22 yaşında\n\n**Adım 2: Ayşe'nin yaşını bul**\nAyşe = Mehmet + 5\nAyşe = 22 + 5 = 27 yaşında\n\n**Doğrulama:**\n- Zeynep: 25 ✓\n- Mehmet: 22 (Zeynep'ten 3 küçük) ✓\n- Ayşe: 27 (Mehmet'ten 5 büyük) ✓\n\n**Sonuç:**\nAyşe 27 yaşındadır."
    }
  ]
}
```

### 🎨 DeepFabric YAML Konfigürasyonu

```yaml
# cot_config.yaml
dataset_system_prompt: "Sen bir problem çözme uzmanısın. Her problemi adım adım çözersin."

topic_tree:
  topic_prompt: |
    Problem Çözme Alanları:
    - Matematik ve aritmetik
    - Algoritma tasarımı
    - Mantık problemleri
    - Kod debugging
    - Optimizasyon
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  temperature: 0.7
  degree: 3
  depth: 2

data_engine:
  conversation_type: "chain_of_thought"  # 🔑 Önemli!
  generation_system_prompt: |
    Her problem için ZORUNLU format:
    
    Adım 1: [İlk işlem]
    [Açıklama ve hesaplama]
    
    Adım 2: [İkinci işlem]
    [Açıklama ve hesaplama]
    
    ...
    
    Sonuç: [Final cevap]
    ✅ Doğrulama: [Kontrol]
  
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  temperature: 0.5

dataset:
  creation:
    num_steps: 150
  save_as: "cot_dataset.jsonl"
```

---

## 3. Structured CoT

### 🎯 Ne İşe Yarar?

Chain of Thought'un **daha yapılandırılmış** versiyonu. Her adım explicit (açık) olarak işaretlenmiş.

### 💡 Agent Training Değeri

- ✅ **Auditing kolaylığı** (her adım izlenebilir)
- ✅ **Debugging** (hangi adımda hata var belli)
- ✅ **Reasoning paths** net
- ✅ Agent'ın düşünce sürecini anlama

### 📝 Format Özellikleri

```json
{
  "messages": [
    {"role": "user", "content": "Problem"},
    {
      "role": "assistant",
      "content": {
        "reasoning_steps": [
          {"step": 1, "action": "...", "result": "..."},
          {"step": 2, "action": "...", "result": "..."}
        ],
        "final_answer": "..."
      }
    }
  ]
}
```

### 🔥 Gerçek Örnekler

#### Örnek 1: Kod Debug (Yapılandırılmış)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Bu Python kodunda hata var, düzelt:\n```python\ndef calculate_average(numbers):\n    total = 0\n    for num in numbers:\n        total += num\n    return total / len(numbers)\n\nresult = calculate_average([])\nprint(result)\n```"
    },
    {
      "role": "assistant",
      "content": "**Structured Reasoning:**\n\n```json\n{\n  \"problem_analysis\": {\n    \"identified_issue\": \"Division by zero error\",\n    \"line\": 5,\n    \"error_type\": \"ZeroDivisionError\"\n  },\n  \"reasoning_steps\": [\n    {\n      \"step\": 1,\n      \"action\": \"Analyze function behavior\",\n      \"observation\": \"Function attempts to divide by len(numbers)\",\n      \"issue\": \"When numbers=[], len(numbers)=0, causes division by zero\"\n    },\n    {\n      \"step\": 2,\n      \"action\": \"Identify edge cases\",\n      \"cases\": [\n        \"Empty list\",\n        \"Single element\",\n        \"Multiple elements\"\n      ],\n      \"problematic_case\": \"Empty list\"\n    },\n    {\n      \"step\": 3,\n      \"action\": \"Design solution\",\n      \"approach\": \"Add input validation before calculation\",\n      \"implementation\": \"Check if list is empty, return appropriate value or raise error\"\n    }\n  ],\n  \"solution\": {\n    \"option_1\": \"Return 0 for empty list\",\n    \"option_2\": \"Return None for empty list\",\n    \"option_3\": \"Raise ValueError\",\n    \"recommended\": \"option_2 (None)\"\n  },\n  \"fixed_code\": \"def calculate_average(numbers):\\n    if not numbers:\\n        return None\\n    total = 0\\n    for num in numbers:\\n        total += num\\n    return total / len(numbers)\",\n  \"verification\": {\n    \"test_case_1\": \"calculate_average([]) → None ✓\",\n    \"test_case_2\": \"calculate_average([5]) → 5.0 ✓\",\n    \"test_case_3\": \"calculate_average([1,2,3]) → 2.0 ✓\"\n  }\n}\n```\n\n**Fixed Code:**\n```python\ndef calculate_average(numbers):\n    if not numbers:  # Handle empty list\n        return None\n    \n    total = 0\n    for num in numbers:\n        total += num\n    return total / len(numbers)\n\nresult = calculate_average([])\nprint(result)  # Output: None\n```"
    }
  ]
}
```

#### Örnek 2: İş Kararı (Yapılandırılmış)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Şirketimiz yeni bir ürün lansmanı yapacak. 100K bütçemiz var. TV reklamı mı, sosyal medya mı, yoksa influencer marketing mi yapmalıyız?"
    },
    {
      "role": "assistant",
      "content": "**Structured Decision Framework:**\n\n```json\n{\n  \"decision_framework\": {\n    \"budget\": \"100,000 TL\",\n    \"goal\": \"Yeni ürün lansmanı\",\n    \"options\": [\"TV Reklamı\", \"Sosyal Medya\", \"Influencer Marketing\"]\n  },\n  \n  \"analysis_steps\": [\n    {\n      \"step\": 1,\n      \"phase\": \"Option Analysis\",\n      \"evaluations\": [\n        {\n          \"option\": \"TV Reklamı\",\n          \"pros\": [\"Geniş reach\", \"Marka kredibilitesi\", \"Yaşlı demografiye erişim\"],\n          \"cons\": [\"Çok pahalı (100K yeterli değil)\", \"Ölçümleme zor\", \"Genç demografiye ulaşamaz\"],\n          \"estimated_cost\": \"150K-500K TL\",\n          \"roi_potential\": \"Orta\",\n          \"feasibility\": \"Düşük (bütçe yetersiz)\"\n        },\n        {\n          \"option\": \"Sosyal Medya Ads\",\n          \"pros\": [\"Hedefe yönelik\", \"Ölçümlenebilir\", \"Esnek bütçe\", \"A/B test\"],\n          \"cons\": [\"Rekabet yoğun\", \"Ad fatigue\", \"Organic reach düşük\"],\n          \"estimated_cost\": \"50K-100K TL\",\n          \"roi_potential\": \"Yüksek\",\n          \"feasibility\": \"Yüksek\"\n        },\n        {\n          \"option\": \"Influencer Marketing\",\n          \"pros\": [\"Güven faktörü\", \"Engaged audience\", \"Authentic content\"],\n          \"cons\": [\"Influencer seçimi kritik\", \"Fake followers riski\", \"ROI belirsiz\"],\n          \"estimated_cost\": \"30K-80K TL (influencer tier'e göre)\",\n          \"roi_potential\": \"Orta-Yüksek\",\n          \"feasibility\": \"Yüksek\"\n        }\n      ]\n    },\n    {\n      \"step\": 2,\n      \"phase\": \"Scoring Matrix\",\n      \"criteria\": {\n        \"reach\": {\"weight\": 0.25},\n        \"targeting\": {\"weight\": 0.30},\n        \"measurability\": {\"weight\": 0.20},\n        \"budget_fit\": {\"weight\": 0.25}\n      },\n      \"scores\": [\n        {\n          \"option\": \"TV\",\n          \"scores\": {\"reach\": 9, \"targeting\": 3, \"measurability\": 4, \"budget_fit\": 2},\n          \"weighted_total\": 4.25\n        },\n        {\n          \"option\": \"Social Media\",\n          \"scores\": {\"reach\": 7, \"targeting\": 9, \"measurability\": 10, \"budget_fit\": 9},\n          \"weighted_total\": 8.75\n        },\n        {\n          \"option\": \"Influencer\",\n          \"scores\": {\"reach\": 6, \"targeting\": 8, \"measurability\": 6, \"budget_fit\": 8},\n          \"weighted_total\": 7.10\n        }\n      ]\n    },\n    {\n      \"step\": 3,\n      \"phase\": \"Risk Assessment\",\n      \"risk_analysis\": [\n        {\n          \"option\": \"Social Media\",\n          \"risks\": [\n            {\"risk\": \"Ad account ban\", \"probability\": \"Low\", \"impact\": \"High\", \"mitigation\": \"Diversify platforms\"},\n            {\"risk\": \"Low conversion\", \"probability\": \"Medium\", \"impact\": \"Medium\", \"mitigation\": \"A/B testing, optimization\"}\n          ]\n        },\n        {\n          \"option\": \"Influencer\",\n          \"risks\": [\n            {\"risk\": \"Influencer scandal\", \"probability\": \"Low\", \"impact\": \"High\", \"mitigation\": \"Thorough vetting\"},\n            {\"risk\": \"Low engagement\", \"probability\": \"Medium\", \"impact\": \"High\", \"mitigation\": \"Micro-influencer mix\"}\n          ]\n        }\n      ]\n    }\n  ],\n  \n  \"recommendation\": {\n    \"primary_choice\": \"Sosyal Medya (70K TL)\",\n    \"secondary_choice\": \"Influencer Marketing (30K TL)\",\n    \"strategy\": \"Hybrid Approach\",\n    \"budget_allocation\": {\n      \"facebook_instagram_ads\": \"40K TL\",\n      \"google_ads\": \"20K TL\",\n      \"linkedin_ads\": \"10K TL\",\n      \"micro_influencers\": \"25K TL (5 influencer, 5K each)\",\n      \"content_creation\": \"5K TL\"\n    },\n    \"rationale\": [\n      \"Sosyal medya highest scoring (8.75) with excellent targeting and measurability\",\n      \"Influencer marketing adds authenticity and trust\",\n      \"Hybrid approach minimizes risk through diversification\",\n      \"Budget allows for comprehensive A/B testing and optimization\",\n      \"All options fit within 100K budget\"\n    ]\n  },\n  \n  \"implementation_timeline\": {\n    \"week_1\": \"Campaign setup, influencer outreach\",\n    \"week_2-3\": \"Content creation, ad creative\",\n    \"week_4-8\": \"Campaign execution, daily monitoring\",\n    \"week_9-12\": \"Optimization based on data, scaling winners\"\n  },\n  \n  \"kpis\": [\n    \"Cost per acquisition (CPA) < 50 TL\",\n    \"Return on ad spend (ROAS) > 3x\",\n    \"Reach: 500K+ unique users\",\n    \"Conversions: 2000+ sales\",\n    \"Engagement rate: >3%\"\n  ]\n}\n```\n\n**Final Recommendation:**\n🎯 **Hybrid Strategy: 70% Sosyal Medya + 30% Influencer Marketing**\n\nBu yaklaşım:\n✅ Bütçe içinde (100K TL)\n✅ Ölçümlenebilir (data-driven)\n✅ Esnek (optimize edilebilir)\n✅ Risk çeşitlendirmesi\n✅ Geniş + hedefe yönelik reach"
    }
  ]
}
```

### 🎨 DeepFabric YAML Konfigürasyonu

```yaml
# structured_cot_config.yaml
dataset_system_prompt: "Sen bir karar destek sistemisin. Her kararı yapılandırılmış şekilde analiz edersin."

topic_tree:
  topic_prompt: |
    Yapılandırılmış Karar Verme Alanları:
    - İş stratejileri ve planning
    - Teknik problem çözme
    - Kod debugging ve optimization
    - Risk analizi
    - Sistemik problemler
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  temperature: 0.7
  degree: 3
  depth: 2

data_engine:
  conversation_type: "chain_of_thought"  # Base type
  generation_system_prompt: |
    STRUCTURED CoT formatı:
    
    Her problem için JSON structured format kullan:
    {
      "problem_analysis": {...},
      "reasoning_steps": [
        {
          "step": 1,
          "action": "...",
          "observation": "...",
          "result": "..."
        }
      ],
      "decision_matrix": {...},
      "recommendation": {...},
      "verification": {...}
    }
    
    Her adım izlenebilir ve debuglanabilir olmalı.
  
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  temperature: 0.4

dataset:
  creation:
    num_steps: 100
  save_as: "structured_cot_dataset.jsonl"
```

---

## 4. Hybrid CoT

### 🎯 Ne İşe Yarar?

**Sezgisel (intuitive) ve analitik (analytical) düşünceyi** birleştirir. Bazen hızlı düşünme, bazen derin analiz gerekir.

### 💡 Agent Training Değeri

- ✅ **Adaptive thinking** (duruma göre düşünme tarzı)
- ✅ **Esnek problem solving**
- ✅ **Hızlı + derinlemesine düşünme dengesi**
- ✅ Real-world scenarios için ideal

### 📝 Format Özellikleri

Bazen kısa, bazen uzun reasoning. Duruma göre adapte oluyor.

### 🔥 Gerçek Örnekler

#### Örnek 1: Basit Soru (Sezgisel)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Python'da bir listeyi nasıl tersine çeviririm?"
    },
    {
      "role": "assistant",
      "content": "**Quick Answer (Sezgisel):**\n\n3 yaygın yöntem:\n\n1. **Slicing** (En pythonic):\n```python\nmy_list = [1, 2, 3, 4]\nreversed_list = my_list[::-1]\n```\n\n2. **reverse() metodu** (In-place):\n```python\nmy_list.reverse()\n```\n\n3. **reversed() fonksiyonu** (Iterator):\n```python\nreversed_list = list(reversed(my_list))\n```\n\n💡 Önerim: Slicing kullan, en okunabilir ve hızlı."
    }
  ]
}
```

#### Örnek 2: Karmaşık Soru (Analitik)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "1 milyon elemanlı bir listeyi tersine çevirmem gerekiyor. Performans kritik. Hangi yöntemi kullanmalıyım ve neden?"
    },
    {
      "role": "assistant",
      "content": "**Deep Analysis (Analitik):**\n\nBu durumda performans kritik, detaylı analiz yapalım:\n\n**Adım 1: Yöntemleri Karşılaştır**\n\n```python\nimport timeit\n\ntest_list = list(range(1000000))\n\n# Method 1: Slicing\nt1 = timeit.timeit(lambda: test_list[::-1], number=100)\n\n# Method 2: reverse() (in-place)\nt2 = timeit.timeit(lambda: test_list.reverse(), number=100)\n\n# Method 3: reversed()\nt3 = timeit.timeit(lambda: list(reversed(test_list)), number=100)\n```\n\n**Adım 2: Performans Sonuçları**\n- Slicing: ~12ms (yeni liste oluşturur, O(n) time, O(n) space)\n- reverse(): ~0.05ms (in-place, O(n) time, O(1) space) ⚡\n- reversed(): ~15ms (iterator + list conversion)\n\n**Adım 3: Memory Analizi**\n```python\nimport sys\n\noriginal_size = sys.getsizeof(test_list)  # ~8MB\n\n# Slicing: 8MB orijinal + 8MB yeni = 16MB\n# reverse(): 8MB (değişiklik in-place)\n# reversed(): 8MB orijinal + iterator overhead + 8MB list\n```\n\n**Adım 4: Karar Matrisi**\n\n| Method | Speed | Memory | Use Case |\n|--------|-------|--------|----------|\n| Slicing | Orta | 2x | Orijinali koru |\n| reverse() | **En hızlı** | **1x** | **Memory kritik** ✅ |\n| reversed() | Yavaş | 2x+ | Iterator gerek |\n\n**Sonuç ve Öneri:**\n\n✅ **reverse() metodunu kullan**\n\n**Gerekçe:**\n1. **240x daha hızlı** (0.05ms vs 12ms)\n2. **%50 daha az memory** (O(1) vs O(n))\n3. 1M eleman için 8MB tasarruf\n4. In-place işlem → GC overhead yok\n\n**Implementation:**\n```python\ndef reverse_large_list(large_list):\n    \"\"\"Performans-odaklı liste tersine çevirme\"\"\"\n    large_list.reverse()  # In-place, O(n) time, O(1) space\n    return large_list  # Return for chaining\n\n# Kullanım\nmy_large_list = list(range(1000000))\nreverse_large_list(my_large_list)\n```\n\n⚠️ **Uyarı:** Eğer orijinal listeyi koruman gerekiyorsa:\n```python\noriginal_preserved = my_list.copy()\noriginal_preserved.reverse()\n```\n\nBu durumda memory 2x olur ama yine de slicing'den hızlıdır."
    }
  ]
}
```

#### Örnek 3: Hybrid (İkisi Karışık)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "E-ticaret sitemde ürün önerisi yapmak istiyorum. Collaborative filtering mi content-based mi kullanmalıyım?"
    },
    {
      "role": "assistant",
      "content": "**Hybrid Reasoning:**\n\n**🚀 Quick Intuition:**\nİkisi de kullan! Hybrid recommendation system en iyisi.\n\n**📊 Deep Analysis (Neden Hybrid?):**\n\n**Adım 1: Her Yöntemin Güçlü/Zayıf Yönleri**\n\n*Collaborative Filtering:*\n- ✅ Sürpriz keşifler\n- ✅ User behavior'e dayalı\n- ❌ Cold start problemi (yeni user/ürün)\n- ❌ Sparsity (az veri = kötü öneri)\n\n*Content-Based:*\n- ✅ Cold start yok\n- ✅ Açıklanabilir (\"Bu ürün X'e benziyor\")\n- ❌ Filter bubble (hep aynı tip ürün)\n- ❌ Sürpriz yok\n\n**Adım 2: Hybrid Stratejisi**\n\n```python\ndef hybrid_recommendation(user_id, item_id):\n    # Kullanıcı profili kontrol et\n    user_history = get_user_history(user_id)\n    \n    if len(user_history) < 5:  # Yeni kullanıcı\n        # Content-based ağırlıklı (70/30)\n        score = (\n            0.7 * content_based_score(user_id, item_id) +\n            0.3 * collaborative_score(user_id, item_id)\n        )\n    else:  # Aktif kullanıcı\n        # Collaborative ağırlıklı (60/40)\n        score = (\n            0.6 * collaborative_score(user_id, item_id) +\n            0.4 * content_based_score(user_id, item_id)\n        )\n    \n    return score\n```\n\n**Sonuç:**\n✅ **Hybrid sistem (60-40 veya 70-30)**\n- Yeni kullanıcılar: Content-based ağır\n- Eski kullanıcılar: Collaborative ağır\n- Her zaman ikisinin blend'i\n\n💡 Bonus: Matrix factorization (SVD) ekle → %15-20 accuracy artışı"
    }
  ]
}
```

### 🎨 DeepFabric YAML Konfigürasyonu

```yaml
# hybrid_cot_config.yaml
dataset_system_prompt: |
  Sen adaptif bir problem solver'sın. Bazı sorulara hızlı cevap ver,
  bazılarını derin analiz et. Duruma göre karar ver.

topic_tree:
  topic_prompt: |
    Çeşitli Karmaşıklıkta Problemler:
    - Basit teknik sorular
    - Karmaşık optimizasyon problemleri
    - Hybrid stratejiler
    - Karar verme senaryoları
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  temperature: 0.8  # Yüksek = çeşitli complexity
  degree: 4
  depth: 2

data_engine:
  conversation_type: "chain_of_thought"
  generation_system_prompt: |
    HYBRID CoT formatı:
    
    Sorunun karmaşıklığına göre karar ver:
    
    **Basit/Açık sorular:**
    - Kısa, sezgisel cevap
    - Direkt çözüm
    - Örnek kod
    
    **Karmaşık/Belirsiz sorular:**
    - Detaylı adım adım analiz
    - Alternatifleri değerlendir
    - Trade-off'ları tartış
    - Veri/benchmark göster
    
    **Hybrid sorular:**
    - Quick answer + deep dive
    - Sezgi + analiz
    - Pratik + teori
  
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  temperature: 0.6

dataset:
  creation:
    num_steps: 200
  save_as: "hybrid_cot_dataset.jsonl"
```

---

## 5. Multi-Turn (Çok Turlu Konuşmalar)

### 🎯 Ne İşe Yarar?

**Context retention** ve **multi-step planning**. Agent uzun konuşmaları takip eder.

### 💡 Agent Training Değeri

- ✅ **Context tracking** (önceki mesajları hatırla)
- ✅ **Long-term planning**
- ✅ **Conversation flow**
- ✅ **User intent understanding**

### 📝 Format Özellikleri

3+ tur konuşma, her tur context'i genişletir.

### 🔥 Gerçek Örnekler

#### Örnek 1: Seyahat Planlama

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Yaz tatili için bir şehir önerisi alabilir miyim?"
    },
    {
      "role": "assistant",
      "content": "Tabii! Size yardımcı olmak için birkaç soru sorayım:\n\n1. Hangi bölgeyi tercih edersiniz? (Türkiye içi, Avrupa, Asya...)\n2. Bütçeniz ne kadar?\n3. Deniz mi, kültür turu mu, doğa mı?\n4. Kaç günlük bir tatil planlıyorsunuz?"
    },
    {
      "role": "user",
      "content": "Avrupa'yı düşünüyorum, 7-10 gün arası, bütçe 15-20K TL civarı. Hem deniz hem kültür olursa süper olur."
    },
    {
      "role": "assistant",
      "content": "Harika! Bu kriterlere göre size **3 şehir** öneriyorum:\n\n**1. Barcelona, İspanya** ⭐ En uygun\n- ✅ Hem sahil hem kültür\n- ✅ Bütçe içinde (~18K TL)\n- 🏖️ Barceloneta plajı\n- 🏛️ Sagrada Familia, Park Güell\n- 🍷 Tapas + sangria kültürü\n\n**2. Dubrovnik, Hırvatistan**\n- ✅ Adriyatik kıyısı\n- ✅ Daha ekonomik (~15K TL)\n- 🏰 Game of Thrones çekim yeri\n\n**3. Atina + Adalar, Yunanistan**\n- ✅ Antik tarih + Ege denizi\n- ✅ Bütçe dostu (~16K TL)\n- 🏛️ Akropolis, Parthenon\n- 🏝️ Mykonos, Santorini (ilave gün)\n\nHangisi daha çok ilginizi çekti?"
    },
    {
      "role": "user",
      "content": "Barcelona çok iyi durdu! Ama 7 gün Barcelona'da mı kalmalıyım, yoksa yakın başka şehirlere de gidebilir miyim?"
    },
    {
      "role": "assistant",
      "content": "Mükemmel soru! **7 günü split etmenizi** öneririm:\n\n**📅 Önerilen İtinerari:**\n\n**Barcelona (4 gün)**\n- Gün 1: Sagrada Familia + Gotik Mahalle\n- Gün 2: Park Güell + Gracia semti\n- Gün 3: Plaj günü (Barceloneta) + La Rambla\n- Gün 4: Casa Batlló + Montjuïc\n\n**+ Valencia (2 gün)** 🚄\n- High-speed train: 3 saat, ~€30\n- City of Arts and Sciences\n- Paella'nın doğduğu yer!\n- Daha ucuz ve az turist\n\n**+ Girona (1 gün)** 🚂\n- Tren: 1.5 saat, €15\n- Ortaçağ şehri\n- Game of Thrones çekim yeri\n- Günübirlik tur\n\n**💰 Revize Bütçe:**\n- Uçak: €250 (gidiş-dönüş)\n- Konaklama: €600 (7 gece, orta segment)\n- Ulaşım: €150 (şehir içi + şehirler arası)\n- Yemek: €350\n- Aktivite/müze: €150\n- **Toplam: ~€1500 (≈18K TL)** ✅\n\nİsterseniz detaylı günlük plan yapabilirim!"
    },
    {
      "role": "user",
      "content": "Süper! Peki konaklama için hangi bölgelerde otel bakmalıyım?"
    },
    {
      "role": "assistant",
      "content": "Barcelona'da konaklama için **3 ideal bölge:**\n\n**1. Eixample** ⭐ En önerdiğim\n- 📍 Merkezi konum\n- 🚇 Metro erişimi mükemmel\n- 🏛️ Sagrada Familia yürüme mesafesinde\n- 💰 Orta segment: €80-120/gece\n- ✅ Güvenli, turistik ama local vibe da var\n- Örnek oteller: Hotel Jazz, Hotel Constanza\n\n**2. Gotik Mahalle (Barri Gòtic)**\n- 📍 Tam merkezde\n- 🏰 Tarihi atmosfer\n- 🌃 Gece hayatı canlı\n- 💰 Biraz daha pahalı: €100-150/gece\n- ⚠️ Bazı sokaklar gürültülü olabilir\n\n**3. Gracia**\n- 📍 Park Güell yakını\n- 🎨 Bohemian vibe\n- 💰 Ekonomik: €60-100/gece\n- ✅ Local deneyim\n- ⚠️ Merkeze 20 dk metro\n\n**Valencia için:**\n- **Ciutat Vella** (Old Town) → €50-70/gece\n- Modern oteller, denize yakın\n\n**💡 Rezervasyon ipuçları:**\n1. Booking.com'da \"free cancellation\" seç\n2. Eixample'da **Passeig de Gràcia** yakını tercih et\n3. En az 2 hafta önceden rezervasyon yap\n4. Airbnb yerine otel (daha güvenli + temizlik)\n\nHazır miyız? İsterseniz uçak biletleri için de yardımcı olabilirim! ✈️"
    }
  ]
}
```

#### Örnek 2: Teknik Support (5 Tur)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Bilgisayarım çok yavaş çalışıyor, ne yapabilirim?"
    },
    {
      "role": "assistant",
      "content": "Yavaşlık sorununu çözelim! Önce birkaç temel kontrol yapalım:\n\n**Hızlı Kontroller:**\n1. Bilgisayar ne kadar süredir açık? (Restart denediniz mi?)\n2. Hangi programlar arka planda çalışıyor?\n3. Disk doluluk oranı nedir? (C: sürücüsü)\n4. İşletim sistemi: Windows mi, Mac mi?\n\nBu bilgileri verirseniz daha hedefli yardımcı olabilirim."
    },
    {
      "role": "user",
      "content": "Windows 10 kullanıyorum. Bilgisayar 3 gündür açık, restart yapmadım. Disk %85 dolu. Arka planda Chrome var (30 sekme açık) ve Steam çalışıyor."
    },
    {
      "role": "assistant",
      "content": "Sorunun kaynağını buldum! **3 ana problem** var:\n\n**Problem 1: 3 günlük uptime**\n❌ Windows'un memory leak'leri var\n✅ **Çözüm:** Hemen restart atın\n\n**Problem 2: Chrome 30 sekme**\n❌ Her sekme ~200MB RAM kullanır\n❌ 30 sekme = ~6GB RAM\n✅ **Çözüm:** \n- Gereksiz sekmeleri kapatın\n- \"The Great Suspender\" extension kullanın\n- Alternatif: Brave/Edge browser (daha az RAM)\n\n**Problem 3: Disk %85 dolu**\n❌ Windows %80 üstünde swap file kullanır (çok yavaş)\n✅ **Çözüm:** Disk temizliği yapın\n\n**Hemen Yapılacaklar:**\n\n1. **Restart** (en önemli)\n2. Chrome sekmelerini azaltın (max 10)\n3. Steam'i kapatın (otomatik başlangıçtan kaldırın)\n4. Disk temizliği:\n   - Windows Disk Cleanup çalıştırın\n   - Temp dosyaları silin\n   - Eski Windows Update dosyaları silin\n\nBunları yaptıktan sonra durum nasıl? Sorun devam ederse daha detaylı bakalım."
    },
    {
      "role": "user",
      "content": "Restart attım, Chrome'u kapattım. Biraz daha iyi ama hala yavaş. Task Manager'da CPU %70-80 arası seyrediyor sürekli."
    },
    {
      "role": "assistant",
      "content": "İyi ilerleme! Şimdi **CPU kullanımına** bakalım.\n\n**Task Manager'ı detaylı inceleyelim:**\n\n1. Task Manager'ı açın (Ctrl + Shift + Esc)\n2. \"Processes\" sekmesine gidin\n3. \"CPU\" sütununa tıklayın (yüksekten düşüğe sıralansın)\n\n**En üstteki 3-4 process'i** bana yazabilir misiniz?\nŞu formatta:\n- Process adı - CPU kullanımı %\n\nÖrnek:\n- Chrome.exe - 45%\n- Windows Defender - 20%\n\nBu bilgiyle hangi program yavaşlattığını bulacağız."
    },
    {
      "role": "user",
      "content": "İşte liste:\n- Antimalware Service Executable - 55%\n- System - 15%\n- Windows Modules Installer Worker - 10%\n- RuntimeBroker.exe - 8%"
    },
    {
      "role": "assistant",
      "content": "**Bulduk! \"Antimalware Service Executable\" = Windows Defender**\n\nBu %55 CPU kullanımı **anormal**. İki olasılık:\n\n**Senaryo 1: Full Scan Yapıyor**\n✅ Normal durum, bitince düzelir\n❓ Ne kadar süredir yüksek? (1 saat+)\n\n**Senaryo 2: Bir Dosya/Klasör Takılmış**\n❌ Sürekli aynı dosyayı taramaya çalışıyor\n\n**Hemen Çözüm:**\n\n**1. Defender'ı geçici durdur:**\n```\n1. Settings → Update & Security → Windows Security\n2. Virus & threat protection\n3. \"Manage settings\"\n4. \"Real-time protection\" → OFF (geçici)\n```\n\n**2. Scan durumunu kontrol et:**\n```\n1. Windows Security açın\n2. \"Virus & threat protection\"\n3. \"Scan options\"\n4. Eğer \"Full scan\" çalışıyorsa → \"Cancel\"\n```\n\n**3. Defender'a exception ekle** (büyük klasörler için):\n```\n1. Settings → Windows Security\n2. Virus & threat protection settings\n3. \"Add or remove exclusions\"\n4. Şu klasörleri ekleyin:\n   - Steam kütüphanesi (örn: D:\\SteamLibrary)\n   - Downloads klasörü (çok dosya varsa)\n```\n\n**4. Alternative çözüm** (kalıcı):\n```powershell\n# PowerShell (Admin) ile çalıştır:\nSet-MpPreference -DisableRealtimeMonitoring $true\n```\n\n⚠️ **Önemli:** Defender'ı kalıcı kapatmayın! Sadece scan sıklığını ayarlayın:\n- Weekly → Monthly\n- Full Scan → Quick Scan\n\nBunları yaptıktan sonra CPU kullanımı nasıl?"
    },
    {
      "role": "user",
      "content": "Defender'ı durdurdum, CPU %20-30'a düştü! Çok teşekkürler. Ama kalıcı çözüm için ne önerirsiniz?"
    },
    {
      "role": "assistant",
      "content": "Harika! Problemi çözdük. Şimdi **kalıcı çözüm**:\n\n**Long-term Optimizasyon:**\n\n**1. Defender Schedule Ayarla**\n```\n1. Task Scheduler açın (Win + R → taskschd.msc)\n2. Microsoft → Windows → Windows Defender\n3. \"Windows Defender Scheduled Scan\" → sağ tık → Properties\n4. Trigger → Edit\n5. Zamanlama: Haftalık, Pazar, 03:00 (bilgisayar açık değilken)\n```\n\n**2. Defender Performans Ayarları**\n```powershell\n# PowerShell (Admin):\n\n# CPU limit koy (%50 max)\nSet-MpPreference -ScanAvgCPULoadFactor 50\n\n# Arka plan tarama hızını düşür\nSet-MpPreference -ScanOnlyIfIdleEnabled $true\n```\n\n**3. Exclusion Listesi (akıllıca)**\n```\nEklenecek klasörler:\n✅ Steam/Oyun kütüphanesi\n✅ Video editing dosyaları (büyük)\n✅ Development folders (node_modules, venv)\n\n❌ EKLEMEyin:\n- Downloads folder (riskli)\n- Desktop\n- Documents\n```\n\n**4. Genel Sistem Optimizasyonu**\n\n```\n**Disable Edilecek Servisler:**\n1. Windows Search (SSD'niz varsa)\n2. Superfetch/Prefetch (SSD'de gereksiz)\n3. Windows Update (manual yap)\n\n**Startup Programları:**\n- Task Manager → Startup\n- Gereksizleri disable et:\n  ❌ Steam\n  ❌ Discord\n  ❌ Spotify\n  ✅ Antivirus (keep enabled)\n```\n\n**5. Disk Temizliği (Aylık Rutin)**\n```batch\n:: cleanup.bat dosyası oluştur:\n@echo off\ncleanmgr /sagerun:1\ndel /q/f/s %TEMP%\\*\nrd /s /q %TEMP%\nmkdir %TEMP%\n```\n\n**📊 Beklenen Sonuçlar:**\n- İdle CPU: %5-10\n- Aktif kullanım: %30-50\n- Disk boş alan: >50GB\n- RAM kullanımı: <70%\n\n**🔄 Aylık Bakım:**\n1. Restart (haftada 1)\n2. Disk cleanup (ayda 1)\n3. Defender full scan (ayda 1, gece)\n4. Windows Update (ayda 1)\n\n**Son kontrol:** Şu an Task Manager'da durumlar nasıl?\n- CPU: ?\n- RAM: ?\n- Disk: ?\n\nHer şey %50'nin altında olmalı."
    }
  ]
}
```

### 🎨 DeepFabric YAML Konfigürasyonu

```yaml
# multi_turn_config.yaml
dataset_system_prompt: |
  Sen yardımsever bir asistansın. Konuşma boyunca context'i hatırlarsın
  ve kullanıcıyla adım adım ilerlersin.

topic_tree:
  topic_prompt: |
    Multi-turn Konuşma Senaryoları:
    - Seyahat planlama
    - Teknik destek
    - Alışveriş danışmanlığı
    - Eğitim koçluğu
    - Sağlık tavsiyeleri
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.8
  degree: 3
  depth: 3

data_engine:
  conversation_type: "multi_turn"  # 🔑 Önemli!
  generation_system_prompt: |
    3-5 turlu doğal bir konuşma oluştur:
    
    Tur 1: Kullanıcı genel soru sorar
    Tur 2: Sen detay için soru sorarsın
    Tur 3: Kullanıcı detay verir
    Tur 4: Sen analiz + öneri verirsin
    Tur 5: Kullanıcı follow-up sorar, sen kapsamlı cevap verirsin
    
    İlkeler:
    - Her turda önceki context'i kullan
    - Kullanıcının isim, tercih gibi bilgilerini hatırla
    - Doğal konuşma akışı
    - Progressive disclosure (adım adım derinleş)
  
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7

dataset:
  creation:
    num_steps: 200
  save_as: "multi_turn_dataset.jsonl"
```

---

*(Devamını bir sonraki mesajda göndereceğim - çok uzun oldu)*
