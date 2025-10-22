"""
Konfigürasyon dosyası
API key ve genel ayarlar burada
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM API Ayarları
    LLM_API_KEY = os.getenv("LLM_API_KEY", "your-api-key-here")
    LLM_MODEL = "gpt-4"  # veya kullandığın model
    LLM_BASE_URL = "https://api.openai.com/v1"  # veya kendi endpoint'in
    
    # Excel Dosya Yolu
    EXCEL_FILE_PATH = "categories.xlsx"
    
    # Streamlit Ayarları
    PAGE_TITLE = "Şikayet Yönetim Sistemi"
    PAGE_ICON = "💬"
    
    # LLM Parametreleri
    TEMPERATURE = 0.3
    MAX_TOKENS = 1000
    
    # Diğer Ayarlar
    DEBUG_MODE = True
