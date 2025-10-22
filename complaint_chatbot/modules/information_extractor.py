"""
Information Extractor Modülü
Şikayet metinlerinden bilgi çıkarır
"""
from typing import Dict, Optional, List
from .llm_client import LLMClient
from .data_manager import DataManager
from config import Config
import sys
import os

# Prompt modülünü import et
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from prompts.extractor_prompt import (
    get_extractor_system_prompt,
    get_extractor_user_prompt,
    get_update_extractor_prompt,
)


class InformationExtractor:
    """Bilgi çıkarma sınıfı"""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        data_manager: Optional[DataManager] = None,
    ):
        """
        Args:
            llm_client: LLM client
            data_manager: Data manager
        """
        self.llm = llm_client or LLMClient()
        self.data_manager = data_manager or DataManager()

    def extract(self, complaint_text: str, category: str) -> Dict:
        """
        Şikayet metninden bilgi çıkar

        Args:
            complaint_text: Şikayet metni
            category: Kategori adı

        Returns:
            {
                "sikayet_metni": "...",
                "alan1": "değer1",
                "alan2": null,
                ...
            }
        """
        try:
            # Kategori alanlarını al
            fields = self.data_manager.get_category_fields(category)

            if not fields:
                raise ValueError(f"Kategori bulunamadı: {category}")

            # Prompt hazırla
            system_prompt = get_extractor_system_prompt()
            user_prompt = get_extractor_user_prompt(
                complaint_text, fields, category
            )

            # LLM'den yanıt al
            response = self.llm.generate_json(user_prompt, system_prompt)

            # Şikayet metnini ekle
            response["sikayet_metni"] = complaint_text

            # Tüm alanların olduğundan emin ol (eksik alanları null yap)
            for field_name in fields.keys():
                if field_name not in response:
                    response[field_name] = None

            return response

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Bilgi çıkarma hatası: {e}")
                raise

            # Fallback: Boş schema döndür
            schema = self.data_manager.get_category_schema(category)
            schema["sikayet_metni"] = complaint_text
            return schema

    def get_missing_fields(self, extracted_data: Dict) -> List[str]:
        """
        Null olan alanları döndür

        Args:
            extracted_data: Çıkarılmış veri

        Returns:
            Null olan alan adları listesi
        """
        missing = []

        for field, value in extracted_data.items():
            # "sikayet_metni" alanını kontrol dışı tut
            if field == "sikayet_metni":
                continue

            if value is None or value == "" or value == "null":
                missing.append(field)

        return missing

    def get_questions_for_missing_fields(
        self, category: str, missing_fields: List[str]
    ) -> Dict[str, str]:
        """
        Eksik alanlar için soruları döndür

        Args:
            category: Kategori adı
            missing_fields: Eksik alan adları

        Returns:
            {
                "alan_adi": "Soru metni",
                ...
            }
        """
        all_questions = self.data_manager.get_category_questions(category)

        questions = {}
        for field in missing_fields:
            if field in all_questions:
                questions[field] = all_questions[field]

        return questions

    def extract_from_response(
        self,
        user_response: str,
        field_name: str,
        question: str,
        original_complaint: str = "",
    ) -> Optional[str]:
        """
        Kullanıcı yanıtından belirli bir alan için değer çıkar

        Args:
            user_response: Kullanıcı yanıtı
            field_name: Alan adı
            question: Sorulan soru
            original_complaint: İlk şikayet metni

        Returns:
            Çıkarılan değer veya None
        """
        try:
            # Prompt hazırla
            system_prompt = get_extractor_system_prompt()
            user_prompt = get_update_extractor_prompt(
                original_complaint, {}, user_response, field_name, question
            )

            # LLM'den yanıt al
            response = self.llm.generate_json(user_prompt, system_prompt)

            value = response.get("value")

            # "null" string'ini None'a çevir
            if value == "null" or value == "":
                return None

            return value

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Yanıt çıkarma hatası: {e}")

            # Fallback: Kullanıcı yanıtını direkt döndür
            return user_response.strip() if user_response.strip() else None

    def update_extracted_data(
        self,
        extracted_data: Dict,
        field_name: str,
        value: any,
    ) -> Dict:
        """
        Çıkarılmış veriyi güncelle

        Args:
            extracted_data: Mevcut veri
            field_name: Güncellenecek alan
            value: Yeni değer

        Returns:
            Güncellenmiş veri
        """
        extracted_data[field_name] = value
        return extracted_data

    def validate_extracted_data(
        self, extracted_data: Dict, category: str
    ) -> Dict:
        """
        Çıkarılmış veriyi doğrula ve temizle

        Args:
            extracted_data: Çıkarılmış veri
            category: Kategori adı

        Returns:
            {
                "valid": True/False,
                "missing_fields": [...],
                "filled_fields": [...],
                "completion_rate": 0.75
            }
        """
        fields = self.data_manager.get_category_fields(category)
        total_fields = len(fields)

        missing = self.get_missing_fields(extracted_data)
        filled = [
            f for f in fields.keys() if f not in missing
        ]

        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "filled_fields": filled,
            "completion_rate": len(filled) / total_fields if total_fields > 0 else 0,
            "total_fields": total_fields,
        }

    def get_extraction_summary(
        self, extracted_data: Dict, category: str
    ) -> str:
        """
        Çıkarma özeti oluştur

        Args:
            extracted_data: Çıkarılmış veri
            category: Kategori adı

        Returns:
            Özet metni
        """
        validation = self.validate_extracted_data(extracted_data, category)

        summary = f"""Kategori: {category}
Toplam Alan: {validation['total_fields']}
Dolu Alan: {len(validation['filled_fields'])}
Eksik Alan: {len(validation['missing_fields'])}
Tamamlanma Oranı: {validation['completion_rate']:.1%}

Dolu Alanlar: {', '.join(validation['filled_fields']) if validation['filled_fields'] else 'Yok'}
Eksik Alanlar: {', '.join(validation['missing_fields']) if validation['missing_fields'] else 'Yok'}
"""
        return summary


if __name__ == "__main__":
    # Test
    try:
        extractor = InformationExtractor()

        complaint = "Merhaba, Beykoz'daki ATM'den 200 TL param sıkıştı"
        category = "ATM"

        print(f"Şikayet: {complaint}")
        print(f"Kategori: {category}\n")

        # Bilgi çıkar
        extracted = extractor.extract(complaint, category)

        print("Çıkarılan Bilgiler:")
        for field, value in extracted.items():
            print(f"  {field}: {value}")

        # Eksik alanlar
        missing = extractor.get_missing_fields(extracted)
        print(f"\nEksik Alanlar: {missing}")

        # Sorular
        questions = extractor.get_questions_for_missing_fields(category, missing)
        print("\nSorulacak Sorular:")
        for field, question in questions.items():
            print(f"  {field}: {question}")

        # Özet
        print("\n" + extractor.get_extraction_summary(extracted, category))

    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
