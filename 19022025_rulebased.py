
PROMPT_1 """ = 
**Role:** You are a campaign analyst who extracts campaign codes, campaign headers, and campaign responsibilities from the user's input and provides answers in JSON format.

**Prompt:**
Analyze the user's input and associate it with only one of the following questions. If none of the five conditions are met, return:
```json
{
  "ANSWER": "NO2"
}
```

1. **Is there a campaign code in the question?**
   - A campaign code is always a 5, 6, or 7-digit integer value.
   - If you find a campaign code, respond in the following JSON format:
     ```json
     {
       "campaign_code": campaign_code_value
     }
     ```

2. **Is the user referring to a specific campaign header?**
   - A specific campaign header means the user is looking for information about a named or clearly defined campaign.
   - Example keywords: "Migros İndirim Kampanyası", "Yaz Fırsatları", "Öğrenci İndirimi"
   - If a specific campaign header is mentioned, respond in the following JSON format:
     ```json
     {
       "spesific_campaign_header": spesific_campaign_header_name
     }
     ```

3. **Is the user asking about general campaign information?**
   - A general campaign query is when the user is not referring to a specific campaign but wants an overview of multiple campaigns, discounts, or promotions.
   - Example keywords: "Migros kampanyalar nelerdir?", "Şu an hangi indirimler var?", "Kampanyalar hakkında bilgi verir misiniz?"
   - If the question is about general campaign information, respond in the following JSON format:
     ```json
     {
       "general_campaign_header": general_campaign_header_name
     }
     ```

4. **Is the user asking about both the campaign responsible person and the campaign code at the same time?**
   - If yes, respond in the following JSON format:
     ```json
     {
       "campaign_responsible": "YES",
       "campaign_code": campaign_code_value
     }
     ```

5. **Is the user asking about both the campaign responsible person and a specific campaign header at the same time?**
   - If yes, respond in the following JSON format:
     ```json
     {
       "campaign_responsible": "YES",
       "Spesific_campaign_header": Spesific_campaign_header_name
     }
     ```

**Examples:**

**Example 1:**
Input: "Kampanya kodu 123456 olan kampanyanın detaylarını paylaşır mısınız?"
Output:
```json
{
  "campaign_code": 123456
}
```

**Example 2:**
Input: "Migros’un indirim kampanyaları hakkında bilgi alabilir miyim?"
Output:
```json
{
  "general_campaign_header": "Migros Kampanyaları"
}
```

**Example 3:**
Input: "X kampanyasının bitiş tarihi nedir?"
Output:
```json
{
  "spesific_campaign_header": "X Kampanyası"
}
```

**Example 4:**
Input: "Kampanya kodu 789012 ve sorumlusu kim?"
Output:
```json
{
  "campaign_responsible": "YES",
  "campaign_code": 789012
}
```

**Example 5:**
Input: "Migros İndirim Kampanyası’nın sorumlusu kimdir?"
Output:
```json
{
  "campaign_responsible": "YES",
  "spesific_campaign_header": "Migros İndirim Kampanyası"
}
```

**Important:** Always provide responses in Turkish.
"""


# POST PROCESS FONKSIYONU

import json

def process_campaign_response(json_response):
    """
    Gelen JSON yanıtını işleyerek kampanya ile ilgili anlamlı bir çıktı döndürür.
    
    Args:
        json_response (str): JSON formatındaki kampanya yanıtı.
        
    Returns:
        dict: Kampanya bilgisiyle ilgili tüm değerleri içeren yapı.
    """
    try:
        response = json.loads(json_response)
        result = {}

        # Kampanya kodu varsa ekle
        if "campaign_code" in response:
            result["campaign_code"] = response["campaign_code"]

        # Spesifik kampanya başlığı varsa ekle (bir soruda sadece bir tane olabilir!)
        if "spesific_campaign_header" in response:
            result["spesific_campaign_header"] = response["spesific_campaign_header"]

        # Genel kampanya başlığı varsa ekle (bir soruda sadece bir tane olabilir!)
        if "general_campaign_header" in response:
            result["general_campaign_header"] = response["general_campaign_header"]

        # Kampanya sorumlusu bilgisi varsa ekle
        if "campaign_responsible" in response:
            result["campaign_responsible"] = response["campaign_responsible"]

        # Eğer hiçbir kategoriye uymuyorsa NO2 döndür
        if "ANSWER" in response and response["ANSWER"] == "NO2":
            return {"NO2": "NO"}  

        return result

    except json.JSONDecodeError:
        return {"error": "Geçersiz JSON formatı"}

