"""
Logger Module
Şikayet etkileşimlerini Excel'e loglama
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path


class ComplaintLogger:
    """
    Şikayet chatbot etkileşimlerini Excel dosyasına loglayan sınıf.
    Her oturumu, soruları, cevapları ve final verilerini kaydeder.
    """

    def __init__(self, log_file_path: str = "logs.xlsx", sheet_name: str = "Logs"):
        """
        Args:
            log_file_path: Log Excel dosyasının yolu
            sheet_name: Excel içindeki sayfa adı
        """
        self.log_file_path = log_file_path
        self.sheet_name = sheet_name

        # Log dosyası yoksa oluştur
        self._initialize_log_file()

    def _initialize_log_file(self):
        """Log dosyası yoksa boş bir Excel dosyası oluştur"""
        if not os.path.exists(self.log_file_path):
            # Boş bir DataFrame ile dosya oluştur
            df = pd.DataFrame(columns=[
                "oturum_id",
                "zaman_damgasi",
                "kategori",
                "ilk_sikayet_metni",
                "soru_cevap_listesi",
                "final_veriler",
                "tamamlanma_durumu",
                "toplam_sure_saniye"
            ])

            df.to_excel(self.log_file_path, sheet_name=self.sheet_name, index=False)
            print(f"Log dosyası oluşturuldu: {self.log_file_path}")

    def log_session(
        self,
        session_id: str,
        category: str,
        initial_complaint: str,
        qa_list: List[Dict[str, str]],
        final_data: Dict[str, any],
        completed: bool = True,
        duration_seconds: Optional[float] = None
    ):
        """
        Bir şikayet oturumunu logla.

        Args:
            session_id: Benzersiz oturum ID'si
            category: Tespit edilen kategori
            initial_complaint: İlk şikayet metni
            qa_list: Soru-cevap listesi [{"soru": "...", "cevap": "..."}, ...]
            final_data: Toplanan final veriler (dict)
            completed: Oturum tamamlandı mı?
            duration_seconds: Toplam süre (saniye)
        """

        try:
            # Mevcut log dosyasını oku
            if os.path.exists(self.log_file_path):
                df = pd.read_excel(self.log_file_path, sheet_name=self.sheet_name)
            else:
                df = pd.DataFrame()

            # Yeni kayıt
            new_record = {
                "oturum_id": session_id,
                "zaman_damgasi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "kategori": category,
                "ilk_sikayet_metni": initial_complaint,
                "soru_cevap_listesi": json.dumps(qa_list, ensure_ascii=False),
                "final_veriler": json.dumps(final_data, ensure_ascii=False),
                "tamamlanma_durumu": "Tamamlandı" if completed else "Yarım Kaldı",
                "toplam_sure_saniye": duration_seconds if duration_seconds else None
            }

            # DataFrame'e ekle
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)

            # Excel'e kaydet
            df.to_excel(self.log_file_path, sheet_name=self.sheet_name, index=False)

            print(f"✓ Oturum loglandı: {session_id}")

        except Exception as e:
            print(f"✗ Loglama hatası: {str(e)}")

    def log_interaction(
        self,
        session_id: str,
        interaction_type: str,
        data: Dict[str, any]
    ):
        """
        Tek bir etkileşimi logla (detaylı loglama için opsiyonel).

        Args:
            session_id: Oturum ID'si
            interaction_type: Etkileşim tipi (örn: "kategorizasyon", "soru_soruldu", "cevap_alindi")
            data: İlgili veri
        """
        # Bu fonksiyon gelecekte detaylı loglama için kullanılabilir
        # Şimdilik sadece session bazlı loglama yapıyoruz
        pass

    def get_sessions_by_category(self, category: str) -> pd.DataFrame:
        """Belirli bir kategoriye ait tüm oturumları getir"""
        if not os.path.exists(self.log_file_path):
            return pd.DataFrame()

        df = pd.read_excel(self.log_file_path, sheet_name=self.sheet_name)
        return df[df["kategori"] == category]

    def get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """Belirli bir oturum ID'sine ait kaydı getir"""
        if not os.path.exists(self.log_file_path):
            return None

        df = pd.read_excel(self.log_file_path, sheet_name=self.sheet_name)
        session_df = df[df["oturum_id"] == session_id]

        if session_df.empty:
            return None

        record = session_df.iloc[0].to_dict()

        # JSON stringlerini parse et
        if "soru_cevap_listesi" in record and pd.notna(record["soru_cevap_listesi"]):
            record["soru_cevap_listesi"] = json.loads(record["soru_cevap_listesi"])

        if "final_veriler" in record and pd.notna(record["final_veriler"]):
            record["final_veriler"] = json.loads(record["final_veriler"])

        return record

    def get_statistics(self) -> Dict[str, any]:
        """Log dosyasından istatistikler üret"""
        if not os.path.exists(self.log_file_path):
            return {"toplam_oturum": 0}

        df = pd.read_excel(self.log_file_path, sheet_name=self.sheet_name)

        stats = {
            "toplam_oturum": len(df),
            "tamamlanan_oturum": len(df[df["tamamlanma_durumu"] == "Tamamlandı"]),
            "kategori_dagilimi": df["kategori"].value_counts().to_dict(),
            "ortalama_sure_saniye": df["toplam_sure_saniye"].mean() if "toplam_sure_saniye" in df.columns else None
        }

        return stats

    def export_to_csv(self, output_path: str):
        """Log dosyasını CSV formatına dönüştür"""
        if not os.path.exists(self.log_file_path):
            print("Log dosyası bulunamadı!")
            return

        df = pd.read_excel(self.log_file_path, sheet_name=self.sheet_name)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✓ Log dosyası CSV'ye dönüştürüldü: {output_path}")

    def clear_logs(self):
        """Tüm logları temizle (dikkatli kullanın!)"""
        response = input("Tüm loglar silinecek. Emin misiniz? (evet/hayir): ")
        if response.lower() in ["evet", "yes", "e", "y"]:
            self._initialize_log_file()
            print("✓ Loglar temizlendi.")
        else:
            print("İşlem iptal edildi.")


# Test için örnek kullanım
if __name__ == "__main__":
    # Test logger
    logger = ComplaintLogger("test_logs.xlsx")

    # Örnek oturum
    logger.log_session(
        session_id="test_001",
        category="ATM_SORUNU",
        initial_complaint="ATM'de param sıkıştı",
        qa_list=[
            {"soru": "Problem yaşadığınız ATM lokasyonu nedir?", "cevap": "Beykoz"},
            {"soru": "Ne kadar paranız sıkıştı?", "cevap": "200 TL"}
        ],
        final_data={
            "atm_lokasyonu": "Beykoz",
            "atm_problemi": "para sıkışması",
            "atm_para_islem_miktari": "200 TL"
        },
        completed=True,
        duration_seconds=45.5
    )

    # İstatistikleri yazdır
    print("\n=== İstatistikler ===")
    stats = logger.get_statistics()
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # Oturumu getir
    print("\n=== Oturum Detayı ===")
    session = logger.get_session_by_id("test_001")
    print(json.dumps(session, ensure_ascii=False, indent=2, default=str))
