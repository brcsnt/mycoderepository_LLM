"""
Şikayet metninden alan bilgilerini çıkarma
"""
import json
from typing import Dict, Any, List
from llm_service import LLMService
from models import Category, CategoryField, ExtractedData

class FieldExtractionService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    def extract_fields(self, complaint_text: str, category: Category,
                      additional_context: Dict[str, Any] = None) -> ExtractedData:
        """
        Şikayet metninden kategori alanlarını çıkar
        
        Args:
            complaint_text: Şikayet metni
            category: Kategori bilgisi
            additional_context: Ek bağlam (önceki sorulara verilen cevaplar)
        
        Returns:
            ExtractedData objesi
        """
        # Alan açıklamalarını hazırla
        field_descriptions = []
        for field in category.fields:
            field_descriptions.append({
                "alan_adi": field.field_name,
                "soru": field.question,
                "tip": field.field_type
            })
        
        system_prompt = """Sen bir doğal dil işleme uzmanısın.
Verilen şikayet metninden belirli alanları çıkarıyorsun.
Eğer bir alan metinde açıkça belirtilmemişse null olarak işaretle.
Sadece JSON formatında yanıt ver."""
        
        context_text = ""
        if additional_context:
            context_text = f"\n\nEk Bilgiler (Kullanıcının daha önce verdiği cevaplar):\n{json.dumps(additional_context, ensure_ascii=False, indent=2)}"
        
        prompt = f"""Aşağıdaki şikayet metninden istenen bilgileri çıkar.

Şikayet Metni: "{complaint_text}"{context_text}

Çıkarılması Gereken Alanlar:
{json.dumps(field_descriptions, ensure_ascii=False, indent=2)}

Kurallar:
1. Eğer bir bilgi metinde açıkça belirtilmişse değerini yaz
2. Eğer bir bilgi metinde yok veya belirsizse null yaz
3. Değerleri olabildiğince temiz ve standart formatta yaz
4. Sayısal değerleri sayı olarak, metin değerleri string olarak ver

Şu formatta JSON yanıt ver:
{{
    "alanlar": {{
        "alan_adi_1": "değer veya null",
        "alan_adi_2": "değer veya null",
        ...
    }}
}}"""

        response = self.llm.call_llm(prompt, system_prompt, response_format="json")
        
        extracted_fields = {}
        if response:
            parsed = self.llm.parse_json_response(response)
            if parsed and 'alanlar' in parsed:
                extracted_fields = parsed['alanlar']
        
        # Eksik alanları null ile doldur
        for field in category.fields:
            if field.field_name not in extracted_fields:
                extracted_fields[field.field_name] = None
        
        return ExtractedData(
            category=category.category_name,
            fields=extracted_fields
        )
    
    def identify_missing_fields(self, extracted_data: ExtractedData,
                               category: Category) -> List[CategoryField]:
        """
        Eksik (null) alanları belirle
        
        Args:
            extracted_data: Çıkarılan veri
            category: Kategori bilgisi
        
        Returns:
            Eksik alanların listesi
        """
        missing_fields = []
        
        for field in category.fields:
            value = extracted_data.fields.get(field.field_name)
            if value is None or value == "" or value == "null":
                missing_fields.append(field)
        
        print(f"📝 {len(missing_fields)} eksik alan belirlendi: {[f.field_name for f in missing_fields]}")
        return missing_fields
    
    def extract_answer_from_response(self, user_response: str,
                                     current_field: CategoryField) -> Any:
        """
        Kullanıcı cevabından spesifik alan değerini çıkar
        
        Args:
            user_response: Kullanıcı cevabı
            current_field: İlgili alan
        
        Returns:
            Çıkarılan değer
        """
        system_prompt = """Sen bir doğal dil işleme uzmanısın.
Kullanıcının verdiği cevaptan sorulan soruya ait değeri çıkar.
Temiz ve standart formatta ver. Sadece JSON formatında yanıt ver."""
        
        prompt = f"""Kullanıcıya şu soru soruldu: "{current_field.question}"

Kullanıcının Cevabı: "{user_response}"

Bu cevaptan "{current_field.field_name}" alanı için değeri çıkar.

Şu formatta JSON yanıt ver:
{{
    "deger": "çıkarılan değer",
    "temiz_deger": "standartlaştırılmış değer"
}}

Örnek:
- "sanırım beykoz taraflarıydı" → "beykoz"
- "200 TL sıkıştı ya" → "200 TL"
- "kredi kartım" → "kredi kartı"
"""

        response = self.llm.call_llm(prompt, system_prompt, response_format="json")
        
        if response:
            parsed = self.llm.parse_json_response(response)
            if parsed:
                return parsed.get('temiz_deger') or parsed.get('deger')
        
        # Fallback: cevabı olduğu gibi kullan
        return user_response.strip()
