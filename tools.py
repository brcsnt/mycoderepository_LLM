import streamlit as st
import os
import json
from collections import deque
from langchain.tools import Tool
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, PromptTemplate
from elastic_search_retriever_embedding import ElasticTextSearch

# OpenAI API Ayarları
api_key = "your_openai_api_key"
azure_api_key = "your_azure_api_key"
azure_api_version = "your_azure_api_version"
azure_endpoint = "your_azure_endpoint"

# Elasticsearch Bağlantısı
es = ElasticTextSearch()

# Proxy Ayarları
http_proxy = "your_http_proxy"
https_proxy = "your_https_proxy"
os.environ["HTTP_PROXY"] = http_proxy
os.environ["HTTPS_PROXY"] = https_proxy

# Kullanıcı Geçmişini Session State ile Yönetme (Son 3 Mesaj)
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = deque(maxlen=3)

# Kampanya Kodu Çıkarma Promptu
extract_campaign_code_prompt = PromptTemplate(
    template="""
    Kullanıcının metninde bir kampanya kodu (4 veya 5 haneli) var mı?
    Eğer varsa, sadece kampanya kodunu döndür. Eğer yoksa, 'None' döndür.
    
    Kullanıcı Sorgusu: {user_input}
    """,
    input_variables=["user_input"]
)

# Kampanya Yanıt Üretme Promptu
campaign_response_prompt = PromptTemplate(
    template="""
    Sen bir kampanya asistanısın. Kullanıcının sorularını kampanya açıklamalarına göre cevaplamalısın.
    
    Kullanıcı sorusu: {user_input}
    
    Kampanya Açıklaması:
    {campaign_description}
    
    Kampanya detaylarını göz önünde bulundurarak, en iyi cevabı ver.
    Cevabın net, anlaşılır ve detaylı olmalı.
    """,
    input_variables=["user_input", "campaign_description"]
)

# Genel Kampanya Bilgisi Tool'u
general_campaign_info_tool = Tool(
    name="General Campaign Info",
    func=lambda user_input: "Black Friday kampanyası için indirim oranı %30 olup, 15 Kasım - 30 Kasım tarihleri arasında geçerlidir. Daha fazla bilgi almak ister misiniz?",
    description="Genel kampanya bilgilerini sağlar."
)

# Kampanya Ürün İçeriği Tool'u
campaign_product_info_tool = Tool(
    name="Campaign Product Info",
    func=lambda user_input: "Bu kampanya elektronik ve giyim kategorilerindeki seçili ürünleri kapsıyor.",
    description="Kampanya dahilindeki ürünleri listeler."
)

# Popüler Kampanyalar Tool'u
popular_campaigns_tool = Tool(
    name="Popular Campaigns",
    func=lambda user_input: "Elbette! İşte size en popüler 3 kampanya:\n\n[1] Yeni Yıl İndirimi\n[2] Yaz Fırsatları\n[3] Öğrenci Kampanyası\nHangisi hakkında bilgi almak istersiniz?",
    description="En popüler kampanyaları listeler."
)

# Kampanya Başlıkları Arama Tool'u
search_campaign_code_tool = Tool(
    name="Search Campaign by Code",
    func=search_campaign_by_code,
    description="Elasticsearch'te campaign_no alanına göre bir kampanya arar.",
    prompt_template=extract_campaign_code_prompt
)

generate_campaign_response_tool = Tool(
    name="Generate Campaign Response",
    func=generate_campaign_response,
    description="Kampanya detaylarına dayanarak kullanıcının sorduğu soruya yanıt üretir.",
    prompt_template=campaign_response_prompt
)

# Kullanıcı Girişi İşleme Fonksiyonu
def process_user_input(user_input):
    with st.spinner("🔍 Kampanya aranıyor..."):
        os.environ["HTTP_PROXY"] = http_proxy
        os.environ["HTTPS_PROXY"] = https_proxy

        campaign_code = extract_campaign_code(user_input)
        
        if campaign_code:
            search_result = search_campaign_by_code(user_input)
            campaign_description = search_result["data"]["campaign_description"]
            response = generate_campaign_response(user_input, campaign_description)
            save_to_history(user_input, response)
            st.subheader("🔹 Yanıt")
            st.write(response)
        elif "diğer kampanyaları" in user_input.lower():
            response = popular_campaigns_tool.run(user_input)
            save_to_history(user_input, response)
            st.subheader("🔹 Yanıt")
            st.write(response)
        elif "black friday" in user_input.lower():
            response = general_campaign_info_tool.run(user_input)
            save_to_history(user_input, response)
            st.subheader("🔹 Yanıt")
            st.write(response)
        elif "hangi ürünleri kapsıyor" in user_input.lower():
            response = campaign_product_info_tool.run(user_input)
            save_to_history(user_input, response)
            st.subheader("🔹 Yanıt")
            st.write(response)
        else:
            search_result = es.search_campaign_by_header(user_input)
            formatted_result = search_result
            save_to_history(user_input, formatted_result)
            st.subheader("🔹 Yanıt")
            st.write(formatted_result)

# Geçmiş Mesajları Saklama ve Gösterme
def save_to_history(user_input, response):
    st.session_state["chat_history"].append({"input": user_input, "response": response})

def display_chat_history():
    st.subheader("📜 Sohbet Geçmişi (Son 3 Mesaj)")
    for chat in st.session_state["chat_history"]:
        st.write(f"**Soru:** {chat['input']}")
        st.write(f"**Yanıt:** {chat['response']}")

# Uygulama Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")
    if st.button("Soruyu İşle"):
        process_user_input(user_input)
    display_chat_history()
