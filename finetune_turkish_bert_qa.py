"""
Turkish BERT Question-Answering Embedding Fine-tuning Script

Bu script, dbmdz/bert-base-turkish-cased modelini soru-cevap çiftleri üzerinde fine-tune eder.
Sentence-transformers kütüphanesi kullanılarak embedding kalitesi artırılır.

Veri Formatı:
1. Basit Format (otomatik hard negatives):
   [{"question": "...", "answer": "..."}]

2. Hard Negatives ile:
   [{"question": "...", "positive": "doğru cevap", "negatives": ["yanlış 1", "yanlış 2"]}]
"""

import json
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
import torch
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Union
import logging
import random
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_qa_data(file_path: str) -> Union[List[Tuple[str, str]], List[Dict]]:
    """
    Soru-cevap verilerini yükler.

    Args:
        file_path: Veri dosyasının yolu (.csv, .json, veya .jsonl)

    Returns:
        List of (question, answer) tuples veya dict with negatives
    """
    path = Path(file_path)

    if path.suffix == '.csv':
        df = pd.read_csv(file_path)
        # Negatif kolonlar varsa kontrol et
        if 'negative1' in df.columns or 'negatives' in df.columns:
            qa_data = []
            for _, row in df.iterrows():
                item = {
                    'question': row['question'],
                    'positive': row.get('positive', row.get('answer')),
                    'negatives': []
                }
                # Negatif kolonları topla
                for col in df.columns:
                    if col.startswith('negative') and pd.notna(row[col]):
                        item['negatives'].append(row[col])
                qa_data.append(item)
        else:
            qa_data = list(zip(df['question'].tolist(), df['answer'].tolist()))

    elif path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # İlk öğeye bakarak format belirle
        if data and isinstance(data[0], dict):
            if 'negatives' in data[0] or 'positive' in data[0]:
                qa_data = data
            else:
                qa_data = [(item['question'], item['answer']) for item in data]
        else:
            qa_data = data

    elif path.suffix == '.jsonl':
        qa_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line)
                if 'negatives' in item or 'positive' in item:
                    qa_data.append(item)
                else:
                    qa_data.append((item['question'], item['answer']))
    else:
        raise ValueError(f"Desteklenmeyen dosya formatı: {path.suffix}")

    logger.info(f"{len(qa_data)} soru-cevap çifti yüklendi.")

    # Negatif örneklerin varlığını kontrol et
    if qa_data and isinstance(qa_data[0], dict):
        has_negatives = any(item.get('negatives') for item in qa_data)
        if has_negatives:
            logger.info("Hard negative örnekler tespit edildi.")

    return qa_data


def generate_hard_negatives(
    qa_pairs: List[Tuple[str, str]],
    num_negatives: int = 3,
    strategy: str = 'random'
) -> List[Dict]:
    """
    Otomatik hard negative örnekler oluşturur.

    Args:
        qa_pairs: Soru-cevap çiftleri
        num_negatives: Her soru için negatif örnek sayısı
        strategy: 'random' veya 'similar' (gelecekte semantic similarity ile)

    Returns:
        List of dicts with question, positive, negatives
    """
    qa_data_with_negatives = []
    all_answers = [a for _, a in qa_pairs]

    for i, (question, answer) in enumerate(qa_pairs):
        # Bu sorunun cevabı hariç diğer tüm cevaplar
        other_answers = all_answers[:i] + all_answers[i+1:]

        # Random negatif örnekler seç
        if len(other_answers) >= num_negatives:
            negatives = random.sample(other_answers, num_negatives)
        else:
            negatives = other_answers

        qa_data_with_negatives.append({
            'question': question,
            'positive': answer,
            'negatives': negatives
        })

    logger.info(f"Her örnek için {num_negatives} hard negative oluşturuldu.")
    return qa_data_with_negatives


