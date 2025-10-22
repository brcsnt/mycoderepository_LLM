"""
Complaint Chatbot Pipeline
Tüm modülleri bir araya getiren ana pipeline
"""
from typing import Dict, List, Optional, Tuple
from modules import (
    LLMClient,
    DataManager,
    Categorizer,
    InformationExtractor,
    ResponseProcessor,
)
from config import Config
import json


class ComplaintChatbot:
    """Şikayet chatbot ana sınıfı"""

    def __init__(self):
        """Pipeline bileşenlerini başlat"""
        # Ortak client ve data manager
        self.llm_client = LLMClient()
        self.data_manager = DataManager()

        # Modüller
        self.categorizer = Categorizer(self.llm_client, self.data_manager)
        self.extractor = InformationExtractor(self.llm_client, self.data_manager)
        self.processor = ResponseProcessor(self.llm_client)

        # State management
        self.current_session = None

    def start_session(self, complaint_text: str) -> Dict:
        """
        Yeni bir şikayet oturumu başlat

        Args:
            complaint_text: Şikayet metni

        Returns:
            {
                "session_id": "...",
                "kategori": "ATM",
                "extracted_data": {...},
                "missing_fields": [...],
                "next_question": {...} veya None,
                "status": "in_progress" / "completed"
            }
        """
        # 1. Kategorize et
        category_result = self.categorizer.categorize(complaint_text)
        category = category_result["kategori"]

        # 2. Bilgi çıkar
        extracted_data = self.extractor.extract(complaint_text, category)

        # 3. Eksik alanları tespit et
        missing_fields = self.extractor.get_missing_fields(extracted_data)

        # 4. Oturum oluştur
        session = {
            "session_id": self._generate_session_id(),
            "kategori": category,
            "kategori_guveni": category_result.get("guven_skoru", 0.0),
            "original_complaint": complaint_text,
            "extracted_data": extracted_data,
            "missing_fields": missing_fields,
            "asked_questions": [],
            "question_index": 0,
        }

        self.current_session = session

        # 5. İlk soruyu belirle
        next_question = self._get_next_question()

        return {
            "session_id": session["session_id"],
            "kategori": category,
            "extracted_data": extracted_data,
            "missing_fields": missing_fields,
            "next_question": next_question,
            "status": "completed" if not next_question else "in_progress",
        }

    def process_answer(
        self, answer: str, session_id: Optional[str] = None
    ) -> Dict:
        """
        Kullanıcı yanıtını işle

        Args:
            answer: Kullanıcı yanıtı
            session_id: Oturum ID (opsiyonel)

        Returns:
            {
                "updated_data": {...},
                "next_question": {...} veya None,
                "status": "in_progress" / "completed",
                "remaining_questions": 2
            }
        """
        if not self.current_session:
            raise ValueError("Aktif oturum bulunamadı. Önce start_session çağırın.")

        # Mevcut soruyu al
        current_question = self._get_current_question()

        if not current_question:
            return {
                "updated_data": self.current_session["extracted_data"],
                "next_question": None,
                "status": "completed",
                "remaining_questions": 0,
            }

        field_name = current_question["field"]

        # 1. Yanıtı normalize et
        normalized_answer = self.processor.normalize(answer, field_name)

        # 2. Değeri güncelle
        self.current_session["extracted_data"][field_name] = normalized_answer

        # 3. Soruyu işaretle
        self.current_session["asked_questions"].append({
            "field": field_name,
            "question": current_question["question"],
            "raw_answer": answer,
            "normalized_answer": normalized_answer,
        })

        # 4. Eksik alanları güncelle
        self.current_session["missing_fields"] = self.extractor.get_missing_fields(
            self.current_session["extracted_data"]
        )

        # 5. Index'i artır
        self.current_session["question_index"] += 1

        # 6. Sonraki soruyu al
        next_question = self._get_next_question()

        return {
            "updated_data": self.current_session["extracted_data"],
            "next_question": next_question,
            "status": "completed" if not next_question else "in_progress",
            "remaining_questions": len(self.current_session["missing_fields"]),
        }

    def get_final_data(self) -> Dict:
        """
        Tamamlanmış veriyi al

        Returns:
            Final JSON data
        """
        if not self.current_session:
            raise ValueError("Aktif oturum bulunamadı.")

        return self.current_session["extracted_data"]

    def get_session_summary(self) -> Dict:
        """
        Oturum özetini al

        Returns:
            Oturum özeti
        """
        if not self.current_session:
            return {}

        validation = self.extractor.validate_extracted_data(
            self.current_session["extracted_data"],
            self.current_session["kategori"],
        )

        return {
            "session_id": self.current_session["session_id"],
            "kategori": self.current_session["kategori"],
            "original_complaint": self.current_session["original_complaint"],
            "total_questions_asked": len(self.current_session["asked_questions"]),
            "completion_rate": validation["completion_rate"],
            "status": "completed" if validation["valid"] else "incomplete",
            "final_data": self.current_session["extracted_data"],
        }

    def _get_next_question(self) -> Optional[Dict]:
        """Sonraki soruyu al"""
        missing_fields = self.current_session["missing_fields"]

        if not missing_fields or self.current_session["question_index"] >= len(
            missing_fields
        ):
            return None

        field_name = missing_fields[self.current_session["question_index"]]
        question_text = self.data_manager.get_field_question(
            self.current_session["kategori"], field_name
        )

        if not question_text:
            # Soru bulunamadı, bir sonrakine geç
            self.current_session["question_index"] += 1
            return self._get_next_question()

        return {
            "field": field_name,
            "question": question_text,
            "index": self.current_session["question_index"] + 1,
            "total": len(missing_fields),
        }

    def _get_current_question(self) -> Optional[Dict]:
        """Mevcut soruyu al"""
        missing_fields = self.current_session["missing_fields"]
        index = self.current_session["question_index"]

        if index >= len(missing_fields):
            return None

        field_name = missing_fields[index]
        question_text = self.data_manager.get_field_question(
            self.current_session["kategori"], field_name
        )

        return {
            "field": field_name,
            "question": question_text,
        }

    def _generate_session_id(self) -> str:
        """Benzersiz oturum ID oluştur"""
        import uuid
        return str(uuid.uuid4())[:8]

    def reset_session(self):
        """Oturumu sıfırla"""
        self.current_session = None

    def export_session_json(self, filepath: Optional[str] = None) -> str:
        """
        Oturum verisini JSON olarak dışa aktar

        Args:
            filepath: Kayıt yolu (opsiyonel)

        Returns:
            JSON string
        """
        if not self.current_session:
            raise ValueError("Aktif oturum bulunamadı.")

        data = self.get_final_data()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    def get_available_categories(self) -> List[str]:
        """Mevcut kategorileri döndür"""
        return self.data_manager.get_all_categories()


