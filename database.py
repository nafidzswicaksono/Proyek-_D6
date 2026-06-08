import sqlite3

# ─────────────────────────────────────────────────────────────────────────────
# CATATAN:
# Koneksi & kursor TIDAK dibuat di level modul agar tidak langsung terhubung
# saat file di-import. Semua koneksi dikelola lewat init_database() di main.py.
# ─────────────────────────────────────────────────────────────────────────────

def init_database(path="beasiswa_lomba.db"):
    """Buka (atau buat) database, buat tabel jika belum ada, kembalikan (koneksi, kursor)."""
    koneksi = sqlite3.connect(path)
    kursor  = koneksi.cursor()

    kursor.execute("""
        CREATE TABLE IF NOT EXISTS Beasiswa (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_beasiswa VARCHAR,
            penyelenggara VARCHAR,
            deadline      DATE,
            Tautan        VARCHAR UNIQUE,
            Jenjang       VARCHAR,
            kategori      VARCHAR,
            Deskripsi     TEXT
        )
    """)

    kursor.execute("""
        CREATE TABLE IF NOT EXISTS Lomba (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_lomba    VARCHAR,
            penyelenggara VARCHAR,
            kategori      VARCHAR,
            jenjang       VARCHAR,
            Deskripsi     TEXT,
            Deadline      DATE,
            Tautan        VARCHAR UNIQUE
        )
    """)

    koneksi.commit()
    print("Database berhasil dibuka/dibuat!")
    return koneksi, kursor


# ═══════════════════════════════════════════════════════════════
#  LOMBA — operasi CRUD
# ═══════════════════════════════════════════════════════════════

def simpan_lomba(koneksi, data_id, data_nama, data_penyelenggara,
                 data_kategori, data_jenjang, data_deskripsi,
                 data_deadline, data_tautan):
    kursor = koneksi.cursor()
    kursor.execute("""
        INSERT OR IGNORE INTO Lomba
            (id, nama_lomba, penyelenggara, kategori, jenjang, Deskripsi, Deadline, Tautan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data_id, data_nama, data_penyelenggara, data_kategori,
          data_jenjang, data_deskripsi, data_deadline, data_tautan))
    koneksi.commit()


def simpan_semua_lomba(koneksi, daftar_lomba):
    """Simpan list hasil scraping lomba ke database."""
    if not daftar_lomba:
        print("Tidak ada data lomba untuk disimpan.")
        return

    kursor = koneksi.cursor()
    for data in daftar_lomba:
        kursor.execute("""
            INSERT OR IGNORE INTO Lomba
                (nama_lomba, penyelenggara, kategori, jenjang, Deskripsi, Deadline, Tautan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("judul", ""),
            data.get("penyelenggara", ""),
            data.get("kategori", ""),
            data.get("target", data.get("jenjang", "")),    # scraplomba pakai "target"
            data.get("deskripsi", ""),
            data.get("tanggal", data.get("deadline", "")),  # scraplomba pakai "tanggal"
            data.get("link", ""),
        ))
    koneksi.commit()
    print(f"  {len(daftar_lomba)} lomba disimpan ke database.")


def bersihkan_kadaluarsa(koneksi):
    kursor = koneksi.cursor()
    kursor.execute("DELETE FROM Lomba WHERE Deadline < date('now')")
    koneksi.commit()


def tampilkan_lomba(kursor):
    kursor.execute("SELECT * FROM Lomba")
    daftar = kursor.fetchall()
    print("Daftar Lomba:")
    for lomba in daftar:
        print(f"  ID:{lomba[0]} | {lomba[1]} | {lomba[2]} | kat:{lomba[3]} | "
              f"jenjang:{lomba[4]} | deadline:{lomba[6]} | {lomba[7]}")


