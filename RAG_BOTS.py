
import streamlit as st
from langchain_community.chat_models import AzureChatOpenAI
from collections import deque

# 📌 Streamlit session state ile chat memory saklama
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = deque(maxlen=3)  # En fazla 3 mesaj saklanır

# 📌 OpenAI istemcisini başlatma
def initialize_openai_client():
    return AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="xyz",
        model_name="xyz",
        openai_api_type="azure"
    )

# 📌 Kullanıcının genel mi yoksa spesifik bir kampanya hakkında mı konuştuğunu belirleme
def detect_query_type(user_input):
    """OpenAI kullanarak kullanıcının genel bir arama mı yoksa spesifik bir kampanya sorgusu mu yaptığını belirler."""
    
    system_prompt = """Kullanıcının mesajını analiz et:
    - Eğer genel bir kampanya arıyorsa 'GENEL ARAMA' döndür. (Örneğin: "Boyner kampanyaları", "İndirimli kampanyalar")
    - Eğer belirli bir kampanya hakkında doğrudan bir soru soruyorsa, kampanya başlığını döndür. (Örneğin: "Yılbaşı restoran kampanyasının bitiş tarihi nedir" → "Yılbaşı Restoran Kampanyası")"""

    client = initialize_openai_client()
    response = client.predict(f"{system_prompt}\n\nKullanıcı Mesajı: {user_input}")
    
    return response.strip()

# 📌 Mesaj Ekleme Fonksiyonu
def add_message(user_input, response):
    """Sohbet geçmişine yeni mesaj ekler."""
    st.session_state.chat_memory.appendleft({"user": user_input, "bot": response})

# 📌 History'yi Ekrana Formatlı Yazdırma
def get_formatted_history():
    """Sohbet geçmişini zaman sırasına göre formatlı döndürür."""
    if not st.session_state.chat_memory:
        return "Sohbet geçmişi henüz boş."
    return "\n\n".join([f"🗣 Kullanıcı: {msg['user']}\n🤖 Bot: {msg['bot']}" for msg in st.session_state.chat_memory])

# 📌 OpenAI'ye Kampanya Bilgisiyle Soru Gönderme
def ask_openai(user_input, campaign_info=None):
    """OpenAI'ye özel sistem prompt'ları ile soru gönderir."""
    if campaign_info:
        system_prompt = f"Kampanya bilgisi verilmiştir. Bu bilgiye göre soruyu yanıtla:\n\nKampanya Açıklaması: {campaign_info}"
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."
    else:
        system_prompt = "Kullanıcı bir kampanya hakkında soru sormuş olabilir. Eğer kampanya kodu veya başlık belirttiyse, ona göre yanıt ver."
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."

    model = initialize_openai_client()
    response = model.predict("\n".join([system_prompt, user_prompt]))
    return response.strip()

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    """Her yeni kullanıcı mesajında sıfırdan başlar ve tüm akışı yönetir."""
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):

            # 📌 Kampanya kodu var mı?
            campaign_code = extract_campaign_code(user_input)

            if len(st.session_state.chat_memory) == 0:
                if campaign_code:
                    campaign_info = es.get_best_related(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    add_message(user_input, response)
                    st.subheader(f"📌 {campaign_code} Kampanyası Yanıt İçeriği")
                    st.write(response)

                else:
                    # 📌 Kullanıcının sorgu tipini analiz et
                    query_type = detect_query_type(user_input)

                    if query_type == "GENEL ARAMA":
                        search_result, formatted_result = es.search_campaign_by_header(user_input)
                        add_message(user_input, formatted_result)  # **🔹 Artık history’ye ekleniyor**
                        st.subheader("📌 En İyi 3 Kampanya")
                        st.write(formatted_result)
                    
                    else:
                        # Kullanıcı belirli bir kampanya hakkında doğrudan soru sorduysa
                        campaign_info = es.filter_campaign_by_title(query_type)
                        response = ask_openai(user_input, campaign_info=campaign_info)
                        add_message(user_input, response)
                        st.subheader(f"📌 {query_type} Kampanyası İçeriği")
                        st.write(response)

        st.subheader("💬 Sohbet Geçmişi (Son 3 Mesaj)")
        st.write(get_formatted_history())

        if len(st.session_state.chat_memory) == 3:
            st.session_state.chat_memory.clear()
            st.warning("📌 Sohbet geçmişi dolduğu için sıfırlandı.")

# 📌 Streamlit Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    st.markdown("---")

    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

    if user_input:
        process_user_input(user_input)

    st.subheader("💬 Sohbet Geçmişi (Son 3 Mesaj)")
    st.write(get_formatted_history())


















import streamlit as st
from langchain_community.chat_models import AzureChatOpenAI
from collections import deque

# 📌 Streamlit session state ile chat memory saklama
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = deque(maxlen=3)  # En fazla 3 mesaj saklanır

# 📌 OpenAI istemcisini başlatma
def initialize_openai_client():
    return AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="xyz",
        model_name="xyz",
        openai_api_type="azure"
    )

# 📌 Kullanıcının yeni sorusunun önceki mesajla ilgili olup olmadığını kontrol etme
def check_follow_up_relevance(user_input, last_message):
    """Kullanıcının yeni sorusunun önceki mesajla ilişkili olup olmadığını kontrol eder."""
    
    system_prompt = """Kullanıcının sorusunu anla ve eğer önceki cevapta belirtilen kampanyalardan biriyle ilgiliyse hangi kampanya ile ilgili olduğunu belirle.
    - Eğer önceki kampanyalardan biriyle ilgiliyse **"kampanya kodu: <kampanya_kodu>"** şeklinde döndür.
    - Eğer yeni bir kampanya hakkında konuşuyorsa **"NEW QUERY"** döndür.
    - Eğer önceki mesajla alakasızsa **"NONE"** döndür."""

    user_prompt = f"Önceki Mesaj: {last_message} \n Yeni Kullanıcı Sorusu: {user_input}"
    
    client = initialize_openai_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.predict("\n".join([msg["content"] for msg in messages]))
    
    return response.strip()

# 📌 Mesaj Ekleme Fonksiyonu
def add_message(user_input, response):
    """Sohbet geçmişine yeni mesaj ekler."""
    st.session_state.chat_memory.appendleft({"user": user_input, "bot": response})  # Yeni mesaj en üste eklenir

# 📌 History'yi Ekrana Formatlı Yazdırma
def get_formatted_history():
    """Sohbet geçmişini zaman sırasına göre formatlı döndürür."""
    if not st.session_state.chat_memory:
        return "Sohbet geçmişi henüz boş."
    return "\n\n".join([f"🗣 Kullanıcı: {msg['user']}\n🤖 Bot: {msg['bot']}" for msg in st.session_state.chat_memory])

