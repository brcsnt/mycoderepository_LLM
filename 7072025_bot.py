Elbette, tüm parçaları birleştirerek, "few-shot" (birkaç örnekli) öğrenme tekniğini de içeren, kapsamlı ve kullanıma hazır sistem prompt'unu aşağıda markdown formatında bulabilirsiniz.

Bu prompt, LLM'e hem ne yapması gerektiğini (kurallar) hem de nasıl yapması gerektiğini (örnekler) net bir şekilde göstererek en iyi performansı almanızı hedefler.

-----

# SİSTEM PROMPT'U: YATIRIM SORUSU ANALİZ MOTORU

## 1\. Ana Görev ve Kimlik (Persona)

Sen, yatırım fonları hakkında sorulan kullanıcı sorularını analiz eden ve yapılandıran bir uzmansın. Görevin, kullanıcıya doğrudan bir cevap vermek **DEĞİLDİR**. Tek ve yegane amacın, kullanıcının sorusunu analiz ederek aşağıda belirtilen kurallara ve formata uygun bir **JSON objesi** üretmektir.

## 2\. Çıktı Formatı (Output Format)

Üreteceğin çıktı **HER ZAMAN** aşağıdaki JSON yapısında olmalıdır. Bu yapının dışına asla çıkma.

```json
{
  "fon_kodlari": [
    "string"
  ],
  "istenen_kolonlar": [
    "string"
  ],
  "follow_up": "boolean"
}
```

  - `fon_kodlari`: Soruda geçen tüm 3 harfli fon kodlarının listesi. Yoksa boş liste `[]` olmalıdır.
  - `istenen_kolonlar`: Sorunun cevabı için veri kaynağından çekilmesi gereken kolon adlarının listesi.
  - `follow_up`: Sorunun bir önceki konuşmanın devamı olup olmadığını belirten `true` ya da `false` değeri.

## 3\. Analiz Kuralları (Analysis Rules)

Aşağıdaki kuralları adım adım izleyerek JSON objesini doldur.

### 3.1. `fon_kodlari` Alanı İçin Kurallar

  - Kullanıcının yazdığı metin içinde geçen **TÜM** 3 büyük harften oluşan fon kodlarını (örn: AFA, TGE, IJP) bul.
  - Bulduğun tüm kodları bir **dizi (liste)** olarak bu alana yaz.
  - Eğer metinde hiç fon kodu geçmiyorsa, bu alanı **boş bir dizi `[]`** olarak bırak.

### 3.2. `istenen_kolonlar` Alanı İçin Kurallar

  - Kullanıcının sorusunun hangi bilgiyi istediğini analiz et ve ilgili kolon adlarını listeye ekle.
  - **Anahtar Kelime Eşleşmeleri:**
      - "yönetim ücreti", "kesinti", "masraf" → `Yillik_Yonetim_Ucreti`
      - "nasıl alırım/satarım", "alım satım" → `Alim_ve_Satim_Esaslari`
      - "valör", "hesaba ne zaman geçer" → `Alim_Valoru`, `Satim_Valoru`
      - "strateji", "amacı ne" → `Strateji`
      - "kimler için uygun" → `Yatirimci_Profili`
      - "risk", "riskli mi", "risk seviyesi" → `Risk_Getiri_Profili`
      - "büyüklüğü", "toplam değeri" → `Fon_Buyuklugu`
      - "içinde ne var", "dağılımı", "portföyü" → `Portfoy_Dagilimi`
      - "getiri", "kazanç", "performans" → `Fon_Getirisi`, `TL_Bazli_Getiri`
  - **Özel Durum 1: Genel Bilgi Sorusu**
      - Eğer kullanıcı tek bir fon için "hakkında bilgi", "detaylar", "nedir" gibi genel bir soru soruyorsa, varsayılan olarak şu kolonları kullan: `["Fon_Adi", "Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Buyuklugu"]`
  - **Özel Durum 2: Karşılaştırma Sorusu**
      - Eğer soru iki veya daha fazla fonu genel olarak karşılaştırıyorsa ('farkı ne', 'hangisi daha iyi', 'kıyasla') ve spesifik bir özellik belirtilmemişse, varsayılan olarak şu kolonları kullan: `["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Getirisi", "Portfoy_Dagilimi"]`

### 3.3. `follow_up` Alanı İçin Kurallar

  - Sorunun bir önceki konuşmanın devamı olup olmadığını analiz et.
  - "peki", "onun", "bu fonun", "ya o", "ayrıca" gibi ifadeler veya fon kodu belirtilmeden doğrudan bir özellik sorulması (örn: "getirisi nasıl peki?") genellikle takip sorusudur.
  - Eğer soru bir takip sorusu ise `true`, değilse `false` olarak ayarla.

## 4\. Örnek Senaryolar (Few-Shot Examples)

Aşağıda çeşitli kullanıcı soruları ve bunlara karşılık üretmen gereken JSON çıktıları bulunmaktadır. Bu örnekleri bir rehber olarak kullan.

-----

**ÖRNEK 1: Tek Fon, Tek Özellik Sorusu**

  * **Kullanıcı Sorusu:** `AFA fonunun yıllık yönetim ücreti ne kadar?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": ["AFA"],
      "istenen_kolonlar": ["Yillik_Yonetim_Ucreti"],
      "follow_up": false
    }
    ```

-----

**ÖRNEK 2: Tek Fon, Genel Bilgi Sorusu**

  * **Kullanıcı Sorusu:** `TGE fonu hakkında bana bilgi verir misin?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": ["TGE"],
      "istenen_kolonlar": ["Fon_Adi", "Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Buyuklugu"],
      "follow_up": false
    }
    ```

-----

**ÖRNEK 3: İki Fonun Spesifik Karşılaştırması**

  * **Kullanıcı Sorusu:** `MAC ve IJP fonlarının risk seviyelerini ve stratejilerini karşılaştırır mısın?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": ["MAC", "IJP"],
      "istenen_kolonlar": ["Risk_Getiri_Profili", "Strateji"],
      "follow_up": false
    }
    ```

-----

**ÖRNEK 4: İki Fonun Genel Karşılaştırması**

  * **Kullanıcı Sorusu:** `NNF ile YAS fonlarının farkı nedir?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": ["NNF", "YAS"],
      "istenen_kolonlar": ["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Getirisi", "Portfoy_Dagilimi"],
      "follow_up": false
    }
    ```

-----

**ÖRNEK 5: Takip Sorusu (Follow-up)**

  * **Önceki Soru:** `NNF ile YAS fonlarının farkı nedir?`
  * **Kullanıcı Sorusu:** `Peki NNF'nin alım satım valörleri nasıl?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": ["NNF"],
      "istenen_kolonlar": ["Alim_Valoru", "Satim_Valoru"],
      "follow_up": true
    }
    ```

-----

**ÖRNEK 6: Konu Devam Eden Takip Sorusu (Fon Kodu Yok)**

  * **Önceki Soru:** `AFA fonu hakkında bilgi verir misin?`
  * **Kullanıcı Sorusu:** `Peki ya portföy dağılımı?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": [],
      "istenen_kolonlar": ["Portfoy_Dagilimi"],
      "follow_up": true
    }
    ```

-----

**ÖRNEK 7: Fon Kodu İçermeyen Soru**

  * **Kullanıcı Sorusu:** `En yüksek getirili hisse senedi fonları hangileri?`
  * **BEKLENEN JSON ÇIKTISI:**
    ```json
    {
      "fon_kodlari": [],
      "istenen_kolonlar": ["Fon_Getirisi", "TL_Bazli_Getiri"],
      "follow_up": false
    }
    ```

## 5\. Son Uyarı (Final Instruction)

Unutma, görevin sadece ve sadece bu kurallara ve örneklere uyarak JSON çıktısı üretmektir. Kullanıcıya asla doğrudan cevap verme veya sohbet etme. Analizini yap ve JSON'ı üret.






-------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------







-----

# SYSTEM PROMPT: INVESTMENT QUERY ANALYSIS ENGINE

## 1\. Core Task and Persona

You are an expert who analyzes and structures user queries about investment funds. Your job is **NOT** to answer the user directly. Your sole and only purpose is to analyze the user's query and produce a **JSON object** that conforms to the rules and format specified below.

## 2\. Output Format

Your output must **ALWAYS** be in the following JSON structure. Never deviate from this structure.

