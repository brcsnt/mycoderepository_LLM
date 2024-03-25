!pip install gensim datasets

import logging
import time
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from datasets import load_dataset

# Setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Load dataset
dataset = load_dataset("anjandash/java-8m-methods-v2", split={'train': 'train', 'validation': 'validation', 'test': 'test'})

# Custom iterator for dataset processing
class DatasetIterator:
    def __init__(self, dataset_split, chunk_size=100000):
        self.dataset_split = dataset_split
        self.chunk_size = chunk_size
        self.total_size = len(dataset_split)
        self.num_chunks = -(-self.total_size // chunk_size)  # Ceiling division to get total number of chunks

    def __iter__(self):
        start_time = time.time()
        for chunk_index in range(self.num_chunks):
            start_idx = chunk_index * self.chunk_size
            end_idx = start_idx + self.chunk_size
            chunk = self.dataset_split.select(range(start_idx, min(end_idx, self.total_size)))
            for example in chunk:
                words = example['text'].split()
                yield TaggedDocument(words=words, tags=[example['id']])
            # Calculate and display progress
            elapsed_time = time.time() - start_time
            chunks_processed = chunk_index + 1
            if chunks_processed < self.num_chunks:
                remaining_chunks = self.num_chunks - chunks_processed
                estimated_total_time = (elapsed_time / chunks_processed) * self.num_chunks
                estimated_remaining_time = estimated_total_time - elapsed_time
                hours, remainder = divmod(estimated_remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"{chunks_processed}/{self.num_chunks} completed, estimated remaining time: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
            else:
                print(f"All chunks processed. Total training time: {elapsed_time:.2f} seconds.")

# Initialize model with correct total_examples count for training
model = Doc2Vec(vector_size=200, window=10, min_count=5, workers=4, epochs=4)

# Build vocabulary as before
# Correctly initializing and using the vocab_iterator
vocab_iterator = DatasetIterator(dataset['train'].select(range(500000)), chunk_size=100000)

# Build the vocabulary
model.build_vocab(vocab_iterator)

# Before training, manually set the model's corpus count to the actual size of your training data
model.corpus_count = len(dataset['train']) + len(dataset['validation']) + int(len(dataset['test']) * 0.9)

# Then, proceed with training using the DatasetIterator
# Ensure train_iterator is correctly set up to iterate over the entire dataset as needed
train_iterator = DatasetIterator(dataset['train'], chunk_size=100000)
model.train(train_iterator, total_examples=model.corpus_count, epochs=model.epochs, start_alpha=model.alpha, end_alpha=model.min_alpha)


'''
# Initialize model
model = Doc2Vec(vector_size=200, window=10, min_count=5, workers=4, epochs=20)

# Prepare the iterator for vocabulary building (using a subset of the data)
vocab_iterator = DatasetIterator(dataset['train'].select(range(50000)), chunk_size=100000)  # Adjust based on available memory

# Build vocabulary
model.build_vocab(vocab_iterator)

# Train the model incrementally, displaying progress
train_iterator = DatasetIterator(dataset['train'], chunk_size=100000)
model.train(train_iterator, total_examples=model.corpus_count, epochs=model.epochs, start_alpha=model.alpha, end_alpha=model.min_alpha)
'''
# Save the model
model.save("java_8m_methods_doc2vec.model")
print("Model saved successfully.")


# Evaluation and testing should be done separately to ensure the model's performance
# can be accurately assessed without using the test data during training.
# Here, you would load your test data, preprocess it if necessary,
# and then use the model.infer_vector method to generate vectors for the test documents.
# These vectors can then be used for evaluation purposes, such as similarity comparisons
# or as input features for downstream machine learning tasks.


##################################################################################################################################################




import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import logging

# Setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Assuming your custom dataset is loaded into a DataFrame named `custom_df` with a column named 'code'
# custom_df = pd.read_csv("path/to/your/dataset.csv")  # Load your dataset here

# Example custom dataset iterator
class CustomDatasetIterator:
    def __init__(self, dataframe, column_name='code'):
        self.dataframe = dataframe
        self.column_name = column_name

    def __iter__(self):
        for index, row in self.dataframe.iterrows():
            words = row[self.column_name].split()  # Splitting the code into words
            tags = [index]  # Using the row index as a unique tag
            yield TaggedDocument(words=words, tags=tags)

# Load your pre-trained model
model_path = "java_8m_methods_doc2vec.model"  # Update this path
model = Doc2Vec.load(model_path)

# Prepare your custom dataset for training
custom_dataset_iterator = CustomDatasetIterator(custom_df, 'code')

# Optionally update the model's vocabulary with new words from the custom dataset
# model.build_vocab(custom_dataset_iterator, update=True)

# Update the model's corpus count to include the new documents
model.corpus_count += len(custom_df)

# Continue training the model with the custom dataset
model.train(custom_dataset_iterator, total_examples=model.corpus_count, epochs=model.epochs)

# Save the updated model
model.save("updated_java_8m_methods_doc2vec.model")
print("Model updated and saved successfully.")
