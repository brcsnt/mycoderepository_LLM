import streamlit as st
import os
import pandas as pd
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Uygulama başlığı ve açıklaması
st.sidebar.title("PDF ve Keyword Seçim Uygulaması")
st.sidebar.info("Bu uygulama, PDF dosyasını seçme ve Excel'deki keyword seçeneklerinden birini belirleyip, PDF metninde en yakın parçaları bulma imkanı sunar.")

st.title("🔍 Metin Analizi ve Benzerlik Uygulaması")
st.write("Bu uygulama ile PDF dosyalarını analiz edebilir ve anahtar kelimelerle ilişkili metin parçalarını bulabilirsiniz.")

# PDF dosyasının yolunu tanımlama ve dosyaları listeleme
pdf_folder_path = "pdf_dosyaları"
try:
    pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith('.pdf')]
    if not pdf_files:
        st.sidebar.error("Klasörde PDF dosyası bulunamadı. Lütfen PDF dosyalarını kontrol edin.")
        st.stop()
except Exception as e:
    st.sidebar.error(f"PDF dosyaları yüklenirken bir hata oluştu: {e}")
    st.stop()

selected_pdf = st.sidebar.selectbox("Bir PDF dosyası seçin:", pdf_files)

# Excel dosyasını okuma
excel_path = "veriler.xlsx"
try:
    df = pd.read_excel(excel_path)
    if 'keyword' not in df.columns or 'keyword_type' not in df.columns:
        st.sidebar.error("Excel dosyasında gerekli kolonlar bulunamadı. 'keyword' ve 'keyword_type' kolonlarının mevcut olduğundan emin olun.")
        st.stop()
except Exception as e:
    st.sidebar.error(f"Excel dosyası yüklenirken bir hata oluştu: {e}")
    st.stop()

# Keyword_type 1 ve 2 seçeneklerini listeleme
keyword_type_1 = df[df['keyword_type'] == 1]['keyword'].tolist()
keyword_type_2 = df[df['keyword_type'] == 2]['keyword'].tolist()

# Kullanıcıya keyword_type seçeneklerini sunma
option = st.radio("Keyword Type Seçimi:", ('Keyword Type 1', 'Keyword Type 2'))

selected_keyword_type = option

# Seçilen keyword_type'a göre keyword'leri listeleme ve kontrol etme
if option == 'Keyword Type 1':
    if not keyword_type_1:
        st.warning("Keyword Type 1 için uygun anahtar kelime bulunamadı.")
        st.stop()
    selected_keyword = st.selectbox("Keyword Type 1'den bir Keyword seçin:", keyword_type_1)
else:
    if not keyword_type_2:
        st.warning("Keyword Type 2 için uygun anahtar kelime bulunamadı.")
        st.stop()
    selected_keyword = st.selectbox("Keyword Type 2'den bir Keyword seçin:", keyword_type_2)

# Kullanıcının top N sonucunu seçmesi
top_n = st.slider("Kaç adet en benzer sonucu görmek istersiniz?", min_value=1, max_value=10, value=5)
selected_top_n = top_n

# Seçilen keyword ve diğer bilgileri ekrana yazdıralım
st.success(f"Seçilen PDF: {selected_pdf}")
st.info(f"Seçilen Keyword Type: {selected_keyword_type}")
st.info(f"Seçilen Keyword: {selected_keyword}")
st.info(f"Top {selected_top_n} sonuç gösterilecek")

# PDF dosyasından metin okuma ve işlem yapma
if selected_pdf and selected_keyword:
    pdf_path = os.path.join(pdf_folder_path, selected_pdf)
    
    # PDF metnini okuma fonksiyonu
    def read_pdf(pdf_path):
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if not text.strip():
                raise ValueError("PDF'den metin çıkarılamadı. Dosyanın boş olmadığından emin olun.")
            return text
        except Exception as e:
            st.error(f"PDF dosyası okunurken bir hata oluştu: {e}")
            st.stop()

    # PDF metnini okuyalım
    pdf_text = read_pdf(pdf_path)

    # Metindeki gereksiz boşlukları temizleme
    cleaned_text = ' '.join(pdf_text.split())

    # RecursiveCharacterTextSplitter kullanarak metni parçalara ayıralım
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(cleaned_text)

    # Boş chunk'ları filtreleme
    chunks = [chunk for chunk in chunks if chunk.strip()]
    if not chunks:
        st.error("Metin parçalara ayrıldıktan sonra geçerli bir metin bulunamadı.")
        st.stop()

    # Sentence Transformer modelini yükleyelim
    model = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        # Chunk'ları embedding vektörlerine dönüştürme (2D formata dönüştürülür)
        chunk_embeddings = model.encode(chunks)
        if len(chunk_embeddings.shape) == 1:
            chunk_embeddings = chunk_embeddings.reshape(1, -1)

        # Keyword'ü embedding vektörüne dönüştürme (2D formata dönüştürülür)
        keyword_embedding = model.encode([selected_keyword]).reshape(1, -1)

        # Cosine similarity hesaplama
        similarities = cosine_similarity(keyword_embedding, chunk_embeddings).flatten()

        # Eğer similarity array boş veya hatalıysa durdur
        if len(similarities) == 0:
            st.error("Benzerlik hesaplanamadı. Lütfen PDF içeriğini ve seçilen keyword'ü kontrol edin.")
            st.stop()

        # En yüksek benzerlik skorlarını alalım
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        top_chunks = [chunks[i] for i in top_indices]
        top_scores = [similarities[i] for i in top_indices]

        # Sonuçları ekrana yazdırma
        st.subheader(f"En Benzer {top_n} Metin Parçası:")
        for i, (chunk, score) in enumerate(zip(top_chunks, top_scores), 1):
            st.write(f"### {i}. Parça (Skor: {score:.4f}):")
            st.write(chunk)
    except Exception as e:
        st.error(f"Embedding veya benzerlik hesaplama sırasında bir hata oluştu: {e}")
