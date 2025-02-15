import streamlit as st
import os
import json
from collections import deque
from langchain.tools import Tool
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import initialize_agent, AgentExecutor, AgentType

# ----------------------------------------------------------------
# Dummy ElasticTextSearch Implementasyonu
# Gerçek uygulamada, bu sınıf Elasticsearch ile iletişimi yönetecek şekilde implemente edilmelidir.
# ----------------------------------------------------------------
class ElasticTextSearch:
    def __init__(self):
        pass

    def search_campaign_by_header(self, user_input):
        # Dummy implementasyon: Kullanıcının girdiği kampanya kodu veya başlığına göre kampanya detaylarını döndürür.
        return f"Elasticsearch'den alınan kampanya detayları: '{user_input}' ile eşleşen kampanya bilgileri."

    def get_top_campaigns(self):
        # Dummy implementasyon: En iyi 3 kampanyayı döndürür.
        return "Elasticsearch: En iyi 3 kampanya bilgisi."

# ElasticTextSearch örneğini oluşturuyoruz.
es = ElasticTextSearch()

# ----------------------------------------------------------------
# initialize_openai_client Fonksiyonu
# Bu fonksiyon, OpenAI/Azure OpenAI istemcisini başlatır.
# Gerçek API anahtarlarınızı, endpoint bilgilerinizi ve proxy ayarlarınızı kullanmalısınız.
# ----------------------------------------------------------------
def initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy):
    import openai
    openai.api_key = api_key                        # API anahtarınızı ayarlayın.
    openai.api_base = azure_endpoint                # Azure endpoint bilgisi.
    openai.api_version = azure_api_version
    os.environ["HTTP_PROXY"] = http_proxy           # Proxy ayarlarını yapın.
    os.environ["HTTPS_PROXY"] = https_proxy
    return openai

# ----------------------------------------------------------------
# API, Proxy ve Bağlantı Ayarları
# Gerçek değerlerinizi buraya girin.
# ----------------------------------------------------------------
azure_api_key = "your_azure_api_key"
azure_api_version = "your_azure_api_version"
azure_endpoint = "https://your-azure-endpoint.openai.azure.com/"
api_key = "your_openai_api_key"
http_proxy = "your_http_proxy"
https_proxy = "your_https_proxy"

# ----------------------------------------------------------------
# Azure OpenAI Modeli Başlatma (LangChain üzerinden)
# ----------------------------------------------------------------
llm = AzureChatOpenAI(
    openai_api_key=azure_api_key,
    openai_api_version=azure_api_version,
    azure_endpoint=azure_endpoint,
    deployment_name="gpt-4",   # Azure'daki dağıtım adınız; doğru olduğundan emin olun.
    temperature=0.7
)

# ----------------------------------------------------------------
# Sohbet Geçmişi Yönetimi (Sadece session_state kullanılıyor)
# ----------------------------------------------------------------
# st.session_state içinde "chat_memory" adında bir deque oluşturuyoruz; sadece son 3 mesajı saklar.
if "chat_memory" not in st.session_state:
    st.session_state["chat_memory"] = deque(maxlen=3)
# Kampanya açıklamasını dinamik olarak saklamak için bir alan.
if "campaign_description" not in st.session_state:
    st.session_state["campaign_description"] = None

# Fonksiyon: get_formatted_history
# Sohbet geçmişindeki mesajları biçimlendirip tek bir string olarak döndürür.
def get_formatted_history():
    return "\n".join(
        [f"Soru: {chat['input']}\nYanıt: {chat['response']}" for chat in st.session_state["chat_memory"]]
    )

# ----------------------------------------------------------------
# Tool Fonksiyonları
# ----------------------------------------------------------------