def tampilkan_lomba_deadline_14_hari(kursor):
    kursor.execute("""
        SELECT * FROM Lomba
        WHERE Deadline BETWEEN date('now') AND date('now', '+14 days')
    """)
    daftar = kursor.fetchall()
    print("Lomba deadline 14 hari ke depan:")
    if not daftar:
        print("  (tidak ada)")
    for lomba in daftar:
        print(f"  ID:{lomba[0]} | {lomba[1]} | deadline:{lomba[6]}")


def tampilkan_lomba_kategori(kursor, kata_kunci_kategori):
    kursor.execute(
        "SELECT * FROM Lomba WHERE kategori LIKE ?",
        (f"%{kata_kunci_kategori}%",)
    )
    return kursor.fetchall()


def tampilkan_lomba_jenjang(kursor, kata_kunci_jenjang):
    kursor.execute(
        "SELECT * FROM Lomba WHERE jenjang LIKE ?",
        (f"%{kata_kunci_jenjang}%",)
    )
    return kursor.fetchall()


def cari_lomba_kata_kunci(kursor, kata_kunci_searching):
    pola = f"%{kata_kunci_searching.strip()}%"
    kursor.execute(
        "SELECT * FROM Lomba WHERE nama_lomba LIKE ? OR Deskripsi LIKE ?",
        (pola, pola)
    )
    return kursor.fetchall()


def tampilkan_lomba_halamanDetail(kursor, id_terpilih):
    kursor.execute("SELECT * FROM Lomba WHERE id = ?", (id_terpilih,))
    return kursor.fetchone()


# ═══════════════════════════════════════════════════════════════
#  BEASISWA — operasi CRUD
# ═══════════════════════════════════════════════════════════════

def simpan_beasiswa(koneksi, data_id, data_nama, data_penyelenggara,
                    data_deadline, data_tautan, data_jenjang, data_deskripsi):
    kursor = koneksi.cursor()
    kursor.execute("""
        INSERT OR IGNORE INTO Beasiswa
            (id, nama_beasiswa, penyelenggara, deadline, Tautan, Jenjang, Deskripsi)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data_id, data_nama, data_penyelenggara, data_deadline,
          data_tautan, data_jenjang, data_deskripsi))
    koneksi.commit()


def simpan_semua_beasiswa(koneksi, daftar_beasiswa):
    """Simpan list hasil scraping beasiswa ke database."""
    if not daftar_beasiswa:
        print("Tidak ada data beasiswa untuk disimpan.")
        return

    kursor = koneksi.cursor()
    for data in daftar_beasiswa:
        kursor.execute("""
            INSERT OR IGNORE INTO Beasiswa
                (nama_beasiswa, penyelenggara, deadline, Tautan, Jenjang, kategori, Deskripsi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("judul", ""),
            data.get("penyelenggara", ""),
            data.get("deadline", ""),
            data.get("link", ""),
            data.get("jenjang", ""),
            data.get("kategori", ""),
            data.get("deskripsi", ""),
        ))
    koneksi.commit()
    print(f"  {len(daftar_beasiswa)} beasiswa disimpan ke database.")


def bersihkan_kadaluarsa_beasiswa(koneksi):
    kursor = koneksi.cursor()
    kursor.execute("DELETE FROM Beasiswa WHERE deadline < date('now')")
    koneksi.commit()


def tampilkan_beasiswa(kursor):
    kursor.execute("SELECT * FROM Beasiswa")
    daftar = kursor.fetchall()
    print("Daftar Beasiswa:")
    for b in daftar:
        print(f"  ID:{b[0]} | {b[1]} | {b[2]} | deadline:{b[3]} | jenjang:{b[5]} | {b[4]}")


def tampilkan_beasiswa_deadline_14_hari(kursor):
    kursor.execute("""
        SELECT * FROM Beasiswa
        WHERE deadline BETWEEN date('now') AND date('now', '+14 days')
    """)
    daftar = kursor.fetchall()
    print("Beasiswa deadline 14 hari ke depan:")
    if not daftar:
        print("  (tidak ada)")
    for b in daftar:
        print(f"  ID:{b[0]} | {b[1]} | deadline:{b[3]}")


