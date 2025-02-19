

# MINO

import streamlit as st
import json
import os
from openai import AzureOpenAI
import config_info
from elastic_search_retriever_embedding import ElasticTextSearch

# Initialize session state for chat history
if 'history' not in st.session_state:
    st.session_state.history = []

es = ElasticTextSearch()

def initialize_openai_client():
    os.environ["HTTP_PROXY"] = config_info.http_proxy
    os.environ["HTTPS_PROXY"] = config_info.https_proxy

    return AzureOpenAI(
        api_key=config_info.azure_api_key,
        api_version=config_info.azure_api_version,
        azure_endpoint=config_info.azure_endpoint
    )

def post_process_campaign_response(json_response: str) -> dict:
    required_keys = [
        "campaign_code", "campaign_responsible_ask", "spesific_campaign_header",
        "general_campaign_header", "follow_up_campaign_code", "follow_up_campaign_header",
        "campaign_related", "pii_check_control"
    ]
    
    try:
        data = json.loads(json_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field: '{key}'")
    
    yes_no_fields = ["campaign_responsible_ask", "campaign_related", "pii_check_control"]
    for field in yes_no_fields:
        value = data[field].strip().upper()
        if value not in ["YES", "NO", ""]:
            raise ValueError(f"Invalid value for {field}: '{data[field]}'")
        data[field] = value

    return data

def generate_routing_response(user_prompt):
    client = initialize_openai_client()
    messages = [
        {"role": "system", "content": config_info.ROUTING_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat.completions.create(
        model=config_info.deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=config_info.max_tokens
    )
    
    return post_process_campaign_response(response.choices[0].message.content)

def generate_campaign_response(user_prompt, campaign_description):
    client = initialize_openai_client()
    messages = [
        {"role": "system", "content": config_info.SYSTEM_PROMPT_MAIN_LAYER},
        {"role": "user", "content": f"Soru: {user_prompt}\nKampanya Bilgisi: {campaign_description}"}
    ]
    
    response = client.chat.completions.create(
        model=config_info.deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=config_info.max_tokens
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🤖 Kampanya Asistanı")
st.warning("📌 Lütfen kampanya ile ilgili sorularınızı girin")

user_input = st.text_input("Lütfen kampanya ile ilgili sorularınızı girin")

if user_input:
    with st.spinner("💭 Düşünüyorum..."):
        try:
            parsed_data = generate_routing_response(user_input)
            response = None
            add_to_history = True

            # Condition handling
            if parsed_data['pii_check_control'] == 'YES':
                response = "Sorunuzda kişisel veri tespit ettim. Lütfen sorunuzu kontrol ediniz."
                add_to_history = False
            elif parsed_data['campaign_responsible_ask'] == 'YES':
                if parsed_data['campaign_code']:
                    resp = es.get_responsible_name_search_code(parsed_data['campaign_code'])
                    response = f"Kampanya sorumlusu: {resp}"
                elif parsed_data['spesific_campaign_header']:
                    resp = es.get_responsible_name_search_header(parsed_data['spesific_campaign_header'])
                    response = f"Kampanya sorumlusu: {resp}"
                add_to_history = False
            elif parsed_data['campaign_code']:
                info = es.get_best_related(parsed_data['campaign_code'])
                response = generate_campaign_response(user_input, info)
            elif parsed_data['spesific_campaign_header']:
                info = es.search_campaign_by_header_one_result(parsed_data['spesific_campaign_header'])
                response = generate_campaign_response(user_input, info)
            elif parsed_data['general_campaign_header']:
                info = es.search_campaign_by_header(parsed_data['general_campaign_header'])
                response = f"Genel arama sonuçları:\n{info}"
            elif parsed_data['follow_up_campaign_code']:
                info = es.get_best_related(parsed_data['follow_up_campaign_code'])
                response = generate_campaign_response(user_input, info)
            elif parsed_data['follow_up_campaign_header']:
                info = es.search_campaign_by_header_one_result(parsed_data['follow_up_campaign_header'])
                response = generate_campaign_response(user_input, info)
            elif parsed_data['campaign_related'] == 'YES':
                response = generate_campaign_response(user_input, "İlgili kampanya bilgileri")
            else:
                response = "Üzgünüm, bu soruya cevap veremiyorum."

            st.subheader("🔎 Yanıt")
            st.write(response)

            if add_to_history and response:
                new_entry = {
                    'user': user_input,
                    'bot': response
                }
                st.session_state.history.insert(0, new_entry)
                st.session_state.history = st.session_state.history[:3]

        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

if st.session_state.history:
    st.subheader("📖 Sohbet Geçmişi")
    for idx, entry in enumerate(st.session_state.history):
        prefix = "Son" if idx == 0 else f"Sondan {['ikinci', 'üçüncü'][idx-1]}"
        st.markdown(f"**{prefix} soru:** {entry['user']}")
        st.markdown(f"**{prefix} yanıt:** {entry['bot']}")
        st.write("---")

















# DDD



import os
import json
import openai
import streamlit as st
from elastic_search_retriever_embedding import ElasticTextSearch
import config_info

# Global ayarlar
max_tokens = 150
ROUTING_PROMPT = """ 
Lütfen aşağıdaki formatta JSON çıktısı üret:
{
    "campaign_code": "",
    "campaign_responsible_ask": "",
    "spesific_campaign_header": "",
    "general_campaign_header": "",
    "follow_up_campaign_code": "",
    "follow_up_campaign_header": "",
    "campaign_related": "",
    "pii_check_control": ""
}
Kurallara göre:
- campaign_responsible_ask, campaign_related ve pii_check_control sadece "YES", "NO" veya boş olabilir.
"""

# Streamlit session state üzerinden sohbet geçmişini tutmak için:
if 'history' not in st.session_state:
    st.session_state.history = []


def update_history(user_question: str, bot_response: str):
    """
    Sohbet geçmişine yeni bir kullanıcı-sistem çiftini ekler.
    Eğer güncel mesaj pii_check_control veya campaign_responsible_ask YES ise eklenmez.
    Sadece son 3 mesaj saklanır.
    """
    st.session_state.history.append({
        "user_question": user_question,
        "bot_response": bot_response
    })
    # Sadece son 3 mesajı tut
    if len(st.session_state.history) > 3:
        st.session_state.history = st.session_state.history[-3:]


def get_formatted_history() -> str:
    """
    Sohbet geçmişini istenen formatta (en son mesaj en üstte) formatlar.
    """
    history = st.session_state.history
    formatted_lines = []
    n = len(history)
    if n >= 1:
        conv = history[-1]
        formatted_lines.append("Kullanıcının son sorusu:")
        formatted_lines.append(conv["user_question"])
        formatted_lines.append("Kullanıcının son sorusunun cevabı:")
        formatted_lines.append(conv["bot_response"])
    if n >= 2:
        conv = history[-2]
        formatted_lines.append("Kullanıcının sondan ikinci sorusu:")
        formatted_lines.append(conv["user_question"])
        formatted_lines.append("Kullanıcının sondan ikinci sorusunun cevabı:")
        formatted_lines.append(conv["bot_response"])
    if n >= 3:
        conv = history[-3]
        formatted_lines.append("Kullanıcının sondan üçüncü sorusu:")
        formatted_lines.append(conv["user_question"])
        formatted_lines.append("Kullanıcının sondan üçüncü sorusunun cevabı:")
        formatted_lines.append(conv["bot_response"])
    return "\n".join(formatted_lines)


def post_process_campaign_response(json_response: str) -> dict:
    """
    OpenAI'dan gelen JSON yanıtını parse edip, gerekli alanları kontrol eder.
    """
    required_keys = [
        "campaign_code",
        "campaign_responsible_ask",
        "spesific_campaign_header",
        "general_campaign_header",
        "follow_up_campaign_code",
        "follow_up_campaign_header",
        "campaign_related",
        "pii_check_control"
    ]
    
    try:
        data = json.loads(json_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field in JSON response: '{key}'")
    
    yes_no_fields = [
        "campaign_responsible_ask",
        "campaign_related",
        "pii_check_control"
    ]
    for field in yes_no_fields:
        value = data[field].strip().upper()
        if value not in ["YES", "NO", ""]:
            raise ValueError(
                f"Field '{field}' must be 'YES', 'NO', or an empty string. Got: '{data[field]}'"
            )
        data[field] = value  # Normalize
        
    return data


def initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy):
    """
    OpenAI (Azure OpenAI) istemcisini yapılandırır.
    """
    os.environ["HTTP_PROXY"] = http_proxy
    os.environ["HTTPS_PROXY"] = https_proxy

    openai.api_key = api_key
    # AzureOpenAI sınıfının import edildiğini varsayıyoruz.
    client = AzureOpenAI(
        azure_api_key=azure_api_key,
        api_version=azure_api_version,
        azure_endpoint=azure_endpoint
    )

    return client


def generate_routing_response(user_prompt, system_prompt=ROUTING_PROMPT, deployment_name=config_info.deployment_name) -> dict:
    """
    Kullanıcının sorusunu routing prompt üzerinden OpenAI API ile yönlendirir ve 
    JSON yanıtı parse edip döndürür.
    """
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
       
    routing_response_text = "Verilen talimatalara uygun olarak soruya cevap ver: " + user_prompt 

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": routing_response_text}
    ]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )

    # API'den gelen yanıtı JSON string olarak alıp, parse ediyoruz.
    response_data = response.to_json()
    # post_process_campaign_response fonksiyonu string formatında JSON beklediğinden;
    processed_data = post_process_campaign_response(response_data)
    return processed_data


def generate_campaign_response(user_prompt, system_prompt=config_info.SYSTEM_PROMPT_MAIN_LAYER, campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def generate_campaign_response_v2(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def generate_campaign_response_v3(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def generate_campaign_response_v4(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def process_user_input(user_input: str) -> str:
    """
    Kullanıcının sorusunu önce routing response üzerinden yönlendirir,
    ardından ilgili iş akışına göre doğru fonksiyonu çalıştırır.
    """
    routing_data = generate_routing_response(user_input, system_prompt=ROUTING_PROMPT)
    
    campaign_code = routing_data.get("campaign_code", "").strip()
    campaign_responsible_ask = routing_data.get("campaign_responsible_ask", "").strip().upper()
    spesific_campaign_header = routing_data.get("spesific_campaign_header", "").strip()
    general_campaign_header = routing_data.get("general_campaign_header", "").strip()
    follow_up_campaign_code = routing_data.get("follow_up_campaign_code", "").strip()
    follow_up_campaign_header = routing_data.get("follow_up_campaign_header", "").strip()
    campaign_related = routing_data.get("campaign_related", "").strip().upper()
    pii_check_control = routing_data.get("pii_check_control", "").strip().upper()
    
    response = ""
    add_to_history = True  # Varsayılan olarak geçmişe eklensin

    if pii_check_control == "YES":
        response = "sorunuzda kişisel veri tespit ettim lütfen sorunuzu kontrol ediniz."
        add_to_history = False
    elif campaign_code and campaign_responsible_ask == "YES":
        es = ElasticTextSearch()
        campaign_responsible = es.get_responsible_name_search_code(campaign_code)
        response = f"kampanyadan sorumlu kişi {campaign_responsible}"
        add_to_history = False
    elif campaign_code and campaign_responsible_ask == "NO":
        es = ElasticTextSearch()
        campaign_info = es.get_best_related(campaign_code)
        response = generate_campaign_response(user_input, campaign_description=campaign_info)
    elif spesific_campaign_header and campaign_responsible_ask == "YES":
        es = ElasticTextSearch()
        campaign_responsible = es.get_responsible_name_search_header(spesific_campaign_header)
        response = f"kampanyadan sorumlu kişi {campaign_responsible}"
        add_to_history = False
    elif spesific_campaign_header and campaign_responsible_ask == "NO":
        es = ElasticTextSearch()
        campaign_info = es.search_campaign_by_header_one_result(spesific_campaign_header)
        response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
    elif general_campaign_header:
        es = ElasticTextSearch()
        campaign_info = es.search_campaign_by_header(general_campaign_header)
        response = f"Yaptığınız genel aramaya göre aşağıdaki sonuçlar bulunmuştur: {campaign_info}"
    elif follow_up_campaign_code:
        es = ElasticTextSearch()
        campaign_info = es.get_best_related(follow_up_campaign_code)
        response = generate_campaign_response_v3(user_input, system_prompt=get_formatted_history(), campaign_description=campaign_info)
    elif follow_up_campaign_header:
        es = ElasticTextSearch()
        campaign_info = es.search_campaign_by_header_one_result(follow_up_campaign_header)
        response = generate_campaign_response_v3(user_input, system_prompt=get_formatted_history(), campaign_description=campaign_info)
    elif campaign_related == "YES":
        response = generate_campaign_response_v4(user_input, system_prompt=get_formatted_history(), campaign_description=None)
    else:
        response = "Lütfen geçerli kampanya bilgileri giriniz."

    if add_to_history:
        update_history(user_input, response)
        
    return response


# Streamlit arayüzü
st.title("🤖 Kampanya Asistanı")
st.warning("📌 Lütfen kampanya ile ilgili sorularınızı girin")

user_input = st.text_input("Lütfen kampanya ile ilgili sorularınızı girin")

if user_input:
    with st.spinner("💭 Düşünüyorum..."):
        answer = process_user_input(user_input)
    st.subheader("🔎 Yanıt")
    st.write(answer)
    st.subheader("📖 Sohbet Geçmişi")
    st.write(get_formatted_history())




















def post_process_campaign_response(json_response: str) -> dict:
    """
    Parses and validates the JSON response from the Campaign Routing Chatbot.
    
    :param json_response: A JSON string matching the chatbot's strict format.
    :return: A Python dictionary containing the parsed and validated data.
    :raises ValueError: If the JSON is invalid or required fields are missing.
    """
    # Required keys per the prompt
    required_keys = [
        "campaign_code",
        "campaign_responsible_ask",
        "spesific_campaign_header",
        "general_campaign_header",
        "follow_up_campaign_code",
        "follow_up_campaign_header",
        "campaign_related",
        "pii_check_control"
    ]
    
    try:
        # Parse the JSON string
        data = json.loads(json_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    # Validate that all required fields exist
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field in JSON response: '{key}'")
    
    # Optional: You can add further validations or transformations here.
    # For instance, ensuring "YES" or "NO" are the only allowed values for certain fields:
    yes_no_fields = [
        "campaign_responsible_ask",
        "campaign_related",
        "pii_check_control"
    ]
    for field in yes_no_fields:
        value = data[field].strip().upper()
        if value not in ["YES", "NO", ""]:
            raise ValueError(
                f"Field '{field}' must be 'YES', 'NO', or an empty string. Got: '{data[field]}'"
            )
        data[field] = value  # Normalize to uppercase if you want consistency

    # Return the validated dictionary
    return data













POWERFULL_ROUTING_PROMPT = """ 

**Role**: You are **CampaignRoutingBot**, a specialized chatbot designed to handle and **route** user questions about campaigns. Think of yourself as the “routing center” for campaign-related inquiries: you analyze the user’s **Turkish** question and decide how to handle it by returning a structured JSON output that adheres to specific fields.


### **Purpose**:
1. **Identify** whether the user’s Turkish query includes a campaign code, a specific campaign header, or a general campaign reference.  
2. **Determine** if the user’s query is a follow-up from previous messages.  
3. **Ensure** the chatbot flags any personal data violations.  
4. **Return** a **strict JSON** in **Turkish** that captures these findings.

### **Behavior**:
- You must **always** respond in **Turkish**.  
- You act as a **router** for campaign inquiries, categorizing the user’s question and populating the JSON fields accurately.  
- You do **not** add or remove JSON fields, and you do **not** provide any extra text or formatting outside the JSON.

---

### **Instructions**:

1. **Detect a Campaign Code**  
   - A valid campaign code is a **5, 6, or 7-digit integer** (e.g., 12345, 123456, 1234567).  
   - If found, store it in `"campaign_code"`.  
   - Check if the user asks about the campaign responsible. Return `"YES"` or `"NO"` in `"campaign_responsible_ask"` (in Turkish).  

   ```json
   "campaign_code": "campaign_code_name",
   "campaign_responsible_ask": "YES or NO"
   ```

2. **Detect a Specific Campaign Header**  
   - If the user refers to a specific campaign (e.g., “Ramazan Kampanyası”), return that in `"spesific_campaign_header"`.  
   - Also check if they ask for the campaign responsible (`"campaign_responsible_ask": "YES"` or `"NO"`).  

   ```json
   "spesific_campaign_header": "campaign_header_name",
   "campaign_responsible_ask": "YES or NO"
   ```

3. **Detect a General Campaign Query**  
   - If the user wants general info (e.g., “Migros kampanyaları nelerdir?”), put that phrase in `"general_campaign_header"`.  

   ```json
   "general_campaign_header": "general_campaign_name"
   ```

4. **Check for Follow-Up**  
   - If the user’s message follows up on a **previous** campaign discussion (last 3 messages), detect the **campaign code** or **campaign header** from the history.
   - If conversation history is provided, it will be appended at the bottom of this prompt. When evaluating, consider the information under that history heading to determine the follow-up details.
   - Fill `"follow_up_campaign_code"` or `"follow_up_campaign_header"` accordingly.  

   ```json
   "follow_up_campaign_code": "",
   "follow_up_campaign_header": ""
   ```

5. **Determine if the Question is Related to Campaigns**  
   - **If the user’s question does not contain a campaign code, does not contain any general or specific campaign header, and is definitely not a follow-up, yet you still believe it is related to campaigns,** set `"campaign_related"` to `"YES"`.  
   - **If it is absolutely not about campaigns, or you do not understand the user’s intent, and you are certain it has nothing to do with campaigns,** set `"campaign_related"` to `"NO"`.  

   ```json
   "campaign_related": "YES or NO"
   ```

6. **Check for Personal Data Violation** (Kişisel Veri İhlali)  
   - If there is personal data (e.g., phone number, ID, etc.), set `"pii_check_control"` to `"YES"`. Otherwise, `"NO"`.  

   ```json
   "pii_check_control": "YES or NO"
   ```

**All** textual values must be in **Turkish** (“YES” or “NO” in uppercase, or exact campaign names).  
**Never** output anything outside the JSON.  
If a field does not apply, leave it as an empty string `""`.

---

### **Output Format (Strict JSON)**

Always respond with a **single JSON object** containing **exactly** these keys:

```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "",
  "spesific_campaign_header": "",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "campaign_related": "",
  "pii_check_control": ""
}
```

- No additional text or fields.  
- All values in **Turkish**.  
- Empty string if not applicable.

---

## **Few-Shot Examples**

Below are some examples of user inputs (in Turkish) and the **only** valid JSON outputs you should produce. Always keep your answers in **Turkish**.

---

### **Example 1**

**User Input**:  
> “Merhaba, 123456 kodlu kampanyanın sorumlusu kim acaba?”

**Analysis**:  
- Campaign code: `123456`  
- Asks for the campaign responsible → `"YES"`  
- No personal data violation → `"NO"`  
- Definitely campaign-related → `"YES"`  

**Output**:
```json
{
  "campaign_code": "123456",
  "campaign_responsible_ask": "YES",
  "spesific_campaign_header": "",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "campaign_related": "YES",
  "pii_check_control": "NO"
}
```

---

### **Example 2**

**User Input**:  
> “Ramazan İndirimi kampanyası var mı, detayları nedir?”

**Analysis**:  
- No numeric code  
- Specific campaign header: “Ramazan İndirimi”  
- Not asking for responsible → `"NO"`  
- No personal data violation → `"NO"`  
- Campaign-related → `"YES"`  

**Output**:
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "spesific_campaign_header": "Ramazan İndirimi",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "campaign_related": "YES",
  "pii_check_control": "NO"
}
```

---

### **Example 3**

**User Input**:  
> “Migros kampanyaları hakkında bilgi verir misin?”

**Analysis**:  
- No numeric code  
- No specific campaign header  
- General campaign query: “Migros kampanyaları”  
- No personal data violation → `"NO"`  

**Output**:
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "spesific_campaign_header": "",
  "general_campaign_header": "Migros kampanyaları",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "campaign_related": "YES",
  "pii_check_control": "NO"
}
```

---

### **Example 4**

**User Input**:  
> “Bir önceki konuşmada bahsettiğim 98765 kodlu kampanyaya devam edelim.”

**Analysis**:  
- 5-digit campaign code: `98765`  
- Possibly a follow-up → `"follow_up_campaign_code": "98765"`  
- Not asking for responsible → `"NO"`  

**Output**:
```json
{
  "campaign_code": "98765",
  "campaign_responsible_ask": "NO",
  "spesific_campaign_header": "",
  "general_campaign_header": "",
  "follow_up_campaign_code": "98765",
  "follow_up_campaign_header": "",
  "campaign_related": "YES",
  "pii_check_control": "NO"
}
```

---

### **Example 5**

**User Input**:  
> “Telefon numarası paylaşır mısınız? 555 123 4567”

**Analysis**:  
- No campaign code  
- No specific or general campaign header  
- Not a follow-up  
- Likely not campaign-related → `"NO"`  
- Personal data violation → `"YES"`  

**Output**:
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "spesific_campaign_header": "",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "campaign_related": "NO",
  "pii_check_control": "YES"
}
```
"""


































import os
import json
import openai
import streamlit as st
from elastic_search_retriever_embedding import ElasticTextSearch
import config_info

# Varsayılan max token sayısı
DEFAULT_MAX_TOKENS = 150

# Routing prompt tanımı
ROUTING_PROMPT = """ 
Lütfen aşağıdaki formatta JSON çıktısı üret:
{
    "campaign_code": "",
    "campaign_responsible_ask": "",
    "spesific_campaign_header": "",
    "general_campaign_header": "",
    "follow_up_campaign_code": "",
    "follow_up_campaign_header": "",
    "campaign_related": "",
    "pii_check_control": ""
}
Kurallara göre:
- campaign_responsible_ask, campaign_related ve pii_check_control sadece "YES", "NO" veya boş olabilir.
"""

class CampaignAssistant:
    def __init__(self):
        """
        Kampanya Asistanı için gerekli konfigürasyon ve başlangıç ayarlarını yapar.
        - config_info modülündeki ayarlar kullanılır.
        - Sohbet geçmişi (history) Streamlit session state üzerinden tutulur.
        """
        self.config = config_info
        self.max_tokens = DEFAULT_MAX_TOKENS
        self.routing_prompt = ROUTING_PROMPT

        # Streamlit session_state üzerinden sohbet geçmişini başlatıyoruz.
        if "history" not in st.session_state:
            st.session_state.history = []
        self.history = st.session_state.history

    def update_history(self, user_question: str, bot_response: str, add_to_history: bool = True):
        """
        Kullanıcı ve sistem (bot) mesajlarını sohbet geçmişine ekler.
        Eğer add_to_history False ise, mesaj geçmişine ekleme yapılmaz.
        Sadece son 3 mesajı saklar.
        """
        if not add_to_history:
            return

        self.history.append({
            "user_question": user_question,
            "bot_response": bot_response
        })

        # Yalnızca son 3 mesajı saklayacak şekilde güncelle
        if len(self.history) > 3:
            self.history = self.history[-3:]
        st.session_state.history = self.history

    def get_formatted_history(self) -> str:
        """
        Sohbet geçmişini, istenen formatta (en son mesaj en üstte olacak şekilde) metin olarak döndürür.
        """
        formatted_lines = []
        n = len(self.history)
        if n >= 1:
            conv = self.history[-1]
            formatted_lines.append("Kullanıcının son sorusu:")
            formatted_lines.append(conv["user_question"])
            formatted_lines.append("Kullanıcının son sorusunun cevabı:")
            formatted_lines.append(conv["bot_response"])
        if n >= 2:
            conv = self.history[-2]
            formatted_lines.append("Kullanıcının sondan ikinci sorusu:")
            formatted_lines.append(conv["user_question"])
            formatted_lines.append("Kullanıcının sondan ikinci sorusunun cevabı:")
            formatted_lines.append(conv["bot_response"])
        if n >= 3:
            conv = self.history[-3]
            formatted_lines.append("Kullanıcının sondan üçüncü sorusu:")
            formatted_lines.append(conv["user_question"])
            formatted_lines.append("Kullanıcının sondan üçüncü sorusunun cevabı:")
            formatted_lines.append(conv["bot_response"])
        return "\n".join(formatted_lines)

    def post_process_campaign_response(self, json_response: str) -> dict:
        """
        OpenAI'dan gelen JSON yanıtını parse eder ve zorunlu alanların varlığını kontrol eder.
        Hatalı formatlarda ValueError fırlatır.
        """
        required_keys = [
            "campaign_code",
            "campaign_responsible_ask",
            "spesific_campaign_header",
            "general_campaign_header",
            "follow_up_campaign_code",
            "follow_up_campaign_header",
            "campaign_related",
            "pii_check_control"
        ]
        try:
            data = json.loads(json_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required field in JSON response: '{key}'")

        # Sadece "YES", "NO" veya boş string kontrolü
        yes_no_fields = [
            "campaign_responsible_ask",
            "campaign_related",
            "pii_check_control"
        ]
        for field in yes_no_fields:
            value = data[field].strip().upper()
            if value not in ["YES", "NO", ""]:
                raise ValueError(
                    f"Field '{field}' must be 'YES', 'NO', or an empty string. Got: '{data[field]}'"
                )
            data[field] = value  # Normalizasyon
        return data

    def initialize_openai_client(self):
        """
        OpenAI (Azure OpenAI) istemcisini, config_info'da tanımlı ayarlarla başlatır.
        Proxy ve API anahtarları ayarlanır.
        """
        try:
            os.environ["HTTP_PROXY"] = self.config.http_proxy
            os.environ["HTTPS_PROXY"] = self.config.https_proxy
            openai.api_key = self.config.api_key
            # AzureOpenAI sınıfının doğru şekilde import edildiğini varsayıyoruz.
            client = AzureOpenAI(
                azure_api_key=self.config.azure_api_key,
                api_version=self.config.azure_api_version,
                azure_endpoint=self.config.azure_endpoint
            )
            return client
        except Exception as e:
            raise RuntimeError(f"OpenAI client initialization failed: {e}")

    def generate_routing_response(self, user_prompt: str) -> dict:
        """
        Kullanıcının sorusunu, routing prompt üzerinden OpenAI API ile yönlendirir.
        Yanıtı post_process_campaign_response ile doğrular ve sözlük olarak döndürür.
        """
        client = self.initialize_openai_client()
        routing_response_text = "Verilen talimatalara uygun olarak soruya cevap ver: " + user_prompt
        messages = [
            {"role": "system", "content": self.routing_prompt},
            {"role": "user", "content": routing_response_text}
        ]
        try:
            response = client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                temperature=0,
                max_tokens=self.max_tokens
            )
            response_json = response.to_json()
            routing_data = self.post_process_campaign_response(response_json)
            return routing_data
        except Exception as e:
            raise RuntimeError(f"Routing response generation failed: {e}")

    def generate_campaign_response(self, user_prompt: str, campaign_description=None) -> str:
        """
        Kampanya yanıtı üretir (campaign_code için akış).
        OpenAI API ile tanımlı sistem prompt ve kampanya metni üzerinden cevap üretir.
        """
        client = self.initialize_openai_client()
        rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metin içeriği: " + str(campaign_description)
        messages = [
            {"role": "system", "content": self.config.SYSTEM_PROMPT_MAIN_LAYER},
            {"role": "user", "content": rag_prompt}
        ]
        try:
            response = client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                temperature=0,
                max_tokens=self.max_tokens
            )
            response_data = json.loads(response.to_json())
            return response_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Campaign response generation failed: {e}")

    def generate_campaign_response_v2(self, user_prompt: str, campaign_description=None) -> str:
        """
        Spesifik kampanya başlığı (spesific_campaign_header) için yanıt üretir.
        """
        client = self.initialize_openai_client()
        rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metin içeriği: " + str(campaign_description)
        messages = [
            {"role": "system", "content": "Kampanya ile ilgili sorulara cevap ver"},
            {"role": "user", "content": rag_prompt}
        ]
        try:
            response = client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                temperature=0,
                max_tokens=self.max_tokens
            )
            response_data = json.loads(response.to_json())
            return response_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Campaign response v2 generation failed: {e}")

    def generate_campaign_response_v3(self, user_prompt: str, campaign_description=None, history_text="") -> str:
        """
        Takip kodu veya takip başlığı (follow_up_campaign_code / follow_up_campaign_header) durumunda,
        history bilgisini de kullanarak yanıt üretir.
        """
        client = self.initialize_openai_client()
        rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metin içeriği: " + str(campaign_description)
        messages = [
            {"role": "system", "content": history_text if history_text else "Kampanya ile ilgili sorulara cevap ver"},
            {"role": "user", "content": rag_prompt}
        ]
        try:
            response = client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                temperature=0,
                max_tokens=self.max_tokens
            )
            response_data = json.loads(response.to_json())
            return response_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Campaign response v3 generation failed: {e}")

    def generate_campaign_response_v4(self, user_prompt: str, campaign_description=None, history_text="") -> str:
        """
        campaign_related durumu için, history bilgisini de ekleyerek yanıt üretir.
        """
        client = self.initialize_openai_client()
        rag_prompt = "Soruya cevap ver: " + user_prompt + "\n\nKampanya metin içeriği: " + str(campaign_description)
        messages = [
            {"role": "system", "content": history_text if history_text else "Kampanya ile ilgili sorulara cevap ver"},
            {"role": "user", "content": rag_prompt}
        ]
        try:
            response = client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                temperature=0,
                max_tokens=self.max_tokens
            )
            response_data = json.loads(response.to_json())
            return response_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Campaign response v4 generation failed: {e}")

    def process_user_input(self, user_input: str) -> str:
        """
        Kullanıcının sorusunu alır, öncelikle routing aşaması ile OpenAI API'den yönlendirir,
        ardından routing verilerine göre uygun iş akışını çalıştırıp yanıtı oluşturur.
        Hata durumlarında uygun mesajlar döner.
        """
        try:
            routing_data = self.generate_routing_response(user_input)
        except Exception as e:
            return f"Routing aşamasında hata oluştu: {e}"
        
        # Routing'den gelen verileri ayrıştırıyoruz.
        campaign_code = routing_data.get("campaign_code", "").strip()
        campaign_responsible_ask = routing_data.get("campaign_responsible_ask", "").strip().upper()
        spesific_campaign_header = routing_data.get("spesific_campaign_header", "").strip()
        general_campaign_header = routing_data.get("general_campaign_header", "").strip()
        follow_up_campaign_code = routing_data.get("follow_up_campaign_code", "").strip()
        follow_up_campaign_header = routing_data.get("follow_up_campaign_header", "").strip()
        campaign_related = routing_data.get("campaign_related", "").strip().upper()
        pii_check_control = routing_data.get("pii_check_control", "").strip().upper()
        
        response = ""
        add_to_history = True  # Varsayılan: mesaj geçmişine ekle
        
        try:
            # 1) pii_check_control YES ise
            if pii_check_control == "YES":
                response = "sorunuzda kişisel veri tespit ettim lütfen sorunuzu kontrol ediniz."
                add_to_history = False
            # 2) campaign_code var ve campaign_responsible_ask YES ise
            elif campaign_code and campaign_responsible_ask == "YES":
                es = ElasticTextSearch()
                campaign_responsible = es.get_responsible_name_search_code(campaign_code)
                response = f"kampanyadan sorumlu kişi {campaign_responsible}"
                add_to_history = False
            # 3) campaign_code var ve campaign_responsible_ask NO ise
            elif campaign_code and campaign_responsible_ask == "NO":
                es = ElasticTextSearch()
                campaign_info = es.get_best_related(campaign_code)
                response = self.generate_campaign_response(user_input, campaign_description=campaign_info)
            # 4) spesific_campaign_header var ve campaign_responsible_ask YES ise
            elif spesific_campaign_header and campaign_responsible_ask == "YES":
                es = ElasticTextSearch()
                campaign_responsible = es.get_responsible_name_search_header(spesific_campaign_header)
                response = f"kampanyadan sorumlu kişi {campaign_responsible}"
                add_to_history = False
            # 5) spesific_campaign_header var ve campaign_responsible_ask NO ise
            elif spesific_campaign_header and campaign_responsible_ask == "NO":
                es = ElasticTextSearch()
                campaign_info = es.search_campaign_by_header_one_result(spesific_campaign_header)
                response = self.generate_campaign_response_v2(user_input, campaign_description=campaign_info)
            # 6) general_campaign_header var ise
            elif general_campaign_header:
                es = ElasticTextSearch()
                campaign_info = es.search_campaign_by_header(general_campaign_header)
                response = f"Yaptığınız genel aramaya göre aşağıdaki sonuçlar bulunmuştur: {campaign_info}"
            # 7) follow_up_campaign_code var ise
            elif follow_up_campaign_code:
                es = ElasticTextSearch()
                campaign_info = es.get_best_related(follow_up_campaign_code)
                history_text = self.get_formatted_history()
                response = self.generate_campaign_response_v3(user_input, campaign_description=campaign_info, history_text=history_text)
            # 8) follow_up_campaign_header var ise
            elif follow_up_campaign_header:
                es = ElasticTextSearch()
                campaign_info = es.search_campaign_by_header_one_result(follow_up_campaign_header)
                history_text = self.get_formatted_history()
                response = self.generate_campaign_response_v3(user_input, campaign_description=campaign_info, history_text=history_text)
            # 9) campaign_related YES ise
            elif campaign_related == "YES":
                history_text = self.get_formatted_history()
                response = self.generate_campaign_response_v4(user_input, campaign_description=None, history_text=history_text)
            else:
                response = "Lütfen geçerli kampanya bilgileri giriniz."
        except Exception as e:
            response = f"İş akışı sırasında hata oluştu: {e}"
            add_to_history = False

        # Sohbet geçmişine ekle (geçerli ise)
        self.update_history(user_input, response, add_to_history=add_to_history)
        return response


# Streamlit Arayüzü: Uygulamanın ana giriş noktası
def main():
    st.title("🤖 Kampanya Asistanı")
    st.warning("📌 Lütfen kampanya ile ilgili sorularınızı girin")

    # Kampanya asistanı sınıfını başlatıyoruz.
    assistant = CampaignAssistant()
    
    user_input = st.text_input("Lütfen kampanya ile ilgili sorularınızı girin")
    if user_input:
        with st.spinner("💭 Düşünüyorum..."):
            try:
                answer = assistant.process_user_input(user_input)
            except Exception as e:
                answer = f"Bir hata oluştu: {e}"
        st.subheader("🔎 Yanıt")
        st.write(answer)
        st.subheader("📖 Sohbet Geçmişi")
        st.write(assistant.get_formatted_history())


if __name__ == "__main__":
    main()

















### FİNAL



import os
import json
import openai
import streamlit as st
from elastic_search_retriever_embedding import ElasticTextSearch
import config_info

# Global ayarlar
max_tokens = 150

# POWERFULL_ROUTING_PROMPT: JSON formatında beklenen çıktıyı tanımlar.
POWERFULL_ROUTING_PROMPT = """ 
Lütfen aşağıdaki formatta JSON çıktısı üret:
{
    "campaign_code": "",
    "campaign_responsible_ask": "",
    "spesific_campaign_header": "",
    "general_campaign_header": "",
    "follow_up_campaign_code": "",
    "follow_up_campaign_header": "",
    "campaign_related": "",
    "pii_check_control": ""
}
Kurallara göre:
- campaign_responsible_ask, campaign_related ve pii_check_control sadece "YES", "NO" veya boş olabilir.
"""

# Streamlit session state üzerinden sohbet geçmişini tutmak için:
if 'history' not in st.session_state:
    st.session_state.history = []


def update_history(user_question: str, bot_response: str):
    """
    Sohbet geçmişine yeni bir kullanıcı-sistem çiftini ekler.
    Eğer güncel mesaj pii_check_control veya campaign_responsible_ask YES ise eklenmez.
    Sadece son 3 mesaj saklanır.
    """
    st.session_state.history.append({
        "user_question": user_question,
        "bot_response": bot_response
    })
    # Sadece son 3 mesajı tut
    if len(st.session_state.history) > 3:
        st.session_state.history = st.session_state.history[-3:]


def get_formatted_history() -> str:
    """
    Sohbet geçmişini istenen formatta (en son mesaj en üstte) formatlar.
    """
    history = st.session_state.history
    formatted_lines = []
    n = len(history)
    if n >= 1:
        conv = history[-1]
        formatted_lines.append("Kullanıcının son sorusu:")
        formatted_lines.append(conv["user_question"])
        formatted_lines.append("Kullanıcının son sorusunun cevabı:")
        formatted_lines.append(conv["bot_response"])
    if n >= 2:
        conv = history[-2]
        formatted_lines.append("Kullanıcının sondan ikinci sorusu:")
        formatted_lines.append(conv["user_question"])
        formatted_lines.append("Kullanıcının sondan ikinci sorusunun cevabı:")
        formatted_lines.append(conv["bot_response"])
    if n >= 3:
        conv = history[-3]
        formatted_lines.append("Kullanıcının sondan üçüncü sorusu:")
        formatted_lines.append(conv["user_question"])
        formatted_lines.append("Kullanıcının sondan üçüncü sorusunun cevabı:")
        formatted_lines.append(conv["bot_response"])
    return "\n".join(formatted_lines)


def post_process_campaign_response(json_response: str) -> dict:
    """
    OpenAI'dan gelen JSON yanıtını parse edip, gerekli alanları kontrol eder.
    """
    required_keys = [
        "campaign_code",
        "campaign_responsible_ask",
        "spesific_campaign_header",
        "general_campaign_header",
        "follow_up_campaign_code",
        "follow_up_campaign_header",
        "campaign_related",
        "pii_check_control"
    ]
    
    try:
        data = json.loads(json_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field in JSON response: '{key}'")
    
    yes_no_fields = [
        "campaign_responsible_ask",
        "campaign_related",
        "pii_check_control"
    ]
    for field in yes_no_fields:
        value = data[field].strip().upper()
        if value not in ["YES", "NO", ""]:
            raise ValueError(
                f"Field '{field}' must be 'YES', 'NO', or an empty string. Got: '{data[field]}'"
            )
        data[field] = value  # Normalize
        
    return data


def initialize_openai_client(api_key, azure_api_key, azure_api_version, azure_endpoint, http_proxy, https_proxy):
    """
    OpenAI (Azure OpenAI) istemcisini yapılandırır.
    """
    os.environ["HTTP_PROXY"] = http_proxy
    os.environ["HTTPS_PROXY"] = https_proxy

    openai.api_key = api_key
    # AzureOpenAI sınıfının import edildiğini varsayıyoruz.
    client = AzureOpenAI(
        azure_api_key=azure_api_key,
        api_version=azure_api_version,
        azure_endpoint=azure_endpoint
    )

    return client


def generate_routing_response(user_prompt, system_prompt=POWERFULL_ROUTING_PROMPT, deployment_name=config_info.deployment_name) -> dict:
    """
    Kullanıcının sorusunu routing prompt üzerinden yönlendirir ve 
    JSON yanıtı parse edip döndürür.
    History bilgisi mevcutsa prompt'a eklenir.
    """
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
       
    # History bilgisi mevcutsa ekle, yoksa boş string kullan.
    history_text = get_formatted_history() if st.session_state.history else ""
    powerfull_prompt = f"{system_prompt}\nHistory:\n{history_text}\n\nSoru: {user_prompt}"

    messages = [
        {"role": "system", "content": powerfull_prompt}
    ]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )

    response_data = response.to_json()
    processed_data = post_process_campaign_response(response_data)
    return processed_data


def generate_campaign_response(user_prompt, system_prompt=config_info.SYSTEM_PROMPT_MAIN_LAYER, campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def generate_campaign_response_v2(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def generate_campaign_response_v3(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def generate_campaign_response_v4(user_prompt, system_prompt="Kampanya ile ilgili sorulara cevap ver", campaign_description=None, deployment_name=config_info.deployment_name) -> str:
    client = initialize_openai_client(
        config_info.api_key,
        config_info.azure_api_key,
        config_info.azure_api_version,
        config_info.azure_endpoint,
        config_info.http_proxy,
        config_info.https_proxy
    )
    
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


def process_user_input(user_input: str) -> str:
    """
    Kullanıcının sorusunu önce routing response üzerinden yönlendirir,
    ardından ilgili iş akışına göre doğru fonksiyonu çalıştırır.
    """
    routing_data = generate_routing_response(user_input, system_prompt=POWERFULL_ROUTING_PROMPT)
    
    campaign_code = routing_data.get("campaign_code", "").strip()
    campaign_responsible_ask = routing_data.get("campaign_responsible_ask", "").strip().upper()
    spesific_campaign_header = routing_data.get("spesific_campaign_header", "").strip()
    general_campaign_header = routing_data.get("general_campaign_header", "").strip()
    follow_up_campaign_code = routing_data.get("follow_up_campaign_code", "").strip()
    follow_up_campaign_header = routing_data.get("follow_up_campaign_header", "").strip()
    campaign_related = routing_data.get("campaign_related", "").strip().upper()
    pii_check_control = routing_data.get("pii_check_control", "").strip().upper()
    
    response = ""
    add_to_history = True  # Varsayılan olarak geçmişe eklensin

    if pii_check_control == "YES":
        response = "sorunuzda kişisel veri tespit ettim lütfen sorunuzu kontrol ediniz."
        add_to_history = False
    elif campaign_code and campaign_responsible_ask == "YES":
        es = ElasticTextSearch()
        campaign_responsible = es.get_responsible_name_search_code(campaign_code)
        response = f"kampanyadan sorumlu kişi {campaign_responsible}"
        add_to_history = False
    elif campaign_code and campaign_responsible_ask == "NO":
        es = ElasticTextSearch()
        campaign_info = es.get_best_related(campaign_code)
        response = generate_campaign_response(user_input, campaign_description=campaign_info)
    elif spesific_campaign_header and campaign_responsible_ask == "YES":
        es = ElasticTextSearch()
        campaign_responsible = es.get_responsible_name_search_header(spesific_campaign_header)
        response = f"kampanyadan sorumlu kişi {campaign_responsible}"
        add_to_history = False
    elif spesific_campaign_header and campaign_responsible_ask == "NO":
        es = ElasticTextSearch()
        campaign_info = es.search_campaign_by_header_one_result(spesific_campaign_header)
        response = generate_campaign_response_v2(user_input, campaign_description=campaign_info)
    elif general_campaign_header:
        es = ElasticTextSearch()
        campaign_info = es.search_campaign_by_header(general_campaign_header)
        response = f"Yaptığınız genel aramaya göre aşağıdaki sonuçlar bulunmuştur: {campaign_info}"
    elif follow_up_campaign_code:
        es = ElasticTextSearch()
        campaign_info = es.get_best_related(follow_up_campaign_code)
        response = generate_campaign_response_v3(user_input, system_prompt=get_formatted_history(), campaign_description=campaign_info)
    elif follow_up_campaign_header:
        es = ElasticTextSearch()
        campaign_info = es.search_campaign_by_header_one_result(follow_up_campaign_header)
        response = generate_campaign_response_v3(user_input, system_prompt=get_formatted_history(), campaign_description=campaign_info)
    elif campaign_related == "YES":
        response = generate_campaign_response_v4(user_input, system_prompt=get_formatted_history(), campaign_description=None)
    else:
        response = "Lütfen geçerli kampanya bilgileri giriniz."

    if add_to_history:
        update_history(user_input, response)
        
    return response


# Streamlit arayüzü
st.title("🤖 Kampanya Asistanı")
st.warning("📌 Lütfen kampanya ile ilgili sorularınızı girin")

user_input = st.text_input("Lütfen kampanya ile ilgili sorularınızı girin")

if user_input:
    with st.spinner("💭 Düşünüyorum..."):
        answer = process_user_input(user_input)
    st.subheader("🔎 Yanıt")
    st.write(answer)
    st.subheader("📖 Sohbet Geçmişi")
    st.write(get_formatted_history())