# 1. extract_campaign_code
# Kullanıcının metninde kampanya kodu varsa, bunu JSON formatında çıkartır.
def extract_campaign_code(user_input):
    prompt = f"""
    Kullanıcının metni: {user_input}
    Eğer metinde kampanya kodu varsa, sadece kampanya kodunu JSON formatında döndür:
    Örnek çıktı: {{"campaign_code": "<kod>"}}
    Eğer yoksa: {{"campaign_code": null}} şeklinde döndür.
    """
    result = llm([HumanMessage(content=prompt)])
    try:
        return json.loads(result.content)
    except Exception:
        return {"campaign_code": None}

# 2. detect_query_type
# Kullanıcının sorgusunun genel arama mı yoksa belirli bir kampanyaya yönelik mi olduğunu belirler.
def detect_query_type(user_input):
    system_prompt = (
        "Lütfen aşağıdaki kurallara kesinlikle uy:\n"
        "- Eğer kullanıcının metninde belirli bir kampanyaya dair doğrudan soru varsa, "
        "yanıt olarak 'kampanya başlık: <kampanya_adı>' formatında ilgili kampanya adını belirt.\n"
        "- Aksi halde, 'GENEL ARAMA' ifadesini döndür.\n"
        "Önceki mesajlar ve mevcut kullanıcı sorgusunu dikkate alarak en doğru yanıtı üret."
    )
    user_prompt = f"[Önceki Mesajlar]: {get_formatted_history()} \n[Kullanıcı Sorusu]: {user_input}"
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, http_proxy, https_proxy)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    deployment_name = "gpt-4"
    max_tokens = 250
    response = client.chat.completions.create(model=deployment_name, messages=messages, max_tokens=max_tokens)
    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()

# 3. check_follow_up_relevance
# Kullanıcının yeni sorusunun, önceki mesajdaki kampanyayla ilişkisini kontrol eder.
# Bu fonksiyon, iki parametre alır: kullanıcı girdisi ve önceki mesajın yanıtı.
def check_follow_up_relevance(user_input, last_message):
    system_prompt = (
        "Aşağıdaki kurallara kesinlikle uy:\n"
        "- Eğer önceki mesajda belirtilen kampanyaya yönelik devam eden bir soru varsa, "
        "lütfen 'kampanya başlık: <kampanya_baslik>' formatında ilgili kampanya adını belirt.\n"
        "- Eğer yeni soru, önceki mesajdaki kampanyadan bağımsız veya yeni bir kampanyaya yönelikse, "
        "sadece 'GENEL ARAMA' ifadesini döndür.\n"
        "Kullanıcının yeni sorusunu ve önceki mesajı dikkate alarak en doğru yanıtı üret."
    )
    #last_message = st.session_state["chat_memory"][0]["response"]
    user_prompt = f"[Önceki Mesaj]: {last_message} \n[Yeni Kullanıcı Sorusu]: {user_input}"
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, http_proxy, https_proxy)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    deployment_name = "gpt-4"
    max_tokens = 300
    response = client.chat.completions.create(model=deployment_name, messages=messages, max_tokens=max_tokens)
    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()

# 4. search_campaign_by_header
# Elasticsearch üzerinden kampanya başlığına göre arama yapar.
def search_campaign_by_header(user_input):
    return es.search_campaign_by_header(user_input)

# 5. search_campaign_by_header_one_result
# Elasticsearch üzerinden kampanya kodu veya başlığına göre tek bir kampanya sonucunu döndürür.
def search_campaign_by_header_one_result(query_type):
    return es.search_campaign_by_header(query_type)