def tampilkan_beasiswa_jenjang(kursor, kata_kunci_jenjang):
    kursor.execute(
        "SELECT * FROM Beasiswa WHERE Jenjang LIKE ?",
        (f"%{kata_kunci_jenjang}%",)
    )
    return kursor.fetchall()


def cari_beasiswa_kata_kunci(kursor, kata_kunci_searching):
    pola = f"%{kata_kunci_searching.strip()}%"
    kursor.execute(
        "SELECT * FROM Beasiswa WHERE nama_beasiswa LIKE ? OR Deskripsi LIKE ?",
        (pola, pola)
    )
    return kursor.fetchall()


def tampilkan_beasiswa_halamanDetail(kursor, id_terpilih):
    kursor.execute("SELECT * FROM Beasiswa WHERE id = ?", (id_terpilih,))
    return kursor.fetchone()


# ═══════════════════════════════════════════════════════════════
#  LOADER — konversi baris DB → format dict yang dipakai UI.py
# ═══════════════════════════════════════════════════════════════

def _hitung_hari(deadline_str: str) -> int:
    """Hitung selisih hari antara hari ini dan string deadline. Return 999 jika gagal parse."""
    from datetime import date
    import re

    if not deadline_str or deadline_str == "-":
        return 999

    bulan_id = {
        "januari":1,"februari":2,"maret":3,"april":4,"mei":5,"juni":6,
        "juli":7,"agustus":8,"september":9,"oktober":10,"november":11,"desember":12,
        "jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"agu":8,
        "sep":9,"okt":10,"nov":11,"des":12,
    }

    teks = deadline_str.lower().strip()

    # Format "dd bulan yyyy"
    m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", teks)
    if m:
        d, bln_nama, y = int(m.group(1)), m.group(2), int(m.group(3))
        bln = bulan_id.get(bln_nama)
        if bln:
            try:
                return (date(y, bln, d) - date.today()).days
            except ValueError:
                pass

    # Format ISO yyyy-mm-dd
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", teks)
    if m:
        try:
            return (date(int(m.group(1)), int(m.group(2)), int(m.group(3))) - date.today()).days
        except ValueError:
            pass

    return 999



# ═══════════════════════════════════════════════════════════════
#  AUTO-KLASIFIKASI KATEGORI & JENJANG DARI TEKS
# ═══════════════════════════════════════════════════════════════

# Kategori beasiswa → kata kunci pendeteksi (cek pada judul + deskripsi)
_KATA_KATEGORI_BEASISWA = {
    "Akademik"      : ["akademik","prestasi","ipk","universitas","kuliah","studi","pendidikan",
                       "bidikmisi","kip","afirmasi","unggulan","beasiswa penuh","full scholarship"],
    "Sains & Riset" : ["riset","penelitian","sains","science","research","lab","teknologi","inovasi",
                       "stem","matematika","fisika","kimia","biologi","informatika","komputer"],
    "Seni & Budaya" : ["seni","budaya","musik","tari","sastra","desain","arsitektur","film",
                       "fotografi","lukis","kriya","teater","broadcasting"],
    "Olahraga"      : ["olahraga","sport","atletik","sepak bola","basket","badminton","renang",
                       "bulu tangkis","voli","tinju","panahan"],
    "Sosial"        : ["sosial","masyarakat","komunitas","lingkungan","kemanusiaan","volunteer",
                       "pengabdian","keagamaan","islam","kristen","pesantren","kepemudaan"],
    "Ekonomi"       : ["ekonomi","bisnis","keuangan","akuntansi","perbankan","finance","manajemen",
                       "wirausaha","entrepreneurship","startup"],
    "Kesehatan"     : ["kesehatan","kedokteran","farmasi","keperawatan","medis","hospital",
                       "gizi","apoteker","kebidanan","kesmas"],
    "Hukum"         : ["hukum","advokasi","law","legal","notariat","kepolisian","kejaksaan"],
    "Internasional" : ["luar negeri","international","abroad","exchange","beasiswa luar",
                       "global","overseas","scholarship abroad","negeri"],
}

