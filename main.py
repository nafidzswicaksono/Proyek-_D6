import sys
import argparse

import database
import scrapbeasiswa
import scraplomba


def jalankan_gui(data_list):
    """Jalankan GUI PyQt5 dengan data dari database."""
    import UI as ui
    from PyQt5.QtWidgets import QApplication

    # Setel DATA global di modul UI dengan format list-of-dict
    # yang sudah dikonversi oleh database.muat_data_dari_db()
    if data_list:
        ui.DATA = data_list

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ui.MainWindow()
    window.show()

    sys.exit(app.exec_())


def main():
    parser = argparse.ArgumentParser(
        description="Aplikasi Info Beasiswa & Lomba"
    )
    parser.add_argument(
        "--scrape",
        action="store_true",
        help="Scrape data terbaru lalu buka GUI"
    )
    parser.add_argument(
        "--scrape-only",
        action="store_true",
        help="Scrape data terbaru dan simpan ke DB tanpa membuka GUI"
    )
    args = parser.parse_args()

    # ── Inisialisasi database ──────────────────────────────────────────────
    koneksi, kursor = database.init_database()

    try:
        if args.scrape or args.scrape_only:
            print("\n=== Memulai proses scraping ===")

            print("\n[1/2] Scraping beasiswa...")
            data_beasiswa = scrapbeasiswa.scrape_beasiswa()
            print(f"  → {len(data_beasiswa)} beasiswa ditemukan")

            print("\n[2/2] Scraping lomba...")
            data_lomba = scraplomba.scrape_lomba()
            print(f"  → {len(data_lomba)} lomba ditemukan")

            database.simpan_semua_beasiswa(koneksi, data_beasiswa)
            database.simpan_semua_lomba(koneksi, data_lomba)

            koneksi.commit()
            print("\n✓ Semua data berhasil disimpan ke database.")

            if args.scrape_only:
                print("Mode --scrape-only: selesai.")
                return

        # ── Muat data dari DB dengan format yang kompatibel dengan UI ─────
        data_ui = database.muat_data_dari_db(kursor)

        if not data_ui:
            print("Database kosong. Gunakan --scrape untuk mengambil data terlebih dahulu.")
            # Tetap buka GUI dengan data contoh bawaan (DATA default di UI.py)
            data_ui = None

        print(f"\nMemuat {len(data_ui) if data_ui else 0} item ke GUI...")

    finally:
        koneksi.close()

    jalankan_gui(data_ui)


if __name__ == "__main__":
    main()