# 6. generate_campaign_response
# Kullanıcının sorusunda geçen kampanya kodu veya kampanya başlığı varsa,
# ElasticSearch'ten kampanya detaylarını alır ve bu detayları kullanarak cevap üretir.
def generate_campaign_response(user_prompt, deployment_name="gpt-4", max_tokens=300):
    # Önce kampanya kodu var mı kontrol edelim.
    campaign_info = extract_campaign_code(user_prompt)
    if campaign_info and campaign_info.get("campaign_code"):
        # Eğer kampanya kodu tespit edildiyse, Elasticsearch'ten kampanya detaylarını al.
        campaign_description = es.search_campaign_by_header(user_prompt)
    else:
        # Eğer kampanya kodu bulunamazsa, detect_query_type ile kampanya başlığına dair sorgu yapalım.
        query_type = detect_query_type(user_prompt)
        if "kampanya başlık" in query_type.lower():
            campaign_description = es.search_campaign_by_header(user_prompt)
        else:
            campaign_description = "Kampanya açıklaması mevcut değil."
    # Varsayılan sistem promptu belirlenir.
    system_prompt = "Kampanya ile ilgili ana katman"
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy)
    rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metni içeriği: " + campaign_description
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": rag_prompt}
    ]
    response = client.chat.completions.create(model=deployment_name, messages=messages, temperature=0, max_tokens=max_tokens)
    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()

# 7. generate_campaign_response_v2
# Alternatif sistem prompt kullanarak benzer şekilde kampanya detaylarını alır ve cevap üretir.
def generate_campaign_response_v2(user_prompt, deployment_name="gpt-4", max_tokens=300):
    campaign_info = extract_campaign_code(user_prompt)
    if campaign_info and campaign_info.get("campaign_code"):
        campaign_description = es.search_campaign_by_header(user_prompt)
    else:
        query_type = detect_query_type(user_prompt)
        if "kampanya başlık" in query_type.lower():
            campaign_description = es.search_campaign_by_header(user_prompt)
        else:
            campaign_description = "Kampanya açıklaması mevcut değil."
    system_prompt = "Kampanya ile ilgili sorulara cevap ver"
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy)
    rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metni içeriği: " + campaign_description
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": rag_prompt}
    ]
    response = client.chat.completions.create(model=deployment_name, messages=messages, temperature=0, max_tokens=max_tokens)
    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()

# ----------------------------------------------------------------
# Tool Tanımlamaları (LangChain Tool yapısı)
# Her tool, fonksiyon adını, kullanılacak fonksiyonu ve açıklamasını içerir.
# ----------------------------------------------------------------
extract_campaign_code_tool = Tool(
    name="Extract Campaign Code Tool",
    func=extract_campaign_code,
    description="Kullanıcının sorgusunda kampanya kodu olup olmadığını kontrol eder. JSON formatında sonuç döndürür."
)

detect_query_type_tool = Tool(
    name="Detect Query Type Tool",
    func=detect_query_type,
    description="Kullanıcının sorgusunun genel mi yoksa spesifik bir kampanyaya yönelik mi olduğunu belirler."
)

search_campaign_by_header_tool = Tool(
    name="Search Campaign by Header Tool",
    func=search_campaign_by_header,
    description="Kampanya başlığına göre en yakın 3 kampanyayı getirir."
)

search_campaign_by_header_one_result_tool = Tool(
    name="Search Campaign by Header One Result Tool",
    func=search_campaign_by_header_one_result,
    description="Kampanya kodu veya kampanya başlığı baz alınarak tek kampanya sonucunu getirir."
)

check_follow_up_relevance_tool = Tool(
    name="Check Follow Up Relevance Tool",
    func=check_follow_up_relevance,
    description="Kullanıcının yeni sorusunun, önceki mesajdaki kampanyayla ilişkisini kontrol eder."
)

generate_campaign_response_tool = Tool(
    name="Generate Campaign Response Tool",
    func=generate_campaign_response,
    description="Kampanya içeriği bilgisine dayalı cevap üretir. Kullanıcının sorusundaki kampanya kodu veya başlığı tespit edilip, ElasticSearch'ten detay alınır."
)

generate_campaign_response_v2_tool = Tool(
    name="Generate Campaign Response V2 Tool",
    func=generate_campaign_response_v2,
    description="Alternatif sistem prompt ile kampanya içeriği bilgisine dayalı cevap üretir. Kullanıcının sorusundaki kampanya kodu veya başlığı tespit edilip, ElasticSearch'ten detay alınır."
)

