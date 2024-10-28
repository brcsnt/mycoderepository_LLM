import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

def generate_confusion_matrix(data, output_col, flag_col):
    # Mapping for the 'Output' column: 'Evet' -> 1, 'Hayır' -> 0
    output_mapping = {'Evet': 1, 'Hayır': 0}
    y_true = data[flag_col]
    y_pred = data[output_col].map(output_mapping)
    
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[1, 0])
    
    # Calculate metrics with '1' as the positive class
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, pos_label=1)
    recall = recall_score(y_true, y_pred, pos_label=1)
    f1 = f1_score(y_true, y_pred, pos_label=1)
    
    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Evet (1)', 'Hayır (0)'], yticklabels=['Evet (1)', 'Hayır (0)'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.show()
    
    # Print the metrics
    print("\nAccuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))

# Example usage
# Replace 'your_data.csv' with your dataset file path
data = pd.read_csv('your_data.csv')  
generate_confusion_matrix(data, 'Output', 'Flag')



"""Açıklamalar:
Haritalama:
"Evet" ve "Hayır" etiketlerini sayısal değerlere (1 ve 0) dönüştürüyoruz.
Confusion Matrix Görselleştirmesi:
seaborn'un heatmap fonksiyonunu kullanarak confusion matrix'i görselleştiriyoruz.
annot=True parametresi ile matrisin hücrelerine sayı değerlerini yazıyoruz.
fmt='d' ile sayıları tam sayı olarak görüntülüyoruz.
cmap='Blues' ile mavi renk tonlarını kullanarak görseli renklendiriyoruz.
xticklabels ve yticklabels ile etiketleri belirliyoruz.
Metriğin Hesaplanması ve Yazdırılması:
Accuracy, Precision, Recall ve F1 Score hesaplanıp ekrana yazdırılıyor."""








import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

def generate_confusion_matrix(data, output_col, flag_col):
    # Mapping for the 'Output' column: 'Evet' -> 1, 'Hayır' -> 0, 'Cevapsız' -> -1
    output_mapping = {'Evet': 1, 'Hayır': 0, 'Cevapsız': -1}
    y_true = data[flag_col]
    y_pred = data[output_col].map(output_mapping)
    
    # Extend labels to include 'Cevapsız' or equivalent label (-1)
    labels = [1, 0, -1]
    
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Evet (1)', 'Hayır (0)', 'Cevapsız (-1)'], 
                yticklabels=['Evet (1)', 'Hayır (0)', 'Cevapsız (-1)'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix Including Unanswered Cases')
    plt.show()
    
    # Calculate and print metrics excluding 'Cevapsız' cases
    y_true_filtered = y_true[y_pred != -1]
    y_pred_filtered = y_pred[y_pred != -1]
    
    if len(y_true_filtered) > 0:
        accuracy = accuracy_score(y_true_filtered, y_pred_filtered)
        precision = precision_score(y_true_filtered, y_pred_filtered, pos_label=1)
        recall = recall_score(y_true_filtered, y_pred_filtered, pos_label=1)
        f1 = f1_score(y_true_filtered, y_pred_filtered, pos_label=1)
        
        print("\nMetrics excluding unanswered cases:")
        print("Accuracy:", round(accuracy, 4))
        print("Precision:", round(precision, 4))
        print("Recall:", round(recall, 4))
        print("F1 Score:", round(f1, 4))
    else:
        print("\nNo valid cases for metrics calculation after excluding unanswered cases.")

# Example usage
# Replace 'your_data.csv' with your dataset file path
data = pd.read_csv('your_data.csv')  
generate_confusion_matrix(data, 'Output', 'Flag')


""" Açıklamalar:
Haritalama:
"Evet" ve "Hayır" etiketleri sırasıyla 1 ve 0 olarak kodlanırken, modelin cevap veremediği durumlar "Cevapsız" olarak işaretlenir ve -1 olarak kodlanır.
Confusion Matrix:
Etiketler [1, 0, -1] olarak belirlenir. Bu sayede "Cevapsız" durumları da matrisin bir parçası olur.
Görselleştirme aşamasında, "Cevapsız" durumu hem x hem de y ekseninde ayrı bir kategori olarak eklenir.
Metriğin Hesaplanması:
Cevapsız kalan durumlar (-1) hariç tutularak diğer metrikler hesaplanır ve ekrana yazdırılır.
Eğer tüm tahminler "Cevapsız" ise bu duruma özel bir mesaj gösterilir."""
