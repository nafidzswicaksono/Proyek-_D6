import sys
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    InvalidSessionIdException,
    TimeoutException,
    WebDriverException,
)
import time

# ── Konfigurasi Chrome ──────────────────────────────────────────────────────
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


def scrape_beasiswa():

    # ── Inisialisasi driver ─────────────────────────────────────────────────
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
    except WebDriverException as e:
        print(f"[ERROR] Gagal membuka ChromeDriver: {e}")
        return []   # jangan sys.exit() agar program utama tetap bisa jalan

    # ── Daftar URL per jenjang ──────────────────────────────────────────────
    JENJANG_URLS = {
        "SMA/SMK"         : "https://beasiswa.id/category/beasiswa/sekolah-menengan-atas/",
        "Diploma (D3/D4)" : "https://beasiswa.id/category/beasiswa/beasiswa-diploma/",
        "S1"              : "https://beasiswa.id/category/beasiswa/beasiswa-sarjana/",
        "S2"              : "https://beasiswa.id/category/beasiswa/beasiswa-magister/",
    }

    JENJANG_KEYWORDS = {
        "SMA/SMK"         : ["sma", "smk", "slta", "sederajat", "high school", "aliyah"],
        "Diploma (D3/D4)" : ["diploma", "d3", "d4", "d-3", "d-4", "vokasi"],
        "S1"              : ["s1", "s-1", "sarjana", "undergraduate", "bachelor"],
        "S2"              : ["s2", "s-2", "magister", "master", "postgraduate"],
    }

    def deteksi_jenjang(teks: str) -> str:
        t = teks.lower()
        for jenjang, keywords in JENJANG_KEYWORDS.items():
            if any(k in t for k in keywords):
                return jenjang
        return "-"

    # ── Helper: ambil teks/atribut aman ────────────────────────────────────
    def ambil_teks(elemen, selector):
        try:
            return elemen.find_element(By.CSS_SELECTOR, selector).text.strip()
        except (NoSuchElementException, StaleElementReferenceException):
            return "-"

    def ambil_attr(elemen, selector, attr):
        try:
            return elemen.find_element(By.CSS_SELECTOR, selector).get_attribute(attr) or "-"
        except (NoSuchElementException, StaleElementReferenceException):
            return "-"

    CARD_SELECTORS = [
        "article",
        "div.entry-content",
        "article.type-beasiswa",
    ]
    JUDUL_SELECTORS = [
        "h2.entry-title a",
        "h1.entry-title a",
        "a[rel='bookmark']",
    ]
    MAKS_KLIK = 10

    # ── Navigasi next-page ──────────────────────────────────────────────────
    def navigasi_semua_halaman():
        klik = 0
        while klik < MAKS_KLIK:
            tombol = None
            for sel in [
                "a.next.page-numbers",
                "button#btnLoadMore",
                "a[rel='next']",
                ".load-more-btn",
                "a.load-more",
            ]:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, sel)
                    style = el.get_attribute("style") or ""
                    if "display: none" in style or "display:none" in style:
                        continue
                    if el.is_displayed() and el.is_enabled():
                        tombol = el
                        break
                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            if tombol is None:
                break

            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tombol)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", tombol)
                klik += 1
                print(f"  Klik halaman ke-{klik} …")
                time.sleep(3)
            except (StaleElementReferenceException, WebDriverException):
                break
            except InvalidSessionIdException:
                print("[ERROR] Browser crash.")
                break   # jangan sys.exit(), biarkan fungsi return dengan data yg sudah ada

        return klik

    # ── Ambil kartu dari halaman yang sudah dimuat ──────────────────────────
    def ambil_kartu_halaman(jenjang_label):
        semua_kartu = []
        for sel in CARD_SELECTORS:
            tmp = driver.find_elements(By.CSS_SELECTOR, sel)
            if tmp:
                semua_kartu = tmp
                print(f"  Selector kartu: '{sel}' → {len(tmp)} item")
                break

        hasil = {}
        for kartu in semua_kartu:
            try:
                a_judul = None
                for sel in JUDUL_SELECTORS:
                    try:
                        a_judul = kartu.find_element(By.CSS_SELECTOR, sel)
                        break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue

                if a_judul is None:
                    continue

                judul = a_judul.text.strip()
                link  = a_judul.get_attribute("href") or "-"
                if not link or link in hasil:
                    continue

                thumbnail = ambil_attr(kartu, "img", "src")
                if thumbnail == "-":
                    thumbnail = ambil_attr(kartu, ".post-thumbnail img", "src")

                deadline = (
                    ambil_teks(kartu, ".deadline")
                    or ambil_teks(kartu, ".entry-date")
                    or ambil_teks(kartu, "time")
                    or ambil_teks(kartu, ".tanggal")
                )
                penyelenggara = (
                    ambil_teks(kartu, ".penyelenggara")
                    or ambil_teks(kartu, ".organizer")
                    or ambil_teks(kartu, ".provider")
                    or ambil_teks(kartu, ".sponsor")
                )
                negara = (
                    ambil_teks(kartu, ".negara")
                    or ambil_teks(kartu, ".country")
                    or ambil_teks(kartu, ".location")
                )
                kategori = (
                    ambil_teks(kartu, ".kategori")
                    or ambil_teks(kartu, ".category")
                    or ambil_teks(kartu, ".cat-links")
                )
                biaya = (
                    ambil_teks(kartu, ".biaya")
                    or ambil_teks(kartu, ".funding")
                    or ambil_teks(kartu, ".beasiswa-type")
                )

                jenjang_final = jenjang_label if jenjang_label != "-" else deteksi_jenjang(judul)

                hasil[link] = {
                    "judul"        : judul,
                    "jenjang"      : jenjang_final,
                    "deadline"     : deadline,
                    "penyelenggara": penyelenggara,
                    "negara"       : negara,
                    "kategori"     : kategori,
                    "biaya"        : biaya,
                    "thumbnail"    : thumbnail,
                    "link"         : link,
                }

            except (NoSuchElementException, StaleElementReferenceException):
                try:
                    for sel in CARD_SELECTORS:
                        tmp = driver.find_elements(By.CSS_SELECTOR, sel)
                        if tmp:
                            semua_kartu = tmp
                            break
                except Exception:
                    pass
                continue
            except InvalidSessionIdException:
                print("[ERROR] Session browser hilang.")
                break

        return hasil

    # ── Loop utama: scrape per jenjang ──────────────────────────────────────
    unik = {}

    # Hanya simpan beasiswa yang judulnya tidak mengandung tahun yang sudah lewat
    import datetime as _dt
    TAHUN_SEKARANG = _dt.date.today().year

    def _judul_valid(judul: str) -> bool:
        import re
        tahun_dalam_judul = re.findall(r"\b(20\d{2})\b", judul)
        if not tahun_dalam_judul:
            return True
        return all(int(t) >= TAHUN_SEKARANG for t in tahun_dalam_judul)

    for jenjang_label, url in JENJANG_URLS.items():
        print(f"\n{'─'*55}")
        print(f"Scraping jenjang: {jenjang_label}")
        print(f"URL: {url}")
        print(f"{'─'*55}")

        try:
            driver.get(url)
            time.sleep(5)
        except Exception as e:
            print(f"  [ERROR] Gagal buka {url}: {e}")
            continue

        time.sleep(3)

        total_nav = navigasi_semua_halaman()
        print(f"  Total klik navigasi: {total_nav}")
        time.sleep(2)

        hasil = ambil_kartu_halaman(jenjang_label)
        # Filter: buang beasiswa yang judulnya mengandung tahun lama
        hasil_valid = {k: v for k, v in hasil.items() if _judul_valid(v["judul"])}
        dibuang = len(hasil) - len(hasil_valid)
        if dibuang:
            print(f"  Filter tahun: {dibuang} beasiswa dibuang (mengandung tahun lama)")
        baru = {k: v for k, v in hasil_valid.items() if k not in unik}
        unik.update(baru)
        print(f"  Beasiswa baru: {len(baru)} | Total: {len(unik)}")

    driver.quit()

    # ── Ringkasan ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Total beasiswa ditemukan: {len(unik)}")
    print(f"{'='*60}\n")

    for no, data in enumerate(unik.values(), 1):
        print(f"{no}. [{data['jenjang']}] {data['judul']}")
        print(f"   Deadline      : {data['deadline']}")
        print(f"   Penyelenggara : {data['penyelenggara']}")
        print(f"   Negara/Lokasi : {data['negara']}")
        print(f"   Kategori      : {data['kategori']}")
        print(f"   Biaya         : {data['biaya']}")
        print(f"   Link          : {data['link']}")
        print()

    from collections import Counter
    hitung = Counter(d["jenjang"] for d in unik.values())
    print(f"\n{'='*60}")
    print("Ringkasan per jenjang:")
    for j, n in sorted(hitung.items()):
        print(f"  {j:<20}: {n} beasiswa")
    print(f"{'='*60}")

    return list(unik.values())


if __name__ == "__main__":
    hasil = scrape_beasiswa()
    print(f"Selesai. Total: {len(hasil)}")