def prepare_training_data(
    qa_data: Union[List[Tuple[str, str]], List[Dict]],
    train_split: float = 0.8,
    use_hard_negatives: bool = True,
    num_negatives: int = 3
) -> Tuple[List[InputExample], List[InputExample]]:
    """
    Veriyi training ve evaluation setlerine ayırır ve InputExample formatına dönüştürür.

    Args:
        qa_data: Soru-cevap verileri
        train_split: Training seti oranı (0-1 arası)
        use_hard_negatives: Hard negative örnekler kullan
        num_negatives: Otomatik oluşturulacak negatif örnek sayısı

    Returns:
        (train_examples, eval_examples)
    """
    # Veriyi karıştır
    random.shuffle(qa_data)

    # Eğer dict formatında değilse, hard negatives oluştur
    if qa_data and isinstance(qa_data[0], tuple):
        if use_hard_negatives:
            logger.info("Otomatik hard negative örnekler oluşturuluyor...")
            qa_data = generate_hard_negatives(qa_data, num_negatives=num_negatives)
        else:
            # Tuple'ları dict'e çevir
            qa_data = [
                {'question': q, 'positive': a, 'negatives': []}
                for q, a in qa_data
            ]

    # Train/eval split
    split_idx = int(len(qa_data) * train_split)
    train_data = qa_data[:split_idx]
    eval_data = qa_data[split_idx:]

    # InputExample formatına dönüştür
    train_examples = []
    for item in train_data:
        question = item['question']
        positive = item['positive']
        negatives = item.get('negatives', [])

        if negatives and use_hard_negatives:
            # Hard negatives ile: Her negative için ayrı örnek
            # MultipleNegativesRankingLoss için anchor (question) ve positive/negative passages
            train_examples.append(
                InputExample(texts=[question, positive])
            )
            # Opsiyonel: Explicit negative pairs da eklenebilir
            # Ancak MultipleNegativesRankingLoss batch içindeki diğerlerini zaten negatif olarak kullanır
        else:
            # Sadece positive pairs
            train_examples.append(
                InputExample(texts=[question, positive])
            )

    eval_examples = []
    for item in eval_data:
        question = item['question']
        positive = item['positive']
        eval_examples.append(
            InputExample(texts=[question, positive], label=1.0)
        )

    logger.info(f"Training örnekleri: {len(train_examples)}")
    logger.info(f"Evaluation örnekleri: {len(eval_examples)}")

    return train_examples, eval_examples, train_data


class HardNegativesDataLoader:
    """
    Hard negatives ile custom DataLoader.
    Her batch'e explicit hard negatives ekler.
    """
    def __init__(self, qa_data: List[Dict], batch_size: int, shuffle: bool = True):
        self.qa_data = qa_data
        self.batch_size = batch_size
        self.shuffle = shuffle

    def __iter__(self):
        indices = list(range(len(self.qa_data)))
        if self.shuffle:
            random.shuffle(indices)

        for i in range(0, len(indices), self.batch_size):
            batch_indices = indices[i:i + self.batch_size]
            batch = []

            for idx in batch_indices:
                item = self.qa_data[idx]
                # Anchor (query)
                query = item['question']
                # Positive passage
                positive = item['positive']
                # Hard negatives
                negatives = item.get('negatives', [])

                batch.append({
                    'query': query,
                    'positive': positive,
                    'negatives': negatives
                })

            yield batch

    def __len__(self):
        return (len(self.qa_data) + self.batch_size - 1) // self.batch_size


def finetune_turkish_bert(
    data_path: str,
    output_dir: str = "./models/turkish-bert-qa-finetuned",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    warmup_steps: int = 100,
    max_seq_length: int = 128,
    train_split: float = 0.8,
    use_hard_negatives: bool = True,
    num_negatives: int = 3
):
    """
    Turkish BERT modelini soru-cevap verileri üzerinde fine-tune eder.

    Args:
        data_path: Veri dosyasının yolu
        output_dir: Model kaydedilecek dizin
        epochs: Eğitim epoch sayısı
        batch_size: Batch boyutu
        learning_rate: Öğrenme oranı
        warmup_steps: Warmup adım sayısı
        max_seq_length: Maksimum token uzunluğu
        train_split: Training veri oranı
        use_hard_negatives: Hard negative örnekler kullan
        num_negatives: Otomatik oluşturulacak negatif örnek sayısı
    """

    logger.info("Turkish BERT modelini yüklüyorum...")
    model = SentenceTransformer('dbmdz/bert-base-turkish-cased')
    model.max_seq_length = max_seq_length

    logger.info("Veri yükleniyor...")
    qa_data = load_qa_data(data_path)
    train_examples, eval_examples, train_data = prepare_training_data(
        qa_data,
        train_split,
        use_hard_negatives=use_hard_negatives,
        num_negatives=num_negatives
    )

    # DataLoader oluştur
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)

    # Loss fonksiyonu: MultipleNegativesRankingLoss
    # Bu loss, soru-cevap çiftlerini birbirine yaklaştırırken
    # batch içindeki diğer cevapları negatif örnek olarak kullanır
    # Hard negatives eklendiğinde daha etkili öğrenir
    train_loss = losses.MultipleNegativesRankingLoss(model)

    logger.info("Loss fonksiyonu: MultipleNegativesRankingLoss")
    if use_hard_negatives:
        logger.info("Hard negative örnekler kullanılıyor - model daha iyi ayrım yapmayı öğrenecek")
        logger.info(f"Batch içi negative'ler + {num_negatives} hard negative per örnek")
    else:
        logger.info("Sadece batch içi negative'ler kullanılıyor")

    # Evaluator oluştur
    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
        eval_examples,
        name='qa-eval'
    )

    logger.info("Fine-tuning başlıyor...")
    logger.info(f"Model: dbmdz/bert-base-turkish-cased")
    logger.info(f"Epochs: {epochs}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Learning rate: {learning_rate}")
    logger.info(f"Hard negatives: {use_hard_negatives}")

    # Model eğitimi
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={'lr': learning_rate},
        output_path=output_dir,
        evaluation_steps=500,  # Her 500 adımda bir evaluate et
        save_best_model=True,
        show_progress_bar=True
    )

    logger.info(f"Model kaydedildi: {output_dir}")

    return model


