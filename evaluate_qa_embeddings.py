"""
Embedding Model Evaluation Script

Bu script, fine-tune edilmiş embedding modellerini değerlendirir.
- Accuracy, precision, recall metrikleri
- MRR (Mean Reciprocal Rank)
- NDCG (Normalized Discounted Cumulative Gain)
- Retrieval performance
"""

import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_qa_data(file_path: str) -> List[Tuple[str, str]]:
    """Soru-cevap verilerini yükler."""
    path = Path(file_path)

    if path.suffix == '.csv':
        df = pd.read_csv(file_path)
        qa_pairs = list(zip(df['question'].tolist(), df['answer'].tolist()))
    elif path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        qa_pairs = [(item['question'], item['answer']) for item in data]
    elif path.suffix == '.jsonl':
        qa_pairs = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line)
                qa_pairs.append((item['question'], item['answer']))
    else:
        raise ValueError(f"Desteklenmeyen dosya formatı: {path.suffix}")

    return qa_pairs


def calculate_retrieval_metrics(
    query_embeddings: np.ndarray,
    answer_embeddings: np.ndarray,
    k_values: List[int] = [1, 3, 5, 10]
) -> Dict[str, float]:
    """
    Retrieval metriklerini hesaplar.

    Args:
        query_embeddings: Soru embeddingleri (N x D)
        answer_embeddings: Cevap embeddingleri (N x D)
        k_values: Top-K değerleri

    Returns:
        Dictionary of metrics
    """
    n_queries = len(query_embeddings)

    # Cosine similarity matrisi hesapla (N x N)
    similarities = cosine_similarity(query_embeddings, answer_embeddings)

    metrics = {}

    # Her k değeri için accuracy hesapla (doğru cevap top-k içinde mi?)
    for k in k_values:
        correct = 0
        for i in range(n_queries):
            # Her soru için en benzer k cevabı bul
            top_k_indices = np.argsort(similarities[i])[-k:][::-1]
            # Doğru cevap top-k içindeyse correct artır
            if i in top_k_indices:
                correct += 1
        accuracy_at_k = correct / n_queries
        metrics[f'accuracy@{k}'] = accuracy_at_k

    # MRR (Mean Reciprocal Rank) hesapla
    reciprocal_ranks = []
    for i in range(n_queries):
        # Benzerlikleri sırala (en yüksekten en düşüğe)
        ranked_indices = np.argsort(similarities[i])[::-1]
        # Doğru cevabın rankını bul (1-indexed)
        rank = np.where(ranked_indices == i)[0][0] + 1
        reciprocal_ranks.append(1.0 / rank)

    metrics['mrr'] = np.mean(reciprocal_ranks)

    # NDCG@k hesapla
    for k in k_values:
        ndcg_scores = []
        for i in range(n_queries):
            # Top-k indekslerini al
            top_k_indices = np.argsort(similarities[i])[-k:][::-1]

            # Relevance scores (doğru cevap için 1, diğerleri için 0)
            relevance = np.array([1.0 if idx == i else 0.0 for idx in top_k_indices])

            # DCG hesapla
            dcg = relevance[0] + np.sum(relevance[1:] / np.log2(np.arange(2, len(relevance) + 1)))

            # IDCG (Ideal DCG) - doğru cevap ilk sıradaysa
            idcg = 1.0

            # NDCG
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcg_scores.append(ndcg)

        metrics[f'ndcg@{k}'] = np.mean(ndcg_scores)

    # Mean Average Precision (MAP)
    avg_precisions = []
    for i in range(n_queries):
        ranked_indices = np.argsort(similarities[i])[::-1]
        # Doğru cevabın rankını bul
        rank = np.where(ranked_indices == i)[0][0] + 1
        # Precision@rank
        precision_at_rank = 1.0 / rank
        avg_precisions.append(precision_at_rank)

    metrics['map'] = np.mean(avg_precisions)

    # Average similarity score for correct pairs
    correct_pair_similarities = [similarities[i][i] for i in range(n_queries)]
    metrics['avg_correct_similarity'] = np.mean(correct_pair_similarities)

    return metrics


