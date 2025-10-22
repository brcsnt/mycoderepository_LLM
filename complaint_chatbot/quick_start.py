#!/usr/bin/env python3
"""
Quick Start Script
Hızlı test ve kurulum scripti
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from chatbot_pipeline import ConversationalChatbot
import json


def check_setup():
    """Kurulum kontrolü"""
    print("=" * 60)
    print("🔍 Kurulum Kontrolü")
    print("=" * 60)

    errors = []

    try:
        # Config kontrolü
        Config.validate()
        print("✓ Config doğrulandı")

        # LLM test
        from modules import LLMClient
        client = LLMClient()
        print("✓ LLM client başlatıldı")

        # Data manager test
        from modules import DataManager
        manager = DataManager()
        categories = manager.get_all_categories()
        print(f"✓ Data manager başlatıldı ({len(categories)} kategori)")

        print("\n✅ Tüm kontroller başarılı!")
        return True

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("\n📋 Kurulum Adımları:")
        print("1. .env.example dosyasını .env olarak kopyalayın")
        print("2. .env dosyasında API key'lerinizi tanımlayın")
        print("3. cd data && python create_template.py")
        print("4. pip install -r requirements.txt")
        return False


def run_demo():
    """Demo çalıştır"""
    print("\n" + "=" * 60)
    print("🤖 Chatbot Demo")
    print("=" * 60)

    try:
        chatbot = ConversationalChatbot()

        # Test senaryosu
        test_messages = [
            "Merhaba, ATM'den param sıkıştı",
            "Beykoz'daki ATM",
            "200 TL sıkıştı",
            "Dün akşam"
        ]

        print("\n📝 Test Senaryosu Başlıyor...\n")

        for i, message in enumerate(test_messages, 1):
            print(f"Kullanıcı #{i}: {message}")
            response = chatbot.chat(message)
            print(f"Bot: {response}\n")

            # Oturum bilgisi
            if chatbot.current_session:
                missing = len(chatbot.current_session['missing_fields'])
                if missing > 0:
                    print(f"[Kalan sorular: {missing}]\n")

        # Final veri
        print("=" * 60)
        print("📊 Final Veri:")
        print("=" * 60)
        final_data = chatbot.get_final_data()
        print(json.dumps(final_data, ensure_ascii=False, indent=2))

        # Özet
        print("\n" + "=" * 60)
        print("📈 Oturum Özeti:")
        print("=" * 60)
        summary = chatbot.get_session_summary()
        print(f"Kategori: {summary['kategori']}")
        print(f"Toplam Soru: {summary['total_questions_asked']}")
        print(f"Tamamlanma: {summary['completion_rate']:.1%}")
        print(f"Durum: {summary['status']}")

        print("\n✅ Demo tamamlandı!")

    except Exception as e:
        print(f"\n❌ Demo hatası: {e}")
        import traceback
        traceback.print_exc()


def interactive_mode():
    """Etkileşimli mod"""
    print("\n" + "=" * 60)
    print("💬 Etkileşimli Mod")
    print("=" * 60)
    print("Çıkmak için 'quit' yazın\n")

    try:
        chatbot = ConversationalChatbot()

        while True:
            user_input = input("Siz: ").strip()

            if user_input.lower() in ["quit", "exit", "çıkış"]:
                print("\nGörüşmek üzere!")
                break

            if not user_input:
                continue

            try:
                response = chatbot.chat(user_input)
                print(f"Bot: {response}\n")

                # Tamamlanma durumu
                if chatbot.current_session:
                    missing = len(chatbot.current_session['missing_fields'])
                    if missing == 0:
                        print("\n✅ Tüm bilgiler toplandı!")
                        print("\nFinal Veri:")
                        final_data = chatbot.get_final_data()
                        print(json.dumps(final_data, ensure_ascii=False, indent=2))

                        # Yeni oturum
                        choice = input("\nYeni şikayet girmek ister misiniz? (e/h): ").strip().lower()
                        if choice == 'e':
                            chatbot.clear_conversation()
                            print("\n🔄 Yeni oturum başlatıldı\n")
                        else:
                            break

            except Exception as e:
                print(f"❌ Hata: {e}\n")

    except KeyboardInterrupt:
        print("\n\nGörüşmek üzere!")


def main():
    """Ana fonksiyon"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          🤖 COMPLAINT CHATBOT - QUICK START 🤖            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Menü
    print("\nLütfen bir seçenek seçin:\n")
    print("1. Kurulum Kontrolü")
    print("2. Demo Çalıştır")
    print("3. Etkileşimli Mod")
    print("4. Streamlit Uygulamasını Başlat")
    print("5. Çıkış")

    choice = input("\nSeçiminiz (1-5): ").strip()

    if choice == "1":
        check_setup()

    elif choice == "2":
        if check_setup():
            run_demo()

    elif choice == "3":
        if check_setup():
            interactive_mode()

    elif choice == "4":
        print("\n🚀 Streamlit uygulaması başlatılıyor...")
        print("Tarayıcınızda http://localhost:8501 adresini açın\n")
        import subprocess
        subprocess.run(["streamlit", "run", "streamlit_app.py"])

    elif choice == "5":
        print("\nGörüşmek üzere!")

    else:
        print("\n❌ Geçersiz seçim!")


if __name__ == "__main__":
    main()
