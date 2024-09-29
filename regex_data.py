import pandas as pd
from io import StringIO
import re

# Verilen verileri bir metin bloğu olarak tanımlayalım
data = """word\texplanation

"""

# Verileri pandas DataFrame'e okuyalım
df = pd.read_csv(StringIO(data), sep='\t')

# İşleme başlamadan önce boş bir liste oluşturalım
sentences = []

# Her bir satırı işleyelim
for idx, row in df.iterrows():
    word = row['word']
    explanation = row['explanation']
    
    # Açıklamadaki başlangıç ve bitiş tırnaklarını kaldıralım
    explanation = explanation.strip('"')
    
    # 'keyword' satırlarını kaldıralım
    explanation = re.sub(r'keyword:.*', '', explanation, flags=re.IGNORECASE)
    
    # Cümleleri tespit etmek için düzenli ifade tanımlayalım
    pattern = r'(?i)(?:sentence\s*)?(\d+):\s*([^:]*?)(?=(?:\s*(?:sentence\s*)?\d+:|$))'
    
    # Açıklamadan tüm eşleşmeleri alalım
    matches = re.findall(pattern, explanation)
    
    for match in matches:
        sentence_num, sentence_text = match
        sentence_text = sentence_text.strip()
        if sentence_text:
            sentences.append({'word': word, 'sentence': sentence_text})

# Sonuç DataFrame'i oluşturalım
output_df = pd.DataFrame(sentences)
print(output_df)