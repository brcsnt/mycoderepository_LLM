"""
Örnek Kullanım Senaryoları
Bu dosya farklı kullanım örneklerini gösterir.
"""

from llm_client import LLMClient
from monitoring import LLMMonitor


def example_1_basic_usage():
    """Örnek 1: Temel Kullanım"""
    print("\n" + "=" * 60)
    print("📝 ÖRNEK 1: TEMEL KULLANIM")
    print("=" * 60 + "\n")

    # Client ve monitor başlat
    client = LLMClient()
    monitor = LLMMonitor()

    # Tek bir soru sor
    prompt = "Python'da fonksiyon nasıl tanımlanır?"
    result = client.generate(prompt)

    print(f"Soru: {prompt}")
    print(f"Cevap: {result['response']}")
    print(f"Süre: {result['response_time']:.2f}s\n")

    # Monitoring'e kaydet
    monitor.add_interaction(result)


def example_2_batch_processing():
    """Örnek 2: Toplu İşleme"""
    print("\n" + "=" * 60)
    print("📦 ÖRNEK 2: TOPLU İŞLEME")
    print("=" * 60 + "\n")

    client = LLMClient()
    monitor = LLMMonitor()

    # Birden fazla soru
    prompts = [
        "JavaScript'te arrow function nedir?",
        "React hooks neden kullanılır?",
        "RESTful API'nin temel prensipleri nelerdir?",
    ]

    # Batch olarak işle
    results = client.batch_generate(prompts)

    # Tümünü monitöre ekle
    for result in results:
        monitor.add_interaction(result)

    # İstatistikleri göster
    monitor.print_statistics()


def example_3_quality_monitoring():
    """Örnek 3: Kalite İzleme"""
    print("\n" + "=" * 60)
    print("📊 ÖRNEK 3: KALİTE İZLEME")
    print("=" * 60 + "\n")

    client = LLMClient()
    monitor = LLMMonitor()

    # Test soruları
    test_prompts = [
        "Python nedir?",
        "Machine learning algoritmaları hakkında detaylı bilgi ver.",
        "SQL JOIN türleri nelerdir ve nasıl kullanılır?",
        "Docker container'ların avantajları?",
        "Kubernetes nedir?",
    ]

    # İşle
    for prompt in test_prompts:
        result = client.generate(prompt)
        monitor.add_interaction(result)

    # Kalite analizi
    quality = monitor.analyze_quality()

    print("📈 Kalite Metrikleri:")
    print(f"   - Çok kısa cevaplar: {quality.get('very_short_responses', 0)}")
    print(f"   - Çok uzun cevaplar: {quality.get('very_long_responses', 0)}")
    print(f"   - Yavaş cevaplar: {quality.get('slow_responses', 0)}")
    print(f"   - Hızlı cevaplar: {quality.get('fast_responses', 0)}")
    print(f"   - Hata oranı: {quality.get('error_rate', 0):.1f}%\n")


def example_4_report_generation():
    """Örnek 4: Evidently Raporu Oluşturma"""
    print("\n" + "=" * 60)
    print("📄 ÖRNEK 4: RAPOR OLUŞTURMA")
    print("=" * 60 + "\n")

    client = LLMClient()
    monitor = LLMMonitor()

    # Veri topla
    prompts = [
        "Python ile web scraping nasıl yapılır?",
        "Git workflow best practices nelerdir?",
        "CI/CD pipeline nedir?",
        "Mikroservis mimarisi avantajları?",
        "Database indexing nasıl çalışır?",
    ]

    for prompt in prompts:
        result = client.generate(prompt)
        monitor.add_interaction(result)

    # Evidently raporu oluştur
    print("Evidently raporu oluşturuluyor...")
    report = monitor.generate_report()

    # Veriyi de kaydet
    monitor.save_data()

    print("\n✅ Rapor ve veri başarıyla kaydedildi!")


def example_5_model_comparison():
    """Örnek 5: Model Karşılaştırma"""
    print("\n" + "=" * 60)
    print("🔬 ÖRNEK 5: MODEL KARŞILAŞTIRMA")
    print("=" * 60 + "\n")

    # Aynı prompt'u farklı ayarlarla test et
    test_prompt = "Machine learning ve deep learning arasındaki farklar nelerdir?"

    client = LLMClient()
    monitor = LLMMonitor()

    # Farklı temperature değerleri ile test et
    temperatures = [0.3, 0.7, 1.0]

    for temp in temperatures:
        print(f"\nTemperature: {temp}")
        result = client.generate(test_prompt, temperature=temp)
        result['temperature'] = temp  # Metadataya ekle
        monitor.add_interaction(result)

        print(f"Response uzunluğu: {len(result['response'])} karakter")
        print(f"Süre: {result['response_time']:.2f}s")

    # İstatistikleri göster
    monitor.print_statistics()


def example_6_error_handling():
    """Örnek 6: Hata Yönetimi"""
    print("\n" + "=" * 60)
    print("⚠️  ÖRNEK 6: HATA YÖNETİMİ")
    print("=" * 60 + "\n")

    client = LLMClient()
    monitor = LLMMonitor()

    # Normal ve potansiyel problemli promptlar
    prompts = [
        "Normal bir soru: Python nedir?",
        "",  # Boş prompt
        "Çok uzun bir prompt: " + "lorem ipsum " * 500,  # Çok uzun prompt
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\nTest {i}:")
        result = client.generate(prompt)

        if 'error' in result:
            print(f"❌ Hata: {result['error']}")
        else:
            print(f"✅ Başarılı: {len(result['response'])} karakter")

        monitor.add_interaction(result)

    # Hata analizi
    quality = monitor.analyze_quality()
    print(f"\n📊 Hata oranı: {quality.get('error_rate', 0):.1f}%")


def main():
    """Tüm örnekleri çalıştır"""
    print("\n" + "=" * 60)
    print("🎓 EVIDENTLY LLM MONITORING - ÖRNEK KULANIMLAR")
    print("=" * 60)

    examples = [
        ("1", "Temel Kullanım", example_1_basic_usage),
        ("2", "Toplu İşleme", example_2_batch_processing),
        ("3", "Kalite İzleme", example_3_quality_monitoring),
        ("4", "Rapor Oluşturma", example_4_report_generation),
        ("5", "Model Karşılaştırma", example_5_model_comparison),
        ("6", "Hata Yönetimi", example_6_error_handling),
    ]

    print("\nHangi örneği çalıştırmak istersiniz?")
    for num, name, _ in examples:
        print(f"  {num}. {name}")
    print("  0. Tümünü çalıştır")
    print("  q. Çıkış")

    choice = input("\nSeçiminiz: ").strip()

    if choice == 'q':
        print("Çıkılıyor...")
        return

    if choice == '0':
        for _, _, func in examples:
            func()
            print("\n" + "-" * 60)
    else:
        for num, _, func in examples:
            if choice == num:
                func()
                break
        else:
            print("Geçersiz seçim!")

    print("\n✅ Örnek(ler) tamamlandı!")


if __name__ == "__main__":
    main()
