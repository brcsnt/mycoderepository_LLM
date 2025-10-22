"""
Ana işlem pipeline'ı
"""
from typing import Dict, Any, Optional, Tuple
from models import ConversationState, ExtractedData
from llm_service import LLMService
from excel_manager import ExcelManager
from categorization import CategorizationService
from field_extraction import FieldExtractionService
from question_handler import QuestionHandler

class ComplaintPipeline:
    def __init__(self):
        self.llm_service = LLMService()
        self.excel_manager = ExcelManager()
        self.categorization_service = CategorizationService(
            self.llm_service, self.excel_manager
        )
        self.field_extraction_service = FieldExtractionService(self.llm_service)
        self.question_handler = QuestionHandler()
    
    def start_new_complaint(self, complaint_text: str) -> Tuple[ConversationState, str]:
        """
        Yeni şikayet işlemini başlat
        
        Args:
            complaint_text: Şikayet metni
        
        Returns:
            (ConversationState, ilk_mesaj)
        """
        print("\n" + "="*50)
        print("🚀 Yeni şikayet işlemi başlatılıyor...")
        print("="*50)
        
        # 1. Kategorizasyon
        print("\n📊 Adım 1: Kategorizasyon yapılıyor...")
        category_name = self.categorization_service.categorize_complaint(complaint_text)
        
        if not category_name:
            return None, "❌ Şikayetiniz kategorize edilemedi. Lütfen daha detaylı bilgi verin."
        
        category = self.excel_manager.get_category(category_name)
        if not category:
            return None, f"❌ '{category_name}' kategorisi bulunamadı."
        
        # 2. Alan çıkarma
        print("\n🔍 Adım 2: Mevcut bilgiler çıkarılıyor...")
        extracted_data = self.field_extraction_service.extract_fields(
            complaint_text, category
        )
        
        # 3. Eksik alanları belirleme
        print("\n📝 Adım 3: Eksik alanlar belirleniyor...")
        missing_fields = self.field_extraction_service.identify_missing_fields(
            extracted_data, category
        )
        
        # 4. ConversationState oluştur
        state = ConversationState(
            original_complaint=complaint_text,
            category=category_name,
            extracted_data=extracted_data.fields.copy(),
            pending_questions=missing_fields
        )
        
        # 5. İlk mesajı oluştur
        if missing_fields:
            first_message = f"✅ Şikayetiniz **{category_name}** kategorisine ayrıldı.\n\n"
            first_message += f"📝 Toplamda **{len(missing_fields)}** soru soracağım.\n\n"
            next_question = self.question_handler.get_next_question(state)
            first_message += next_question
        else:
            first_message = f"✅ Şikayetiniz **{category_name}** kategorisine ayrıldı.\n\n"
            first_message += "🎉 Tüm gerekli bilgiler mevcut!\n\n"
            first_message += self.question_handler.generate_completion_message(state)
            state.is_complete = True
        
        print("\n✅ Pipeline başarıyla tamamlandı!")
        print("="*50 + "\n")
        
        return state, first_message
    
    def process_user_answer(self, state: ConversationState,
                           user_answer: str) -> Tuple[ConversationState, str]:
        """
        Kullanıcı cevabını işle
        
        Args:
            state: Mevcut sohbet durumu
            user_answer: Kullanıcının cevabı
        
        Returns:
            (güncellenmiş_state, yanıt_mesajı)
        """
        current_field = state.get_current_question()
        
        if not current_field:
            return state, "⚠️ İşlenecek soru kalmadı."
        
        # Cevaptan değeri çıkar
        extracted_value = self.field_extraction_service.extract_answer_from_response(
            user_answer, current_field
        )
        
        # Cevabı kaydet ve sonraki soruya geç
        self.question_handler.process_answer(state, user_answer, extracted_value)
        
        # Sohbet bitti mi kontrol et
        if self.question_handler.is_conversation_complete(state):
            response_message = self.question_handler.generate_completion_message(state)
        else:
            next_question = self.question_handler.get_next_question(state)
            response_message = next_question
        
        return state, response_message
    
    def get_final_json(self, state: ConversationState) -> Dict[str, Any]:
        """
        Final JSON çıktısını oluştur
        
        Args:
            state: Tamamlanmış sohbet durumu
        
        Returns:
            JSON formatında veri
        """
        return {
            "sikayet_metni": state.original_complaint,
            "kategori": state.category,
            **state.extracted_data
        }