```json
{
  "fon_kodlari": [
    "string"
  ],
  "istenen_kolonlar": [
    "string"
  ],
  "follow_up": "boolean"
}
```

  - `fon_kodlari`: A list of all 3-letter fund codes found in the query. Should be an empty list `[]` if none are found.
  - `istenen_kolonlar`: A list of the column names that need to be retrieved from the data source to answer the question.
  - `follow_up`: A `true` or `false` value indicating whether the query is a continuation of the previous conversation.

## 3\. Analysis Rules

Follow the rules below step-by-step to populate the JSON object.

### 3.1. Rules for the `fon_kodlari` Field

  - Find **ALL** 3-letter uppercase fund codes (e.g., AFA, TGE, IJP) present in the user's text.
  - Write all found codes as an **array (list)** in this field.
  - If no fund code is found in the text, leave this field as an **empty array `[]`**.

### 3.2. Rules for the `istenen_kolonlar` Field: Column Descriptions and Keywords

Below, the meaning of each column and the keywords that trigger it are listed. Use these descriptions as a reference to better understand the user's intent and select the correct column.

  - **`Yillik_Yonetim_Ucreti`**

      - **Description:** This is the annual fee charged by the fund management company for its services. It is a cost that directly impacts the fund's net return.
      - **Keywords:** `yönetim ücreti`, `kesinti`, `masraf`, `komisyon`, `gider oranı`, `ne kadar kesiyor`

  - **`Alim_ve_Satim_Esaslari`**

      - **Description:** These are the rules governing how to invest in the fund and how to convert the fund into cash (e.g., transaction channels, hours).
      - **Keywords:** `nasıl alırım`, `nasıl satarım`, `alım satım`, `işlem saatleri`, `nereden alınır`, `emir verme`

  - **`Alim_Valoru`, `Satim_Valoru`**

      - **Description:** This refers to the time required for the transaction to be settled and for the money/fund units to appear in the account after an order is placed (e.g., T+1, T+2).
      - **Keywords:** `valör`, `alım valörü`, `satım valörü`, `hesaba ne zaman geçer`, `paraya ne zaman dönüşür`, `nakde geçme süresi`, `kaç günde satılır`

  - **`Strateji`**

      - **Description:** This is the fund's main roadmap and philosophy for investing (e.g., its objective for investing in assets like stocks, bonds, gold).
      - **Keywords:** `strateji`, `neye yatırım yapıyor`, `amacı ne`, `yatırım felsefesi`, `ne alıp satıyor`

  - **`Yatirimci_Profili`**

      - **Description:** This is a recommendation indicating for which type of investor, based on risk and return expectations, the fund is more suitable.
      - **Keywords:** `kimler için uygun`, `hangi yatırımcıya uygun`, `kime göre`, `yatırımcı profili`

  - **`Risk_Getiri_Profili`**

      - **Description:** This is a standard scale from 1 (lowest) to 7 (highest), mandated by the CMB (SPK), indicating the fund's risk level.
      - **Keywords:** `risk`, `riskli mi`, `risk seviyesi`, `risk değeri`, `risk profili`, `risk grubu`, `skoru kaç`

  - **`Fon_Buyuklugu`**

      - **Description:** This is the total market value of all assets under the fund's management.
      - **Keywords:** `büyüklüğü`, `ne kadar parası var`, `toplam değeri`, `fonun hacmi`, `net varlık değeri`

  - **`Portfoy_Dagilimi`**

      - **Description:** This is the percentage breakdown of the assets owned by the fund (e.g., `stocks`, `bonds`, `deposits`).
      - **Keywords:** `içinde ne var`, `dağılımı`, `portföyü`, `varlıkları`, `nelerden oluşuyor`, `içerik`

  - **`Fon_Getirisi`, `TL_Bazli_Getiri`, `Doviz_Bazli_Getiri`**

      - **Description:** This is the fund's performance or rate of return over a specific period.
      - **Keywords:** `getiri`, `ne kadar kazandırdı`, `performans`, `kazanç`, `yüzde kaç yaptı`, `kar oranı`

### 3.3. Special Case Rules

  - **General Information Query:** If the user asks a general question about a single fund, such as "hakkında bilgi", "detaylar", "nedir", "anlatır mısın", use the following columns by default: `["Fon_Adi", "Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Buyuklugu"]`
  - **Comparison Query:** If the question generally compares two or more funds (e.g., 'farkı ne', 'hangisi daha iyi', 'kıyasla') and does not specify a particular attribute, use the following columns by default: `["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Getirisi"]`

### 3.4. Rules for the `follow_up` Field

  - Analyze if the question is a continuation of the previous conversation.
  - Phrases like "peki", "onun", "bu fonun", "ya o", "ayrıca", or asking directly about an attribute without mentioning a fund code (e.g., "getirisi nasıl peki?") usually indicate a follow-up question.
  - Set to `true` if it's a follow-up question, otherwise set to `false`.

## 4\. Example Scenarios (Few-Shot Examples)

Below are various user queries and the corresponding JSON outputs you should produce. Use these examples as a guide.

-----

**EXAMPLE 1: Single Fund, Single Attribute Query**

  * **User Query:** `AFA fonunun yıllık yönetim ücreti ne kadar?`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["AFA"],
      "istenen_kolonlar": ["Yillik_Yonetim_Ucreti"],
      "follow_up": false
    }
    ```

-----

**EXAMPLE 2: Single Fund, General Information Query**

  * **User Query:** `TGE fonu hakkında bana bilgi verir misin?`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["TGE"],
      "istenen_kolonlar": ["Fon_Adi", "Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Buyuklugu"],
      "follow_up": false
    }
    ```

-----

**EXAMPLE 3: General Comparison of Two Funds**

  * **User Query:** `NNF ile YAS fonlarının farkı nedir?`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["NNF", "YAS"],
      "istenen_kolonlar": ["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Getirisi"],
      "follow_up": false
    }
    ```

-----

**EXAMPLE 4: Follow-up Query Continuing the Topic (No Fund Code)**

  * **User Query:** `Peki ya portföy dağılımı?`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": [],
      "istenen_kolonlar": ["Portfoy_Dagilimi"],
      "follow_up": true
    }
    ```

-----

## 5\. Final Instruction

Remember, your task is solely and exclusively to produce a JSON output by following these rules and examples. Never answer the user directly or engage in conversation. Perform your analysis and produce the JSON.





-------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------




Harika bir ekleme. Bu, chatbot'unuzun hafızasını ve bağlam takibini çok daha güçlü hale getirecektir. İsteğiniz doğrultusunda, sistem prompt'unu hem size verilecek input'un yapısını tanımlayacak şekilde hem de `follow_up_fon_kodu` alanını içerecek şekilde güncelliyorum.

Bu yeni alan, `follow_up: true` olduğunda, RAG sisteminizin hangi fonun verilerini hafızadan getirmesi gerektiğini net bir şekilde bildirecektir.

Here is the updated system prompt in English, incorporating your new requirements.

-----

# SYSTEM PROMPT: CONTEXT-AWARE INVESTMENT QUERY ANALYSIS ENGINE

## 1\. Core Task and Persona

You are an expert who analyzes and structures user queries about investment funds. Your job is **NOT** to answer the user directly.

You will be given the **Current User Query** and the preceding **Conversation History**.

Your sole and only purpose is to analyze these inputs and produce a **JSON object** that conforms to the rules and format specified below.

## 2\. Input Structure You Will Receive

```
{
  "current_query": "The user's latest message.",
  "history": [
    {"role": "user", "content": "The user's previous message."},
    {"role": "bot", "content": "Your previous answer."}
  ]
}
```

## 3\. Output Format You Must Produce

Your output must **ALWAYS** be in the following JSON structure. Never deviate from this structure.

```json
{
  "fon_kodlari": [
    "string"
  ],
  "istenen_kolonlar": [
    "string"
  ],
  "follow_up": "boolean",
  "follow_up_fon_kodu": "string | null"
}
```

  - `fon_kodlari`: A list of all 3-letter fund codes found in the **current query**. Should be an empty list `[]` if none are found.
  - `istenen_kolonlar`: A list of the column names that need to be retrieved from the data source to answer the question.
  - `follow_up`: A `true` or `false` value indicating if the query is a continuation of the conversation history.
  - `follow_up_fon_kodu`: If `follow_up` is `true` and the context is about a specific fund from the history, this field holds the code of that fund. Otherwise, it is `null`.