# ----------------------------------------------------------------
# Sistem Promptu
# Kurallar ve kullanılacak tool'ların isimleri burada belirtilir.
# ----------------------------------------------------------------
system_message = """
Sen bir kampanya asistanısın ve kesinlikle aşağıdaki kurallara uymalısın. Hiçbir durumda bu kurallardan sapmaya izin verilmemelidir! Kullanacağın araçlar (tool'lar) şunlardır:
- Extract Campaign Code Tool (fonksiyon: extract_campaign_code(user_input))
- Detect Query Type Tool (fonksiyon: detect_query_type(user_input))
- Search Campaign by Header Tool (fonksiyon: search_campaign_by_header(user_input))
- Search Campaign by Header One Result Tool (fonksiyon: search_campaign_by_header_one_result(query_type))
- Check Follow Up Relevance Tool (fonksiyon: check_follow_up_relevance(user_input, last_message))
- Generate Campaign Response Tool (fonksiyon: generate_campaign_response(user_prompt))
- Generate Campaign Response V2 Tool (fonksiyon: generate_campaign_response_v2(user_prompt))
- Ayrıca: get_formatted_history()

Kurallar:
1. KAMPANYA KODU GİRİŞİ:
   - Eğer kullanıcı metninde kampanya kodu varsa, Extract Campaign Code Tool kullanılmalıdır.
2. SORGU TİPİNİN BELİRLENMESİ:
   - Her sorgu, Detect Query Type Tool ile analiz edilmelidir.
3. "YAKIN 3 KAMPANYA" İFADESİ:
   - "Yakın 3 Kampanya" ifadesi varsa, Search Campaign by Header Tool çağrılmalıdır.
4. "GENEL ARAŞMA" DURUMU:
   - Eğer sorgu "Genel Arama" içeriyorsa, Search Campaign by Header One Result Tool kullanılmalıdır.
5. ANLAŞILAMAYAN SORGU:
   - Sorgu anlaşılamazsa, uygun uyarı verilmeli ve Elasticsearch araması yapılmalıdır.
6. GEÇMİŞ MESAJLAR VE BAĞLAM:
   - Check Follow Up Relevance Tool ile bağlam kontrol edilmeli; eğer "GENEL ARAMA" dönerse, sohbet geçmişi temizlenmelidir.
7. KAMPANYA İÇERİKLİ CEVAP:
   - Kullanıcının sorusunda geçen kampanya kodu veya kampanya başlığı tespit edilip, ElasticSearch'ten kampanya detayları alınmalı ve Generate Campaign Response Tool veya V2 Tool kullanılarak cevap üretilmelidir.
ÖNEMLİ: Tüm kurallara uyulmalı ve araçlar doğru şekilde kullanılmalıdır!
"""

