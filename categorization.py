"""
Şikayet metni kategorizasyonu
"""
from typing import Optional
from llm_service import LLMService
from excel_manager import ExcelManager

class CategorizationService:
    def __init__(self, llm_service: LLMService, excel_manager: ExcelManager):
        self.llm = llm_service
        self.excel_manager = excel_manager
    
    def categorize_complaint(self, complaint_text: str) -> Optional[str]:
        """
        Şikayet metnini kategorize et
        
        Args:
            complaint_text: Şikayet metni
        
        Returns:
            Kategori adı veya None
        """
        categories = self.excel_manager.get_all_categories()
        
        system_prompt = """Sen bir müşteri şikayetlerini kategorize eden asistansın.
Verilen şikayet metnini analiz edip en uygun kategoriyi belirle.
Sadece JSON formatında yanıt ver."""
        
        prompt = f"""Lütfen aşağıdaki şikayet metnini kategorize et.

Mevcut Kategoriler: {', '.join(categories)}

Şikayet Metni: "{complaint_text}"

Şu formatta JSON yanıt ver:
{{
    "kategori": "kategori_adi",
    "guven_skoru": 0.95,
    "aciklama": "Neden bu kategori seçildi"
}}

Eğer hiçbir kategoriye uymuyorsa kategori olarak "Diger" yaz."""

        response = self.llm.call_llm(prompt, system_prompt, response_format="json")
        
        if response:
            parsed = self.llm.parse_json_response(response)
            if parsed and 'kategori' in parsed:
                category = parsed['kategori']
                print(f"✅ Kategori belirlendi: {category} (Güven: {parsed.get('guven_skoru', 'N/A')})")
                return category
        
        print("⚠️ Kategori belirlenemedi")
        return None
