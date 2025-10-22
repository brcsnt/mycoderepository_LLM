"""
Excel template oluşturma scripti
Kategori, alan ve soru bilgilerini içeren Excel dosyası oluşturur
"""
import pandas as pd

# Örnek veri yapısı
data = [
    {
        "kategori": "ATM",
        "alan_adi": "atm_lokasyonu",
        "alan_aciklamasi": "ATM'nin bulunduğu lokasyon",
        "soru": "Problem yaşadığınız ATM lokasyonu nedir?"
    },
    {
        "kategori": "ATM",
        "alan_adi": "atm_problemi",
        "alan_aciklamasi": "ATM'de yaşanan problem türü",
        "soru": "ATM'de yaşadığınız sorun nedir?"
    },
    {
        "kategori": "ATM",
        "alan_adi": "atm_para_islem_miktari",
        "alan_aciklamasi": "İşlem yapılan para miktarı",
        "soru": "ATM'de ne kadar paranız sıkıştı veya işlem yapmaya çalıştınız?"
    },
    {
        "kategori": "ATM",
        "alan_adi": "tarih_saat",
        "alan_aciklamasi": "Olayın gerçekleştiği tarih ve saat",
        "soru": "Problem ne zaman gerçekleşti?"
    },
    {
        "kategori": "Kredi Kartı",
        "alan_adi": "kart_turu",
        "alan_aciklamasi": "Kredi kartının türü",
        "soru": "Hangi kredi kartınızla ilgili problem yaşıyorsunuz?"
    },
    {
        "kategori": "Kredi Kartı",
        "alan_adi": "problem_turu",
        "alan_aciklamasi": "Yaşanan problem türü",
        "soru": "Kredi kartınızla ilgili ne tür bir problem yaşıyorsunuz?"
    },
    {
        "kategori": "Kredi Kartı",
        "alan_adi": "islem_tutari",
        "alan_aciklamasi": "İşlem tutarı",
        "soru": "İşlem tutarı nedir?"
    },
    {
        "kategori": "Kredi Kartı",
        "alan_adi": "islem_yeri",
        "alan_aciklamasi": "İşlemin gerçekleştiği yer",
        "soru": "İşlemi nerede yaptınız?"
    },
    {
        "kategori": "Banka Hesabı",
        "alan_adi": "hesap_turu",
        "alan_aciklamasi": "Hesap türü (vadesiz, vadeli vb.)",
        "soru": "Hangi hesabınızla ilgili problem yaşıyorsunuz?"
    },
    {
        "kategori": "Banka Hesabı",
        "alan_adi": "problem_turu",
        "alan_aciklamasi": "Yaşanan problem türü",
        "soru": "Hesabınızla ilgili ne tür bir problem yaşıyorsunuz?"
    },
    {
        "kategori": "Banka Hesabı",
        "alan_adi": "islem_tutari",
        "alan_aciklamasi": "İşlem tutarı",
        "soru": "İşlem tutarı nedir?"
    },
    {
        "kategori": "Banka Hesabı",
        "alan_adi": "tarih",
        "alan_aciklamasi": "İşlem tarihi",
        "soru": "İşlem ne zaman gerçekleşti?"
    },
    {
        "kategori": "Müşteri Hizmetleri",
        "alan_adi": "iletisim_kanali",
        "alan_aciklamasi": "İletişim kanalı (telefon, şube vb.)",
        "soru": "Hangi kanaldan iletişime geçtiniz?"
    },
    {
        "kategori": "Müşteri Hizmetleri",
        "alan_adi": "problem_konusu",
        "alan_aciklamasi": "Problem konusu",
        "soru": "Müşteri hizmetleriyle ilgili ne tür bir problem yaşıyorsunuz?"
    },
    {
        "kategori": "Müşteri Hizmetleri",
        "alan_adi": "gorusme_tarihi",
        "alan_aciklamasi": "Görüşme tarihi",
        "soru": "Müşteri hizmetleriyle ne zaman görüştünüz?"
    },
    {
        "kategori": "Müşteri Hizmetleri",
        "alan_adi": "yetkili_adi",
        "alan_aciklamasi": "Görüşülen yetkili adı",
        "soru": "Görüştüğünüz yetkilinin adı nedir?"
    },
    {
        "kategori": "EFT/Havale",
        "alan_adi": "islem_turu",
        "alan_aciklamasi": "İşlem türü (EFT, havale, fast)",
        "soru": "Hangi tür para transferi yaptınız?"
    },
    {
        "kategori": "EFT/Havale",
        "alan_adi": "tutar",
        "alan_aciklamasi": "Transfer tutarı",
        "soru": "Transfer tutarı ne kadardı?"
    },
    {
        "kategori": "EFT/Havale",
        "alan_adi": "alici_bilgisi",
        "alan_aciklamasi": "Alıcı hesap bilgisi",
        "soru": "Para gönderdiğiniz hesap bilgisi nedir?"
    },
    {
        "kategori": "EFT/Havale",
        "alan_adi": "problem_turu",
        "alan_aciklamasi": "Yaşanan problem",
        "soru": "Transfer işlemiyle ilgili ne tür bir problem yaşıyorsunuz?"
    }
]

# DataFrame oluştur
df = pd.DataFrame(data)

# Excel'e kaydet
output_path = "categories_template.xlsx"
df.to_excel(output_path, index=False, sheet_name="Kategoriler")

print(f"✓ Excel template oluşturuldu: {output_path}")
print(f"✓ Toplam {len(df['kategori'].unique())} kategori")
print(f"✓ Toplam {len(df)} alan tanımı")
print("\nKategoriler:")
for kategori in df['kategori'].unique():
    alan_sayisi = len(df[df['kategori'] == kategori])
    print(f"  - {kategori}: {alan_sayisi} alan")
