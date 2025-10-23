# app.py

import streamlit as st
from config_loader import load_config_from_excel
from llm_handler import analyze_initial_complaint, extract_entity_from_answer

def initialize_session_state():
    """Oturum durumunu (session state) başlatır."""
    if "stage" not in st.session_state:
        # 'stage' (aşama), akışın nerede olduğunu yönetir:
        # 0. config_upload: Excel ve sütun adları bekleniyor
        # 1. initial_complaint: İlk şikayet bekleniyor
        # 2. follow_up: Eksik bilgiler için takip soruları soruluyor
        # 3. completed: Tüm bilgiler toplandı
        st.session_state.stage = "config_upload"
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "complaint_data" not in st.session_state:
        # Doldurulan JSON verisi burada tutulacak
        st.session_state.complaint_data = {}
        
    if "category" not in st.session_state:
        st.session_state.category = None
        
    if "questions_to_ask" not in st.session_state:
        # Sorulacak alan adlarının (key) listesi (kuyruk)
        st.session_state.questions_to_ask = []
        
    if "current_question_key" not in st.session_state:
        # O an sorduğumuz sorunun anahtarı (örn: "atm_lokasyonu")
        st.session_state.current_question_key = None
        
    if "config_data" not in st.session_state:
        # Excel'den yüklenen config sözlüğü burada tutulacak
        st.session_state.config_data = {}

def reset_application():
    """Uygulamayı başa sarmak için oturumu temizler."""
    st.session_state.clear()
    initialize_session_state()
    st.rerun()

def handle_initial_complaint(user_input):
    """
    (Pipeline Adım 1)
    Kullanıcının ilk şikayet metnini işler.
    """
    st.session_state.chat_history.append(("Kullanıcı", user_input))
    
    # Config'i session_state'den alıp LLM'e parametre olarak geç
    config_data = st.session_state.config_data

    # 1. LLM'i çağır (Kategorizasyon ve İlk Çıkarım)
    category, extracted_data = analyze_initial_complaint(user_input, config_data)

    st.session_state.category = category
    st.session_state.complaint_data = extracted_data

    # 2. Eksik alanları (değeri None olan) tespit et
    missing_fields = []
    if isinstance(extracted_data, dict):
        for field, value in extracted_data.items():
            if value is None:
                missing_fields.append(field)
    
    st.session_state.questions_to_ask = missing_fields

    # 3. Akışı bir sonraki aşamaya (takip soruları) taşı
    if not missing_fields:
        # Hiç eksik alan yoksa
        st.session_state.stage = "completed"
        st.session_state.chat_history.append(("Bot", "Anladım. Tüm gerekli bilgileri aldım."))
    else:
        # Sorulacak soru varsa, ilk soruyu ayarla
        st.session_state.current_question_key = st.session_state.questions_to_ask.pop(0) # Kuyruktan ilk soruyu çek
        st.session_state.stage = "follow_up"
        bot_message = f"Anladım. Şikayetinizin kategorisi: {category}. Size yardımcı olmak için birkaç sorum olacak."
        st.session_state.chat_history.append(("Bot", bot_message))

def handle_follow_up_answer(user_answer):
    """
    (Pipeline Adım 2)
    Kullanıcının takip sorusuna verdiği cevabı işler.
    """
    st.session_state.chat_history.append(("Kullanıcı", user_answer))

    # Config'i session_state'den al
    config_data = st.session_state.config_data

    current_key = st.session_state.current_question_key
    question_text = config_data[st.session_state.category]["questions"][current_key]

    # 1. LLM'i çağır (Sadece bu cevap için Veri Çıkarımı - Görev 2)
    extracted_value = extract_entity_from_answer(user_answer, current_key, question_text)

    if extracted_value:
        # 2. JSON verisini (session state'de) güncelle
        st.session_state.complaint_data[current_key] = extracted_value
        st.session_state.chat_history.append(("Bot", f"Not edildi: {current_key} = {extracted_value}"))
    else:
        # Eğer LLM çıkaramazsa, cevabı "Anlayamadım" olarak not et
        st.session_state.chat_history.append(("Bot", "Bu cevaptan net bir bilgi çıkaramadım, şimdilik not alıyorum."))
        st.session_state.complaint_data[current_key] = f"Anlaşılamadı (Orijinal cevap: {user_answer})"

    # 3. Sorulacak başka soru var mı kontrol et
    if st.session_state.questions_to_ask:
        # Bir sonraki soruyu ayarla
        st.session_state.current_question_key = st.session_state.questions_to_ask.pop(0)
    else:
        # Sorular bitti
        st.session_state.current_question_key = None
        st.session_state.stage = "completed"


# --- STREAMLIT UYGULAMA ARAYÜZÜ ---

st.set_page_config(layout="wide")
st.title("Parametrik Şikayet Chatbot Demosu (LLM + Streamlit)")

# Oturum durumunu başlat
initialize_session_state()

# --- Yan Taraf (Sidebar) ---
st.sidebar.title("Debug: Oturum Durumu")
st.sidebar.write(f"**Aşama (Stage):** `{st.session_state.stage}`")
st.sidebar.write(f"**Kategori:** `{st.session_state.category}`")

st.sidebar.subheader("Yüklenen Yapılandırma (Config)")
st.sidebar.json(st.session_state.config_data, expanded=False)

