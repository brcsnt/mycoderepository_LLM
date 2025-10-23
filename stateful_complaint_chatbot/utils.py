"""
Utils Module
Yardımcı fonksiyonlar ve genel araçlar
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
import json


def generate_session_id() -> str:
    """
    Benzersiz oturum ID'si oluştur.

    Returns:
        Zaman damgası ve UUID kombinasyonu (örn: "20240315_143025_abc123")
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"


def find_null_fields(data: Dict[str, any]) -> List[str]:
    """
    Veri sözlüğünde None/null olan alanları bul.

    Args:
        data: Veri sözlüğü

    Returns:
        None olan alan adları listesi
    """
    null_fields = []
    for field, value in data.items():
        if value is None or value == "null" or value == "":
            null_fields.append(field)

    return null_fields


def format_data_for_display(data: Dict[str, any]) -> str:
    """
    Veriyi kullanıcıya gösterim için formatla.

    Args:
        data: Veri sözlüğü

    Returns:
        Formatlı string
    """
    lines = []
    for field, value in data.items():
        display_value = value if value is not None else "❌ Eksik"
        emoji = "✅" if value is not None else "❌"
        lines.append(f"{emoji} **{field}**: {display_value}")

    return "\n".join(lines)


def format_json_pretty(data: Dict[str, any]) -> str:
    """
    JSON'u güzel formatlı string'e dönüştür.

    Args:
        data: Veri sözlüğü

    Returns:
        Formatlı JSON string
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


def validate_field_value(value: any) -> bool:
    """
    Bir alanın değerinin geçerli olup olmadığını kontrol et.

    Args:
        value: Kontrol edilecek değer

    Returns:
        Geçerli ise True
    """
    if value is None:
        return False

    if isinstance(value, str):
        # Boş string, "null", "none" gibi değerler geçersiz
        cleaned = value.strip().lower()
        if cleaned in ["", "null", "none", "n/a", "yok", "bilmiyorum"]:
            return False

    return True


def clean_text(text: str) -> str:
    """
    Metni temizle (gereksiz boşluklar, özel karakterler vb.)

    Args:
        text: Ham metin

    Returns:
        Temizlenmiş metin
    """
    if not text:
        return ""

    # Başındaki ve sonundaki boşlukları temizle
    text = text.strip()

    # Çoklu boşlukları tek boşluğa indir
    import re
    text = re.sub(r'\s+', ' ', text)

    return text


def calculate_completion_percentage(data: Dict[str, any]) -> float:
    """
    Veri tamamlanma yüzdesini hesapla.

    Args:
        data: Veri sözlüğü

    Returns:
        Tamamlanma yüzdesi (0-100)
    """
    if not data:
        return 0.0

    total_fields = len(data)
    filled_fields = sum(1 for v in data.values() if validate_field_value(v))

    return (filled_fields / total_fields) * 100


def merge_data(base_data: Dict[str, any], new_data: Dict[str, any]) -> Dict[str, any]:
    """
    İki veri sözlüğünü birleştir. new_data içindeki değerler base_data'yı override eder.

    Args:
        base_data: Temel veri sözlüğü
        new_data: Yeni veri sözlüğü

    Returns:
        Birleştirilmiş veri sözlüğü
    """
    merged = base_data.copy()

    for key, value in new_data.items():
        # Sadece geçerli değerleri güncelle
        if validate_field_value(value):
            merged[key] = value

    return merged


def create_qa_list_entry(field_name: str, question: str, answer: str) -> Dict[str, str]:
    """
    Soru-cevap listesi için entry oluştur.

    Args:
        field_name: Alan adı
        question: Soru
        answer: Cevap

    Returns:
        Soru-cevap dict'i
    """
    return {
        "alan": field_name,
        "soru": question,
        "cevap": answer,
        "zaman": datetime.now().strftime("%H:%M:%S")
    }


def get_user_friendly_field_name(field_name: str) -> str:
    """
    Teknik alan adını kullanıcı dostu hale getir.

    Args:
        field_name: Teknik alan adı (örn: "atm_lokasyonu")

    Returns:
        Kullanıcı dostu ad (örn: "ATM Lokasyonu")
    """
    # Alt çizgileri boşluğa çevir
    friendly = field_name.replace("_", " ")

    # Her kelimenin ilk harfini büyüt
    friendly = friendly.title()

    return friendly


def estimate_time_remaining(questions_remaining: int, avg_time_per_question: float = 15.0) -> str:
    """
    Kalan süreyi tahmin et.

    Args:
        questions_remaining: Kalan soru sayısı
        avg_time_per_question: Soru başına ortalama süre (saniye)

    Returns:
        Tahmin edilen süre string'i (örn: "~30 saniye")
    """
    total_seconds = questions_remaining * avg_time_per_question

    if total_seconds < 60:
        return f"~{int(total_seconds)} saniye"
    else:
        minutes = int(total_seconds / 60)
        return f"~{minutes} dakika"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Uzun metinleri kısalt.

    Args:
        text: Metin
        max_length: Maksimum uzunluk

    Returns:
        Kısaltılmış metin
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


# Streamlit için renk ve emoji sabitleri
class UIConstants:
    """UI için sabitler"""

    # Emojiler
    EMOJI_SUCCESS = "✅"
    EMOJI_ERROR = "❌"
    EMOJI_WARNING = "⚠️"
    EMOJI_INFO = "ℹ️"
    EMOJI_QUESTION = "❓"
    EMOJI_ROBOT = "🤖"
    EMOJI_USER = "👤"
    EMOJI_COMPLETED = "🎉"
    EMOJI_IN_PROGRESS = "⏳"

    # Durumlar
    STAGE_INITIAL = "initial_complaint"
    STAGE_FOLLOW_UP = "follow_up"
    STAGE_COMPLETED = "completed"

    # Mesajlar
    MSG_WELCOME = "👋 Merhaba! Şikayetinizi dinlemek için buradayım."
    MSG_INITIAL_PROMPT = "Lütfen şikayetinizi detaylı bir şekilde yazın:"
    MSG_PROCESSING = "⏳ İşleniyor..."
    MSG_COMPLETED = "🎉 Şikayetiniz başarıyla kaydedildi!"


# Test için örnek kullanım
if __name__ == "__main__":
    # Test fonksiyonları
    print("=== Session ID ===")
    print(generate_session_id())

    print("\n=== Null Fields ===")
    test_data = {
        "alan1": "değer1",
        "alan2": None,
        "alan3": "değer3",
        "alan4": ""
    }
    print(find_null_fields(test_data))

    print("\n=== Completion Percentage ===")
    print(f"{calculate_completion_percentage(test_data)}%")

    print("\n=== Display Format ===")
    print(format_data_for_display(test_data))

    print("\n=== User Friendly Names ===")
    print(get_user_friendly_field_name("atm_lokasyonu"))
    print(get_user_friendly_field_name("musteri_tc_no"))

    print("\n=== Time Estimate ===")
    print(estimate_time_remaining(3))
    print(estimate_time_remaining(10))
