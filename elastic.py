def get_min_max_scores(self, text):
    # En düşük skoru almak için
    min_query = {
        "query": {
            "multi_match": {
                "query": text,
                "fields": ["chunk_text"]
            }
        },
        "sort": [
            {"_score": "asc"}
        ],
        "size": 1
    }
    min_resp = self.es_client.search(index=self.index_name, body=min_query)
    min_score = min_resp["hits"]["hits"][0]["_score"] if min_resp["hits"]["hits"] else None
    
    # En yüksek skoru almak için
    max_query = {
        "query": {
            "multi_match": {
                "query": text,
                "fields": ["chunk_text"]
            }
        },
        "sort": [
            {"_score": "desc"}
        ],
        "size": 1
    }
    max_resp = self.es_client.search(index=self.index_name, body=max_query)
    max_score = max_resp["hits"]["hits"][0]["_score"] if max_resp["hits"]["hits"] else None
    
    # Eğer skorlar aynıysa, hesaplamalarda hata çıkmaması için küçük bir fark ekleyin
    if min_score is not None and min_score == max_score:
        max_score += 1e-10
        
    return min_score, max_score
