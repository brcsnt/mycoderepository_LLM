# Gerekli kütüphaneleri yükle
!pip install transformers
!pip install torch

import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, AdamW, get_scheduler
from tqdm.auto import tqdm

# Veri setini yükle ve ön işleme
df = pd.read_csv('path/to/your/dataset.csv')  # Veri seti yolu

# `code1` ve `code2`'yi birleştir ve ayrıcı tokenlar ekleyerek tek bir metin olarak hazırla
df['input_output'] = df['code1'] + " <|separator|> " + df['code2']

print(df.head())

# Dataset ve Dataloader'ın Hazırlanması
class CodeDataset(Dataset):
    def __init__(self, tokenizer, dataframe, max_length):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        encoding = self.tokenizer(self.data.iloc[idx]['input_output'],
                                  return_tensors='pt',
                                  max_length=self.max_length,
                                  padding='max_length',
                                  truncation=True)
        labels = encoding.input_ids.clone()
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            'input_ids': encoding.input_ids.squeeze(),
            'attention_mask': encoding.attention_mask.squeeze(),
            'labels': labels.squeeze()
        }

tokenizer = AutoTokenizer.from_pretrained('starcoder2-checkpoint')
dataset = CodeDataset(tokenizer, df, max_length=512)
loader = DataLoader(dataset, batch_size=4, shuffle=True)

# Modelin Hazırlanması ve Eğitimi
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = AutoModelForCausalLM.from_pretrained('starcoder2-checkpoint').to(device)
model.train()

optimizer = AdamW(model.parameters(), lr=5e-5)
num_epochs = 3
num_training_steps = num_epochs * len(loader)
lr_scheduler = get_scheduler("linear",
                             optimizer=optimizer,
                             num_warmup_steps=0,
                             num_training_steps=num_training_steps)

progress_bar = tqdm(range(num_training_steps))

for epoch in range(num_epochs):
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)
        
    print(f"Epoch {epoch+1}, Loss: {loss.item()}")

# Modeli kaydet
model.save_pretrained('./fine_tuned_starcoder2')
tokenizer.save_pretrained('./fine_tuned_starcoder2')