def calculate_similarity_distribution(
    query_embeddings: np.ndarray,
    answer_embeddings: np.ndarray
) -> Dict[str, float]:
    """
    Benzerlik dağılımını analiz eder.

    Returns:
        Statistics about similarity scores
    """
    similarities = cosine_similarity(query_embeddings, answer_embeddings)
    n = len(similarities)

    # Correct pairs (diagonal)
    correct_similarities = np.array([similarities[i][i] for i in range(n)])

    # Incorrect pairs (off-diagonal)
    incorrect_similarities = []
    for i in range(n):
        for j in range(n):
            if i != j:
                incorrect_similarities.append(similarities[i][j])
    incorrect_similarities = np.array(incorrect_similarities)

    stats = {
        'correct_mean': float(np.mean(correct_similarities)),
        'correct_std': float(np.std(correct_similarities)),
        'correct_min': float(np.min(correct_similarities)),
        'correct_max': float(np.max(correct_similarities)),
        'incorrect_mean': float(np.mean(incorrect_similarities)),
        'incorrect_std': float(np.std(incorrect_similarities)),
        'incorrect_min': float(np.min(incorrect_similarities)),
        'incorrect_max': float(np.max(incorrect_similarities)),
        'separation': float(np.mean(correct_similarities) - np.mean(incorrect_similarities))
    }

    return stats


def evaluate_model(
    model_path: str,
    test_data_path: str,
    use_instructions: bool = False,
    k_values: List[int] = [1, 3, 5, 10],
    save_results: bool = True
) -> Dict:
    """
    Modeli değerlendirir.

    Args:
        model_path: Model dizini
        test_data_path: Test veri dosyası
        use_instructions: BGE instruction kullan
        k_values: Top-K değerleri
        save_results: Sonuçları dosyaya kaydet

    Returns:
        Evaluation results dictionary
    """
    logger.info(f"Model yükleniyor: {model_path}")
    model = SentenceTransformer(model_path)

    logger.info(f"Test verisi yükleniyor: {test_data_path}")
    qa_pairs = load_qa_data(test_data_path)
    questions, answers = zip(*qa_pairs)

    # BGE instruction (opsiyonel)
    query_instruction = "Bu soruyu cevaplamak için ilgili bilgiyi ara: " if use_instructions else ""

    if use_instructions:
        questions = [f"{query_instruction}{q}" for q in questions]

    logger.info(f"{len(questions)} soru-cevap çifti değerlendiriliyor...")

    # Embeddingleri hesapla
    logger.info("Soru embeddingleri hesaplanıyor...")
    query_embeddings = model.encode(questions, normalize_embeddings=True, show_progress_bar=True)

    logger.info("Cevap embeddingleri hesaplanıyor...")
    answer_embeddings = model.encode(answers, normalize_embeddings=True, show_progress_bar=True)

    # Metrikleri hesapla
    logger.info("Retrieval metrikleri hesaplanıyor...")
    retrieval_metrics = calculate_retrieval_metrics(query_embeddings, answer_embeddings, k_values)

    logger.info("Benzerlik dağılımı analiz ediliyor...")
    similarity_stats = calculate_similarity_distribution(query_embeddings, answer_embeddings)

    # Sonuçları birleştir
    results = {
        'model_path': model_path,
        'test_data_path': test_data_path,
        'num_samples': len(qa_pairs),
        'embedding_dimension': query_embeddings.shape[1],
        'use_instructions': use_instructions,
        'retrieval_metrics': retrieval_metrics,
        'similarity_statistics': similarity_stats
    }

    # Sonuçları yazdır
    print_results(results)

    # Sonuçları kaydet
    if save_results:
        output_file = f"{Path(model_path).name}_evaluation.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Sonuçlar kaydedildi: {output_file}")

    return results


