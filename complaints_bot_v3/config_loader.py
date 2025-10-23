# config_loader.py

import pandas as pd
import streamlit as st # Hata mesajlarını arayüzde göstermek için

def load_config_from_excel(excel_file, column_mapping):
    """
    Bir Excel dosyasını okur ve COMPLAINT_CATEGORIES formatında bir sözlük döndürür.
    
    Args:
        excel_file: Streamlit'ten yüklenen Excel dosyası objesi.
        column_mapping: Kullanıcının sütun adlarını bizim beklediğimiz adlara
                        eşleştiren bir sözlük.
                        Örn: {'category': 'Kategori_Adi', 'field': 'Alan_Kodu', 
                              'question': 'Sorusu', 'description': 'Kategori_Aciklamasi'}
    """
    
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        st.error(f"Excel dosyası okunamadı: {e}")
        return {}

    # Gerekli sütunların var olup olmadığını kontrol et
    required_cols = list(column_mapping.values())
    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel'de beklenen sütunlar bulunamadı. Aranan sütunlar: {required_cols}. Lütfen Excel'inizi veya yukarıdaki eşleştirme alanlarını kontrol edin.")
        return {}
        
    # Sütun adlarını bizim standart adlarımıza çevirelim
    # (Bu, sonraki işlemleri kolaylaştırır)
    reverse_mapping = {v: k for k, v in column_mapping.items()}
    df = df.rename(columns=reverse_mapping)

    config_dict = {}

    # Her kategoriyi gruplayarak sözlüğü oluştur
    # 'first()' kullanarak her grup için ilk açıklamayı alıyoruz (açıklamalar tekrar etmeli)
    for category_name, group in df.groupby('category'):
        
        fields = {}
        questions = {}
        
        for _, row in group.iterrows():
            field_name = str(row['field']) # Alan kodlarının string olduğundan emin ol
            field_question = str(row['question']) # Soruların string olduğundan emin ol
            
            # Alan adı veya soru boşsa o satırı atla
            if not field_name or pd.isna(field_name) or not field_question or pd.isna(field_question):
                continue
                
            fields[field_name] = None  # JSON şablonu için None olarak başlat
            questions[field_name] = field_question
            
        config_dict[category_name] = {
            "fields": fields,
            "questions": questions,
            "category_description": str(group['description
