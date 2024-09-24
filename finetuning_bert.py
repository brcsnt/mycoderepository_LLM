import time
import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tqdm import tqdm

# Record the overall start time
overall_start_time = time.time()

# 1. Load and preprocess the dataset
print("Loading and preprocessing the dataset...")
data_start_time = time.time()

# Replace 'your_dataset.csv' with the path to your actual dataset
df = pd.read_csv('your_dataset.csv')
df = df[['keyword', 'explanation']]

# Create positive pairs (correct keyword-explanation pairs)
positive_pairs = df.copy()
positive_pairs['label'] = 1

# Create negative pairs by shuffling explanations
negative_pairs = df.copy()
negative_pairs['explanation'] = (
    df['explanation'].sample(frac=1).reset_index(drop=True)
)
negative_pairs['label'] = 0

# Combine and shuffle the pairs
all_pairs = pd.concat([positive_pairs, negative_pairs], ignore_index=True)
all_pairs = all_pairs.sample(frac=1).reset_index(drop=True)

# Split into training and validation sets
train_pairs, val_pairs = train_test_split(all_pairs, test_size=0.1)

data_end_time = time.time()
print(f"Data loading and preprocessing took {data_end_time - data_start_time:.2f} seconds.")

# 2. Initialize tokenizer and model
print("\nInitializing the tokenizer and model...")
model_start_time = time.time()

model_name = 'bert-base-uncased'  # Or any other BERT variant
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Use GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

model_end_time = time.time()
print(f"Model initialization took {model_end_time - model_start_time:.2f} seconds.")

# 3. Create custom dataset class
class KeywordExplanationDataset(Dataset):
    def __init__(self, pairs, tokenizer, max_length=128):
        self.pairs = pairs.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        row = self.pairs.iloc[idx]
        encoding = self.tokenizer(
            row['keyword'],
            row['explanation'],
            add_special_tokens=True,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt',
        )
        inputs = {key: val.squeeze(0) for key, val in encoding.items()}
        inputs['labels'] = torch.tensor(
            row['label'], dtype=torch.long
        )
        return inputs

# 4. Create DataLoader objects
print("\nCreating DataLoader objects...")
dataloader_start_time = time.time()

batch_size = 16

train_dataset = KeywordExplanationDataset(train_pairs, tokenizer)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

val_dataset = KeywordExplanationDataset(val_pairs, tokenizer)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

dataloader_end_time = time.time()
print(f"DataLoader creation took {dataloader_end_time - dataloader_start_time:.2f} seconds.")

# 5. Set up the optimizer
print("\nSetting up the optimizer...")
optimizer_start_time = time.time()

optimizer = AdamW(model.parameters(), lr=2e-5)

optimizer_end_time = time.time()
print(f"Optimizer setup took {optimizer_end_time - optimizer_start_time:.2f} seconds.")

# 6. Training loop
print("\nStarting the training loop...")
training_start_time = time.time()

epochs = 3

for epoch in range(epochs):
    print(f"\n===== Epoch {epoch + 1} / {epochs} =====")
    print("Training...")
    epoch_start_time = time.time()
    model.train()
    total_train_loss = 0

    for batch in tqdm(train_loader):
        optimizer.zero_grad()
        batch = {k: v.to(device) for k, v in batch.items()}

        outputs = model(**batch)
        loss = outputs.loss
        total_train_loss += loss.item()

        loss.backward()
        optimizer.step()

    avg_train_loss = total_train_loss / len(train_loader)
    epoch_end_time = time.time()
    print(f"Average Training Loss: {avg_train_loss:.4f}")
    print(f"Epoch training time: {epoch_end_time - epoch_start_time:.2f} seconds.")

    # Validation
    print("\nRunning Validation...")
    validation_start_time = time.time()
    model.eval()
    total_eval_loss = 0
    predictions, true_labels = [], []

    for batch in tqdm(val_loader):
        batch = {k: v.to(device) for k, v in batch.items()}

        with torch.no_grad():
            outputs = model(**batch)
            loss = outputs.loss
            logits = outputs.logits

        total_eval_loss += loss.item()

        preds = torch.argmax(logits, dim=1).cpu().numpy()
        labels = batch['labels'].cpu().numpy()

        predictions.extend(preds)
        true_labels.extend(labels)

    avg_val_loss = total_eval_loss / len(val_loader)
    accuracy = accuracy_score(true_labels, predictions)
    validation_end_time = time.time()
    print(f"Validation Loss: {avg_val_loss:.4f}")
    print(f"Validation Accuracy: {accuracy:.4f}")
    print(f"Validation time: {validation_end_time - validation_start_time:.2f} seconds.")

training_end_time = time.time()
print(f"\nTotal training time: {training_end_time - training_start_time:.2f} seconds.")

# 7. Save the fine-tuned model
print("\nSaving the fine-tuned model...")
saving_start_time = time.time()

output_dir = 'fine-tuned-bert-keyword-explanation'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

saving_end_time = time.time()
print(f"Model saving took {saving_end_time - saving_start_time:.2f} seconds.")
print(f"Model saved to {output_dir}")

# Record the overall end time
overall_end_time = time.time()
print(f"\nTotal script execution time: {overall_end_time - overall_start_time:.2f} seconds.")

# 8. Example usage of the fine-tuned model
# (Optional: Uncomment to test the model immediately)
# print("\nTesting the fine-tuned model with a sample input...")
# inference_start_time = time.time()

# Load the fine-tuned model and tokenizer
# tokenizer = BertTokenizer.from_pretrained(output_dir)
# model = BertForSequenceClassification.from_pretrained(output_dir)
# model.to(device)

# Prepare a sample input
# sample_keyword = "artificial intelligence"
# sample_explanation = "A field of study that gives computers the ability to learn."

# encoding = tokenizer(
#     sample_keyword,
#     sample_explanation,
#     add_special_tokens=True,
#     max_length=128,
#     truncation=True,
#     padding='max_length',
#     return_tensors='pt',
# )
# encoding = {k: v.to(device) for k, v in encoding.items()}

# with torch.no_grad():
#     outputs = model(**encoding)
#     logits = outputs.logits
#     predicted_class = torch.argmax(logits, dim=1).item()

# if predicted_class == 1:
#     print("The explanation matches the keyword.")
# else:
#     print("The explanation does not match the keyword.")

# inference_end_time = time.time()
# print(f"Inference time: {inference_end_time - inference_start_time:.2f} seconds.")





# Use only 1% of the dataset for estimation
subset_fraction = 0.01
train_pairs_subset = train_pairs.sample(frac=subset_fraction)
train_dataset_subset = KeywordExplanationDataset(train_pairs_subset, tokenizer)
train_loader_subset = DataLoader(train_dataset_subset, batch_size=batch_size, shuffle=True)

# Measure training time on the subset
start_time = time.time()
# ... (training loop with train_loader_subset)
end_time = time.time()
elapsed_time = end_time - start_time

# Estimate total time
estimated_total_time = elapsed_time / subset_fraction
print(f"Estimated total training time: {estimated_total_time / 60:.2f} minutes")
