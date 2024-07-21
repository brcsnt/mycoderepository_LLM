class CampaignBot:
    def __init__(self, excel_path, api_key):
        self.excel_path = excel_path
        self.api_key = api_key
        self.df = pd.DataFrame()  # Boş bir DataFrame oluşturuyoruz
        self.load_excel(excel_path)  # Excel dosyasını yükle
        openai.api_key = self.api_key  # OpenAI API anahtarını ayarla

    def load_excel(self, excel_path):
        """Excel dosyasını yükler"""
        try:
            self.df = pd.read_excel(excel_path)
            # Kampanya Kodu sütununu string'e dönüştür
            self.df['Kampanya Kodu'] = self.df['Kampanya Kodu'].astype(str)
            print("Excel dosyası başarıyla yüklendi.")
            # Excel dosyasının ilk birkaç satırını yazdırarak doğruluğunu kontrol edin
            print(self.df.head())
        except Exception as e:
            print(f"Excel dosyası yüklenirken hata: {str(e)}")

    def get_campaign_description(self, code):
        """Kampanya koduna karşılık gelen açıklama metnini döndürür"""
        try:
            # Kodun büyük/küçük harf duyarlılığını kontrol edin
            campaign_row = self.df.loc[self.df['Kampanya Kodu'].str.upper() == code.upper()]
            if not campaign_row.empty:
                return campaign_row['Açıklama Metni'].values[0]
            else:
                return None
        except Exception as e:
            print(f"Kampanya kodu aranırken hata: {str(e)}")
            return None
    
    def ask_question(self, description, question):
        """Kampanya açıklamasını kullanarak OpenAI API ile soruyu cevaplar"""
        try:
            if len(description) > 30000:
                return "Bu kampanya metni 30.000 karakterden uzun olduğu için sorulara cevap veremiyorum."
            
            prompt = f"Kampanya: {description}\n\nSoru: {question}\nCevap:"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen, sadece belirli bir kampanya ile ilgili bilgi sağlayan ve soruları yanıtlayan bir yapay zeka asistanısın. Yanıtların sadece kampanya detayları, hedefleri, stratejileri, ilerleme güncellemeleri, metrikler, hedef kitle, promosyon faaliyetleri, zaman çizelgesi ve sonuçlar ile sınırlı olmalıdır. Kampanya ile doğrudan ilgili olmayan konularda bilgi verme veya tartışmaya girme.Eğer bir soru cevap vermen gereken metindeki konuların dışına çıkıyorsa, kullanıcıya sadece kampanya ile ilgili bilgi sağlayabileceğini nazikçe bildir."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Soru sorulurken hata: {str(e)}")
            return None



# Excel dosyasının sabit yolu
excel_path = "kampanya_listesi.xlsx"
api_key_input = widgets.Password(description="OpenAI API Anahtarı:")
code_input = widgets.Text(description="Kampanya Kodu:")
question_input = widgets.Text(description="Sorunuzu Girin:")
output = widgets.Output()

# Kampanya botu nesnesini başlatmak için düğme
start_button = widgets.Button(description="Başlat")
def start_button_clicked(b):
    global bot
    api_key = api_key_input.value
    bot = CampaignBot(excel_path, api_key)
    with output:
        output.clear_output()
        print("Kampanya botu başlatıldı.")
start_button.on_click(start_button_clicked)

# Kampanya sorgulama ve cevaplama düğmeleri
query_button = widgets.Button(description="Sorgula")
answer_button = widgets.Button(description="Cevapla")

def query_button_clicked(b):
    code = code_input.value
    description = bot.get_campaign_description(code)
    with output:
        output.clear_output()
        if description:
            if len(description) > 30000:
                print("Bu kampanya metni 30.000 karakterden uzun olduğu için sorulara cevap veremiyorum.")
            else:
                print(f"Kampanya Açıklaması:\n{description}")
                global campaign_description
                campaign_description = description
        else:
            print("Geçersiz kampanya kodu. Lütfen doğru bir kampanya kodu girin.")
query_button.on_click(query_button_clicked)

def answer_button_clicked(b):
    question = question_input.value
    with output:
        output.clear_output()
        if 'campaign_description' in globals():
            answer = bot.ask_question(campaign_description, question)
            print(f"Cevap:\n{answer}")
        else:
            print("Lütfen önce kampanya kodunu sorgulayın.")
answer_button.on_click(answer_button_clicked)

# Widget'ları görüntüle
display(api_key_input, start_button, code_input, query_button, question_input, answer_button, output)