# Örnek Kullanım
json_examples = [
    '{"campaign_code": 123456}',  # Kampanya kodu
    '{"general_campaign_header": "Migros Kampanyaları"}',  # Genel kampanya
    '{"spesific_campaign_header": "Yaz Fırsatları"}',  # Spesifik kampanya
    '{"campaign_responsible": "YES", "campaign_code": 789012}',  # Kampanya sorumlusu + kod
    '{"campaign_responsible": "YES", "spesific_campaign_header": "Öğrenci İndirimi"}',  # Kampanya sorumlusu + spesifik kampanya
    '{"ANSWER": "NO2"}'  # Koşulları sağlamayan input
]

for example in json_examples:
    print(process_campaign_response(example))










FOLLOW_UP_PROMPT = """
**Role:** You are an intelligent assistant designed to analyze user inquiries and determine if a new question is a follow-up to a previous question. You will examine both the last asked question and its answer to decide if the user is continuing the conversation about the same campaign.

**Prompt:**
Analyze the new user question and compare it with the last user question and answer. Determine if the new question is a follow-up or not.

- If the new question is **not related** to the last question and answer, respond with:
  ```json
  {
    "ANSWER": "NO3"
  }
  ```

- If the new question **is related** to the last question and answer, determine whether it continues referring to a specific campaign by checking for either a **campaign code** or a **specific campaign header**. Then respond accordingly:
  - If the follow-up question refers to a **campaign code**, respond with:
    ```json
    {
      "follow_up": "YES",
      "follow_up_campaign_code": campaign_code_value
    }
    ```
  
  - If the follow-up question refers to a **specific campaign header**, respond with:
    ```json
    {
      "follow_up": "YES",
      "follow_up_specific_campaign_header": specific_campaign_header_value
    }
    ```

**Examples:**

**Example 1:**
```json
{
  "last_history_question": "Kampanya kodu 123456 olan kampanya hangi indirimleri kapsıyor?",
  "last_history_answer": "Bu kampanya market ürünlerinde %10 indirim sunmaktadır.",
  "new_question": "Bu kampanya ne zamana kadar geçerli?"
}
```
**Response:**
```json
{
  "follow_up": "YES",
  "follow_up_campaign_code": 123456
}
```

**Example 2:**
```json
{
  "last_history_question": "Migros İndirim Kampanyası hakkında bilgi verir misiniz?",
  "şast_history_answer": "Migros İndirim Kampanyası market alışverişlerinde %20 indirim sağlar.",
  "new_question": "Bu kampanyadan nasıl faydalanabilirim?"
}
```
**Response:**
```json
{
  "follow_up": "YES",
  "follow_up_specific_campaign_header": "Migros İndirim Kampanyası"
}
```

**Example 3:**
```json
{
  "last_history_question": "Kampanya kodu 789012 olan kampanya hangi kategorilerde geçerli?",
  "last_history_answer": "Bu kampanya elektronik ve beyaz eşyalarda geçerlidir.",
  "new_question": "Telefon aksesuarları da dahil mi?"
}
```
**Response:**
```json
{
  "follow_up": "YES",
  "follow_up_campaign_code": 789012
}
```

**Example 4:**
```json
{
  "last_history_question": "Migros kampanyaları hakkında bilgi verir misiniz?",
  "last_history_answer": "Migros şu an market alışverişlerinde birçok farklı kampanya sunmaktadır.",
  "new_question": "Boyner kampanyaları nelerdir?"
}
```
**Response:**
```json
{
  "ANSWER": "NO3"
}
```

**Important:** Always provide responses in Turkish.


"""

# POST PROCESS FONKSIYONU

import json

