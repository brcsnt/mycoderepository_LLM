"""
Categorizer Modülü
Şikayet metinlerini kategorize eder
"""
from typing import Dict, Optional
from .llm_client import LLMClient
from .data_manager import DataManager
from config import Config
import sys
import os

# Prompt modülünü import et
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from prompts.categorizer_prompt import (
    get_categorizer_system_prompt,
    get_categorizer_user_prompt,
    get_fallback_category_prompt,
)


class Categorizer:
    """Şikayet kategorize sınıfı"""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        data_manager: Optional[DataManager] = None,
    ):
        """
        Args:
            llm_client: LLM client (varsayılan: yeni instance)
            data_manager: Data manager (varsayılan: yeni instance)
        """
        self.llm = llm_client or LLMClient()
        self.data_manager = data_manager or DataManager()

    def categorize(self, complaint_text: str) -> Dict:
        """
        Şikayet metnini kategorize et

        Args:
            complaint_text: Şikayet metni

        Returns:
            {
                "kategori": "ATM",
                "guven_skoru": 0.95,
                "aciklama": "ATM ile ilgili şikayet"
            }
        """
        try:
            # Mevcut kategorileri al
            categories = self.data_manager.get_all_categories()

            if not categories:
                raise ValueError("Kategori bulunamadı. Excel dosyasını kontrol edin.")

            # Prompt hazırla
            system_prompt = get_categorizer_system_prompt()
            user_prompt = get_categorizer_user_prompt(complaint_text, categories)

            # LLM'den yanıt al
            response = self.llm.generate_json(user_prompt, system_prompt)

            # Yanıtı doğrula
            if "kategori" not in response:
                if Config.DEBUG_MODE:
                    print(f"Geçersiz yanıt: {response}")
                return self._fallback_categorize(complaint_text, categories)

            kategori = response["kategori"]

            # Kategori geçerli mi kontrol et
            if not self.data_manager.validate_category(kategori):
                # En yakın kategoriyi bul
                kategori = self._find_closest_category(kategori, categories)

            return {
                "kategori": kategori,
                "guven_skoru": response.get("guven_skoru", 0.8),
                "aciklama": response.get("aciklama", ""),
            }

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Kategorize hatası: {e}")
                raise

            # Fallback: İlk kategoriyi döndür
            return {
                "kategori": self.data_manager.get_all_categories()[0],
                "guven_skoru": 0.5,
                "aciklama": "Otomatik kategorize edildi",
            }

    def _fallback_categorize(
        self, complaint_text: str, categories: list
    ) -> Dict:
        """Basit fallback kategorize"""
        try:
            # Basit keyword eşleştirme
            complaint_lower = complaint_text.lower()

            for category in categories:
                if category.lower() in complaint_lower:
                    return {
                        "kategori": category,
                        "guven_skoru": 0.7,
                        "aciklama": "Keyword eşleştirmesi ile bulundu",
                    }

            # Hiçbiri eşleşmezse ilk kategori
            return {
                "kategori": categories[0],
                "guven_skoru": 0.5,
                "aciklama": "Varsayılan kategori",
            }

        except:
            return {
                "kategori": categories[0],
                "guven_skoru": 0.3,
                "aciklama": "Hata nedeniyle varsayılan",
            }

    def _find_closest_category(self, kategori: str, categories: list) -> str:
        """En yakın kategoriyi bul (basit string matching)"""
        kategori_lower = kategori.lower()

        # Tam eşleşme (case-insensitive)
        for cat in categories:
            if cat.lower() == kategori_lower:
                return cat

        # Kısmi eşleşme
        for cat in categories:
            if kategori_lower in cat.lower() or cat.lower() in kategori_lower:
                return cat

        # Hiçbiri eşleşmezse ilk kategori
        return categories[0]

    def categorize_with_confidence(
        self, complaint_text: str, min_confidence: float = 0.7
    ) -> Optional[Dict]:
        """
        Minimum güven skoruyla kategorize et

        Args:
            complaint_text: Şikayet metni
            min_confidence: Minimum güven skoru (0-1)

        Returns:
            Kategori bilgisi veya None (güven skoru düşükse)
        """
        result = self.categorize(complaint_text)

        if result["guven_skoru"] < min_confidence:
            return None

        return result

    def get_category_suggestions(
        self, complaint_text: str, top_k: int = 3
    ) -> list:
        """
        Şikayet için kategori önerileri

        Args:
            complaint_text: Şikayet metni
            top_k: Döndürülecek öneri sayısı

        Returns:
            Kategori önerileri listesi
        """
        # Bu basit implementasyonda sadece en iyi sonucu döndürüyoruz
        # Gelişmiş versiyonda tüm kategoriler için skor hesaplanabilir
        result = self.categorize(complaint_text)
        return [result]


if __name__ == "__main__":
    # Test
    try:
        categorizer = Categorizer()

        test_complaints = [
            "ATM'den param sıkıştı",
            "Kredi kartım çalınmış",
            "Hesabımdan hatalı para çekilmiş",
            "Müşteri hizmetleri beni aramadı",
        ]

        for complaint in test_complaints:
            result = categorizer.categorize(complaint)
            print(f"\nŞikayet: {complaint}")
            print(f"Kategori: {result['kategori']}")
            print(f"Güven: {result['guven_skoru']:.2f}")
            print(f"Açıklama: {result['aciklama']}")

    except Exception as e:
        print(f"Hata: {e}")
