"""
Bilgi çıkarma için prompt şablonları
"""


def get_extractor_system_prompt() -> str:
    """Bilgi çıkarma için sistem promptu"""
    return """Sen bir bilgi çıkarma uzmanısın.

Görevin metin içinden belirli alanları çıkarmak ve JSON formatında sunmak.

KURALLAR:
1. Metinden çıkarılabilecek alanları doldur
2. Çıkarılamayan alanlar için null değer kullan
3. Tahmin yapma, sadece metinde açıkça belirtilen bilgileri çıkar
4. Tarih, saat, miktar gibi bilgileri normalize et
5. Yanıtını sadece JSON formatında ver
6. JSON dışında hiçbir açıklama ekleme

ÖNEMLİ: Alanların değeri metinde yoksa mutlaka null koy. Boş string ("") kullanma.
"""


def get_extractor_user_prompt(
    complaint_text: str, fields: dict, category: str
) -> str:
    """
    Bilgi çıkarma kullanıcı promptu

    Args:
        complaint_text: Şikayet metni
        fields: Çıkarılacak alanlar ve açıklamaları
        category: Kategori adı

    Returns:
        Prompt metni
    """
    fields_description = "\n".join(
        [f"  - {field}: {info['aciklama']}" for field, info in fields.items()]
    )

    return f"""Kategori: {category}

Şikayet Metni:
"{complaint_text}"

Çıkarılacak Alanlar:
{fields_description}

Yukarıdaki şikayet metninden ilgili bilgileri çıkar ve JSON formatında döndür.

Örnek yanıt formatı:
{{
  "alan1": "değer1",
  "alan2": null,
  "alan3": "değer3"
}}

Metinde olmayan bilgiler için null kullan."""


def get_update_extractor_prompt(
    original_complaint: str,
    extracted_data: dict,
    user_response: str,
    field_name: str,
    question: str,
) -> str:
    """
    Kullanıcı yanıtı ile veriyi güncelleme promptu

    Args:
        original_complaint: İlk şikayet metni
        extracted_data: Mevcut çıkarılmış veri
        user_response: Kullanıcının yanıtı
        field_name: Güncellenen alan adı
        question: Sorulan soru

    Returns:
        Prompt metni
    """
    return f"""Orijinal Şikayet:
"{original_complaint}"

Soru: {question}
Kullanıcı Yanıtı: "{user_response}"

Bu yanıttan "{field_name}" alanı için değer çıkar.

Sadece ilgili değeri döndür, JSON formatında:
{{"value": "çıkarılan değer"}}

Değer bulunamazsa:
{{"value": null}}
"""


if __name__ == "__main__":
    # Test
    print("=== Sistem Promptu ===")
    print(get_extractor_system_prompt())

    print("\n=== Kullanıcı Promptu ===")
    fields = {
        "atm_lokasyonu": {"aciklama": "ATM lokasyonu"},
        "atm_problemi": {"aciklama": "Yaşanan problem"},
        "tutar": {"aciklama": "Para miktarı"},
    }
    print(
        get_extractor_user_prompt("ATM'den 200 TL param sıkıştı", fields, "ATM")
    )