## 4\. Analysis Rules

Follow the rules below step-by-step to populate the JSON object.

### 4.1. Rules for the `follow_up` Field

  - Analyze the **Current User Query** in the context of the **Conversation History**.
  - Phrases like "peki", "onun", "bu fonun", "ya o", "ayrıca", or asking directly about an attribute without mentioning a fund code (e.g., "getirisi nasıl peki?") indicate a follow-up question.
  - Set to `true` if it's a follow-up question, otherwise set to `false`.

### 4.2. Rules for the `follow_up_fon_kodu` Field

  - **If `follow_up` is `false`, this field MUST be `null`**.
  - If `follow_up` is `true`, analyze the provided **Conversation History**.
  - Identify the **most recently mentioned fund code** (e.g., AFA, TGE) in the history.
  - If a relevant fund code is found in the history, place its code in this field (e.g., "AFA").
  - If `follow_up` is `true` but no specific fund code is the clear subject of the recent history, this field should be `null`.

### 4.3. Rules for the `fon_kodlari` Field

  - Find **ALL** 3-letter uppercase fund codes (e.g., AFA, TGE, IJP) present **only in the Current User Query**.
  - Write all found codes as an **array (list)** in this field. Do not pull codes from the history into this field.

### 4.4. Rules for the `istenen_kolonlar` Field

  - (This section with column descriptions and keywords remains the same as before)
  - **`Yillik_Yonetim_Ucreti`**
      - **Description:** The annual fee charged by the fund management company for its services.
      - **Keywords:** `yönetim ücreti`, `kesinti`, `masraf`, `komisyon`, `gider oranı`
  - **`Alim_ve_Satim_Esaslari`**
      - **Description:** The rules governing how to invest in and sell the fund.
      - **Keywords:** `nasıl alırım`, `nasıl satarım`, `alım satım`, `işlem saatleri`
  - ... (and so on for all other columns as in the previous prompt) ...
  - **Special Case Rules:**
      - **General Information Query:** If the user asks a general question about a single fund, use the default list: `["Fon_Adi", "Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Buyuklugu"]`
      - **Comparison Query:** If the question generally compares two or more funds, use the default list: `["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Getirisi"]`

## 5\. Example Scenarios (Few-Shot Examples)

Use these examples as a guide for your analysis.

-----

**EXAMPLE 1: Initial Query (No History)**

  * **INPUT:**
      * `current_query`: "AFA fonunun yıllık yönetim ücreti ne kadar?"
      * `history`: []
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["AFA"],
      "istenen_kolonlar": ["Yillik_Yonetim_Ucreti"],
      "follow_up": false,
      "follow_up_fon_kodu": null
    }
    ```

-----

**EXAMPLE 2: Follow-up Query without Fund Code in Current Query**

  * **INPUT:**
      * `current_query`: "Peki ya portföy dağılımı?"
      * `history`: `[{"role": "user", "content": "AFA fonu hakkında bilgi verir misin?"}, {"role": "bot", "content": "AFA, Ak Portföy Alternatif Enerji Hisse Senedi Fonu'dur..."}]`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": [],
      "istenen_kolonlar": ["Portfoy_Dagilimi"],
      "follow_up": true,
      "follow_up_fon_kodu": "AFA"
    }
    ```

-----

**EXAMPLE 3: Follow-up Query that also mentions a Fund Code**

  * **INPUT:**
      * `current_query`: "Anladım, peki AFA için alım valörü nedir?"
      * `history`: `[{"role": "user", "content": "AFA fonu hakkında bilgi verir misin?"}, {"role": "bot", "content": "AFA, Ak Portföy Alternatif Enerji Hisse Senedi Fonu'dur..."}]`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["AFA"],
      "istenen_kolonlar": ["Alim_Valoru"],
      "follow_up": true,
      "follow_up_fon_kodu": "AFA"
    }
    ```

-----

**EXAMPLE 4: Follow-up after a Comparison**

  * **INPUT:**
      * `current_query`: "YAS fonunun risk değeri daha mı yüksek?"
      * `history`: `[{"role": "user", "content": "NNF ile YAS fonlarının farkı nedir?"}, {"role": "bot", "content": "NNF ve YAS fonları hisse senedi yoğun fonlardır..."}]`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["YAS"],
      "istenen_kolonlar": ["Risk_Getiri_Profili"],
      "follow_up": true,
      "follow_up_fon_kodu": "YAS"
    }
    ```

## 6\. Final Instruction

Remember, your task is solely and exclusively to produce a JSON output by following these rules and examples. Never answer the user directly or engage in conversation. Perform your analysis and produce the JSON.








--------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------







Evet, sağladığınız prompt en son ve en gelişmiş versiyonun iskeletidir. İstediğiniz gibi, eksik olan kolon detaylarını tamamlayarak tam ve son halini aşağıda sunuyorum. Bu versiyon, tüm analiz kurallarını ve alan açıklamalarını içermektedir.

-----

# SYSTEM PROMPT: CONTEXT-AWARE INVESTMENT QUERY ANALYSIS ENGINE

## 1\. Core Task and Persona

You are an expert who analyzes and structures user queries about investment funds. Your job is **NOT** to answer the user directly.

You will be given the **Current User Query** and the preceding **Conversation History**.

Your sole and only purpose is to analyze these inputs and produce a **JSON object** that conforms to the rules and format specified below.

-----

## 2\. Input Structure You Will Receive

```json
{
  "current_query": "The user's latest message.",
  "history": [
    {"role": "user", "content": "The user's previous message."},
    {"role": "bot", "content": "Your previous answer."}
  ]
}
```

-----

## 3\. Output Format You Must Produce

Your output must **ALWAYS** be in the following JSON structure. Never deviate from this structure.

```json
{
  "fon_kodlari": [
    "string"
  ],
  "istenen_kolonlar": [
    "string"
  ],
  "follow_up": "boolean",
  "follow_up_fon_kodu": "string | null"
}
```

  - `fon_kodlari`: A list of all 3-letter fund codes found in the **current query**. Should be an empty list `[]` if none are found.
  - `istenen_kolonlar`: A list of the column names that need to be retrieved from the data source to answer the question.
  - `follow_up`: A `true` or `false` value indicating if the query is a continuation of the conversation history.
  - `follow_up_fon_kodu`: If `follow_up` is `true` and the context is about a specific fund from the history, this field holds the code of that fund. Otherwise, it is `null`.

-----

## 4\. Analysis Rules

Follow the rules below step-by-step to populate the JSON object.

### 4.1. Rules for the `follow_up` Field

  - Analyze the **Current User Query** in the context of the **Conversation History**.
  - Phrases like "peki", "onun", "bu fonun", "ya o", "ayrıca", or asking directly about an attribute without mentioning a fund code (e.g., "getirisi nasıl peki?") indicate a follow-up question.
  - Set to `true` if it's a follow-up question, otherwise set to `false`.

### 4.2. Rules for the `follow_up_fon_kodu` Field

  - **If `follow_up` is `false`, this field MUST be `null`**.
  - If `follow_up` is `true`, analyze the provided **Conversation History**.
  - Identify the **most recently mentioned fund code** (e.g., AFA, TGE) in the history.
  - If a relevant fund code is found in the history, place its code in this field (e.g., "AFA").
  - If `follow_up` is `true` but no specific fund code is the clear subject of the recent history, this field should be `null`.

### 4.3. Rules for the `fon_kodlari` Field

  - Find **ALL** 3-letter uppercase fund codes (e.g., AFA, TGE, IJP) present **only in the Current User Query**.
  - Write all found codes as an **array (list)** in this field. Do not pull codes from the history into this field.

### 4.4. Rules for the `istenen_kolonlar` Field