class ConversationalChatbot(ComplaintChatbot):
    """
    Konuşma tarzı chatbot (Streamlit için daha uygun)
    Mesaj geçmişini yönetir
    """

    def __init__(self):
        super().__init__()
        self.conversation_history = []

    def chat(self, user_message: str) -> str:
        """
        Kullanıcı mesajını işle ve yanıt döndür

        Args:
            user_message: Kullanıcı mesajı

        Returns:
            Bot yanıtı
        """
        # Kullanıcı mesajını kaydet
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        # Oturum yoksa başlat
        if not self.current_session:
            result = self.start_session(user_message)

            if result["status"] == "completed":
                response = f"Şikayetiniz kaydedildi. Kategori: {result['kategori']}"
            else:
                next_q = result["next_question"]
                response = f"Şikayetiniz alındı. Kategori: {result['kategori']}\n\n{next_q['question']}"

        else:
            # Yanıtı işle
            result = self.process_answer(user_message)

            if result["status"] == "completed":
                response = "Tüm bilgiler alındı. Teşekkür ederiz!"
            else:
                next_q = result["next_question"]
                response = next_q["question"]

        # Bot yanıtını kaydet
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
        })

        return response

    def get_conversation_history(self) -> List[Dict]:
        """Konuşma geçmişini döndür"""
        return self.conversation_history

    def clear_conversation(self):
        """Konuşmayı sıfırla"""
        self.conversation_history = []
        self.reset_session()


if __name__ == "__main__":
    # Test
    try:
        chatbot = ConversationalChatbot()

        print("=== Complaint Chatbot Test ===\n")

        # İlk şikayet
        response = chatbot.chat("Merhaba, ATM'den param sıkıştı")
        print(f"Bot: {response}\n")

        # Cevaplar
        response = chatbot.chat("Beykoz'daki ATM")
        print(f"Bot: {response}\n")

        response = chatbot.chat("200 TL sıkıştı")
        print(f"Bot: {response}\n")

        # Final data
        print("\n=== Final Data ===")
        final_data = chatbot.get_final_data()
        print(json.dumps(final_data, ensure_ascii=False, indent=2))

        # Özet
        print("\n=== Session Summary ===")
        summary = chatbot.get_session_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
