"""
Excel dosyasından kategori bilgilerini okuma
"""
import pandas as pd
from typing import Dict, List
from models import Category, CategoryField
from config import Config

class ExcelManager:
    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or Config.EXCEL_FILE_PATH
        self.categories: Dict[str, Category] = {}
        self._load_categories()
    
    def _load_categories(self):
        """Excel'den kategorileri yükle"""
        try:
            df = pd.read_excel(self.excel_path)
            
            # Excel formatı: kategori_adi | alan_adi | soru | alan_tipi | gerekli_mi
            grouped = df.groupby('kategori_adi')
            
            for category_name, group in grouped:
                fields = []
                for _, row in group.iterrows():
                    field = CategoryField(
                        field_name=row['alan_adi'],
                        question=row['soru'],
                        field_type=row.get('alan_tipi', 'string'),
                        required=row.get('gerekli_mi', True)
                    )
                    fields.append(field)
                
                self.categories[category_name] = Category(
                    category_name=category_name,
                    fields=fields,
                    description=group.iloc[0].get('aciklama', None)
                )
            
            print(f"✅ {len(self.categories)} kategori yüklendi: {list(self.categories.keys())}")
            
        except FileNotFoundError:
            print(f"⚠️ Excel dosyası bulunamadı: {self.excel_path}")
            print("📝 Örnek Excel dosyası oluşturuluyor...")
            self._create_sample_excel()
        except Exception as e:
            print(f"❌ Excel yükleme hatası: {str(e)}")
    
    def _create_sample_excel(self):
        """Örnek Excel dosyası oluştur"""
        sample_data = {
            'kategori_adi': [
                'ATM', 'ATM', 'ATM',
                'Kart', 'Kart', 'Kart',
                'Hesap', 'Hesap', 'Hesap'
            ],
            'alan_adi': [
                'atm_lokasyonu', 'atm_problemi', 'atm_para_miktari',
                'kart_turu', 'kart_problemi', 'kart_son_kullanim',
                'hesap_turu', 'hesap_problemi', 'hesap_islem_tarihi'
            ],
            'soru': [
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
            'alan_tipi': [
                'string', 'string', 'string',
                'string', 'string', 'string',
                'string', 'string', 'string'
            ],
            'gerekli_mi': [True] * 9,
            'aciklama': [
                'ATM ile ilgili şikayetler', '', '',
                'Kart ile ilgili şikayetler', '', '',
                'Hesap ile ilgili şikayetler', '', ''
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_excel(self.excel_path, index=False)
        print(f"✅ Örnek Excel dosyası oluşturuldu: {self.excel_path}")
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
