import config_info
from elastic_search_retriever_embedding import ElasticTextSearch

es = ElasticTextSearch()

# Kullanıcı sorusunda kampanya kodunun bulunması
def extract_campaign_code(query):
    """Metin içindeki kampanya kodunu çıkarır."""
    logger.debug(f"Extracting campaign code from query: {query}")
    
    # Convert the prompt to lowercase
    prompt = query.lower()
    
    # check for currency patterns
    currency_pattern = r"(\d+)\s*(tl|eur|usd|lira|dolar|euro)"
    match = re.search(currency_pattern, prompt)

    if match:
        prompt = prompt.replace(match.group(), "")
        match = re.search(currency_pattern, prompt)

    # check for year patterns
    year_pattern = r"(\d+)\s*(yılı|yılında|sene|senesinde|tarihinde|günü|gün)"
    year_matches = re.search(year_pattern, prompt)

    while year_matches:
        prompt = prompt.replace(year_matches.group(), "")
        year_matches = re.search(year_pattern, prompt)

    # find all 4 or 5-digit numbers and specific patterns in the prompt
    matches = re.findall(r"(\d{4,5})\s*(numaralı kampanya|kampanyasında|nolu kampanya|kodlu kampanya|kampanya|kampanyasının)", prompt)
    print(matches)

    # convert the matches to a list of strings
    matches = [match[0] for match in matches if match[0]]
    print(matches)

    # convert the strings to integers
    # print(numbers)

    if len(matches) == 0:  # if no matches are found, find 4 or 5 digit numbers
        pattern = r"(\d{4,5})"
        matches = re.findall(pattern, prompt)

        if len(matches) == 0:
            print("Lütfen kampanya kodunuzu girdiğinizden emin olun veya giriş bilgilerinizi kontrol edin.")
            return None
        else:
            return int(matches[0])  # return the first match

    return matches[0]  # return the first match


# OpenAI API Anahtarı
api_key = config_info.api_key
azure_api_key = config_info.azure_api_key
azure_api_version = config_info.azure_api_version
azure_endpoint = config_info.azure_endpoint
http_proxy = config_info.http_proxy
https_proxy = config_info.https_proxy
deployment_name = config_info.deployment_name

# OpenAI bağlantı bilgileri
def initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy):
    os.environ["HTTP_PROXY"] = http_proxy
    os.environ["HTTPS_PROXY"] = https_proxy

    openai.api_key = api_key
    client = AzureOpenAI(
        azure_api_key=azure_api_key,
        api_version=azure_api_version,
        azure_endpoint=azure_endpoint
    )

    return client

def generate_campaign_response(user_prompt, system_prompt=config_info.SYSTEM_PROMPT_MAIN_LAYER, campaign_description=None, deployment_name=config_info.deployment_name):
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy)
    
    # OpenAI API kullanarak metin üretir.
    # user_prompt: kullanıcı sorusu
    # system_prompt: sistem mesajı
    # campaign_description: kampanya metni
    
    rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metin içeriği: " + str(campaign_description)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": rag_prompt}
    ]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )

    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()


def generate_campaign_response_v2(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name):
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy)
    
    # OpenAI API kullanarak metin üretir.
    # user_prompt: kullanıcı sorusu
    # system_prompt: sistem mesajı
    # campaign_description: kampanya metni

    rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metin içeriği: " + str(campaign_description)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": rag_prompt}
    ]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )

    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()


# Streamlit state ile global memory saklama
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = deque(maxlen=3)


# Mesaj Ekleme Fonksiyonu
def add_message(user_input, response):
    """Sohbet geçmişine mesaj ekler (Yeni mesaj en üste gelir)."""
    st.session_state.chat_memory.appendleft({"user": user_input, "bot": response})  # Yeni mesaj en başa eklenir


# History'i ekrana formatlı yazdırma
def get_formatted_history():
    """Sohbet geçmişini zaman sırasına göre formatlı şekilde döndürür."""
    if not st.session_state.chat_memory:
        return "Sohbet geçmişi henüz boş."

    return "\n".join([f"Kullanıcı Sorusu: {msg['user']}\nBot Cevabı: {msg['bot']}" for msg in st.session_state.chat_memory])