system_message_v2 = """
# 🚨 KESİNLİKLE UYULACAK KURALLAR 🚨

Sen bir kampanya asistanısın. Tüm cevaplarını **aşağıdaki adımları sırasıyla uygulayarak** ve **yalnızca belirtilen araçları (tools) kullanarak** oluşturmalısın. Hiçbir adımı atlama!

## 🔧 KULLANILACAK ARAÇLAR VE TETİKLEYİCİLER:
1. **Extract Campaign Code Tool** 
   - KULLANIM: Kullanıcı metninde "KMP-123", "kampanya 456" gibi kod varsa.
   - ÇIKTI: {"campaign_code": "KMP-123"} veya {"campaign_code": null}

2. **Detect Query Type Tool** 
   - KULLANIM: Her yeni kullanıcı sorusunda ZORUNLU olarak ilk çalıştırılacak.
   - ÇIKTI: "kampanya başlık: [TAM_KAMPANYA_ADI]" veya "GENEL ARAMA"

3. **Search Campaign by Header Tool** 
   - KULLANIM: Detect Query Type "GENEL ARAMA" döndürdüyse veya kullanıcı "yakın 3 kampanya" dediyse.
   - ÇIKTI: Elasticsearch'ten en fazla 3 sonuç.

4. **Search Campaign by Header One Result Tool** 
   - KULLANIM: Detect Query Type "kampanya başlık" döndürdüyse veya Extract Campaign Code Tool kod bulduysa.
   - ÇIKTI: Elasticsearch'ten 1 sonuç.

5. **Check Follow Up Relevance Tool** 
   - KULLANIM: Önceki mesajda kampanya varsa ve yeni soru geldiyse.
   - ÇIKTI: "kampanya başlık: [TAM_KAMPANYA_ADI]" veya "GENEL ARAMA"

6. **Generate Campaign Response Tool** 
   - KULLANIM: Kampanya detayları alındıktan sonra nihai cevabı oluşturmak için.
   - ÇIKTI: Kullanıcıya özelleştirilmiş cevap.

## 🛠 İŞ AKIŞI ADIMLARI:
1. **Adım - Sorgu Tipini Belirle:**
   - Her yeni mesajda İLK olarak `Detect Query Type Tool` kullan.
   - Örnek: "Bu kampanyanın şartları nedir?" → "kampanya başlık: Yaz Indirimi"

2. **Adım - Bağlam Kontrolü:**
   - Eğer önceki mesajda kampanya varsa `Check Follow Up Relevance Tool` kullan.
   - Örnek: Önceki cevap "Yaz Indirimi" ile ilgiliyse, yeni soru "Bu kampanyada indirim oranı?" → İlişkili

3. **Adım - Kampanya Kodu/Başlık Ara:**
   - Detect Query Type "kampanya başlık" döndürdüyse veya kampanya kodu varsa:
     - `Search Campaign by Header One Result Tool` ile detayları al.
   - "GENEL ARAMA" durumunda `Search Campaign by Header Tool` kullan.

4. **Adım - Cevap Oluştur:**
   - Elasticsearch'ten gelen verileri kullanarak `Generate Campaign Response Tool` veya V2 ile cevap üret.

## ❗ KRİTİK HATA DURUMLARINDA:
- Elasticsearch'ten veri gelmezse: "Üzgünüm, ilgili kampanya bulunamadı. Lütfen başka bir sorgu deneyin."
- Araçlar yanlış sırada kullanılırsa: "Sistem hatası oluştu. Lütfen tekrar deneyin."

## 📌 ÖNEMLİ UYARILAR:
- Hiçbir koşulda kendi fikrini belirtme! YALNIZCA araçlardan gelen verileri kullan.
- Araçları TAM İSİMLERİYLE çağır. (Örn: "Extract Campaign Code Tool" yerine "extract_tool" YOK)
- Adımları atlama! Sıra: Detect Query Type → Check Relevance → Search → Generate Response
"""

# ----------------------------------------------------------------
# Agent ve Agent Executor'un Başlatılması
# ----------------------------------------------------------------
agent = initialize_agent(
    tools=[
        extract_campaign_code_tool,
        detect_query_type_tool,
        search_campaign_by_header_tool,
        search_campaign_by_header_one_result_tool,
        check_follow_up_relevance_tool,
        generate_campaign_response_tool,
        generate_campaign_response_v2_tool
    ],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={
        "prefix": system_message,
        "suffix": "\nLütfen yukarıdaki kurallara uyarak cevabını oluştur.",
        "format_instructions": ""
    },
    verbose=True
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=[
        extract_campaign_code_tool,
        detect_query_type_tool,
        search_campaign_by_header_tool,
        search_campaign_by_header_one_result_tool,
        check_follow_up_relevance_tool,
        generate_campaign_response_tool,
        generate_campaign_response_v2_tool
    ],
    verbose=True
)