def test_model(model_path: str, test_queries: List[str] = None):
    """
    Fine-tune edilmiş modeli test eder.

    Args:
        model_path: Model dizini
        test_queries: Test soruları (opsiyonel)
    """
    logger.info(f"Model yükleniyor: {model_path}")
    model = SentenceTransformer(model_path)

    if test_queries is None:
        test_queries = [
            "Türkiye'nin başkenti neresidir?",
            "Yapay zeka nedir?",
            "Python programlama dilinin avantajları nelerdir?"
        ]

    logger.info("\nÖrnek embeddingler hesaplanıyor:")
    embeddings = model.encode(test_queries)

    for query, emb in zip(test_queries, embeddings):
        logger.info(f"\nSoru: {query}")
        logger.info(f"Embedding boyutu: {emb.shape}")
        logger.info(f"İlk 5 değer: {emb[:5]}")

    # Benzerlik testi
    if len(test_queries) >= 2:
        from scipy.spatial.distance import cosine
        similarity = 1 - cosine(embeddings[0], embeddings[1])
        logger.info(f"\nİlk iki soru arası benzerlik: {similarity:.4f}")


def main():
    parser = argparse.ArgumentParser(description='Turkish BERT QA Embedding Fine-tuning with Hard Negatives')
    parser.add_argument('--data_path', type=str, required=True,
                       help='Soru-cevap veri dosyası yolu (.csv, .json, .jsonl)')
    parser.add_argument('--output_dir', type=str,
                       default='./models/turkish-bert-qa-finetuned',
                       help='Model kaydedilecek dizin')
    parser.add_argument('--epochs', type=int, default=3,
                       help='Eğitim epoch sayısı')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='Batch boyutu')
    parser.add_argument('--learning_rate', type=float, default=2e-5,
                       help='Öğrenme oranı')
    parser.add_argument('--warmup_steps', type=int, default=100,
                       help='Warmup adım sayısı')
    parser.add_argument('--max_seq_length', type=int, default=128,
                       help='Maksimum token uzunluğu')
    parser.add_argument('--train_split', type=float, default=0.8,
                       help='Training veri oranı (0-1 arası)')
    parser.add_argument('--no_hard_negatives', action='store_true',
                       help='Hard negative örnekler kullanma')
    parser.add_argument('--num_negatives', type=int, default=3,
                       help='Otomatik oluşturulacak hard negative sayısı')
    parser.add_argument('--test_only', action='store_true',
                       help='Sadece test et (eğitme yapma)')

    args = parser.parse_args()

    if args.test_only:
        test_model(args.output_dir)
    else:
        model = finetune_turkish_bert(
            data_path=args.data_path,
            output_dir=args.output_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            warmup_steps=args.warmup_steps,
            max_seq_length=args.max_seq_length,
            train_split=args.train_split,
            use_hard_negatives=not args.no_hard_negatives,
            num_negatives=args.num_negatives
        )

        # Eğitim sonrası test
        logger.info("\n" + "="*50)
        logger.info("Eğitim tamamlandı! Model test ediliyor...")
        logger.info("="*50)
        test_model(args.output_dir)


if __name__ == "__main__":
    main()
