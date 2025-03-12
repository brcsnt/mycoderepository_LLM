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




import pdfplumber

with pdfplumber.open("KAP.pdf") as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        print(f"Sayfa {i} metni:\n{text}\n{'-'*40}\n")
        # İlk sayfayı kontrol etmek için döngüden çıkabilirsiniz
        if i == 1:
            break












import pdfplumber
import pandas as pd

# PDF'den tüm metni çekelim
all_text = ""
with pdfplumber.open("KAP.pdf") as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            all_text += page_text + "\n"

# Metni satırlara ayıralım
lines = all_text.splitlines()

# Tablo verilerini içerecek liste
data = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    parts = line.split()
    # Satırın ilk elemanı sayı ise ve ikinci eleman tarih formatına uygun ise (örneğin "03.01.24")
    if len(parts) >= 3 and parts[0].isdigit() and len(parts[1])==8 and ":" in parts[2]:
        # İlk satır: Bildirim No, Tarih, Saat
        bildirim_no = parts[0]
        tarih = parts[1]
        saat = parts[2]
        # İkinci satır: Firma ve Rapor Tipi (bu satırda genellikle her ikisi de bulunuyor)
        if i+1 < len(lines):
            firma_ve_rapor = lines[i+1].strip()
        else:
            firma_ve_rapor = ""
        # Eğer rapor tipi sabit bir ifade ise (örneğin "DG Değerleme Raporu") bu satırın sonunda yer alıyorsa,
        # onu ayırmak için örneğin şu şekilde bir kontrol yapabilirsiniz:
        rapor_tipi = ""
        if "DG Değerleme Raporu" in firma_ve_rapor:
            rapor_tipi = "DG Değerleme Raporu"
            # Firma kısmını, rapor tipini çıkartarak elde edebiliriz
            firma = firma_ve_rapor.replace("DG Değerleme Raporu", "").strip()
        else:
            firma = firma_ve_rapor
        # Üçüncü satırdan itibaren detayları toplayalım. Detaylar, "-" ya da boş satır görünceye kadar devam ediyor.
        detay = ""
        j = i+2
        while j < len(lines):
            current_line = lines[j].strip()
            if current_line == "-" or current_line == "":
                break
            detay += current_line + " "
            j += 1
        detay = detay.strip()
        # Bulunan satırı veri listesine ekleyelim
        data.append({
            "Bildirim No": bildirim_no,
            "Tarih": tarih,
            "Saat": saat,
            "Firma": firma,
            "Rapor Tipi": rapor_tipi,
            "Detay": detay
        })
        # Bir sonraki bildirime geçmek için index'i "-" bulunan satırın sonrasına ayarla
        i = j + 1
    else:
        i += 1

# Verilerden DataFrame oluşturalım
df = pd.DataFrame(data)
print(df)
