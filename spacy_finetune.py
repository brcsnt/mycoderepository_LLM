# 1. Gerekli Kütüphanelerin Kurulumu
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Gerekli paketlerin kurulumu
install("spacy==3.5.0")
install("torch")
install("transformers")

import spacy

# 2. Veri Setinin Hazırlanması
import json
from spacy.tokens import DocBin

# Örnek veri seti
veriler = [
    {
        "text": "ABC Şirketi bugün yeni bir ürün tanıttı.",
        "entities": [[0, 11, "ORG"]]
    },
    {
        "text": "XYZ Holding, finans sektöründe liderdir.",
        "entities": [[0, 11, "ORG"]]
    }
]

def hazirla_veri(veriler, output_file):
    nlp = spacy.blank("tr")
    doc_bin = DocBin()
    for veri in veriler:
        text = veri['text']
        entities = veri['entities']
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in entities:
            span = doc.char_span(start, end, label=label)
            if span is None:
                print(f"Uyarı: '{text[start:end]}' için span oluşturulamadı.")
            else:
                ents.append(span)
        doc.ents = ents
        doc_bin.add(doc)
    doc_bin.to_disk(output_file)

# Eğitim verisini hazırlama
hazirla_veri(veriler, "train.spacy")

# 3. Konfigürasyon Dosyasının Oluşturulması ve Model Yolunun Belirtilmesi
from spacy.cli.init_config import init_config
from spacy.util import load_config, Config

# Temel konfigürasyon dosyasını oluşturma
init_config(
    lang="tr",
    pipeline=["transformer", "ner"],
    optimize="accuracy",
    output_path="config.cfg"
)

# Konfigürasyon dosyasını yükleme ve model yolunu ayarlama
config = load_config("config.cfg")

# Yerel modelinizin tam yolunu buraya girin
model_path = "/your/local/path/to/tr_core_news_trf"

config["components"]["transformer"]["model"]["path"] = model_path

# Veri yollarını belirtme
config["paths"]["train"] = "train.spacy"
# Eğer doğrulama veri setiniz varsa:
# config["paths"]["dev"] = "dev.spacy"

# Değişiklikleri kaydetme
config.to_disk("config.cfg")

# 4. Eğitimin Başlatılması
from spacy.cli.train import train

train(
    config_path="config.cfg",
    output_path="output",
    use_gpu=-1  # CPU kullanmak için -1, GPU kullanmak isterseniz GPU ID'sini girin (örneğin, 0)
)

# 5. Eğitilen Modelin Kullanılması
import spacy

nlp = spacy.load("./output/model-best")

doc = nlp("DEF Teknoloji yeni bir akıllı telefon piyasaya sürdü.")
for ent in doc.ents:
    print(ent.text, ent.label_)
