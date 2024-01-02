import pandas as pd
from transformers import AutoTokenizer, pipeline

# Fine-tuned modelinizi ve tokenizer'ınızı yükleyin
model_name = "fine-tuned-modelin-adı"
tokenizer = AutoTokenizer.from_pretrained(model_name)
text_generation_pipeline = pipeline(
    "text-generation",
    model=model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)

# Input DataFrame'inizi yükleyin (örnek: input_dataframe)
# input_dataframe = pd.read_csv("dosya_yolu.csv")

# Yeni bir DataFrame oluşturun
output_dataframe = pd.DataFrame(columns=["dosya_adı", "generated_text"])

# Her satır için modeli çalıştırın
for index, row in input_dataframe.iterrows():
    prompt = row['text']
    sequences = text_generation_pipeline(
        f'<s>[INST] {prompt} [/INST]',
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=200,
    )
    generated_text = sequences[0]['generated_text']
    output_dataframe = output_dataframe.append({"dosya_adı": row['dosya_adı'], "generated_text": generated_text}, ignore_index=True)

# Sonuç DataFrame'ini göster
print(output_dataframe)
