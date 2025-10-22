"""
Streamlit demo arayüzü
"""
import streamlit as st
import json
from pipeline import ComplaintPipeline
from models import ConversationState, ChatMessage
from config import Config

# Sayfa konfigürasyonu
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide"
)

# Session state başlatma
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = ComplaintPipeline()

if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

# Başlık
st.title("💬 Şikayet Yönetim Sistemi")
st.markdown("---")

# Sidebar - Bilgi paneli
with st.sidebar:
    st.header("ℹ️ Bilgilendirme")
    st.info("""
    **Nasıl Çalışır?**
    
    1. Şikayetinizi yazın
    2. Sistem otomatik kategorize edecek
    3. Eksik bilgiler için sorular soracak
    4. Tüm bilgiler toplandığında JSON formatında sonuç üretilecek
    """)
    
    st.markdown("---")
    
    st.header("📊 Durum")
    if st.session_state.conversation_state:
        state = st.session_state.conversation_state
        st.write(f"**Kategori:** {state.category or 'Belirleniyor...'}")
        st.write(f"**Toplanan Alan:** {len([v for v in state.extracted_data.values() if v is not None])}")
        st.write(f"**Eksik Alan:** {len(state.pending_questions) - state.current_question_index}")
        st.write(f"**Durum:** {'✅ Tamamlandı' if state.is_complete else '⏳ Devam ediyor'}")
    else:
        st.write("Henüz şikayet başlatılmadı.")
    
    st.markdown("---")
    
    if st.button("🔄 Yeni Şikayet", use_container_width=True):
        st.session_state.conversation_state = None
        st.session_state.messages = []
        st.rerun()

# Ana alan
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Sohbet")
    
    # Mesajları göster
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message.role):
                st.markdown(message.content)
    
    # Kullanıcı input
    if not st.session_state.processing:
        if st.session_state.conversation_state is None:
            # İlk şikayet metni
            user_input = st.chat_input("Şikayetinizi buraya yazın...")
            
            if user_input:
                st.session_state.processing = True
                
                # Kullanıcı mesajını ekle
                user_msg = ChatMessage(role="user", content=user_input)
                st.session_state.messages.append(user_msg)
                
                # Pipeline'ı başlat
                with st.spinner("İşleniyor..."):
                    state, response = st.session_state.pipeline.start_new_complaint(user_input)
                
                if state:
                    st.session_state.conversation_state = state
                    
                    # Bot yanıtını ekle
                    bot_msg = ChatMessage(role="assistant", content=response)
                    st.session_state.messages.append(bot_msg)
                else:
                    # Hata mesajı
                    bot_msg = ChatMessage(role="assistant", content=response)
                    st.session_state.messages.append(bot_msg)
                
                st.session_state.processing = False
                st.rerun()
        
        elif not st.session_state.conversation_state.is_complete:
            # Soruları cevaplandırma
            user_input = st.chat_input("Cevabınızı yazın...")
            
            if user_input:
                st.session_state.processing = True
                
                # Kullanıcı mesajını ekle
                user_msg = ChatMessage(role="user", content=user_input)
                st.session_state.messages.append(user_msg)
                
                # Cevabı işle
                with st.spinner("İşleniyor..."):
                    state, response = st.session_state.pipeline.process_user_answer(
                        st.session_state.conversation_state,
                        user_input
                    )
                
                st.session_state.conversation_state = state
                
                # Bot yanıtını ekle
                bot_msg = ChatMessage(role="assistant", content=response)
                st.session_state.messages.append(bot_msg)
                
                st.session_state.processing = False
                st.rerun()
        else:
            st.success("✅ Şikayet işlemi tamamlandı!")
            st.info("Yeni bir şikayet başlatmak için sol menüden 'Yeni Şikayet' butonuna tıklayın.")

with col2:
    st.header("📄 JSON Çıktısı")
    
    if st.session_state.conversation_state:
        if st.session_state.conversation_state.is_complete:
            # Final JSON'u göster
            final_json = st.session_state.pipeline.get_final_json(
                st.session_state.conversation_state
            )
            
            st.json(final_json)
            
            # Download butonu
            json_str = json.dumps(final_json, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON İndir",
                data=json_str,
                file_name="sikayet.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            # Şu anki durum
            st.info("Sohbet tamamlanınca JSON çıktısı burada görünecek.")
            
            current_data = {
                "sikayet_metni": st.session_state.conversation_state.original_complaint,
                "kategori": st.session_state.conversation_state.category,
                **st.session_state.conversation_state.extracted_data
            }
            
            with st.expander("Mevcut Veri"):
                st.json(current_data)
    else:
        st.info("Henüz şikayet başlatılmadı.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Şikayet Yönetim Sistemi v1.0 | Powered by LLM"
    "</div>",
    unsafe_allow_html=True
)
