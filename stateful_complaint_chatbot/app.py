"""
Stateful Complaint Chatbot - Streamlit Ana Uygulama
LLM tabanlı, çok adımlı şikayet toplama sistemi
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import json
import time

# Kendi modüllerimizi import et
from config_manager import ConfigManager
from llm_handler import LLMHandler
from logger import ComplaintLogger
from utils import (
    generate_session_id,
    find_null_fields,
    format_data_for_display,
    format_json_pretty,
    calculate_completion_percentage,
    merge_data,
    create_qa_list_entry,
    estimate_time_remaining,
    UIConstants
)

# Environment variables yükle
load_dotenv()

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Şikayet Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS ile özelleştirme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .stage-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Session state'i başlat"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.stage = UIConstants.STAGE_INITIAL
        st.session_state.session_id = generate_session_id()
        st.session_state.start_time = time.time()

        # Veri alanları
        st.session_state.initial_complaint = ""
        st.session_state.category = None
        st.session_state.complaint_data = {}
        st.session_state.questions_to_ask = []
        st.session_state.current_field = None
        st.session_state.qa_history = []

        # Chat history
        st.session_state.messages = []


def initialize_components():
    """Config, LLM ve Logger bileşenlerini başlat"""
    if "components_loaded" not in st.session_state:
        try:
            # Config dosyası yolu
            config_path = os.getenv("CONFIG_FILE", "config_template.xlsx")

            # Sütun mapping (kullanıcı özelleştirebilir)
            column_mapping = {
                "kategori": os.getenv("COL_CATEGORY", "Kategori"),
                "alan": os.getenv("COL_FIELD", "Alan"),
                "soru": os.getenv("COL_QUESTION", "Soru"),
                "zorunlu": os.getenv("COL_REQUIRED", "Zorunlu")
            }

            # Config Manager
            st.session_state.config_manager = ConfigManager(
                excel_path=config_path,
                column_mapping=column_mapping
            )

            # LLM Handler
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("❌ GEMINI_API_KEY environment variable tanımlı değil!")
                st.stop()

            model_name = os.getenv("MODEL_NAME", "gemini-3-27b")
            st.session_state.llm_handler = LLMHandler(api_key=api_key, model_name=model_name)

            # Logger
            log_file = os.getenv("LOG_FILE", "logs.xlsx")
            st.session_state.logger = ComplaintLogger(log_file_path=log_file)

            st.session_state.components_loaded = True

        except Exception as e:
            st.error(f"❌ Bileşenler yüklenirken hata: {str(e)}")
            st.stop()


def handle_initial_complaint(complaint_text: str):
    """
    İlk şikayet metnini işle:
    1. Kategorize et
    2. Mevcut verileri çıkar
    3. Null alanları tespit et
    4. Follow-up aşamasına geç
    """
    try:
        with st.spinner("🔍 Şikayetiniz analiz ediliyor..."):
            # LLM ile kategorize et ve veri çıkar
            category, initial_data = st.session_state.llm_handler.categorize_and_extract(
                complaint_text,
                st.session_state.config_manager.categories
            )

            # Session state'e kaydet
            st.session_state.category = category
            st.session_state.complaint_data = initial_data
            st.session_state.initial_complaint = complaint_text

            # Null alanları bul
            null_fields = find_null_fields(initial_data)

            # Sorulacak soruları hazırla (sadece zorunlu alanlar veya tüm null alanlar)
            questions_to_ask = []
            for field in null_fields:
                # Config'den soruyu al
                question = st.session_state.config_manager.get_question_for_field(category, field)
                if question:
                    questions_to_ask.append({
                        "field": field,
                        "question": question
                    })

            st.session_state.questions_to_ask = questions_to_ask

            # Mesaj ekle
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Şikayetiniz **{category}** kategorisine ayrıldı.\n\n"
                          f"**Tespit Edilen Bilgiler:**\n{format_data_for_display(initial_data)}"
            })

            # Sorulacak soru varsa follow-up aşamasına geç
            if questions_to_ask:
                st.session_state.stage = UIConstants.STAGE_FOLLOW_UP
                st.session_state.current_field = questions_to_ask[0]["field"]

                remaining = len(questions_to_ask)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"📝 Eksik bilgileri tamamlamak için {remaining} soru soracağım. "
                              f"Tahmini süre: {estimate_time_remaining(remaining)}\n\n"
                              f"**Soru 1/{remaining}:** {questions_to_ask[0]['question']}"
                })
            else:
                # Tüm bilgiler mevcut, tamamlandı
                st.session_state.stage = UIConstants.STAGE_COMPLETED
                finalize_complaint()

    except Exception as e:
        st.error(f"❌ Hata: {str(e)}")


def handle_follow_up_answer(answer: str):
    """
    Takip sorusuna verilen cevabı işle:
    1. LLM ile veriyi çıkar
    2. Complaint data'yı güncelle
    3. QA history'ye ekle
    4. Sonraki soruya geç veya tamamla
    """
    try:
        current_q = st.session_state.questions_to_ask[0]
        field_name = current_q["field"]
        question = current_q["question"]

        with st.spinner("💭 Cevabınız işleniyor..."):
            # LLM ile veriyi çıkar
            extracted_value = st.session_state.llm_handler.extract_field_value(
                user_answer=answer,
                field_name=field_name,
                question=question,
                context=st.session_state.initial_complaint
            )

            # Complaint data'yı güncelle
            st.session_state.complaint_data[field_name] = extracted_value

            # QA history'ye ekle
            qa_entry = create_qa_list_entry(field_name, question, answer)
            st.session_state.qa_history.append(qa_entry)

            # İşlenmiş soruyu listeden çıkar
            st.session_state.questions_to_ask.pop(0)

            # Sonraki soru var mı?
            if st.session_state.questions_to_ask:
                next_q = st.session_state.questions_to_ask[0]
                st.session_state.current_field = next_q["field"]

                remaining = len(st.session_state.questions_to_ask)
                total = remaining + len(st.session_state.qa_history)
                current_num = len(st.session_state.qa_history) + 1

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ Teşekkürler!\n\n**Soru {current_num}/{total}:** {next_q['question']}"
                })
            else:
                # Tüm sorular bitti, finalize et
                st.session_state.stage = UIConstants.STAGE_COMPLETED
                finalize_complaint()

    except Exception as e:
        st.error(f"❌ Hata: {str(e)}")


def finalize_complaint():
    """Şikayeti finalize et ve logla"""
    try:
        with st.spinner("📊 Veriler son kez kontrol ediliyor..."):
            # Final validation ve refinement
            refined_data = st.session_state.llm_handler.validate_and_refine_data(
                st.session_state.complaint_data,
                st.session_state.initial_complaint
            )

            st.session_state.complaint_data = refined_data

            # Süreyi hesapla
            duration = time.time() - st.session_state.start_time

            # Logla
            st.session_state.logger.log_session(
                session_id=st.session_state.session_id,
                category=st.session_state.category,
                initial_complaint=st.session_state.initial_complaint,
                qa_list=st.session_state.qa_history,
                final_data=refined_data,
                completed=True,
                duration_seconds=duration
            )

            # Başarı mesajı
            completion_pct = calculate_completion_percentage(refined_data)

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"🎉 **Şikayetiniz başarıyla kaydedildi!**\n\n"
                          f"📊 **Veri Tamamlanma:** %{completion_pct:.0f}\n"
                          f"⏱️ **Toplam Süre:** {duration:.1f} saniye\n"
                          f"🆔 **Oturum ID:** {st.session_state.session_id}\n\n"
                          f"**Kaydedilen Bilgiler:**\n{format_data_for_display(refined_data)}"
            })

    except Exception as e:
        st.error(f"❌ Finalize hatası: {str(e)}")


def render_sidebar():
    """Sidebar içeriğini render et"""
    with st.sidebar:
        st.markdown("### ⚙️ Sistem Bilgileri")

        # Oturum bilgileri
        st.markdown(f"""
        **🆔 Oturum ID:** `{st.session_state.session_id}`
        **📍 Aşama:** `{st.session_state.stage}`
        **⏱️ Süre:** {time.time() - st.session_state.start_time:.0f}s
        """)

        # Kategori bilgisi
        if st.session_state.category:
            st.markdown(f"**📋 Kategori:** {st.session_state.category}")

        # Progress bar
        if st.session_state.complaint_data:
            completion = calculate_completion_percentage(st.session_state.complaint_data)
            st.progress(completion / 100)
            st.markdown(f"**Tamamlanma:** %{completion:.0f}")

        st.divider()

        # Mevcut veriler
        if st.session_state.complaint_data:
            st.markdown("### 📊 Toplanan Veriler")
            with st.expander("Detayları Göster"):
                st.json(st.session_state.complaint_data)

        st.divider()

        # Config bilgileri
        st.markdown("### 📚 Mevcut Kategoriler")
        categories = st.session_state.config_manager.get_categories()
        for cat in categories:
            st.markdown(f"- {cat}")

        st.divider()

        # Yeniden başlat butonu
        if st.button("🔄 Yeni Oturum Başlat"):
            # Session state'i temizle
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # Log istatistikleri
        st.divider()
        st.markdown("### 📈 Genel İstatistikler")
        if st.button("İstatistikleri Göster"):
            stats = st.session_state.logger.get_statistics()
            st.json(stats)


def render_chat_interface():
    """Ana chat arayüzünü render et"""

    # Header
    st.markdown('<div class="main-header">🤖 Şikayet Chatbot</div>', unsafe_allow_html=True)

    # Stage bilgisi
    stage_emoji = {
        UIConstants.STAGE_INITIAL: "📝",
        UIConstants.STAGE_FOLLOW_UP: "❓",
        UIConstants.STAGE_COMPLETED: "✅"
    }

    stage_text = {
        UIConstants.STAGE_INITIAL: "İlk Şikayet Bekleniyor",
        UIConstants.STAGE_FOLLOW_UP: "Takip Soruları",
        UIConstants.STAGE_COMPLETED: "Tamamlandı"
    }

    current_stage = st.session_state.stage
    st.markdown(f"""
    <div class="stage-info">
        <strong>{stage_emoji.get(current_stage, '📍')} Aşama:</strong> {stage_text.get(current_stage, current_stage)}
    </div>
    """, unsafe_allow_html=True)

    # Chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        with st.chat_message(role):
            st.markdown(content)

    # Chat input
    if current_stage == UIConstants.STAGE_INITIAL:
        # İlk şikayet bekleniyor
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.markdown("👋 Merhaba! Şikayetinizi dinlemek için buradayım.\n\n"
                          "📝 Lütfen şikayetinizi detaylı bir şekilde yazın:")

        user_input = st.chat_input("Şikayetinizi buraya yazın...")

        if user_input:
            # Kullanıcı mesajını ekle
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            # İşle
            handle_initial_complaint(user_input)
            st.rerun()

    elif current_stage == UIConstants.STAGE_FOLLOW_UP:
        # Takip soruları aşaması
        user_input = st.chat_input("Cevabınızı buraya yazın...")

        if user_input:
            # Kullanıcı cevabını ekle
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            # İşle
            handle_follow_up_answer(user_input)
            st.rerun()

    elif current_stage == UIConstants.STAGE_COMPLETED:
        # Tamamlandı
        st.success("✅ Oturum tamamlandı! Yeni bir oturum başlatmak için yan menüdeki butonu kullanın.")

        # JSON export butonu
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 JSON İndir"):
                json_str = format_json_pretty(st.session_state.complaint_data)
                st.download_button(
                    label="İndir",
                    data=json_str,
                    file_name=f"complaint_{st.session_state.session_id}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📋 Panoya Kopyala"):
                st.code(format_json_pretty(st.session_state.complaint_data), language="json")


def main():
    """Ana fonksiyon"""

    # Session state başlat
    initialize_session_state()

    # Bileşenleri başlat
    initialize_components()

    # Sidebar
    render_sidebar()

    # Ana chat arayüzü
    render_chat_interface()


if __name__ == "__main__":
    main()
