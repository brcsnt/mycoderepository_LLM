"""
Turkish BERT Question-Answering Embedding Fine-tuning Script

Bu script, dbmdz/bert-base-turkish-cased modelini soru-cevap çiftleri üzerinde fine-tune eder.
Sentence-transformers kütüphanesi kullanılarak embedding kalitesi artırılır.

Veri Formatı:
- CSV veya JSON formatında soru-cevap çiftleri
- Kolonlar: 'question' (soru), 'answer' (cevap)
"""

import json
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
import torch
import argparse
from pathlib import Path
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_qa_data(file_path: str) -> List[Tuple[str, str]]:
    """
    Soru-cevap verilerini yükler.

    Args:
        file_path: Veri dosyasının yolu (.csv, .json, veya .jsonl)

    Returns:
        List of (question, answer) tuples
    """
    path = Path(file_path)

    if path.suffix == '.csv':
        df = pd.read_csv(file_path)
        # CSV kolonlarının 'question' ve 'answer' olduğu varsayılıyor
        # Farklı kolon isimleri varsa buradan değiştirin
        qa_pairs = list(zip(df['question'].tolist(), df['answer'].tolist()))

    elif path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # JSON formatı: [{"question": "...", "answer": "..."}, ...]
        qa_pairs = [(item['question'], item['answer']) for item in data]

    elif path.suffix == '.jsonl':
        qa_pairs = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line)
                qa_pairs.append((item['question'], item['answer']))
    else:
        raise ValueError(f"Desteklenmeyen dosya formatı: {path.suffix}")

    logger.info(f"{len(qa_pairs)} soru-cevap çifti yüklendi.")
    return qa_pairs


def prepare_training_data(qa_pairs: List[Tuple[str, str]],
                         train_split: float = 0.8) -> Tuple[List[InputExample], List[InputExample]]:
    """
    Veriyi training ve evaluation setlerine ayırır ve InputExample formatına dönüştürür.

    Args:
        qa_pairs: Soru-cevap çiftleri listesi
        train_split: Training seti oranı (0-1 arası)

    Returns:
        (train_examples, eval_examples)
    """
    # Veriyi karıştır
    import random
    random.shuffle(qa_pairs)

    # Train/eval split
    split_idx = int(len(qa_pairs) * train_split)
    train_pairs = qa_pairs[:split_idx]
    eval_pairs = qa_pairs[split_idx:]

    # InputExample formatına dönüştür
    # Soru ve cevap aynı anlama geldiği için label=1.0 (similarity score)
    train_examples = [
        InputExample(texts=[q, a], label=1.0)
        for q, a in train_pairs
    ]

    eval_examples = [
        InputExample(texts=[q, a], label=1.0)
        for q, a in eval_pairs
    ]

    logger.info(f"Training örnekleri: {len(train_examples)}")
    logger.info(f"Evaluation örnekleri: {len(eval_examples)}")

    return train_examples, eval_examples


def finetune_turkish_bert(
    data_path: str,
    output_dir: str = "./models/turkish-bert-qa-finetuned",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    warmup_steps: int = 100,
    max_seq_length: int = 128,
    train_split: float = 0.8
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
    """

    logger.info("Turkish BERT modelini yüklüyorum...")
    model = SentenceTransformer('dbmdz/bert-base-turkish-cased')
    model.max_seq_length = max_seq_length

    logger.info("Veri yükleniyor...")
    qa_pairs = load_qa_data(data_path)
    train_examples, eval_examples = prepare_training_data(qa_pairs, train_split)

    # DataLoader oluştur
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)

    # Loss fonksiyonu: MultipleNegativesRankingLoss
    # Bu loss, soru-cevap çiftlerini birbirine yaklaştırırken
    # batch içindeki diğer cevapları negatif örnek olarak kullanır
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # Alternatif loss fonksiyonları:
    # 1. CosineSimilarityLoss - Basit cosine similarity
    # train_loss = losses.CosineSimilarityLoss(model)

    # 2. ContrastiveLoss - Positive ve negative pairs ile
    # train_loss = losses.ContrastiveLoss(model)

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
    parser = argparse.ArgumentParser(description='Turkish BERT QA Embedding Fine-tuning')
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
            train_split=args.train_split
        )

        # Eğitim sonrası test
        logger.info("\n" + "="*50)
        logger.info("Eğitim tamamlandı! Model test ediliyor...")
        logger.info("="*50)
        test_model(args.output_dir)


if __name__ == "__main__":
    main()
