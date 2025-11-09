"""
LLM API Client
Farklı LLM sağlayıcılarıyla iletişim kurar.
"""

import time
import requests
from typing import Dict, Any, Optional, List
from config import LLMConfig


class LLMClient:
    """Çeşitli LLM sağlayıcılarıyla etkileşim için generic client"""

    def __init__(self):
        self.config = LLMConfig.get_config()
        self.provider = self.config['provider']
        self.base_url = self.config['base_url']
        self.model = self.config['model']
        self.api_key = self.config.get('api_key')

        print(f"✅ LLM Client başlatıldı: {self.provider} - {self.model}")

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        LLM'den response üret ve metrikleri topla

        Args:
            prompt: Kullanıcı promptu
            **kwargs: Ek parametreler (temperature, max_tokens, vb.)

        Returns:
            Dict içinde response ve metrikler
        """
        start_time = time.time()

        try:
            if self.provider == 'ollama':
                response_data = self._generate_ollama(prompt, **kwargs)
            elif self.provider == 'openai':
                response_data = self._generate_openai(prompt, **kwargs)
            elif self.provider == 'huggingface':
                response_data = self._generate_huggingface(prompt, **kwargs)
            elif self.provider in ['groq', 'together']:
                # Groq ve Together OpenAI-compatible API kullanır
                response_data = self._generate_openai_compatible(prompt, **kwargs)
            else:
                raise ValueError(f"Desteklenmeyen sağlayıcı: {self.provider}")

            response_time = time.time() - start_time

            return {
                'prompt': prompt,
                'response': response_data['response'],
                'response_time': response_time,
                'model': self.model,
                'provider': self.provider,
                'metadata': response_data.get('metadata', {})
            }

        except Exception as e:
            return {
                'prompt': prompt,
                'response': f"Hata: {str(e)}",
                'response_time': time.time() - start_time,
                'model': self.model,
                'provider': self.provider,
                'error': str(e),
                'metadata': {}
            }

    def _generate_ollama(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Ollama API ile generate"""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }

        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()

        return {
            'response': data.get('response', ''),
            'metadata': {
                'total_duration': data.get('total_duration'),
                'load_duration': data.get('load_duration'),
                'eval_count': data.get('eval_count')
            }
        }

    def _generate_openai(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """OpenAI API ile generate"""
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 500),
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        data = response.json()

        return {
            'response': data['choices'][0]['message']['content'],
            'metadata': {
                'usage': data.get('usage', {}),
                'finish_reason': data['choices'][0].get('finish_reason')
            }
        }

    def _generate_openai_compatible(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """OpenAI-compatible API'ler için (Groq, Together)"""
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 500),
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        data = response.json()

        return {
            'response': data['choices'][0]['message']['content'],
            'metadata': {
                'usage': data.get('usage', {}),
                'finish_reason': data['choices'][0].get('finish_reason')
            }
        }

    def _generate_huggingface(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Hugging Face Inference API ile generate"""
        url = f"{self.base_url}/{self.model}"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": kwargs.get('temperature', 0.7),
                "max_new_tokens": kwargs.get('max_tokens', 500),
                "return_full_text": False
            }
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        data = response.json()

        # Hugging Face response formatı farklı olabilir
        if isinstance(data, list):
            response_text = data[0].get('generated_text', '')
        else:
            response_text = data.get('generated_text', '')

        return {
            'response': response_text,
            'metadata': {}
        }

    def batch_generate(self, prompts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Birden fazla prompt için batch generation"""
        results = []

        for i, prompt in enumerate(prompts):
            print(f"Processing {i+1}/{len(prompts)}...")
            result = self.generate(prompt, **kwargs)
            results.append(result)

        return results


if __name__ == "__main__":
    # Test
    client = LLMClient()

    test_prompt = "Python'da 'Hello World' nasıl yazdırılır? Kısa bir örnek göster."

    print(f"\n📝 Test Prompt: {test_prompt}")
    print("=" * 60)

    result = client.generate(test_prompt)

    print(f"\n🤖 Response: {result['response']}")
    print(f"⏱️  Response Time: {result['response_time']:.2f}s")
    print(f"🏷️  Model: {result['model']}")
    print(f"📊 Metadata: {result['metadata']}")