def detect_query_type(user_input):
    """OpenAI Kullanarak kullanıcının genel bir arama mı yoksa spesifik bir kampanya hakkında mı konuştuğunu belirler."""
    system_prompt = """Kullanıcının mesajını analiz et:
    - Eğer genel bir kampanya arıyorsa GENEL_ARAMA anahtar kelimesi döndür. Örneğin: "Boyner kampanyaları", "İndirimli kampanyalar"
    - Eğer belirli bir kampanyada hakkında konuşuyorsa, kampanya başlığını döndür. (Örneğin: "Yılbaşı restoran kampanyasının bitiş tarihi nedir" -> "Yılbaşı restoran kampanyası")"""

    user_prompt = f"[system_prompt]\n\nKullanıcı Mesajı: {user_input}"
    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    deployment_name = config_info.deployment_name
    max_tokens = 250

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )

    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()


# Kullanıcının yeni sorusunun son mesaj ile ilgili olup olmadığını doğrulama
def check_follow_up_relevance(user_input, last_message):
    """
    Kullanıcının yeni sorusunun sohbet geçmişindeki son mesajla ilgili olup olmadığını kontrol eder.
    """

    system_prompt = """Kullanıcının sorusunu anla ve eğer önceki cevapta belirtilen kampanyalardan biriyle ilgiliyse hangi kampanya ile ilgili olduğunu belirle.
    - Eğer önceki kampanyalardan biriyle ilgiliyse **<kampanya_id>** şeklinde döndür.
    - Eğer önceki kampanyalardan biriyle ilgilisyse fakat kampanya başlığı bilinmiyorsa **kampanya başlık: <kampanya_baslik>** şeklinde döndür.
    - Eğer hiç alakası yoksa **NONE** döndür."""

    user_prompt = f"Önceki Mesaj: {last_message} \n\nKullanıcı Sorusu: {user_input}"

    client = initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    deployment_name = config_info.deployment_name
    max_tokens = 200

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )

    response_data = json.loads(response.to_json())
    return response_data["choices"][0]["message"]["content"].strip()



def process_user_input(user_input):
    """Her yeni kullanıcı mesajında sıfırdan başlar ve tüm akışı yönetir."""

    if user_input:
        with st.spinner("💭 Düşünüyorum..."):

            # 🔗 Kampanya kodu var mı?
            campaign_code = extract_campaign_code(user_input)

            # 📌 Eğer history boşsa (İlk mesaj ise) o zaman:
            if len(st.session_state.chat_memory) == 0:
                # Kampanya kodu varsa, ElasticSearch'ten kampanya bilgisi çek
                campaign_info = es.get_best_related(campaign_code)
                response = generate_campaign_response(user_input, campaign_description=campaign_info)
                add_message(user_input, response)  # Hafızaya ekle
                st.subheader(f"🔎 {campaign_code} Kampanyası Yanıt İçeriği")
                st.write(response)

            # 🕵️ Kullanıcının sorgu tipini analiz et
            query_type = detect_query_type(user_input)
            query_type = query_type.strip().lower()
            st.warning(f"🚨 Algılanan Sorgu Tipi : {query_type}")

            if query_type.lower().strip() == "genel_arama":
                search_result, formatted_result = es.search_campaign_by_header(user_input)
                add_message(user_input, formatted_result)
                st.subheader("🔎 Sorunuza En Yakın 3 Kampanya")
                st.write(formatted_result)

            elif query_type.lower().strip() == "genel_arama":
                # Kullanıcı belirli bir kampanya hakkında doğrudan sorduyysa
                campaign_info = es.search_campaign_by_header_one_result(query_type)
                response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
                add_message(user_input, response)
                st.warning(f"🚀 Arama yaptığın kampanya başlığı: {query_type}")
                st.subheader(f"📌 {query_type} Kampanyası Yanıt İçeriği")
                st.write(response)

            else:
                st.warning("Bu soruyu anlamadım. Lütfen farklı bir şekilde sormayı deneyin.")

            # ⏳ History dolayısıyla OpenAI’ye sorarak kullanıcının amacını analiz et
            formatted_history = get_formatted_history()
            follow_up_response = check_follow_up_relevance(user_input, last_message=formatted_history)
            st.warning(f"🔄 Follow-up response: {follow_up_response} ✅ (Debugging için eklendi)")

            # 🔍 1. Kullanıcı direkt kampanya kodu mu belirtti?
            if follow_up_response.lower().strip().startswith("kampanya kodu:"):
                campaign_code = follow_up_response.split(":")[1].strip()
                campaign_info = es.get_best_related(campaign_code)
                response = generate_campaign_response(user_input, campaign_description=campaign_info)
                add_message(user_input, response)
                st.subheader(f"📌 {campaign_code} Kampanyası Yanıt İçeriği")
                st.write(response)

            # 🔍 2. Kullanıcı kampanya adını mı belirtti?
            elif follow_up_response.lower().strip().startswith("kampanya başlık:"):
                campaign_title = follow_up_response.split(":")[1].strip()
                campaign_info = es.search_campaign_by_title(campaign_title)
                response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
                add_message(user_input, response)
                st.subheader(f"📌 {campaign_title} Kampanyası Yanıt İçeriği")
                st.write(response)

            # 🔍 3. Kullanıcının sorusu hiçbirine uymadı
            elif follow_up_response.lower() == "none":
                st.session_state.chat_memory.clear()
                st.warning("⚠️ Yeni bir konu başlatıldı, önceki konuşmalar silindi.")
                process_user_input(user_input)  # Süreci baştan başlat
                st.warning("Bu sorunun mevcut konu ile alakası yok.")

            # 🔍 4. Kullanıcı baştan yeni bir konu açtı, hafızayı sıfırla
            elif follow_up_response.lower() == "new query":
                st.session_state.chat_memory.clear()
                st.warning("⚠️ Yeni bir konu başlatıldı, önceki konuşmalar sıfırlandı.")
                process_user_input(user_input)  # Süreci baştan başlat

        # Sohbet geçmişini güncelle ve ekrana yazdır
        st.subheader("📖 Sohbet Geçmişi")
        st.write(get_formatted_history())

        # Eğer 3 mesaj olduysa sıfırla
        if len(st.session_state.chat_memory) >= 3:
            st.session_state.chat_memory.clear()
            st.warning("⚠️ Sohbet geçmişi dolduğu için sıfırlandı.")


