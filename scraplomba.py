import sys
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    InvalidSessionIdException,
)
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)


def scrape_lomba():
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)

    try:
        driver.get("https://infolomba.id/")
    except Exception as e:
        print(f"Gagal membuka halaman: {e}")
        driver.quit()
        return []   # kembalikan list kosong, bukan sys.exit()

    time.sleep(3)

    # ── Klik tombol "Muat lebih banyak event" sampai habis ──────────────────
    klik = 0
    while klik < 5:
        try:
            tombol = driver.find_element(By.ID, "btnLoadMore")

            try:
                style = tombol.get_attribute("style") or ""
                if "display: none" in style or "display:none" in style:
                    break
                if not tombol.is_displayed() or not tombol.is_enabled():
                    break
            except StaleElementReferenceException:
                break

            driver.execute_script("arguments[0].scrollIntoView();", tombol)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tombol)
            klik += 1
            print(f"Klik ke-{klik}...")
            time.sleep(3)

        except (NoSuchElementException, StaleElementReferenceException):
            break
        except InvalidSessionIdException:
            print("Browser crash — coba jalankan ulang.")
            return []   # kembalikan list kosong, bukan sys.exit()

    print(f"Total klik: {klik}")

    # ── Helper ambil teks ────────────────────────────────────────────────────
    def ambil_teks(kartu, selector):
        try:
            return kartu.find_element(By.CSS_SELECTOR, selector).text.strip()
        except (NoSuchElementException, StaleElementReferenceException):
            return "-"

    # ── Ambil semua kartu ────────────────────────────────────────────────────
    time.sleep(2)
    semua_kartu = driver.find_elements(By.CSS_SELECTOR, "div.col")

    unik = {}
    for kartu in semua_kartu:             
        try:
            a_judul = kartu.find_element(By.CSS_SELECTOR, "h4.event-title a")
            link    = a_judul.get_attribute("href")
            judul   = a_judul.text.strip()

            if not link or link in unik:
                continue

            unik[link] = {
                "judul"        : judul,
                "countdown"    : ambil_teks(kartu, "div.countdown"),
                "target"       : ambil_teks(kartu, "div.target"),
                "biaya"        : ambil_teks(kartu, "div.biaya"),
                "lokasi"       : ambil_teks(kartu, "div.lokasi"),
                "tanggal"      : ambil_teks(kartu, "div.tanggal"),
                "penyelenggara": ambil_teks(kartu, "div.penyelenggara span:last-child"),
                "link"         : link,
            }

        except (NoSuchElementException, StaleElementReferenceException):
            # Refresh referensi elemen jika stale, lalu lanjut iterasi
            try:
                semua_kartu = driver.find_elements(By.CSS_SELECTOR, "div.col")
            except Exception:
                pass
            continue        # ← lanjutkan loop, JANGAN break

    # ── Tutup browser SETELAH loop selesai ──────────────────────────────────
    driver.quit()           

    print(f"\nTotal lomba ditemukan: {len(unik)}\n")
    for no, data in enumerate(unik.values(), 1):
        print(f"{no}. {data['judul']}")
        print(f"   Countdown     : {data['countdown']}")
        print(f"   Target        : {data['target']}")
        print(f"   Biaya         : {data['biaya']}")
        print(f"   Lokasi        : {data['lokasi']}")
        print(f"   Tanggal       : {data['tanggal']}")
        print(f"   Penyelenggara : {data['penyelenggara']}")
        print(f"   Link          : {data['link']}\n")

    return list(unik.values())


if __name__ == "__main__":
    hasil = scrape_lomba()
    print(f"Selesai. Total: {len(hasil)}")
