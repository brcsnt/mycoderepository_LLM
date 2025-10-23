# llm_handler.py

import os
import json

# --------------------------------------------------------------------
# --- SAHTE (MOCK) API ÇAĞRISI ---
# Gerçek uygulamada burayı kendi LLM API'nizle (Gemini, OpenAI vb.) doldurmalısınız.
# Bu sahte fonksiyon, API'ye para harcamadan demo yapabilmek içindir.
def llm_api_call(prompt):
    """
    LLM API'sine çağrı yapan sahte (mock) bir fonksiyon.
    """
    print("--- LLM ÇAĞRISI ---")
    print(f"PROMPT: {prompt}")

    # --- SAHTE (MOCK) CEVAPLAR ---
    if "KATEGORİLENDİRME VE İLK ÇIKARIM" in prompt:
        if "param sıkıştı" in prompt:
            # Modelin tam olarak bu formatta bir JSON string'i döndürmesini istiyoruz
            mock_response = {
                "category": "ATM_SORUNU",
                "extracted_data": {
                    "atm_lokasyonu": None,
                    "atm_problemi": "para sıkışması",
                    "atm_para_islem_miktarı": None
                }
            }
            return json.dumps(mock_response)
        
    if "VERİ ÇIKARIMI" in prompt:
        if "beykoz" in prompt:
            return "Beykoz"
        if "200 TL" in prompt:
            return "200 TL"
        if "akşam 5 gibi" in prompt:
            return "yaklaşık 17:00"

    # Varsayılan cevap
    return json.dumps({"category": "GENEL_BILGI", "extracted_data": {"talep_detayi": "Anlaşılamadı"}})
    # --- SAHTE CEVAPLARIN SONU ---

    # --- GERÇEK API ÇAĞRISI (ÖRNEK - örn: Google Gemini) ---
    # import google.generativeai as genai
    # genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    # model = genai.GenerativeModel('gemini-pro')
    # response = model.generate_content(prompt)
    # return response.text
    # --- GERÇEK API ÇAĞRISI SONU ---
# --------------------------------------------------------------------


def create_categorization_prompt(user_text, complaint_categories):
    """(Görev 1) Kategorizasyon ve İlk Çıkarım için prompt oluşturur."""
    
    system_prompt = f"""
SENARYO: Bir banka şikayet botu için arka uç LLM'sisin. Görevin, kullanıcıdan gelen ilk şikayet metnini analiz etmektir.
GÖREV:
1.  Metni en uygun kategoriye ata.
2.  Bu kategori için tanımlanan alanları (fields) kullanarak, metinden çıkarabildiğin kadar bilgiyi çıkar.
3.  Çıkaramadığın bilgilere "None" (Python'daki None) ata.
4.  Cevabını HER ZAMAN ve SADECE aşağıdaki gibi bir JSON formatında döndür:
    {{"category": "KATEGORI_ADI", "extracted_data": {{"alan1": "veri1", "alan2": None}} }}

KATEGORİLER VE ALANLAR:
"""
    # config'den kategorileri ve alanlarını alıp prompt'a ekliyoruz
    for category, data in complaint_categories.items():
        system_prompt += f"\nKategori: {category}\nAçıklama: {data['category_description']}\nAlanlar: {list(data['fields'].keys())}\n"

    final_prompt = f"""
{system_prompt}
---
İŞARET: KATEGORİLENDİRME VE İLK ÇIKARIM
KULLANICI METNİ: "{user_text}"
---
JSON ÇIKTISI:
"""
    return final_prompt

def analyze_initial_complaint(user_text, complaint_categories):
    """
    (Görev 1) İlk şikayet metnini alır, kategorize eder ve ilk veri çıkarımını yapar.
    Artık 'complaint_categories' parametresini alıyor.
    """
    prompt = create_categorization_prompt(user_text, complaint_categories)
    response_text = llm_api_call(prompt)

    try:
        # API'den gelen string JSON'u Python dict'e çevir
        result = json.loads(response_text)
        category = result.get("category")
        extracted_data = result.get("extracted_data")

        # Kategori bulunamazsa veya geçerli değilse
        if category not in complaint_categories:
            print(f"Hata: LLM'den geçersiz kategori alındı: {category}")
            category = "GENEL_BILGI" # Güvenli bir varsayılana dön
            
            # GENEL_BILGI kategorisinin config'de olduğundan emin ol
            if category not in complaint_categories:
                 # En kötü durum senaryosu
                 return "GENEL_BILGI", {"talep_detayi": user_text}

            extracted_data = complaint_categories[category]["fields"].copy()
            extracted_data["talep_detayi"] = user_text # Ham metni kaydet

        # Modelin, şablonda olmayan bir alan (halüsinasyon) döndürmediğinden emin ol
        valid_fields = complaint_categories[category]["fields"].keys()
        
        # Şablonu al (tüm değerler None)
        clean_data_template = complaint_categories[category]["fields"].copy()
        
        # Sadece şablondaki alanları LLM'den gelen veriyle güncelle
        if extracted_data:
            for key in valid_fields:
                if key in extracted_data and extracted_data[key] is not None:
                    clean_data_template[key] = extracted_data[key]
                
        return category, clean_data_template

    except json.JSONDecodeError as e:
        print(f"LLM yanıtı JSON formatında değil: {e}")
        print(f"Alınan yanıt: {response_text}")
        # En kötü durum senaryosu: hiçbir şey çıkarılamadı
        category = "GENEL_BILGI"
        if category in complaint_categories:
            data = complaint_categories[category]["fields"].copy()
            data["talep_detayi"] = user_text
        else:
            data = {"talep_detayi": user_text} # Fallback
        return category, data


def create_extraction_prompt(answer_text, field_name, question):
    """(Görev 2) Spesifik Veri Çıkarımı için prompt oluşturur."""
    return f"""
SENARYO: Kullanıcıya bir soru sordun ve bir cevap aldın.
GÖREV: Bu cevaptan SADECE istenen bilgiyi çıkar. Cevabı temizle ve normalize et.
Gereksiz kibarlık ifadelerini ("sanırım", "galiba", "ya") çıkar.
Eğer cevapta ilgili bilgi yoksa "None" döndür.
---
İŞARET: VERİ ÇIKARIMI
SORULAN SORU: "{question}"
İSTENEN BİLGİ ALANI: "{field_name}"
KULLANICININ CEVABI: "{answer_text}"
---
ÇIKARILAN BİLGİ:
"""

def extract_entity_from_answer(answer_text, field_name, question):
    """
    (Görev 2) Kullanıcının verdiği spesifik bir cevaptan
    ilgili veriyi çıkarmak için LLM'i kullanır.
    """
    prompt = create_extraction_prompt(answer_text, field_name, question)
    extracted_data = llm_api_call(prompt)

    if extracted_data is None or extracted_data.lower() == "none" or "çıkarılamadı" in extracted_data:
        return None
    
    # LLM cevabı JSON formatında dönerse (mock fonksiyonumuzdaki gibi)
    try:
        data = json.loads(extracted_data)
        return data # Veya data.get(field_name)
    except:
        # Eğer LLM sadece "Beykoz" gibi ham metin dönerse
        return extracted_data.strip().strip('"') # Tırnak işaretlerini temizle