# Streamlit Arayüzü
st.title("🤖 Kampanya Asistanı")
st.warning("📌 Lütfen kampanya ile ilgili sorularınızı girin")

user_input = st.text_input("Lütfen kampanya ile ilgili sorularınızı girin")

if user_input:
    process_user_input(user_input)



-------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------


def process_user_input(user_input):
    """Kullanıcının her yeni mesajında iş akışını belirler.

    Akış:
    1. Kullanıcı mesajında kampanya kodu aranır.
       - Eğer kampanya kodu varsa:
         • ElasticSearch’ten ilgili kampanya açıklaması alınır.
         • Kampanya açıklaması ile birlikte kullanıcı sorusuna cevap üretilir.
       - Eğer kampanya kodu yoksa:
         • Sohbet geçmişinde mesaj var mı kontrol edilir.
           - Eğer geçmiş boşsa:
               - Soru, genel arama mı yoksa spesifik kampanya mı belirlemek için analiz edilir.
                 • Genel arama ise: Top N kampanya başlığı ile sonuç getirilir.
                 • Spesifik kampanya ise: Top 1 sonuç alınır ve ilgili kampanya üzerinden cevaplanır.
           - Eğer geçmiş doluysa:
               - OpenAI ile kullanıcının sorusunun geçmişle (follow-up) ilişkisi sorgulanır.
                 • Eğer follow-up değilse yukarıdaki genel/spesifik akışa girer.
                 • Eğer follow-up ise; önceki mesajdaki kampanya kodu ya da kampanya başlığı kullanılarak akış tekrarlanır.
         • Ek olarak, eğer kullanıcı kampanyayı değiştirdiyse (örneğin follow-up “new query” ise) geçmiş sıfırlanır.
    """
    if not user_input:
        return

    with st.spinner("💭 Düşünüyorum..."):
        # 1. Adım: Kullanıcı mesajında kampanya kodu var mı?
        campaign_code = extract_campaign_code(user_input)

        if campaign_code is not None:
            # Kampanya kodu bulundu: ElasticSearch'ten kampanya açıklamasını getir.
            campaign_info = es.get_best_related(campaign_code)
            response = generate_campaign_response(user_input, campaign_description=campaign_info)
            add_message(user_input, response)
            st.subheader(f"🔎 {campaign_code} Kampanyası Yanıt İçeriği")
            st.write(response)

        else:
            # Kampanya kodu bulunamadı.
            if len(st.session_state.chat_memory) == 0:
                # Geçmiş boş: Soru tipi belirleniyor.
                query_type = detect_query_type(user_input).lower().strip()
                st.info(f"Algılanan Sorgu Tipi: {query_type}")

                if query_type == "genel_arama":
                    # Genel arama: Top N kampanya başlığı getir.
                    search_result, formatted_result = es.search_campaign_by_header(user_input)
                    add_message(user_input, formatted_result)
                    st.subheader("🔎 Sorunuza En Yakın Kampanyalar")
                    st.write(formatted_result)
                else:
                    # Spesifik kampanya adı: Top 1 sonuç getir.
                    campaign_info = es.search_campaign_by_header_one_result(user_input)
                    response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
                    add_message(user_input, response)
                    st.subheader(f"📌 {query_type} Kampanyası Yanıt İçeriği")
                    st.write(response)

            else:
                # Geçmiş dolu: Kullanıcının yeni mesajının önceki mesajla ilişkisini (follow-up) kontrol et.
                formatted_history = get_formatted_history()
                follow_up_response = check_follow_up_relevance(user_input, last_message=formatted_history).lower().strip()
                st.info(f"Follow-up Analizi: {follow_up_response}")

                if follow_up_response.startswith("kampanya kodu:"):
                    # Follow-up sonucunda kampanya kodu elde edildi.
                    campaign_code = follow_up_response.split(":", 1)[1].strip()
                    campaign_info = es.get_best_related(campaign_code)
                    response = generate_campaign_response(user_input, campaign_description=campaign_info)
                    add_message(user_input, response)
                    st.subheader(f"📌 {campaign_code} Kampanyası Yanıt İçeriği")
                    st.write(response)

                elif follow_up_response.startswith("kampanya başlık:"):
                    # Follow-up sonucunda kampanya başlığı elde edildi.
                    campaign_title = follow_up_response.split(":", 1)[1].strip()
                    campaign_info = es.search_campaign_by_title(campaign_title)
                    response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
                    add_message(user_input, response)
                    st.subheader(f"📌 {campaign_title} Kampanyası Yanıt İçeriği")
                    st.write(response)

                elif follow_up_response == "none":
                    # Follow-up olmadığı için, normal akışa geç:
                    query_type = detect_query_type(user_input).lower().strip()
                    st.info(f"Yeni Sorgu Tipi: {query_type}")

                    if query_type == "genel_arama":
                        search_result, formatted_result = es.search_campaign_by_header(user_input)
                        add_message(user_input, formatted_result)
                        st.subheader("🔎 Sorunuza En Yakın Kampanyalar")
                        st.write(formatted_result)
                    else:
                        campaign_info = es.search_campaign_by_header_one_result(user_input)
                        response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
                        add_message(user_input, response)
                        st.subheader(f"📌 {query_type} Kampanyası Yanıt İçeriği")
                        st.write(response)

                elif follow_up_response == "new query":
                    # Kullanıcı kampanyayı değiştirdiyse: geçmiş sıfırlanır ve süreç baştan başlatılır.
                    st.session_state.chat_memory.clear()
                    st.warning("⚠️ Yeni kampanya sorgusu algılandı, geçmiş sıfırlandı.")
                    process_user_input(user_input)
                    return  # Tekrar işlem yapıldığı için aşağıya inme.

        # Sohbet geçmişini ekrana yazdır.
        st.subheader("📖 Sohbet Geçmişi")
        st.write(get_formatted_history())

        # Eğer geçmiş 3 mesaja ulaştıysa sıfırlama yap.
        if len(st.session_state.chat_memory) >= 3:
            st.session_state.chat_memory.clear()
            st.warning("⚠️ Sohbet geçmişi dolduğu için sıfırlandı.")






