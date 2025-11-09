"""
Evidently LLM Monitoring - Ana Uygulama
LLM API'sine bağlanır ve Evidently ile izler.
"""

import sys
from typing import List, Optional
from llm_client import LLMClient
from monitoring import LLMMonitor


class LLMMonitoringApp:
    """Ana uygulama sınıfı"""

    def __init__(self):
        print("\n" + "=" * 60)
        print("🚀 EVIDENTLY LLM MONİTORİNG SİSTEMİ")
        print("=" * 60 + "\n")

        # LLM client ve monitor başlat
        try:
            self.llm_client = LLMClient()
            self.monitor = LLMMonitor()
            print("\n✅ Sistem başarıyla başlatıldı!\n")
        except Exception as e:
            print(f"\n❌ Hata: {e}")
            print("Lütfen konfigürasyonu kontrol edin.\n")
            sys.exit(1)

    def process_single_prompt(self, prompt: str, **kwargs) -> dict:
        """
        Tek bir prompt işle ve monitör et

        Args:
            prompt: Kullanıcı promptu
            **kwargs: LLM parametreleri

        Returns:
            LLM response ve metrikleri
        """
        print(f"📝 İşleniyor: {prompt[:50]}...")

        # LLM'den response al
        result = self.llm_client.generate(prompt, **kwargs)

        # Monitoring sistemine kaydet
        self.monitor.add_interaction(result)

        return result

    def process_batch(self, prompts: List[str], **kwargs) -> List[dict]:
        """
        Birden fazla prompt'u işle

        Args:
            prompts: Prompt listesi
            **kwargs: LLM parametreleri

        Returns:
            Response listesi
        """
        print(f"\n📦 {len(prompts)} prompt toplu işleniyor...\n")

        results = []
        for i, prompt in enumerate(prompts, 1):
            print(f"[{i}/{len(prompts)}] İşleniyor...")
            result = self.process_single_prompt(prompt, **kwargs)
            results.append(result)

        return results

    def interactive_mode(self):
        """İnteraktif sohbet modu"""
        print("\n💬 İNTERAKTİF MOD")
        print("Çıkmak için 'exit' veya 'quit' yazın")
        print("Rapor oluşturmak için 'report' yazın")
        print("İstatistikler için 'stats' yazın")
        print("-" * 60 + "\n")

        while True:
            try:
                user_input = input("👤 Siz: ").strip()

                if not user_input:
                    continue

                # Özel komutlar
                if user_input.lower() in ['exit', 'quit', 'çıkış']:
                    print("\n👋 Görüşmek üzere!")
                    break

                elif user_input.lower() == 'report':
                    print("\n📊 Rapor oluşturuluyor...\n")
                    self.monitor.generate_report()
                    continue

                elif user_input.lower() == 'stats':
                    self.monitor.print_statistics()
                    continue

                elif user_input.lower() == 'save':
                    self.monitor.save_data()
                    continue

                # Normal prompt işle
                result = self.process_single_prompt(user_input)

                print(f"\n🤖 LLM: {result['response']}")
                print(f"⏱️  Süre: {result['response_time']:.2f}s")
                print(f"📏 Uzunluk: {len(result['response'])} karakter\n")

            except KeyboardInterrupt:
                print("\n\n👋 Kesintiye uğradı. Çıkılıyor...")
                break
            except Exception as e:
                print(f"\n❌ Hata: {e}\n")

    def run_demo(self):
        """Demo senaryosu çalıştır"""
        print("\n🎬 DEMO SENARYOSU BAŞLIYOR...\n")

        # Örnek sorular
        demo_prompts = [
            "Python'da liste ve tuple arasındaki farklar nelerdir?",
            "Machine learning için hangi Python kütüphanelerini önerirsin?",
            "REST API nedir? Kısa bir açıklama yap.",
            "Docker container'ları neden kullanılır?",
            "Git'te branch nedir ve nasıl kullanılır?",
        ]

        # Prompts işle
        results = self.process_batch(demo_prompts)

        # İstatistikler göster
        print("\n" + "=" * 60)
        self.monitor.print_statistics()

        # Kalite analizi
        quality = self.monitor.analyze_quality()
        print("📊 KALİTE ANALİZİ")
        print("=" * 60)
        print(f"Çok kısa cevaplar (<50 karakter): {quality.get('very_short_responses', 0)}")
        print(f"Çok uzun cevaplar (>1000 karakter): {quality.get('very_long_responses', 0)}")
        print(f"Yavaş cevaplar (>5s): {quality.get('slow_responses', 0)}")
        print(f"Hızlı cevaplar (<1s): {quality.get('fast_responses', 0)}")
        print(f"Hata oranı: {quality.get('error_rate', 0):.1f}%")
        print("=" * 60 + "\n")

        # Rapor oluştur
        print("📄 Evidently raporu oluşturuluyor...\n")
        self.monitor.generate_report()

        # Veriyi kaydet
        print("💾 Veri kaydediliyor...\n")
        self.monitor.save_data()

        print("\n✅ Demo tamamlandı!")

    def run_custom_scenario(self, prompts: List[str], generate_report: bool = True):
        """
        Özel senaryo çalıştır

        Args:
            prompts: İşlenecek promptlar
            generate_report: Rapor oluşturulsun mu?
        """
        results = self.process_batch(prompts)

        self.monitor.print_statistics()

        if generate_report:
            self.monitor.generate_report()
            self.monitor.save_data()

        return results


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description='Evidently LLM Monitoring')
    parser.add_argument('--mode', choices=['interactive', 'demo', 'batch'],
                        default='interactive',
                        help='Çalışma modu')
    parser.add_argument('--prompts', nargs='+',
                        help='Batch modunda işlenecek promptlar')

    args = parser.parse_args()

    # Uygulamayı başlat
    app = LLMMonitoringApp()

    # Mod seçimine göre çalıştır
    if args.mode == 'interactive':
        app.interactive_mode()
    elif args.mode == 'demo':
        app.run_demo()
    elif args.mode == 'batch':
        if not args.prompts:
            print("❌ Batch modu için --prompts parametresi gerekli!")
            sys.exit(1)
        app.run_custom_scenario(args.prompts)
    else:
        print(f"❌ Geçersiz mod: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