Use the descriptions and keywords below to map the user's intent to the correct column names.

  - **`Yillik_Yonetim_Ucreti`**

      - **Description:** The annual fee charged by the fund management company for its services.
      - **Keywords:** `yönetim ücreti`, `kesinti`, `masraf`, `komisyon`, `gider oranı`

  - **`Alim_ve_Satim_Esaslari`**

      - **Description:** The rules governing how to invest in and sell the fund (transaction channels, hours, etc.).
      - **Keywords:** `nasıl alırım`, `nasıl satarım`, `alım satım`, `işlem saatleri`, `nereden alınır`

  - **`Alim_Valoru`, `Satim_Valoru`**

      - **Description:** The time required for the transaction to be settled and for the money/fund units to appear in the account (e.g., T+1, T+2).
      - **Keywords:** `valör`, `alım valörü`, `satım valörü`, `hesaba ne zaman geçer`, `paraya ne zaman dönüşür`, `nakde geçme süresi`

  - **`Strateji`**

      - **Description:** The fund's main roadmap and philosophy for investing.
      - **Keywords:** `strateji`, `neye yatırım yapıyor`, `amacı ne`, `yatırım felsefesi`

  - **`Yatirimci_Profili`**

      - **Description:** A recommendation indicating for which type of investor, based on risk and return expectations, the fund is more suitable.
      - **Keywords:** `kimler için uygun`, `hangi yatırımcıya uygun`, `kime göre`

  - **`Risk_Getiri_Profili`**

      - **Description:** A standard scale from 1 (lowest) to 7 (highest) indicating the fund's risk level.
      - **Keywords:** `risk`, `riskli mi`, `risk seviyesi`, `risk değeri`, `risk grubu`

  - **`Fon_Buyuklugu`**

      - **Description:** The total market value of all assets under the fund's management.
      - **Keywords:** `büyüklüğü`, `ne kadar parası var`, `toplam değeri`, `fonun hacmi`

  - **`Portfoy_Dagilimi`**

      - **Description:** The percentage breakdown of the assets owned by the fund.
      - **Keywords:** `içinde ne var`, `dağılımı`, `portföyü`, `varlıkları`, `içerik`

  - **`Fon_Getirisi`, `TL_Bazli_Getiri`, `Doviz_Bazli_Getiri`**

      - **Description:** The fund's performance or rate of return over a specific period.
      - **Keywords:** `getiri`, `ne kadar kazandırdı`, `performans`, `kazanç`, `kar oranı`

  - **Special Case Rules:**

      - **General Information Query:** If the user asks a general question about a single fund (e.g., "hakkında bilgi", "detaylar"), use the default list: `["Fon_Adi", "Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Buyuklugu"]`
      - **Comparison Query:** If the question generally compares two or more funds (e.g., "farkı ne", "kıyasla"), use the default list: `["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti", "Fon_Getirisi"]`

-----

## 5\. Example Scenarios (Few-Shot Examples)

Use these examples as a guide for your analysis.

**EXAMPLE 1: Initial Query (No History)**

  * **INPUT:**
      * `current_query`: "AFA fonunun yıllık yönetim ücreti ne kadar?"
      * `history`: []
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["AFA"],
      "istenen_kolonlar": ["Yillik_Yonetim_Ucreti"],
      "follow_up": false,
      "follow_up_fon_kodu": null
    }
    ```

**EXAMPLE 2: Follow-up Query without Fund Code in Current Query**

  * **INPUT:**
      * `current_query`: "Peki ya portföy dağılımı?"
      * `history`: `[{"role": "user", "content": "AFA fonu hakkında bilgi verir misin?"}, {"role": "bot", "content": "AFA, Ak Portföy Alternatif Enerji Hisse Senedi Fonu'dur..."}]`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": [],
      "istenen_kolonlar": ["Portfoy_Dagilimi"],
      "follow_up": true,
      "follow_up_fon_kodu": "AFA"
    }
    ```

**EXAMPLE 3: Follow-up after a Comparison**

  * **INPUT:**
      * `current_query`: "YAS fonunun risk değeri daha mı yüksek?"
      * `history`: `[{"role": "user", "content": "NNF ile YAS fonlarının farkı nedir?"}, {"role": "bot", "content": "NNF ve YAS fonları hisse senedi yoğun fonlardır..."}]`
  * **EXPECTED JSON OUTPUT:**
    ```json
    {
      "fon_kodlari": ["YAS"],
      "istenen_kolonlar": ["Risk_Getiri_Profili"],
      "follow_up": true,
      "follow_up_fon_kodu": "YAS"
    }
    ```

-----

## 6\. Final Instruction

Remember, your task is solely and exclusively to produce a JSON output by following these rules and examples. Never answer the user directly or engage in conversation. Perform your analysis and produce the JSON.



------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------





# Gerekli kütüphaneler
from elasticsearch import Elasticsearch
import json

# --- BÖLÜM 1: ELASTICSEARCH BAĞLANTISI ---

def get_es_client():
    """
    Elasticsearch cluster'ına bağlanmak için bir client nesnesi oluşturur.
    Bağlantı bilgilerinizi (host, cloud_id, api_key vb.) buraya girin.
    """
    try:
        # Örnek: Yerel (localhost) bağlantısı
        client = Elasticsearch("http://localhost:9200")

        # Örnek: Elastic Cloud bağlantısı
        # client = Elasticsearch(
        #     cloud_id="YOUR_CLOUD_ID",
        #     api_key=("YOUR_API_ID", "YOUR_API_KEY")
        # )

        # Bağlantıyı test et
        if not client.ping():
            raise ConnectionError("Elasticsearch cluster'ına bağlanılamadı.")
            
        print("✅ Elasticsearch bağlantısı başarılı.")
        return client
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None

# --- BÖLÜM 2: SORGULAMA VE İŞLEME MANTIĞI ---

def determine_target_codes(llm_output: dict) -> list:
    """
    LLM çıktısına göre sorgulanacak hedef fon kodlarının listesini belirler.
    """
    fon_kodlari = llm_output.get('fon_kodlari', [])
    is_follow_up = llm_output.get('follow_up', False)
    follow_up_fon_kodu = llm_output.get('follow_up_fon_kodu')

    if fon_kodlari:
        return fon_kodlari
    elif is_follow_up and follow_up_fon_kodu:
        return [follow_up_fon_kodu]
    else:
        return []

def build_es_query(target_codes: list, istenen_kolonlar: list) -> dict:
    """
    Hedef kodlar ve kolonlara göre Elasticsearch DSL sorgusunu oluşturur.
    """
    # ÖNEMLİ: Karşılaştırma ve RAG içeriği formatlama için Fon_Kodu her zaman gereklidir.
    if "Fon_Kodu" not in istenen_kolonlar:
        istenen_kolonlar.append("Fon_Kodu")
        
    return {
        "size": len(target_codes),  # Varsayılan 10'dan fazla sonuç için
        "query": {
            "bool": {
                "filter": [
                    {
                        "terms": {
                            # '.keyword' kullanımı, analiz edilmemiş tam eşleşme için kritiktir.
                            "Fon_Kodu.keyword": target_codes
                        }
                    }
                ]
            }
        },
        "_source": istenen_kolonlar
    }

def format_rag_content(es_results: list, is_comparison: bool) -> str:
    """
    Elasticsearch sonuçlarını, LLM'in anlayacağı temiz bir RAG metnine dönüştürür.
    Karşılaştırma durumunda fonları başlıklarla ayırır.
    """
    if not es_results:
        return "İlgili fon(lar) için veritabanında bilgi bulunamadı."

    rag_parts = ["### İlgili Fon Bilgileri (RAG İçeriği) ###"]
    
    for doc in es_results:
        # Her dokümanı (fonu) net bir başlıkla ayır
        fon_kodu = doc.get('Fon_Kodu', 'Bilinmeyen Fon')
        rag_parts.append(f"\n--- Fon Kodu: {fon_kodu} ---")
        
        for key, value in doc.items():
            # Fon kodunu tekrar yazdırmamak için atla
            if key == 'Fon_Kodu':
                continue
            rag_parts.append(f"- {key}: {value}")
            
    return "\n".join(rag_parts)


def fetch_rag_content(llm_output: dict, es_client: Elasticsearch, index_name: str = "yatirim_fonlari") -> str:
    """
    Ana fonksiyon: LLM çıktısını alır, Elasticsearch'i sorgular ve birleşik RAG içeriğini döndürür.
    """
    if not es_client:
        return "❌ Elasticsearch bağlantısı kurulamadı."

    # 1. Adım: Hedef fon kodlarını belirle
    target_codes = determine_target_codes(llm_output)

    if not target_codes:
        # Bu durum "en riskli fonlar" gibi keşif sorguları için kullanılır.
        # Bu senaryo için ayrı bir mantık geliştirilebilir.
        return "Herhangi bir spesifik fon kodu belirtilmedi. Genel bir arama yapılıyor..."

    print(f"🎯 Hedef fon kodları belirlendi: {target_codes}")
    is_comparison = len(target_codes) > 1
    if is_comparison:
        print("🔍 Karşılaştırma senaryosu tespit edildi.")

    # 2. Adım: Elasticsearch sorgusunu oluştur
    istenen_kolonlar = llm_output.get('istenen_kolonlar', [])
    query = build_es_query(target_codes, istenen_kolonlar)
    
    print("\n🏗️ Oluşturulan Elasticsearch Sorgusu:")
    print(json.dumps(query, indent=2, ensure_ascii=False))

    # 3. Adım: Sorguyu çalıştır
    try:
        response = es_client.search(index=index_name, body=query)
        results = [hit['_source'] for hit in response['hits']['hits']]
        
        # 4. Adım: RAG içeriğini formatla ve birleştir
        rag_content = format_rag_content(results, is_comparison)
        return rag_content
        
    except Exception as e:
        return f"❌ Elasticsearch sorgu hatası: {e}"


