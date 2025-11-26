

# 2. Gerekli kütüphaneleri yükle
!pip install -q docling

# 3. MODELLERİ KULLANMA - DÜZELTİLMİŞ KOD

print("="*60)
print("YÖNTEM 1: Pipeline Options ile (Düzeltilmiş)")
print("="*60)

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Model path'ini belirt
artifacts_path = "/content/drive/MyDrive/docling_models"

# Pipeline ayarlarını yap
pipeline_options = PdfPipelineOptions(
    artifacts_path=artifacts_path,  # Local model path
    do_ocr=True,  # OCR aktif
    do_table_structure=True,  # Tablo tanıma aktif
    do_layout_analysis=True  # Layout analizi aktif
)

# OCR ayarları (düzeltilmiş - ocr_artifacts_path parametresi yok)
pipeline_options.ocr_options = EasyOcrOptions(
    force_full_page_ocr=False,  # Sadece gerekli yerlerde OCR
    lang=["en"]  # OCR dili
)

# Converter'ı oluştur
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

print("✅ Converter başarıyla oluşturuldu!")

# Test için bir PDF dönüştür
# result = doc_converter.convert("dosya.pdf")

print("\n" + "="*60)
print("YÖNTEM 2: Environment Variable ile (EN BASİT - ÖNERİLEN)")
print("="*60)

import os

# Environment variable ayarla
os.environ['DOCLING_ARTIFACTS_PATH'] = "/content/drive/MyDrive/docling_models"

from docling.document_converter import DocumentConverter

# Direkt converter oluştur (otomatik olarak env variable'ı kullanır)
converter = DocumentConverter()

print("✅ Converter başarıyla oluşturuldu!")

print("\n" + "="*60)
print("🎯 GERÇEK KULLANIM ÖRNEĞİ")
print("="*60)

# Örnek PDF URL'si ile test
pdf_url = "/content/drive/MyDrive/ingilizce_çalışma/DECODE_PROFESSIONAL_JARGON.pdf"  # Kısa bir test PDF'i

print(f"📄 İşleniyor: {pdf_url}")

try:
    # Dönüştür (sadece ilk 2 sayfa - hızlı test için)
    result = converter.convert(pdf_url)
    
    # Sonuçları göster
    print(f"\n✅ Dönüştürme başarılı!")
    print(f"📊 Döküman Başlığı: {result.document.name}")
    print(f"📝 İşlenen Sayfa Sayısı: {len(result.document.pages)}")
    
    # İlk birkaç satırı göster
    markdown_text = result.document.export_to_markdown()
    print(f"\n📄 İlk 500 karakter:")
    print(markdown_text[:500])
    
except Exception as e:
    print(f"❌ Hata: {e}")
    print("\nModellerin doğru yüklendiğinden emin olun:")
    print("1. Modellerin /content/drive/MyDrive/docling_models klasöründe olduğunu kontrol edin")
    print("2. Gerekirse modelleri tekrar indirin")

print("\n" + "="*60)
print("💡 BASIT KULLANIM ÖRNEĞİ")
print("="*60)

print("""
# En basit kullanım:
import os
from docling.document_converter import DocumentConverter

# Model yolunu ayarla
os.environ['DOCLING_ARTIFACTS_PATH'] = "/content/drive/MyDrive/docling_models"

# Converter oluştur ve kullan
converter = DocumentConverter()
result = converter.convert("dosya.pdf")

# Markdown olarak kaydet
with open("output.md", "w") as f:
    f.write(result.document.export_to_markdown())
""")

print("\n" + "="*60)
print("🔍 MODEL KONTROLÜ")
print("="*60)

# Modellerin var olup olmadığını kontrol et
import os

model_path = "/content/drive/MyDrive/docling_models"
if os.path.exists(model_path):
    print(f"✅ Model klasörü mevcut: {model_path}")
    print("\nKlasör içeriği:")
    !ls -la {model_path} | head -10
else:
    print(f"❌ Model klasörü bulunamadı: {model_path}")
    print("\nModelleri indirmek için şu komutu çalıştırın:")
    print("!docling-tools models download")
    print("!cp -r ~/.cache/docling/models/* /content/drive/MyDrive/docling_models/")
