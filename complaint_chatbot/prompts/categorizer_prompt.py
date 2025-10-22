"""
Kategorize etme için prompt şablonları
"""


def get_categorizer_system_prompt() -> str:
    """Kategorize sistemi için sistem promptu"""
    return """Sen bir müşteri şikayeti kategorize uzmanısın.

Görevin şikayet metinlerini analiz edip doğru kategoriye yönlendirmek.

KURALLAR:
1. Sadece verilen kategorilerden birini seç
2. Şikayetin ana konusuna odaklan
3. Belirsiz durumlarda en yakın kategoriyi seç
4. Yanıtını JSON formatında ver
5. JSON dışında hiçbir açıklama ekleme

JSON FORMAT:
{
    "kategori": "kategori_adi",
    "guven_skoru": 0.95,
    "aciklama": "Kısa açıklama"
}
"""


def get_categorizer_user_prompt(complaint_text: str, categories: list) -> str:
    """
    Kategorize kullanıcı promptu

    Args:
        complaint_text: Şikayet metni
        categories: Mevcut kategoriler listesi

    Returns:
        Prompt metni
    """
    categories_str = ", ".join(categories)

    return f"""Şikayet Metni:
"{complaint_text}"

Mevcut Kategoriler:
{categories_str}

Bu şikayeti yukarıdaki kategorilerden birine ata.
Yanıtını JSON formatında ver."""


def get_fallback_category_prompt(complaint_text: str) -> str:
    """Kategori bulunamazsa genel kategori belirle"""
    return f"""Şikayet Metni:
"{complaint_text}"

Bu şikayetin ana konusunu tek kelime veya kısa ifade ile belirt.
Sadece kategori ismini döndür, başka açıklama ekleme.

Örnek yanıtlar:
- ATM
- Kredi Kartı
- Banka Hesabı
- Müşteri Hizmetleri
- Internet Bankacılığı
- Kredi
- Sigorta
"""


if __name__ == "__main__":
    # Test
    print("=== Sistem Promptu ===")
    print(get_categorizer_system_prompt())

    print("\n=== Kullanıcı Promptu ===")
    print(
        get_categorizer_user_prompt(
            "ATM'den param sıkıştı", ["ATM", "Kredi Kartı", "Banka Hesabı"]
        )
    )