# ----------------------------------------------------------------
# Kullanıcı Girişi İşleme Fonksiyonu
# ----------------------------------------------------------------
def process_user_input(user_input):
    with st.spinner("🔍 İşleniyor..."):
        os.environ["HTTP_PROXY"] = http_proxy
        os.environ["HTTPS_PROXY"] = https_proxy

        # İlk olarak, kullanıcının sorgusunun türünü belirleyelim.
        query_type = detect_query_type(user_input)
        # Eğer sorgu "GENEL ARAMA" değilse, ElasticSearch'ten dinamik kampanya içeriği alınır.
        if query_type != "GENEL ARAMA":
            dynamic_description = search_campaign_by_header_one_result(query_type)
            st.session_state["campaign_description"] = dynamic_description
        else:
            st.session_state["campaign_description"] = None

        # Eğer geçmişteki mesajlar varsa, son mesajın yanıtı üzerinden bağlam kontrolü yapalım.
        if st.session_state["chat_memory"]:
            last_response = st.session_state["chat_memory"][0]["response"]
            relevance = check_follow_up_relevance(user_input, last_response)
            if relevance == "GENEL ARAMA":
                # Yeni bir kampanya başlatıldığını varsayarak geçmiş temizlenir.
                st.session_state["chat_memory"].clear()
                st.info("Yeni bir kampanya başlatıldı, önceki konuşmalar sıfırlandı.")

        # Agent, sistem promptundaki kurallara göre kullanıcının sorusunu işler.
        response = agent_executor.run(user_input)
        # İşlenen soru ve yanıt, sohbet geçmişine eklenir.
        st.session_state["chat_memory"].appendleft({"input": user_input, "response": response})
        
        st.subheader("🔹 Yanıt")
        st.write(response)

# ----------------------------------------------------------------
# Streamlit Arayüzü
# ----------------------------------------------------------------
st.title("📢 Kampanya Asistanı")
user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

if st.button("Soruyu İşle"):
    process_user_input(user_input)

st.subheader("📜 Sohbet Geçmişi")
for chat in st.session_state["chat_memory"]:
    st.write(f"**Soru:** {chat['input']}")
    st.write(f"**Yanıt:** {chat['response']}")






#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


import streamlit as st
import os
import json
from collections import deque
from langchain.tools import Tool
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import initialize_agent, AgentExecutor, AgentType

# ----------------------------------------------------------------
# Dummy ElasticTextSearch Implementation
# ----------------------------------------------------------------
class ElasticTextSearch:
    def __init__(self):
        self.dummy_data = {
            "KMP-2023": "Yaz İndirimi Kampanyası - Elektronik ürünlerde %30'a varan indirimler",
            "KMP-2024": "Kış Tatili Kampanyası - Tüm seyahat paketlerinde erken rezervasyon avantajı",
            "GENEL": ["Kampanya 1: Yeni müşteri %10 indirim", "Kampanya 2: Öğrencilere özel fırsat"]
        }

    def search_campaign_by_header(self, user_input):
        if "KMP-" in user_input:
            return self.dummy_data.get(user_input.split("KMP-")[1].strip(), "Kampanya bulunamadı")
        return "\n".join(self.dummy_data["GENEL"][:3])

    def get_top_campaigns(self):
        return "\n".join(self.dummy_data["GENEL"][:3])

es = ElasticTextSearch()

# ----------------------------------------------------------------
# OpenAI/Azure Client Initialization
# ----------------------------------------------------------------
def initialize_openai_client():
    from openai import AzureOpenAI
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2023-12-01-preview",
        azure_endpoint="https://your-endpoint.openai.azure.com/"
    )

# ----------------------------------------------------------------
# Session State Management
# ----------------------------------------------------------------
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = deque(maxlen=3)
if "current_campaign" not in st.session_state:
    st.session_state.current_campaign = None

# ----------------------------------------------------------------
# Core Functions
# ----------------------------------------------------------------
def get_formatted_history():
    return "\n".join(
        [f"Soru: {chat['input']}\nYanıt: {chat['response']}" 
         for chat in st.session_state.chat_memory]
    )