# Kategori lomba → kata kunci pendeteksi
_KATA_KATEGORI_LOMBA = {
    "Sains"         : ["sains","olimpiade","osn","science","matematika","fisika","kimia","biologi",
                       "astronomi","komputer","informatika","riset","penelitian","ilmiah","lkti",
                       "karya tulis ilmiah","teknologi","inovasi","stem","robotika","robot"],
    "Desain"        : ["desain","design","poster","grafis","ilustrasi","logo","branding",
                       "infografis","visual","ui","ux","fotografi","arsitektur","kriya"],
    "Seni & Budaya" : ["seni","budaya","musik","tari","vokal","puisi","cerpen","sastra","film",
                       "sinematografi","teater","pantomim","lukis","kaligrafi","paduan suara",
                       "menyanyi","mewarnai","menggambar","cipta"],
    "Teknologi"     : ["teknologi","hackathon","coding","programming","software","aplikasi",
                       "web","mobile","ai","machine learning","data","cyber","iot","drone","game"],
    "Bahasa"        : ["bahasa","debat","speech","pidato","mc","story telling","spelling",
                       "english","inggris","mandarin","arab","jepang","korea","esai","essay"],
    "Bisnis"        : ["bisnis","business","plan","startup","wirausaha","entrepreneurship",
                       "marketing","manajemen","ekonomi","finance","keuangan","investasi"],
    "Olahraga"      : ["olahraga","sport","badminton","basket","voli","futsal","renang",
                       "atletik","pencak","silat","karate","taekwondo","catur","lari"],
    "Sosial"        : ["sosial","lingkungan","kemanusiaan","volunteer","pengabdian","kesehatan",
                       "komunitas","desa","green","sustainability","climate","eco"],
}

# Jenjang → kata kunci pendeteksi (untuk beasiswa)
_KATA_JENJANG_BEASISWA = {
    "SMA/SMK"        : ["sma","smk","slta","aliyah","sederajat","high school","madrasah aliyah",
                        "sman","smkn","sekolah menengah atas","sekolah menengah kejuruan"],
    "Diploma (D3/D4)": ["diploma","d3","d4","d-3","d-4","vokasi","politeknik","d iii","d iv"],
    "S1"             : ["s1","s-1","sarjana","undergraduate","bachelor","s 1","strata 1",
                        "strata-1","s1/d4","d4/s1"],
    "S2"             : ["s2","s-2","magister","master","postgraduate","pascasarjana","s 2",
                        "strata 2","strata-2"],
    "S3"             : ["s3","s-3","doktor","phd","ph.d","doctorate","strata 3","strata-3"],
    "Umum"           : ["umum","semua jenjang","semua tingkat","terbuka","open","all level"],
}

# Jenjang → kata kunci pendeteksi (untuk lomba)
_KATA_JENJANG_LOMBA = {
    "SD"       : ["sd","mi","sekolah dasar","madrasah ibtidaiyah","sdn","elementary"],
    "SMP"      : ["smp","mts","sekolah menengah pertama","madrasah tsanawiyah","smpn","junior"],
    "SMA/SMK"  : ["sma","smk","slta","aliyah","sederajat","sman","smkn","sekolah menengah"],
    "Mahasiswa": ["mahasiswa","universitas","perguruan tinggi","college","university","s1","s2",
                  "d3","d4","diploma","sarjana","undergraduate"],
    "Umum"     : ["umum","semua","terbuka","open","all","masyarakat","profesional","publik"],
}


