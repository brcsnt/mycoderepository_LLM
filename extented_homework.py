# Defining the new static thresholds for categorizing text length including "very long" category
def categorize_text_length_extended(length):
    if length <= 300:
        return "very short"
    elif 301 <= length <= 600:
        return "short"
    elif 601 <= length <= 900:
        return "medium"
    elif 901 <= length <= 1200:
        return "long"
    else:
        return "very long"

# Adding a new column for text length (number of characters) and categorizing it with the extended categories
df_train_sample['text_length'] = df_train_sample['text'].apply(len)
df_train_sample['length_category'] = df_train_sample['text_length'].apply(categorize_text_length_extended)


# Adding a new column for text length (number of characters) and categorizing it with the extended categories
df_test_sample['text_length'] = df_test_sample['text'].apply(len)
df_test_sample['length_category'] = df_test_sample['text_length'].apply(categorize_text_length_extended)

# Displaying the updated DataFrame with the text_length and length_category columns
df_test_sample[['text', 'text_length', 'length_category','label']].head()