-------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------



import re
import streamlit as st
from typing import Optional

def process_user_input(user_input: str) -> None:
    """Kullanıcının her yeni mesajında iş akışını belirler (Hata yönetimi ve iyileştirmelerle)."""
    if not user_input:
        st.warning("⚠️ Lütfen geçerli bir mesaj girin.")
        return

    # Sonsuz döngü koruması için retry sayacı
    if "retry_count" not in st.session_state:
        st.session_state.retry_count = 0

    with st.spinner("💭 Düşünüyorum..."):
        try:
            # 1. Adım: Kampanya kodu çıkarımı (Regex ile güçlendirilmiş)
            campaign_code = extract_campaign_code(user_input)
            
            if campaign_code:
                handle_campaign_code_flow(campaign_code, user_input)
            else:
                handle_no_campaign_code_flow(user_input)

            # Sohbet geçmişini yönet
            manage_chat_history()

        except Exception as e:
            st.error(f"⛔ Beklenmeyen hata: {str(e)}")
            log_error(e)  # Hata loglama fonksiyonu

def handle_campaign_code_flow(code: str, user_input: str) -> None:
    """Kampanya kodu bulunduğunda çalışan akış."""
    try:
        campaign_info = es.get_best_related(code)
        if not campaign_info:
            st.warning(f"⚠️ {code} kampanyası bulunamadı.")
            return

        response = generate_campaign_response(user_input, campaign_info)
        display_response(code, response, "🔎")
        add_message(user_input, response)

    except ElasticsearchError as e:
        st.error("🔌 ElasticSearch bağlantı hatası. Lütfen tekrar deneyin.")

