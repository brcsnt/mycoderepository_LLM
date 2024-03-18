# Gerekli kütüphaneleri yükle
!pip install transformers
!pip install torch

import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import BartTokenizer, BartForConditionalGeneration, Trainer, TrainingArguments

# Veri setini yükle ve ön işle
df = pd.read_csv("yol/dosya_adi.csv")  # Veri setinin yolu

# DataFrame örneğini göster
print(df.head())

# Tokenizer ve modeli yükle
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large')

def preprocess_data(examples):
    inputs = [code1 for code1 in examples['code1']]
    targets = [code2 for code2 in examples['code2']]
    model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")

    # Hedefleri tokenize et
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=512, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# DataFrame'i dictionary'e dönüştür ve veriyi hazırla
dataset = df.to_dict('list')
dataset = preprocess_data(dataset)

# PyTorch Dataset sınıfını tanımla
class CodeDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings['input_ids'])

train_dataset = CodeDataset(dataset)

# Modeli yükle ve fine-tuning için ayarları yap
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large')

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    # eval_dataset=val_dataset,  # Değerlendirme seti varsa eklenebilir
)

# Eğitimi başlat
trainer.train()

# Modeli kaydet
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")
