import pandas as pd

# Kayıtların tamamını içeren çok satırlı veriyi buraya yapıştırın.
raw_data = """\
388	03.01.24 23:26	RYGYO	REYSAŞ GAYRİMENKUL YATIRIM ORTAKLIĞI A.Ş.	DG	Değerleme Raporu	Konutlar ve Dükkanlar (İstanbul - Sancaktepe - Samandıra - 6650 - 17) F 2023 Yılsonu Değerleme Raporu	-	Ekli Dosya Mevcut
387	03.01.24 23:26	RYGYO	REYSAŞ GAYRİMENKUL YATIRIM ORTAKLIĞI A.Ş.	DG	Değerleme Raporu	Depo (Sakarya - Arifiye - Yukarıkirezce - 2587 - 46) 2023 Yılsonu Değerleme Raporu	-	Ekli Dosya Mevcut
... (diğer kayıtlar)
1	03.01.24 08:05	PGSUS	PEGASUS HAVA TAŞIMACILIĞI A.Ş.	ÖDA	Finansal Duran Varlık Edinimi	Yurt Dışında Bağlı Şirket Kuruluşu	-	"""

# Her satırı ayırıyoruz
rows = raw_data.strip().split("\n")

# Satırlardaki verileri sütunlarına göre bölüp, kayıt sözlüklerini oluşturuyoruz.
records = []
for row in rows:
    # Sütunlar tab (\t) karakteri ile ayrılmıştır.
    cols = row.split("\t")
    record = {
        "Sıra": cols[0].strip() if len(cols) > 0 else "",
        "Tarih": cols[1].strip() if len(cols) > 1 else "",
        "Kod": cols[2].strip() if len(cols) > 2 else "",
        "Şirket/Fon": cols[3].strip() if len(cols) > 3 else "",
        "Tip": cols[4].strip() if len(cols) > 4 else "",
        "İşlem": cols[5].strip() if len(cols) > 5 else "",
        "Açıklama": cols[6].strip() if len(cols) > 6 else "",
        "Ek": cols[7].strip() if len(cols) > 7 else "",
        "Ekli Dosya": cols[8].strip() if len(cols) > 8 else ""
    }
    records.append(record)

# DataFrame oluşturuluyor
df = pd.DataFrame(records)

# DataFrame'in ilk birkaç satırını görüntüleyelim
print(df.head())
