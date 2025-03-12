import pdfplumber
import pandas as pd

all_tables = []  # Tüm sayfalardaki tabloları saklamak için liste

with pdfplumber.open("KAP.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        # Her sayfadaki tabloları çıkarıyoruz
        tables = page.extract_tables()
        for table in tables:
            # Eğer tablo başlık içeriyorsa, ilk satırı kolon isimleri olarak kullanıyoruz
            if len(table) > 1:
                df_table = pd.DataFrame(table[1:], columns=table[0])
                df_table['Sayfa'] = i + 1  # Hangi sayfadan geldiğini belirtiyoruz
                all_tables.append(df_table)

# Eğer herhangi bir tablo bulunduysa, tüm tabloları birleştiriyoruz
if all_tables:
    final_df = pd.concat(all_tables, ignore_index=True)
    excel_file = "KAP_data.xlsx"
    final_df.to_excel(excel_file, index=False)
    print(f"Excel dosyası '{excel_file}' oluşturuldu.")
else:
    print("PDF dosyasında tablo bulunamadı.")




import re
import pandas as pd
from pypdf import PdfReader

# PDF dosyasını açıp tüm sayfalardan metni çıkarıyoruz
reader = PdfReader("KAP.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# Kaydın genellikle bir rakamla başladığını varsayarsak, her kaydı ayırmak için:
records = re.split(r'\n(?=\d+\s)', full_text)
data = []
for rec in records:
    rec = rec.strip()
    if rec:
        # Kaydın tamamını tek bir alan olarak alıyoruz; daha detaylı ayrıştırma için ek düzenlemeler gerekir.
        data.append({"RawRecord": rec})

# DataFrame oluşturuluyor ve Excel'e yazılıyor.
df = pd.DataFrame(data)
excel_file = "KAP_data_pypdf.xlsx"
df.to_excel(excel_file, index=False)
print(f"Excel dosyası '{excel_file}' oluşturuldu.")




import pdfplumber
import re
import pandas as pd

# PDF'deki her bildirimi yakalamak için örnek regex (dosyanın yapısına göre uyarlanmalı)
# Bu örnekte, bildirimin "bildirim no", "tarih", "saat", "firma", "rapor tipi" ve "detay" kısımlarını ayırmayı hedefliyoruz.
pattern = re.compile(
    r"(?P<BildirimNo>\d+)\s+(?P<Tarih>\d{2}\.\d{2}\.\d{2})\s+(?P<Saat>\d{2}:\d{2})\s+(?P<Firma>(?:[A-ZÇĞİÖŞÜa-zçğıöşü0-9\s\.\-&/]+?))\s+(?P<RaporTipi>(?:DG Değerleme Raporu|ÖDA|Diğer Rapor Tipleri))\s+(?P<Detay>.*?)(?=\n\d+\s+\d{2}\.\d{2}\.\d{2}|\Z)",
    re.DOTALL
)

records = []

with pdfplumber.open("KAP.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        # Sayfadaki her eşleşmeyi bul
        for match in pattern.finditer(text):
            record = match.groupdict()
            # Gerekiyorsa alanlardan baştaki ve sondaki boşlukları temizle
            record = {k: v.strip() for k, v in record.items()}
            records.append(record)

# DataFrame oluşturma
df = pd.DataFrame(records)

# DataFrame'i görüntüleme
print(df)