st.sidebar.subheader("Mevcut Veri (JSON)")
st.sidebar.json(st.session_state.complaint_data, expanded=True)

st.sidebar.subheader("Sorulacak Sorular (Kuyruk)")
st.sidebar.write(st.session_state.questions_to_ask)
st.sidebar.write(f"**Şu An Sorulan Soru:** `{st.session_state.current_question_key}`")

st.sidebar.divider()
st.sidebar.button("DEMOYU RESETLE", on_click=reset_application, use_container_width=True)


# --- ANA UYGULAMA AKIŞI ---

if st.session_state.stage == "config_upload":
    st.header("1. Adım: Yapılandırma Dosyasını Yükleyin")
    
    st.markdown("""
    Lütfen sistemin kullanacağı kategorileri, alanları ve soruları içeren bir Excel dosyası yükleyin.
    Excel dosyanızın "uzun formatta" olması gerekmektedir. Örnek yapı:
    
    | Kategori_Adi | Alan_Kodu | Sorusu | Kategori_Aciklamasi |
    | :--- | :--- | :--- | :--- |
    | ATM_SORUNU | atm_lokasyonu | Lokasyon nedir? | ATM Para Sıkışması vb. |
    | ATM_SORUNU | atm_problemi | Problem nedir? | ATM Para Sıkışması vb. |
    | KREDI_KARTI | kart_son_dort | Son 4 hane? | Kart sorunları |
    """)
    
    uploaded_file = st.file_uploader("Kategori/Alan/Soru listenizi içeren Excel dosyasını (.xlsx) yükleyin.", type="xlsx")
    
    st.subheader("Sütun Adı Eşleştirme")
    st.markdown("Lütfen Excel dosyanızdaki **gerçek** sütun adlarını girin.")
    
    col_map = {}
    col1, col2 = st.columns(2)
    with col1:
        col_map['category'] = st.text_input("Kategori adını içeren sütun:", "Kategori_Adi")
        col_map['field'] = st.text_input("Alan kodunu içeren sütun:", "Alan_Kodu")
    with col2:
        col_map['question'] = st.text_input("Soruyu içeren sütun:", "Sorusu")
        col_map['description'] = st.text_input("Kategori açıklamasını içeren sütun:", "Kategori_Aciklamasi")
    
    if uploaded_file is not None and st.button("Yapılandırmayı Yükle", use_container_width=True):
        with st.spinner("Yapılandırma dosyası işleniyor..."):
            config = load_config_from_excel(uploaded_file, col_map)
            
            if config:
                st.session_state.config_data = config
                st.session_state.stage = "initial_complaint" # Bir sonraki aşamaya geç
                st.success("Yapılandırma başarıyla yüklendi!")
                st.info("Chatbot şimdi hazır. Lütfen şikayetinizi girin.")
                st.rerun()

elif st.session_state.stage in ["initial_complaint", "follow_up", "completed"]:
    st.header("2. Adım: Şikayet Botu")

    # Chat geçmişini ekrana bas
    chat_container = st.container(height=500) # Kaydırılabilir sohbet alanı
    with chat_container:
        for author, text in st.session_state.chat_history:
            with st.chat_message(author):
                st.write(text)

    # Akışın (stage) durumuna göre arayüzü yönet
    if st.session_state.stage == "completed":
        st.success("Tüm bilgiler toplandı. Teşekkür ederiz! Sonuç JSON'u yandaki 'Mevcut Veri' kısmındadır.")

    elif st.session_state.stage == "follow_up":
        # Takip sorusunu sor
        config_data = st.session_state.config_data
        question_key = st.session_state.current_question_key
        
        # Olası bir hatayı önleme (config yüklenmeden bu aşamaya gelindiyse)
        if not config_data or st.session_state.category not in config_data:
            st.error("Yapılandırma hatası. Lütfen demoyu resetleyin.")
        else:
            question_to_ask = config_data[st.session_state.category]["questions"][question_key]
            
            # Botun sorusunu chat_message olarak ekle (eğer zaten eklenmediyse)
            if not st.session_state.chat_history or st.session_state.chat_history[-1] != ("Bot", question_to_ask):
                 st.session_state.chat_history.append(("Bot", question_to_ask))
                 with chat_container: # Yeni mesajı da container'a ekle
                     with st.chat_message("Bot"):
                         st.write(question_to_ask)

            # Cevap girişi
            user_follow_up = st.chat_input("Cevabınız...")
            if user_follow_up:
                handle_follow_up_answer(user_follow_up)
                st.rerun()

    elif st.session_state.stage == "initial_complaint":
        if not st.session_state.chat_history:
            st.session_state.chat_history.append(("Bot", "Merhaba, ben şikayet botunuz. Lütfen yaşadığınız sorunu kısaca özetler misiniz?"))
            with chat_container: # Mesajı container'a ekle
                 with st.chat_message("Bot"):
                     st.write("Merhaba, ben şikayet botunuz. Lütfen yaşadığınız sorunu kısaca özetler misiniz?")
                     
        user_initial_complaint = st.chat_input("Lütfen şikayetinizi buraya yazın...")
        if user_initial_complaint:
            handle_initial_complaint(user_initial_complaint)
            st.rerun()
