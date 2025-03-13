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