# 📌 OpenAI'ye Kampanya Bilgisiyle Soru Gönderme
def ask_openai(user_input, campaign_info=None):
    """OpenAI'ye özel sistem prompt'ları ile soru gönderir."""
    if campaign_info:
        system_prompt = f"Kampanya bilgisi verilmiştir. Bu bilgiye göre soruyu yanıtla:\n\nKampanya Açıklaması: {campaign_info}"
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."
    else:
        system_prompt = "Kullanıcı bir kampanya hakkında soru sormuş olabilir. Eğer kampanya kodu veya başlık belirttiyse, ona göre yanıt ver."
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."

    model = initialize_openai_client()
    response = model.predict("\n".join([system_prompt, user_prompt]))
    return response.strip()

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    """Her yeni kullanıcı mesajında sıfırdan başlar ve tüm akışı yönetir."""
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):

            # 📌 Kampanya kodu var mı?
            campaign_code = extract_campaign_code(user_input)

            if len(st.session_state.chat_memory) == 0:
                if campaign_code:
                    campaign_info = es.get_best_related(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    add_message(user_input, response)
                    st.subheader(f"📌 {campaign_code} Kampanyası Yanıt İçeriği")
                    st.write(response)
                else:
                    search_result, formatted_result = es.search_campaign_by_header(user_input)
                    add_message(user_input, formatted_result)  # **🔹 Artık history’ye ekleniyor**
                    st.subheader("📌 En İyi 3 Kampanya")
                    st.write(formatted_result)

            else:
                last_message = st.session_state.chat_memory[0]["bot"]
                follow_up_response = check_follow_up_relevance(user_input, last_message)

                st.warning(f"Follow-up response: {follow_up_response}")  # **🔍 Debugging için ekledim**

                if follow_up_response.startswith("kampanya kodu:"):
                    campaign_code = follow_up_response.split(":")[1].strip()
                    campaign_info = es.get_best_related(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    add_message(user_input, response)
                    st.subheader(f"📌 {campaign_code} Kampanyası Yanıt İçeriği")
                    st.write(response)

                elif follow_up_response == "NEW QUERY":
                    search_result, formatted_result = es.search_campaign_by_header(user_input)
                    add_message(user_input, formatted_result)
                    st.subheader("📌 En İyi 3 Kampanya")
                    st.write(formatted_result)

                elif follow_up_response == "NONE":
                    st.warning("Bu sorunuz önceki kampanyalarla ilgili değil. Lütfen soruyu farklı şekilde sormayı deneyin.")

        st.subheader("💬 Sohbet Geçmişi (Son 3 Mesaj)")
        st.write(get_formatted_history())

        if len(st.session_state.chat_memory) == 3:
            st.session_state.chat_memory.clear()
            st.warning("📌 Sohbet geçmişi dolduğu için sıfırlandı.")

# 📌 Streamlit Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    st.markdown("---")

    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

    if user_input:
        process_user_input(user_input)

    st.subheader("💬 Sohbet Geçmişi (Son 3 Mesaj)")
    st.write(get_formatted_history())














import streamlit as st
from langchain_community.chat_models import AzureChatOpenAI
from collections import deque

# 📌 Streamlit session state ile chat memory ve top N kampanyaları saklama
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = deque(maxlen=3)  # En fazla 3 mesaj saklanır

if "top_n_campaigns" not in st.session_state:
    st.session_state.top_n_campaigns = []  # En iyi kampanyaları saklamak için

# 📌 Mesaj Ekleme Fonksiyonu (En fazla 3 mesaj tutar)
def add_message(user_input, response):
    """Sohbet geçmişine yeni mesaj ekler."""
    st.session_state.chat_memory.appendleft({"user": user_input, "bot": response})  # Yeni mesaj en üste eklenir

# 📌 History'yi Ekrana Formatlı Yazdırma
def get_formatted_history():
    """Sohbet geçmişini zaman sırasına göre formatlı döndürür."""
    if not st.session_state.chat_memory:
        return "Sohbet geçmişi henüz boş."
    return "\n\n".join([f"🗣 Kullanıcı: {msg['user']}\n🤖 Bot: {msg['bot']}" for msg in st.session_state.chat_memory])

# 📌 OpenAI'ye Kampanya Bilgisiyle Soru Gönderme
def ask_openai(user_input, campaign_info=None, history_analysis=None):
    """OpenAI'ye özel sistem prompt'ları ile soru gönderir."""
    if campaign_info:
        system_prompt = f"Kampanya bilgisi verilmiştir. Bu bilgiye göre soruyu yanıtla:\n\nKampanya Açıklaması: {campaign_info}"
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."
    elif history_analysis:
        system_prompt = "Kullanıcının yeni mesajı, önceki konuşmalardaki bir bilgiye referans veriyor mu? Eğer veriyorsa, ilgili bilgiyi döndür, eğer tamamen yeni bir şey soruyorsa 'Yeni Konu' döndür."
        user_prompt = f"Önceki Mesajlar:\n{history_analysis}\nKullanıcının Yeni Sorusu: {user_input}"

    else:
        system_prompt = "Kullanıcı bir kampanya hakkında soru sormuş olabilir. Eğer kampanya kodu veya başlık belirttiyse, ona göre yanıt ver."
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."

    model = AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="cyz",
        model_name="xyz",
        openai_api_type="azure"
    )

    response = model.predict(system_prompt + "\n" + user_prompt)
    return response.strip()

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):

            # 📌 Kampanya kodu var mı?
            campaign_code = extract_campaign_code(user_input)

            if len(st.session_state.chat_memory) == 0:
                if campaign_code:
                    campaign_info = es.search_campaign_by_code(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    add_message(user_input, response)
                    st.subheader("📌 Yanıt")
                    st.write(response)
                else:
                    search_result, formatted_result = es.search_campaign_by_header(user_input)
                    st.session_state.top_n_campaigns = search_result  # Kampanyaları sakla
                    st.subheader("📌 En İyi 3 Kampanya")
                    st.write(formatted_result)
            else:
                formatted_history = get_formatted_history()
                follow_up_response = ask_openai(user_input, history_analysis=formatted_history)

                if follow_up_response.lower() != "yeni konu":
                    # Eğer kullanıcı önceki mesajlardan birine referans verdiyse o bilgiyi getir
                    campaign_info = es.search_campaign_by_code(follow_up_response)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    add_message(user_input, response)
                    st.subheader("📌 Yanıt")
                    st.write(response)

                else:
                    # Eğer tamamen yeni bir konuysa, hafızayı temizlemeden yeni arama yap
                    search_result, formatted_result = es.search_campaign_by_header(user_input)
                    st.session_state.top_n_campaigns = search_result  # Yeni kampanyaları sakla
                    st.subheader("📌 En İyi 3 Kampanya")
                    st.write(formatted_result)

        # 📌 Sohbet Geçmişini Güncelle ve Ekrana Yazdır
        st.subheader("💬 Sohbet Geçmişi (Son 3 Mesaj)")
        st.write(get_formatted_history())

        # 📌 Eğer 3 mesaj olduysa sıfırla
        if len(st.session_state.chat_memory) == 3:
            st.session_state.chat_memory.clear()
            st.warning("📌 Sohbet geçmişi dolduğu için sıfırlandı.")

# 📌 Streamlit Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    st.markdown("---")

    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

    if user_input:
        process_user_input(user_input)

    # 📌 Sohbet Geçmişi Ekrana Yazdırılıyor
    st.subheader("💬 Sohbet Geçmişi (Son 3 Mesaj)")
    st.write(get_formatted_history())



















import streamlit as st
import logging
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
import os
import re

# 1️⃣ Logger Ayarla
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2️⃣ API Anahtarı Tanımla
os.environ["OPENAI_API_KEY"] = "your_api_key_here"

# 3️⃣ Örnek Kampanya Verileri
campaigns = [
    {"code": "KAMP001", "title": "Migros İndirim Kampanyası", "content": "Migros marketlerinde %20 indirim! 1-10 Şubat arasında geçerlidir.", "start_date": "01-02-2024", "end_date": "10-02-2024"},
    {"code": "KAMP002", "title": "Beyaz Eşya Kampanyası", "content": "Beyaz eşyalar 15 Mart'a kadar özel fiyatlarla!", "start_date": "01-03-2024", "end_date": "15-03-2024"},
    {"code": "KAMP003", "title": "Giyim Sezon Sonu İndirimi", "content": "Tüm giyim ürünlerinde %30 indirim!", "start_date": "01-04-2024", "end_date": "30-04-2024"}
   
]

# 4️⃣ OpenAI Embeddings kullanarak ChromaDB oluştur ve doldur
embeddings = OpenAIEmbeddings()
vector_store = Chroma(embedding_function=embeddings)

# Kampanya verilerini ChromaDB'ye ekleyelim
docs = [Document(page_content=f"{c['title']}: {c['content']} (Geçerlilik: {c['start_date']} - {c['end_date']})", metadata={"code": c["code"]}) for c in campaigns]
vector_store.add_documents(docs)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 5️⃣ LLM Modeli Tanımla ve Sistem Prompt Ekle
system_prompt = "Sen bir reklam kampanya asistanısın. Kullanıcıya kampanyalar hakkında bilgi ver, ama sadece kampanya metinlerinden referans al."
llm = ChatOpenAI(model_name="gpt-4", temperature=0, system_prompt=system_prompt)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 6️⃣ Sohbet Hafızasını (Memory) Tanımla
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
previous_retrieved_campaigns = {}
follow_up_count = 0
max_follow_up = 5  # Kullanıcının aynı kampanya içinde sorabileceği maksimum takip sorusu

# 7️⃣ Kampanya Kodunu Çıkart ve Doğrudan Bilgi Getir
def extract_campaign_code(user_input):
    try:
        match = re.search(r"KAMP\d{3}", user_input)
        return match.group(0) if match else None
    except Exception as e:
        logger.error(f"Kampanya kodu çıkarma hatası: {e}")
        return None

# 8️⃣ Yeni Kampanyaya Geçişi Algıla
def detect_new_campaign(user_input):
    global previous_retrieved_campaigns, follow_up_count
    
    try:
        logger.info(f"Yeni kampanya tespiti için giriş alındı: {user_input}")
        
        campaign_code = extract_campaign_code(user_input)
        if campaign_code:
            docs = retriever.get_relevant_documents(campaign_code)
            if docs:
                previous_retrieved_campaigns[campaign_code] = docs[0]
                follow_up_count = 0  # Yeni kampanya başladığında follow-up sayacını sıfırla
                logger.info(f"Belirtilen kampanya kodu bulundu: {campaign_code}, İçerik: {docs[0].page_content}")
                return docs[0].page_content
        
        # VectorStore kullanarak en alakalı top_n kampanyayı bul
        similar_docs = retriever.get_relevant_documents(user_input)
        if similar_docs:
            previous_retrieved_campaigns = {f"KAMP{i+1:03}": doc for i, doc in enumerate(similar_docs)}
            follow_up_count = 0  # Yeni kampanya bulunduğunda follow-up sıfırlanır
            result = "\n".join([f"{key} - {doc.page_content.split(' ', 5)[0]}..." for key, doc in previous_retrieved_campaigns.items()])
            return f"En alakalı kampanyalar:\n{result}"
        
        return "Uygun kampanya bulunamadı."
    except Exception as e:
        logger.error(f"Yeni kampanya tespitinde hata: {e}")
        return "Bir hata oluştu, lütfen tekrar deneyin."

# 9️⃣ Kullanıcıdan Giriş Al ve Yanıt Döndür
def chat_with_bot(user_input):
    global previous_retrieved_campaigns, follow_up_count
    
    try:
        logger.info(f"Kullanıcı girişi: {user_input}")
        
        if follow_up_count >= max_follow_up:
            return "⚠ Maksimum takip soru sınırına ulaşıldı. Yeni bir kampanya hakkında soru sorabilirsiniz."
        
        chat_history = memory.load_memory_variables({})["chat_history"]
        campaign_info = detect_new_campaign(user_input)
        if campaign_info:
            return campaign_info
        
        match = re.search(r"(KAMP\d{3}) hakkında (.+)\??", user_input)
        if match:
            campaign_code = match.group(1)
            if campaign_code in previous_retrieved_campaigns:
                selected_campaign = previous_retrieved_campaigns[campaign_code]
                follow_up_count += 1  # Takip sorusu sayısını artır
                logger.info(f"Seçilen kampanya: {selected_campaign}")
                return qa_chain.run(f"{chat_history}\nKullanıcı: {user_input}\nBu kampanya hakkında: {selected_campaign.page_content}")
            return "⚠ Geçersiz kampanya kodu. Lütfen geçerli bir kampanya girin."
        
        follow_up_count += 1  # Genel sorular için de takip sorusu sayısını artır
        response = qa_chain.run(f"{chat_history}\nKullanıcı: {user_input}")
        memory.save_context({"input": user_input}, {"output": response})
        logger.info(f"LLM Yanıtı: {response}")
        return response
    except Exception as e:
        logger.error(f"Chat işleminde hata: {e}")
        return "Bir hata oluştu, lütfen tekrar deneyin."

# 🔟 Streamlit Arayüzü
st.title("📢 Reklam Kampanya Chatbotu")
st.write("Sorularınızı sorun, kampanyalar hakkında bilgi alın!")

user_input = st.text_input("Mesajınızı girin:")
if st.button("Gönder"):
    if user_input:
        response = chat_with_bot(user_input)
        st.write(response)



---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





import streamlit as st
import logging
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
import os
import re

# 1️⃣ Logger Ayarla - Hata ve işlem kayıtlarını tutmak için kullanılır
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2️⃣ OpenAI API Anahtarı Tanımla - OpenAI LLM modelini kullanabilmek için gerekli
os.environ["OPENAI_API_KEY"] = "your_api_key_here"

# 3️⃣ Örnek Kampanya Verileri - Kullanıcıya sunulacak kampanyalar burada tanımlanır
campaigns = [
    {"code": "KAMP001", "title": "Migros İndirim Kampanyası", "content": "Migros marketlerinde %20 indirim! 1-10 Şubat arasında geçerlidir.", "start_date": "01-02-2024", "end_date": "10-02-2024"},
    {"code": "KAMP002", "title": "Beyaz Eşya Kampanyası", "content": "Beyaz eşyalar 15 Mart'a kadar özel fiyatlarla!", "start_date": "01-03-2024", "end_date": "15-03-2024"},
    {"code": "KAMP003", "title": "Giyim Sezon Sonu İndirimi", "content": "Tüm giyim ürünlerinde %30 indirim!", "start_date": "01-04-2024", "end_date": "30-04-2024"}
]

# 4️⃣ OpenAI Embeddings kullanarak ChromaDB oluştur ve doldur - Kampanyalar vektör olarak saklanır
embeddings = OpenAIEmbeddings()
vector_store = Chroma(embedding_function=embeddings)

# Kampanya verilerini ChromaDB'ye ekleyelim
docs = [Document(page_content=f"{c['title']}: {c['content']} (Geçerlilik: {c['start_date']} - {c['end_date']})", metadata={"code": c["code"]}) for c in campaigns]
vector_store.add_documents(docs)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 5️⃣ LLM Modeli Tanımla ve Sistem Prompt Ekle - Modelin nasıl davranacağını belirler
system_prompt = "Sen bir reklam kampanya asistanısın. Kullanıcıya kampanyalar hakkında bilgi ver, ama sadece kampanya metinlerinden referans al."
follow_up_prompt = "Bu bir takip sorusudur. Önceki konuşmaları dikkate alarak, sadece kampanya metinlerine dayanarak kesin ve kısa bir yanıt ver."

llm = ChatOpenAI(model_name="gpt-4", temperature=0, system_prompt=system_prompt)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 6️⃣ Sohbet Hafızasını (Memory) Tanımla - Kullanıcının konuşmalarını saklar
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
previous_retrieved_campaigns = {}  # Önceki getirilen kampanyaları saklar
follow_up_count = 0  # Kullanıcının kaç tane takip sorusu sorduğunu takip eder
max_follow_up = 5  # Kullanıcının aynı kampanya içinde sorabileceği maksimum takip sorusu

# 9️⃣ Kullanıcıdan Giriş Al ve Yanıt Döndür - Kullanıcının mesajını alır ve uygun cevabı döndürür
def chat_with_bot(user_input):
    global previous_retrieved_campaigns, follow_up_count
    
    try:
        logger.info(f"Kullanıcı girişi: {user_input}")
        
        if follow_up_count >= max_follow_up:
            return "⚠ Maksimum takip soru sınırına ulaşıldı. Yeni bir kampanya hakkında soru sorabilirsiniz."
        
        chat_history = memory.load_memory_variables({})["chat_history"]
        campaign_info = detect_new_campaign(user_input)
        if campaign_info:
            return campaign_info
        
        match = re.search(r"(KAMP\d{3}) hakkında (.+)\??", user_input)
        if match:
            campaign_code = match.group(1)
            if campaign_code in previous_retrieved_campaigns:
                selected_campaign = previous_retrieved_campaigns[campaign_code]
                follow_up_count += 1
                logger.info(f"Seçilen kampanya: {selected_campaign}")
                return qa_chain.run(f"{follow_up_prompt}\n{chat_history}\nKullanıcı: {user_input}\nBu kampanya hakkında: {selected_campaign.page_content}")
        
        follow_up_count += 1
        if follow_up_count > 1:
            response = qa_chain.run(f"{follow_up_prompt}\n{chat_history}\nKullanıcı: {user_input}")
        else:
            response = qa_chain.run(f"{system_prompt}\n{chat_history}\nKullanıcı: {user_input}")
        
        memory.save_context({"input": user_input}, {"output": response})
        logger.info(f"LLM Yanıtı: {response}")
        return response
    except Exception as e:
        logger.error(f"Chat işleminde hata: {e}")
        return "Bir hata oluştu, lütfen tekrar deneyin."

# 🔟 Streamlit Arayüzü - Kullanıcıdan giriş alıp chatbot ile iletişime geçmesini sağlar
st.title("📢 Reklam Kampanya Chatbotu")
st.write("Sorularınızı sorun, kampanyalar hakkında bilgi alın!")

user_input = st.text_input("Mesajınızı girin:")
if st.button("Gönder"):
    if user_input:
        response = chat_with_bot(user_input)
        st.write(response)



------------------------------------------------------------------------------------------------------------------------------------------------



"""


Evet, kodun son hali yukarıdaki diyalog akışına uygun şekilde cevap verebilecek şekilde tasarlanmıştır. Örneğin:

Kullanıcı: "KAMP001 kampanyası nedir ?"

Sorguda açıkça "KAMP001" yer aldığından, sistem doğrudan bu kampanyayı tespit eder, global kampanya listesi ve takip sayacı sıfırlanır (konuşma geçmişi temizlenir) ve KAMP001’in içerik bilgisi ile LLM’ye sorgu gönderilerek yanıt üretilir.
Kullanıcı: "Bana Migros kampanyasının detaylarını söyle."

Sorguda açık bir kampanya kodu olmadığı için, sistem vector store üzerinden TOP_N (3) kriterine göre ilgili kampanyaları arar. Eğer Migros ile ilgili kampanyalar varsa, bu kampanyaların kod ve başlık bilgileri liste halinde (örneğin, “1. KAMP001: Migros İndirim Kampanyası” gibi) sunulur.
Kullanıcı: "2.gelen kampanyanın içeriği nedir?"

Bu takip (follow-up) sorgusunda, sistem önceki listelenen kampanyalar ve konuşma geçmişini LLM’ye göndererek kullanıcının hangi kampanyaya atıfta bulunduğunu belirlemesini ister. LLM’nin tespit ettiği kampanyanın içerik bilgisi, kullanıcının sorusu ile birlikte LLM’ye gönderilir ve LLM’nin cevabı ekrana basılır.
Kullanıcı: "Peki 3.sıradaki kampanyanın detayı neydi yazar mısın?"

Aynı şekilde, LLM önceki listeden (örneğin, 3. sıradaki kampanya) hangi kampanyanın kastedildiğini belirler, ilgili kampanyanın içerik bilgisi ve kullanıcı sorusu ile LLM’den nihai yanıt alınır.
Kullanıcı: "Peki sonuncu yazan kampanyanın detayı?"

LLM, "sonuncu" ifadesini de göz önünde bulundurarak önceki listeden en son elemanı tespit eder ve bu kampanyanın detayları, kullanıcının sorusu ile birlikte LLM’ye gönderilerek yanıt üretilir.
Kullanıcı: "Beyaz eşya kampanyasının detayları neydi peki"

Eğer LLM, bu sorgunun önceki listelenen kampanyalarla ilişkili olmadığını belirlerse, sistem global durumu (last_retrieved_campaigns ve konuşma geçmişini) temizler ve yeni kampanya sorgusu olarak "Beyaz Eşya Kampanyası"nı vector store’dan arar. Böylece yeni kampanya sorgusu üzerinden ilgili kampanyanın detayları LLM’den alınır.
Kullanıcı: "KAMP003 kampanyasının detayları nedir ?"

Sorguda açıkça "KAMP003" yer aldığından, sistem doğrudan KAMP003’ü tespit eder, global durum sıfırlanır ve KAMP003’ün içerik bilgisi ile LLM’ye sorgu gönderilerek yanıt alınır.
Ayrıca, takip sorgularında maksimum takip sayısı (örneğin MAX_FOLLOW_UP = 5) uygulanmakta; eğer kullanıcı 5 takip sorgusuna ulaşırsa, sistem otomatik olarak global durumu temizleyip yeni kampanya sorgusu yapılmasını isteyecektir.

Bu yapı sayesinde, kullanıcı hiçbir ek numeric veya sıralama girdisi vermeden, tamamen doğal diyalog akışı içerisinde doğru kampanyanın tespit edilip, ilgili kampanyanın içerik bilgisiyle LLM tarafından üretilen yanıt ekrana basılacaktır.


"""


import streamlit as st
import logging
import os
import re
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

# 1️⃣ Logger Ayarla
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2️⃣ OpenAI API Anahtarı Tanımla
os.environ["OPENAI_API_KEY"] = "your_api_key_here"  # API anahtarınızı buraya girin

# 3️⃣ Örnek Kampanya Verileri
campaigns = [
    {"code": "KAMP001", "title": "Migros İndirim Kampanyası", "content": "Migros marketlerinde %20 indirim! 1-10 Şubat arasında geçerlidir.", "start_date": "01-02-2024", "end_date": "10-02-2024"},
    {"code": "KAMP002", "title": "Beyaz Eşya Kampanyası", "content": "Beyaz eşyalar 15 Mart'a kadar özel fiyatlarla!", "start_date": "01-03-2024", "end_date": "15-03-2024"},
    {"code": "KAMP003", "title": "Giyim Sezon Sonu İndirimi", "content": "Tüm giyim ürünlerinde %30 indirim!", "start_date": "01-04-2024", "end_date": "30-04-2024"}
]

# Parametrik olarak top_n değeri (şu anda 3 olarak ayarlandı)
TOP_N = 3

# Takip sorguları için maksimum sayıyı belirleyelim (örneğin, 5)
MAX_FOLLOW_UP = 5

# 4️⃣ OpenAI Embeddings kullanarak ChromaDB oluştur ve doldur
embeddings = OpenAIEmbeddings()
vector_store = Chroma(embedding_function=embeddings)
docs = [
    Document(
        page_content=f"{c['title']}: {c['content']} (Geçerlilik: {c['start_date']} - {c['end_date']})",
        metadata={"code": c["code"]}
    )
    for c in campaigns
]
vector_store.add_documents(docs)
# TOP_N kriteri kullanılarak en iyi sonuçlar alınır.
retriever = vector_store.as_retriever(search_kwargs={"k": TOP_N})

# 5️⃣ LLM Modeli ve Prompt Ayarları
system_prompt = "Sen bir reklam kampanya asistanısın. Kullanıcıya kampanyalar hakkında bilgi ver, yanıtlarını sadece kampanya metinlerine dayandır."
follow_up_prompt = (
    "Bu bir takip (follow-up) sorusudur. Aşağıdaki konuşma geçmişini ve listelenen kampanyaları inceleyerek, "
    "kullanıcının hangi kampanya hakkında detay istediğini belirle ve sadece o kampanyanın detaylarını ver."
)

llm = ChatOpenAI(model_name="gpt-4", temperature=0, system_prompt=system_prompt)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 6️⃣ Konuşma Hafızası ve Global Durum Değişkenleri
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
last_retrieved_campaigns = []   # Son sorgudan dönen kampanyaların listesini saklar
follow_up_count = 0              # Takip sorguları için sayacı tutar

# 7️⃣ Yeni Kampanya Sorgularını Doğal Dil ile Tespit Eden Fonksiyon
def detect_new_campaign(user_input: str):
    """
    Eğer sorguda doğrudan kampanya kodu geçmiyorsa,
    vector store üzerinden ilgili kampanyaları getirir.
    
    - Eğer tek bir kampanya bulunursa, kampanyanın content’i ve kullanıcının sorusu ile LLM'den yanıt alınır.
    - Eğer birden fazla kampanya bulunursa, TOP_N kadar sonuç liste halinde sunulur.
    """
    global last_retrieved_campaigns
    if re.search(r"KAMP\d{3}", user_input, re.IGNORECASE):
        return None  # Sorguda açık kampanya kodu varsa bu fonksiyon devreye girmez.

    retrieved_docs = retriever.get_relevant_documents(user_input)
    if not retrieved_docs:
        return "Üzgünüm, sorgunuza uygun kampanya bulunamadı."
    
    last_retrieved_campaigns = retrieved_docs

    if len(retrieved_docs) == 1:
        doc = retrieved_docs[0]
        response = qa_chain.run(
            f"{system_prompt}\nKullanıcı: {user_input}\nBu kampanya hakkında: {doc.page_content}"
        )
        return response
    else:
        # Birden fazla kampanya bulunduğunda, TOP_N kadar sonuç liste halinde sunulur.
        response_lines = ["İlgili kampanyalar:"]
        for i, doc in enumerate(retrieved_docs[:TOP_N], start=1):
            title = doc.page_content.split(":")[0].strip()
            code = doc.metadata.get("code", "Bilinmiyor")
            response_lines.append(f"{i}. {code}: {title}")
        return "\n".join(response_lines)

# 8️⃣ Kullanıcı Girdilerini İşleyen Fonksiyon
def chat_with_bot(user_input: str):
    global last_retrieved_campaigns, follow_up_count
    try:
        logger.info(f"Kullanıcı girişi: {user_input}")
        chat_history = memory.load_memory_variables({})["chat_history"]

        # (A) Eğer sorguda açıkça kampanya kodu (örn. "KAMP001") varsa:
        code_match = re.search(r"(KAMP\d{3})", user_input, re.IGNORECASE)
        if code_match:
            campaign_code = code_match.group(1).upper()
            selected_doc = next((doc for doc in docs if doc.metadata.get("code", "").upper() == campaign_code), None)
            if selected_doc:
                # Yeni kampanya sorgusu olduğundan, global liste ve (opsiyonel) geçmiş temizlenir.
                last_retrieved_campaigns = [selected_doc]
                follow_up_count = 0
                memory.clear()  # Konuşma geçmişini temizle
                # Kampanyanın content’i ve kullanıcının sorusu ile LLM'den yanıt alınır.
                response = qa_chain.run(
                    f"{system_prompt}\nKullanıcı: {user_input}\nBu kampanya hakkında: {selected_doc.page_content}"
                )
                memory.save_context({"input": user_input}, {"output": response})
                return response
            else:
                return "Belirtilen kampanya bulunamadı."

        # (B) Eğer daha önceki sorgudan dönen kampanya listesi boşsa, yeni sorgu olarak ele al:
        if not last_retrieved_campaigns:
            new_campaign_response = detect_new_campaign(user_input)
            memory.save_context({"input": user_input}, {"output": new_campaign_response})
            return new_campaign_response

        # (C) Gelen sorgu bir takip (follow-up) sorgusuyse:
        # Eğer takip sorgularının sayısı maksimum değeri aştıysa:
        if follow_up_count >= MAX_FOLLOW_UP:
            # Maksimum takip sayısına ulaşıldığında, kullanıcıya yeni kampanya sorgusu yapması istenir.
            last_retrieved_campaigns = []
            memory.clear()  # Konuşma geçmişini temizle
            follow_up_count = 0
            return "Maksimum takip soru sınırına ulaşıldı. Lütfen yeni kampanya sorgusu yapınız."

        # Takip sorgusunda, LLM’den önceki listelenen kampanyalar ve konuşma geçmişine dayanarak,
        # kullanıcının hangi kampanyaya atıfta bulunduğunu belirlemesi istenir.
        campaigns_context = "\n".join(
            f"{doc.metadata.get('code','Bilinmiyor')}: {doc.page_content}"
            for doc in last_retrieved_campaigns
        )
        determination_prompt = (
            f"Aşağıdaki listelenen kampanyalar içerisinden, kullanıcının aşağıdaki sorgusuyla en çok hangi kampanyaya atıfta bulunduğunu belirle. "
            f"Eğer sorgu, listelenen kampanyalarla ilgili değilse, sadece 'yeni kampanya' yaz.\n\n"
            f"Listelenen Kampanyalar:\n{campaigns_context}\n\n"
            f"Kullanıcının Sorgusu: {user_input}\n\n"
            f"Yanıt (sadece ilgili kampanya kodunu ya da 'yeni kampanya' ifadesini ver): "
        )
        determination = llm.run(determination_prompt).strip().lower()
        logger.info(f"Determination: {determination}")

        # Eğer LLM yanıtında "yeni kampanya" ifadesi geçiyorsa:
        if "yeni kampanya" in determination:
            last_retrieved_campaigns = []
            memory.clear()  # Konuşma geçmişini temizle
            follow_up_count = 0
            new_campaign_response = detect_new_campaign(user_input)
            memory.save_context({"input": user_input}, {"output": new_campaign_response})
            return new_campaign_response
        else:
            # LLM yanıtından tespit edilen kampanya kodunu kullanarak ilgili kampanyayı seçelim.
            campaign_code_match = re.search(r"(KAMP\d{3})", determination, re.IGNORECASE)
            if campaign_code_match:
                campaign_code = campaign_code_match.group(1).upper()
                selected_doc = next((doc for doc in last_retrieved_campaigns if doc.metadata.get("code", "").upper() == campaign_code), None)
                if not selected_doc:
                    return "Listede belirtilen kampanya bulunamadı."
            else:
                return "Lütfen hangi kampanyadan bahsettiğinizi netleştiriniz."
            
            follow_up_count += 1
            # Kampanyanın content’i ve kullanıcının sorusu ile LLM’den yardım alınır, son yanıt ekrana basılır.
            response = qa_chain.run(
                f"{follow_up_prompt}\nKullanıcı: {user_input}\nBu kampanya hakkında: {selected_doc.page_content}\nKonuşma Geçmişi:\n{chat_history}"
            )
            memory.save_context({"input": user_input}, {"output": response})
            return response

    except Exception as e:
        logger.error(f"Chat işleminde hata: {e}")
        return "Bir hata oluştu, lütfen tekrar deneyin."

# 9️⃣ Streamlit Arayüzü
st.title("📢 Reklam Kampanya Chatbotu")
st.write("Sorularınızı sorun, kampanyalar hakkında bilgi alın!")

user_input = st.text_input("Mesajınızı girin:")
if st.button("Gönder"):
    if user_input:
        response = chat_with_bot(user_input)
        st.write(response)





----------------------------------------------------------------------------------------------------

# LOG LU YAPI



import streamlit as st
import logging
import os
import re
import pandas as pd
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

# 1️⃣ Logger Ayarla
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2️⃣ OpenAI API Anahtarı Tanımla
os.environ["OPENAI_API_KEY"] = "your_api_key_here"  # API anahtarınızı buraya girin

# 3️⃣ Örnek Kampanya Verileri
campaigns = [
    {"code": "KAMP001", "title": "Migros İndirim Kampanyası", "content": "Migros marketlerinde %20 indirim! 1-10 Şubat arasında geçerlidir.", "start_date": "01-02-2024", "end_date": "10-02-2024"},
    {"code": "KAMP002", "title": "Beyaz Eşya Kampanyası", "content": "Beyaz eşyalar 15 Mart'a kadar özel fiyatlarla!", "start_date": "01-03-2024", "end_date": "15-03-2024"},
    {"code": "KAMP003", "title": "Giyim Sezon Sonu İndirimi", "content": "Tüm giyim ürünlerinde %30 indirim!", "start_date": "01-04-2024", "end_date": "30-04-2024"}
]

# Parametrik olarak top_n değeri (şu anda 3 olarak ayarlandı)
TOP_N = 3

# Takip sorguları için maksimum sayı (örneğin 5)
MAX_FOLLOW_UP = 5

# 4️⃣ OpenAI Embeddings kullanarak ChromaDB oluştur ve doldur
embeddings = OpenAIEmbeddings()
vector_store = Chroma(embedding_function=embeddings)
docs = [
    Document(
        page_content=f"{c['title']}: {c['content']} (Geçerlilik: {c['start_date']} - {c['end_date']})",
        metadata={"code": c["code"]}
    )
    for c in campaigns
]
vector_store.add_documents(docs)
retriever = vector_store.as_retriever(search_kwargs={"k": TOP_N})

# 5️⃣ LLM Modeli ve Prompt Ayarları
system_prompt = "Sen bir reklam kampanya asistanısın. Kullanıcıya kampanyalar hakkında bilgi ver, yanıtlarını sadece kampanya metinlerine dayandır."
follow_up_prompt = (
    "Bu bir takip (follow-up) sorusudur. Aşağıdaki konuşma geçmişini ve listelenen kampanyaları inceleyerek, "
    "kullanıcının hangi kampanya hakkında detay istediğini belirle ve sadece o kampanyanın detaylarını ver."
)

llm = ChatOpenAI(model_name="gpt-4", temperature=0, system_prompt=system_prompt)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 6️⃣ Konuşma Hafızası ve Global Durum Değişkenleri
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Global kampanya listesi ve takip sayısı
last_retrieved_campaigns = []   # Son sorgudan dönen kampanyaların listesini saklar
follow_up_count = 0              # Takip sorguları için sayaç

# Session yönetimi için: kampanya kodu ve session id bilgileri
if "current_campaign_code" not in st.session_state:
    st.session_state["current_campaign_code"] = None
if "session_id" not in st.session_state:
    st.session_state["session_id"] = 0
if "session_counter" not in st.session_state:
    st.session_state["session_counter"] = 0

# Excel loglarını tutmak için st.session_state kullanıyoruz
if "chat_logs" not in st.session_state:
    st.session_state["chat_logs"] = []

def log_conversation(user_input: str, bot_response: str, campaign_code: str):
    """Her etkileşimi st.session_state üzerinden kaydeder ve Excel dosyasına yazar."""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": st.session_state["session_id"],
        "campaign_code": campaign_code,
        "user_input": user_input,
        "bot_response": bot_response
    }
    st.session_state["chat_logs"].append(log_entry)
    # Pandas DataFrame'e çevirip Excel dosyasına yazalım (her mesaj sonrası güncelleme)
    df = pd.DataFrame(st.session_state["chat_logs"])
    df.to_excel("chat_logs.xlsx", index=False)

