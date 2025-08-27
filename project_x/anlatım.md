Elbette, yapay zeka tarafından okunabilir doküman özelliklerini özetleyen sunum formatında bir slayt aşağıda hazırlanmıştır.

---

### **Slayt: Yapay Zeka İçin Doküman Nasıl Hazırlanır?**

#### **Başlık: Geleceğin Verisi: AI Tarafından Okunabilir Dokümanlar Oluşturma**

---

**1. "AI Tarafından Okunabilirlik" Nedir?**

* [cite_start]**Temel Fikir:** Bir yapay zeka sisteminin, bir belgedeki bilgiyi ne kadar az hesaplama maliyetiyle ve ne kadar doğru çıkarabildiğinin bir ölçüsüdür[cite: 5].
* [cite_start]**Amaç:** Bilgiyi, insanların anladığı görsel formatlardan (PDF gibi), makinelerin anladığı yapısal formatlara (Markdown, JSON gibi) dönüştürmektir[cite: 10, 11]. [cite_start]Bu işlem, sorgu anındaki yükü azaltır ve sistem performansını artırır[cite: 9, 13].

---

**2. Temel Kural: Önce Metni Temizle (Text Preprocessing)**

* [cite_start]**Neden Önemli?** Kirli ve tutarsız metin, yapay zekanın anlamsal arama ve anlama yeteneğini doğrudan zayıflatır[cite: 21, 29, 30].
* **Ne Yapılmalı?**
    * [cite_start]**Tokenizasyon:** Metni kelime veya cümle gibi anlamlı birimlere ayırmak[cite: 17, 18].
    * **Normalleştirme:**
        * [cite_start]Tüm metni küçük harfe çevirmek ("Yapay Zeka" ve "yapay zeka" aynı olsun diye)[cite: 23].
        * [cite_start]Noktalama işaretleri ve gereksiz karakterleri temizlemek[cite: 25].
        * [cite_start]Kısaltmaları açmak (Örn: "KVKK" -> "Kişisel Verilerin Korunması Kanunu")[cite: 26].

---

**3. Doğru Formatı Seç: Yapı Her Şeydir**

* **❌ Kaçınılması Gereken:** **PDF**. [cite_start]Görsel sunumu önceliklendirir, makine tarafından okunması zordur ve maliyetli OCR işlemleri gerektirir[cite: 37, 38].
* **✅ Tercih Edilmesi Gereken:** **Markdown (.md)**. [cite_start]İnsan ve makine okunabilirliği arasında ideal bir denge kurar[cite: 43]. [cite_start]Başlık, liste gibi belgenin mantıksal yapısını korur, bu da yapay zekanın metni daha derin anlamasına yardımcı olur[cite: 44, 53].
* **Diğer Formatlar:**
    * [cite_start]**Düz Metin (.txt):** Kolay işlenir ama tüm yapısal bilgiyi kaybeder[cite: 39, 40].
    * [cite_start]**JSON:** Yapılandırılmış verileri (tablolar, meta veriler) depolamak için mükemmeldir[cite: 41].

---

**4. RAG İçin Akıllıca Parçala (Chunking)**

* [cite_start]**Neden Gerekli?** Büyük metinleri, dil modellerinin (LLM) işleyebileceği ve daha hassas arama sonuçları üretebilecek küçük, anlamlı parçalara ayırmak için[cite: 67, 69].
* **En İyi Stratejiler:**
    * [cite_start]**Basit Yöntemler:** Sabit boyutlu veya cümle/paragraf bazlı bölme[cite: 86, 88, 91].
    * **Gelişmiş Yöntemler:**
        * [cite_start]**Özyinelemeli (Recursive):** Belge yapısına dinamik olarak uyum sağlar[cite: 95, 97].
        * [cite_start]**Anlamsal (Semantic):** Anlamsal olarak ilişkili metinleri bir araya getirerek en kaliteli sonuçları üretir[cite: 98, 99].
* [cite_start]**Kritik Denge:** Parçalar ne çok büyük (anlam bulanıklaşır) ne de çok küçük (bağlam kaybolur) olmalıdır[cite: 111, 113].

---

**5. Her Parçaya Kimlik Ver: Meta Veri Ekle**

* [cite_start]**Meta Veri Nedir?** "Veri hakkındaki veri"dir[cite: 123]. [cite_start]Her bir metin parçasını; kaynak belge, sayfa numarası, bölüm başlığı gibi bilgilerle etiketlemektir[cite: 128].
* **Ne İşe Yarar?**
    * [cite_start]Parçalama sırasında kaybolan bağlamı yeniden oluşturur[cite: 129].
    * [cite_start]Aramaları filtrelemeye olanak tanır (Örn: "Sadece 2023 tarihli finansal raporlarda arama yap")[cite: 148]. [cite_start]Bu, hızı ve doğruluğu önemli ölçüde artırır[cite: 150, 151].

---

**6. Metin Dışındakileri Unutma: Tablo ve Görseller**

* [cite_start]**Tablolar:** PDF içinde hapsolmuş tabloları, OCR ve Bilgisayarla Görü teknolojileriyle ayıklayıp **JSON** gibi yapılandırılmış formatlara dönüştürmek gerekir[cite: 156, 159, 161, 172].
* **Görseller:**
    * [cite_start]İçindeki metinleri **OCR** ile çıkarmak[cite: 181].
    * Anlamını açıklayan **Alternatif Metin (Alt-Text)** eklemek. [cite_start]İyi bir alt-text, görseli yapay zeka için aranabilir ve anlaşılabilir bir veriye dönüştürür[cite: 186, 188].

---

**7. En Üst Seviye: Anlamsal Anlam Kazandırma**

* [cite_start]**Hedef:** Yapay zekanın metindeki varlıkları ("Apple Inc." gibi) ve ilişkileri sadece istatistiksel olarak tahmin etmesi yerine, açıkça anlamasını sağlamak[cite: 193, 215].
* [cite_start]**Nasıl Yapılır?** **JSON-LD** ve **schema.org** gibi standartlar kullanarak metne yapılandırılmış veri katmanı eklemek (Örn: `{"@type": "Organization", "name": "Apple Inc."}`)[cite: 207, 209].
* [cite_start]**Sonuç:** Bu, yapay zekanın "halüsinasyon" görmesini engeller ve doğruluğunu en üst düzeye çıkarır[cite: 213, 214]. [cite_start]En ideal "AI-Readable" yapı, bir belgeden türetilmiş bir **Bilgi Grafiğidir (Knowledge Graph)**[cite: 202].