def extract_follow_up_data(json_response):
    """
    Gelen JSON yanıtını işleyerek, kullanıcının yeni sorusunun önceki soruya bağlı olup olmadığını belirler.
    
    Args:
        json_response (str): JSON formatındaki input verisi.
        
    Returns:
        dict: Doğru formatta takip bilgisi içeren JSON yanıtı.
    """
    try:
        response = json.loads(json_response)
        result = {}

        # Eğer yeni soru önceki soru ve cevaba bağlı değilse NO3 döndür
        if "ANSWER" in response and response["ANSWER"] == "NO3":
            return {"ANSWER": "NO3"}

        # Kampanya kodu varsa JSON çıktısına ekle
        if "follow_up_campaign_code" in response:
            result["follow_up"] = "YES"
            result["follow_up_campaign_code"] = response["follow_up_campaign_code"]

        # Spesifik kampanya başlığı varsa JSON çıktısına ekle
        elif "follow_up_specific_campaign_header" in response:
            result["follow_up"] = "YES"
            result["follow_up_specific_campaign_header"] = response["follow_up_specific_campaign_header"]

        return result

    except json.JSONDecodeError:
        return {"error": "Geçersiz JSON formatı"}

# Örnek Kullanım
json_examples = [
    '{"follow_up": "YES", "follow_up_campaign_code": 123456}',  # Kampanya kodu olan takip sorusu
    '{"follow_up": "YES", "follow_up_specific_campaign_header": "Migros İndirim Kampanyası"}',  # Spesifik kampanya başlığı olan takip sorusu
    '{"ANSWER": "NO3"}'  # İlgisiz yeni soru
]

for example in json_examples:
    print(extract_follow_up_data(example))




###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################



import json
import streamlit as st
from collections import deque
from openai import AzureOpenAI
import os
from elastic_search_retriever_embedding import ElasticTextSearch

# ElasticSearch bağlantısı için instance oluşturma
es = ElasticTextSearch()

# PROMPT TANIMLARI
PROMPT_1 = """**Role:** Kampanya analisti... [Yukarıdaki PROMPT_1 içeriği]"""
FOLLOW_UP_PROMPT = """**Role:** Akıllı asistan... [Yukarıdaki FOLLOW_UP_PROMPT içeriği]"""

# OPENAI KONFİGÜRASYONU
def initialize_openai_client():
    """Azure OpenAI istemcisini başlatır"""
    return AzureOpenAI(
        api_key=st.secrets["AZURE_API_KEY"],
        api_version=st.secrets["AZURE_API_VERSION"],
        azure_endpoint=st.secrets["AZURE_ENDPOINT"]
    )

# POST-PROCESS FONKSİYONLARI
def process_campaign_response(json_str):
    """PROMPT_1'den gelen ham JSON çıktısını işler"""
    try:
        data = json.loads(json_str)
        # NO2 durumunda özel işaret döndür
        if data.get("ANSWER") == "NO2":
            return {"status": "NO2"}
        # Geçerli verileri filtrele
        return {k: v for k, v in data.items() if k != "ANSWER"}
    except Exception as e:
        st.error(f"JSON parse hatası: {str(e)}")
        return {"error": "Invalid JSON"}

def extract_follow_up_data(json_str):
    """Follow-up promptundan gelen verileri işler"""
    try:
        data = json.loads(json_str)
        # NO3 durumunda özel işaret
        if data.get("ANSWER") == "NO3":
            return {"status": "NO3"}
        return data
    except Exception as e:
        st.error(f"Follow-up parse hatası: {str(e)}")
        return {"error": "Invalid JSON"}

# DİYALOG YÖNETİCİSİ
class DialogManager:
    """Konuşma geçmişini ve context'i yöneten sınıf"""
    
    def __init__(self):
        # Session state ilk yüklemede initialize et
        if "history" not in st.session_state:
            st.session_state.history = deque(maxlen=3)  # Son 3 mesajı sakla
            st.session_state.context = None
            st.session_state.current_flow = "INITIAL"

    def reset_conversation(self):
        """Tüm konuşma geçmişini temizler"""
        st.session_state.history.clear()
        st.session_state.context = None
        st.session_state.current_flow = "INITIAL"
        st.success("Yeni konuşma başlatıldı!")

    def conditional_add_to_history(self, user_input, response, is_responsible_query):
        """
        Kampanya sorumlusu sorgularını geçmişe EKLEMEZ
        Diğer tüm sorguları son 3 mesaj limitiyle kaydeder
        """
        if not is_responsible_query:
            st.session_state.history.append({
                "user": user_input,
                "bot": response,
                "timestamp": datetime.now().isoformat()
            })