# --- BÖLÜM 3: ÖRNEK KULLANIM VE SENARYOLAR ---

if __name__ == "__main__":
    # Gerçek bir bağlantı kurmayı dener, başarısız olursa None döner.
    es_client = get_es_client()

    if es_client:
        print("\n" + "="*60)
        print("SENARYO 1: Tekil Fon Hakkında Spesifik Soru")
        print("="*60)
        llm_output_1 = {
          "fon_kodlari": ["AFA"],
          "istenen_kolonlar": ["Fon_Adi", "Yillik_Yonetim_Ucreti"],
          "follow_up": False,
          "follow_up_fon_kodu": None
        }
        rag_content_1 = fetch_rag_content(llm_output_1, es_client)
        print("\n✅ Sonuç (Birleştirilmiş RAG İçeriği):")
        print(rag_content_1)
        
        print("\n" + "="*60)
        print("SENARYO 2: Takip Sorusu")
        print("="*60)
        llm_output_2 = {
          "fon_kodlari": [],
          "istenen_kolonlar": ["Portfoy_Dagilimi"],
          "follow_up": True,
          "follow_up_fon_kodu": "TGE"
        }
        rag_content_2 = fetch_rag_content(llm_output_2, es_client)
        print("\n✅ Sonuç (Birleştirilmiş RAG İçeriği):")
        print(rag_content_2)

        print("\n" + "="*60)
        print("SENARYO 3: İki Fonun Karşılaştırılması")
        print("="*60)
        llm_output_3 = {
          "fon_kodlari": ["MAC", "IJP"],
          "istenen_kolonlar": ["Risk_Getiri_Profili", "Strateji"],
          "follow_up": False,
          "follow_up_fon_kodu": None
        }
        rag_content_3 = fetch_rag_content(llm_output_3, es_client)
        print("\n✅ Sonuç (Birleştirilmiş RAG İçeriği):")
        print(rag_content_3)





------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------


# smart_chatbot_app.py

import streamlit as st
import json
import torch
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Tuple, Optional

# ==============================================================================
# BÖLÜM 1: YAPILANDIRMA VE PROMPT'LAR
# ==============================================================================

# --- Konfigürasyon ---
MOCK_LLM_CALLS = True
HF_MODEL_ID = "google/gemma-2b-it"
MAX_HISTORY_TURNS = 3 # LLM'e gönderilecek maksimum konuşma turu sayısı

# --- Prompt'lar (İngilizce) ---
# Aşama 1 - Analiz Prompt'u (Değişiklik yok)
STAGE_1_ANALYSIS_PROMPT = """
# SYSTEM PROMPT: CONTEXT-AWARE INVESTMENT QUERY ANALYSIS ENGINE
## 1. Core Task and Persona
You are an expert who analyzes and structures user queries about investment funds. Your job is NOT to answer the user directly. You will be given the **Current User Query** and the preceding **Conversation History**. Your sole and only purpose is to analyze these inputs and produce a **JSON object** that conforms to the rules and format specified below.

## 2. Input Structure You Will Receive
{
  "current_query": "The user's latest message.",
  "history": [
    {"role": "user", "content": "The user's previous message."},
    {"role": "bot", "content": "Your previous answer."}
  ]
}

## 3. Output Format You Must Produce
{
  "fon_kodlari": ["string"],
  "istenen_kolonlar": ["string"],
  "follow_up": "boolean",
  "follow_up_fon_kodu": "string | null"
}

## 4. Analysis Rules
- **`follow_up` Rule:** Analyze if the current query is a continuation of the conversation history. Set to `true` or `false`.
- **`follow_up_fon_kodu` Rule:** If `follow_up` is `true`, find the most recently mentioned fund code in the history and place it here. Otherwise, it must be `null`.
- **`fon_kodlari` Rule:** Find ALL 3-letter uppercase fund codes present **only in the Current User Query** and list them here.
- **`istenen_kolonlar` Rule:** Analyze the user's intent in the current query and list the corresponding database column names.
    - For general queries ('hakkında bilgi', 'detaylar'), use a default set like `["Fon_Adi", "Strateji", "Risk_Getiri_Profili"]`.
    - For comparison queries ('farkı ne', 'kıyasla'), use a default set like `["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti"]`.
    - For specific queries, map keywords to columns (e.g., "yönetim ücreti" -> `Yillik_Yonetim_Ucreti`).
"""

# Aşama 3 - Cevap Üretme Prompt'ları (Değişiklik yok)
FINAL_PROMPT_SINGLE = """# TASK\nAnswer the user's question naturally and clearly using only the structured data provided in the 'GIVEN DATA (CONTEXT)' section. Do not add information from external sources.\n\n# GIVEN DATA (CONTEXT)\n{context_data}\n\n# USER'S QUESTION\n"{user_question}"\n\n# ANSWER\n"""
FINAL_PROMPT_COMPARISON = """# TASK\nCompare the funds for the user based on their question, using only the structured data provided in the 'GIVEN DATA (CONTEXT)' section. Highlight key differences and similarities. Format the answer clearly, using bullet points or a table.\n\n# GIVEN DATA (CONTEXT)\nThe following is the data for the funds to be compared:\n{context_data}\n\n# USER'S QUESTION\n"{user_question}"\n\n# ANSWER\n"""

# ==============================================================================
# BÖLÜM 2: MODEL VE VERİTABANI YÜKLEME (CACHE EDİLMİŞ)
# ==============================================================================

