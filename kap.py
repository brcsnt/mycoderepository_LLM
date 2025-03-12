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