def handle_no_campaign_code_flow(user_input: str) -> None:
    """Kampanya kodu yoksa çalışan akış."""
    if not st.session_state.chat_memory:
        handle_empty_history(user_input)
    else:
        handle_history_with_context(user_input)

def handle_empty_history(user_input: str) -> None:
    """Geçmiş boşsa sorgu tipini analiz et."""
    query_type = detect_query_type(user_input).lower().strip()
    
    # Sorgu tipi validasyonu
    if query_type not in ["genel_arama", "spesifik"]:
        query_type = "genel_arama"  # Fallback
        st.warning("⚠️ Sorgu tipi belirlenemedi, genel arama yapılıyor.")

    st.info(f"🔍 Algılanan Sorgu Tipi: {query_type}")
    
    if query_type == "genel_arama":
        search_and_display_top_n(user_input)
    else:
        search_and_display_top_1(user_input)

def handle_history_with_context(user_input: str) -> None:
    """Geçmiş doluysa bağlamı analiz et."""
    formatted_history = get_formatted_history()
    follow_up_response = check_follow_up_relevance(user_input, formatted_history).lower().strip()

    # Follow-up yanıtı format validasyonu
    if follow_up_response.startswith(("kampanya kodu:", "kampanya başlık:")):
        handle_follow_up_campaign(follow_up_response, user_input)
    elif follow_up_response == "new query":
        handle_new_query(user_input)
    else:
        handle_fallback_flow(user_input)

def handle_follow_up_campaign(response: str, user_input: str) -> None:
    """Follow-up kampanya bilgisi işleme."""
    try:
        if "kampanya kodu:" in response:
            code = response.split(":", 1)[1].strip()
            campaign_info = es.get_best_related(code)
            display_response(code, generate_response(...), "📌")
        else:
            title = response.split(":", 1)[1].strip()
            campaign_info = es.search_campaign_by_title(title)
            display_response(title, generate_response(...), "📌")
        
        add_message(user_input, response)
    except Exception as e:
        st.error("🔍 Kampanya bilgisi alınamadı. Lütfen farklı bir ifade deneyin.")

def handle_new_query(user_input: str) -> None:
    """Yeni sorgu durumu."""
    if st.session_state.retry_count < 3:
        st.session_state.chat_memory.clear()
        st.session_state.retry_count += 1
        st.warning("⚠️ Yeni sorgu algılandı, geçmiş sıfırlandı.")
        process_user_input(user_input)
    else:
        st.error("🔁 Maksimum yeniden deneme sayısına ulaşıldı. Lütfen yeni bir sorgu girin.")

def handle_fallback_flow(user_input: str) -> None:
    """Hiçbir koşula uymayan durumlar için."""
    st.warning("🤔 Tam olarak anlayamadım. Lütfen şu şekilde sorun:")
    st.markdown("- `XYZ kampanyası hakkında bilgi ver`")
    st.markdown("- `İndirimli ürünleri göster`")
    add_message(user_input, "Anlama hatası: Belirsiz sorgu")

def manage_chat_history() -> None:
    """Geçmiş yönetimi."""
    st.subheader("📖 Sohbet Geçmişi")
    st.write(get_formatted_history())
    
    # Geçmiş sıfırlama mantığı (3 mesaj yerine bağlama duyarlı)
    if len(st.session_state.chat_memory) >= 5:  # Daha esnek sınır
        st.session_state.chat_memory = st.session_state.chat_memory[-2:]  # Son 2 mesajı tut
        st.warning("⚠️ Sohbet bağlamı optimize edildi.")

# Yardımcı Fonksiyonlar --------------------------------------------------------

def extract_campaign_code(text: str) -> Optional[str]:
    """Gelişmiş regex ile kampanya kodu çıkarımı."""
    pattern = r"\b(?:KAMP|CMP|KY)[-_]?\d{3,}[A-Z]?\b"  # Örnek pattern: KAMP123, CMP-456A
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group().upper() if match else None

