"""
Data Manager Modülü
Excel dosyasından kategori, alan ve soru bilgilerini yükler
"""
import pandas as pd
from typing import Dict, List, Optional
from config import Config


class DataManager:
    """Excel verilerini yöneten sınıf"""

    def __init__(self, excel_path: Optional[str] = None):
        """
        Args:
            excel_path: Excel dosya yolu (varsayılan: Config.EXCEL_PATH)
        """
        self.excel_path = excel_path or Config.EXCEL_PATH
        self.data = None
        self.categories_cache = {}
        self.load_data()

    def load_data(self):
        """Excel dosyasını yükle"""
        try:
            self.data = pd.read_excel(self.excel_path)

            # Sütun isimlerini kontrol et
            required_columns = ["kategori", "alan_adi", "alan_aciklamasi", "soru"]
            missing_columns = [
                col for col in required_columns if col not in self.data.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"Excel dosyasında eksik sütunlar: {', '.join(missing_columns)}"
                )

            # Cache'i güncelle
            self._build_cache()

            if Config.DEBUG_MODE:
                print(f"✓ Excel verisi yüklendi: {len(self.data)} kayıt")
                print(f"✓ Kategoriler: {self.get_all_categories()}")

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Excel dosyası bulunamadı: {self.excel_path}\n"
                "Lütfen önce data/create_template.py scriptini çalıştırın."
            )
        except Exception as e:
            raise Exception(f"Excel dosyası yüklenirken hata: {str(e)}")

    def _build_cache(self):
        """Kategori verilerini cache'le"""
        for kategori in self.data["kategori"].unique():
            kategori_data = self.data[self.data["kategori"] == kategori]
            self.categories_cache[kategori] = kategori_data.to_dict("records")

    def get_all_categories(self) -> List[str]:
        """Tüm kategorileri döndür"""
        return list(self.categories_cache.keys())

    def get_category_fields(self, kategori: str) -> Dict[str, Dict]:
        """
        Bir kategorinin tüm alanlarını döndür

        Args:
            kategori: Kategori adı

        Returns:
            {
                "alan_adi": {
                    "soru": "Soru metni",
                    "aciklama": "Alan açıklaması"
                },
                ...
            }
        """
        if kategori not in self.categories_cache:
            return {}

        fields = {}
        for record in self.categories_cache[kategori]:
            fields[record["alan_adi"]] = {
                "soru": record["soru"],
                "aciklama": record["alan_aciklamasi"],
            }

        return fields

    def get_category_questions(self, kategori: str) -> Dict[str, str]:
        """
        Bir kategorinin alan-soru eşleşmesini döndür

        Args:
            kategori: Kategori adı

        Returns:
            {"alan_adi": "Soru metni", ...}
        """
        if kategori not in self.categories_cache:
            return {}

        questions = {}
        for record in self.categories_cache[kategori]:
            questions[record["alan_adi"]] = record["soru"]

        return questions

    def get_field_question(self, kategori: str, alan_adi: str) -> Optional[str]:
        """
        Belirli bir alan için soruyu döndür

        Args:
            kategori: Kategori adı
            alan_adi: Alan adı

        Returns:
            Soru metni veya None
        """
        questions = self.get_category_questions(kategori)
        return questions.get(alan_adi)

    def get_category_schema(self, kategori: str) -> Dict[str, None]:
        """
        Kategori için boş JSON şeması oluştur

        Args:
            kategori: Kategori adı

        Returns:
            {"alan_adi": None, "alan_adi2": None, ...}
        """
        if kategori not in self.categories_cache:
            return {}

        schema = {}
        for record in self.categories_cache[kategori]:
            schema[record["alan_adi"]] = None

        return schema

    def validate_category(self, kategori: str) -> bool:
        """Kategori geçerli mi kontrol et"""
        return kategori in self.categories_cache

    def get_category_info(self, kategori: str) -> Dict:
        """
        Kategori hakkında detaylı bilgi döndür

        Args:
            kategori: Kategori adı

        Returns:
            {
                "kategori": "ATM",
                "alan_sayisi": 4,
                "alanlar": {...},
                "sorular": {...}
            }
        """
        if not self.validate_category(kategori):
            return {}

        return {
            "kategori": kategori,
            "alan_sayisi": len(self.categories_cache[kategori]),
            "alanlar": self.get_category_fields(kategori),
            "sorular": self.get_category_questions(kategori),
        }

    def reload(self):
        """Excel dosyasını yeniden yükle"""
        self.load_data()


if __name__ == "__main__":
    # Test
    try:
        manager = DataManager()

        print("Tüm kategoriler:")
        for kategori in manager.get_all_categories():
            info = manager.get_category_info(kategori)
            print(f"\n{kategori}:")
            print(f"  Alan sayısı: {info['alan_sayisi']}")
            print("  Sorular:")
            for alan, soru in info["sorular"].items():
                print(f"    - {alan}: {soru}")

    except Exception as e:
        print(f"Hata: {e}")
