import pandas as pd
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch

class HybridSearch:
    def __init__(self, index_name):
        # Elasticsearch bağlantısını kur
        self.es = Elasticsearch("http://localhost:9200")
        self.index_name = index_name
        
        # Transformer modelini yükle
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
    def get_embedding(self, text):
        # Metni embedding vektörüne dönüştür
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings[0].numpy()

    def hybrid_search(self, keyword, top_n=5):
        # Anahtar kelime için embedding vektörünü oluştur
        keyword_embedding = self.get_embedding(keyword)

        # BM25 araması (keyword match)
        bm25_query = {
            "match": {
                "chunk_text": keyword  # Elasticsearch'te "chunk_text" alanında keyword aranır
            }
        }

        # Dense vector (cosine similarity) arama
        dense_vector_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'chunk_embedding_vector') + 1.0",
                    "params": {"query_vector": keyword_embedding.tolist()}
                }
            }
        }

        # Hybrid sorgu yapısı
        hybrid_query = {
            "size": top_n,
            "query": {
                "bool": {
                    "should": [
                        bm25_query,         # BM25 ile keyword araması
                        dense_vector_query  # Dense vector ile semantik arama
                    ]
                }
            }
        }

        # Elasticsearch sorgusunu çalıştır
        response = self.es.search(index=self.index_name, body=hybrid_query)

        # Sonuçları işleyerek liste halinde döndür
        results = [
            {
                "id": hit["_id"],
                "pdf_file_name": hit["_source"]["pdf_file_name"],
                "chunk_text": hit["_source"]["chunk_text"],
                "chunk_embedding_vector": hit["_source"]["chunk_embedding_vector"],
                "_score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
        
        return results

# Veri çerçevesinde her anahtar kelime için arama yap ve sonuçları yeni bir DataFrame'e kaydet
def search_keywords_and_store_results(df_keywords, index_name, top_n=5):
    # HybridSearch sınıfının örneğini oluştur
    search_instance = HybridSearch(index_name=index_name)
    
    # Sonuçları kaydedeceğimiz liste
    results_list = []
    
    # Her keyword için arama yap
    for keyword in df_keywords["keywords"]:
        # Hybrid arama yap
        search_results = search_instance.hybrid_search(keyword, top_n=top_n)
        
        # Sonuçları DataFrame yapısına uygun hale getir
        for rank, result in enumerate(search_results, start=1):
            results_list.append({
                "id": result["id"],
                "pdf_file_name": result["pdf_file_name"],
                "chunk_text": result["chunk_text"],
                "chunk_embedding_vector": result["chunk_embedding_vector"],
                "_score": result["_score"],
                "_rank": rank,
                "keywords": keyword
            })
    
    # Sonuçları bir DataFrame olarak oluştur
    results_df = pd.DataFrame(results_list)
    return results_df

# Örnek kullanım
# df_keywords: Arama yapılacak anahtar kelimelerden oluşan DataFrame
# index_name: Elasticsearch indeks adı
index_name = "my_index"
df_keywords = pd.DataFrame({"keywords": ["örnek anahtar kelime1", "örnek anahtar kelime2"]})

# Her anahtar kelime için arama yap ve sonuçları bir DataFrame'de topla
results_df = search_keywords_and_store_results(df_keywords, index_name=index_name, top_n=5)

# Sonuçları incele
print(results_df)