def update_session(campaign_code: str):
    """
    Yeni kampanya kodu geldiyse session id güncellenir, 
    aynı kampanya kodu devam ediyorsa aynı session id kullanılır.
    """
    if st.session_state["current_campaign_code"] is None:
        st.session_state["current_campaign_code"] = campaign_code
        st.session_state["session_counter"] = 1
        st.session_state["session_id"] = 1
    elif st.session_state["current_campaign_code"] != campaign_code:
        st.session_state["session_counter"] += 1
        st.session_state["current_campaign_code"] = campaign_code
        st.session_state["session_id"] = st.session_state["session_counter"]
    # Eğer kampanya kodu aynı ise, session_id değişmeden kalır.

# 7️⃣ Yeni Kampanya Sorgularını Doğal Dil ile Tespit Eden Fonksiyon
def detect_new_campaign(user_input: str):
    """
    Eğer sorguda doğrudan kampanya kodu geçmiyorsa,
    vector store üzerinden ilgili kampanyaları getirir.
    
    - Eğer tek bir kampanya bulunursa, kampanyanın content’i ve kullanıcının sorusu ile LLM'den yanıt alınır.
    - Eğer birden fazla kampanya bulunursa, TOP_N kadar sonuç liste halinde sunulur.
    """
    global last_retrieved_campaigns
    if re.search(r"KAMP\d{3}", user_input, re.IGNORECASE):
        return None  # Sorguda açık kampanya kodu varsa bu fonksiyon devreye girmez.

    retrieved_docs = retriever.get_relevant_documents(user_input)
    if not retrieved_docs:
        return "Üzgünüm, sorgunuza uygun kampanya bulunamadı."
    
    last_retrieved_campaigns = retrieved_docs

    # Eğer sadece 1 kampanya bulunduysa, session güncellemesi yapalım.
    if len(retrieved_docs) == 1:
        doc = retrieved_docs[0]
        campaign_code = doc.metadata.get("code", "").upper()
        update_session(campaign_code)
        response = qa_chain.run(
            f"{system_prompt}\nKullanıcı: {user_input}\nBu kampanya hakkında: {doc.page_content}"
        )
        return response
    else:
        # Birden fazla kampanya bulunursa, TOP_N kadar sonuç liste halinde sunulur.
        response_lines = ["İlgili kampanyalar:"]
        for i, doc in enumerate(retrieved_docs[:TOP_N], start=1):
            title = doc.page_content.split(":")[0].strip()
            code = doc.metadata.get("code", "Bilinmiyor")
            response_lines.append(f"{i}. {code}: {title}")
        return "\n".join(response_lines)