def _klasifikasi_teks(teks: str, mapping: dict) -> str:
    """Deteksi kategori/jenjang berdasarkan kemunculan kata kunci dalam teks."""
    t = teks.lower()
    skor = {label: 0 for label in mapping}
    for label, keywords in mapping.items():
        for kw in keywords:
            if kw in t:
                skor[label] += 1
    best = max(skor, key=skor.get)
    return best if skor[best] > 0 else None


def _tebak_kategori_beasiswa(judul: str, deskripsi: str, kategori_db: str) -> str:
    """Tentukan kategori beasiswa: pakai DB jika ada, tebak jika kosong."""
    if kategori_db and kategori_db not in ("-", ""):
        return kategori_db
    teks = f"{judul} {deskripsi}"
    return _klasifikasi_teks(teks, _KATA_KATEGORI_BEASISWA) or "Akademik"


def _tebak_kategori_lomba(judul: str, deskripsi: str, kategori_db: str) -> str:
    """Tentukan kategori lomba: pakai DB jika ada, tebak jika kosong."""
    if kategori_db and kategori_db not in ("-", ""):
        return kategori_db
    teks = f"{judul} {deskripsi}"
    return _klasifikasi_teks(teks, _KATA_KATEGORI_LOMBA) or "Sains"


def _tebak_jenjang_beasiswa(judul: str, deskripsi: str, jenjang_db: str) -> str:
    """Tentukan jenjang beasiswa: pakai DB jika ada, tebak jika kosong."""
    if jenjang_db and jenjang_db not in ("-", "", "Umum"):
        return jenjang_db
    teks = f"{judul} {deskripsi}"
    return _klasifikasi_teks(teks, _KATA_JENJANG_BEASISWA) or "Umum"


def _tebak_jenjang_lomba(judul: str, deskripsi: str, jenjang_db: str) -> str:
    """Tentukan jenjang lomba: pakai DB jika ada, tebak jika kosong."""
    if jenjang_db and jenjang_db not in ("-", "", "Umum"):
        return jenjang_db
    teks = f"{judul} {deskripsi}"
    return _klasifikasi_teks(teks, _KATA_JENJANG_LOMBA) or "Umum"


def _buat_deskripsi_beasiswa(nama: str, penyelenggara: str, jenjang: str,
                              kategori: str, deadline: str, deskripsi_db: str) -> str:
    """Buat deskripsi yang informatif jika DB tidak menyediakan."""
    if deskripsi_db and len(deskripsi_db.strip()) > 20:
        return deskripsi_db.strip()
    bagian = []
    if penyelenggara and penyelenggara != "-":
        bagian.append(f"{nama} adalah program beasiswa dari {penyelenggara}")
    else:
        bagian.append(f"Program beasiswa {nama}")
    if jenjang and jenjang not in ("-", "Umum"):
        bagian[0] += f" untuk jenjang {jenjang}"
    if kategori and kategori not in ("-",):
        bagian.append(f"Kategori: {kategori}.")
    if deadline and deadline not in ("-",):
        bagian.append(f"Batas pendaftaran: {deadline}.")
    bagian.append("Kunjungi website resmi untuk informasi persyaratan dan cara pendaftaran selengkapnya.")
    return " ".join(bagian)


def _buat_deskripsi_lomba(nama: str, penyelenggara: str, jenjang: str,
                           kategori: str, deadline: str, deskripsi_db: str) -> str:
    """Buat deskripsi yang informatif jika DB tidak menyediakan."""
    if deskripsi_db and len(deskripsi_db.strip()) > 20:
        return deskripsi_db.strip()
    bagian = []
    if penyelenggara and penyelenggara != "-":
        bagian.append(f"{nama} adalah kompetisi yang diselenggarakan oleh {penyelenggara}")
    else:
        bagian.append(f"Kompetisi {nama}")
    if jenjang and jenjang not in ("-", "Umum"):
        bagian[0] += f" untuk peserta {jenjang}"
    if kategori and kategori not in ("-",):
        bagian.append(f"Bidang lomba: {kategori}.")
    if deadline and deadline not in ("-",):
        bagian.append(f"Batas pendaftaran: {deadline}.")
    bagian.append("Kunjungi website resmi untuk informasi hadiah dan cara pendaftaran selengkapnya.")
    return " ".join(bagian)