# ANALİZ FONKSİYONLARI
def analyze_query(client, prompt_template, user_input, history=""):
    """OpenAI ile sorgu analizi yapar"""
    messages = [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Geçmiş: {history}\nSoru: {user_input}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=st.secrets["DEPLOYMENT_NAME"],
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"OpenAI sorgu hatası: {str(e)}")
        return {"error": "API hatası"}

# ANA İŞLEM FONKSİYONU
def process_user_input(user_input):
    """Kullanıcı girdisini işleyen ana fonksiyon"""
    
    # 1. Adım: Gerekli bileşenleri initialize et
    dialog = DialogManager()
    client = initialize_openai_client()
    is_responsible_query = False  # Kritik bayrak

    # 2. Adım: Temel sorgu analizi
    base_analysis = analyze_query(client, PROMPT_1, user_input)
    processed_data = process_campaign_response(json.dumps(base_analysis))

    # 3. Adım: Kampanya sorumlusu sorgusu kontrolü
    if processed_data.get("campaign_responsible") == "YES":
        is_responsible_query = True
        dialog.reset_conversation()
        st.toast("⚠️ Kampanya sorumlusu sorgusu - Geçmiş temizlendi!", icon="⚠️")
        
        # Sorumlu sorgusunu geçmişe EKLEME
        return  # Hemen çıkış yap

    # 4. Adım: Follow-up kontrol (Sadece normal sorgularda)
    follow_up_result = {}
    if st.session_state.context and not is_responsible_query:
        follow_up_analysis = analyze_query(
            client, FOLLOW_UP_PROMPT, 
            user_input, 
            st.session_state.context.get("last_response", "")
        )
        follow_up_result = extract_follow_up_data(json.dumps(follow_up_analysis))
        
        # NO3 durumunda akışı sıfırla
        if follow_up_result.get("status") == "NO3":
            dialog.reset_conversation()
            return

    # 5. Adım: Context belirleme
    context = {}
    if processed_data.get("campaign_code"):
        context["type"] = "CODE"
        context["value"] = processed_data["campaign_code"]
    elif processed_data.get("spesific_campaign_header"):
        context["type"] = "HEADER"
        context["value"] = processed_data["spesific_campaign_header"]
    else:
        context["type"] = "GENERAL"

    # 6. Adım: ElasticSearch veri çekme
    try:
        if context["type"] == "CODE":
            campaign_data = es.get_best_related(context["value"])
            st.success(f"🔑 Kampanya Kodu: {context['value']}")
        elif context["type"] == "HEADER":
            campaign_data = es.search_campaign_by_header(context["value"])
            st.success(f"📌 Kampanya Başlığı: {context['value']}")
        else:
            campaign_data = es.search_general_campaigns()
            st.info("🔍 Genel kampanya listesi getiriliyor...")
    except Exception as e:
        st.error(f"📛 Veri çekme hatası: {str(e)}")
        return

    # 7. Adım: GPT ile yanıt oluşturma
    try:
        response = client.chat.completions.create(
            model=st.secrets["DEPLOYMENT_NAME"],
            messages=[{
                "role": "system",
                "content": f"""## KONTEXT BİLGİLERİ ##
                Kampanya Verisi: {json.dumps(campaign_data)}
                Kullanıcı Geçmişi: {list(st.session_state.history)}"""
            },{
                "role": "user",
                "content": user_input
            }]
        )
        bot_response = response.choices[0].message.content
    except Exception as e:
        st.error(f"🤖 Yanıt oluşturma hatası: {str(e)}")
        return

    # 8. Adım: Geçmişe KAYIT (Sorumlu sorguları hariç)
    dialog.conditional_add_to_history(
        user_input, 
        bot_response,
        is_responsible_query
    )

    # 9. Adım: Context güncelleme
    st.session_state.context = {
        "last_question": user_input,
        "last_response": bot_response,
        "query_type": context["type"]
    }

    # 10. Adım: Kullanıcıya gösterim
    st.subheader("🤖 Asistan Yanıtı")
    st.markdown(bot_response)
    
    # Debug paneli
    with st.expander("⚙️ Sistem Detayları"):
        st.json({
            "base_analysis": base_analysis,
            "processed_data": processed_data,
            "context": context,
            "elastic_data": campaign_data,
            "is_responsible_query": is_responsible_query
        })

