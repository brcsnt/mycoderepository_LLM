import streamlit as st
from langchain.memory import ConversationSummaryMemory
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import re
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Elasticsearch bağlantısı
es = Elasticsearch("http://localhost:9200")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# LLaMA 3.1 8B modelini GPU'ya yükle
model_id = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

def llama_generate(prompt, max_length=256):
    """LLaMA 3.1 modelini kullanarak metin üretir."""
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
    output = model.generate(input_ids, max_length=max_length)
    return tokenizer.decode(output[0], skip_special_tokens=True)

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

def generate_campaign_response(campaign):
    """Kampanya bilgilerini kullanarak LLM tabanlı yanıt oluşturur."""
    prompt = f"Kullanıcı şu kampanya hakkında bilgi istiyor: {campaign['campaign_header']}. Açıklama: {campaign['campaign_description']}. Cevap oluştur."
    return llama_generate(prompt)
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
                generate_campaign_response_tool
            ],
            llm=None,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
            verbose=True
        )
        
        response = agent.run(user_input)
        
        if "Aşağıdaki kampanyaları buldum" in response:
            st.session_state.top_n_results = search_campaign_by_header(user_input, top_n=3)
        
        for idx, res in enumerate(st.session_state.top_n_results):
            if res['campaign_header'].lower() in user_input.lower() or str(idx + 1) in user_input:
                response = generate_campaign_response(res)
                break
        
        st.subheader("💬 Yanıt")
        st.write(response)
        memory.save_context({"input": user_input}, {"output": response})
