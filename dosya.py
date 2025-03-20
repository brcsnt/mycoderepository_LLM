def get_pdf_list(self, headline_patterns=None):
    """
    headline_patterns: Hariç tutulacak regex desenlerinin listesi.
                       Varsayılan olarak aşağıdaki desenler kullanılır:
                         - "^.*borsa istanbul bistech devre kesici uygulamasi.*$"
                         - ".*yatırım fonu.*"
                       (Not: headline alanı text olduğu için analiz edilir; analyzer metni küçük harfe çevirir.)
    """
    # Varsayılan desenleri belirleyelim (küçük harf ve Lucene regex sözdizimine uygun)
    if headline_patterns is None:
        headline_patterns = [
            "^.*borsa istanbul bistech devre kesici uygulamasi.*$",
            ".*yatırım fonu.*"
        ]
    
    # Sorgu gövdesi: Tüm dokümanları getirmek için match_all kullanılıyor,
    # ancak headline alanında belirtilen regex desenlerine uyanlar hariç tutuluyor.
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "must_not": []
            }
        },
        "aggs": {
            "distinct_disclosures": {
                "terms": {
                    "field": "pdf_file_link",  # İlgili alan; kendi alan adınızı kullanın.
                    "size": 10000
                }
            }
        }
    }
    
    # Her bir regex desenini must_not kısmına ekliyoruz.
    for pattern in headline_patterns:
        query_body["query"]["bool"]["must_not"].append({
            "regexp": {
                "headline": {
                    "value": pattern
                }
            }
        })
    
    # Sorgu gövdesini kontrol amaçlı yazdırıyoruz.
    print("Elasticsearch query:", query_body)
    
    # Elasticsearch sorgusunu çalıştırıyoruz.
    response = self.es.search(index="my_index", body=query_body)
    
    return response