# STREAMLIT ARAYÜZ KONFİGÜRASYONU
st.title("🎯 Akıllı Kampanya Asistanı")
st.caption("Son 3 mesaj saklanır | Sorumlu sorguları geçmişe kaydedilmez")

# Kullanıcı girdisi
user_input = st.chat_input("Sorunuzu buraya yazın...")
if user_input:
    process_user_input(user_input)

# Konuşma geçmişi gösterimi
st.subheader("🗨️ Konuşma Geçmişi")
if st.session_state.history:
    for msg in st.session_state.history:
        st.markdown(f"**👤 Kullanıcı:** {msg['user']}")
        st.markdown(f"**🤖 Asistan:** {msg['bot']}")
        st.divider()
else:
    st.info("Henüz konuşma geçmişi yok.")

# Manuel reset butonu
if st.button("🔄 Konuşmayı Sıfırla"):
    DialogManager().reset_conversation()









#######################################################################################

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################








import json
import streamlit as st
from collections import deque
from openai import AzureOpenAI
from elastic_search_retriever_embedding import ElasticTextSearch

# ----------------------
# 1. SABİT TANIMLAMALAR
# ----------------------
MAX_HISTORY = 3  # Maksimum konuşma geçmişi boyutu
PROMPT_1 = """[PROMPT_1 içeriği buraya]"""
FOLLOW_UP_PROMPT = """[FOLLOW_UP_PROMPT içeriği buraya]"""

# ----------------------
# 2. OPENAI KONFİGÜRASYONU
# ----------------------
def initialize_openai_client():
    """Azure OpenAI istemcisini başlatır ve session state'e kaydeder"""
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = AzureOpenAI(
            api_key=st.secrets["AZURE_API_KEY"],
            api_version=st.secrets["AZURE_API_VERSION"],
            azure_endpoint=st.secrets["AZURE_ENDPOINT"]
        )
    return st.session_state.openai_client

# ----------------------
# 3. DİYALOG YÖNETİCİSİ
# ----------------------
class DialogManager:
    """Konuşma geçmişini ve context durumunu yönetir"""
    
    def __init__(self):
        # Session state başlatma
        if "history" not in st.session_state:
            st.session_state.history = deque(maxlen=MAX_HISTORY)  # Son 3 mesaj
            st.session_state.active_context = None  # Mevcut konuşma bağlamı
            st.session_state.active_campaign = None  # İşlenen aktif kampanya

    def update_history(self, user_input, bot_response, add_to_history=True):
        """Geçmişi koşullu olarak günceller"""
        if add_to_history:
            st.session_state.history.append({
                "user": user_input,
                "bot": bot_response
            })

    def handle_context(self, processed_data):
        """
        Context ve active_campaign açıklaması:
        - active_context: Kullanıcının son sorgu tipini tutar (genel/spesifik)
        - active_campaign: İşlem yapılan spesifik kampanya bilgilerini içerir
        """
        if processed_data.get("campaign_code"):
            st.session_state.active_campaign = {
                "type": "CODE",
                "value": processed_data["campaign_code"],
                "responsible": None
            }
        elif processed_data.get("spesific_campaign_header"):
            st.session_state.active_campaign = {
                "type": "HEADER",
                "value": processed_data["spesific_campaign_header"],
                "responsible": None
            }
        else:
            st.session_state.active_context = "GENEL_ARAMA"

# ----------------------
# 4. ELASTICSEARCH OPERASYONLARI
# ----------------------
class ElasticDummyOperations:
    """Sahte ElasticSearch operasyonları"""
    
    @staticmethod
    def find_responsible(campaign_info):
        """Kampanya sorumlusu için dummy veri"""
        return {
            "responsible_name": "Ahmet Yılmaz",
            "contact": "ahmet.yilmaz@sirket.com",
            "department": "Kampanya Yönetimi"
        }