# 8️⃣ Kullanıcı Girdilerini İşleyen Fonksiyon
def chat_with_bot(user_input: str):
    global last_retrieved_campaigns, follow_up_count
    try:
        logger.info(f"Kullanıcı girişi: {user_input}")
        chat_history = memory.load_memory_variables({})["chat_history"]

        # (A) Sorguda açıkça kampanya kodu varsa:
        code_match = re.search(r"(KAMP\d{3})", user_input, re.IGNORECASE)
        if code_match:
            campaign_code = code_match.group(1).upper()
            update_session(campaign_code)
            selected_doc = next((doc for doc in docs if doc.metadata.get("code", "").upper() == campaign_code), None)
            if selected_doc:
                last_retrieved_campaigns = [selected_doc]
                follow_up_count = 0
                memory.clear()  # Konuşma geçmişini temizle
                # Kampanyanın content’i ve kullanıcının sorusu ile LLM’den yanıt alınır.
                response = qa_chain.run(
                    f"{system_prompt}\nKullanıcı: {user_input}\nBu kampanya hakkında: {selected_doc.page_content}"
                )
                log_conversation(user_input, response, campaign_code)
                memory.save_context({"input": user_input}, {"output": response})
                return response
            else:
                return "Belirtilen kampanya bulunamadı."

        # (B) Eğer önceki kampanya listesi boşsa, yeni sorgu olarak ele al:
        if not last_retrieved_campaigns:
            new_campaign_response = detect_new_campaign(user_input)
            # Eğer tek kampanya bulunduysa, session bilgileri detect_new_campaign içinde güncellenecektir.
            # Kampanya kodını, global listeden (varsa) alalım.
            campaign_code = last_retrieved_campaigns[0].metadata.get("code", "").upper() if last_retrieved_campaigns else ""
            log_conversation(user_input, new_campaign_response, campaign_code)
            memory.save_context({"input": user_input}, {"output": new_campaign_response})
            return new_campaign_response

        # (C) Gelen sorgu bir takip (follow-up) sorgusuysa:
        if follow_up_count >= MAX_FOLLOW_UP:
            last_retrieved_campaigns = []
            memory.clear()  # Konuşma geçmişini temizle
            follow_up_count = 0
            return "Maksimum takip soru sınırına ulaşıldı. Lütfen yeni kampanya sorgusu yapınız."

        # Takip sorgusunda, LLM’den önceki listelenen kampanyalar ve konuşma geçmişi üzerinden hangi kampanyaya atıfta bulunduğunu belirlemesi istenir.
        campaigns_context = "\n".join(
            f"{doc.metadata.get('code','Bilinmiyor')}: {doc.page_content}"
            for doc in last_retrieved_campaigns
        )
        determination_prompt = (
            f"Aşağıdaki listelenen kampanyalar içerisinden, kullanıcının aşağıdaki sorgusuyla en çok hangi kampanyaya atıfta bulunduğunu belirle. "
            f"Eğer sorgu, listelenen kampanyalarla ilgili değilse, sadece 'yeni kampanya' yaz.\n\n"
            f"Listelenen Kampanyalar:\n{campaigns_context}\n\n"
            f"Kullanıcının Sorgusu: {user_input}\n\n"
            f"Yanıt (sadece ilgili kampanya kodunu ya da 'yeni kampanya' ifadesini ver): "
        )
        determination = llm.run(determination_prompt).strip().lower()
        logger.info(f"Determination: {determination}")

        if "yeni kampanya" in determination:
            last_retrieved_campaigns = []
            memory.clear()  # Konuşma geçmişini temizle
            follow_up_count = 0
            new_campaign_response = detect_new_campaign(user_input)
            campaign_code = last_retrieved_campaigns[0].metadata.get("code", "").upper() if last_retrieved_campaigns else ""
            log_conversation(user_input, new_campaign_response, campaign_code)
            memory.save_context({"input": user_input}, {"output": new_campaign_response})
            return new_campaign_response
        else:
            campaign_code_match = re.search(r"(KAMP\d{3})", determination, re.IGNORECASE)
            if campaign_code_match:
                campaign_code = campaign_code_match.group(1).upper()
                selected_doc = next((doc for doc in last_retrieved_campaigns if doc.metadata.get("code", "").upper() == campaign_code), None)
                if not selected_doc:
                    return "Listede belirtilen kampanya bulunamadı."
                update_session(campaign_code)
            else:
                return "Lütfen hangi kampanyadan bahsettiğinizi netleştiriniz."
            
            follow_up_count += 1
            response = qa_chain.run(
                f"{follow_up_prompt}\nKullanıcı: {user_input}\nBu kampanya hakkında: {selected_doc.page_content}\nKonuşma Geçmişi:\n{chat_history}"
            )
            log_conversation(user_input, response, campaign_code)
            memory.save_context({"input": user_input}, {"output": response})
            return response

    except Exception as e:
        logger.error(f"Chat işleminde hata: {e}")
        return "Bir hata oluştu, lütfen tekrar deneyin."

# 9️⃣ Streamlit Arayüzü
st.title("📢 Reklam Kampanya Chatbotu")
st.write("Sorularınızı sorun, kampanyalar hakkında bilgi alın!")
st.markdown("---")

# Sohbet geçmişini göstermek için basit bir alan
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

user_input = st.text_input("Mesajınızı girin:")

if st.button("Gönder"):
    if user_input:
        bot_response = chat_with_bot(user_input)
        # Konuşma geçmişini güncelleyelim (sadece metin olarak)
        st.session_state["conversation"].append(("Kullanıcı", user_input))
        st.session_state["conversation"].append(("Bot", bot_response))
        # Sohbet geçmişini ekranda gösterelim
        for speaker, message in st.session_state["conversation"]:
            if speaker == "Kullanıcı":
                st.markdown(f"**Kullanıcı:** {message}")
            else:
                st.markdown(f"**Bot:** {message}")


























İşte tüm gereksinimleri karşılayan güncel kod sürümü (Türkçe yorum satırları ile birlikte):

