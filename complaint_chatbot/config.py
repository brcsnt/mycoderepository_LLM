"""
Uygulama yapılandırma ayarları
.env dosyasından ortam değişkenlerini okur
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """Uygulama yapılandırma sınıfı"""

    # Proje root dizini
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"

    # LLM Provider Ayarları
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")

    # Excel Dosya Yolu
    EXCEL_PATH = os.getenv("EXCEL_PATH", str(DATA_DIR / "categories_template.xlsx"))

    # Debug
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

    @classmethod
    def get_api_key(cls) -> str:
        """Seçili provider için API key döndür"""
        provider_key_map = {
            "openai": cls.OPENAI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "google": cls.GOOGLE_API_KEY,
            "huggingface": cls.HUGGINGFACE_API_KEY,
            "azure": cls.AZURE_OPENAI_API_KEY,
        }

        api_key = provider_key_map.get(cls.LLM_PROVIDER, "")

        if not api_key:
            raise ValueError(
                f"API key bulunamadı! {cls.LLM_PROVIDER.upper()}_API_KEY "
                "ortam değişkenini .env dosyasında tanımlayın."
            )

        return api_key

    @classmethod
    def validate(cls):
        """Yapılandırma ayarlarını doğrula"""
        errors = []

        # API key kontrolü
        try:
            cls.get_api_key()
        except ValueError as e:
            errors.append(str(e))

        # Excel dosya kontrolü
        if not os.path.exists(cls.EXCEL_PATH):
            errors.append(f"Excel dosyası bulunamadı: {cls.EXCEL_PATH}")

        if errors:
            raise ValueError(
                "Yapılandırma hataları:\n" + "\n".join(f"- {e}" for e in errors)
            )

        return True

    @classmethod
    def info(cls) -> dict:
        """Yapılandırma bilgilerini döndür"""
        return {
            "llm_provider": cls.LLM_PROVIDER,
            "llm_model": cls.LLM_MODEL,
            "temperature": cls.LLM_TEMPERATURE,
            "max_tokens": cls.LLM_MAX_TOKENS,
            "excel_path": cls.EXCEL_PATH,
            "debug_mode": cls.DEBUG_MODE,
        }


if __name__ == "__main__":
    # Test
    try:
        Config.validate()
        print("✓ Yapılandırma başarılı!")
        print("\nAyarlar:")
        for key, value in Config.info().items():
            print(f"  {key}: {value}")
    except ValueError as e:
        print(f"✗ Yapılandırma hatası:\n{e}")
