"""
LLM API çağrıları ve prompt yönetimi
"""
import json
import requests
from typing import Dict, Any, Optional
from config import Config

class LLMService:
    def __init__(self):
        self.api_key = Config.LLM_API_KEY
        self.model = Config.LLM_MODEL
        self.base_url = Config.LLM_BASE_URL
        self.temperature = Config.TEMPERATURE
        self.max_tokens = Config.MAX_TOKENS
    
    def call_llm(self, prompt: str, system_prompt: str = None, 
                 response_format: str = "json") -> str:
        """
        LLM API çağrısı
        
        Args:
            prompt: Kullanıcı promptu
            system_prompt: Sistem promptu
            response_format: "json" veya "text"
        
        Returns:
            LLM yanıtı
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # JSON formatı istiyorsak response_format ekle
            if response_format == "json":
                payload["response_format"] = {"type": "json_object"}
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"❌ LLM API hatası: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {str(e)}")
            return None
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """JSON yanıtını parse et"""
        try:
            # Bazen LLM ```json ... ``` formatında döndürebilir
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse hatası: {str(e)}")
            print(f"Yanıt: {response}")
            return None