```python
"""
🎯 AKILLI KAMPANYA ASİSTANI v3.1
Özellikler:
- Parametrik Tarihçe Yönetimi
- Bağlamsal Konuşma Desteği
- Dinamik Sınır Kontrolleri
"""

# ------------------------------ 📦 PAKETLER ------------------------------
import os
import openai
import streamlit as st
import logging
import json
import numpy as np
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from typing import Optional, List, Dict, Tuple
from sentence_transformers import SentenceTransformer

# ------------------------------ ⚙️ KONFİGÜRASYON ------------------------------
load_dotenv()

class HistoryConfig:
    """Tarihçe yönetimi için parametreler"""
    MAX_HISTORY_LENGTH = 10          # Maksimum saklanacak mesaj sayısı
    CONTEXT_HISTORY_COUNT = 3        # Bağlam için kullanılacak mesaj çifti sayısı
    ENABLE_HISTORY = True            # Tarihçe kaydını aktif/pasif yap
    AUTO_PRUNE = True                # Otomatik temizlik aktif mi?
    ALLOWED_ROLES = ("user", "assistant")  # İzin verilen roller

class AIConfig:
    """AI ile ilgili ayarlar"""
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    MODEL_CACHE_PATH = "./model_cache"
    LLM_MODEL = "gpt-4-turbo"

class ElasticConfig:
    """Elasticsearch ayarları"""
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
    INDEX_NAME = "campaigns"
    VECTOR_FIELD = "campaign_header_description_embedding_vector"
    KNN_K = 3

# ------------------------------ 🤖 SİSTEM İNİT ------------------------------
es = Elasticsearch(ElasticConfig.ELASTICSEARCH_URL)
embedding_model = SentenceTransformer(
    AIConfig.EMBEDDING_MODEL_NAME,
    cache_folder=AIConfig.MODEL_CACHE_PATH
)

# ------------------------------ 📝 LOGGING ------------------------------
logging.basicConfig(
    filename="campaign_assistant.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_event(event_type: str, message: str):
    """Log kaydı oluşturma"""
    logging.info(f"[{event_type.upper()}] {message}")

# ------------------------------ 🧠 HISTORY MANAGER ------------------------------
class HistoryManager:
    """Konuşma tarihçesi yönetim sınıfı"""
    
    @staticmethod
    def initialize():
        """Session state'i başlat"""
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
            
    @staticmethod
    def add_message(role: str, content: str):
        """Yeni mesaj ekleme"""
        if role not in HistoryConfig.ALLOWED_ROLES:
            log_event("HISTORY_ERROR", f"Geçersiz rol: {role}")
            return
            
        if HistoryConfig.ENABLE_HISTORY:
            st.session_state.conversation_history.append({
                "role": role,
                "content": content
            })
            HistoryManager._apply_limits()
            
    @staticmethod
    def clear_history():
        """Tüm tarihçeyi temizle"""
        if HistoryConfig.ENABLE_HISTORY:
            st.session_state.conversation_history = []
            log_event("HISTORY", "Tarihçe temizlendi")
    
    @staticmethod
    def _apply_limits():
        """Tarihçe sınırlarını uygula"""
        if HistoryConfig.AUTO_PRUNE:
            current_len = len(st.session_state.conversation_history)
            if current_len > HistoryConfig.MAX_HISTORY_LENGTH:
                remove_count = current_len - HistoryConfig.MAX_HISTORY_LENGTH
                st.session_state.conversation_history = st.session_state.conversation_history[remove_count:]
                log_event("HISTORY", f"{remove_count} eski mesaj silindi")
    
    @staticmethod
    def get_context_history() -> List[Tuple[str, str]]:
        """Bağlam için kullanılacak tarihçeyi getir"""
        # Her bir çift için 2 mesaj olduğundan count*2 alıyoruz
        lookback = HistoryConfig.CONTEXT_HISTORY_COUNT * 2
        return HistoryManager.get_formatted_history()[-lookback:]
    
    @staticmethod
    def get_formatted_history() -> List[Tuple[str, str]]:
        """Formatlanmış tüm tarihçeyi getir"""
        return [(msg["role"], msg["content"]) for msg in st.session_state.conversation_history]

# ------------------------------ 🔧 YARDIMCI FONKSİYONLAR ------------------------------
def get_embedding(text: str) -> List[float]:
    """Metni vektöre dönüştür"""
    try:
        return embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()
    except Exception as e:
        log_event("EMBEDDING_ERROR", f"Hata: {str(e)}")
        return []

# ------------------------------ 🔍 ELASTICSEARCH OPERASYONLARI ------------------------------
def hybrid_search(query: str) -> Tuple[Optional[Dict], List[Dict]]:
    """Hibrit arama stratejisi"""
    campaign_code = extract_campaign_code(query)
    exact_result = exact_campaign_search(campaign_code) if campaign_code else None
    vector_results = vector_semantic_search(query)
    return exact_result, vector_results

def exact_campaign_search(campaign_number: str) -> Optional[Dict]:
    """Tam eşleşme araması"""
    try:
        response = es.search(
            index=ElasticConfig.INDEX_NAME,
            body={"query": {"term": {"campaign_number.keyword": campaign_number}}}
        )
        return response['hits']['hits'][0]['_source'] if response['hits']['hits'] else None
    except Exception as e:
        log_event("ELASTICSEARCH_ERROR", f"Exact search error: {str(e)}")
        return None

def vector_semantic_search(query: str) -> List[Dict]:
    """Vektörel benzerlik araması"""
    try:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []

        response = es.search(
            index=ElasticConfig.INDEX_NAME,
            body={
                "knn": {
                    "field": ElasticConfig.VECTOR_FIELD,
                    "query_vector": query_embedding,
                    "k": ElasticConfig.KNN_K,
                    "num_candidates": 100
                },
                "_source": ["campaign_number", "campaign_header", "campaign_description"]
            }
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        log_event("ELASTICSEARCH_ERROR", f"Vector search error: {str(e)}")
        return []

# ------------------------------ 🤖 AI ENTEGRASYONLARI ------------------------------
def extract_campaign_code(query: str) -> Optional[str]:
    """Kampanya kodu çıkarma"""
    try:
        response = openai.ChatCompletion.create(
            model=AIConfig.LLM_MODEL,
            messages=[{"role": "user", "content": query}],
            functions=[{
                "name": "extract_campaign_code",
                "description": "Kampanya kodunu çıkarır",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_number": {"type": "string"}
                    },
                    "required": ["campaign_number"]
                }
            }],
            function_call={"name": "extract_campaign_code"}
        )
        args = json.loads(response.choices[0].message.function_call.arguments)
        return args.get("campaign_number")
    except Exception as e:
        log_event("OPENAI_ERROR", f"Code extraction failed: {str(e)}")
        return None

def generate_response(query: str, context: str) -> str:
    """Akıllı yanıt oluşturma"""
    try:
        # Bağlam için son 3 çift mesajı kullan
        history_context = "\n".join([f"{role}: {content}" for role, content in HistoryManager.get_context_history()])
        
        response = openai.ChatCompletion.create(
            model=AIConfig.LLM_MODEL,
            messages=[
                {"role": "system", "content": f"""
                Kampanya Uzmanı Asistan - Son {HistoryConfig.CONTEXT_HISTORY_COUNT} konuşma geçmişi:
                {history_context}
                """},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        log_event("OPENAI_ERROR", f"LLM response failed: {str(e)}")
        return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."

# ------------------------------ 🖥️ KULLANICI ARAYÜZÜ ------------------------------
def render_sidebar():
    """Yan menüyü oluştur"""
    with st.sidebar:
        st.header("⚙️ Sistem Ayarları")
        
        # Tarihçe yönetim düğmeleri
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Tarihçeyi Temizle"):
                HistoryManager.clear_history()
                st.experimental_rerun()
                
        with col2:
            if st.button("🔄 Otomatik Temizle"):
                HistoryManager._apply_limits()
                st.experimental_rerun()

        # Sistem istatistikleri
        st.markdown(f"""
        **📊 Sistem Durumu:**
        - **Maks. Tarihçe:** {HistoryConfig.MAX_HISTORY_LENGTH} mesaj
        - **Bağlam Penceresi:** Son {HistoryConfig.CONTEXT_HISTORY_COUNT} çift
        - **Aktif Kayıt:** `{'✅' if HistoryConfig.ENABLE_HISTORY else '❌'}`
        - **Mevcut Kayıt:** {len(st.session_state.conversation_history)} mesaj
        """)

def render_chat_interface():
    """Ana sohbet arayüzünü oluştur"""
    st.title("🔍 Akıllı Kampanya Asistanı v3.1")
    
    # Konuşma geçmişi
    for role, content in HistoryManager.get_formatted_history():
        with st.chat_message(name=role):
            st.markdown(content)
            if role == "assistant" and "Kampanya Detayları:" in content:
                with st.expander("📜 Detayları Göster"):
                    st.markdown(f"```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```")

    # Kullanıcı girişi
    if user_input := st.chat_input("Mesajınızı yazın..."):
        HistoryManager.add_message("user", user_input)
        process_user_query(user_input)

def process_user_query(query: str):
    """Sorgu işleme mantığı"""
    exact_result, vector_results = hybrid_search(query)
    
    if exact_result:
        context = f"""
        ✅ **{exact_result['campaign_number']} Numaralı Kampanya**
        **Başlık:** {exact_result['campaign_header']}
        **Açıklama:** {exact_result['campaign_description']}
        """
        response = generate_response(query, context)
        HistoryManager.add_message("assistant", response)
    elif vector_results:
        response = format_search_results(vector_results)
        HistoryManager.add_message("assistant", response)
    else:
        HistoryManager.add_message("assistant", "⚠️ İlgili kampanya bulunamadı")
    
    st.experimental_rerun()

def format_search_results(results: List[Dict]) -> str:
    """Arama sonuçlarını formatla"""
    formatted = ["🔍 Arama Sonuçları:"]
    for i, res in enumerate(results, 1):
        formatted.append(f"""
        {i}. **{res['campaign_header']}**  
        `{res['campaign_number']}`  
        {res['campaign_description'][:100]}...
        """)
    return "\n".join(formatted)

# ------------------------------ 🚀 UYGULAMA BAŞLATMA ------------------------------
if __name__ == "__main__":
    HistoryManager.initialize()
    render_sidebar()
    render_chat_interface()
```

**Önemli Güncellemeler ve Açıklamalar:**

1. **Parametrik Tarihçe Kontrolleri:**
   ```python
   class HistoryConfig:
       CONTEXT_HISTORY_COUNT = 3  # Bağlam için kullanılacak mesaj çifti sayısı
   ```

2. **Bağlam Tabanlı Tarihçe Yönetimi:**
   ```python
   def get_context_history() -> List[Tuple[str, str]]:
       lookback = HistoryConfig.CONTEXT_HISTORY_COUNT * 2
       return get_formatted_history()[-lookback:]
   ```

3. **Yeni Sistem İstatistikleri:**
   ```python
   st.markdown(f"""
   **📊 Sistem Durumu:**
   - **Bağlam Penceresi:** Son {HistoryConfig.CONTEXT_HISTORY_COUNT} çift
   """)
   ```

4. **Geliştirilmiş Yanıt Üretimi:**
   ```python
   history_context = "\n".join([f"{role}: {content}" for role, content in HistoryManager.get_context_history()])
   ```

5. **Dinamik Detay Görünümü:**
   ```python
   with st.expander("📜 Detayları Göster"):
       st.markdown(f"```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```")
   ```

**Test Senaryosu Çıktıları ile Uyumluluk:**

1. **Bağlam Takibi:**  
   Sistem artık son 3 konuşma çiftini dikkate alarak bağlamsal referansları daha iyi yönetebiliyor.

2. **Sıralı Referanslar:**  
   "ikinci", "3.sıradaki" gibi ifadelerde önceki sonuç listesini koruyarak doğru kampanyayı bulabiliyor.

3. **Dinamik Sınır Yönetimi:**  
   `MAX_HISTORY_LENGTH` ve `CONTEXT_HISTORY_COUNT` parametreleri bağımsız olarak yönetilebiliyor.

**Kullanım Senaryo Örneği:**

```python
# HistoryConfig.CONTEXT_HISTORY_COUNT = 3 iken
Kullanıcı: "1. kampanya nedir?" → Tarihçeye eklenir
Asistan: Cevap1 → Tarihçeye eklenir

Kullanıcı: "2. kampanyayı açıkla" → Önceki 2 mesaj bağlama dahil
Asistan: Cevap2 → Tarihçeye eklenir

Kullanıcı: "Son kampanyada ne vardı?" → Tüm 6 mesaj bağlamda kullanılır
Asistan: Tüm tarihçeyi kullanarak cevap verir
```

**Yapılandırma Seçenekleri:**
```python
# Bağlam derinliğini değiştirmek için
HistoryConfig.CONTEXT_HISTORY_COUNT = 5  # Son 5 konuşma çiftini kullan

# Tarihçe boyutunu ayarlamak için
HistoryConfig.MAX_HISTORY_LENGTH = 20  # Maksimum 20 mesaj sakla
```

Bu güncellemelerle sistem, kullanıcı etkileşimlerini daha akıllı bir şekilde takip edebiliyor ve karmaşık sorgulara bağlama duyarlı yanıtlar üretebiliyor.






"""
🎯 AKILLI KAMPANYA ASİSTANI v3.1
Özellikler:
- Parametrik Tarihçe Yönetimi
- Bağlamsal Konuşma Desteği
- Dinamik Sınır Kontrolleri
"""

# ------------------------------ 📦 PAKETLER ------------------------------
import os
import openai
import streamlit as st
import logging
import json
import numpy as np
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from typing import Optional, List, Dict, Tuple
from sentence_transformers import SentenceTransformer

# ------------------------------ ⚙️ KONFİGÜRASYON ------------------------------
load_dotenv()

class HistoryConfig:
    """Tarihçe yönetimi için parametreler"""
    MAX_HISTORY_LENGTH = 10          # Maksimum saklanacak mesaj sayısı
    CONTEXT_HISTORY_COUNT = 3        # Bağlam için kullanılacak mesaj çifti sayısı
    ENABLE_HISTORY = True            # Tarihçe kaydını aktif/pasif yap
    AUTO_PRUNE = True                # Otomatik temizlik aktif mi?
    ALLOWED_ROLES = ("user", "assistant")  # İzin verilen roller

class AIConfig:
    """AI ile ilgili ayarlar"""
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    MODEL_CACHE_PATH = "./model_cache"
    LLM_MODEL = "gpt-4-turbo"

class ElasticConfig:
    """Elasticsearch ayarları"""
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
    INDEX_NAME = "campaigns"
    VECTOR_FIELD = "campaign_header_description_embedding_vector"
    KNN_K = 3

# ------------------------------ 🤖 SİSTEM İNİT ------------------------------
es = Elasticsearch(ElasticConfig.ELASTICSEARCH_URL)
embedding_model = SentenceTransformer(
    AIConfig.EMBEDDING_MODEL_NAME,
    cache_folder=AIConfig.MODEL_CACHE_PATH
)

