import streamlit as st
from transformers import AutoTokenizer, pipeline
import torch

# Model ve tokenizer yüklemek için fonksiyon
@st.cache(allow_output_mutation=True)
def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model_pipeline = pipeline(
        "text-generation",
        model=model_name,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    return tokenizer, model_pipeline

# Kullanıcı girdisine göre metin üretmek için fonksiyon
def generate_text(model_pipeline, tokenizer, user_prompt, top_k, max_length):
    sequences = model_pipeline(
        f'<s>[INST] {user_prompt} [/INST]',
        do_sample=True,
        top_k=top_k,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=max_length,
    )
    return sequences[0]['generated_text']

# Streamlit arayüzü
st.title('Hugging Face LLM Chat App')

# Model seçimi
model_name = st.sidebar.selectbox("Model seçin", ["gpt2", "distilgpt2", "bert-base-uncased"])  # Gerektiği gibi model isimlerini değiştirin veya ekleyin

# Kullanıcıdan parametreleri alma
user_input = st.text_input("Mesajınızı girin:")
top_k = st.sidebar.number_input("Top K değeri", min_value=1, value=10)  # Varsayılan olarak 10
max_length = st.sidebar.number_input("Maksimum uzunluk", min_value=1, max_value=300, value=50)  # Varsayılan olarak 50

# Yanıtı gösterme
if user_input:
    tokenizer, model_pipeline = load_model(model_name)
    response = generate_text(model_pipeline, tokenizer, user_input, top_k, max_length)
    st.text_area("Yanıt", value=response, height=300)