def muat_data_dari_db(kursor):
    """
    Ambil semua data dari DB (hanya yang belum kadaluarsa) dan konversi ke
    format list-of-dict yang kompatibel dengan DATA di UI.py.

    Setiap item memiliki keys:
        id, type, title, organizer, desc, deadline, days, urgent,
        cat, level, active, reqs, prizes, url
    """
    hasil = []

    # ── Beasiswa: hanya ambil yang deadline-nya belum lewat ───────────────
    kursor.execute("""
        SELECT id, nama_beasiswa, penyelenggara, deadline,
               Tautan, Jenjang, kategori, Deskripsi
        FROM Beasiswa
        WHERE deadline IS NULL
           OR TRIM(deadline) = ''
           OR TRIM(deadline) = '-'
           OR deadline >= date('now')
        ORDER BY deadline ASC
    """)
    for row in kursor.fetchall():
        db_id, nama, penyelenggara, deadline, tautan, jenjang, kategori, deskripsi = row
        nama         = (nama or "").strip()
        penyelenggara= (penyelenggara or "").strip()
        deskripsi    = (deskripsi or "").strip()
        jenjang      = (jenjang or "").strip()
        kategori     = (kategori or "").strip()

        kat_final  = _tebak_kategori_beasiswa(nama, deskripsi, kategori)
        jen_final  = _tebak_jenjang_beasiswa(nama, deskripsi, jenjang)
        desc_final = _buat_deskripsi_beasiswa(nama, penyelenggara, jen_final,
                                               kat_final, deadline or "", deskripsi)
        hari = _hitung_hari(deadline or "")

        # Buat poin persyaratan umum berdasarkan jenjang
        reqs_umum = _reqs_default_beasiswa(jen_final)
        # Buat poin keuntungan umum
        prizes_umum = _prizes_default_beasiswa(kat_final)

        hasil.append({
            "id"        : db_id,
            "type"      : "Beasiswa",
            "title"     : nama          or "-",
            "organizer" : penyelenggara or "-",
            "desc"      : desc_final,
            "deadline"  : deadline      or "-",
            "days"      : hari,
            "urgent"    : 0 <= hari <= 7,
            "cat"       : kat_final,
            "level"     : jen_final,
            "active"    : True,
            "reqs"      : reqs_umum,
            "prizes"    : prizes_umum,
            "url"       : (tautan or "").strip() or "#",
        })

    # ── Lomba: hanya ambil yang deadline-nya belum lewat ──────────────────
    kursor.execute("""
        SELECT id, nama_lomba, penyelenggara, kategori,
               jenjang, Deskripsi, Deadline, Tautan
        FROM Lomba
        WHERE Deadline IS NULL
           OR TRIM(Deadline) = ''
           OR TRIM(Deadline) = '-'
           OR Deadline >= date('now')
        ORDER BY Deadline ASC
    """)
    for row in kursor.fetchall():
        db_id, nama, penyelenggara, kategori, jenjang, deskripsi, deadline, tautan = row
        nama         = (nama or "").strip()
        penyelenggara= (penyelenggara or "").strip()
        deskripsi    = (deskripsi or "").strip()
        jenjang      = (jenjang or "").strip()
        kategori     = (kategori or "").strip()

        kat_final  = _tebak_kategori_lomba(nama, deskripsi, kategori)
        jen_final  = _tebak_jenjang_lomba(nama, deskripsi, jenjang)
        desc_final = _buat_deskripsi_lomba(nama, penyelenggara, jen_final,
                                            kat_final, deadline or "", deskripsi)
        hari = _hitung_hari(deadline or "")

        reqs_umum   = _reqs_default_lomba(jen_final)
        prizes_umum = _prizes_default_lomba(kat_final)

        hasil.append({
            "id"        : db_id,
            "type"      : "Lomba",
            "title"     : nama          or "-",
            "organizer" : penyelenggara or "-",
            "desc"      : desc_final,
            "deadline"  : deadline      or "-",
            "days"      : hari,
            "urgent"    : 0 <= hari <= 7,
            "cat"       : kat_final,
            "level"     : jen_final,
            "active"    : True,
            "reqs"      : reqs_umum,
            "prizes"    : prizes_umum,
            "url"       : (tautan or "").strip() or "#",
        })

    return hasil


