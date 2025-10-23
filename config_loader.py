"""
Excel Sütun Mapping Konfigürasyonu
Bu dosya Excel dosyasındaki sütun adlarını parametrik hale getirir.
Kullanıcı kendi Excel formatını buradan tanımlayabilir.
"""
import os
import json
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ExcelColumnMapping:
    """Excel sütun adlarının mapping'i"""
    # Ana sütun adları
    kategori_adi: str = "kategori_adi"
    alan_adi: str = "alan_adi"
    soru: str = "soru"
    alan_tipi: str = "alan_tipi"
    gerekli_mi: str = "gerekli_mi"
    aciklama: str = "aciklama"

    def to_dict(self) -> Dict[str, str]:
        """Mapping'i dictionary'ye çevir"""
        return {
            "kategori_adi": self.kategori_adi,
            "alan_adi": self.alan_adi,
            "soru": self.soru,
            "alan_tipi": self.alan_tipi,
            "gerekli_mi": self.gerekli_mi,
            "aciklama": self.aciklama
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ExcelColumnMapping':
        """Dictionary'den mapping oluştur"""
        return cls(
            kategori_adi=data.get("kategori_adi", "kategori_adi"),
            alan_adi=data.get("alan_adi", "alan_adi"),
            soru=data.get("soru", "soru"),
            alan_tipi=data.get("alan_tipi", "alan_tipi"),
            gerekli_mi=data.get("gerekli_mi", "gerekli_mi"),
            aciklama=data.get("aciklama", "aciklama")
        )


class ConfigLoader:
    """
    Konfigürasyon yükleyici sınıfı
    Excel sütun mapping'lerini JSON dosyasından veya environment variable'dan okur
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Args:
            config_file: JSON config dosyası yolu (opsiyonel)
        """
        self.config_file = config_file or "excel_config.json"
        self.column_mapping: ExcelColumnMapping = self._load_mapping()

    def _load_mapping(self) -> ExcelColumnMapping:
        """
        Sütun mapping'ini yükle

        Öncelik sırası:
        1. JSON config dosyası
        2. Environment variables
        3. Varsayılan değerler
        """
        # 1. JSON config dosyasından yükle
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if "excel_columns" in config_data:
                        print(f"✅ Excel sütun mapping'i yüklendi: {self.config_file}")
                        return ExcelColumnMapping.from_dict(config_data["excel_columns"])
            except Exception as e:
                print(f"⚠️ Config dosyası okunamadı: {str(e)}")

        # 2. Environment variables'dan yükle
        env_mapping = {
            "kategori_adi": os.getenv("EXCEL_COL_CATEGORY", "kategori_adi"),
            "alan_adi": os.getenv("EXCEL_COL_FIELD", "alan_adi"),
            "soru": os.getenv("EXCEL_COL_QUESTION", "soru"),
            "alan_tipi": os.getenv("EXCEL_COL_TYPE", "alan_tipi"),
            "gerekli_mi": os.getenv("EXCEL_COL_REQUIRED", "gerekli_mi"),
            "aciklama": os.getenv("EXCEL_COL_DESCRIPTION", "aciklama")
        }

        # Eğer environment'da özelleştirilmiş değer varsa kullan
        if any(os.getenv(f"EXCEL_COL_{key.upper()}") for key in ["CATEGORY", "FIELD", "QUESTION"]):
            print("✅ Excel sütun mapping'i environment variables'dan yüklendi")
            return ExcelColumnMapping.from_dict(env_mapping)

        # 3. Varsayılan değerleri kullan
        print("ℹ️ Varsayılan Excel sütun mapping'i kullanılıyor")
        return ExcelColumnMapping()

    def save_mapping(self, mapping: ExcelColumnMapping):
        """
        Mapping'i JSON dosyasına kaydet

        Args:
            mapping: Kaydedilecek mapping
        """
        config_data = {
            "excel_columns": mapping.to_dict(),
            "description": "Excel dosyasındaki sütun adlarının mapping'i"
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Mapping kaydedildi: {self.config_file}")
        except Exception as e:
            print(f"❌ Mapping kaydedilemedi: {str(e)}")

    def create_default_config(self):
        """Varsayılan config dosyası oluştur"""
        default_mapping = ExcelColumnMapping()
        self.save_mapping(default_mapping)

        print(f"""
📝 Varsayılan config dosyası oluşturuldu: {self.config_file}

Eğer Excel dosyanızda farklı sütun adları kullanıyorsanız,
bu dosyayı düzenleyerek sütun adlarınızı tanımlayabilirsiniz.

Örnek:
{{
  "excel_columns": {{
    "kategori_adi": "Category",
    "alan_adi": "Field_Name",
    "soru": "Question",
    "alan_tipi": "Type",
    "gerekli_mi": "Required",
    "aciklama": "Description"
  }}
}}
""")

    def get_column_name(self, field: str) -> str:
        """
        Belirli bir alan için Excel sütun adını getir

        Args:
            field: Alan adı (kategori_adi, alan_adi, vb.)

        Returns:
            Excel'deki sütun adı
        """
        return getattr(self.column_mapping, field, field)

    def print_mapping(self):
        """Mevcut mapping'i yazdır"""
        print("\n" + "="*50)
        print("📋 Excel Sütun Mapping'i")
        print("="*50)
        mapping_dict = self.column_mapping.to_dict()
        for key, value in mapping_dict.items():
            print(f"  {key:15} -> {value}")
        print("="*50 + "\n")


# Global instance
_config_loader = None

def get_config_loader(config_file: Optional[str] = None) -> ConfigLoader:
    """
    Global ConfigLoader instance'ını getir (Singleton pattern)

    Args:
        config_file: Config dosyası yolu

    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_file)
    return _config_loader


if __name__ == "__main__":
    # Test ve örnek kullanım
    loader = ConfigLoader()
    loader.print_mapping()

    # Varsayılan config oluştur
    if not os.path.exists(loader.config_file):
        loader.create_default_config()
