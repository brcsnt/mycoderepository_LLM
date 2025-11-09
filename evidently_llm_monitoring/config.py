"""
Evidently LLM Monitoring - Konfigürasyon Dosyası
Bu dosya LLM API ve Evidently ayarlarını içerir.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# .env dosyasından environment variables yükle
load_dotenv()


class LLMConfig:
    """LLM API Konfigürasyonu"""

    # Kullanılabilir LLM Sağlayıcıları
    PROVIDERS = {
        'openai': {
            'api_key_env': 'OPENAI_API_KEY',
            'base_url': 'https://api.openai.com/v1',
            'default_model': 'gpt-3.5-turbo'
        },
        'huggingface': {
            'api_key_env': 'HUGGINGFACE_API_KEY',
            'base_url': 'https://api-inference.huggingface.co/models',
            'default_model': 'mistralai/Mistral-7B-Instruct-v0.2'
        },
        'ollama': {
            'api_key_env': None,  # Ollama yerel çalışır, API key gerektirmez
            'base_url': 'http://localhost:11434',
            'default_model': 'llama2'
        },
        'groq': {
            'api_key_env': 'GROQ_API_KEY',
            'base_url': 'https://api.groq.com/openai/v1',
            'default_model': 'mixtral-8x7b-32768'
        },
        'together': {
            'api_key_env': 'TOGETHER_API_KEY',
            'base_url': 'https://api.together.xyz/v1',
            'default_model': 'mistralai/Mixtral-8x7B-Instruct-v0.1'
        }
    }

    # Aktif sağlayıcı (varsayılan: Ollama - ücretsiz ve yerel)
    ACTIVE_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Aktif sağlayıcının konfigürasyonunu döndür"""
        provider_config = cls.PROVIDERS.get(cls.ACTIVE_PROVIDER)

        if not provider_config:
            raise ValueError(f"Geçersiz LLM sağlayıcı: {cls.ACTIVE_PROVIDER}")

        config = {
            'provider': cls.ACTIVE_PROVIDER,
            'base_url': provider_config['base_url'],
            'model': os.getenv('LLM_MODEL', provider_config['default_model']),
        }

        # API key varsa ekle
        if provider_config['api_key_env']:
            api_key = os.getenv(provider_config['api_key_env'])
            if not api_key and cls.ACTIVE_PROVIDER != 'ollama':
                print(f"⚠️  Uyarı: {provider_config['api_key_env']} bulunamadı!")
            config['api_key'] = api_key

        return config


class EvidentlyConfig:
    """Evidently Monitoring Konfigürasyonu"""

    # Raporların kaydedileceği dizin
    REPORTS_DIR = os.getenv('EVIDENTLY_REPORTS_DIR', './evidently_reports')

    # Monitoring metrik eşikleri
    THRESHOLDS = {
        'min_response_length': 10,
        'max_response_length': 2000,
        'min_sentiment_score': -0.5,
        'max_toxicity_score': 0.3,
    }

    # İzlenecek metrikler
    METRICS = [
        'response_length',
        'sentiment',
        'toxicity',
        'response_time',
        'token_count'
    ]

    # Dashboard portu
    DASHBOARD_PORT = int(os.getenv('EVIDENTLY_DASHBOARD_PORT', 8080))
