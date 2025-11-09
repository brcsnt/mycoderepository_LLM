"""
Evidently LLM Monitoring Modülü
LLM çıktılarını izler ve değerlendirir.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from evidently import ColumnMapping
    from evidently.report import Report
    from evidently.metric_preset import TextEvals
    from evidently.metrics import (
        ColumnSummaryMetric,
        TextDescriptorsDriftMetric,
    )
    from evidently.descriptors import (
        TextLength,
        SentenceCount,
        WordCount,
        Sentiment,
        TriggerWordsPresence,
    )
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    print("⚠️  Evidently kurulu değil. 'pip install evidently' ile kurabilirsiniz.")

from config import EvidentlyConfig


class LLMMonitor:
    """LLM çıktılarını Evidently ile izler"""

    def __init__(self, reports_dir: Optional[str] = None):
        if not EVIDENTLY_AVAILABLE:
            raise ImportError("Evidently kütüphanesi kurulu değil!")

        self.reports_dir = Path(reports_dir or EvidentlyConfig.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.data_history: List[Dict[str, Any]] = []

        print(f"✅ LLM Monitor başlatıldı. Raporlar: {self.reports_dir}")

    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """
        LLM etkileşimini kaydet

        Args:
            interaction: prompt, response, metrikler içeren dict
        """
        # Timestamp ekle
        interaction['timestamp'] = datetime.now().isoformat()

        # Temel metrikleri hesapla
        interaction['response_length'] = len(interaction.get('response', ''))
        interaction['prompt_length'] = len(interaction.get('prompt', ''))

        self.data_history.append(interaction)

        print(f"✅ Etkileşim kaydedildi. Toplam: {len(self.data_history)}")

    def create_dataframe(self) -> pd.DataFrame:
        """Kaydedilen etkileşimlerden DataFrame oluştur"""
        if not self.data_history:
            return pd.DataFrame()

        return pd.DataFrame(self.data_history)

    def generate_report(self, save: bool = True) -> Optional[Report]:
        """
        Evidently raporu oluştur

        Args:
            save: Raporu dosyaya kaydet mi?

        Returns:
            Evidently Report objesi
        """
        if not self.data_history:
            print("⚠️  Henüz veri yok, rapor oluşturulamıyor.")
            return None

        df = self.create_dataframe()

        print(f"📊 {len(df)} etkileşim için rapor oluşturuluyor...")

        # Text descriptors tanımla
        text_descriptors = [
            TextLength(column_name="response"),
            WordCount(column_name="response"),
            SentenceCount(column_name="response"),
            Sentiment(column_name="response"),
        ]

        # Evidently raporu oluştur
        report = Report(metrics=[
            TextEvals(column_name="response", descriptors=text_descriptors),
            ColumnSummaryMetric(column_name="response_time"),
            ColumnSummaryMetric(column_name="response_length"),
        ])

        # Raporu çalıştır
        report.run(reference_data=None, current_data=df)

        if save:
            # Raporu HTML olarak kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.reports_dir / f"llm_report_{timestamp}.html"

            report.save_html(str(report_path))
            print(f"✅ Rapor kaydedildi: {report_path}")

            # JSON versiyonu da kaydet
            json_path = self.reports_dir / f"llm_report_{timestamp}.json"
            report.save_json(str(json_path))
            print(f"✅ JSON rapor kaydedildi: {json_path}")

        return report

    def get_statistics(self) -> Dict[str, Any]:
        """Temel istatistikleri hesapla"""
        if not self.data_history:
            return {}

        df = self.create_dataframe()

        stats = {
            'total_interactions': len(df),
            'avg_response_time': df['response_time'].mean() if 'response_time' in df else None,
            'avg_response_length': df['response_length'].mean(),
            'avg_prompt_length': df['prompt_length'].mean(),
            'providers': df['provider'].value_counts().to_dict() if 'provider' in df else {},
            'models': df['model'].value_counts().to_dict() if 'model' in df else {},
        }

        return stats

    def save_data(self, filename: Optional[str] = None) -> None:
        """Veriyi JSON dosyasına kaydet"""
        if not self.data_history:
            print("⚠️  Kaydedilecek veri yok.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_data_{timestamp}.json"

        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data_history, f, indent=2, ensure_ascii=False)

        print(f"✅ Veri kaydedildi: {filepath}")

    def load_data(self, filepath: str) -> None:
        """JSON dosyasından veri yükle"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data_history = json.load(f)

        print(f"✅ {len(self.data_history)} etkileşim yüklendi.")

    def print_statistics(self) -> None:
        """İstatistikleri konsola yazdır"""
        stats = self.get_statistics()

        if not stats:
            print("⚠️  Henüz istatistik yok.")
            return

        print("\n" + "=" * 60)
        print("📊 LLM MONİTORİNG İSTATİSTİKLERİ")
        print("=" * 60)

        print(f"\n📈 Toplam Etkileşim: {stats['total_interactions']}")

        if stats.get('avg_response_time'):
            print(f"⏱️  Ortalama Response Time: {stats['avg_response_time']:.2f}s")

        print(f"📏 Ortalama Response Uzunluğu: {stats['avg_response_length']:.0f} karakter")
        print(f"📝 Ortalama Prompt Uzunluğu: {stats['avg_prompt_length']:.0f} karakter")

        if stats.get('providers'):
            print(f"\n🔌 Kullanılan Provider'lar:")
            for provider, count in stats['providers'].items():
                print(f"   - {provider}: {count} istek")

        if stats.get('models'):
            print(f"\n🤖 Kullanılan Modeller:")
            for model, count in stats['models'].items():
                print(f"   - {model}: {count} istek")

        print("=" * 60 + "\n")

    def analyze_quality(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Response kalitesini analiz et

        Args:
            df: Analiz edilecek DataFrame (None ise mevcut data kullanılır)

        Returns:
            Kalite metrikleri
        """
        if df is None:
            df = self.create_dataframe()

        if df.empty:
            return {}

        quality_metrics = {
            'very_short_responses': len(df[df['response_length'] < 50]),
            'very_long_responses': len(df[df['response_length'] > 1000]),
            'slow_responses': len(df[df['response_time'] > 5.0]) if 'response_time' in df else 0,
            'fast_responses': len(df[df['response_time'] < 1.0]) if 'response_time' in df else 0,
        }

        # Hata oranı
        if 'error' in df.columns:
            quality_metrics['error_rate'] = (df['error'].notna().sum() / len(df)) * 100
        else:
            quality_metrics['error_rate'] = 0.0

        return quality_metrics


if __name__ == "__main__":
    # Test
    print("🧪 Monitoring modülü test ediliyor...\n")

    monitor = LLMMonitor()

    # Örnek etkileşimler
    test_interactions = [
        {
            'prompt': 'Python nedir?',
            'response': 'Python, yüksek seviyeli, yorumlamalı bir programlama dilidir.',
            'response_time': 1.2,
            'provider': 'test',
            'model': 'test-model'
        },
        {
            'prompt': 'Machine learning nedir?',
            'response': 'Machine learning, bilgisayarların deneyimlerden öğrenmesini sağlayan yapay zeka dalıdır.',
            'response_time': 1.5,
            'provider': 'test',
            'model': 'test-model'
        }
    ]

    for interaction in test_interactions:
        monitor.add_interaction(interaction)

    monitor.print_statistics()

    print("\n✅ Monitoring modülü test tamamlandı!")