def _reqs_default_beasiswa(jenjang: str) -> list:
    """Persyaratan umum beasiswa berdasarkan jenjang."""
    base = ["Warga Negara Indonesia (WNI)", "Tidak sedang menerima beasiswa lain",
            "Mengisi formulir pendaftaran online", "Melampirkan dokumen persyaratan"]
    extras = {
        "SMA/SMK"        : ["Siswa SMA/SMK/sederajat aktif", "Nilai rapor rata-rata minimal 7.5"],
        "Diploma (D3/D4)": ["Mahasiswa D3/D4 aktif", "IPK minimal 3.00"],
        "S1"             : ["Mahasiswa S1 aktif", "IPK minimal 3.00", "Surat rekomendasi dosen"],
        "S2"             : ["Mahasiswa/calon mahasiswa S2", "IPK S1 minimal 3.25",
                            "Sertifikat bahasa (TOEFL/IELTS)", "Proposal rencana studi"],
        "S3"             : ["Mahasiswa/calon mahasiswa S3", "IPK S2 minimal 3.50",
                            "Sertifikat bahasa internasional", "Proposal riset"],
        "Umum"           : ["Peserta umum dari seluruh Indonesia"],
    }
    return extras.get(jenjang, ["Baca syarat lengkap di website resmi"]) + base


def _prizes_default_beasiswa(kategori: str) -> list:
    """Keuntungan umum beasiswa berdasarkan kategori."""
    umum = ["Biaya pendidikan (sebagian atau penuh)", "Sertifikat penerima beasiswa",
            "Jaringan alumni penerima beasiswa"]
    extras = {
        "Akademik"      : ["Tunjangan hidup bulanan", "Biaya buku & alat tulis"],
        "Internasional" : ["Tiket perjalanan PP", "Tunjangan hidup di luar negeri",
                           "Biaya visa & akomodasi"],
        "Ekonomi"       : ["Uang saku bulanan", "Pelatihan kewirausahaan", "Magang di lembaga mitra"],
        "Kesehatan"     : ["Biaya praktikum & klinik", "Tunjangan penelitian"],
        "Sains & Riset" : ["Dana riset", "Akses jurnal ilmiah", "Bimbingan peneliti senior"],
    }
    return umum + extras.get(kategori, ["Lihat keuntungan lengkap di website resmi"])


def _reqs_default_lomba(jenjang: str) -> list:
    """Persyaratan umum lomba berdasarkan jenjang."""
    base = ["Karya/pendaftaran bersifat original", "Mengisi formulir pendaftaran",
            "Mengikuti aturan dan ketentuan lomba"]
    extras = {
        "SD"       : ["Siswa SD/MI aktif", "Pendaftaran melalui sekolah atau mandiri"],
        "SMP"      : ["Siswa SMP/MTs aktif", "Surat izin dari orang tua/sekolah"],
        "SMA/SMK"  : ["Siswa SMA/SMK/sederajat aktif", "Surat izin dari kepala sekolah"],
        "Mahasiswa": ["Mahasiswa aktif (D3/D4/S1/S2)", "Kartu Tanda Mahasiswa (KTM) berlaku"],
        "Umum"     : ["Terbuka untuk umum (sesuai ketentuan usia)", "KTP/identitas diri"],
    }
    return extras.get(jenjang, ["Baca syarat lengkap di website resmi"]) + base