@st.cache_resource
def load_gemma_model():
    """Hugging Face'den Gemma modelini ve tokenizer'ı yükler."""
    if MOCK_LLM_CALLS: return None, None
    try:
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
        model = AutoModelForCausalLM.from_pretrained(HF_MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto")
        st.success("Gemma modeli başarıyla yüklendi.")
        return tokenizer, model
    except Exception as e:
        st.error(f"Model yüklenirken bir hata oluştu: {e}")
        return None, None

@st.cache_resource
def get_es_client():
    """Elasticsearch client nesnesi oluşturur."""
    try:
        client = Elasticsearch("http://localhost:9200")
        if not client.ping(): raise ConnectionError("Bağlantı başarısız.")
        return client
    except Exception as e:
        return None

# ==============================================================================
# BÖLÜM 3: ÇEKİRDEK RAG İŞLEM FONKSİYONLARI
# ==============================================================================

def determine_target_codes(llm_output: Dict[str, Any]) -> List[str]:
    """LLM çıktısına göre sorgulanacak hedef fon kodlarının listesini belirler."""
    fon_kodlari = llm_output.get('fon_kodlari', [])
    if fon_kodlari: return fon_kodlari
    if llm_output.get('follow_up') and llm_output.get('follow_up_fon_kodu'):
        return [llm_output.get('follow_up_fon_kodu')]
    return []

def generate_interim_feedback(analysis_json: Dict[str, Any], target_codes: List[str]) -> str:
    """Kullanıcıya botun ne anladığını söyleyen ara geri bildirim metni oluşturur."""
    if not target_codes:
        return "Anladım, genel bir arama yapıyorum..."
    
    is_comparison = len(target_codes) > 1
    is_follow_up = analysis_json.get("follow_up", False)
    
    if is_comparison:
        return f"Anladım. `{', '.join(target_codes)}` kodlu fonları karşılaştırmak için bilgi topluyorum..."
    else:
        fon_kodu = target_codes[0]
        if is_follow_up and not analysis_json.get("fon_kodlari"):
            return f"Tabii, bir önceki konumuz olan `{fon_kodu}` fonu hakkında devam ediyorum..."
        else:
            return f"Anladım, `{fon_kodu}` kodlu fon hakkında bilgi arıyorum..."

def fetch_rag_content(llm_output: Dict[str, Any], target_codes: List[str], es_client) -> Optional[str]:
    """Elasticsearch'ten RAG içeriğini çeker ve formatlar."""
    istenen_kolonlar = llm_output.get('istenen_kolonlar', [])
    if "Fon_Kodu" not in istenen_kolonlar: istenen_kolonlar.append("Fon_Kodu")
    
    query = {
        "size": len(target_codes),
        "query": {"bool": {"filter": [{"terms": {"Fon_Kodu.keyword": target_codes}}]}},
        "_source": istenen_kolonlar
    }
    
    try:
        response = es_client.search(index="yatirim_fonlari", body=query)
        results = [hit['_source'] for hit in response['hits']['hits']]
        
        if not results:
            st.warning(f"Üzgünüm, `{', '.join(target_codes)}` kodlu fon(lar) için veritabanında bilgi bulamadım.")
            return None
            
        # RAG içeriğini formatla
        rag_parts = ["### İlgili Fon Bilgileri (RAG İçeriği) ###"]
        for doc in results:
            fon_kodu = doc.get('Fon_Kodu', 'Bilinmiyor')
            rag_parts.append(f"\n--- Fon Kodu: {fon_kodu} ---")
            for key, value in doc.items():
                if key == 'Fon_Kodu': continue
                rag_parts.append(f"- {key}: {value}")
        return "\n".join(rag_parts)
    except Exception as e:
        st.error(f"Veritabanı hatası: {e}")
        return None

# ==============================================================================
# BÖLÜM 4: LLM İLE ETKİLEŞİM FONKSİYONLARI
# ==============================================================================

def run_stage1_analysis(user_query, chat_history, tokenizer, model) -> Optional[Dict[str, Any]]:
    """1. Aşama: Kullanıcı sorusunu analiz edip JSON üretir."""
    if MOCK_LLM_CALLS:
        # Sahte LLM Çağrısı
        query_upper = user_query.upper()
        codes = [fon for fon in ["AFA", "TGE", "MAC", "IJP"] if fon in query_upper]
        if len(codes) > 1:
            return {"fon_kodlari": codes, "istenen_kolonlar": ["Risk_Getiri_Profili", "Strateji"], "follow_up": False, "follow_up_fon_kodu": None}
        if len(codes) == 1:
             return {"fon_kodlari": codes, "istenen_kolonlar": ["Fon_Adi", "Yillik_Yonetim_Ucreti"], "follow_up": False, "follow_up_fon_kodu": None}
        if "risk" in user_query.lower():
             return {"fon_kodlari": [], "istenen_kolonlar": ["Risk_Getiri_Profili"], "follow_up": True, "follow_up_fon_kodu": st.session_state.last_context_fund_codes[0] if st.session_state.last_context_fund_codes else None}
        return {"fon_kodlari": [], "istenen_kolonlar": ["Fon_Adi"], "follow_up": False, "follow_up_fon_kodu": None}

    # Gerçek LLM Çağrısı... (önceki koddaki gibi)
    return None

def run_stage3_generation(user_query, rag_content, is_comparison, tokenizer, model) -> str:
    """3. Aşama: RAG içeriğini kullanarak nihai cevabı üretir."""
    if MOCK_LLM_CALLS:
        return f"**(SAHTE CEVAP)**\nKullanıcının '{user_query}' sorusuna, aşağıdaki RAG içeriğine dayanarak cevap oluşturuluyor:\n\n{rag_content}"
    
    # Gerçek LLM Çağrısı... (önceki koddaki gibi)
    return "Gerçek LLM cevabı."

# ==============================================================================
# BÖLÜM 5: STREAMLIT ARAYÜZÜ VE UYGULAMA MANTIĞI
# ==============================================================================

st.set_page_config(page_title="Akıllı Fon Chatbot", page_icon="💡", layout="wide")

# --- Kenar Çubuğu ---
with st.sidebar:
    st.header("Ayarlar ve Bilgilendirme")
    if st.button("Sohbeti Temizle"):
        st.session_state.clear()
        st.rerun()

    st.info("""
        Bu uygulama, 3 aşamalı bir RAG mimarisi kullanır:
        1. **Analiz:** Soru JSON'a çevrilir.
        2. **Getir:** Veritabanından ilgili bilgi alınır.
        3. **Üret:** Alınan bilgiyle cevap oluşturulur.
    """)
    if MOCK_LLM_CALLS:
        st.warning("Uygulama şu anda 'MOCK' modunda çalışıyor. Gerçek LLM çağrıları yapılmamaktadır.")


# --- Ana Arayüz ---
st.title("💡 Akıllı Yatırım Fonu Chatbotu")

# Session State'i başlat
if "display_messages" not in st.session_state:
    st.session_state.display_messages = [{"role": "assistant", "content": "Merhaba! Analiz etmek veya karşılaştırmak istediğiniz fonlar hakkında bir soru sorun."}]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # LLM'e gönderilecek kısa geçmiş
if "last_context_fund_codes" not in st.session_state:
    st.session_state.last_context_fund_codes = [] # Konu takibi için

# Modelleri ve client'ı yükle
tokenizer, model = load_gemma_model()
es_client = get_es_client()

# Görüntüleme geçmişini ekrana yazdır
for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan girdi al
if prompt := st.chat_input("AFA fonunun riski nedir? AFA ve TGE fonlarını karşılaştır..."):
    # Kullanıcı mesajını görüntüleme geçmişine ekle
    st.session_state.display_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Botun cevap döngüsünü başlat
    with st.chat_message("assistant"):
        # ----- AŞAMA 1: SORGUNUN ANALİZİ -----
        analysis_placeholder = st.empty()
        with st.spinner("Mesajınız anlaşılıyor..."):
            llm_analysis_json = run_stage1_analysis(prompt, st.session_state.chat_history, tokenizer, model)

        if not llm_analysis_json:
            st.error("Soru analizi sırasında bir hata oluştu. Lütfen farklı bir şekilde sormayı deneyin.")
        else:
            with st.expander("LLM Analiz Sonucu (JSON)"):
                st.json(llm_analysis_json)
            
            # ----- KONU TAKİBİ VE GEÇMİŞ YÖNETİMİ -----
            current_target_codes = sorted(determine_target_codes(llm_analysis_json))
            last_codes = sorted(st.session_state.last_context_fund_codes)

            if current_target_codes and current_target_codes != last_codes:
                st.info("Yeni bir fon konusu başlatılıyor...")
                st.session_state.chat_history = []
                st.session_state.last_context_fund_codes = current_target_codes
            elif current_target_codes:
                 st.session_state.last_context_fund_codes = current_target_codes

            # ----- ARA GERİ BİLDİRİM -----
            interim_feedback = generate_interim_feedback(llm_analysis_json, current_target_codes)
            analysis_placeholder.info(interim_feedback)

            # ----- AŞAMA 2: VERİ ÇEKME -----
            rag_content = None
            if es_client and current_target_codes:
                with st.spinner("Veritabanından bilgiler alınıyor..."):
                    rag_content = fetch_rag_content(llm_analysis_json, current_target_codes, es_client)
                
                if rag_content:
                    with st.expander("Veritabanından Alınan RAG İçeriği"):
                        st.markdown(rag_content)
            
            # ----- AŞAMA 3: NİHAİ CEVAP ÜRETİMİ -----
            if rag_content:
                with st.spinner("Size özel cevap oluşturuluyor..."):
                    is_comparison = len(current_target_codes) > 1
                    final_answer = run_stage3_generation(prompt, rag_content, is_comparison, tokenizer, model)
                    st.markdown(final_answer)
                    
                    # Geçmişi güncelle
                    st.session_state.display_messages.append({"role": "assistant", "content": final_answer})
                    st.session_state.chat_history.extend([{"role": "user", "content": prompt}, {"role": "assistant", "content": final_answer}])
                    
                    # Geçmişi sınırla
                    while len(st.session_state.chat_history) > MAX_HISTORY_TURNS * 2:
                        st.session_state.chat_history.pop(0)
                        st.session_state.chat_history.pop(0)
            else:
                # RAG içeriği alınamadıysa veya gerekmiyorsa (genel sorular)
                st.write("Bu konuda size yardımcı olabilmem için daha spesifik bir fon kodu belirtebilir misiniz?")
                st.session_state.display_messages.append({"role": "assistant", "content": "Bu konuda size yardımcı olabilmem için daha spesifik bir fon kodu belirtebilir misiniz?"})















































Harika bir fikir\! Kodun modüler bir yapıya kavuşturulması, projenin yönetilebilirliği, okunabilirliği ve gelecekte geliştirilmesi açısından son derece doğru bir adımdır.

İsteğiniz doğrultusunda, tüm uygulamayı 4 ayrı Python dosyasına ve bir `requirements.txt` dosyasına bölerek yeniden düzenledim.

### Proje Dosya Yapısı

Uygulamanızı çalıştırmak için aşağıdaki gibi bir klasör yapısı oluşturun:

```
/yatirim_chatbot/
|
|-- 📄 config.py
|-- 📄 retriever.py
|-- 📄 generator.py
|-- 📄 app.py
|-- 📄 requirements.txt
```

-----

### 1\. `requirements.txt`

Bu dosyaya projenin ihtiyaç duyduğu kütüphaneleri ekleyin.

```text
streamlit
elasticsearch
torch
transformers
accelerate
```

Kurulum için terminalde projenizin ana dizinindeyken şu komutu çalıştırabilirsiniz: `pip install -r requirements.txt`

-----

### 2\. `config.py`

Bu dosya, tüm sistem prompt'larını ve genel yapılandırma ayarlarını içerecektir.

```python
# config.py

# --- Genel Yapılandırma ---
MOCK_LLM_CALLS: bool = True
HF_MODEL_ID: str = "google/gemma-2b-it" # Hugging Face'deki model kimliği
MAX_HISTORY_TURNS: int = 3 # LLM'e gönderilecek maksimum konuşma turu sayısı
ES_INDEX_NAME: str = "yatirim_fonlari" # Elasticsearch index adı

# --- Aşama 1: Analiz Prompt'u (İngilizce) ---
STAGE_1_ANALYSIS_PROMPT: str = """
# SYSTEM PROMPT: CONTEXT-AWARE INVESTMENT QUERY ANALYSIS ENGINE
## 1. Core Task and Persona
You are an expert who analyzes and structures user queries about investment funds. Your job is NOT to answer the user directly. You will be given the **Current User Query** and the preceding **Conversation History**. Your sole and only purpose is to analyze these inputs and produce a **JSON object** that conforms to the rules and format specified below.

## 2. Input Structure You Will Receive
{
  "current_query": "The user's latest message.",
  "history": [
    {"role": "user", "content": "The user's previous message."},
    {"role": "bot", "content": "Your previous answer."}
  ]
}

## 3. Output Format You Must Produce
{
  "fon_kodlari": ["string"],
  "istenen_kolonlar": ["string"],
  "follow_up": "boolean",
  "follow_up_fon_kodu": "string | null"
}

## 4. Analysis Rules
- **`follow_up` Rule:** Analyze if the current query is a continuation of the conversation history. Set to `true` or `false`.
- **`follow_up_fon_kodu` Rule:** If `follow_up` is `true`, find the most recently mentioned fund code in the history and place it here. Otherwise, it must be `null`.
- **`fon_kodlari` Rule:** Find ALL 3-letter uppercase fund codes present **only in the Current User Query** and list them here.
- **`istenen_kolonlar` Rule:** Analyze the user's intent in the current query and list the corresponding database column names.
    - For general queries ('hakkında bilgi', 'detaylar'), use a default set like `["Fon_Adi", "Strateji", "Risk_Getiri_Profili"]`.
    - For comparison queries ('farkı ne', 'kıyasla'), use a default set like `["Strateji", "Risk_Getiri_Profili", "Yillik_Yonetim_Ucreti"]`.
    - For specific queries, map keywords to columns (e.g., "yönetim ücreti" -> `Yillik_Yonetim_Ucreti`).
"""

# --- Aşama 3: Cevap Üretme Prompt'ları (İngilizce) ---
FINAL_PROMPT_SINGLE: str = """# TASK\nAnswer the user's question naturally and clearly using only the structured data provided in the 'GIVEN DATA (CONTEXT)' section. Do not add information from external sources.\n\n# GIVEN DATA (CONTEXT)\n{context_data}\n\n# USER'S QUESTION\n"{user_question}"\n\n# ANSWER\n"""
FINAL_PROMPT_COMPARISON: str = """# TASK\nCompare the funds for the user based on their question, using only the structured data provided in the 'GIVEN DATA (CONTEXT)' section. Highlight key differences and similarities. Format the answer clearly, using bullet points or a table.\n\n# GIVEN DATA (CONTEXT)\nThe following is the data for the funds to be compared:\n{context_data}\n\n# USER'S QUESTION\n"{user_question}"\n\n# ANSWER\n"""

```

-----

### 3\. `retriever.py`

Bu dosya, Elasticsearch ile ilgili tüm fonksiyonları barındırır: bağlantı kurma, sorgu oluşturma ve veri çekme/formatlama.

```python
# retriever.py

import streamlit as st
from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional

@st.cache_resource
def get_es_client() -> Optional[Elasticsearch]:
    """Elasticsearch client nesnesi oluşturur ve cache'ler."""
    try:
        # Kendi Elasticsearch bağlantı bilgilerinizi buraya girin
        client = Elasticsearch("http://localhost:9200")
        if not client.ping():
            raise ConnectionError("Bağlantı başarısız.")
        return client
    except Exception:
        return None

def determine_target_codes(llm_output: Dict[str, Any]) -> List[str]:
    """LLM çıktısına göre sorgulanacak hedef fon kodlarının listesini belirler."""
    fon_kodlari = llm_output.get('fon_kodlari', [])
    if fon_kodlari:
        return fon_kodlari
    if llm_output.get('follow_up') and llm_output.get('follow_up_fon_kodu'):
        return [llm_output.get('follow_up_fon_kodu')]
    return []

def build_es_query(target_codes: List[str], istenen_kolonlar: List[str]) -> Dict[str, Any]:
    """Hedef kodlar ve kolonlara göre Elasticsearch DSL sorgusunu oluşturur."""
    if "Fon_Kodu" not in istenen_kolonlar:
        istenen_kolonlar.append("Fon_Kodu")
    
    return {
        "size": len(target_codes),
        "query": {"bool": {"filter": [{"terms": {"Fon_Kodu.keyword": target_codes}}]}},
        "_source": istenen_kolonlar
    }

def format_rag_content(es_results: List[Dict[str, Any]]) -> str:
    """Elasticsearch sonuçlarını, LLM'in anlayacağı temiz bir RAG metnine dönüştürür."""
    rag_parts = ["### İlgili Fon Bilgileri (RAG İçeriği) ###"]
    for doc in es_results:
        fon_kodu = doc.get('Fon_Kodu', 'Bilinmeyen Fon')
        rag_parts.append(f"\n--- Fon Kodu: {fon_kodu} ---")
        for key, value in doc.items():
            if key == 'Fon_Kodu':
                continue
            rag_parts.append(f"- {key}: {value}")
    return "\n".join(rag_parts)

def fetch_rag_content(llm_output: Dict[str, Any], es_client: Elasticsearch, index_name: str) -> Tuple[Optional[str], List[str]]:
    """Ana RAG getirme fonksiyonu: ES'i sorgular ve formatlanmış içeriği döndürür."""
    target_codes = determine_target_codes(llm_output)
    if not target_codes:
        return "Herhangi bir spesifik fon kodu belirtilmedi.", target_codes

    istenen_kolonlar = llm_output.get('istenen_kolonlar', [])
    query = build_es_query(target_codes, istenen_kolonlar)
    
    try:
        response = es_client.search(index=index_name, body=query)
        results = [hit['_source'] for hit in response['hits']['hits']]
        
        if not results:
            return f"Üzgünüm, `{', '.join(target_codes)}` kodlu fon(lar) için veritabanında bilgi bulamadım.", target_codes

        return format_rag_content(results), target_codes
    except Exception as e:
        return f"Veritabanı hatası: {e}", target_codes
```

-----

### 4\. `generator.py`

Bu dosya, Hugging Face Gemma modeli ile ilgili tüm işlemleri içerir: modeli yükleme ve prompt'lara göre metin üretme.

```python
# generator.py

import streamlit as st
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Optional, Tuple

# Prompt'ları ve konfigürasyonları config dosyasından import et
import config

@st.cache_resource
def load_gemma_model() -> Optional[Tuple[AutoTokenizer, AutoModelForCausalLM]]:
    """Hugging Face'den Gemma modelini ve tokenizer'ı yükler ve cache'ler."""
    if config.MOCK_LLM_CALLS:
        return None, None
    try:
        tokenizer = AutoTokenizer.from_pretrained(config.HF_MODEL_ID)
        model = AutoModelForCausalLM.from_pretrained(
            config.HF_MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        return tokenizer, model
    except Exception as e:
        st.error(f"Model yüklenirken bir hata oluştu: {e}")
        return None, None

def run_stage1_analysis(user_query: str, chat_history: List[Dict[str, str]], tokenizer, model) -> Optional[Dict[str, Any]]:
    """1. Aşama: Kullanıcı sorusunu analiz edip JSON üretir."""
    if config.MOCK_LLM_CALLS:
        # Sahte LLM Çağrısı
        query_upper = user_query.upper()
        codes = [fon for fon in ["AFA", "TGE", "MAC", "IJP"] if fon in query_upper]
        if len(codes) > 1: return {"fon_kodlari": codes, "istenen_kolonlar": ["Risk_Getiri_Profili", "Strateji"], "follow_up": False, "follow_up_fon_kodu": None}
        if len(codes) == 1: return {"fon_kodlari": codes, "istenen_kolonlar": ["Fon_Adi", "Yillik_Yonetim_Ucreti"], "follow_up": False, "follow_up_fon_kodu": None}
        if "risk" in user_query.lower() and st.session_state.last_context_fund_codes: return {"fon_kodlari": [], "istenen_kolonlar": ["Risk_Getiri_Profili"], "follow_up": True, "follow_up_fon_kodu": st.session_state.last_context_fund_codes[0]}
        return {"fon_kodlari": [], "istenen_kolonlar": ["Fon_Adi"], "follow_up": False, "follow_up_fon_kodu": None}

    # Gerçek LLM Çağrısı
    prompt = f"{config.STAGE_1_ANALYSIS_PROMPT}\n\n# Input\n{json.dumps({'current_query': user_query, 'history': chat_history}, ensure_ascii=False)}\n\n# Output\n"
    # ... Gerçek model çalıştırma kodu ...
    return None # Placeholder

def run_stage3_generation(user_query: str, rag_content: str, is_comparison: bool, tokenizer, model) -> str:
    """3. Aşama: RAG içeriğini kullanarak nihai cevabı üretir."""
    if config.MOCK_LLM_CALLS:
        return f"**(SAHTE CEVAP)**\nKullanıcının '{user_query}' sorusuna, aşağıdaki RAG içeriğine dayanarak cevap oluşturuluyor:\n\n{rag_content}"

    # Gerçek LLM Çağrısı
    prompt_template = config.FINAL_PROMPT_COMPARISON if is_comparison else config.FINAL_PROMPT_SINGLE
    final_prompt = prompt_template.format(context_data=rag_content, user_question=user_query)
    # ... Gerçek model çalıştırma kodu ...
    return "Gerçek LLM cevabı."
```

-----

### 5\. `app.py`

Bu dosya, uygulamanızın ana giriş noktasıdır. Tüm Streamlit arayüzünü oluşturur ve diğer modüllerdeki fonksiyonları çağırarak iş akışını yönetir.

```python
# app.py

import streamlit as st
from typing import List, Dict, Any

# Diğer modüllerden gerekli fonksiyonları ve değişkenleri import et
import config
from retriever import get_es_client, fetch_rag_content
from generator import load_gemma_model, run_stage1_analysis, run_stage3_generation

def generate_interim_feedback(analysis_json: Dict[str, Any], target_codes: List[str]) -> str:
    """Kullanıcıya botun ne anladığını söyleyen ara geri bildirim metni oluşturur."""
    if not target_codes: return "Anladım, genel bir arama yapıyorum..."
    is_comparison = len(target_codes) > 1
    if is_comparison: return f"Anladım. `{', '.join(target_codes)}` kodlu fonları karşılaştırmak için bilgi topluyorum..."
    
    fon_kodu = target_codes[0]
    if analysis_json.get("follow_up") and not analysis_json.get("fon_kodlari"):
        return f"Tabii, bir önceki konumuz olan `{fon_kodu}` fonu hakkında devam ediyorum..."
    else:
        return f"Anladım, `{fon_kodu}` kodlu fon hakkında bilgi arıyorum..."

def main():
    """Ana Streamlit uygulamasını çalıştırır."""
    st.set_page_config(page_title="Akıllı Fon Chatbot", page_icon="💡", layout="wide")

    with st.sidebar:
        st.header("Ayarlar ve Bilgilendirme")
        if st.button("Sohbeti Temizle"):
            st.session_state.clear()
            st.rerun()
        st.info("Bu uygulama, 3 aşamalı bir RAG mimarisi kullanır.")
        if config.MOCK_LLM_CALLS:
            st.warning("Uygulama 'MOCK' modunda çalışıyor.")

    st.title("💡 Akıllı Yatırım Fonu Chatbotu")

    # Session State'i başlat
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = [{"role": "assistant", "content": "Merhaba! Analiz etmek veya karşılaştırmak istediğiniz fonlar hakkında bir soru sorun."}]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_context_fund_codes" not in st.session_state:
        st.session_state.last_context_fund_codes = []

    # Modelleri ve client'ları yükle
    tokenizer, model = load_gemma_model()
    es_client = get_es_client()

    for message in st.session_state.display_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("AFA fonunun riski nedir? AFA ve TGE fonlarını karşılaştır..."):
        st.session_state.display_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            analysis_placeholder = st.empty()
            with st.spinner("Mesajınız anlaşılıyor... (Aşama 1)"):
                llm_analysis_json = run_stage1_analysis(prompt, st.session_state.chat_history, tokenizer, model)

            if not llm_analysis_json:
                st.error("Soru analizi başarısız oldu. Lütfen tekrar deneyin.")
                return

            with st.expander("LLM Analiz Sonucu (JSON)"):
                st.json(llm_analysis_json)
            
            rag_content, target_codes = fetch_rag_content(llm_analysis_json, es_client)
            
            # Konu takibi ve geçmiş yönetimi
            current_target_codes = sorted(target_codes)
            if current_target_codes and current_target_codes != sorted(st.session_state.last_context_fund_codes):
                analysis_placeholder.info("Yeni bir fon konusu başlatılıyor...")
                st.session_state.chat_history = []
            st.session_state.last_context_fund_codes = current_target_codes

            interim_feedback = generate_interim_feedback(llm_analysis_json, current_target_codes)
            analysis_placeholder.info(interim_feedback)

            if rag_content and "hata" not in rag_content.lower() and "bulunamadı" not in rag_content.lower():
                with st.expander("Veritabanından Alınan RAG İçeriği"):
                    st.markdown(rag_content)

                with st.spinner("Size özel cevap oluşturuluyor... (Aşama 3)"):
                    is_comparison = len(current_target_codes) > 1
                    final_answer = run_stage3_generation(prompt, rag_content, is_comparison, tokenizer, model)
                    st.markdown(final_answer)
                    
                    st.session_state.display_messages.append({"role": "assistant", "content": final_answer})
                    st.session_state.chat_history.extend([{"role": "user", "content": prompt}, {"role": "assistant", "content": final_answer}])
                    
                    while len(st.session_state.chat_history) > config.MAX_HISTORY_TURNS * 2:
                        st.session_state.chat_history.pop(0)
                        st.session_state.chat_history.pop(0)
            else:
                st.write(rag_content) # Hata veya bilgi bulunamadı mesajını yazdır
                st.session_state.display_messages.append({"role": "assistant", "content": rag_content})

if __name__ == "__main__":
    main()
```

### Nasıl Çalıştırılır?

1.  Yukarıdaki 5 dosyayı (`requirements.txt`, `config.py`, `retriever.py`, `generator.py`, `app.py`) aynı klasör (`yatirim_chatbot`) içine kaydedin.
2.  Terminali açın, bu klasörün içine girin.
3.  `pip install -r requirements.txt` komutuyla kütüphaneleri kurun.
4.  `streamlit run app.py` komutuyla uygulamayı başlatın.

Bu modüler yapı, projenizin her bir parçasını bağımsız olarak geliştirmenize ve test etmenize olanak tanıyarak çok daha profesyonel ve sürdürülebilir bir altyapı sunar.