def print_results(results: Dict):
    """Sonuçları güzel bir formatta yazdırır."""
    print("\n" + "="*70)
    print("EVALUATION RESULTS")
    print("="*70)

    print(f"\nModel: {results['model_path']}")
    print(f"Test Data: {results['test_data_path']}")
    print(f"Samples: {results['num_samples']}")
    print(f"Embedding Dimension: {results['embedding_dimension']}")
    print(f"Use Instructions: {results['use_instructions']}")

    print("\n" + "-"*70)
    print("RETRIEVAL METRICS")
    print("-"*70)

    metrics = results['retrieval_metrics']
    print(f"{'Metric':<20} {'Value':>10}")
    print("-" * 32)

    # Accuracy@k metrikleri
    for key in sorted(metrics.keys()):
        if key.startswith('accuracy@'):
            print(f"{key:<20} {metrics[key]:>10.4f}")

    print()

    # Diğer metrikler
    for key in ['mrr', 'map']:
        if key in metrics:
            print(f"{key.upper():<20} {metrics[key]:>10.4f}")

    print()

    # NDCG metrikleri
    for key in sorted(metrics.keys()):
        if key.startswith('ndcg@'):
            print(f"{key:<20} {metrics[key]:>10.4f}")

    print()
    print(f"{'Avg Correct Sim':<20} {metrics['avg_correct_similarity']:>10.4f}")

    print("\n" + "-"*70)
    print("SIMILARITY STATISTICS")
    print("-"*70)

    stats = results['similarity_statistics']
    print(f"\n{'Correct Pairs:':<20}")
    print(f"  Mean:              {stats['correct_mean']:>8.4f}")
    print(f"  Std:               {stats['correct_std']:>8.4f}")
    print(f"  Min:               {stats['correct_min']:>8.4f}")
    print(f"  Max:               {stats['correct_max']:>8.4f}")

    print(f"\n{'Incorrect Pairs:':<20}")
    print(f"  Mean:              {stats['incorrect_mean']:>8.4f}")
    print(f"  Std:               {stats['incorrect_std']:>8.4f}")
    print(f"  Min:               {stats['incorrect_min']:>8.4f}")
    print(f"  Max:               {stats['incorrect_max']:>8.4f}")

    print(f"\n{'Separation:':<20} {stats['separation']:>8.4f}")
    print(f"  (Correct mean - Incorrect mean)")

    print("\n" + "="*70)


def compare_models(
    model_paths: List[str],
    test_data_path: str,
    use_instructions: bool = False
) -> pd.DataFrame:
    """
    Birden fazla modeli karşılaştırır.

    Args:
        model_paths: Model dizinleri listesi
        test_data_path: Test veri dosyası
        use_instructions: BGE instruction kullan

    Returns:
        Comparison dataframe
    """
    all_results = []

    for model_path in model_paths:
        logger.info(f"\n{'='*70}")
        logger.info(f"Değerlendiriliyor: {model_path}")
        logger.info(f"{'='*70}")

        results = evaluate_model(
            model_path,
            test_data_path,
            use_instructions=use_instructions,
            save_results=False
        )

        # Sonuçları düzleştir
        flat_results = {
            'model': Path(model_path).name,
            **results['retrieval_metrics'],
            **{f'sim_{k}': v for k, v in results['similarity_statistics'].items()}
        }
        all_results.append(flat_results)

    # DataFrame oluştur
    df = pd.DataFrame(all_results)

    # Sonuçları yazdır
    print("\n" + "="*100)
    print("MODEL COMPARISON")
    print("="*100)
    print(df.to_string(index=False))
    print("="*100)

    # CSV olarak kaydet
    output_file = "model_comparison.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"\nKarşılaştırma tablosu kaydedildi: {output_file}")

    return df


def main():
    parser = argparse.ArgumentParser(description='Embedding Model Evaluation')
    parser.add_argument('--model_path', type=str, required=True,
                       help='Model dizini (veya virgülle ayrılmış model listesi)')
    parser.add_argument('--test_data', type=str, required=True,
                       help='Test veri dosyası yolu')
    parser.add_argument('--use_instructions', action='store_true',
                       help='BGE instruction kullan')
    parser.add_argument('--k_values', type=int, nargs='+', default=[1, 3, 5, 10],
                       help='Top-K değerleri (varsayılan: 1 3 5 10)')
    parser.add_argument('--compare', action='store_true',
                       help='Birden fazla modeli karşılaştır (model_path virgülle ayrılmış olmalı)')

    args = parser.parse_args()

    if args.compare:
        model_paths = [p.strip() for p in args.model_path.split(',')]
        compare_models(model_paths, args.test_data, args.use_instructions)
    else:
        evaluate_model(
            args.model_path,
            args.test_data,
            use_instructions=args.use_instructions,
            k_values=args.k_values
        )


if __name__ == "__main__":
    main()
