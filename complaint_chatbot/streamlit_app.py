"""
Complaint Chatbot - Streamlit Arayüzü
Kullanıcı dostu şikayet toplama chatbot uygulaması
"""
import streamlit as st
import json
import sys
from pathlib import Path

# Proje root'unu path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from chatbot_pipeline import ConversationalChatbot
from config import Config


# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Şikayet Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .status-in-progress {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-completed {
        background-color: #d4edda;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Session state başlat"""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ConversationalChatbot()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_started" not in st.session_state:
        st.session_state.session_started = False


def display_message(role: str, content: str):
    """Mesaj göster"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>Siz:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>Bot:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)


def display_sidebar():
    """Sidebar bilgileri"""
    with st.sidebar:
        st.header("⚙️ Sistem Bilgileri")

        # Config bilgileri
        config_info = Config.info()

        st.subheader("LLM Ayarları")
        st.text(f"Provider: {config_info['llm_provider']}")
        st.text(f"Model: {config_info['llm_model']}")
        st.text(f"Temperature: {config_info['temperature']}")

        st.divider()

        # Kategori bilgileri
        if st.session_state.chatbot:
            st.subheader("Mevcut Kategoriler")
            categories = st.session_state.chatbot.get_available_categories()
            for cat in categories:
                st.text(f"• {cat}")

        st.divider()

        # Session bilgileri
        if st.session_state.chatbot.current_session:
            st.subheader("Oturum Bilgileri")

            session = st.session_state.chatbot.current_session
            st.text(f"ID: {session['session_id']}")
            st.text(f"Kategori: {session['kategori']}")
            st.text(f"Güven: {session['kategori_guveni']:.2f}")

            # İlerleme
            total_fields = len(session['extracted_data']) - 1  # -1 for sikayet_metni
            missing_fields = len(session['missing_fields'])
            filled_fields = total_fields - missing_fields

            st.progress(filled_fields / total_fields if total_fields > 0 else 0)
            st.text(f"Tamamlanma: {filled_fields}/{total_fields}")

        st.divider()

        # Debug mode
        if st.checkbox("Debug Mode"):
            st.subheader("Debug Info")
            if st.session_state.chatbot.current_session:
                st.json(st.session_state.chatbot.current_session)

        # Reset butonu
        if st.button("🔄 Oturumu Sıfırla"):
            st.session_state.chatbot.clear_conversation()
            st.session_state.messages = []
            st.session_state.session_started = False
            st.rerun()


def display_chat_interface():
    """Ana chat arayüzü"""
    st.markdown('<div class="main-header">🤖 Şikayet Chatbot</div>', unsafe_allow_html=True)

    # Hoşgeldin mesajı
    if not st.session_state.session_started:
        st.info("👋 Merhaba! Şikayetinizi yazarak başlayabilirsiniz.")

    # Mesaj geçmişini göster
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            display_message(msg["role"], msg["content"])

    # Input alanı
    st.divider()

    col1, col2 = st.columns([6, 1])

    with col1:
        user_input = st.text_input(
            "Mesajınız:",
            key="user_input",
            placeholder="Şikayetinizi veya cevabınızı buraya yazın...",
            label_visibility="collapsed"
        )

    with col2:
        send_button = st.button("Gönder", use_container_width=True, type="primary")

    # Mesaj gönderme
    if send_button and user_input:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Bot yanıtı al
        with st.spinner("Düşünüyorum..."):
            try:
                bot_response = st.session_state.chatbot.chat(user_input)

                # Bot mesajını ekle
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_response
                })

                st.session_state.session_started = True

            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")

        st.rerun()


def display_results_panel():
    """Sonuç paneli"""
    if st.session_state.chatbot.current_session:
        session = st.session_state.chatbot.current_session

        # Durum badge
        if len(session['missing_fields']) == 0:
            st.markdown('<span class="status-badge status-completed">✓ Tamamlandı</span>',
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="status-badge status-in-progress">⏳ Devam Ediyor ({len(session["missing_fields"])} soru kaldı)</span>',
                       unsafe_allow_html=True)

        st.divider()

        # Çıkarılan veriyi göster
        st.subheader("📊 Toplanan Bilgiler")

        extracted_data = session['extracted_data']

        # JSON formatında göster
        col1, col2 = st.columns(2)

        with col1:
            st.json(extracted_data)

        with col2:
            # Tablo formatında göster
            data_list = []
            for key, value in extracted_data.items():
                status = "✓" if value is not None else "✗"
                data_list.append({
                    "Alan": key,
                    "Değer": value if value is not None else "-",
                    "Durum": status
                })

            st.dataframe(data_list, use_container_width=True, hide_index=True)

        # Export butonu
        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 JSON İndir", use_container_width=True):
                json_str = json.dumps(extracted_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="İndir",
                    data=json_str,
                    file_name=f"sikayet_{session['session_id']}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📋 Özet Göster", use_container_width=True):
                summary = st.session_state.chatbot.get_session_summary()
                st.json(summary)

        with col3:
            if st.button("🔄 Yeni Şikayet", use_container_width=True):
                st.session_state.chatbot.clear_conversation()
                st.session_state.messages = []
                st.session_state.session_started = False
                st.rerun()


def main():
    """Ana uygulama"""
    initialize_session_state()

    # Sidebar
    display_sidebar()

    # Ana layout
    col1, col2 = st.columns([3, 2])

    with col1:
        display_chat_interface()

    with col2:
        st.subheader("📝 Anlık Durum")
        display_results_panel()


if __name__ == "__main__":
    try:
        # Config doğrula
        Config.validate()
        main()

    except ValueError as e:
        st.error(f"Yapılandırma hatası: {e}")
        st.info("""
        Lütfen aşağıdaki adımları takip edin:
        1. .env.example dosyasını .env olarak kopyalayın
        2. .env dosyasında API key'lerinizi tanımlayın
        3. data/create_template.py scriptini çalıştırın
        4. Uygulamayı yeniden başlatın
        """)

    except Exception as e:
        st.error(f"Beklenmeyen hata: {e}")
        import traceback
        st.code(traceback.format_exc())
