# Importing necessary libraries
import pandas as pd
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments

# Load your dataset
dataset_path = "path_to_your_dataset.csv"
df = pd.read_csv(dataset_path)

# Assuming 'code' is the source and 'summary' is the target
source_texts = df['code'].tolist()
target_texts = df['summary'].tolist()

# Initialize the tokenizer
tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")

# Dataset class for code summarization
class CodeSummarizationDataset(torch.utils.data.Dataset):
    def __init__(self, tokenizer, source_texts, target_texts, max_length=512):
        self.encodings = []
        self.labels = []

        for source, target in zip(source_texts, target_texts):
            encoding = tokenizer(source, padding='max_length', max_length=max_length, truncation=True, return_tensors="pt")
            self.encodings.append(encoding)
            self.labels.append(target)

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item

# Prepare the dataset
dataset = CodeSummarizationDataset(tokenizer, source_texts, target_texts)

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

# Load the pre-trained CodeBERT model
model = RobertaForSequenceClassification.from_pretrained("microsoft/codebert-base")

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("path_to_save_fine_tuned_model")

# Testing with an example
test_source_code = "Example source code snippet"
inputs = tokenizer.encode(test_source_code, return_tensors='pt')
outputs = model(inputs)
print("Summary:", outputs)
