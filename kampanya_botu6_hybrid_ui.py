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

def search_campaign_by_header(query, top_n=3):
    """Campaign_header alanında embedding vektör ile arama yapar."""
    query_vector = get_embedding(query)
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
    response = es.search(index="campaigns", body={"query": script_query, "size": top_n})
    results = response.get("hits", {}).get("hits", [])
    return [{"campaign_no": res["_source"]["campaign_no"], "campaign_header": res["_source"]["campaign_header"]} for res in results] if results else []
search_campaign_header_tool = Tool(
    name="Search Campaign by Header",
    func=search_campaign_by_header,
    description="Finds top N relevant campaigns using embedding search in the campaign_header field."
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

def generate_campaign_response(campaign, system_prompt="Asistan olarak doğru ve açıklayıcı cevaplar ver."):
    """Kampanya bilgilerini kullanarak OpenAI GPT modelini kullanarak yanıt oluşturur."""
    prompt = f"Kullanıcı şu kampanya hakkında bilgi istiyor: {campaign['campaign_header']}. Açıklama: {campaign['campaign_description']}. Cevap oluştur."
    return openai_generate(prompt, system_prompt)
generate_campaign_response_tool = Tool(
    name="Generate Campaign Response",
    func=generate_campaign_response,
    description="Generates an AI-powered response based on campaign details."
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

if user_input:
    with st.spinner("Yanıt oluşturuluyor..."):
        agent = initialize_agent(
            tools=[
                extract_campaign_code_tool,
                search_campaign_code_tool,
                search_campaign_header_tool,
                search_campaign_hybrid_tool,
                generate_campaign_response_tool
            ],
            llm=None,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
            verbose=True
        )
        response = agent.run(user_input)
        st.subheader("💬 Yanıt")
        st.write(response)
        memory.save_context({"input": user_input}, {"output": response})
