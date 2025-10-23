"""
Config Template Excel Oluşturucu
Örnek konfigürasyon dosyası oluşturur
"""

import pandas as pd

# Örnek veri
data = [
    # ATM SORUNU kategorisi
    {
        "Kategori": "ATM_SORUNU",
        "Alan": "atm_lokasyonu",
        "Soru": "Problem yaşadığınız ATM'nin lokasyonu nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "ATM_SORUNU",
        "Alan": "atm_problemi",
        "Soru": "ATM'de yaşadığınız sorun nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "ATM_SORUNU",
        "Alan": "atm_para_islem_miktari",
        "Soru": "İşlem yapmaya çalıştığınız tutar nedir?",
        "Zorunlu": "Hayır"
    },
    {
        "Kategori": "ATM_SORUNU",
        "Alan": "atm_tarih_saat",
        "Soru": "Problemi ne zaman yaşadınız? (tarih ve saat)",
        "Zorunlu": "Hayır"
    },

    # KART SORUNU kategorisi
    {
        "Kategori": "KART_SORUNU",
        "Alan": "kart_tipi",
        "Soru": "Hangi kart ile ilgili sorun yaşıyorsunuz? (Banka kartı/Kredi kartı)",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "KART_SORUNU",
        "Alan": "kart_problemi",
        "Soru": "Kartınızla ilgili yaşadığınız sorun nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "KART_SORUNU",
        "Alan": "kart_son_dort_hane",
        "Soru": "Kartınızın son 4 hanesi nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "KART_SORUNU",
        "Alan": "kart_kullanim_yeri",
        "Soru": "Kartı nerede kullanmaya çalıştınız?",
        "Zorunlu": "Hayır"
    },

    # HESAP SORUNU kategorisi
    {
        "Kategori": "HESAP_SORUNU",
        "Alan": "hesap_tipi",
        "Soru": "Hangi hesap türü ile ilgili sorun yaşıyorsunuz? (Vadesiz/Vadeli/Mevduat)",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "HESAP_SORUNU",
        "Alan": "hesap_problemi",
        "Soru": "Hesabınızla ilgili yaşadığınız sorun nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "HESAP_SORUNU",
        "Alan": "hesap_islem_tutari",
        "Soru": "Sorun ile ilgili işlem tutarı var mı? Varsa ne kadar?",
        "Zorunlu": "Hayır"
    },
    {
        "Kategori": "HESAP_SORUNU",
        "Alan": "hesap_tarih",
        "Soru": "Sorunu ne zaman fark ettiniz?",
        "Zorunlu": "Hayır"
    },

    # MOBİL UYGULAMA SORUNU kategorisi
    {
        "Kategori": "MOBIL_UYGULAMA_SORUNU",
        "Alan": "uygulama_adi",
        "Soru": "Hangi mobil uygulama ile ilgili sorun yaşıyorsunuz?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "MOBIL_UYGULAMA_SORUNU",
        "Alan": "uygulama_problemi",
        "Soru": "Uygulamada yaşadığınız sorun nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "MOBIL_UYGULAMA_SORUNU",
        "Alan": "cihaz_tipi",
        "Soru": "Hangi cihazda sorun yaşıyorsunuz? (iOS/Android)",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "MOBIL_UYGULAMA_SORUNU",
        "Alan": "uygulama_versiyon",
        "Soru": "Uygulama versiyonu nedir?",
        "Zorunlu": "Hayır"
    },

    # HAVALE/EFT SORUNU kategorisi
    {
        "Kategori": "HAVALE_EFT_SORUNU",
        "Alan": "islem_tipi",
        "Soru": "İşlem türü nedir? (Havale/EFT/FAST)",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "HAVALE_EFT_SORUNU",
        "Alan": "islem_tutari",
        "Soru": "İşlem tutarı nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "HAVALE_EFT_SORUNU",
        "Alan": "alici_bilgisi",
        "Soru": "Alıcı IBAN veya hesap bilgisi nedir?",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "HAVALE_EFT_SORUNU",
        "Alan": "islem_durumu",
        "Soru": "İşlem durumu nedir? (Başarısız/Beklemede/Eksik)",
        "Zorunlu": "Evet"
    },
    {
        "Kategori": "HAVALE_EFT_SORUNU",
        "Alan": "islem_tarihi",
        "Soru": "İşlemi ne zaman gerçekleştirdiniz?",
        "Zorunlu": "Hayır"
    },
]

# DataFrame oluştur
df = pd.DataFrame(data)

# Excel'e kaydet
output_file = "config_template.xlsx"
df.to_excel(output_file, index=False, sheet_name="Config")

print(f"✅ Config template oluşturuldu: {output_file}")
print(f"📊 Toplam {len(df)} satır")
print(f"📋 Toplam {df['Kategori'].nunique()} kategori")
print("\nKategoriler:")
for cat in df['Kategori'].unique():
    count = len(df[df['Kategori'] == cat])
    print(f"  - {cat}: {count} alan")