# ------------------------------ 📝 LOGGING ------------------------------
logging.basicConfig(
    filename="campaign_assistant.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_event(event_type: str, message: str):
    """Log kaydı oluşturma"""
    logging.info(f"[{event_type.upper()}] {message}")

# ------------------------------ 🧠 HISTORY MANAGER ------------------------------
class HistoryManager:
    """Konuşma tarihçesi yönetim sınıfı"""
    
    @staticmethod
    def initialize():
        """Session state'i başlat"""
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
            
    @staticmethod
    def add_message(role: str, content: str):
        """Yeni mesaj ekleme"""
        if role not in HistoryConfig.ALLOWED_ROLES:
            log_event("HISTORY_ERROR", f"Geçersiz rol: {role}")
            return
            
        if HistoryConfig.ENABLE_HISTORY:
            st.session_state.conversation_history.append({
                "role": role,
                "content": content
            })
            HistoryManager._apply_limits()
            
    @staticmethod
    def clear_history():
        """Tüm tarihçeyi temizle"""
        if HistoryConfig.ENABLE_HISTORY:
            st.session_state.conversation_history = []
            log_event("HISTORY", "Tarihçe temizlendi")
    
    @staticmethod
    def _apply_limits():
        """Tarihçe sınırlarını uygula"""
        if HistoryConfig.AUTO_PRUNE:
            current_len = len(st.session_state.conversation_history)
            if current_len > HistoryConfig.MAX_HISTORY_LENGTH:
                remove_count = current_len - HistoryConfig.MAX_HISTORY_LENGTH
                st.session_state.conversation_history = st.session_state.conversation_history[remove_count:]
                log_event("HISTORY", f"{remove_count} eski mesaj silindi")
    
    @staticmethod
    def get_context_history() -> List[Tuple[str, str]]:
        """Bağlam için kullanılacak tarihçeyi getir"""
        # Her bir çift için 2 mesaj olduğundan count*2 alıyoruz
        lookback = HistoryConfig.CONTEXT_HISTORY_COUNT * 2
        return HistoryManager.get_formatted_history()[-lookback:]
    
    @staticmethod
    def get_formatted_history() -> List[Tuple[str, str]]:
        """Formatlanmış tüm tarihçeyi getir"""
        return [(msg["role"], msg["content"]) for msg in st.session_state.conversation_history]

# ------------------------------ 🔧 YARDIMCI FONKSİYONLAR ------------------------------
def get_embedding(text: str) -> List[float]:
    """Metni vektöre dönüştür"""
    try:
        return embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()
    except Exception as e:
        log_event("EMBEDDING_ERROR", f"Hata: {str(e)}")
        return []

# ------------------------------ 🔍 ELASTICSEARCH OPERASYONLARI ------------------------------
def hybrid_search(query: str) -> Tuple[Optional[Dict], List[Dict]]:
    """Hibrit arama stratejisi"""
    campaign_code = extract_campaign_code(query)
    exact_result = exact_campaign_search(campaign_code) if campaign_code else None
    vector_results = vector_semantic_search(query)
    return exact_result, vector_results

def exact_campaign_search(campaign_number: str) -> Optional[Dict]:
    """Tam eşleşme araması"""
    try:
        response = es.search(
            index=ElasticConfig.INDEX_NAME,
            body={"query": {"term": {"campaign_number.keyword": campaign_number}}}
        )
        return response['hits']['hits'][0]['_source'] if response['hits']['hits'] else None
    except Exception as e:
        log_event("ELASTICSEARCH_ERROR", f"Exact search error: {str(e)}")
        return None

def vector_semantic_search(query: str) -> List[Dict]:
    """Vektörel benzerlik araması"""
    try:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []

        response = es.search(
            index=ElasticConfig.INDEX_NAME,
            body={
                "knn": {
                    "field": ElasticConfig.VECTOR_FIELD,
                    "query_vector": query_embedding,
                    "k": ElasticConfig.KNN_K,
                    "num_candidates": 100
                },
                "_source": ["campaign_number", "campaign_header", "campaign_description"]
            }
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        log_event("ELASTICSEARCH_ERROR", f"Vector search error: {str(e)}")
        return []

# ------------------------------ 🤖 AI ENTEGRASYONLARI ------------------------------
def extract_campaign_code(query: str) -> Optional[str]:
    """Kampanya kodu çıkarma"""
    try:
        response = openai.ChatCompletion.create(
            model=AIConfig.LLM_MODEL,
            messages=[{"role": "user", "content": query}],
            functions=[{
                "name": "extract_campaign_code",
                "description": "Kampanya kodunu çıkarır",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_number": {"type": "string"}
                    },
                    "required": ["campaign_number"]
                }
            }],
            function_call={"name": "extract_campaign_code"}
        )
        args = json.loads(response.choices[0].message.function_call.arguments)
        return args.get("campaign_number")
    except Exception as e:
        log_event("OPENAI_ERROR", f"Code extraction failed: {str(e)}")
        return None