# ----------------------
# 5. ANA İŞLEM AKIŞI
# ----------------------
def process_user_input(user_input):
    """Kullanıcı girdisini işleyen ana fonksiyon"""
    
    # 5.1 Gerekli bileşenleri başlat
    dialog = DialogManager()
    client = initialize_openai_client()
    es = ElasticTextSearch()
    dummy_es = ElasticDummyOperations()

    # 5.2 Temel sorgu analizi
    base_response = analyze_query(client, PROMPT_1, user_input)
    processed_data = process_campaign_response(base_response)

    # 5.3 Kampanya sorumlusu sorgusu kontrolü
    if processed_data.get("campaign_responsible") == "YES":
        # Sorumlu bilgisi için özel işlem
        if st.session_state.active_campaign:
            responsible_info = dummy_es.find_responsible(st.session_state.active_campaign)
            response = f"""
            🕴️ **Kampanya Sorumlusu Bilgisi:**
            - İsim: {responsible_info['responsible_name']}
            - Departman: {responsible_info['department']}
            - İletişim: {responsible_info['contact']}
            """
            st.markdown(response)
            # Geçmişe EKLEME ve context'i değiştirme
            dialog.update_history(user_input, response, add_to_history=False)
            return

    # 5.4 Diğer işlemler (önceki kodun devamı)
    # ... (Veri çekme, GPT yanıtı oluşturma vs.)

# ----------------------
# 6. STREAMLIT ARAYÜZ
# ----------------------
st.title("💬 Akıllı Kampanya Asistanı")
st.caption(f"✅ Son {MAX_HISTORY} mesaj saklanır | 🚫 Sorumlu sorguları kaydedilmez")

# Kullanıcı girdisi
user_input = st.chat_input("Sorunuzu buraya yazın...")
if user_input:
    process_user_input(user_input)

# Konuşma geçmişi gösterimi
if st.session_state.history:
    st.subheader("📜 Son Konuşmalar")
    for msg in st.session_state.history:
        st.markdown(f"**👤 Kullanıcı:** {msg['user']}")
        st.markdown(f"**🤖 Asistan:** {msg['bot']}")
        st.divider()






#######################################################################################

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################









import json
import streamlit as st
from collections import deque
from openai import AzureOpenAI
from elastic_search_retriever_embedding import ElasticTextSearch

# ----------------------
# 1. SABİT TANIMLAMALAR
# ----------------------
MAX_HISTORY = 3  # Son 3 mesajı sakla
PROMPT_1 = """**Role:** Kampanya analisti... [PROMPT_1 içeriği]"""
FOLLOW_UP_PROMPT = """**Role:** Akıllı asistan... [FOLLOW_UP_PROMPT içeriği]"""

# ----------------------
# 2. OPENAI BAĞLANTISI
# ----------------------
def initialize_openai_client():
    """Azure OpenAI istemcisini başlatır ve session state'e kaydeder"""
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = AzureOpenAI(
            api_key=st.secrets["AZURE_API_KEY"],
            api_version=st.secrets["AZURE_API_VERSION"],
            azure_endpoint=st.secrets["AZURE_ENDPOINT"]
        )
    return st.session_state.openai_client

# ----------------------
# 3. DİYALOG YÖNETİCİSİ
# ----------------------
class DialogManager:
    """Konuşma geçmişini ve bağlamı yöneten sınıf"""
    
    def __init__(self):
        # Session state başlatma
        if "history" not in st.session_state:
            st.session_state.history = deque(maxlen=MAX_HISTORY)  # Son 3 mesaj
            st.session_state.active_context = None  # GENEL/SPESİFİK
            st.session_state.active_campaign = None  # Aktif kampanya detayları
        
    def update_history(self, user_input, response, allow_history=True):
        """Geçmişi koşullu olarak günceller"""
        if allow_history:
            st.session_state.history.append({
                "user": user_input,
                "bot": response,
                "timestamp": datetime.now().isoformat()
            })
    
    def handle_campaign_context(self, processed_data):
        """Aktif kampanya context'ini günceller"""
        if processed_data.get("campaign_code"):
            self.active_campaign = {
                "type": "CODE",
                "value": processed_data["campaign_code"],
                "data": None
            }
        elif processed_data.get("spesific_campaign_header"):
            self.active_campaign = {
                "type": "HEADER",
                "value": processed_data["spesific_campaign_header"],
                "data": None
            }
        else:
            self.active_context = "GENEL"

