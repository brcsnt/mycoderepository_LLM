"""
Config Manager Module
Excel'den parametrik olarak konfigürasyon okuma ve yönetimi
"""

import pandas as pd
from typing import Dict, List, Optional
import os


class ConfigManager:
    """
    Excel dosyasından kategori, alan ve soru bilgilerini okuyup yöneten sınıf.
    Excel dosyası formatı parametrik olarak belirlenebilir.
    """

    def __init__(self, excel_path: str, column_mapping: Optional[Dict[str, str]] = None):
        """
        Args:
            excel_path: Konfigürasyon Excel dosyasının yolu
            column_mapping: Excel sütun adlarının sistem içi kullanılan adlara eşleştirilmesi
                Örnek: {
                    "kategori": "Kategori Adı",
                    "alan": "Alan Bilgisi",
                    "soru": "Sorulacak Soru",
                    "zorunlu": "Zorunlu mu?"
                }
        """
        self.excel_path = excel_path

        # Varsayılan sütun eşleştirmesi
        self.default_mapping = {
            "kategori": "Kategori",
            "alan": "Alan",
            "soru": "Soru",
            "zorunlu": "Zorunlu"
        }

        # Kullanıcı tanımlı mapping varsa onu kullan, yoksa varsayılanı
        self.column_mapping = column_mapping if column_mapping else self.default_mapping

        # Konfigürasyonu yükle
        self.config_data = self._load_config()
        self.categories = self._parse_categories()

    def _load_config(self) -> pd.DataFrame:
        """Excel dosyasını oku ve DataFrame olarak döndür"""
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {self.excel_path}")

        try:
            df = pd.read_excel(self.excel_path)

            # Sütun adlarını kontrol et
            for system_name, excel_name in self.column_mapping.items():
                if excel_name not in df.columns:
                    raise ValueError(
                        f"Excel dosyasında '{excel_name}' sütunu bulunamadı. "
                        f"Mevcut sütunlar: {list(df.columns)}"
                    )

            return df

        except Exception as e:
            raise Exception(f"Excel dosyası okunurken hata: {str(e)}")

    def _parse_categories(self) -> Dict[str, Dict]:
        """
        Excel verilerini kategori bazlı yapılandırılmış bir sözlüğe dönüştür.

        Returns:
            {
                "ATM_SORUNU": {
                    "fields": {
                        "atm_lokasyonu": {
                            "question": "Problem yaşadığınız ATM lokasyonu nedir?",
                            "required": True
                        },
                        ...
                    }
                },
                ...
            }
        """
        categories = {}

        # Sütun adlarını al
        kategori_col = self.column_mapping["kategori"]
        alan_col = self.column_mapping["alan"]
        soru_col = self.column_mapping["soru"]
        zorunlu_col = self.column_mapping["zorunlu"]

        # Her satırı işle
        for _, row in self.config_data.iterrows():
            kategori = str(row[kategori_col]).strip()
            alan = str(row[alan_col]).strip()
            soru = str(row[soru_col]).strip()

            # Zorunlu alanı kontrolü (Evet/Yes/True/1 gibi değerler)
            zorunlu_val = str(row[zorunlu_col]).strip().lower()
            zorunlu = zorunlu_val in ['evet', 'yes', 'true', '1', 'e', 'y']

            # Kategori yoksa oluştur
            if kategori not in categories:
                categories[kategori] = {"fields": {}}

            # Alan bilgisini ekle
            categories[kategori]["fields"][alan] = {
                "question": soru,
                "required": zorunlu
            }

        return categories

    def get_categories(self) -> List[str]:
        """Tüm kategori isimlerini döndür"""
        return list(self.categories.keys())

    def get_category_config(self, category: str) -> Optional[Dict]:
        """Belirli bir kategorinin konfigürasyonunu döndür"""
        return self.categories.get(category)

    def get_fields_for_category(self, category: str) -> List[str]:
        """Belirli bir kategori için tüm alan isimlerini döndür"""
        category_config = self.get_category_config(category)
        if category_config:
            return list(category_config["fields"].keys())
        return []

    def get_question_for_field(self, category: str, field: str) -> Optional[str]:
        """Belirli bir alan için soruyu döndür"""
        category_config = self.get_category_config(category)
        if category_config and field in category_config["fields"]:
            return category_config["fields"][field]["question"]
        return None

    def is_field_required(self, category: str, field: str) -> bool:
        """Alanın zorunlu olup olmadığını kontrol et"""
        category_config = self.get_category_config(category)
        if category_config and field in category_config["fields"]:
            return category_config["fields"][field]["required"]
        return False

    def reload_config(self):
        """Konfigürasyonu yeniden yükle (Excel güncellendiğinde kullanılır)"""
        self.config_data = self._load_config()
        self.categories = self._parse_categories()

    def get_summary(self) -> str:
        """Konfigürasyon özetini döndür"""
        summary = f"Toplam Kategori Sayısı: {len(self.categories)}\n\n"

        for category, config in self.categories.items():
            field_count = len(config["fields"])
            required_count = sum(1 for f in config["fields"].values() if f["required"])
            summary += f"📋 {category}: {field_count} alan ({required_count} zorunlu)\n"

            for field_name, field_info in config["fields"].items():
                req_marker = "✓" if field_info["required"] else "○"
                summary += f"   {req_marker} {field_name}: {field_info['question']}\n"
            summary += "\n"

        return summary


# Test için örnek kullanım
if __name__ == "__main__":
    # Örnek kullanım
    try:
        # Varsayılan sütun adlarıyla
        config = ConfigManager("config_template.xlsx")
        print(config.get_summary())

        # Özel sütun adlarıyla
        custom_mapping = {
            "kategori": "Şikayet Kategorisi",
            "alan": "Veri Alanı",
            "soru": "Kullanıcıya Sorulacak Soru",
            "zorunlu": "Zorunlu Alan mı?"
        }
        # config = ConfigManager("config_custom.xlsx", column_mapping=custom_mapping)

    except Exception as e:
        print(f"Hata: {e}")
