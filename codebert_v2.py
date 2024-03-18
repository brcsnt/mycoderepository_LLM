# Gerekli kütüphaneleri yükle
!pip install transformers
!pip install torch

import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import RobertaTokenizer, EncoderDecoderModel, Trainer, TrainingArguments

# Veri setini yükle
df = pd.read_csv("yol/dosya_adi.csv")  # Veri setinin yolu

# DataFrame'i incele
print(df.head())

# Tokenizer ve modeli yükle
tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')

def preprocess_data(df):
    inputs = df['code1'].tolist()
    targets = df['code2'].tolist()
    input_encodings = tokenizer(inputs, padding=True, truncation=True, max_length=512)
    target_encodings = tokenizer(targets, padding=True, truncation=True, max_length=512)

    return {
        'input_ids': input_encodings['input_ids'],
        'attention_mask': input_encodings['attention_mask'],
        'labels': target_encodings['input_ids']
    }

# Veri setini hazırla
processed_dataset = preprocess_data(df)

# PyTorch Dataset sınıfını tanımla
class CodeDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = item['input_ids']
        return item

    def __len__(self):
        return len(self.encodings['input_ids'])

train_dataset = CodeDataset(processed_dataset)

# Modeli yükle ve fine-tuning için ayarları yap
model = EncoderDecoderModel.from_encoder_decoder_pretrained('microsoft/codebert-base', 'microsoft/codebert-base')

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
)

# Eğitimi başlat
trainer.train()

# Modeli kaydet
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")