def extract_campaign_code(user_input: str) -> dict:
    prompt = f"""Kullanıcı metnindeki kampanya kodunu çıkar:
    Metin: {user_input}
    Çıktı formatı: {{"campaign_code": "KMP-123"}} veya {{"campaign_code": null}}"""
    result = llm([HumanMessage(content=prompt)])
    try:
        return json.loads(result.content)
    except:
        return {"campaign_code": None}

def detect_query_type(user_input: str) -> str:
    history = get_formatted_history()
    prompt = f"""Sorgu tipini belirle:
    Geçmiş Mesajlar: {history}
    Son Sorgu: {user_input}
    Çıktı: 'kampanya başlık: [TAM_AD]' veya 'GENEL ARAMA'"""
    result = llm([HumanMessage(content=prompt)])
    return result.content.strip()

def check_follow_up_relevance(user_input: str) -> str:
    if not st.session_state.chat_memory:
        return "GENEL ARAMA"
    
    last_response = st.session_state.chat_memory[0]["response"]
    prompt = f"""Yeni soru önceki kampanyayla ilişkili mi?
    Önceki Yanıt: {last_response}
    Yeni Soru: {user_input}
    Çıktı: 'kampanya başlık: [TAM_AD]' veya 'GENEL ARAMA'"""
    
    result = llm([HumanMessage(content=prompt)])
    return result.content.strip()

def generate_campaign_response(user_input: str) -> str:
    campaign_data = es.search_campaign_by_header(user_input)
    prompt = f"""Kullanıcı sorusunu kampanya verileriyle yanıtla:
    Soru: {user_input}
    Veriler: {campaign_data}
    Yanıt:"""
    result = llm([HumanMessage(content=prompt)])
    return result.content.strip()

# ----------------------------------------------------------------
# LangChain Tools
# ----------------------------------------------------------------
tools = [
    Tool(
        name="ExtractCampaignCode",
        func=extract_campaign_code,
        description="Kampanya kodunu çıkarmak için kullanılır"
    ),
    Tool(
        name="DetectQueryType",
        func=detect_query_type,
        description="Sorgu tipini belirler (GENEL ARAMA veya spesifik kampanya)"
    ),
    Tool(
        name="CheckFollowUpRelevance",
        func=check_follow_up_relevance,
        description="Yeni sorunun önceki bağlamla ilişkisini kontrol eder"
    ),
    Tool(
        name="GenerateCampaignResponse",
        func=generate_campaign_response,
        description="Kampanya verilerine dayalı yanıt oluşturur"
    )
]

# ----------------------------------------------------------------
# Agent Configuration
# ----------------------------------------------------------------
system_prompt = """
**KRİTİK KURALLAR:**
1. Her sorguda sırayla şu araçları kullan:
   a) DetectQueryType -> b) CheckFollowUpRelevance -> c) GenerateCampaignResponse
2. DetectQueryType çıktısı 'kampanya başlık' içeriyorsa otomatik olarak GenerateCampaignResponse kullan
3. 'GENEL ARAMA' durumunda en fazla 3 kampanya göster
4. Hiçbir durumda kendi bilgini kullanma, sadece araç çıktılarını kullan
"""

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    temperature=0.3
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=3,
    agent_kwargs={
        "prefix": system_prompt,
        "memory_prompts": [],
        "input_variables": ["input", "agent_scratchpad"]
    }
)

# ----------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------
st.title("🤖 Akıllı Kampanya Asistanı")

user_input = st.chat_input("Sorunuzu buraya yazın...")

if user_input:
    with st.spinner("Analiz ediliyor..."):
        try:
            response = agent.run(user_input)
            st.session_state.chat_memory.appendleft({
                "input": user_input,
                "response": response
            })
            
            st.subheader("Yanıt")
            st.write(response)
            
            st.subheader("Sohbet Geçmişi")
            for msg in st.session_state.chat_memory:
                st.markdown(f"**Soru:** {msg['input']}  \n**Yanıt:** {msg['response']}")
                
        except Exception as e:
            st.error(f"Sistem hatası: {str(e)}")
            st.info("Lütfen farklı bir şekilde tekrar deneyin")

