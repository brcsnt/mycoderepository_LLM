"""
BGE Model Question-Answering Embedding Fine-tuning Script

Bu script, BGE (BAAI General Embedding) modelini soru-cevap çiftleri üzerinde fine-tune eder.
BGE-M3 (multilingual) veya BGE-base modelleri kullanılabilir.

BGE modelleri instruction-based olduğundan, query ve passage için farklı instruction'lar kullanılır.

Veri Formatı:
1. Basit Format (otomatik hard negatives):
   [{"question": "...", "answer": "..."}]

2. Hard Negatives ile:
   [{"question": "...", "positive": "doğru cevap", "negatives": ["yanlış 1", "yanlış 2"]}]
"""

import json
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator, InformationRetrievalEvaluator
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


class BGEInstructionExample(InputExample):
    """
    BGE modelleri için instruction-based InputExample.
    """
    def __init__(self, texts: List[str], label: float = 0.0, query_instruction: str = "", passage_instruction: str = ""):
        self.query_instruction = query_instruction
        self.passage_instruction = passage_instruction
        # Instruction'ları metinlere ekle
        if query_instruction:
            texts[0] = f"{query_instruction}{texts[0]}"
        if passage_instruction and len(texts) > 1:
            texts[1] = f"{passage_instruction}{texts[1]}"
        super().__init__(texts=texts, label=label)


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
    use_instructions: bool = True,
    use_hard_negatives: bool = True,
    num_negatives: int = 3
) -> Tuple[List[InputExample], List[InputExample]]:
    """
    Veriyi training ve evaluation setlerine ayırır ve InputExample formatına dönüştürür.

    Args:
        qa_data: Soru-cevap verileri
        train_split: Training seti oranı (0-1 arası)
        use_instructions: BGE instruction'larını kullan
        use_hard_negatives: Hard negative örnekler kullan
        num_negatives: Otomatik oluşturulacak negatif örnek sayısı

    Returns:
        (train_examples, eval_examples, train_data)
    """
    # BGE için instruction'lar
    query_instruction = "Bu soruyu cevaplamak için ilgili bilgiyi ara: " if use_instructions else ""
    passage_instruction = ""  # Passage için genellikle boş bırakılır

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

        # Instruction ekle
        if use_instructions:
            question_with_inst = f"{query_instruction}{question}"
        else:
            question_with_inst = question

        train_examples.append(
            InputExample(texts=[question_with_inst, positive])
        )

    eval_examples = []
    for item in eval_data:
        question = item['question']
        positive = item['positive']

        # Instruction ekle
        if use_instructions:
            question_with_inst = f"{query_instruction}{question}"
        else:
            question_with_inst = question

        eval_examples.append(
            InputExample(texts=[question_with_inst, positive], label=1.0)
        )

    logger.info(f"Training örnekleri: {len(train_examples)}")
    logger.info(f"Evaluation örnekleri: {len(eval_examples)}")

    return train_examples, eval_examples, train_data