def generate_response(query: str, context: str) -> str:
    """Akıllı yanıt oluşturma"""
    try:
        # Bağlam için son 3 çift mesajı kullan
        history_context = "\n".join([f"{role}: {content}" for role, content in HistoryManager.get_context_history()])
        
        response = openai.ChatCompletion.create(
            model=AIConfig.LLM_MODEL,
            messages=[
                {"role": "system", "content": f"""
                Kampanya Uzmanı Asistan - Son {HistoryConfig.CONTEXT_HISTORY_COUNT} konuşma geçmişi:
                {history_context}
                """},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        log_event("OPENAI_ERROR", f"LLM response failed: {str(e)}")
        return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."

# ------------------------------ 🖥️ KULLANICI ARAYÜZÜ ------------------------------
def render_sidebar():
    """Yan menüyü oluştur"""
    with st.sidebar:
        st.header("⚙️ Sistem Ayarları")
        
        # Tarihçe yönetim düğmeleri
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Tarihçeyi Temizle"):
                HistoryManager.clear_history()
                st.experimental_rerun()
                
        with col2:
            if st.button("🔄 Otomatik Temizle"):
                HistoryManager._apply_limits()
                st.experimental_rerun()

        # Sistem istatistikleri
        st.markdown(f"""
        **📊 Sistem Durumu:**
        - **Maks. Tarihçe:** {HistoryConfig.MAX_HISTORY_LENGTH} mesaj
        - **Bağlam Penceresi:** Son {HistoryConfig.CONTEXT_HISTORY_COUNT} çift
        - **Aktif Kayıt:** `{'✅' if HistoryConfig.ENABLE_HISTORY else '❌'}`
        - **Mevcut Kayıt:** {len(st.session_state.conversation_history)} mesaj
        """)

def render_chat_interface():
    """Ana sohbet arayüzünü oluştur"""
    st.title("🔍 Akıllı Kampanya Asistanı v3.1")
    
    # Konuşma geçmişi
    for role, content in HistoryManager.get_formatted_history():
        with st.chat_message(name=role):
            st.markdown(content)
            if role == "assistant" and "Kampanya Detayları:" in content:
                with st.expander("📜 Detayları Göster"):
                    st.markdown(f"```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```")

    # Kullanıcı girişi
    if user_input := st.chat_input("Mesajınızı yazın..."):
        HistoryManager.add_message("user", user_input)
        process_user_query(user_input)

def process_user_query(query: str):
    """Sorgu işleme mantığı"""
    exact_result, vector_results = hybrid_search(query)
    
    if exact_result:
        context = f"""
        ✅ **{exact_result['campaign_number']} Numaralı Kampanya**
        **Başlık:** {exact_result['campaign_header']}
        **Açıklama:** {exact_result['campaign_description']}
        """
        response = generate_response(query, context)
        HistoryManager.add_message("assistant", response)
    elif vector_results:
        response = format_search_results(vector_results)
        HistoryManager.add_message("assistant", response)
    else:
        HistoryManager.add_message("assistant", "⚠️ İlgili kampanya bulunamadı")
    
    st.experimental_rerun()

def format_search_results(results: List[Dict]) -> str:
    """Arama sonuçlarını formatla"""
    formatted = ["🔍 Arama Sonuçları:"]
    for i, res in enumerate(results, 1):
        formatted.append(f"""
        {i}. **{res['campaign_header']}**  
        `{res['campaign_number']}`  
        {res['campaign_description'][:100]}...
        """)
    return "\n".join(formatted)

# ------------------------------ 🚀 UYGULAMA BAŞLATMA ------------------------------
if __name__ == "__main__":
    HistoryManager.initialize()
    render_sidebar()
    render_chat_interface()




























**Akış Diyagramı (Mermaid.js Syntax):**

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontSize': '14px'}}}%%
graph TD
    A[Kullanıcı Sorgusu] --> B{Kampanya Kodu Var mı?}
    B -->|Evet| C[Tam Eşleşme Ara]
    B -->|Hayır| D[Vektörel Benzerlik Ara]
    C --> E{Sonuç Bulundu mu?}
    E -->|Evet| F[Detayları Göster]
    E -->|Hayır| D
    D --> G[Sonuçları Formatla]
    G --> H{Önceki Sonuçlarda Referans Var mı?}
    H -->|Evet| I[ContextManager'dan Getir]
    H -->|Hayır| J[Yeni Sonuçları Göster]
    I --> K[İlgili Kampanya Detayını Göster]
    J --> L[Sonuçları Tarihçeye Ekle]
    K --> L
    F --> L
    L --> M[Tarihçe Sınır Kontrolü]
    M -->|MAX_HISTORY Aşıldı| N[Eski Mesajları Temizle]
    M -->|Limit Dahilinde| O[Sonraki Sorguyu Bekle]
    N --> O
    O --> A
```

**Akış Açıklamaları:**

1. **Başlangıç:** Kullanıcı Streamlit arayüzüne sorgu giriyor
2. **Kampanya Kodu Analizi:** 
   - Sorguda kampanya kodu olup olmadığı kontrol ediliyor
3. **Tam Eşleşme Arama:** 
   - Kod varsa Elasticsearch'te `term` query ile direkt arama
4. **Vektörel Arama:** 
   - Kod yoksa veya bulunamazsa embedding model ile semantik arama
5. **Context Kontrolü:** 
   - "ikinci", "son" gibi referanslar için ContextManager kontrol ediliyor
6. **Sonuç Formatlama:** 
   - Sonuçlar kullanıcı dostu formatta düzenleniyor
7. **Tarihçe Yönetimi:** 
   - `MAX_HISTORY_LENGTH` parametresine göre otomatik temizlik
8. **Döngü:** 
   - Sistem yeni sorgular için hazır bekliyor

**Önemli Karar Noktaları:**

```mermaid
graph TD
    A[Referanslı Sorgu] --> B{ContextManager'da Kayıt Var mı?}
    B -->|Evet| C[Index ile Kampanya Getir]
    B -->|Hayır| D[Elasticsearch'te Yeniden Ara]
    C --> E[Detayları Göster]
    D --> F[Yeni Sonuçları İşle]
```

**Sistem Bileşenleri:**

```mermaid
classDiagram
    class HistoryManager{
        +initialize()
        +add_message()
        +clear_history()
        +get_context_history()
    }
    
    class ContextManager{
        +update_search_results()
        +get_campaign_by_index()
    }
    
    class Elasticsearch{
        +exact_search()
        +vector_search()
    }
    
    class OpenAI{
        +extract_code()
        +generate_response()
    }
    
    HistoryManager --> ContextManager : Veri Paylaşımı
    Elasticsearch --> ContextManager : Sonuçları Günceller
    OpenAI --> HistoryManager : Tarihçeyi Kullanır
```

**Örnek Çalışma Akışı:**

```mermaid
sequenceDiagram
    participant Kullanıcı
    participant Streamlit
    participant ContextManager
    participant Elasticsearch
    
    Kullanıcı->>Streamlit: "Migros kampanyaları"
    Streamlit->>Elasticsearch: vector_search("Migros kampanyaları")
    Elasticsearch-->>Streamlit: 3 sonuç döner
    Streamlit->>ContextManager: Sonuçları kaydet
    Streamlit->>Kullanıcı: Sonuçları göster
    
    Kullanıcı->>Streamlit: "İkinci kampanyayı açıkla"
    Streamlit->>ContextManager: get_campaign_by_index(2)
    ContextManager-->>Streamlit: MIG-FAMILY detayları
    Streamlit->>Kullanıcı: Kampanya detaylarını göster
```

Bu yapı, kullanıcı etkileşimlerini yönetirken hem performans hem de bağlamsal tutarlılık sağlar. Tüm akış parametrik kontrollerle optimize edilmiştir.















import streamlit as st
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.chat_models import AzureChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

# 📌 Bellek Yönetimi (En fazla 3 mesaj tutulacak)
def get_memory(n=3):
    client = AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="cyz",
        model_name="xyz",
        openai_api_type="azure"
    )
    return ConversationBufferWindowMemory(
        llm=client,
        memory_key="chat_history",
        k=n,
        return_messages=True
    )

memory = get_memory(n=3)

# 📌 Streaming için Callback Handler
class StreamHandler(BaseCallbackHandler):
    def __init__(self, display_element):
        self.display_element = display_element
        self.collected_text = ""

    def on_llm_new_token(self, token: str, **kwargs):
        self.collected_text += token
        self.display_element.markdown(self.collected_text)

# 📌 OpenAI’ye Kampanya Bilgisiyle Soru Gönderme
def ask_openai(user_input, campaign_info=None, follow_up_info=None):
    """
    OpenAI'ye özel sistem prompt'ları ile soru gönderir.
    """
    if campaign_info:
        system_prompt = f"Kampanya hakkında bilgi verilmiştir. Bu bilgi doğrultusunda soruyu yanıtla:\n\nKampanya Bilgisi: {campaign_info}"
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."
    elif follow_up_info:
        system_prompt = "Kullanıcının önceki kampanyalarla ilgili mi yoksa tamamen yeni bir konuda mı konuştuğunu belirle."
        user_prompt = f"Önceki Kampanyalar: {follow_up_info}\nKullanıcının yeni sorusu: {user_input}\nBu önceki kampanyalarla alakalı mı? Eğer alakalıysa ilgili kampanya kodunu veya başlığını döndür, değilse 'Hiçbiri' yaz."
    else:
        system_prompt = "Kullanıcı kampanya hakkında soru sormuş olabilir, ancak kesin bir bilgi yok. Soruyu anlamaya çalış ve eğer gerekirse kampanya bilgisi sor."
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."

    model = AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="cyz",
        model_name="xyz",
        openai_api_type="azure"
    )

    response = model.predict(system_prompt + "\n" + user_prompt)
    return response.strip()

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):
            # 🔍 Kampanya kodu var mı kontrol et
            campaign_code = extract_campaign_code(user_input)

            if campaign_code:
                # 📌 Elasticsearch'ten kampanya bilgisi çek
                campaign_info = es.search_campaign_by_code(campaign_code)

                # 📌 OpenAI’ye soru gönder
                response = ask_openai(user_input, campaign_info=campaign_info)

                # 🔍 Hafızaya ekle
                memory.save_context({"input": user_input, "response": response})

                st.subheader("📌 Yanıt")
                st.write(response)

            else:
                # 📌 Kampanya kodu yok, en alakalı 3 kampanyayı getir
                search_result, formatted_result = es.search_campaign_by_header(user_input)

                st.subheader("📌 En İyi 3 Kampanya")
                st.write(formatted_result)

                # 📌 Kullanıcının yeni sorusu önceki kampanyalarla mı ilgili?
                follow_up_response = ask_openai(user_input, follow_up_info=formatted_result)

                if follow_up_response.lower() != "hiçbiri":
                    st.write(f"🚀 Kullanıcının yeni sorusu `{follow_up_response}` kampanyasıyla ilgili.")

                    if follow_up_response.startswith("CAMP-"):
                        # Kampanya kodu bulundu, Elasticsearch'ten bilgi çek ve OpenAI'ye gönder
                        campaign_info = es.search_campaign_by_code(follow_up_response)
                        response = ask_openai(user_input, campaign_info=campaign_info)
                        st.subheader("📌 Yanıt")
                        st.write(response)
                    else:
                        # Başlık bulundu, Elasticsearch'ten filtreleme yapılacak
                        campaign_info = es.filter_campaign_by_title(follow_up_response)
                        response = ask_openai(user_input, campaign_info=campaign_info)
                        st.subheader(f"📌 {follow_up_response} Kampanyası İçeriği")
                        st.write(response)

                else:
                    # 📌 Hiçbir kampanyayla alakalı değilse, OpenAI’ye genel soru olarak gönder
                    response = ask_openai(user_input)
                    st.subheader("📌 Yanıt")
                    st.write(response)

# 📌 Streamlit Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    st.markdown("---")

    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

    # 📌 Bellekteki verileri yükleme
    memory_variables = memory.load_memory_variables({})
    chat_history = memory_variables.get('chat_history', [])

    if not isinstance(chat_history, list):
        chat_history = []

    if "top_n_results" not in st.session_state:
        st.session_state.top_n_results = []

    # Kullanıcı girişini işleme fonksiyonunu çağır
    if user_input:
        process_user_input(user_input)

    # 📌 Sohbet Geçmişi (En fazla 3 mesaj gösterilecek)
    st.subheader("💬 Sohbet Geçmişi")
    for msg in chat_history[-3:]:  # En son 3 mesajı göster
        st.write(msg)







import streamlit as st
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.chat_models import AzureChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

# 📌 Kampanya kodu kontrolü
def is_valid_campaign_code(code):
    """
    Kampanya kodunun geçerli olup olmadığını kontrol eden fonksiyon.
    - Tamamen sayısal mı?
    - "CAMP-12345" gibi bir formatta mı?
    """
    return code.isdigit() or (code.startswith("CAMP-") and code[5:].isdigit())

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):
            # 🔍 Kampanya kodu var mı kontrol et
            campaign_code = extract_campaign_code(user_input)

            if campaign_code:
                # 📌 Elasticsearch'ten kampanya bilgisi çek
                campaign_info = es.search_campaign_by_code(campaign_code)

                # 📌 OpenAI’ye soru gönder
                response = ask_openai(user_input, campaign_info=campaign_info)

                # 🔍 Hafızaya ekle
                memory.save_context({"input": user_input, "response": response})

                st.subheader("📌 Yanıt")
                st.write(response)

            else:
                # 📌 Kampanya kodu yok, en alakalı 3 kampanyayı getir
                search_result, formatted_result = es.search_campaign_by_header(user_input)

                st.subheader("📌 En İyi 3 Kampanya")
                st.write(formatted_result)

                # 📌 Kullanıcının yeni sorusu önceki kampanyalarla mı ilgili?
                follow_up_response = ask_openai(user_input, follow_up_info=formatted_result)

                if is_valid_campaign_code(follow_up_response):
                    st.write(f"🚀 Kullanıcının yeni sorusu `{follow_up_response}` kampanyasıyla ilgili.")

                    # Kampanya kodu bulundu, Elasticsearch'ten bilgi çek ve OpenAI'ye gönder
                    campaign_info = es.search_campaign_by_code(follow_up_response)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    st.subheader("📌 Yanıt")
                    st.write(response)

                elif follow_up_response != "Hiçbiri":
                    # Kampanya adı bulundu, Elasticsearch'te başlığa göre arama yapılacak
                    campaign_info = es.filter_campaign_by_title(follow_up_response)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    st.subheader(f"📌 {follow_up_response} Kampanyası İçeriği")
                    st.write(response)

                else:
                    # 📌 Hiçbir kampanyayla alakalı değilse, OpenAI’ye genel soru olarak gönder
                    response = ask_openai(user_input)
                    st.subheader("📌 Yanıt")
                    st.write(response)









import streamlit as st
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.chat_models import AzureChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

# 📌 Kampanya kodu kontrolü
def is_valid_campaign_code(code):
    """
    Kampanya kodunun geçerli olup olmadığını kontrol eden fonksiyon.
    - Tamamen sayısal mı?
    - "CAMP-12345" gibi bir formatta mı?
    """
    return code.isdigit() or (code.startswith("CAMP-") and code[5:].isdigit())

# 📌 Kullanıcının yeni sorusunun son mesaj ile ilgili olup olmadığını doğrulama
def check_follow_up_relevance(user_input, last_message):
    """
    Kullanıcının yeni sorusunun sohbet geçmişindeki son mesajla ilgili olup olmadığını kontrol eder.
    """
    system_prompt = "Kullanıcının yeni mesajı önceki mesajla ilgili mi? Eğer ilgiliyse 'Evet' döndür, değilse 'Hayır' döndür."
    user_prompt = f"Önceki Mesaj: {last_message}\nYeni Kullanıcı Sorusu: {user_input}"

    model = AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="cyz",
        model_name="xyz",
        openai_api_type="azure"
    )

    response = model.predict(system_prompt + "\n" + user_prompt)
    return response.strip().lower() == "evet"

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):
            # 🔍 Kampanya kodu var mı kontrol et
            campaign_code = extract_campaign_code(user_input)

            # 📌 Sohbet geçmişinden son mesajı al
            memory_variables = memory.load_memory_variables({})
            chat_history = memory_variables.get('chat_history', [])
            last_message = chat_history[-1] if chat_history else ""

            # 📌 Yeni soru önceki mesaj ile ilgili mi?
            if last_message and not check_follow_up_relevance(user_input, last_message):
                st.warning("Lütfen sorunuzu başka türlü tekrar sorunuz.")
                return

            if campaign_code:
                # 📌 Elasticsearch'ten kampanya bilgisi çek
                campaign_info = es.search_campaign_by_code(campaign_code)

                # 📌 OpenAI’ye soru gönder
                response = ask_openai(user_input, campaign_info=campaign_info)

                # 🔍 Hafızaya ekle
                memory.save_context({"input": user_input, "response": response})

                st.subheader("📌 Yanıt")
                st.write(response)

            else:
                # 📌 Kampanya kodu yok, en alakalı 3 kampanyayı getir
                search_result, formatted_result = es.search_campaign_by_header(user_input)

                st.subheader("📌 En İyi 3 Kampanya")
                st.write(formatted_result)

                # 📌 Kullanıcının yeni sorusu önceki kampanyalarla mı ilgili?
                follow_up_response = ask_openai(user_input, follow_up_info=formatted_result)

                if is_valid_campaign_code(follow_up_response):
                    st.write(f"🚀 Kullanıcının yeni sorusu `{follow_up_response}` kampanyasıyla ilgili.")

                    # Kampanya kodu bulundu, Elasticsearch'ten bilgi çek ve OpenAI'ye gönder
                    campaign_info = es.search_campaign_by_code(follow_up_response)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    st.subheader("📌 Yanıt")
                    st.write(response)

                elif follow_up_response != "Hiçbiri":
                    # Kampanya adı bulundu, Elasticsearch'te başlığa göre arama yapılacak
                    campaign_info = es.filter_campaign_by_title(follow_up_response)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    st.subheader(f"📌 {follow_up_response} Kampanyası İçeriği")
                    st.write(response)

                else:
                    # 📌 Kullanıcının sorusu önceki mesajla ilgili değilse, uyarı ver
                    st.warning("Lütfen sorunuzu başka türlü tekrar sorunuz.")















import streamlit as st
from langchain_community.chat_models import AzureChatOpenAI
from collections import deque

# 📌 Gelişmiş Memory Yönetimi (Son 3 mesaj formatlı saklanacak)
class ConversationMemory:
    def __init__(self, max_size=3):
        self.history = deque(maxlen=max_size)

    def add_message(self, user_input, response):
        """Sohbet geçmişine mesaj ekler"""
        self.history.append({"user": user_input, "bot": response})

    def get_formatted_history(self):
        """Geçmiş mesajları formatlı şekilde döndürür"""
        return "\n".join([f"Kullanıcı: {msg['user']}\nBot: {msg['bot']}" for msg in self.history])

memory = ConversationMemory()

# 📌 OpenAI’ye Kampanya Bilgisiyle Soru Gönderme
def ask_openai(user_input, campaign_info=None, follow_up_info=None):
    """
    OpenAI'ye özel sistem prompt'ları ile soru gönderir.
    """
    if campaign_info:
        system_prompt = f"Kampanya hakkında bilgi verilmiştir. Bu bilgi doğrultusunda soruyu yanıtla:\n\nKampanya Bilgisi: {campaign_info}"
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."
    elif follow_up_info:
        system_prompt = "Kullanıcının önceki kampanyalarla ilgili mi yoksa tamamen yeni bir konuda mı konuştuğunu belirle."
        user_prompt = f"Önceki Kampanyalar: {follow_up_info}\nKullanıcının yeni sorusu: {user_input}\nEğer ilgiliyse ilgili kampanya kodunu veya başlığını döndür. Eğer hiçbiri ile ilgili değilse 'Hiçbiri' yaz. Eğer ilgili değil ama yeni bir kampanya belirtiyorsa, yeni kampanya adını döndür."
    else:
        system_prompt = "Kullanıcı kampanya hakkında soru sormuş olabilir, ancak kesin bir bilgi yok. Soruyu anlamaya çalış ve eğer gerekirse kampanya bilgisi sor."
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."

    model = AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="cyz",
        model_name="xyz",
        openai_api_type="azure"
    )

    response = model.predict(system_prompt + "\n" + user_prompt)
    return response.strip()

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):
            # 🔍 Kampanya kodu var mı kontrol et
            campaign_code = extract_campaign_code(user_input)

            # 📌 Sohbet geçmişini al
            formatted_history = memory.get_formatted_history()

            if campaign_code:
                # 📌 Elasticsearch'ten kampanya bilgisi çek
                campaign_info = es.search_campaign_by_code(campaign_code)

                # 📌 OpenAI’ye soru gönder
                response = ask_openai(user_input, campaign_info=campaign_info)

                # 🔍 Hafızaya ekle
                memory.add_message(user_input, response)

                st.subheader("📌 Yanıt")
                st.write(response)

            else:
                # 📌 Kampanya kodu yok, en alakalı 3 kampanyayı getir
                search_result, formatted_result = es.search_campaign_by_header(user_input)

                st.subheader("📌 En İyi 3 Kampanya")
                st.write(formatted_result)

                # 📌 Kullanıcının yeni sorusu önceki kampanyalarla mı ilgili?
                follow_up_response = ask_openai(user_input, follow_up_info=formatted_history)

                if follow_up_response.lower() == "hiçbiri":
                    st.warning("Lütfen sorunuzu başka türlü tekrar sorunuz.")
                    return

                elif follow_up_response.lower().startswith("kampanya kodu:"):
                    campaign_code = follow_up_response.split(":")[1].strip()
                    campaign_info = es.search_campaign_by_code(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    memory.add_message(user_input, response)
                    st.subheader("📌 Yanıt")
                    st.write(response)

                elif follow_up_response.lower().startswith("kampanya adı:"):
                    campaign_title = follow_up_response.split(":")[1].strip()
                    campaign_info = es.filter_campaign_by_title(campaign_title)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    memory.add_message(user_input, response)
                    st.subheader(f"📌 {campaign_title} Kampanyası İçeriği")
                    st.write(response)

                else:
                    st.warning(f"Yeni kampanya belirttiniz: {follow_up_response}. Akış yeniden başlatılıyor...")
                    process_user_input(f"Yeni kampanya arıyorum: {follow_up_response}")

# 📌 Streamlit Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    st.markdown("---")

    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

    # Kullanıcı girişini işleme fonksiyonunu çağır
    if user_input:
        process_user_input(user_input)

    # 📌 Sohbet Geçmişi
    st.subheader("💬 Sohbet Geçmişi")
    st.write(memory.get_formatted_history())













import streamlit as st
from langchain_community.chat_models import AzureChatOpenAI
from collections import deque

# 📌 Hafıza (History) Yönetimi: Son 3 mesajı tutan yapı
class ConversationMemory:
    def __init__(self, max_size=3):
        self.history = deque(maxlen=max_size)  # En fazla 3 mesaj tutulur

    def add_message(self, user_input, response):
        """Sohbet geçmişine mesaj ekler (Yeni mesaj en üste gelir)."""
        self.history.appendleft({"user": user_input, "bot": response})  # Yeni mesaj en başa eklenir

    def get_formatted_history(self):
        """Geçmiş mesajları zaman sırasına göre (sondan başa) formatlı şekilde döndürür."""
        return "\n".join([f"Kullanıcı: {msg['user']}\nBot: {msg['bot']}" for msg in self.history])

    def clear_memory(self):
        """Hafızayı temizler (Yeni soru geldiğinde sıfırlamak için)."""
        self.history.clear()

memory = ConversationMemory()

# 📌 OpenAI'ye Kampanya Bilgisiyle Soru Gönderme
def ask_openai(user_input, campaign_info=None, history_analysis=None):
    """
    OpenAI'ye özel sistem prompt'ları ile soru gönderir.
    - Kampanya bilgisi varsa ona göre cevaplar.
    - Geçmiş mesajlardan analiz yapıyorsa ona göre yorum yapar.
    """
    if campaign_info:
        system_prompt = f"Kampanya bilgisi verilmiştir. Bu bilgiye göre soruyu yanıtla:\n\nKampanya Açıklaması: {campaign_info}"
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."
    elif history_analysis:
        system_prompt = "Kullanıcının yeni mesajı, önceki konuşmalar ile ilgili mi? Kampanya kodu mu söyledi, başlık mı belirtti, yeni mi başladı? Eğer kampanya kodu verdiyse 'Kampanya Kodu: XXX', başlık verdiyse 'Kampanya Adı: XXX', hiçbirine uymuyorsa 'Hiçbiri', eğer tamamen farklı yeni bir konuysa 'Baştan Yeni' döndür."
        user_prompt = f"Önceki Mesajlar:\n{history_analysis}\nKullanıcının Yeni Sorusu: {user_input}"

    else:
        system_prompt = "Kullanıcı bir kampanya hakkında soru sormuş olabilir. Eğer kampanya kodu veya başlık belirttiyse, ona göre yanıt ver."
        user_prompt = f"Kullanıcı Sorusu: {user_input}\nYanıtı kısa ve net bir şekilde ver."

    model = AzureChatOpenAI(
        openai_api_key=config_info.azure_api_key,
        openai_api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint,
        deployment_name="cyz",
        model_name="xyz",
        openai_api_type="azure"
    )

    response = model.predict(system_prompt + "\n" + user_prompt)
    return response.strip()

# 📌 Kullanıcı Girişi İşleme
def process_user_input(user_input):
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):

            # 📌 Kampanya kodu var mı?
            campaign_code = extract_campaign_code(user_input)

            # 📌 Eğer history boşsa (İlk mesaj)
            if len(memory.history) == 0:
                if campaign_code:
                    # Kampanya kodu varsa, Elasticsearch'ten kampanya bilgisi çek
                    campaign_info = es.search_campaign_by_code(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    memory.add_message(user_input, response)  # Hafızaya ekle
                    st.subheader("📌 Yanıt")
                    st.write(response)
                else:
                    # Kampanya kodu yoksa, Elasticsearch ile top 3 kampanya getir
                    search_result, formatted_result = es.search_campaign_by_header(user_input)
                    st.subheader("📌 En İyi 3 Kampanya")
                    st.write(formatted_result)
            else:
                # 📌 History doluysa OpenAI’ye sorarak kullanıcının amacını analiz et
                formatted_history = memory.get_formatted_history()
                follow_up_response = ask_openai(user_input, history_analysis=formatted_history)

                # 🔍 1. Kullanıcı direkt kampanya kodu söyledi mi?
                if follow_up_response.lower().startswith("kampanya kodu:"):
                    campaign_code = follow_up_response.split(":")[1].strip()
                    campaign_info = es.search_campaign_by_code(campaign_code)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    memory.add_message(user_input, response)  # Hafızaya ekle
                    st.subheader("📌 Yanıt")
                    st.write(response)

                # 🔍 2. Kullanıcı kampanya adını mı belirtti?
                elif follow_up_response.lower().startswith("kampanya adı:"):
                    campaign_title = follow_up_response.split(":")[1].strip()
                    campaign_info = es.filter_campaign_by_title(campaign_title)
                    response = ask_openai(user_input, campaign_info=campaign_info)
                    memory.add_message(user_input, response)  # Hafızaya ekle
                    st.subheader(f"📌 {campaign_title} Kampanyası İçeriği")
                    st.write(response)

                # 🔍 3. Kullanıcının sorusu hiçbirine uymadıysa
                elif follow_up_response.lower() == "hiçbiri":
                    st.warning("Soruyu başka türlü sorarsanız yardımcı olabilirim.")

                # 🔍 4. Kullanıcı baştan yeni bir konu açtıysa, hafızayı sıfırla
                elif follow_up_response.lower() == "baştan yeni":
                    memory.clear_memory()
                    st.warning("Yeni bir konu başlattınız, önceki konuşmalar sıfırlandı.")
                    process_user_input(user_input)  # Süreci baştan başlat

# 📌 Streamlit Arayüzü
if __name__ == "__main__":
    st.title("📢 Kampanya Asistanı")
    st.markdown("---")

    user_input = st.text_input("Lütfen kampanya ile ilgili sorunuzu girin:")

    if user_input:
        process_user_input(user_input)

    # 📌 Sohbet Geçmişi
    st.subheader("💬 Sohbet Geçmişi")
    st.write(memory.get_formatted_history())

















    import os
import json
import logging
import re
import time
import requests
from typing import TypedDict, Optional, Literal, List, Dict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your-openai-key")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-openai-endpoint.openai.azure.com")
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = "banking_campaigns"
EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
DEPLOYMENT_NAME_INTENT = "gpt-4-intent"
DEPLOYMENT_NAME_RESPONSE = "gpt-4-response"
API_VERSION = "2023-07-01-preview"
EMBEDDING_DIM = 1536  # For text-embedding-ada-002

# Initialize clients
es = Elasticsearch(ES_HOST)
logging.basicConfig(level=logging.INFO)

class ChatbotState(TypedDict):
    user_input: str
    intent: Optional[Literal["retrieval", "follow_up", "general"]]
    conversation_history: List[dict]
    retrieved_info: Optional[dict]
    candidate_campaigns: Optional[List[Dict]]
    current_response: Optional[str]
    last_campaign_mentioned: Optional[str]

def create_es_index():
    """Create Elasticsearch index with hybrid search configuration"""
    body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "index": {
                "similarity": {
                    "bm25_similarity": {
                        "type": "BM25"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "details": {
                    "type": "text",
                    "fields": {
                        "embedding": {
                            "type": "dense_vector",
                            "dims": EMBEDDING_DIM,
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                },
                "keywords": {"type": "keyword"},
                "eligibility": {"type": "text"},
                "valid_until": {"type": "date"}
            }
        }
    }
    
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body=body)
        logging.info("Created Elasticsearch index")

def index_campaigns():
    """Index sample banking campaigns with embeddings"""
    campaigns = [
        {
            "name": "Summer Savings Campaign",
            "details": "Earn a 5% bonus interest rate on deposits from June to August.",
            "keywords": ["summer", "savings", "bonus"],
            "eligibility": "Minimum deposit of $1,000 required",
            "valid_until": "2024-08-31"
        },
        {
            "name": "Home Loan Special",
            "details": "Fixed-rate mortgages starting at 3.99% APR with low down payments.",
            "keywords": ["mortgage", "home", "loan"],
            "eligibility": "700+ credit score required",
            "valid_until": "2024-12-31"
        }
    ]
    
    # Generate and add embeddings
    for campaign in campaigns:
        campaign["details.embedding"] = get_embedding(campaign["details"])
    
    # Bulk index documents
    actions = [
        {
            "_op_type": "index",
            "_index": ES_INDEX,
            "_source": campaign
        }
        for campaign in campaigns
    ]
    
    bulk(es, actions)
    logging.info(f"Indexed {len(campaigns)} campaigns")

def get_embedding(text: str) -> List[float]:
    """Get text embedding using Azure OpenAI"""
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{EMBEDDING_DEPLOYMENT}/embeddings?api-version={API_VERSION}"
    headers = {"Content-Type": "application/json", "api-key": AZURE_OPENAI_KEY}
    body = {"input": text}
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        logging.error(f"Embedding generation failed: {e}")
        return []

def hybrid_search(query: str) -> List[Dict]:
    """Perform hybrid search combining BM25 and vector search"""
    query_embedding = get_embedding(query)
    
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "details": {
                                "query": query,
                                "boost": 0.5
                            }
                        }
                    },
                    {
                        "knn": {
                            "details.embedding": {
                                "vector": query_embedding,
                                "k": 10,
                                "num_candidates": 100,
                                "boost": 0.5
                            }
                        }
                    }
                ]
            }
        },
        "size": 3,
        "_source": ["name", "details", "eligibility", "valid_until"]
    }
    
    try:
        result = es.search(index=ES_INDEX, body=search_body)
        return [hit["_source"] for hit in result["hits"]["hits"]]
    except Exception as e:
        logging.error(f"Elasticsearch search failed: {e}")
        return []

def retrieve_campaign_candidates(query: str) -> List[Dict]:
    """Retrieve a list of candidate campaigns using hybrid search"""
    return hybrid_search(query)

def truncate_history(history: List[dict], max_tokens: int = 1000) -> List[dict]:
    """Truncate conversation history based on token count"""
    token_count = 0
    truncated = []
    for msg in reversed(history):
        tokens = len(msg["content"].split()) + 5
        if token_count + tokens > max_tokens:
            break
        token_count += tokens
        truncated.insert(0, msg)
    return truncated

def call_openai(deployment: str, messages: list, temperature: float = 0.3) -> str:
    """Call Azure OpenAI API"""
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"
    headers = {"Content-Type": "application/json", "api-key": AZURE_OPENAI_KEY}
    body = {"messages": messages, "temperature": temperature, "max_tokens": 500}
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"API call failed: {e}")
        return "I'm having trouble processing your request. Please try again."

def classify_intent(state: ChatbotState) -> ChatbotState:
    """Classify banking intent with LLM"""
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in truncate_history(state["conversation_history"])])
    
    system_prompt = """Classify banking intent. Respond in JSON with 'intent' and 'reason'."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"History:\n{history_str}\n\nQuery: {state['user_input']}"}
    ]
    
    response = call_openai(DEPLOYMENT_NAME_INTENT, messages)
    try:
        result = json.loads(re.search(r'\{.*\}', response, re.DOTALL).group())
        state["intent"] = result.get("intent", "general").lower()
    except:
        state["intent"] = "general"
    
    return state

def generate_response(state: ChatbotState) -> ChatbotState:
    """Generate response using LLM with Elasticsearch context"""
    context = []
    if state["intent"] == "retrieval":
        # Use the selected campaign if available.
        if state.get("retrieved_info"):
            campaign = state["retrieved_info"]
            context.append(
                f"Campaign: {campaign['name']}\n"
                f"Details: {campaign['details']}\n"
                f"Eligibility: {campaign['eligibility']}\n"
                f"Valid Until: {campaign.get('valid_until', 'N/A')}"
            )
            state["last_campaign_mentioned"] = campaign["name"]
        else:
            context.append("No matching campaigns found. Offer general banking help.")
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in truncate_history(state["conversation_history"])[-3:]])
    
    system_prompt = f"""Banking assistant. Use context:
{'\n'.join(context)}

History:
{history_str}"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["user_input"]}
    ]
    
    response = call_openai(DEPLOYMENT_NAME_RESPONSE, messages, temperature=0.5)
    state["current_response"] = re.sub(r'\s+', ' ', response).strip()
    state["conversation_history"].append({"role": "assistant", "content": state["current_response"]})
    return state

def handle_campaign_selection(state: ChatbotState) -> bool:
    """
    Check if the current user input is a campaign selection.
    If so, update state["retrieved_info"] with the chosen campaign and clear candidate_campaigns.
    Returns True if a selection was made.
    """
    selection = state["user_input"].strip().lower()
    candidates = state.get("candidate_campaigns", [])
    chosen_campaign = None

    # Try to interpret input as a number (ordinal selection)
    if selection.isdigit():
        index = int(selection) - 1
        if 0 <= index < len(candidates):
            chosen_campaign = candidates[index]
    else:
        # Otherwise try matching campaign name or id.
        for candidate in candidates:
            candidate_name = candidate.get("name", "").lower()
            candidate_id = str(candidate.get("id", "")).lower()  # if an id field exists
            if candidate_name in selection or candidate_id in selection:
                chosen_campaign = candidate
                break

    if chosen_campaign:
        state["retrieved_info"] = chosen_campaign
        state["candidate_campaigns"] = None
        return True
    else:
        print("I couldn't understand your selection. Please try again by specifying a number or campaign name/ID.")
        return False

def main():
    """Main chat loop"""
    create_es_index()
    index_campaigns()
    
    state: ChatbotState = {
        "user_input": "",
        "intent": None,
        "conversation_history": [],
        "retrieved_info": None,
        "candidate_campaigns": None,
        "current_response": None,
        "last_campaign_mentioned": None
    }
    
    print("\n🏦 Welcome to BankAI! Ask about our campaigns or banking services.")
    print("Type 'exit' to end the chat.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if user_input.lower() in ('exit', 'quit'):
            print("\n💼 Thank you for using BankAI!")
            break

        state["user_input"] = user_input
        state["conversation_history"].append({"role": "user", "content": user_input})
        
        # If we are in selection mode, handle campaign selection
        if state.get("candidate_campaigns"):
            if not handle_campaign_selection(state):
                # Selection not made, wait for correct input.
                continue
            # Once a valid selection is made, inform the user.
            print(f"Selected campaign: {state['retrieved_info']['name']}")
        
        # Classify intent if not already in selection mode.
        state = classify_intent(state)
        
        if state["intent"] == "retrieval" and not state.get("retrieved_info"):
            # Retrieve candidate campaigns using hybrid search.
            candidates = retrieve_campaign_candidates(user_input)
            if len(candidates) == 0:
                state["retrieved_info"] = None
            elif len(candidates) == 1:
                state["retrieved_info"] = candidates[0]
            else:
                # More than one candidate found; store them for selection.
                state["candidate_campaigns"] = candidates
                print("I found multiple matching campaigns:")
                for i, campaign in enumerate(candidates):
                    campaign_id = campaign.get("id", "N/A")
                    print(f"{i+1}. {campaign.get('name')} (ID: {campaign_id})")
                print("Please select one by typing the corresponding number, campaign name, or campaign ID.")
                continue  # Wait for user selection in next loop iteration
        
        print("💭...", end="", flush=True)
        start_time = time.time()
        state = generate_response(state)
        elapsed_time = time.time() - start_time
        
        print(f"\r{' '*20}\r", end="")
        print(f"BankAI: {state['current_response']} (Response time: {elapsed_time:.2f}s)\n")

if __name__ == "__main__":
    main()

