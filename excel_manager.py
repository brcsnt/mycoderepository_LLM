"""
Excel dosyasından kategori bilgilerini okuma
"""
import pandas as pd
from typing import Dict, List, Optional
from models import Category, CategoryField
from config import Config
from config_loader import get_config_loader

class ExcelManager:
    def __init__(self, excel_path: str = None, config_file: str = None):
        self.excel_path = excel_path or Config.EXCEL_FILE_PATH
        self.categories: Dict[str, Category] = {}

        # Parametrik sütun mapping'ini yükle
        self.config_loader = get_config_loader(config_file)
        self.col_map = self.config_loader.column_mapping

        # Mapping'i yazdır
        if Config.DEBUG_MODE:
            self.config_loader.print_mapping()

        self._load_categories()

    def _load_categories(self):
        """Excel'den kategorileri yükle (parametrik sütun adları ile)"""
        try:
            df = pd.read_excel(self.excel_path)

            # Parametrik sütun adlarını kullan
            col_kategori = self.col_map.kategori_adi
            col_alan = self.col_map.alan_adi
            col_soru = self.col_map.soru
            col_tip = self.col_map.alan_tipi
            col_gerekli = self.col_map.gerekli_mi
            col_aciklama = self.col_map.aciklama

            # Gerekli sütunların varlığını kontrol et
            required_cols = [col_kategori, col_alan, col_soru]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                raise ValueError(f"Excel dosyasında eksik sütunlar: {missing_cols}\n"
                               f"Mevcut sütunlar: {list(df.columns)}\n"
                               f"Lütfen config_loader.py veya excel_config.json dosyasını kontrol edin.")

            # Kategorilere göre grupla
            grouped = df.groupby(col_kategori)
            
            for category_name, group in grouped:
                fields = []
                for _, row in group.iterrows():
                    field = CategoryField(
                        field_name=row[col_alan],
                        question=row[col_soru],
                        field_type=row.get(col_tip, 'string'),
                        required=row.get(col_gerekli, True)
                    )
                    fields.append(field)

                self.categories[category_name] = Category(
                    category_name=category_name,
                    fields=fields,
                    description=group.iloc[0].get(col_aciklama, None)
                )
            
            print(f"✅ {len(self.categories)} kategori yüklendi: {list(self.categories.keys())}")
            
        except FileNotFoundError:
            print(f"⚠️ Excel dosyası bulunamadı: {self.excel_path}")
            print("📝 Örnek Excel dosyası oluşturuluyor...")
            self._create_sample_excel()
        except Exception as e:
            print(f"❌ Excel yükleme hatası: {str(e)}")
    
    def _create_sample_excel(self):
        """Örnek Excel dosyası oluştur (parametrik sütun adları ile)"""
        # Parametrik sütun adlarını kullan
        col_kategori = self.col_map.kategori_adi
        col_alan = self.col_map.alan_adi
        col_soru = self.col_map.soru
        col_tip = self.col_map.alan_tipi
        col_gerekli = self.col_map.gerekli_mi
        col_aciklama = self.col_map.aciklama

        sample_data = {
            col_kategori: [
                'ATM', 'ATM', 'ATM',
                'Kart', 'Kart', 'Kart',
                'Hesap', 'Hesap', 'Hesap'
            ],
            col_alan: [
                'atm_lokasyonu', 'atm_problemi', 'atm_para_miktari',
                'kart_turu', 'kart_problemi', 'kart_son_kullanim',
                'hesap_turu', 'hesap_problemi', 'hesap_islem_tarihi'
            ],
            col_soru: [
                'Problem yaşadığınız ATM lokasyonu nedir?',
                'ATM de sorun yaşadığınız durum nedir?',
                'ATM de ne kadar paranız sıkıştı?',
                'Hangi kart türünü kullanıyorsunuz? (Kredi/Banka Kartı)',
                'Kartınızla ilgili ne gibi bir sorun yaşıyorsunuz?',
                'Kartınızın son kullanım tarihi nedir?',
                'Hesap türünüz nedir? (Vadesiz/Vadeli)',
                'Hesabınızla ilgili ne gibi bir sorun yaşıyorsunuz?',
                'İşlem tarihi nedir?'
            ],
            col_tip: [
                'string', 'string', 'string',
                'string', 'string', 'string',
                'string', 'string', 'string'
            ],
            col_gerekli: [True] * 9,
            col_aciklama: [
                'ATM ile ilgili şikayetler', '', '',
                'Kart ile ilgili şikayetler', '', '',
                'Hesap ile ilgili şikayetler', '', ''
            ]
        }

        df = pd.DataFrame(sample_data)
        df.to_excel(self.excel_path, index=False)
        print(f"✅ Örnek Excel dosyası oluşturuldu: {self.excel_path}")
        print(f"📋 Kullanılan sütun adları: {list(sample_data.keys())}")
        self._load_categories()
    
    def get_category(self, category_name: str) -> Category:
        """Kategori bilgisini getir"""
        return self.categories.get(category_name)
    
    def get_all_categories(self) -> List[str]:
        """Tüm kategori isimlerini döndür"""
        return list(self.categories.keys())
    
    def get_category_fields(self, category_name: str) -> List[CategoryField]:
        """Kategorinin alanlarını döndür"""
        category = self.get_category(category_name)
        return category.fields if category else []
