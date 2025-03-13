Below are the updated sections for your prompt in English. These updates focus solely on determining whether the user's query is a general question or one related to a specific campaign based entirely on the text, without relying on time information.

---

**Updated Section for Specific Campaign Header Extraction:**

- **Current Instruction:**  
  "When the user’s query contains a specific campaign name (e.g., 'Ocak ayı Migros Ramazan kampanyası'), it is considered a specific campaign inquiry and should be placed under the `specific_campaign_header` field."

- **Updated Instruction:**  
  "Examine the structure of the user's query to determine whether it contains a clear, unique, and singular campaign identifier. For example, if the query includes an explicit campaign name like 'Migros Ramazan kampanyası', classify it as a specific campaign inquiry and extract the campaign name (e.g., 'Migros Ramazan') into the `specific_campaign_header` field. This classification must be based solely on the text of the query; any time reference present should be processed separately and must not influence the determination of a specific campaign inquiry."

---

**Updated Section for General Campaign Header Extraction:**

- **Current Instruction:**  
  "When the user's query only contains general campaign terms (e.g., 'Boyner kampanyaları' or 'Boyner kampanyaları listele'), it is considered a general campaign inquiry and should be placed under the `general_campaign_header` field."

- **Updated Instruction:**  
  "If the user’s query contains a general and all-encompassing campaign reference rather than a unique campaign identifier (for example, 'Boyner kampanyaları'), classify the query as a general campaign inquiry. The primary criterion here is whether the query represents a general concept rather than a specific, unique campaign. Any additional time reference should be treated as supplementary information and must not affect this primary classification."

---

These revisions ensure that the system determines whether a query is general or specific based solely on the campaign reference within the text, independent of any time-related details.






Aşağıda, spesifik kampanya sorguları ve genel kampanya sorguları için çok daha çeşitli few-shot örnekleri yer almaktadır. Bu örneklerde, sistemin yalnızca kullanıcının metin ifadesine dayanarak ayrım yapması hedeflenmektedir.

---

### **Spesifik Kampanya Sorguları**

#### **Örnek 1**
**Kullanıcı Girdisi:**  
> "Migros Ramazan kampanyası hakkında detaylı bilgi verir misiniz?"

**Çıktı:**
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "specific_campaign_header": "Migros Ramazan",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "follow_up_campaign_responsible": "",
  "campaign_related": "",
  "campaign_time": "",
  "pii_check_violate": "NO"
}
```

#### **Örnek 2**
**Kullanıcı Girdisi:**  
> "A101 Black Friday kampanyası ne zaman başlayacak?"

**Çıktı:**
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "specific_campaign_header": "A101 Black Friday",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "follow_up_campaign_responsible": "",
  "campaign_related": "",
  "campaign_time": "",
  "pii_check_violate": "NO"
}
```

#### **Örnek 3**
**Kullanıcı Girdisi:**  
> "Ocak ayında Kipa Yılbaşı kampanyası neler içeriyor?"

**Çıktı:**
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "specific_campaign_header": "Kipa Yılbaşı",
  "general_campaign_header": "",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "follow_up_campaign_responsible": "",
  "campaign_related": "",
  "campaign_time": "",
  "pii_check_violate": "NO"
}
```

---

### **Genel Kampanya Sorguları**

#### **Örnek 4**
**Kullanıcı Girdisi:**  
> "Migros kampanyaları neler var?"

**Çıktı:**
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "specific_campaign_header": "",
  "general_campaign_header": "Migros kampanyaları",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "follow_up_campaign_responsible": "",
  "campaign_related": "",
  "campaign_time": "",
  "pii_check_violate": "NO"
}
```

#### **Örnek 5**
**Kullanıcı Girdisi:**  
> "Boyner kampanyaları güncel durumda mı?"

**Çıktı:**
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "specific_campaign_header": "",
  "general_campaign_header": "Boyner kampanyaları",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "follow_up_campaign_responsible": "",
  "campaign_related": "",
  "campaign_time": "",
  "pii_check_violate": "NO"
}
```

#### **Örnek 6**
**Kullanıcı Girdisi:**  
> "Market kampanyaları hakkında bilgi verebilir misin?"

**Çıktı:**
```json
{
  "campaign_code": "",
  "campaign_responsible_ask": "NO",
  "specific_campaign_header": "",
  "general_campaign_header": "Market kampanyaları",
  "follow_up_campaign_code": "",
  "follow_up_campaign_header": "",
  "follow_up_campaign_responsible": "",
  "campaign_related": "",
  "campaign_time": "",
  "pii_check_violate": "NO"
}
```

---

Bu örnekler, sistemin yalnızca kullanıcının sorgusundaki kampanya referansına bakarak spesifik mi yoksa genel mi olduğunu doğru şekilde belirlemesini sağlayacak şekilde çeşitlendirilmiştir. Zaman ifadesi varsa, bu ek bilgi olarak işlenecek, ancak ana sınıflandırma tamamen kampanya ifadesinin belirginliğine dayanacaktır.
