# Importing necessary libraries
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments

# Load your dataset
dataset_path = "path_to_your_dataset.csv"
df = pd.read_csv(dataset_path)

# Assuming 'unknown code1' is input and 'unknown code2' is the target
source_texts = df['unknown code1'].tolist()
target_texts = df['unknown code2'].tolist()

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("path_to_your_codellama_tokenizer")

# Dataset class
class CodeTranslationDataset(torch.utils.data.Dataset):
    def __init__(self, tokenizer, source_texts, target_texts, max_length=512):
        self.input_ids = []
        self.attn_masks = []
        self.labels = []

        for source, target in zip(source_texts, target_texts):
            inputs = tokenizer(source, padding='max_length', max_length=max_length, truncation=True, return_tensors="pt")
            targets = tokenizer(target, padding='max_length', max_length=max_length, truncation=True, return_tensors="pt")
            self.input_ids.append(inputs.input_ids.squeeze())
            self.attn_masks.append(inputs.attention_mask.squeeze())
            self.labels.append(targets.input_ids.squeeze())

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            'input_ids': self.input_ids[idx],
            'attention_mask': self.attn_masks[idx],
            'labels': self.labels[idx]
        }

# Prepare the dataset
dataset = CodeTranslationDataset(tokenizer, source_texts, target_texts)

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

# Load the pre-trained CodeLlama model
model = AutoModelForSeq2SeqLM.from_pretrained("path_to_your_codellama_model")

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
outputs = model.generate(inputs, max_length=512)
print("Translated Code:", tokenizer.decode(outputs[0], skip_special_tokens=True))



---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------



import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW

# Load your dataset
train_df = pd.read_csv('path_to_train_dataset.csv')  # Replace with your train dataset path
test_df = pd.read_csv('path_to_test_dataset.csv')    # Replace with your test dataset path

# Dataset class
class CodeDataset(Dataset):
    def __init__(self, tokenizer, df, max_length=512):
        self.tokenizer = tokenizer
        self.input_texts = df['input_code_column'].tolist()
        self.target_texts = df['output_code_column'].tolist()
        self.max_length = max_length

    def __len__(self):
        return len(self.input_texts)

    def __getitem__(self, idx):
        source = self.tokenizer.encode_plus(self.input_texts[idx], max_length=self.max_length, padding='max_length', truncation=True, return_tensors="pt")
        target = self.tokenizer.encode_plus(self.target_texts[idx], max_length=self.max_length, padding='max_length', truncation=True, return_tensors="pt")
        return source, target

# Initialize the tokenizer
tokenizer = T5Tokenizer.from_pretrained('t5-small')  # You can replace 't5-small' with the specific model you're using

# Prepare the dataset and dataloader
train_dataset = CodeDataset(tokenizer, train_df)
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)

test_dataset = CodeDataset(tokenizer, test_df)
test_loader = DataLoader(test_dataset, batch_size=4)

# Load the T5 model
model = T5ForConditionalGeneration.from_pretrained('t5-small').to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

# Define the optimizer
optimizer = AdamW(model.parameters(), lr=5e-5)

# Fine-tuning the model
for epoch in range(3):  # Number of training epochs
    model.train()
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch[0]['input_ids'].squeeze().to(model.device)
        attention_mask = batch[0]['attention_mask'].squeeze().to(model.device)
        labels = batch[1]['input_ids'].squeeze().to(model.device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
    print(f'Epoch {epoch} completed')

# Evaluate the model
model.eval()
total_loss = 0
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch[0]['input_ids'].squeeze().to(model.device)
        attention_mask = batch[0]['attention_mask'].squeeze().to(model.device)
        labels = batch[1]['input_ids'].squeeze().to(model.device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        total_loss += outputs.loss.item()
average_loss = total_loss / len(test_loader)
print(f'Average loss on test dataset: {average_loss}')

# Save the model
model.save_pretrained('path_to_save_fine_tuned_model')


---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------

import pandas as pd
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments

# Load your dataset
train_df = pd.read_csv('path_to_train_dataset.csv')
test_df = pd.read_csv('path_to_test_dataset.csv')

# T5 expects a certain format
prefix = "translate Code to Code: "

train_df['input_code_column'] = prefix + train_df['input_code_column']
test_df['input_code_column'] = prefix + test_df['input_code_column']

# Initialize the tokenizer
tokenizer = T5Tokenizer.from_pretrained('t5-small') # Choose model size

# Tokenization
def tokenize_data(df, tokenizer, max_length=512):
    input_encodings = tokenizer(df['input_code_column'].tolist(), padding=True, truncation=True, max_length=max_length)
    target_encodings = tokenizer(df['output_code_column'].tolist(), padding=True, truncation=True, max_length=max_length)
    return input_encodings, target_encodings

# Prepare datasets
class CodeDataset(torch.utils.data.Dataset):
    def __init__(self, input_encodings, target_encodings):
        self.input_encodings = input_encodings
        self.target_encodings = target_encodings

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.input_encodings.items()}
        item['labels'] = torch.tensor(self.target_encodings['input_ids'][idx])
        return item

    def __len__(self):
        return len(self.input_encodings.input_ids)

# Tokenize the datasets
train_input_encodings, train_target_encodings = tokenize_data(train_df, tokenizer)
test_input_encodings, test_target_encodings = tokenize_data(test_df, tokenizer)

train_dataset = CodeDataset(train_input_encodings, train_target_encodings)
test_dataset = CodeDataset(test_input_encodings, test_target_encodings)

# Load the model
model = T5ForConditionalGeneration.from_pretrained('t5-small').to(device) # Choose model size

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

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Train the model
trainer.train()

# Evaluate the model
results = trainer.evaluate()

# Save the fine-tuned model
model.save_pretrained("path_to_save_fine_tuned_model")

# Output evaluation results
print("Evaluation Loss:", results["eval_loss"])



---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments

# Load your dataset
train_df = pd.read_csv('path_to_train_dataset.csv')
test_df = pd.read_csv('path_to_test_dataset.csv')

# Initialize the tokenizer for your seq2seq model
tokenizer = AutoTokenizer.from_pretrained('model_checkpoint')

# Tokenization and formatting the data
def process_data_to_model_inputs(batch):
    inputs = tokenizer(batch["input_code_column"], padding="max_length", truncation=True, max_length=512)
    outputs = tokenizer(batch["output_code_column"], padding="max_length", truncation=True, max_length=512)
    batch["input_ids"] = inputs.input_ids
    batch["attention_mask"] = inputs.attention_mask
    batch["labels"] = outputs.input_ids
    return batch

train_data = train_df.apply(process_data_to_model_inputs, axis=1)
test_data = test_df.apply(process_data_to_model_inputs, axis=1)

# Convert to PyTorch tensors
class CodeDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return {key: torch.tensor(val[index]) for key, val in self.data.items()}

train_dataset = CodeDataset(train_data)
test_dataset = CodeDataset(test_data)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01
)

