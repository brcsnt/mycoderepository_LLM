"""
LLM Client Modülü
Farklı LLM provider'larını destekleyen birleşik API
"""
import json
from typing import Dict, Optional, List
from config import Config


class LLMClient:
    """LLM API çağrılarını yöneten client sınıfı"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Args:
            provider: LLM provider (openai, anthropic, google, huggingface)
            model: Model adı
            temperature: Yaratıcılık parametresi (0-1)
            max_tokens: Maksimum token sayısı
        """
        self.provider = provider or Config.LLM_PROVIDER
        self.model = model or Config.LLM_MODEL
        self.temperature = temperature or Config.LLM_TEMPERATURE
        self.max_tokens = max_tokens or Config.LLM_MAX_TOKENS
        self.api_key = Config.get_api_key()

        self._client = self._initialize_client()

    def _initialize_client(self):
        """Provider'a göre client oluştur"""
        if self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)

        elif self.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)

        elif self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model)

        elif self.provider == "azure":
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_version="2024-02-15-preview"
            )

        else:
            raise ValueError(f"Desteklenmeyen provider: {self.provider}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """
        LLM'den yanıt oluştur

        Args:
            prompt: Kullanıcı promptu
            system_prompt: Sistem promptu
            json_mode: JSON formatında yanıt isteme

        Returns:
            LLM yanıtı (string)
        """
        try:
            if self.provider in ["openai", "azure"]:
                return self._generate_openai(prompt, system_prompt, json_mode)

            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, system_prompt, json_mode)

            elif self.provider == "google":
                return self._generate_google(prompt, system_prompt)

            else:
                raise ValueError(f"Desteklenmeyen provider: {self.provider}")

        except Exception as e:
            if Config.DEBUG_MODE:
                raise
            return f"Hata oluştu: {str(e)}"

    def _generate_openai(
        self, prompt: str, system_prompt: Optional[str], json_mode: bool
    ) -> str:
        """OpenAI API çağrısı"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _generate_anthropic(
        self, prompt: str, system_prompt: Optional[str], json_mode: bool
    ) -> str:
        """Anthropic (Claude) API çağrısı"""
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_google(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Google (Gemini) API çağrısı"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        response = self._client.generate_content(
            full_prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            },
        )
        return response.text

    def generate_json(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict:
        """
        JSON formatında yanıt oluştur

        Args:
            prompt: Kullanıcı promptu
            system_prompt: Sistem promptu

        Returns:
            JSON dict
        """
        # JSON formatı isteme talimatı ekle
        json_instruction = "\n\nYanıtını sadece geçerli JSON formatında ver, başka açıklama ekleme."
        full_prompt = prompt + json_instruction

        response = self.generate(full_prompt, system_prompt, json_mode=True)

        try:
            # Yanıtı parse et
            # Bazen LLM markdown code block içinde yanıt verebilir
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            return json.loads(response.strip())

        except json.JSONDecodeError as e:
            if Config.DEBUG_MODE:
                print(f"JSON parse hatası: {e}")
                print(f"Yanıt: {response}")

            # Fallback: Boş dict döndür
            return {}

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Çoklu mesajla sohbet

        Args:
            messages: Mesaj listesi [{"role": "user/assistant", "content": "..."}]
            system_prompt: Sistem promptu

        Returns:
            LLM yanıtı
        """
        if self.provider in ["openai", "azure"]:
            msg_list = []
            if system_prompt:
                msg_list.append({"role": "system", "content": system_prompt})
            msg_list.extend(messages)

            response = self._client.chat.completions.create(
                model=self.model,
                messages=msg_list,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = self._client.messages.create(**kwargs)
            return response.content[0].text

        else:
            # Diğer provider'lar için basit birleştirme
            combined = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            return self.generate(combined, system_prompt)


if __name__ == "__main__":
    # Test
    client = LLMClient()
    response = client.generate("Merhaba, nasılsın?")
    print(f"Yanıt: {response}")
