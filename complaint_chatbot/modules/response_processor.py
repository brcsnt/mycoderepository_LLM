"""
Response Processor Modülü
Kullanıcı yanıtlarını işler ve normalize eder
"""
from typing import Dict, Optional
from .llm_client import LLMClient
from config import Config
import sys
import os

# Prompt modülünü import et
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from prompts.response_prompt import (
    get_normalizer_system_prompt,
    get_normalizer_user_prompt,
    get_validation_prompt,
)


class ResponseProcessor:
    """Kullanıcı yanıtlarını işleyen sınıf"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Args:
            llm_client: LLM client
        """
        self.llm = llm_client or LLMClient()

    def normalize(self, user_response: str, field_name: str) -> str:
        """
        Kullanıcı yanıtını normalize et

        Args:
            user_response: Kullanıcı yanıtı
            field_name: Alan adı

        Returns:
            Normalize edilmiş değer
        """
        try:
            # Boş yanıt kontrolü
            if not user_response or not user_response.strip():
                return None

            # Prompt hazırla
            system_prompt = get_normalizer_system_prompt()
            user_prompt = get_normalizer_user_prompt(user_response, field_name)

            # LLM'den yanıt al
            response = self.llm.generate_json(user_prompt, system_prompt)

            normalized = response.get("normalized_value")

            if not normalized or normalized == "null":
                # Fallback: Basit temizleme
                return self._simple_normalize(user_response)

            return normalized

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Normalize hatası: {e}")

            # Fallback: Basit temizleme
            return self._simple_normalize(user_response)

    def _simple_normalize(self, text: str) -> str:
        """Basit metin temizleme"""
        if not text:
            return None

        # Gereksiz kelimeleri kaldır
        filler_words = [
            "sanırım", "galiba", "herhalde", "belki", "şey",
            "yani", "işte", "ya", "evet", "hayır", "tamam"
        ]

        words = text.strip().split()
        cleaned_words = [
            w for w in words
            if w.lower() not in filler_words
        ]

        result = " ".join(cleaned_words).strip()

        # İlk harfi büyük yap
        if result:
            result = result[0].upper() + result[1:]

        return result if result else None

    def validate(
        self, value: str, field_name: str, field_description: str
    ) -> Dict:
        """
        Değeri doğrula

        Args:
            value: Doğrulanacak değer
            field_name: Alan adı
            field_description: Alan açıklaması

        Returns:
            {
                "valid": True/False,
                "reason": "açıklama",
                "suggestion": "öneri"
            }
        """
        try:
            # Prompt hazırla
            system_prompt = "Sen bir veri doğrulama uzmanısın."
            user_prompt = get_validation_prompt(
                value, field_name, field_description
            )

            # LLM'den yanıt al
            response = self.llm.generate_json(user_prompt, system_prompt)

            return {
                "valid": response.get("valid", True),
                "reason": response.get("reason", ""),
                "suggestion": response.get("suggestion", ""),
            }

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Doğrulama hatası: {e}")

            # Fallback: Her şeyi geçerli say
            return {
                "valid": True,
                "reason": "",
                "suggestion": "",
            }

    def process_multiple_responses(
        self, responses: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Birden fazla yanıtı işle

        Args:
            responses: {"alan_adi": "kullanıcı_yanıtı", ...}

        Returns:
            {"alan_adi": "normalize_edilmiş_değer", ...}
        """
        processed = {}

        for field_name, response in responses.items():
            normalized = self.normalize(response, field_name)
            processed[field_name] = normalized

        return processed

    def clean_text(self, text: str) -> str:
        """
        Metni temizle (genel amaçlı)

        Args:
            text: Temizlenecek metin

        Returns:
            Temizlenmiş metin
        """
        if not text:
            return ""

        # Fazla boşlukları kaldır
        text = " ".join(text.split())

        # Başta ve sonda boşluk kaldır
        text = text.strip()

        return text

    def extract_number(self, text: str) -> Optional[float]:
        """
        Metinden sayı çıkar

        Args:
            text: Metin

        Returns:
            Sayı veya None
        """
        import re

        if not text:
            return None

        # Sayı pattern'i
        pattern = r"[\d.,]+"
        matches = re.findall(pattern, text)

        if not matches:
            return None

        try:
            # İlk sayıyı al
            number_str = matches[0].replace(",", ".")
            return float(number_str)
        except:
            return None

    def extract_currency(self, text: str) -> Dict[str, any]:
        """
        Metinden para birimi çıkar

        Args:
            text: Metin

        Returns:
            {"amount": 200.0, "currency": "TL"}
        """
        if not text:
            return {"amount": None, "currency": None}

        amount = self.extract_number(text)

        # Para birimi tespiti
        currency = None
        text_lower = text.lower()

        if "tl" in text_lower or "₺" in text:
            currency = "TL"
        elif "usd" in text_lower or "$" in text:
            currency = "USD"
        elif "eur" in text_lower or "€" in text:
            currency = "EUR"

        return {
            "amount": amount,
            "currency": currency,
        }

    def format_response(
        self, field_name: str, raw_value: str, normalized_value: str
    ) -> str:
        """
        Yanıt formatla (debug için)

        Args:
            field_name: Alan adı
            raw_value: Ham değer
            normalized_value: Normalize edilmiş değer

        Returns:
            Formatlanmış string
        """
        return f"""Alan: {field_name}
Ham Değer: {raw_value}
İşlenmiş Değer: {normalized_value}
"""


if __name__ == "__main__":
    # Test
    processor = ResponseProcessor()

    test_cases = [
        ("atm_lokasyonu", "sanırım beykoz taraflarıydı"),
        ("tutar", "200 TL sıkıştı ya"),
        ("tarih", "dün akşam saat 6 gibi"),
    ]

    for field, response in test_cases:
        normalized = processor.normalize(response, field)
        print(f"\nAlan: {field}")
        print(f"Ham: {response}")
        print(f"Normalize: {normalized}")

        # Para birimi testi
        if "tutar" in field or "para" in field:
            currency_info = processor.extract_currency(response)
            print(f"Miktar: {currency_info['amount']} {currency_info['currency']}")
