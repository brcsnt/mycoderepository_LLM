import streamlit as st
import os
import pandas as pd

# Uygulama Başlığı ve Açıklaması
st.title("PDF ve Keyword Seçim Uygulaması")
st.subheader("Klasördeki PDF dosyalarından birini seçin ve ardından Excel'deki keyword seçeneklerinden birini belirleyin.")
st.text("Bu uygulama, kullanıcıya bir PDF dosyası seçme ve daha sonra Excel'de belirtilen keyword seçenekleri arasında bir seçim yapma imkanı sunar.")

# PDF dosyalarının bulunduğu klasörün yolu
pdf_folder_path = "pdf_dosyaları"  # Bu kısmı kendi klasör yolunla değiştirmelisin

# Klasördeki PDF dosyalarını listeleyelim
pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith('.pdf')]

# Kullanıcıya PDF dosyaları arasından seçim yaptırma
selected_pdf = st.selectbox("Bir PDF dosyası seçin:", pdf_files)

# Seçilen PDF dosyasını ekrana yazdırma
st.write(f"Seçtiğiniz PDF: {selected_pdf}")

# Excel dosyasının yolu
excel_path = "veriler.xlsx"  # Excel dosyasının yolunu burada belirtmelisiniz

# Excel dosyasını okuyalım
df = pd.read_excel(excel_path)

# Keyword_type 1 ve 2 değerlerine göre filtreleyelim
keyword_type_1 = df[df['keyword_type'] == 1]['keyword'].tolist()
keyword_type_2 = df[df['keyword_type'] == 2]['keyword'].tolist()

# Kullanıcıya keyword_type 1 ve 2 seçeneklerini sunalım
option = st.radio("Keyword Type Seçimi:", ('Keyword Type 1', 'Keyword Type 2'))

# Seçilen keyword_type'a göre keyword'leri listeleyelim
if option == 'Keyword Type 1':
    selected_keyword = st.selectbox("Keyword Type 1'den bir Keyword seçin:", keyword_type_1)
else:
    selected_keyword = st.selectbox("Keyword Type 2'den bir Keyword seçin:", keyword_type_2)

# Seçilen keyword'ü ekrana yazdıralım
st.write(f"Seçtiğiniz Keyword: {selected_keyword}")