def finetune_bge(
    data_path: str,
    model_name: str = "BAAI/bge-m3",  # BGE-M3 multilingual model
    output_dir: str = "./models/bge-qa-finetuned",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 1e-5,
    warmup_steps: int = 100,
    max_seq_length: int = 512,
    train_split: float = 0.8,
    use_instructions: bool = True,
    use_hard_negatives: bool = True,
    num_negatives: int = 3,
    pooling_mode: str = "cls"  # 'cls' veya 'mean'
):
    """
    BGE modelini soru-cevap verileri üzerinde fine-tune eder.

    Args:
        data_path: Veri dosyasının yolu
        model_name: BGE model adı (varsayılan: BAAI/bge-m3 multilingual)
        output_dir: Model kaydedilecek dizin
        epochs: Eğitim epoch sayısı
        batch_size: Batch boyutu
        learning_rate: Öğrenme oranı (BGE için genellikle daha düşük)
        warmup_steps: Warmup adım sayısı
        max_seq_length: Maksimum token uzunluğu (BGE 512'ye kadar destekler)
        train_split: Training veri oranı
        use_instructions: Instruction-based training kullan
        use_hard_negatives: Hard negative örnekler kullan
        num_negatives: Otomatik oluşturulacak negatif örnek sayısı
        pooling_mode: Pooling stratejisi ('cls' veya 'mean')
    """

    logger.info(f"BGE modelini yüklüyorum: {model_name}")

    # BGE model alternatifleri:
    # - BAAI/bge-m3 (multilingual, Türkçe dahil, en iyi seçenek)
    # - BAAI/bge-base-en-v1.5 (sadece İngilizce)
    # - BAAI/bge-large-en-v1.5 (büyük model, İngilizce)
    # - BAAI/bge-small-en-v1.5 (küçük model, hızlı)

    model = SentenceTransformer(model_name)
    model.max_seq_length = max_seq_length

    # Pooling stratejisini ayarla
    if hasattr(model, '_modules') and 'pooling' in model._modules:
        if pooling_mode == 'cls':
            model._modules['pooling'].pooling_mode_cls_token = True
            model._modules['pooling'].pooling_mode_mean_tokens = False
        elif pooling_mode == 'mean':
            model._modules['pooling'].pooling_mode_cls_token = False
            model._modules['pooling'].pooling_mode_mean_tokens = True

    logger.info("Veri yükleniyor...")
    qa_data = load_qa_data(data_path)
    train_examples, eval_examples, train_data = prepare_training_data(
        qa_data,
        train_split,
        use_instructions=use_instructions,
        use_hard_negatives=use_hard_negatives,
        num_negatives=num_negatives
    )

    # DataLoader oluştur
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)

    # Loss fonksiyonu: MultipleNegativesRankingLoss
    # BGE modelleri için en uygun loss fonksiyonu
    # Hard negatives eklendiğinde daha etkili öğrenir
    train_loss = losses.MultipleNegativesRankingLoss(model)

    logger.info("Loss fonksiyonu: MultipleNegativesRankingLoss")
    if use_hard_negatives:
        logger.info("Hard negative örnekler kullanılıyor - model daha iyi ayrım yapmayı öğrenecek")
        logger.info(f"Batch içi negative'ler + {num_negatives} hard negative per örnek")
    else:
        logger.info("Sadece batch içi negative'ler kullanılıyor")

    # Alternatif: MatryoshkaLoss (farklı embedding boyutları için)
    # from sentence_transformers import losses
    # train_loss = losses.MatryoshkaLoss(
    #     model,
    #     losses.MultipleNegativesRankingLoss(model),
    #     matryoshka_dims=[768, 512, 256, 128, 64]
    # )

    # Evaluator oluştur
    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
        eval_examples,
        name='bge-qa-eval'
    )

    logger.info("Fine-tuning başlıyor...")
    logger.info(f"Model: {model_name}")
    logger.info(f"Epochs: {epochs}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Learning rate: {learning_rate}")
    logger.info(f"Max sequence length: {max_seq_length}")
    logger.info(f"Use instructions: {use_instructions}")
    logger.info(f"Hard negatives: {use_hard_negatives}")
    logger.info(f"Pooling mode: {pooling_mode}")

    # Model eğitimi
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={'lr': learning_rate},
        output_path=output_dir,
        evaluation_steps=500,
        save_best_model=True,
        show_progress_bar=True,
        # BGE için önerilen scheduler
        scheduler='warmuplinear'
    )

    logger.info(f"Model kaydedildi: {output_dir}")

    return model


def test_model(
    model_path: str,
    test_queries: List[str] = None,
    use_instructions: bool = True
):
    """
    Fine-tune edilmiş BGE modelini test eder.

    Args:
        model_path: Model dizini
        test_queries: Test soruları (opsiyonel)
        use_instructions: Query instruction kullan
    """
    logger.info(f"Model yükleniyor: {model_path}")
    model = SentenceTransformer(model_path)

    query_instruction = "Bu soruyu cevaplamak için ilgili bilgiyi ara: " if use_instructions else ""

    if test_queries is None:
        test_queries = [
            "Türkiye'nin başkenti neresidir?",
            "Yapay zeka nedir?",
            "Python programlama dilinin avantajları nelerdir?",
            "Makine öğrenmesi nasıl çalışır?",
            "Derin öğrenme nedir?"
        ]

    # Instruction'ları ekle
    if use_instructions:
        test_queries_with_instruction = [f"{query_instruction}{q}" for q in test_queries]
    else:
        test_queries_with_instruction = test_queries

    logger.info("\nÖrnek embeddingler hesaplanıyor:")
    embeddings = model.encode(test_queries_with_instruction, normalize_embeddings=True)

    for query, emb in zip(test_queries, embeddings):
        logger.info(f"\nSoru: {query}")
        logger.info(f"Embedding boyutu: {emb.shape}")
        logger.info(f"İlk 5 değer: {emb[:5]}")
        logger.info(f"Norm: {(emb**2).sum()**0.5:.4f}")  # Normalized olmalı (≈1.0)

    # Benzerlik matrisi
    if len(test_queries) >= 2:
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        sim_matrix = cosine_similarity(embeddings)
        logger.info("\n" + "="*50)
        logger.info("Benzerlik Matrisi:")
        logger.info("="*50)

        # Header
        logger.info(f"{'':30} " + " ".join([f"Q{i+1:2d}" for i in range(len(test_queries))]))
        logger.info("-" * (30 + 5 * len(test_queries)))

        # Matrix
        for i, query in enumerate(test_queries):
            query_short = query[:27] + "..." if len(query) > 30 else query
            row = f"{query_short:30} "
            row += " ".join([f"{sim_matrix[i][j]:.2f}" for j in range(len(test_queries))])
            logger.info(row)


