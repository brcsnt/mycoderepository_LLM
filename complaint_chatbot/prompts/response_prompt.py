"""
Cevap işleme için prompt şablonları
"""


def get_normalizer_system_prompt() -> str:
    """Cevap normalize etme sistem promptu"""
    return """Sen bir metin normalizasyon uzmanısın.

Görevin kullanıcı cevaplarını temizlemek ve standart formata getirmek.

KURALLAR:
1. Gereksiz kelimeleri kaldır (tamam, sanırım, galiba, vb.)
2. Lokasyon isimleri için standart formata çevir
3. Tarih ve saatleri normalize et
4. Para miktarlarını sayı ve birim olarak ayır
5. Kısa ve öz yanıt ver
6. Sadece istenen bilgiyi döndür

Örnekler:
Girdi: "sanırım beykoz taraflarıydı"
Çıktı: "Beykoz"

Girdi: "200 TL sıkıştı ya"
Çıktı: "200 TL"

Girdi: "dün akşam saat 6 gibi"
Çıktı: "dün 18:00"
"""


def get_normalizer_user_prompt(user_response: str, field_name: str) -> str:
    """
    Normalize etme kullanıcı promptu

    Args:
        user_response: Kullanıcı yanıtı
        field_name: Alan adı

    Returns:
        Prompt metni
    """
    return f"""Alan: {field_name}
Kullanıcı Yanıtı: "{user_response}"

Bu yanıtı temizle ve normalize et. Sadece ana bilgiyi döndür.
Yanıtını JSON formatında ver:

{{"normalized_value": "temizlenmiş değer"}}
"""


def get_validation_prompt(value: str, field_name: str, field_description: str) -> str:
    """
    Değer doğrulama promptu

    Args:
        value: Doğrulanacak değer
        field_name: Alan adı
        field_description: Alan açıklaması

    Returns:
        Prompt metni
    """
    return f"""Alan: {field_name}
Açıklama: {field_description}
Değer: "{value}"

Bu değer alan için uygun mu? Değerlendir.

Yanıtını JSON formatında ver:
{{
    "valid": true/false,
    "reason": "açıklama",
    "suggestion": "önerilen düzeltme (varsa)"
}}
"""


if __name__ == "__main__":
    # Test
    print("=== Sistem Promptu ===")
    print(get_normalizer_system_prompt())

    print("\n=== Kullanıcı Promptu ===")
    print(get_normalizer_user_prompt("sanırım beykoz taraflarıydı", "atm_lokasyonu"))