def _prizes_default_lomba(kategori: str) -> list:
    """Hadiah umum lomba berdasarkan kategori."""
    umum = ["Sertifikat penghargaan", "Piala/trofi juara"]
    extras = {
        "Sains"         : ["Uang pembinaan juara 1, 2, 3", "Beasiswa pendidikan",
                           "Publikasi karya ilmiah"],
        "Teknologi"     : ["Uang tunai & merchandise", "Mentoring dari praktisi industri",
                           "Kesempatan magang/inkubasi startup"],
        "Desain"        : ["Uang tunai", "Karya dipamerkan secara nasional",
                           "Lisensi software desain profesional"],
        "Bahasa"        : ["Uang tunai", "Kursus bahasa lanjutan", "Kamus & materi belajar"],
        "Seni & Budaya" : ["Uang tunai", "Penampilan di acara nasional",
                           "Rekaman/publikasi karya"],
        "Bisnis"        : ["Modal usaha / seed funding", "Mentoring wirausahawan senior",
                           "Jaringan investor & mitra bisnis"],
        "Olahraga"      : ["Medali & piala", "Pembinaan atlet", "Tiket pertandingan nasional"],
        "Sosial"        : ["Uang tunai", "Implementasi program di masyarakat",
                           "Kolaborasi dengan lembaga mitra"],
    }
    return umum + extras.get(kategori, ["Lihat hadiah lengkap di website resmi"])


# ═══════════════════════════════════════════════════════════════
#  FUNGSI AGREGASI UNTUK VISUALISASI DATA (GRAFIK)
# ═══════════════════════════════════════════════════════════════

def dapatkan_perbandingan_total(kursor):
    """Menghitung total data beasiswa vs total data lomba"""
    kursor.execute("SELECT COUNT(*) FROM Beasiswa")
    total_beasiswa = kursor.fetchone()[0] or 0
    
    kursor.execute("SELECT COUNT(*) FROM Lomba")
    total_lomba = kursor.fetchone()[0] or 0
    
    return {
        "Beasiswa": total_beasiswa,
        "Lomba": total_lomba
    }

def dapatkan_distribusi_kategori(kursor):
    """Menghitung jumlah data berdasarkan kategori"""
    # Agregasi untuk Beasiswa
    kursor.execute("SELECT kategori, COUNT(*) FROM Beasiswa GROUP BY kategori")
    beasiswa_kat = {row[0] if row[0] else "Lainnya": row[1] for row in kursor.fetchall()}
    
    # Agregasi untuk Lomba
    kursor.execute("SELECT kategori, COUNT(*) FROM Lomba GROUP BY kategori")
    lomba_kat = {row[0] if row[0] else "Lainnya": row[1] for row in kursor.fetchall()}
    
    return {
        "beasiswa": beasiswa_kat,
        "lomba": lomba_kat
    }

def dapatkan_distribusi_jenjang(kursor):
    """Menghitung jumlah data berdasarkan jenjang pendidikan"""
    # Agregasi untuk Beasiswa
    kursor.execute("SELECT Jenjang, COUNT(*) FROM Beasiswa GROUP BY Jenjang")
    beasiswa_jen = {row[0] if row[0] else "Umum": row[1] for row in kursor.fetchall()}
    
    # Agregasi untuk Lomba
    kursor.execute("SELECT jenjang, COUNT(*) FROM Lomba GROUP BY jenjang")
    lomba_jen = {row[0] if row[0] else "Umum": row[1] for row in kursor.fetchall()}
    
    return {
        "beasiswa": beasiswa_jen,
        "lomba": lomba_jen
    }