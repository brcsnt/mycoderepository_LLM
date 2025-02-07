import streamlit as st
from langchain.memory import ConversationSummaryMemory
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import re
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import openai
import os

# Elasticsearch bağlantısı
es = Elasticsearch("http://localhost:9200")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# OpenAI API Anahtarı
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_generate(prompt, system_prompt=None, max_tokens=256):
    """OpenAI API kullanarak metin üretir."""
    if system_prompt:
        prompt = f"{system_prompt}\n\n{prompt}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response["choices"][0]["message"]["content"].strip()

def get_embedding(text):
    """Verilen metni vektör haline getirir."""
    return embedding_model.encode(text).tolist()

def extract_campaign_code(query):
    """Metin içindeki kampanya kodunu çıkarır."""
    match = re.search(r'\bKAMP\d{3}\b', query, re.IGNORECASE)
    return match.group() if match else None
extract_campaign_code_tool = Tool(
    name="Extract Campaign Code",
    func=extract_campaign_code,
    description="Extracts a campaign code from the user query if available."
)

def search_campaign_by_code(campaign_no):
    """Kampanya kodu ile Elasticsearch'te arama yapar."""
    response = es.search(index="campaigns", body={"query": {"match": {"campaign_no": campaign_no}}})
    results = response.get("hits", {}).get("hits", [])
    return results[0]["_source"] if results else None
search_campaign_code_tool = Tool(
    name="Search Campaign by Code",
    func=search_campaign_by_code,
    description="Searches a campaign by its campaign_no field in Elasticsearch."
)

def search_campaign_hybrid(query, top_n=3):
    """Hibrit arama: Metin eşleşmesi ve embedding skorlarıyla arama yapar."""
    query_vector = get_embedding(query)
    hybrid_query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["campaign_header", "campaign_description"],
                            "boost": 1.0
                        }
                    },
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": """
                                    double header_score = cosineSimilarity(params.query_vector, 'campaign_header_embedding');
                                    double description_score = cosineSimilarity(params.query_vector, 'campaign_description_embedding');
                                    return header_score * 0.6 + description_score * 0.4;
                                """,
                                "params": {"query_vector": query_vector}
                            },
                            "boost": 2.0
                        }
                    }
                ]
            }
        },
        "size": top_n
    }
    response = es.search(index="campaigns", body=hybrid_query)
    results = response.get("hits", {}).get("hits", [])
    return [{"campaign_no": res["_source"]["campaign_no"], "campaign_header": res["_source"]["campaign_header"], "campaign_description": res["_source"].get("campaign_description", "")} for res in results] if results else []
search_campaign_hybrid_tool = Tool(
    name="Search Campaign Hybrid",
    func=search_campaign_hybrid,
    description="Performs a hybrid search using both text match and embedding similarity."
)

def generate_campaign_response(user_input, campaign, chat_history, system_prompt="Asistan olarak doğru ve açıklayıcı cevaplar ver."):
    """Kampanya bilgilerini kullanarak OpenAI GPT modelini kullanarak yanıt oluşturur."""
    recent_history = "\n".join(chat_history[-3:])  # Son 3 konuşma geçmişini al
    prompt = f"Önceki konuşmalar: {recent_history}\nKullanıcı şu kampanya hakkında sordu: '{user_input}'.\nKampanya Bilgileri: {campaign['campaign_header']}. Açıklama: {campaign['campaign_description']}. Cevap oluştur."
    return openai_generate(prompt, system_prompt)
generate_campaign_response_tool = Tool(
    name="Generate Campaign Response",
    func=lambda user_input, campaign, chat_history: generate_campaign_response(user_input, campaign, chat_history),
    description="Generates an AI-powered response based on campaign details, user input, and last 3 messages from chat history."
)

def get_memory(n=3):
    return ConversationSummaryMemory(memory_key="chat_history", max_token_limit=n)

memory = get_memory(n=3)

st.title("📢 Kampanya Chatbot")
user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

chat_history = memory.load_memory_variables({}).get('chat_history', [])
st.subheader("📜 Sohbet Geçmişi")
for msg in chat_history[-3:]:
    st.write(msg)

if "top_n_results" not in st.session_state:
    st.session_state.top_n_results = []
if "last_campaign" not in st.session_state:
    st.session_state.last_campaign = None
if "previous_campaign" not in st.session_state:
    st.session_state.previous_campaign = None
if "previous_chat_history" not in st.session_state:
    st.session_state.previous_chat_history = []
if "last_query" not in st.session_state:
    st.session_state.last_query = None

if user_input:
    with st.spinner("Yanıt oluşturuluyor..."):
        campaign_no = extract_campaign_code(user_input)
        if campaign_no:
            campaign = search_campaign_by_code(campaign_no)
        else:
            campaigns = search_campaign_hybrid(user_input, top_n=3)
            if campaigns:
                campaign = campaigns[0]
                st.session_state.top_n_results = campaigns
            else:
                campaign = None
        
        if campaign:
            if st.session_state.last_campaign and st.session_state.last_campaign != campaign:
                st.session_state.previous_campaign = st.session_state.last_campaign
                st.session_state.previous_chat_history = chat_history[-3:]
            
            st.session_state.last_campaign = campaign
            st.session_state.last_query = user_input
            relevant_history = "\n".join(st.session_state.previous_chat_history[-3:])
            response = generate_campaign_response(user_input, campaign, relevant_history)
        else:
            response = "İlgili bir kampanya bulunamadı."
        
        st.subheader("💬 Yanıt")
        st.write(response)
        memory.save_context({"input": user_input}, {"output": response})
