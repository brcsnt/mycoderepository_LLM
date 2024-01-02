import pandas as pd
import nltk
from nltk.translate.bleu_score import sentence_bleu
import difflib
# nltk kütüphanesinin gerekli bileşenlerini indir
nltk.download('punkt')

# input_dataframe ve output_dataframe olarak adlandırılan DataFrame'leriniz varsayılmıştır.

# CodeBLEU skorunu hesaplamak için fonksiyon (Basitleştirilmiş versiyon)
def calculate_codebleu(original, generated):
    # Burada, daha karmaşık bir CodeBLEU hesaplama yöntemi uygulanabilir.
    return sentence_bleu([original.split()], generated.split())

# BLEU skorunu hesaplamak için fonksiyon
def calculate_bleu(original, generated):
    return sentence_bleu([original.split()], generated.split())

# Metin benzerliğini hesaplamak için fonksiyon
def calculate_similarity(original, generated):
    return difflib.SequenceMatcher(None, original, generated).ratio()

# Sonuçları saklamak için yeni bir DataFrame
results = pd.DataFrame(columns=["text", "generated_text", "CodeBLEU_Score", "BLEU_Score", "Similarity_Score"])

# Her satır için skorları hesaplayın ve sonuçları saklayın
for index, row in output_dataframe.iterrows():
    original_text = input_dataframe.loc[index, 'text']
    generated_text = row['generated_text']
    codebleu_score = calculate_codebleu(original_text, generated_text)
    bleu_score = calculate_bleu(original_text, generated_text)
    similarity_score = calculate_similarity(original_text, generated_text)
    results = results.append({
        "text": original_text, 
        "generated_text": generated_text, 
        "CodeBLEU_Score": codebleu_score, 
        "BLEU_Score": bleu_score, 
        "Similarity_Score": similarity_score
    }, ignore_index=True)

# Sonuç DataFrame'ini göster
print(results)