def display_response(title: str, content: str, icon: str) -> None:
    """Yanıtları standart formatta göster."""
    st.subheader(f"{icon} {title}")
    st.markdown(f"```\n{content}\n```")  # Okunabilir format

def log_error(error: Exception) -> None:
    """Hataları logla (Örnek implementasyon)."""
    with open("error_log.txt", "a") as f:
        f.write(f"{datetime.now()} - {str(error)}\n")








system_prompt = """# GÖREV
Kullanıcı mesajını aşağıdaki KURALLARA göre sınıflandır:

## KURALLAR
1. Eğer kullanıcı:
   - Genel kampanya listesi istiyorsa (Örnek: "kampanyalar", "indirimler")
   - Belirli kategori/kriter belirtmeden arıyorsa (Örnek: "En popüler kampanyalar")
   → "GENEL_ARAMA" döndür

2. Eğer kullanıcı:
   - Açıkça bir kampanya adı/başlığı belirtmişse (Örnek: "Yazlık giyim kampanyası detayları")
   - Kampanyaya özgü parametre soruyorsa (bitiş tarihi, kapsam vb.)
   → Kampanya başlığını TAM OLARAK şu formatta çıkar: "[ORIJINAL_MESAJDAKI_KAMPANYA_ADI]"

## ÇIKTI FORMATI
- YALNIZCA "GENEL_ARAMA" veya kampanya adını döndür. 
- Hiçbir ek açıklama yapma.

## ÖRNEKLER
Kullanıcı: "Boyner'deki elektronik kampanyaları göster"
Çıktı: "Elektronik kampanyaları"

Kullanıcı: "Son kampanyalar neler?"
Çıktı: "GENEL_ARAMA"
"""

system_prompt = """# GÖREV
Kullanıcının yeni sorusunu önceki mesajla ilişkilendir:

## KURALLAR
1. Önceki mesajda:
   - Kampanya kodu (Örnek: KAMP123) varsa → "kampanya kodu: [KOD]"
   - Kampanya başlığı listesi varsa → "kampanya başlık: [TAM_BASLIK]"
   - İlişki YOKSA → "new query"

2. Kampanya başlığı eşleştirme:
   - Kullanıcı "şu kampanya" diyorsa → listedeki İLK başlığı al
   - Sayısal referans varsa (Örnek: "3 numaralı kampanya") → Sırayla eşle

3. Belirsiz durumlarda → "new query"

## ÇIKTI FORMATI
AŞAĞIDAKİLERDEN BİRİNİ SEÇ:
- kampanya kodu: [ElasticSearch'teki_KOD]
- kampanya başlık: [TAM_BASLIK]
- new query

## ÖRNEKLER
Önceki Mesaj: "1. Yazlık İndirimler 2. Okula Dönüş"
Soru: "İlkinde % kaç indirim var?"
Çıktı: "kampanya başlık: Yazlık İndirimler"

Önceki Mesaj: "KAMP456: Elektronik Ürünlerde Fırsatlar"
Soru: "Bitiş tarihi ne zaman?"
Çıktı: "kampanya kodu: KAMP456"
"""


def detect_query_type(user_input: str) -> str:
    """Güçlendirilmiş sorgu tipi belirleme."""
    client = initialize_openai_client(...)
    
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Kullanıcı Mesajı: {user_input}"}
        ],
        temperature=0,
        max_tokens=50,  # Daha sıkı token sınırı
        stop=["\n"]  # İstenmeyen devam metinlerini engelle
    )
    
    raw_output = response.choices[0].message.content.strip()
    
    # Validasyon katmanı
    if raw_output == "GENEL_ARAMA":
        return raw_output
    else:
        # Kampanya başlığı format kontrolü
        if len(raw_output) > 60:  # Uzun metinleri kırp
            return "GENEL_ARAMA"
        return raw_output

def check_follow_up_relevance(user_input: str, last_message: str) -> str:
    """Optimize edilmiş bağlam takibi."""
    client = initialize_openai_client(...)
    
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Önceki Mesaj: {last_message}\n\nYeni Soru: {user_input}"}
        ],
        temperature=0,
        max_tokens=100,
        response_format={"type": "json_object"}  # JSON format zorlama
    )
    
    output = json.loads(response.choices[0].message.content)
    return output.get("decision", "new query")  # Fallback