# ----------------------
# 4. VERİ İŞLEME FONKSİYONLARI
# ----------------------
class DataProcessor:
    """Veri işleme operasyonlarını yönetir"""
    
    @staticmethod
    def process_campaign_response(json_str):
        """PROMPT_1 çıktısını işler"""
        try:
            data = json.loads(json_str)
            return {
                "status": "OK" if "ANSWER" not in data else data["ANSWER"],
                "data": {k:v for k,v in data.items() if k != "ANSWER"}
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    @staticmethod
    def generate_response(client, user_input, context):
        """GPT ile bağlamsal yanıt oluşturur"""
        messages = [
            {"role": "system", "content": f"Context: {json.dumps(context)}"},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model=st.secrets["DEPLOYMENT_NAME"],
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content

# ----------------------
# 5. ANA İŞLEM AKIŞI
# ----------------------
def process_user_input(user_input):
    """Kullanıcı girdisini işleyen ana fonksiyon"""
    
    # 5.1 Gerekli bileşenleri başlat
    dialog = DialogManager()
    client = initialize_openai_client()
    es = ElasticTextSearch()
    processor = DataProcessor()
    
    # 5.2 Temel sorgu analizi
    raw_response = analyze_query(client, PROMPT_1, user_input)
    processed_data = processor.process_campaign_response(raw_response)
    
    # 5.3 Kampanya sorumlusu kontrolü
    if processed_data["data"].get("campaign_responsible") == "YES":
        # Dummy veri ile sorumlu bilgisi göster
        responsible_info = {
            "name": "Ahmet Yılmaz",
            "email": "ahmet.yilmaz@sirket.com",
            "phone": "+90 555 123 45 67"
        }
        response = f"""
        🕴️ **Kampanya Sorumlusu Bilgileri:**
        - İsim: {responsible_info['name']}
        - E-posta: {responsible_info['email']}
        - Telefon: {responsible_info['phone']}
        """
        st.markdown(response)
        # Geçmişe EKLEME ve context'i değiştirme
        dialog.update_history(user_input, response, allow_history=False)
        return
    
    # 5.4 Context güncelleme
    dialog.handle_campaign_context(processed_data["data"])
    
    # 5.5 Veri çekme operasyonları
    try:
        if dialog.active_campaign["type"] == "CODE":
            campaign_data = es.get_by_code(dialog.active_campaign["value"])
        elif dialog.active_campaign["type"] == "HEADER":
            campaign_data = es.get_by_header(dialog.active_campaign["value"])
        else:
            campaign_data = es.get_general_campaigns()
    except Exception as e:
        st.error(f"🔍 Veri çekme hatası: {str(e)}")
        return
    
    # 5.6 GPT ile yanıt oluşturma
    bot_response = processor.generate_response(client, user_input, campaign_data)
    
    # 5.7 Çıktıları işleme
    st.subheader("🤖 Asistan Yanıtı")
    st.markdown(bot_response)
    
    # 5.8 Geçmişi güncelleme
    dialog.update_history(user_input, bot_response)
    
    # 5.9 Debug paneli
    with st.expander("⚙️ Sistem Detayları"):
        st.json({
            "user_input": user_input,
            "processed_data": processed_data,
            "campaign_data": campaign_data,
            "active_context": dialog.active_context
        })

# ----------------------
# 6. STREAMLIT ARAYÜZ
# ----------------------
st.title("💬 Akıllı Kampanya Asistanı")
st.caption(f"✅ Son {MAX_HISTORY} mesaj saklanır | 🚫 Hassas sorgular kaydedilmez")

# Kullanıcı girdi alanı
user_input = st.chat_input("Kampanya ile ilgili sorunuzu yazın...")
if user_input:
    process_user_input(user_input)

# Konuşma geçmişi gösterimi
if st.session_state.history:
    st.subheader("📜 Konuşma Geçmişi")
    for msg in st.session_state.history:
        st.markdown(f"**👤:** {msg['user']}")
        st.markdown(f"**🤖:** {msg['bot']}")
        st.divider()

# Manuel sıfırlama butonu
if st.button("🔄 Konuşmayı Yeniden Başlat"):
    DialogManager().reset_conversation()








#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################