# Load pre-trained model for fine-tuning
model = AutoModelForSeq2SeqLM.from_pretrained('model_checkpoint').to(device)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Fine-tune the model
trainer.train()

# Evaluate the model
eval_results = trainer.evaluate()
print(f"Test Loss: {eval_results['eval_loss']}")

# Save the fine-tuned model
model.save_pretrained("path_to_save_fine_tuned_model")




import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the tokenizer and model
model_checkpoint = "path_to_save_fine_tuned_model"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)

# Function to translate code using the model
def translate_code(model, tokenizer, code_snippet, max_length=512):
    inputs = tokenizer.encode("translate Code to Code: " + code_snippet, return_tensors="pt", max_length=max_length, truncation=True)
    outputs = model.generate(inputs, max_length=max_length)
    translated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_code

# Example code snippet
example_code_snippet = "Your code snippet here"

# Translate the code
translated_code = translate_code(model, tokenizer, example_code_snippet)
print("Original Code:", example_code_snippet)
print("Translated Code:", translated_code)



import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Function to load the model and tokenizer
@st.cache(allow_output_mutation=True)
def load_model():
    model_checkpoint = "path_to_save_fine_tuned_model"
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
    return tokenizer, model

# Function to translate code
def translate_code(tokenizer, model, code_snippet, max_length=512):
    inputs = tokenizer.encode("translate Code to Code: " + code_snippet, return_tensors="pt", max_length=max_length, truncation=True)
    outputs = model.generate(inputs, max_length=max_length)
    translated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_code

# Streamlit app layout
st.title("Code Translator App")
st.write("This app uses a fine-tuned model to translate code snippets.")

# Load model and tokenizer
tokenizer, model = load_model()

# Text area for input
input_code = st.text_area("Input your code snippet here:", height=150)

# Button to translate code
if st.button('Translate Code'):
    if input_code:
        with st.spinner('Translating...'):
            translated_code = translate_code(tokenizer, model, input_code)
            st.write("## Translated Code")
            st.code(translated_code)
    else:
        st.warning("Please input a code snippet to translate.")




---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------


# Gerekli kütüphanelerin içe aktarılması
import streamlit as st
from transformers import T5ForConditionalGeneration, T5Tokenizer

# T5 modellerini yüklemek için fonksiyon
def load_model(model_name):
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    return model, tokenizer

# Streamlit uygulaması
def main():
    # Sayfa yapılandırması
    st.set_page_config(page_title="Code Converter with T5 Models", layout="wide")

    # Başlık ve açıklama
    st.title("Code Converter using T5 Models")
    st.write("Select a T5 model and enter your code to convert it.")

    # Model seçenekleri
    model_options = {
        "Model 1": "path_or_name_of_t5_model_1",
        "Model 2": "path_or_name_of_t5_model_2",
        "Model 3": "path_or_name_of_t5_model_3"
    }
    selected_model = st.selectbox("Choose a T5 Model", list(model_options.keys()))

    # Kod girişi için metin alanı
    input_code = st.text_area("Input Code", height=250)

    # Dönüştür ve Temizle butonları
    convert_button = st.button("Convert", disabled=(input_code == ""))
    clear_button = st.button("Clear")

    # Temizle butonu işlevselliği
    if clear_button:
        st.experimental_rerun()

    # Kod dönüştürme işlemi
    if convert_button and input_code:
        # Seçilen modeli yükle
        model, tokenizer = load_model(model_options[selected_model])

        # Kodu çevir
        input_text = "translate English to Python: " + input_code  # İngilizceden Python'a çeviri varsayılıyor
        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        output_ids = model.generate(input_ids)
        output_code = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Çıktıyı göster
        st.subheader("Converted Code")
        st.code(output_code)

if __name__ == "__main__":
    main()









