"""
Kullanıcıya soru sorma ve cevap işleme
"""
from typing import Optional
from models import ConversationState, CategoryField, ChatMessage

class QuestionHandler:
    def __init__(self):
        pass
    
    def get_next_question(self, state: ConversationState) -> Optional[str]:
        """
        Sonraki soruyu getir
        
        Args:
            state: Sohbet durumu
        
        Returns:
            Soru metni veya None
        """
        current_question = state.get_current_question()
        
        if current_question is None:
            return None
        
        # Soru sayısı ve kalan soru bilgisi ekle
        total_questions = len(state.pending_questions)
        current_index = state.current_question_index + 1
        
        question_text = f"**Soru {current_index}/{total_questions}:** {current_question.question}"
        
        return question_text
    
    def process_answer(self, state: ConversationState, answer: str,
                      extracted_value: any) -> bool:
        """
        Kullanıcı cevabını işle ve sonraki soruya geç
        
        Args:
            state: Sohbet durumu
            answer: Kullanıcı cevabı
            extracted_value: LLM'den çıkarılan değer
        
        Returns:
            True: Başarılı, False: Hata
        """
        current_question = state.get_current_question()
        
        if current_question is None:
            return False
        
        # Değeri kaydet
        state.extracted_data[current_question.field_name] = extracted_value
        
        # Sonraki soruya geç
        state.move_to_next_question()
        
        print(f"✅ Cevap kaydedildi: {current_question.field_name} = {extracted_value}")
        
        return True
    
    def is_conversation_complete(self, state: ConversationState) -> bool:
        """Sohbet tamamlandı mı?"""
        return state.is_complete
    
    def generate_completion_message(self, state: ConversationState) -> str:
        """Tamamlanma mesajı oluştur"""
        message = "✅ **Tüm bilgiler toplandı!**\n\n"
        message += "📋 **Toplanan Bilgiler:**\n"
        
        for field_name, value in state.extracted_data.items():
            message += f"- **{field_name}**: {value}\n"
        
        message += "\n💡 Şikayetiniz kaydedildi ve ilgili birimle paylaşılacak."
        
        return message