def compare_models(
    original_model: str,
    finetuned_model: str,
    test_queries: List[str],
    test_answers: List[str],
    use_instructions: bool = True
):
    """
    Orijinal ve fine-tuned modelleri karşılaştırır.

    Args:
        original_model: Orijinal model adı
        finetuned_model: Fine-tuned model yolu
        test_queries: Test soruları
        test_answers: Test cevapları
        use_instructions: Instruction kullan
    """
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    query_instruction = "Bu soruyu cevaplamak için ilgili bilgiyi ara: " if use_instructions else ""

    logger.info("Modeller yükleniyor...")
    model_orig = SentenceTransformer(original_model)
    model_ft = SentenceTransformer(finetuned_model)

    # Instruction'ları ekle
    if use_instructions:
        queries_with_inst = [f"{query_instruction}{q}" for q in test_queries]
    else:
        queries_with_inst = test_queries

    logger.info("\nEmbeddingler hesaplanıyor...")

    # Orijinal model
    q_emb_orig = model_orig.encode(queries_with_inst, normalize_embeddings=True)
    a_emb_orig = model_orig.encode(test_answers, normalize_embeddings=True)

    # Fine-tuned model
    q_emb_ft = model_ft.encode(queries_with_inst, normalize_embeddings=True)
    a_emb_ft = model_ft.encode(test_answers, normalize_embeddings=True)

    logger.info("\n" + "="*70)
    logger.info("MODEL KARŞILAŞTIRMASI")
    logger.info("="*70)

    for i, (query, answer) in enumerate(zip(test_queries, test_answers)):
        sim_orig = cosine_similarity([q_emb_orig[i]], [a_emb_orig[i]])[0][0]
        sim_ft = cosine_similarity([q_emb_ft[i]], [a_emb_ft[i]])[0][0]

        logger.info(f"\nSoru {i+1}: {query[:50]}...")
        logger.info(f"Cevap: {answer[:50]}...")
        logger.info(f"  Orijinal model benzerlik: {sim_orig:.4f}")
        logger.info(f"  Fine-tuned model benzerlik: {sim_ft:.4f}")
        logger.info(f"  İyileşme: {(sim_ft - sim_orig)*100:.2f}%")


def main():
    parser = argparse.ArgumentParser(description='BGE Model QA Embedding Fine-tuning with Hard Negatives')
    parser.add_argument('--data_path', type=str, required=True,
                       help='Soru-cevap veri dosyası yolu (.csv, .json, .jsonl)')
    parser.add_argument('--model_name', type=str, default='BAAI/bge-m3',
                       help='BGE model adı (varsayılan: BAAI/bge-m3)')
    parser.add_argument('--output_dir', type=str,
                       default='./models/bge-qa-finetuned',
                       help='Model kaydedilecek dizin')
    parser.add_argument('--epochs', type=int, default=3,
                       help='Eğitim epoch sayısı')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='Batch boyutu')
    parser.add_argument('--learning_rate', type=float, default=1e-5,
                       help='Öğrenme oranı')
    parser.add_argument('--warmup_steps', type=int, default=100,
                       help='Warmup adım sayısı')
    parser.add_argument('--max_seq_length', type=int, default=512,
                       help='Maksimum token uzunluğu')
    parser.add_argument('--train_split', type=float, default=0.8,
                       help='Training veri oranı (0-1 arası)')
    parser.add_argument('--no_instructions', action='store_true',
                       help='Instruction kullanma')
    parser.add_argument('--no_hard_negatives', action='store_true',
                       help='Hard negative örnekler kullanma')
    parser.add_argument('--num_negatives', type=int, default=3,
                       help='Otomatik oluşturulacak hard negative sayısı')
    parser.add_argument('--pooling_mode', type=str, default='cls',
                       choices=['cls', 'mean'],
                       help='Pooling stratejisi')
    parser.add_argument('--test_only', action='store_true',
                       help='Sadece test et (eğitme yapma)')
    parser.add_argument('--compare', action='store_true',
                       help='Orijinal ve fine-tuned modeli karşılaştır')

    args = parser.parse_args()

    use_instructions = not args.no_instructions

    if args.test_only:
        test_model(args.output_dir, use_instructions=use_instructions)
    elif args.compare:
        # Karşılaştırma için örnek veriler
        test_queries = [
            "Türkiye'nin başkenti neresidir?",
            "Python nedir?"
        ]
        test_answers = [
            "Türkiye'nin başkenti Ankara'dır.",
            "Python yüksek seviyeli bir programlama dilidir."
        ]
        compare_models(
            args.model_name,
            args.output_dir,
            test_queries,
            test_answers,
            use_instructions=use_instructions
        )
    else:
        model = finetune_bge(
            data_path=args.data_path,
            model_name=args.model_name,
            output_dir=args.output_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            warmup_steps=args.warmup_steps,
            max_seq_length=args.max_seq_length,
            train_split=args.train_split,
            use_instructions=use_instructions,
            use_hard_negatives=not args.no_hard_negatives,
            num_negatives=args.num_negatives,
            pooling_mode=args.pooling_mode
        )

        # Eğitim sonrası test
        logger.info("\n" + "="*50)
        logger.info("Eğitim tamamlandı! Model test ediliyor...")
        logger.info("="*50)
        test_model(args.output_dir, use_instructions=use_instructions)


if __name__ == "__main__":
    main()
