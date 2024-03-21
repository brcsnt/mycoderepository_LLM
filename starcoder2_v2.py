import os
import torch
import pandas as pd
from transformers import (
    AutoModelForCausalLM, 
    Trainer, 
    TrainingArguments,
    DataCollatorForLanguageModeling,
    PreTrainedTokenizerFast,
)
from datasets import Dataset
from accelerate import Accelerator

# Assuming 'df' is your DataFrame with 'input' and 'output' columns
# Example: df = pd.DataFrame({'input': ['print("Hello, World!")'], 'output': ['console.log("Hello, World!");']})

def prepare_dataset(df):
    # Convert the DataFrame into Hugging Face's Dataset format
    dataset = Dataset.from_pandas(df)
    
    # You might need to customize this function to properly format your dataset
    def tokenize_function(examples):
        # Concatenate input and output texts, separated by a special token (e.g., <|endoftext|>)
        # Adjust this based on how your tokenizer expects the data
        concatenated_examples = [inp + tokenizer.sep_token + out for inp, out in zip(examples['input'], examples['output'])]
        return tokenizer(concatenated_examples, max_length=args.max_seq_length, truncation=True, padding="max_length")
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    return tokenized_dataset

def main():
    # Replace 'your_tokenizer_model' with the appropriate tokenizer for your model
    global tokenizer
    tokenizer = PreTrainedTokenizerFast.from_pretrained("bigcode/starcoder2-3b")
    
    # Convert DataFrame to tokenized dataset
    tokenized_data = prepare_dataset(df)

    model = AutoModelForCausalLM.from_pretrained("bigcode/starcoder2-3b")

    # Use Accelerator for distributed training support
    accelerator = Accelerator()

    training_args = TrainingArguments(
        output_dir="finetune_starcoder2",
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=10_000,
        save_total_limit=2,
        prediction_loss_only=True,
    )

    # Prepare data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_data,
    )

    # Train
    trainer.train()

    # Save the model
    trainer.save_model("finetune_starcoder2_final")

    print("Training Done! 💥")

if __name__ == "__main__":
    main()


###########################################################################################################################################




from transformers import (
    AutoModelForCausalLM, 
    Trainer, 
    TrainingArguments, 
    PreTrainedTokenizerFast, 
    BitsAndBytesConfig
)

# Other imports remain the same

def main():
    global tokenizer
    tokenizer = PreTrainedTokenizerFast.from_pretrained("bigcode/starcoder2-3b")
    
    # Convert DataFrame to tokenized dataset
    tokenized_data = prepare_dataset(df)

    # BitsAndBytesConfig for model quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,  # Enable loading the model in 4-bit quantization
        bnb_4bit_quant_type="nf4",  # Quantization type
        bnb_4bit_compute_dtype=torch.bfloat16,  # Compute data type
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        "bigcode/starcoder2-3b",
        quantization_config=bnb_config,  # Apply quantization configuration
    )

    # Accelerator, TrainingArguments, and Trainer initialization remain the same

    # Initialize Trainer with model, args, data collator, and dataset
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_data,
    )

    # Training and model saving remain the same

if __name__ == "__main__":
    main()


##############################################################################################################################



import argparse
import os
import pandas as pd
from transformers import (
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    TextDatasetForNextTokenPrediction,
    DataCollatorForLanguageModeling,
    PreTrainedTokenizerFast,
    BitsAndBytesConfig,
    LoraConfig,
)
from datasets import Dataset
import torch

# Örnek DataFrame (df) varsayımı
# df = pd.DataFrame({'input': ['kod parçası 1', 'kod parçası 2'], 'output': ['çevrilen kod 1', 'çevrilen kod 2']})

def prepare_dataset(df, tokenizer, max_seq_length):
    # DataFrame'i Dataset formatına çevir
    def tokenize_function(examples):
        # Model için uygun formatta veriyi hazırla
        concatenated_examples = [inp + tokenizer.sep_token + out for inp, out in zip(examples['input'], examples['output'])]
        return tokenizer(concatenated_examples, max_length=max_seq_length, truncation=True, padding="max_length")
    
    dataset = Dataset.from_pandas(df)
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    return tokenized_dataset

def main():
    # Args değerlerini sabit olarak tanımla
    args = {
        "model_id": "bigcode/starcoder2-3b",
        "max_seq_length": 1024,
        "micro_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "weight_decay": 0.01,
        "bf16": True,
        "attention_dropout": 0.1,
        "learning_rate": 2e-4,
        "lr_scheduler_type": "cosine",
        "warmup_steps": 100,
        "seed": 0,
        "output_dir": "finetune_starcoder2",
        "push_to_hub": False,
    }

    tokenizer = PreTrainedTokenizerFast.from_pretrained(args["model_id"])
    model = AutoModelForCausalLM.from_pretrained(
        args["model_id"],
        attention_dropout=args["attention_dropout"],
        torch_dtype=torch.bfloat16 if args["bf16"] else None,
    )

    # DataFrame'den dataset hazırla
    df = pd.read_csv("your_dataset.csv")  # DataFrame'inizi yükleyin
    tokenized_dataset = prepare_dataset(df, tokenizer, args["max_seq_length"])

    # TrainingArguments ve Trainer tanımla
    training_args = TrainingArguments(
        output_dir=args["output_dir"],
        per_device_train_batch_size=args["micro_batch_size"],
        gradient_accumulation_steps=args["gradient_accumulation_steps"],
        learning_rate=args["learning_rate"],
        num_train_epochs=3,
        weight_decay=args["weight_decay"],
        logging_dir="./logs",
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # Modeli eğit
    trainer.train()

    # Modeli kaydet
    trainer.save_model(args["output_dir"])
    if args["push_to_hub"]:
        trainer.push_to_hub()

if __name__ == "__main__":
    main()
