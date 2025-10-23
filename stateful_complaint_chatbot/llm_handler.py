"""
LLM Handler Module
Gemini API entegrasyonu ve prompt yönetimi
"""

import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional, Tuple
import re


class LLMHandler:
    """
    Gemini API kullanarak şikayet kategorizasyonu ve veri çıkarımı yapan sınıf.
    İki ana görev:
    1. İlk şikayet metninden kategori ve mevcut verileri çıkarma
    2. Takip sorularına verilen cevaplardan spesifik veri çıkarma
    """

    def __init__(self, api_key: str, model_name: str = "gemini-3-27b"):
        """
        Args:
            api_key: Gemini API anahtarı
            model_name: Kullanılacak model adı (varsayılan: gemini-3-27b)
        """
        if not api_key:
            raise ValueError("API key boş olamaz. GEMINI_API_KEY environment variable'ı ayarlayın.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def categorize_and_extract(
        self,
        complaint_text: str,
        available_categories: Dict[str, Dict]
    ) -> Tuple[str, Dict[str, Optional[str]]]:
        """
        GÖREV 1: İlk şikayet metnini kategorize et ve mevcut bilgileri çıkar.

        Args:
            complaint_text: Kullanıcının ilk şikayet metni
            available_categories: Mevcut kategoriler ve alanları
                {
                    "ATM_SORUNU": {
                        "fields": {
                            "atm_lokasyonu": {...},
                            "atm_problemi": {...}
                        }
                    }
                }

        Returns:
            (kategori_adı, veri_dict)
            Örnek: ("ATM_SORUNU", {"atm_lokasyonu": None, "atm_problemi": "para sıkışması"})
        """

        # Kategorileri ve alanları prompt için hazırla
        categories_info = self._format_categories_for_prompt(available_categories)

        prompt = f"""
Sen bir müşteri şikayeti analiz asistanısın. Görevin, verilen şikayet metnini kategorize etmek ve mevcut bilgileri çıkarmak.

MEVCUT KATEGORİLER VE ALANLAR:
{categories_info}

ŞİKAYET METNİ:
"{complaint_text}"

GÖREV:
1. Şikayeti yukarıdaki kategorilerden BİRİNE ata (en uygun kategoriyi seç)
2. Şikayet metninden çıkarabileceğin bilgileri ilgili alanlara doldur
3. Çıkaramadığın alanları null olarak bırak

ÇIKTI FORMATI (sadece JSON döndür, başka açıklama yapma):
{{
    "kategori": "KATEGORI_ADI",
    "veriler": {{
        "alan_1": "çıkarılan değer veya null",
        "alan_2": "çıkarılan değer veya null",
        ...
    }}
}}

ÖNEMLİ KURALLAR:
- Sadece JSON döndür, başka metin yazma
- Kategori adını tam olarak yukarıdaki listeden seç
- Alan adlarını tam olarak yukarıdaki listeden kullan
- Emin olmadığın bilgileri uydurma, null yaz
- Çıkarılan değerleri temiz ve kısa tut (gereksiz kelimeler ekleme)
"""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            kategori = result.get("kategori", "")
            veriler = result.get("veriler", {})

            # Kategori geçerli mi kontrol et
            if kategori not in available_categories:
                raise ValueError(f"LLM geçersiz kategori döndürdü: {kategori}")

            # Tüm alanları içeren tam bir dict oluştur (eksik alanları None ile doldur)
            category_fields = available_categories[kategori]["fields"].keys()
            full_data = {field: veriler.get(field, None) for field in category_fields}

            return kategori, full_data

        except Exception as e:
            raise Exception(f"Kategorizasyon hatası: {str(e)}")

    def extract_field_value(
        self,
        user_answer: str,
        field_name: str,
        question: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        GÖREV 2: Kullanıcının belirli bir soruya verdiği cevaptan temiz veriyi çıkar.

        Args:
            user_answer: Kullanıcının cevabı
            field_name: İlgili alan adı (örn: "atm_lokasyonu")
            question: Sorulan soru
            context: Ek bağlam bilgisi (opsiyonel)

        Returns:
            Çıkarılan temiz değer veya None

        Örnek:
            user_answer: "sanırım beykoz taraflarıydı"
            field_name: "atm_lokasyonu"
            question: "Problem yaşadığınız ATM lokasyonu nedir?"
            -> Return: "Beykoz"
        """

        context_part = f"\nBAĞLAM: {context}" if context else ""

        prompt = f"""
Sen bir veri çıkarma asistanısın. Kullanıcının cevabından sadece istenilen bilgiyi temiz bir şekilde çıkar.

SORULAN SORU: "{question}"
ALAN ADI: {field_name}
KULLANICI CEVABI: "{user_answer}"{context_part}

GÖREV:
Kullanıcının cevabından, sorulan soruya karşılık gelen bilgiyi çıkar ve temizle.

KURALLAR:
- Sadece asıl bilgiyi çıkar (gereksiz kelimeler olmadan)
- "sanırım", "galiba", "taraflarıydı" gibi belirsizlik ifadelerini çıkar
- Cevap net değilse veya bilgi yoksa "null" döndür
- Sayısal değerlerde sadece sayı ve birimi döndür
- Lokasyon bilgilerini düzgün formatta döndür (ilk harf büyük)

ÇIKTI FORMATI (sadece değeri döndür, JSON veya başka format kullanma):
temiz_değer

Örnekler:
Kullanıcı: "sanırım beykoz taraflarıydı" -> Beykoz
Kullanıcı: "200 TL sıkıştı ya" -> 200 TL
Kullanıcı: "bilmiyorum ki" -> null
Kullanıcı: "kredi kartımdan 500 lira" -> 500 TL
"""

        try:
            response = self.model.generate_content(prompt)
            extracted_value = response.text.strip()

            # "null", "yok", "bilmiyorum" gibi değerler None döndür
            if extracted_value.lower() in ["null", "none", "yok", "bilmiyorum", "bilinmiyor", "n/a"]:
                return None

            return extracted_value if extracted_value else None

        except Exception as e:
            raise Exception(f"Veri çıkarma hatası: {str(e)}")

    def validate_and_refine_data(
        self,
        complaint_data: Dict[str, any],
        original_text: str
    ) -> Dict[str, any]:
        """
        FİNAL GÖREV: Toplanan tüm verileri doğrula ve rafine et.

        Args:
            complaint_data: Toplanan tüm veriler
            original_text: İlk şikayet metni

        Returns:
            Rafine edilmiş ve doğrulanmış veri sözlüğü
        """

        data_json = json.dumps(complaint_data, ensure_ascii=False, indent=2)

        prompt = f"""
Sen bir veri doğrulama asistanısın. Toplanan şikayet verilerini kontrol et ve rafine et.

ORIJINAL ŞİKAYET:
"{original_text}"

TOPLANAN VERILER:
{data_json}

GÖREV:
1. Tüm verilerin tutarlı olduğunu kontrol et
2. Gereksiz kelimeler veya tekrarlar varsa temizle
3. Format tutarsızlıkları düzelt
4. Eksik ama çıkarılabilecek bilgiler varsa ekle

KURALLAR:
- Veri yapısını değiştirme (alanları silme veya ekleme)
- Sadece mevcut değerleri rafine et
- Uydurma bilgi ekleme
- Sadece JSON döndür

ÇIKTI FORMATI:
{{
    "alan_1": "rafine_değer",
    "alan_2": "rafine_değer",
    ...
}}
"""

        try:
            response = self.model.generate_content(prompt)
            refined_data = self._parse_json_response(response.text)
            return refined_data

        except Exception as e:
            # Hata durumunda orijinal veriyi döndür
            print(f"Rafine etme hatası (orijinal veri kullanılıyor): {str(e)}")
            return complaint_data

    def _format_categories_for_prompt(self, categories: Dict[str, Dict]) -> str:
        """Kategorileri ve alanları prompt için string formatına dönüştür"""
        lines = []
        for cat_name, cat_info in categories.items():
            lines.append(f"\n[{cat_name}]")
            for field_name, field_info in cat_info["fields"].items():
                req = "(zorunlu)" if field_info.get("required", False) else "(opsiyonel)"
                lines.append(f"  - {field_name}: {field_info['question']} {req}")

        return "\n".join(lines)

    def _parse_json_response(self, response_text: str) -> Dict:
        """LLM yanıtından JSON çıkar"""
        try:
            # Önce direkt parse dene
            return json.loads(response_text)
        except json.JSONDecodeError:
            # JSON kod bloğu içinde olabilir
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Sadece {...} kısmını bul
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            raise ValueError(f"JSON parse edilemedi: {response_text}")


# Test için örnek kullanım
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable tanımlı değil!")
        exit(1)

    # Test kategorileri
    test_categories = {
        "ATM_SORUNU": {
            "fields": {
                "atm_lokasyonu": {
                    "question": "Problem yaşadığınız ATM lokasyonu nedir?",
                    "required": True
                },
                "atm_problemi": {
                    "question": "ATM'de yaşadığınız sorun nedir?",
                    "required": True
                },
                "atm_para_islem_miktari": {
                    "question": "ATM'de ne kadar paranız sıkıştı?",
                    "required": False
                }
            }
        }
    }

    try:
        llm = LLMHandler(api_key=api_key)

        # Test 1: Kategorizasyon ve ilk çıkarım
        print("=== TEST 1: Kategorizasyon ===")
        complaint = "merhaba, ATM'de param sıkıştı"
        kategori, veriler = llm.categorize_and_extract(complaint, test_categories)
        print(f"Kategori: {kategori}")
        print(f"Veriler: {json.dumps(veriler, ensure_ascii=False, indent=2)}")

        # Test 2: Spesifik veri çıkarımı
        print("\n=== TEST 2: Veri Çıkarımı ===")
        answer = "sanırım beykoz taraflarıydı"
        extracted = llm.extract_field_value(
            answer,
            "atm_lokasyonu",
            "Problem yaşadığınız ATM lokasyonu nedir?"
        )
        print(f"Çıkarılan değer: {extracted}")

    except Exception as e:
        print(f"Hata: {e}")
