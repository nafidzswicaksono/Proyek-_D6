import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QLineEdit, QComboBox,
    QCheckBox, QGridLayout, QDialog, QGraphicsDropShadowEffect,
    QSizePolicy, QSpacerItem, QAbstractItemView, QTabWidget
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QSize, QRect, QPoint, QPropertyAnimation,
    QEasingCurve, QTimer, QUrl, QThread
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen,
    QLinearGradient, QPixmap, QCursor, QFontMetrics, QIcon, QDesktopServices
)

# ── Matplotlib (opsional – dashboard charts) ──────────────────
try:
    import matplotlib
    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ══════════════════════════════════════════════════════════════
#  THEME SYSTEM
# ══════════════════════════════════════════════════════════════
LIGHT = {
    "mode": "light",
    # Backgrounds
    "bg_base":      "#F5F7FF",
    "bg_surface":   "#FFFFFF",
    "bg_card":      "#FFFFFF",
    "bg_card_hov":  "#F8F9FF",
    "bg_input":     "#F1F3FF",
    "bg_header":    "#FFFFFF",
    "bg_sidebar":   "#FAFBFF",
    # Text
    "tx_primary":   "#0F172A",
    "tx_secondary": "#475569",
    "tx_muted":     "#94A3B8",
    "tx_on_accent": "#FFFFFF",
    # Borders
    "bd_base":      "#E2E8F0",
    "bd_strong":    "#CBD5E1",
    "bd_focus":     "#6366F1",
    # Accents
    "ac_blue":      "#6366F1",       # indigo
    "ac_blue_lt":   "#EEF2FF",
    "ac_cyan":      "#0EA5E9",
    "ac_cyan_lt":   "#E0F2FE",
    "ac_violet":    "#8B5CF6",
    "ac_violet_lt": "#F3EEFF",
    "ac_green":     "#10B981",
    "ac_green_lt":  "#ECFDF5",
    "ac_amber":     "#F59E0B",
    "ac_amber_lt":  "#FFFBEB",
    "ac_rose":      "#F43F5E",
    "ac_rose_lt":   "#FFF1F2",
    # Stat card bgs
    "stat1_bg":     "#EEF2FF", "stat1_bd": "#C7D2FE",
    "stat2_bg":     "#F3EEFF", "stat2_bd": "#DDD6FE",
    "stat3_bg":     "#E0F2FE", "stat3_bd": "#BAE6FD",
    "stat4_bg":     "#ECFDF5", "stat4_bd": "#A7F3D0",
    # Gradients (as tuple stop colors for QPainter)
    "grad_a": "#6366F1", "grad_b": "#0EA5E9",
    # Filter btn active
    "filt_act_bg":  "#6366F1", "filt_act_tx": "#FFFFFF",
    "filt_idle_bg": "#FFFFFF", "filt_idle_tx": "#475569",
    "filt_idle_bd": "#CBD5E1",
    # Shadow
    "shadow": QColor(99, 102, 241, 22),
    "card_shadow": QColor(15, 23, 42, 14),
    # Toggle btn
    "toggle_bg":    "#EEF2FF", "toggle_tx": "#6366F1", "toggle_bd": "#C7D2FE",
    "toggle_icon":  "🌙",
    # Header accent strip
    "header_strip": True,
}

DARK = {
    "mode": "dark",
    "bg_base":      "#1C1F2E",
    "bg_surface":   "#252837",
    "bg_card":      "#252837",
    "bg_card_hov":  "#2C3048",
    "bg_input":     "#1E2130",
    "bg_header":    "#1E2130",
    "bg_sidebar":   "#1E2130",
    "tx_primary":   "#F1F5F9",
    "tx_secondary": "#94A3B8",
    "tx_muted":     "#64748B",
    "tx_on_accent": "#FFFFFF",
    "bd_base":      "#2D3350",
    "bd_strong":    "#3D4468",
    "bd_focus":     "#818CF8",
    "ac_blue":      "#818CF8",
    "ac_blue_lt":   "#2D3158",
    "ac_cyan":      "#38BDF8",
    "ac_cyan_lt":   "#1E3048",
    "ac_violet":    "#A78BFA",
    "ac_violet_lt": "#2D2548",
    "ac_green":     "#34D399",
    "ac_green_lt":  "#1A3028",
    "ac_amber":     "#FBBF24",
    "ac_amber_lt":  "#2E2510",
    "ac_rose":      "#FB7185",
    "ac_rose_lt":   "#321828",
    "stat1_bg": "#2D3158", "stat1_bd": "#4049A0",
    "stat2_bg": "#2D2548", "stat2_bd": "#6040A0",
    "stat3_bg": "#1E3048", "stat3_bd": "#2060A0",
    "stat4_bg": "#1A3028", "stat4_bd": "#208060",
    "grad_a": "#818CF8", "grad_b": "#38BDF8",
    "filt_act_bg":  "#818CF8", "filt_act_tx": "#0F172A",
    "filt_idle_bg": "#252837", "filt_idle_tx": "#94A3B8",
    "filt_idle_bd": "#3D4468",
    "shadow": QColor(0, 0, 0, 60),
    "card_shadow": QColor(0, 0, 0, 50),
    "toggle_bg":    "#2D3158", "toggle_tx": "#818CF8", "toggle_bd": "#4049A0",
    "toggle_icon":  "☀️",
    "header_strip": False,
}

T = LIGHT   # current theme (mutable reference via dict)


def gfx_shadow(widget, blur=20, color: QColor = None, dx=0, dy=4):
    if color is None:
        color = T["card_shadow"]
    e = QGraphicsDropShadowEffect()
    e.setBlurRadius(blur)
    e.setColor(color)
    e.setOffset(dx, dy)
    widget.setGraphicsEffect(e)


# ══════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════
DATA = [
    {"id":1,"type":"Lomba","title":"Olimpiade Sains Nasional","organizer":"Kemendikbud",
     "desc":"Kompetisi sains tingkat nasional untuk siswa SMA di bidang IPA, Matematika, Komputer, dan Astronomi.",
     "deadline":"10 April 2026","days":4,"urgent":True,"cat":"Sains","level":"SMA","active":True,
     "reqs":["Siswa SMA aktif","Nilai rata-rata min 8.0","Surat izin sekolah","Surat izin orang tua"],
     "prizes":["Medali emas/perak/perunggu","Piagam penghargaan","Pembinaan intensif","Olimpiade internasional","Beasiswa PT"],
     "url":"https://osn.kemendikbud.go.id"},
    {"id":2,"type":"Lomba","title":"Lomba Desain Poster Digital","organizer":"Adobe Indonesia",
     "desc":'Kompetisi desain poster digital bertema "Masa Depan Berkelanjutan" untuk pelajar dan mahasiswa.',
     "deadline":"20 April 2026","days":9,"urgent":False,"cat":"Desain","level":"SMA/Mahasiswa","active":True,
     "reqs":["Pelajar/Mahasiswa aktif","Karya original","Format A3 300dpi","File AI/PSD/PDF"],
     "prizes":["Uang tunai Rp 10 juta","Lisensi Adobe CC 1 tahun","Sertifikat","Pameran karya nasional"],
     "url":"https://adobe.com/id"},
    {"id":3,"type":"Lomba","title":"Lomba Karya Tulis Ilmiah Nasional","organizer":"LIPI",
     "desc":"Kompetisi penulisan karya tulis ilmiah tingkat nasional bertema teknologi untuk kehidupan.",
     "deadline":"25 April 2026","days":14,"urgent":False,"cat":"Riset","level":"Mahasiswa","active":True,
     "reqs":["Mahasiswa D3/S1 aktif","Tim 2-3 orang","Abstrak maks 300 kata","Full paper maks 20 hal"],
     "prizes":["Juara 1: Rp 15 juta","Juara 2: Rp 10 juta","Juara 3: Rp 7.5 juta","Publikasi jurnal"],
     "url":"https://lipi.go.id"},
    {"id":4,"type":"Beasiswa","title":"Beasiswa Unggulan Kemendikbud","organizer":"Kemendikbud",
     "desc":"Beasiswa penuh untuk mahasiswa berprestasi tingkat S1, S2, dan S3 di perguruan tinggi terkemuka.",
     "deadline":"30 April 2026","days":19,"urgent":False,"cat":"Akademik","level":"Mahasiswa","active":True,
     "reqs":["WNI","IPK min 3.25/3.50","Usia maks 40 tahun","Tidak menerima beasiswa lain"],
     "prizes":["Biaya pendidikan penuh","Tunjangan hidup","Tunjangan buku","Tunjangan riset","Asuransi"],
     "url":"https://beasiswaunggulan.kemdikbud.go.id"},
    {"id":5,"type":"Beasiswa","title":"Beasiswa LPDP 2026","organizer":"Kemenkeu",
     "desc":"Program beasiswa pemerintah Indonesia untuk studi lanjut S2/S3 dalam dan luar negeri.",
     "deadline":"15 Mei 2026","days":34,"urgent":False,"cat":"Akademik","level":"Pascasarjana","active":True,
     "reqs":["WNI","IPK min 3.0","TOEFL/IELTS","Esai motivasi","Rencana studi"],
     "prizes":["Biaya pendidikan penuh","Tunjangan hidup","Tiket PP","Tunjangan keluarga","Dana riset"],
     "url":"https://lpdp.kemenkeu.go.id"},
    {"id":6,"type":"Lomba","title":"Hackathon Inovasi Digital 2026","organizer":"Kominfo",
     "desc":"Kompetisi inovasi teknologi digital untuk memecahkan masalah sosial dengan solusi tech.",
     "deadline":"5 Mei 2026","days":24,"urgent":False,"cat":"Teknologi","level":"Mahasiswa/Umum","active":True,
     "reqs":["Tim 3-5 orang","Min 1 mahasiswa aktif","Prototype fungsional","Presentasi 10 menit"],
     "prizes":["Grand Prize: Rp 50 juta","Runner-up: Rp 25 juta","3rd: Rp 15 juta","Mentoring startup"],
     "url":"https://kominfo.go.id"},
    {"id":7,"type":"Beasiswa","title":"Beasiswa Bank Indonesia","organizer":"Bank Indonesia",
     "desc":"Beasiswa untuk mahasiswa S1 berprestasi di bidang ekonomi, keuangan, dan perbankan.",
     "deadline":"20 Mei 2026","days":39,"urgent":False,"cat":"Ekonomi","level":"S1","active":True,
     "reqs":["Mahasiswa S1 sem 4-7","IPK min 3.0","Jur. Ekonomi/Keuangan","Aktif organisasi"],
     "prizes":["Rp 1.5 juta/bulan","Biaya pendidikan","Laptop","Magang BI"],
     "url":"https://www.bi.go.id"},
    {"id":8,"type":"Lomba","title":"Kompetisi Debat Bahasa Inggris","organizer":"British Council",
     "desc":"Kompetisi debat bahasa Inggris antar universitas tingkat nasional format British Parliamentary.",
     "deadline":"28 April 2026","days":17,"urgent":False,"cat":"Bahasa","level":"Mahasiswa","active":True,
     "reqs":["Mahasiswa aktif","Tim 2 orang","B.Inggris aktif","Registrasi online"],
     "prizes":["Trophy nasional","Rp 8 juta","Sertifikat","Kursus B.Inggris 1 tahun"],
     "url":"https://britishcouncil.org/id"},
    {"id":9,"type":"Beasiswa","title":"Beasiswa Pertamina Foundation","organizer":"Pertamina",
     "desc":"Program beasiswa untuk mahasiswa berprestasi dari keluarga kurang mampu di seluruh Indonesia.",
     "deadline":"10 Juni 2026","days":60,"urgent":False,"cat":"Akademik","level":"S1","active":True,
     "reqs":["Mahasiswa S1 aktif","IPK min 3.0","Penghasilan OT < Rp 4jt","Surat keterangan"],
     "prizes":["Biaya pendidikan penuh","Rp 1.2 juta/bulan","Laptop","Pelatihan soft skills"],
     "url":"https://pertaminafoundation.org"},
    {"id":10,"type":"Lomba","title":"National Programming Contest","organizer":"ICPC Indonesia",
     "desc":"Kompetisi pemrograman tingkat nasional sebagai seleksi untuk ICPC Asia Regional.",
     "deadline":"12 Mei 2026","days":31,"urgent":False,"cat":"Teknologi","level":"Mahasiswa","active":True,
     "reqs":["Mahasiswa aktif","Tim 3 orang","1 pembimbing dosen","Registrasi online"],
     "prizes":["Trophy + Rp 12 juta","Trophy + Rp 8 juta","Tiket ICPC Asia","Sertifikat"],
     "url":"https://icpc.baylor.edu"},
    {"id":11,"type":"Beasiswa","title":"Beasiswa Djarum Plus","organizer":"Djarum Foundation",
     "desc":"Program beasiswa plus pembinaan karakter untuk mahasiswa S1 semester 4-5 berprestasi.",
     "deadline":"1 Juni 2026","days":51,"urgent":False,"cat":"Akademik","level":"S1","active":True,
     "reqs":["Mahasiswa S1 sem 4-5","IPK min 3.2","Aktif organisasi","Bukan penerima beasiswa lain"],
     "prizes":["Rp 750 ribu/bulan","Pelatihan soft skills","Beasiswa ke LN","Jaringan beswan"],
     "url":"https://djarumbeasiswaplus.org"},
    {"id":12,"type":"Lomba","title":"Film Pendek Kreatif Nusantara","organizer":"Kemenparekraf",
     "desc":"Festival film pendek nasional untuk sineas muda Indonesia bertema budaya dan pariwisata.",
     "deadline":"30 Mei 2026","days":49,"urgent":False,"cat":"Seni","level":"SMA/Mahasiswa/Umum","active":False,
     "reqs":["WNI 17-35 tahun","Film maks 15 menit","Tema budaya/pariwisata","MP4 1080p"],
     "prizes":["Grand Prize: Rp 30 juta","2nd: Rp 20 juta","3rd: Rp 10 juta","Tayang streaming"],
     "url":"https://kemenparekraf.go.id"},
]

CATEGORIES_BEASISWA = ["Semua Kategori"]
CATEGORIES_LOMBA    = ["Semua Kategori"]

LEVELS_BEASISWA = ["Semua Jenjang","SMA/SMK","Diploma (D3/D4)","S1","S2","S3","Umum"]
LEVELS_LOMBA    = ["Semua Jenjang","SD","SMP","SMA/SMK","Mahasiswa","Umum"]

# Normalisasi jenjang mentah dari scraper → nilai standar
LEVEL_NORM_BEASISWA = {
    "sma":"SMA/SMK","smk":"SMA/SMK","sma/smk":"SMA/SMK","slta":"SMA/SMK","aliyah":"SMA/SMK",
    "diploma":"Diploma (D3/D4)","d3":"Diploma (D3/D4)","d4":"Diploma (D3/D4)",
    "diploma (d3/d4)":"Diploma (D3/D4)","diploma (d3)":"Diploma (D3/D4)","vokasi":"Diploma (D3/D4)",
    "s1":"S1","sarjana":"S1","undergraduate":"S1","bachelor":"S1",
    "s2":"S2","magister":"S2","master":"S2","pascasarjana":"S2",
    "s3":"S3","doktor":"S3","phd":"S3",
    "mahasiswa":"S1",
    "umum":"Umum","-":"Umum","":"Umum",
}
LEVEL_NORM_LOMBA = {
    "sd":"SD","mi":"SD",
    "smp":"SMP","mts":"SMP",
    "sma":"SMA/SMK","smk":"SMA/SMK","sma/smk":"SMA/SMK","slta":"SMA/SMK",
    "mahasiswa":"Mahasiswa","s1":"Mahasiswa","s2":"Mahasiswa",
    "diploma":"Mahasiswa","d3":"Mahasiswa","d4":"Mahasiswa",
    "umum":"Umum","-":"Umum","":"Umum",
}

def _normalize_level(raw: str, is_lomba: bool) -> str:
    mapping = LEVEL_NORM_LOMBA if is_lomba else LEVEL_NORM_BEASISWA
    return mapping.get(raw.strip().lower(), raw.strip() or "Umum")

def _build_dynamic_options(data):
    global CATEGORIES_BEASISWA, CATEGORIES_LOMBA
    cats_b, cats_l = set(), set()
    for item in data:
        is_lomba = item["type"] == "Lomba"
        raw_levels = [s.strip() for s in str(item.get("level","")).split("/")]
        normed = []
        for r in raw_levels:
            n = _normalize_level(r, is_lomba)
            if n and n not in normed:
                normed.append(n)
        item["level_norm"] = normed
        item["level"] = "/".join(normed) if normed else "Umum"
        cat = item.get("cat","").strip()
        if cat and cat not in ("-",""):
            (cats_l if is_lomba else cats_b).add(cat)
    CATEGORIES_BEASISWA = ["Semua Kategori"] + sorted(cats_b)
    CATEGORIES_LOMBA    = ["Semua Kategori"] + sorted(cats_l)

LOMBA_ICONS  = {"Sains":"🔬","Desain":"🎨","Riset":"📝","Teknologi":"💻","Bahasa":"🗣️","Seni":"🎬","default":"🏆"}
BEA_ICONS    = {"Akademik":"🎓","Ekonomi":"💰","default":"🎓"}


def item_icon(item):
    if item["type"] == "Lomba":
        return LOMBA_ICONS.get(item["cat"], LOMBA_ICONS["default"])
    return BEA_ICONS.get(item["cat"], BEA_ICONS["default"])


# ══════════════════════════════════════════════════════════════
#  REUSABLE WIDGETS
# ══════════════════════════════════════════════════════════════
class Chip(QLabel):
    """Small pill badge"""
    def __init__(self, text, tx_color=None, bg_color=None, parent=None):
        super().__init__(text, parent)
        tx = tx_color or T["tx_on_accent"]
        bg = bg_color or T["ac_blue"]
        self._tx = tx; self._bg = bg
        self._refresh()
        self.setFixedHeight(22)

    def _refresh(self):
        self.setStyleSheet(f"""
            QLabel {{
                background: {self._bg};
                color: {self._tx};
                border-radius: 9px;
                padding: 0px 10px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.2px;
            }}
        """)

    def recolor(self, tx, bg):
        self._tx = tx; self._bg = bg
        self._refresh()


class IconButton(QPushButton):
    def __init__(self, text, tooltip="", parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if tooltip:
            self.setToolTip(tooltip)

    def apply_style(self, bg, tx, bd, hover_bg, hover_tx, hover_bd,
                    radius=10, font_size=13, font_weight=600,
                    padding="0 16px", height=38):
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {tx};
                border-radius: {radius}px;
                font-size: {font_size}px;
                font-weight: {font_weight};
                border: none;
                padding: {padding};
            }}
            QPushButton:hover {{
                background: {hover_bg};
                color: {hover_tx};
                border-color: transparent;
            }}
            QPushButton:pressed {{
                background: {hover_bg};
            }}
        """)


# ══════════════════════════════════════════════════════════════
#  TOGGLE SWITCH (theme toggle)
# ══════════════════════════════════════════════════════════════
class ThemeToggle(QWidget):
    toggled = pyqtSignal(bool)   # True = dark

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = False
        self.setFixedSize(130, 38)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._btn = QPushButton()
        self._btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._btn.setFixedHeight(38)
        self._btn.clicked.connect(self._on_click)
        lay.addWidget(self._btn)
        self._refresh()

    def _refresh(self):
        icon = "🌙  Mode Gelap" if not self._dark else "☀️  Mode Terang"
        self._btn.setText(icon)
        bg   = T["toggle_bg"]
        tx   = T["toggle_tx"]
        bd   = T["toggle_bd"]
        self._btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {tx};
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 700;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {bd};
            }}
        """)

    def _on_click(self):
        self._dark = not self._dark
        self.toggled.emit(self._dark)

    def sync(self):
        self._refresh()



# ══════════════════════════════════════════════════════════════
#  STYLED CHECKBOX (custom painted with checkmark)
# ══════════════════════════════════════════════════════════════
class StyledCheckBox(QWidget):
    """Custom checkbox widget that paints a visible checkmark when checked."""
    stateChanged = pyqtSignal(int)
    _BOX = 20

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._checked = False
        self._text = text
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(32)

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        return QSize(self._BOX + 10 + fm.horizontalAdvance(self._text) + 8, 32)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        b = self._BOX
        by = (self.height() - b) // 2
        if self._checked:
            painter.setBrush(QBrush(QColor(T["ac_blue"])))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, by, b, b, 6, 6)
            pen = QPen(QColor("white"), 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(4, by + b // 2 + 1, b // 2 - 1, by + b - 4)
            painter.drawLine(b // 2 - 1, by + b - 4, b - 3, by + 4)
        else:
            painter.setBrush(QBrush(QColor(T["bg_surface"])))
            painter.setPen(QPen(QColor(T["bd_strong"]), 1.5))
            painter.drawRoundedRect(0, by, b, b, 6, 6)
        painter.setPen(QPen(QColor(T["tx_secondary"])))
        f = self.font()
        painter.setFont(f)
        painter.drawText(b + 10, 0, self.width() - b - 10, self.height(),
                         Qt.AlignVCenter, self._text)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.update()
        self.stateChanged.emit(2 if self._checked else 0)

    def isChecked(self):
        return self._checked

    def setChecked(self, val: bool):
        self._checked = bool(val)
        self.update()

    def refresh_theme(self):
        self.update()


# ══════════════════════════════════════════════════════════════
#  STAT CARD
# ══════════════════════════════════════════════════════════════
class StatCard(QFrame):
    def __init__(self, label, value, accent, bg_key, bd_key, parent=None):
        super().__init__(parent)
        self._label = label
        self._accent = accent
        self._bg_key = bg_key
        self._bd_key = bd_key
        self.setFixedHeight(88)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(3)

        self._val_lbl = QLabel(str(value))
        self._val_lbl.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {accent}; background: transparent; letter-spacing: -0.5px;")
        self._txt_lbl = QLabel(label)
        self._txt_lbl.setStyleSheet(f"font-size: 12px; color: {T['tx_secondary']}; background: transparent; font-weight: 600;")

        lay.addWidget(self._val_lbl)
        lay.addWidget(self._txt_lbl)
        self._restyle()

    def _restyle(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {T[self._bg_key]};
                border-radius: 14px;
                border: none;
            }}
        """)
        gfx_shadow(self, 12, T["shadow"])

    def set_value(self, v):
        self._val_lbl.setText(str(v))

    def refresh_theme(self):
        self._restyle()
        self._txt_lbl.setStyleSheet(f"font-size: 12px; color: {T['tx_secondary']}; background: transparent; font-weight: 600;")


# ══════════════════════════════════════════════════════════════
#  DETAIL DIALOG
# ══════════════════════════════════════════════════════════════
class DetailDialog(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(620, 640)
        self._build()

    def _build(self):
        is_lomba = self.item["type"] == "Lomba"
        accent   = T["ac_blue"] if is_lomba else T["ac_violet"]
        accent_lt= T["ac_blue_lt"] if is_lomba else T["ac_violet_lt"]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {T['bg_surface']};
                border-radius: 22px;
                border: none;
            }}
        """)
        gfx_shadow(card, 60, QColor(0, 0, 0, 60 if T["mode"]=="dark" else 30))
        outer.addWidget(card)

        ml = QVBoxLayout(card)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        banner = QFrame()
        banner.setFixedHeight(130)
        banner.setStyleSheet(f"""
            QFrame {{
                background: {accent_lt};
                border-top-left-radius: 22px;
                border-top-right-radius: 22px;
                border: none;
            }}
        """)
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(28, 20, 28, 20)
        bl.setSpacing(0)
        icon_lbl = QLabel(item_icon(self.item))
        icon_lbl.setStyleSheet("font-size: 52px; background: transparent;")
        bl.addWidget(icon_lbl)
        bl.addStretch()
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        type_chip = Chip(self.item["type"], T["tx_on_accent"], accent)
        right_col.addStretch()
        right_col.addWidget(type_chip, alignment=Qt.AlignRight)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(34, 34)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {T['bg_card']};
                color: {T['tx_secondary']};
                border-radius: 17px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background: {T['ac_rose_lt']};
                color: {T['ac_rose']};
            }}
        """)
        close_btn.clicked.connect(self.close)
        right_col.addWidget(close_btn, alignment=Qt.AlignRight)
        right_col.addStretch()
        bl.addLayout(right_col)
        ml.addWidget(banner)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {T['bg_base']}; width: 5px; border-radius: 3px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {T['bd_strong']}; border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        ml.addWidget(scroll)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        scroll.setWidget(body)
        blay = QVBoxLayout(body)
        blay.setContentsMargins(28, 22, 28, 12)
        blay.setSpacing(12)

        title = QLabel(self.item["title"])
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {T['tx_primary']}; background: transparent; letter-spacing: -0.3px;")
        blay.addWidget(title)

        mrow = QHBoxLayout()
        org = QLabel(f"🏢  {self.item['organizer']}")
        org.setStyleSheet(f"font-size: 14px; color: {T['tx_secondary']}; background: transparent;")
        d = self.item["days"]
        dl_color = T["ac_rose"] if d<=7 else T["ac_amber"] if d<=14 else T["ac_green"]
        dl = QLabel(f"📅  {self.item['deadline']}  ·  {d} hari lagi")
        dl.setStyleSheet(f"font-size: 14px; color: {dl_color}; font-weight: 700; background: transparent;")
        mrow.addWidget(org); mrow.addStretch(); mrow.addWidget(dl)
        blay.addLayout(mrow)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {T['bd_base']}; border: none; max-height: 1px;")
        div.setFixedHeight(1)
        blay.addWidget(div)

        self._sec(blay, "Deskripsi", accent)
        desc_text = self.item.get("desc") or "Kunjungi website resmi untuk informasi lengkap mengenai program ini."
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 14px; color: {T['tx_secondary']}; background: transparent;")
        blay.addWidget(desc)

        self._sec(blay, "Persyaratan", accent)
        req_frame = QFrame()
        req_frame.setStyleSheet(f"QFrame {{ background: {T['bg_base']}; border-radius: 12px; border: none; }}")
        rfl = QVBoxLayout(req_frame); rfl.setContentsMargins(16, 12, 16, 12); rfl.setSpacing(8)
        reqs = self.item.get("reqs") or []
        if reqs:
            for r in reqs:
                row = QHBoxLayout()
                dot = QLabel("✓"); dot.setFixedWidth(22)
                dot.setStyleSheet(f"font-size: 13px; color: {T['ac_green']}; font-weight: 700; background: transparent;")
                txt = QLabel(r); txt.setWordWrap(True)
                txt.setStyleSheet(f"font-size: 14px; color: {T['tx_secondary']}; background: transparent;")
                row.addWidget(dot); row.addWidget(txt); row.addStretch()
                rfl.addLayout(row)
        else:
            no_req = QLabel("Lihat persyaratan lengkap di website resmi.")
            no_req.setStyleSheet(f"font-size: 14px; color: {T['tx_muted']}; background: transparent; font-style: italic;")
            rfl.addWidget(no_req)
        blay.addWidget(req_frame)

        self._sec(blay, "Hadiah & Keuntungan", T["ac_green"])
        prize_frame = QFrame()
        prize_frame.setStyleSheet(f"QFrame {{ background: {T['ac_green_lt']}; border-radius: 12px; border: none; }}")
        pfl = QVBoxLayout(prize_frame); pfl.setContentsMargins(16, 12, 16, 12); pfl.setSpacing(8)
        prizes = self.item.get("prizes") or []
        if prizes:
            for p in prizes:
                row = QHBoxLayout()
                dot = QLabel("★"); dot.setFixedWidth(22)
                dot.setStyleSheet(f"font-size: 11px; color: {T['ac_green']}; background: transparent;")
                txt = QLabel(p); txt.setWordWrap(True)
                txt.setStyleSheet(f"font-size: 14px; color: {T['ac_green']}; font-weight: 600; background: transparent;")
                row.addWidget(dot); row.addWidget(txt); row.addStretch()
                pfl.addLayout(row)
        else:
            no_prize = QLabel("Lihat hadiah dan keuntungan lengkap di website resmi.")
            no_prize.setStyleSheet(f"font-size: 14px; color: {T['ac_green']}; background: transparent; font-style: italic;")
            pfl.addWidget(no_prize)
        blay.addWidget(prize_frame)
        blay.addStretch()

        foot = QHBoxLayout()
        foot.setContentsMargins(28, 6, 28, 24)
        foot.setSpacing(10)
        visit = QPushButton("  🔗  Kunjungi Website Resmi")
        visit.setFixedHeight(48)
        visit.setCursor(QCursor(Qt.PointingHandCursor))
        visit.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {accent}, stop:1 {T['ac_cyan']});
                color: white; border-radius: 13px;
                font-size: 14px; font-weight: 800; border: none;
            }}
        """)
        _url = self.item.get("url", "#")
        visit.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(_url)) if _url and _url != "#" else None)
        foot.addWidget(visit)
        close2 = QPushButton("Tutup")
        close2.setFixedSize(100, 48)
        close2.setCursor(QCursor(Qt.PointingHandCursor))
        close2.setStyleSheet(f"""
            QPushButton {{
                background: {T['bg_base']};
                color: {T['tx_secondary']};
                border-radius: 13px;
                font-size: 14px; font-weight: 600; border: none;
            }}
            QPushButton:hover {{
                color: {T['ac_rose']}; background: {T['ac_rose_lt']};
            }}
        """)
        close2.clicked.connect(self.close)
        foot.addWidget(close2)
        ml.addLayout(foot)

    def _sec(self, layout, text, color):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(f"font-size: 11px; font-weight: 800; color: {color}; background: transparent; letter-spacing: 1px;")
        layout.addWidget(lbl)


# ══════════════════════════════════════════════════════════════
#  ITEM CARD
# ══════════════════════════════════════════════════════════════
class ItemCard(QFrame):
    detail_clicked = pyqtSignal(dict)

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setMinimumWidth(240)
        self.setMinimumHeight(272)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._is_lomba = item["type"] == "Lomba"
        self._build()

    def _build(self):
        accent    = T["ac_blue"]   if self._is_lomba else T["ac_violet"]
        accent_lt = T["ac_blue_lt"] if self._is_lomba else T["ac_violet_lt"]

        self.setStyleSheet(f"""
            QFrame {{
                background: {T['bg_card']};
                border-radius: 18px;
                border: none;
            }}
            QFrame:hover {{
                background: {T['bg_card_hov']};
                border: none;
            }}
        """)
        gfx_shadow(self, 16, T["card_shadow"])

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Banner ──
        top = QFrame()
        top.setFixedHeight(100)
        top.setStyleSheet(f"""
            QFrame {{
                background: {accent_lt};
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }}
        """)
        tl = QVBoxLayout(top)
        tl.setContentsMargins(14, 10, 14, 10)
        tl.setSpacing(0)

        # Badges row
        br = QHBoxLayout()
        br.setSpacing(6)
        type_chip = Chip(self.item["type"], T["tx_on_accent"], accent)
        br.addWidget(type_chip)
        if self.item.get("urgent"):
            urg = Chip("⚡ Segera", T["tx_on_accent"], T["ac_rose"])
            br.addWidget(urg)
        if not self.item["active"]:
            nc = Chip("Nonaktif", T["tx_primary"], T["bd_strong"])
            br.addWidget(nc)
        br.addStretch()
        tl.addLayout(br)
        tl.addStretch()

        icon_lbl = QLabel(item_icon(self.item))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 30px; background: transparent;")
        tl.addWidget(icon_lbl)
        lay.addWidget(top)

        # ── Body ──
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(17, 13, 17, 15)
        bl.setSpacing(6)

        title = QLabel(self.item["title"])
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {T['tx_primary']}; background: transparent; letter-spacing: -0.1px;")
        bl.addWidget(title)

        org = QLabel(f"  {self.item['organizer']}")
        org.setStyleSheet(f"font-size: 12px; color: {T['tx_muted']}; background: transparent;")
        bl.addWidget(org)

        d = self.item["days"]
        dl_color = T["ac_rose"] if d<=7 else T["ac_amber"] if d<=14 else T["tx_muted"]
        dl = QLabel(f"📅  {self.item['deadline']}")
        dl.setStyleSheet(f"font-size: 12px; color: {dl_color}; font-weight: 600; background: transparent;")
        bl.addWidget(dl)

        # Tags
        tr = QHBoxLayout()
        tr.setSpacing(6)
        for tag in [self.item["cat"], self.item["level"].split("/")[0]]:
            t = QLabel(tag)
            t.setStyleSheet(f"""
                background: {T['bg_base']};
                color: {T['tx_secondary']};
                border-radius: 6px;
                padding: 2px 9px;
                font-size: 11px;
                font-weight: 600;
                border: none;
            """)
            tr.addWidget(t)
        tr.addStretch()
        bl.addLayout(tr)
        bl.addStretch()

        # Button
        btn = QPushButton("Lihat Detail →")
        btn.setFixedHeight(38)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent_lt};
                color: {accent};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 700;
                border: none;
                margin-top: 4px;
            }}
            QPushButton:hover {{
                background: {accent};
                color: {'white'};
                border: none;
            }}
        """)
        btn.clicked.connect(lambda: self.detail_clicked.emit(self.item))
        bl.addWidget(btn)
        lay.addWidget(body)


# ══════════════════════════════════════════════════════════════
#  DEADLINE ITEM (sidebar) — bisa diklik, buka DetailDialog
# ══════════════════════════════════════════════════════════════
class DeadlineItem(QFrame):
    detail_clicked = pyqtSignal(dict)

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self._item = item
        d = item["days"]
        accent    = T["ac_rose"]    if d <= 7  else T["ac_amber"]    if d <= 14 else T["ac_green"]
        accent_lt = T["ac_rose_lt"] if d <= 7  else T["ac_amber_lt"] if d <= 14 else T["ac_green_lt"]
        self._accent    = accent
        self._accent_lt = accent_lt

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._base_style = f"""
            QFrame {{
                background: {accent_lt};
                border-radius: 14px;
                border: none;
            }}
        """
        self._hover_style = f"""
            QFrame {{
                background: {accent};
                border-radius: 14px;
                border: none;
            }}
        """
        self.setStyleSheet(self._base_style)
        gfx_shadow(self, 6, T["card_shadow"])

        outer = QHBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        # Circle icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(38, 38)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: {accent};
                border-radius: 19px;
                border: none;
            }}
        """)
        icon_lay = QHBoxLayout(icon_frame)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel("⏰")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
        icon_lay.addWidget(icon_lbl)
        outer.addWidget(icon_frame, alignment=Qt.AlignTop)

        # Right content
        right = QVBoxLayout()
        right.setSpacing(3)

        title = QLabel(item["title"])
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {T['tx_primary']}; background: transparent;")

        org = QLabel(item["organizer"])
        org.setStyleSheet(f"font-size: 12px; color: {T['tx_muted']}; background: transparent;")

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)
        dl_lbl = QLabel(f"{d} hari lagi")
        dl_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {accent}; background: transparent;")

        chip_color = T["ac_blue"] if item["type"] == "Lomba" else T["ac_violet"]
        type_chip = Chip(item["type"], T["tx_on_accent"], chip_color)

        bottom_row.addWidget(dl_lbl)
        bottom_row.addStretch()
        bottom_row.addWidget(type_chip)

        right.addWidget(title)
        right.addWidget(org)
        right.addSpacing(4)
        right.addLayout(bottom_row)

        outer.addLayout(right, 1)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._base_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.detail_clicked.emit(self._item)
        super().mousePressEvent(event)


# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
class Header(QWidget):
    filter_changed = pyqtSignal()
    theme_toggled  = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._current_filter = "Semua"
        self.setAutoFillBackground(True)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background: {T['bg_header']};")
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 0, 36, 0)
        root.setSpacing(0)

        # ── Top bar ──
        top_bar = QWidget()
        top_bar.setStyleSheet("background: transparent;")
        tbl = QHBoxLayout(top_bar)
        tbl.setContentsMargins(0, 18, 0, 14)
        tbl.setSpacing(0)

        # Logo
        logo = QFrame()
        logo.setFixedSize(44, 44)
        logo.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {T['ac_blue']}, stop:1 {T['ac_cyan']});
                border-radius: 13px;
            }}
        """)
        ll = QHBoxLayout(logo); ll.setContentsMargins(0,0,0,0)
        li = QLabel("✦")
        li.setAlignment(Qt.AlignCenter)
        li.setStyleSheet(f"font-size: 20px; color: white; background: transparent; font-weight: 900;")
        ll.addWidget(li)
        gfx_shadow(logo, 14, T["shadow"])

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        app_title = QLabel("Scholarship & Competition Hub")
        app_title.setStyleSheet(f"font-size: 20px; font-weight: 900; color: {T['tx_primary']}; background: transparent; letter-spacing: -0.5px;")
        subtitle = QLabel("Temukan beasiswa dan lomba terbaik untuk masa depanmu")
        subtitle.setStyleSheet(f"font-size: 13px; color: {T['tx_muted']}; background: transparent;")
        title_col.addWidget(app_title)
        title_col.addWidget(subtitle)

        tbl.addWidget(logo)
        tbl.addSpacing(13)
        tbl.addLayout(title_col)
        tbl.addStretch()

        # Search container (input + hint label)
        _search_container = QWidget()
        _search_container.setStyleSheet("background: transparent;")
        _sc_lay = QVBoxLayout(_search_container)
        _sc_lay.setContentsMargins(0, 0, 0, 0)
        _sc_lay.setSpacing(3)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("  Cari beasiswa atau lomba...")
        self.search_input.setFixedSize(300, 42)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {T['bg_input']};
                border: none;
                border-radius: 12px;
                padding: 0 16px;
                font-size: 13px;
                color: {T['tx_primary']};
            }}
            QLineEdit:focus {{
                border: none;
                background: {T['bg_surface']};
            }}
            QLineEdit::placeholder {{
                color: {T['tx_muted']};
            }}
        """)
        _sc_lay.addWidget(self.search_input)

        self.search_hint = QLabel("⚠  Masukkan minimal 3 huruf untuk mencari")
        self.search_hint.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {T['ac_amber']};"
            " background: transparent; padding-left: 6px;"
        )
        self.search_hint.setVisible(False)
        _sc_lay.addWidget(self.search_hint)

        tbl.addWidget(_search_container)
        tbl.addSpacing(10)

        # Theme toggle
        self.theme_toggle = ThemeToggle()
        self.theme_toggle.toggled.connect(self.theme_toggled.emit)
        tbl.addWidget(self.theme_toggle)
        tbl.addSpacing(10)

        # Collapse btn
        self._toggle_btn = QPushButton("▲")
        self._toggle_btn.setFixedSize(38, 38)
        self._toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._toggle_btn.clicked.connect(self._toggle_collapse)
        self._style_collapse_btn()
        tbl.addWidget(self._toggle_btn)

        root.addWidget(top_bar)

        # ── Collapsible ──
        self._collapsible = QWidget()
        self._collapsible.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(self._collapsible)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(12)

        # Stats row
        self._stat_row = QHBoxLayout()
        self._stat_row.setSpacing(14)
        self._stats = {}
        stat_cfg = [
            ("Total Peluang", 12, T["ac_blue"],   "stat1_bg", "stat1_bd"),
            ("Beasiswa",       6, T["ac_violet"], "stat2_bg", "stat2_bd"),
            ("Lomba",          6, T["ac_cyan"],   "stat3_bg", "stat3_bd"),
            ("Masih Aktif",   11, T["ac_green"],  "stat4_bg", "stat4_bd"),
        ]
        for lbl, val, acc, bg_k, bd_k in stat_cfg:
            sc = StatCard(lbl, val, acc, bg_k, bd_k)
            self._stat_row.addWidget(sc)
            self._stats[lbl] = sc
        cl.addLayout(self._stat_row)

        # Filter bar
        filter_w = QWidget()
        filter_w.setStyleSheet("background: transparent;")
        fl = QHBoxLayout(filter_w)
        fl.setContentsMargins(0, 0, 0, 16)
        fl.setSpacing(8)

        flbl = QLabel("Filter :")
        flbl.setStyleSheet(f"font-size: 13px; color: {T['tx_muted']}; background: transparent;")
        fl.addWidget(flbl)

        self.btn_semua    = self._make_filter_btn("Semua",       active=True)
        self.btn_beasiswa = self._make_filter_btn("🎓 Beasiswa", active=False)
        self.btn_lomba    = self._make_filter_btn("🏆 Lomba",    active=False)
        for b in [self.btn_semua, self.btn_beasiswa, self.btn_lomba]:
            fl.addWidget(b)

        # Combo wrapper
        self._combo_wrap = QWidget()
        self._combo_wrap.setStyleSheet("background: transparent;")
        cw = QHBoxLayout(self._combo_wrap)
        cw.setContentsMargins(0,0,0,0)
        cw.setSpacing(8)
        self.combo_cat   = self._make_combo(CATEGORIES_BEASISWA)
        self.combo_level = self._make_combo(LEVELS_BEASISWA)
        cw.addWidget(self.combo_cat)
        cw.addWidget(self.combo_level)
        self._combo_wrap.setVisible(False)
        fl.addWidget(self._combo_wrap)

        fl.addStretch()

        self.chk_active = StyledCheckBox("Hanya aktif")
        self.chk_active.setChecked(True)
        fl.addWidget(self.chk_active)
        cl.addWidget(filter_w)
        root.addWidget(self._collapsible)

        # Separator
        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {T['bd_base']}; border: none;")
        root.addWidget(sep)

        # Connections
        self.btn_semua.clicked.connect(lambda: self._set_filter("Semua"))
        self.btn_beasiswa.clicked.connect(lambda: self._set_filter("Beasiswa"))
        self.btn_lomba.clicked.connect(lambda: self._set_filter("Lomba"))

    def _make_filter_btn(self, text, active=False):
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._style_filter_btn(btn, active)
        return btn

    def _style_filter_btn(self, btn, active):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {T['filt_act_bg']};
                    color: {T['filt_act_tx']};
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: 700;
                    border: none;
                    padding: 0 18px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {T['filt_idle_bg']};
                    color: {T['filt_idle_tx']};
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: 600;
                    border: none;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    color: {T['ac_blue']};
                    border-color: transparent;
                    background: {T['ac_blue_lt']};
                }}
            """)

    def _set_filter(self, mode):
        self._current_filter = mode
        self._style_filter_btn(self.btn_semua,    mode=="Semua")
        self._style_filter_btn(self.btn_beasiswa, mode=="Beasiswa")
        self._style_filter_btn(self.btn_lomba,    mode=="Lomba")
        self._combo_wrap.setVisible(mode != "Semua")
        if mode != "Semua":
            self.update_combos(mode)
        self.filter_changed.emit()

    def update_combos(self, mode):
        """Isi ulang combo kategori & jenjang sesuai tipe filter (Beasiswa/Lomba)."""
        is_lomba = (mode == "Lomba")
        cats   = CATEGORIES_LOMBA    if is_lomba else CATEGORIES_BEASISWA
        levels = LEVELS_LOMBA        if is_lomba else LEVELS_BEASISWA

        self.combo_cat.blockSignals(True)
        self.combo_level.blockSignals(True)
        self.combo_cat.clear()
        self.combo_level.clear()
        for c in cats:
            self.combo_cat.addItem(c)
        for l in levels:
            self.combo_level.addItem(l)
        self.combo_cat.blockSignals(False)
        self.combo_level.blockSignals(False)

    def _make_combo(self, items):
        cb = QComboBox()
        for i in items:
            cb.addItem(i)
        cb.setFixedHeight(36)
        cb.setStyleSheet(f"""
            QComboBox {{
                background: {T['bg_input']};
                border: none;
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
                color: {T['tx_primary']};
                min-width: 148px;
            }}
            QComboBox:hover {{ border-color: transparent; }}
            QComboBox QAbstractItemView {{
                background: {T['bg_surface']};
                border: none;
                selection-background-color: {T['ac_blue_lt']};
                color: {T['tx_primary']};
                padding: 4px;
                outline: 0;
            }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
        """)
        return cb

    def _style_checkbox(self):
        self.chk_active.refresh_theme()

    def _style_collapse_btn(self):
        self._toggle_btn.setText("▲" if not self._collapsed else "▼")
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {T['bg_input']};
                color: {T['tx_muted']};
                border-radius: 10px;
                font-size: 11px;
                font-weight: 700;
                border: none;
            }}
            QPushButton:hover {{
                color: {T['ac_blue']};
                border-color: transparent;
                background: {T['ac_blue_lt']};
            }}
        """)

    def _toggle_collapse(self):
        self._collapsed = not self._collapsed
        self._collapsible.setVisible(not self._collapsed)
        self._style_collapse_btn()

    def update_stats(self, total, bea, lomba, aktif):
        self._stats["Total Peluang"].set_value(total)
        self._stats["Beasiswa"].set_value(bea)
        self._stats["Lomba"].set_value(lomba)
        self._stats["Masih Aktif"].set_value(aktif)

    def full_restyle(self):
        self.setStyleSheet(f"background: {T['bg_header']};")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {T['bg_input']};
                border: none;
                border-radius: 12px;
                padding: 0 16px;
                font-size: 13px;
                color: {T['tx_primary']};
            }}
            QLineEdit:focus {{
                border: none;
                background: {T['bg_surface']};
            }}
        """)
        self.search_hint.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {T['ac_amber']};"
            " background: transparent; padding-left: 6px;"
        )
        self.theme_toggle.sync()
        self._style_collapse_btn()
        self._style_filter_btn(self.btn_semua,    self._current_filter=="Semua")
        self._style_filter_btn(self.btn_beasiswa, self._current_filter=="Beasiswa")
        self._style_filter_btn(self.btn_lomba,    self._current_filter=="Lomba")
        for cb in [self.combo_cat, self.combo_level]:
            cb.setStyleSheet(f"""
                QComboBox {{
                    background: {T['bg_input']};
                    border: none;
                    border-radius: 10px;
                    padding: 0 12px;
                    font-size: 13px;
                    color: {T['tx_primary']};
                    min-width: 148px;
                }}
                QComboBox:hover {{ border-color: transparent; }}
                QComboBox QAbstractItemView {{
                    background: {T['bg_surface']};
                    border: none;
                    selection-background-color: {T['ac_blue_lt']};
                    color: {T['tx_primary']};
                    padding: 4px;
                }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
            """)
        self._style_checkbox()
        for sc in self._stats.values():
            sc.refresh_theme()


# ══════════════════════════════════════════════════════════════
#  DASHBOARD WIDGET — grafik analisis dinamis
# ══════════════════════════════════════════════════════════════
class DashboardWidget(QWidget):
    """
    Tab dashboard yang berisi grafik analisis data beasiswa & lomba.
    Grafik bersifat DINAMIS — bisa di-refresh berkali-kali via update_charts(data).
    Tidak ada grafik statis yang dibuat sekali di __init__.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_data = []
        self._build_skeleton()

    # ── Skeleton UI (tanpa grafik) ────────────────────────────
    def _build_skeleton(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {T['bg_base']}; width: 6px; border-radius: 3px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {T['bd_strong']}; border-radius: 3px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        outer.addWidget(scroll)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        scroll.setWidget(inner)

        self._lay = QVBoxLayout(inner)
        self._lay.setContentsMargins(36, 26, 36, 26)
        self._lay.setSpacing(20)

        # ── Judul ──
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_icon = QLabel("📊")
        title_icon.setStyleSheet("font-size: 26px; background: transparent;")
        title_lbl = QLabel("Dashboard Analisis")
        title_lbl.setStyleSheet(
            f"font-size: 22px; font-weight: 900; color: {T['tx_primary']};"
            " background: transparent; letter-spacing: -0.4px;"
        )
        title_sub = QLabel("Statistik dan distribusi data beasiswa & lomba")
        title_sub.setStyleSheet(
            f"font-size: 13px; color: {T['tx_muted']}; background: transparent;"
        )
        tcol = QVBoxLayout(); tcol.setSpacing(2)
        tcol.addWidget(title_lbl); tcol.addWidget(title_sub)
        title_row.addWidget(title_icon); title_row.addLayout(tcol); title_row.addStretch()
        self._lay.addLayout(title_row)

        # ── Area grafik ──
        if not HAS_MPL:
            self._no_mpl_label = QLabel(
                "⚠  Matplotlib tidak terinstall.\n"
                "Jalankan:  pip install matplotlib\n"
                "lalu restart aplikasi."
            )
            self._no_mpl_label.setAlignment(Qt.AlignCenter)
            self._no_mpl_label.setStyleSheet(
                f"font-size: 15px; color: {T['ac_rose']}; background: transparent; padding: 40px;"
            )
            self._lay.addWidget(self._no_mpl_label)
            return

        # Buat Figure sekali saja – isinya dikosongkan & digambar ulang di update_charts
        self._fig = Figure(facecolor="none")
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("background: transparent;")
        self._canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._canvas.setMinimumHeight(380)
        self._lay.addWidget(self._canvas)

        # Placeholder sebelum data pertama dimuat
        self._draw_empty_state()

    # ── Helper: hex → tuple matplotlib ───────────────────────
    @staticmethod
    def _hex(h: str, alpha: float = 1.0):
        h = h.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        return (r, g, b, alpha)

    # ── Placeholder saat belum ada data ──────────────────────
    def _draw_empty_state(self):
        if not HAS_MPL:
            return
        self._fig.clear()
        ax = self._fig.add_subplot(1, 1, 1)
        ax.set_facecolor("none")
        ax.text(
            0.5, 0.5,
            "📂  Belum ada data.\nKlik  🔄 Refresh Data  untuk memuat data.",
            ha="center", va="center", fontsize=13,
            color=self._hex(T["tx_muted"])[:3],
            transform=ax.transAxes
        )
        ax.axis("off")
        self._canvas.draw()

    # ══════════════════════════════════════════════════════════
    #  update_charts  ←  METHOD UTAMA yang dipanggil dari luar
    # ══════════════════════════════════════════════════════════
    def update_charts(self, data: list):
        """
        Refresh seluruh dashboard berdasarkan data terbaru.

        Alur:
          1. Hitung ulang statistik (total, beasiswa, lomba, aktif)
          2. Perbarui StatCard mini di atas
          3. Bersihkan Figure lama  (fig.clear())
          4. Gambar 3 grafik baru
          5. Panggil canvas.draw()

        Tidak ada duplikasi canvas, tidak ada figure menumpuk.
        """
        self._last_data = data

        # ── 1. Hitung ulang statistik ──────────────────────
        total   = len(data)
        beasiswa = sum(1 for d in data if d["type"] == "Beasiswa")
        lomba    = sum(1 for d in data if d["type"] == "Lomba")
        aktif    = sum(1 for d in data if d.get("active", True))

        if not HAS_MPL:
            return

        if not data:
            self._draw_empty_state()
            return

        # ── 2. Warna dari tema aktif ───────────────────────
        h      = self._hex
        tx     = h(T["tx_primary"])[:3]
        tx2    = h(T["tx_secondary"])[:3]
        bd     = h(T["bd_base"])[:3]
        c_bea  = h(T["ac_violet"])
        c_lom  = h(T["ac_blue"])
        palette = [
            T["ac_blue"], T["ac_violet"], T["ac_cyan"],
            T["ac_green"], T["ac_amber"], T["ac_rose"],
        ]

        # ── 3. Bersihkan figure lama ───────────────────────
        self._fig.clear()
        self._fig.set_facecolor("none")

        # ── 4a. Subplot 1 — Bar: Beasiswa vs Lomba ─────────
        ax1 = self._fig.add_subplot(1, 3, 1)
        ax1.set_facecolor("none")

        bars = ax1.bar(
            ["Beasiswa", "Lomba"], [beasiswa, lomba],
            color=[c_bea, c_lom], width=0.5, zorder=3,
            edgecolor="none"
        )
        ax1.set_title("Beasiswa vs Lomba", color=tx, fontsize=11,
                      fontweight="bold", pad=10)
        for spine in ("top", "right"):
            ax1.spines[spine].set_visible(False)
        for spine in ("bottom", "left"):
            ax1.spines[spine].set_color(bd)
        ax1.tick_params(colors=tx2, labelsize=9)
        for lbl in ax1.get_xticklabels() + ax1.get_yticklabels():
            lbl.set_color(tx2)
        ax1.grid(axis="y", color=bd, alpha=0.6, zorder=0, linewidth=0.8)
        # Nilai di atas bar
        for bar, val in zip(bars, [beasiswa, lomba]):
            if val > 0:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(0.2, total * 0.01),
                    str(val), ha="center", va="bottom",
                    color=tx, fontweight="bold", fontsize=10
                )

        # ── 4b. Subplot 2 — Pie: Kategori ──────────────────
        ax2 = self._fig.add_subplot(1, 3, 2)
        ax2.set_facecolor("none")

        cat_counts: dict[str, int] = {}
        for d in data:
            cat = (d.get("cat") or "Lainnya").strip() or "Lainnya"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        if cat_counts:
            labels = list(cat_counts.keys())
            sizes  = list(cat_counts.values())
            colors = [h(palette[i % len(palette)]) for i in range(len(labels))]
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=labels, autopct="%1.0f%%",
                colors=colors, startangle=90, pctdistance=0.75,
                textprops={"fontsize": 8, "color": tx}
            )
            for at in autotexts:
                at.set_color(tx)
                at.set_fontsize(8)
        ax2.set_title("Distribusi Kategori", color=tx, fontsize=11,
                      fontweight="bold", pad=10)

        # ── 4c. Subplot 3 — Horizontal bar: Jenjang ────────
        ax3 = self._fig.add_subplot(1, 3, 3)
        ax3.set_facecolor("none")

        level_counts: dict[str, int] = {}
        for d in data:
            raw = d.get("level", "") or ""
            for part in raw.split("/"):
                part = part.strip()
                if part:
                    level_counts[part] = level_counts.get(part, 0) + 1

        if level_counts:
            sorted_lvl = sorted(level_counts.items(), key=lambda x: x[1], reverse=True)
            lvl_labels = [k for k, _ in sorted_lvl]
            lvl_vals   = [v for _, v in sorted_lvl]
            colors3    = [h(palette[i % len(palette)]) for i in range(len(lvl_labels))]
            bars3 = ax3.barh(
                lvl_labels, lvl_vals,
                color=colors3, height=0.55, zorder=3, edgecolor="none"
            )
            for spine in ("top", "right"):
                ax3.spines[spine].set_visible(False)
            for spine in ("bottom", "left"):
                ax3.spines[spine].set_color(bd)
            ax3.tick_params(colors=tx2, labelsize=8)
            for lbl in ax3.get_xticklabels() + ax3.get_yticklabels():
                lbl.set_color(tx2)
            ax3.grid(axis="x", color=bd, alpha=0.6, zorder=0, linewidth=0.8)
            max_v = max(lvl_vals) if lvl_vals else 1
            for bar3, val in zip(bars3, lvl_vals):
                ax3.text(
                    bar3.get_width() + max(0.1, max_v * 0.02),
                    bar3.get_y() + bar3.get_height() / 2,
                    str(val), va="center",
                    color=tx, fontweight="bold", fontsize=9
                )
        ax3.set_title("Distribusi Jenjang", color=tx, fontsize=11,
                      fontweight="bold", pad=10)

        # ── 5. Render ──────────────────────────────────────
        self._fig.tight_layout(pad=2.0)
        self._canvas.draw()

    # ── Dipanggil saat tema berubah ───────────────────────────
    def refresh_theme(self):
        """Gambar ulang grafik dengan warna tema terbaru."""
        if self._last_data:
            self.update_charts(self._last_data)
        elif HAS_MPL:
            self._draw_empty_state()


# ══════════════════════════════════════════════════════════════
#  SCRAPE WORKER — jalankan scraping di background thread
# ══════════════════════════════════════════════════════════════
class ScrapeWorker(QThread):
    """
    Worker thread untuk scraping agar UI tidak freeze.

    Sinyal:
        finished(list)  → data baru berhasil dimuat
        error(str)      → pesan error jika scraping gagal
        progress(str)   → status/pesan sementara (opsional untuk status bar)

    Cara pakai di MainWindow:
        self._worker = ScrapeWorker()
        self._worker.finished.connect(self.on_scrape_finished)
        self._worker.error.connect(self.on_scrape_error)
        self._worker.progress.connect(self._set_status)
        self._worker.start()
    """

    finished = pyqtSignal(list)   # data_baru: list[dict]
    error    = pyqtSignal(str)    # pesan error
    progress = pyqtSignal(str)    # status sementara

    def run(self):
        try:
            import database as _db
            import scrapbeasiswa as _sb
            import scraplomba as _sl

            self.progress.emit("⏳  [1/3] Scraping beasiswa...")
            data_beasiswa = _sb.scrape_beasiswa()
            self.progress.emit(f"⏳  [2/3] Scraping lomba... ({len(data_beasiswa)} beasiswa ditemukan)")
            data_lomba = _sl.scrape_lomba()
            self.progress.emit("⏳  [3/3] Menyimpan ke database...")

            koneksi, kursor = _db.init_database()
            try:
                _db.simpan_semua_beasiswa(koneksi, data_beasiswa)
                _db.simpan_semua_lomba(koneksi, data_lomba)
                koneksi.commit()
                data_baru = _db.muat_data_dari_db(kursor)
            finally:
                koneksi.close()

            self.progress.emit(f"✅  Scraping selesai — {len(data_baru)} item ditemukan")
            self.finished.emit(data_baru)

        except Exception as exc:
            self.error.emit(f"❌  Scraping gagal: {exc}")


# ══════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scholarship & Competition Hub")
        self.setMinimumSize(1100, 700)
        self.resize(1300, 860)

        # Data lokal (sinkron dengan global DATA)
        self.data: list = list(DATA)

        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(80)
        self._resize_timer.timeout.connect(self._refresh)

        # Worker scraping (QThread)
        self._worker: ScrapeWorker | None = None

        self._build()
        self._connect()

        # Normalisasi data dan bangun opsi filter dari data aktual
        if DATA:
            _build_dynamic_options(DATA)
        QTimer.singleShot(0, self._refresh)
        # Muat dashboard setelah UI siap
        QTimer.singleShot(100, lambda: self.dashboard_tab.update_charts(self.data))

    def _build(self):
        self._apply_base_style()
        central = QWidget()
        central.setStyleSheet(f"background: {T['bg_base']};")
        self.setCentralWidget(central)

        self._root = QVBoxLayout(central)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # ── Header ──
        self.header = Header()
        gfx_shadow(self.header, 10, QColor(0, 0, 0, 18 if T["mode"] == "light" else 50), 0, 2)
        self._root.addWidget(self.header)

        # ── Toolbar tipis: Refresh / Scrape + Status ──────
        self._toolbar = QWidget()
        self._toolbar.setFixedHeight(52)
        self._toolbar.setStyleSheet(f"background: {T['bg_surface']}; border: none;")
        tb_lay = QHBoxLayout(self._toolbar)
        tb_lay.setContentsMargins(36, 0, 36, 0)
        tb_lay.setSpacing(12)

        self._btn_scrape = QPushButton("🔄  Refresh Data")
        self._btn_scrape.setFixedHeight(36)
        self._btn_scrape.setCursor(QCursor(Qt.PointingHandCursor))
        self._btn_scrape.setStyleSheet(f"""
            QPushButton {{
                background: {T['ac_blue']};
                color: white;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 700;
                border: none;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background: {T['ac_cyan']};
            }}
            QPushButton:disabled {{
                background: {T['bd_base']};
                color: {T['tx_muted']};
            }}
        """)

        self._status_lbl = QLabel("Siap")
        self._status_lbl.setStyleSheet(
            f"font-size: 12px; color: {T['tx_muted']}; background: transparent;"
        )

        tb_lay.addWidget(self._btn_scrape)
        tb_lay.addWidget(self._status_lbl)
        tb_lay.addStretch()

        # Label terakhir update
        self._last_update_lbl = QLabel("")
        self._last_update_lbl.setStyleSheet(
            f"font-size: 11px; color: {T['tx_muted']}; background: transparent;"
        )
        tb_lay.addWidget(self._last_update_lbl)
        self._root.addWidget(self._toolbar)

        # ── Tab Widget ───────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {T['bg_base']};
            }}
            QTabBar::tab {{
                background: {T['bg_surface']};
                color: {T['tx_secondary']};
                border: none;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
                min-width: 130px;
                border-bottom: 3px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {T['ac_blue']};
                background: {T['bg_base']};
                border-bottom: 3px solid {T['ac_blue']};
                font-weight: 800;
            }}
            QTabBar::tab:hover:!selected {{
                background: {T['bg_card_hov']};
                color: {T['tx_primary']};
            }}
        """)
        self._root.addWidget(self._tabs)

        # ═══════════════════════════════════════════════
        #  Tab 0 — Daftar (konten asli)
        # ═══════════════════════════════════════════════
        self._list_tab = QWidget()
        self._list_tab.setStyleSheet(f"background: {T['bg_base']};")
        list_tab_lay = QHBoxLayout(self._list_tab)
        list_tab_lay.setContentsMargins(36, 22, 36, 22)
        list_tab_lay.setSpacing(22)

        # Kiri
        left = QVBoxLayout()
        left.setSpacing(14)

        count_row = QHBoxLayout()
        self._count_lbl = QLabel()
        self._count_lbl.setStyleSheet(
            f"font-size: 17px; font-weight: 800; color: {T['tx_primary']}; letter-spacing: -0.3px;"
        )
        count_row.addWidget(self._count_lbl)
        count_row.addStretch()
        left.addLayout(count_row)

        self._main_scroll = QScrollArea()
        self._main_scroll.setWidgetResizable(True)
        self._main_scroll.setFrameShape(QFrame.NoFrame)
        self._style_scroll(self._main_scroll)

        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background: transparent;")
        self._cards_grid = QGridLayout(self._cards_widget)
        self._cards_grid.setSpacing(18)
        self._cards_grid.setAlignment(Qt.AlignTop)
        self._main_scroll.setWidget(self._cards_widget)
        left.addWidget(self._main_scroll)
        list_tab_lay.addLayout(left, 3)

        # Sidebar
        self._sidebar_container = QWidget()
        self._sidebar_container.setStyleSheet("background: transparent;")
        self._sidebar_container.setMinimumWidth(260)
        self._sidebar_container.setMaximumWidth(400)
        sidebar = QVBoxLayout(self._sidebar_container)
        sidebar.setSpacing(10)
        sidebar.setContentsMargins(0, 0, 0, 0)

        sb_header = QFrame()
        sb_header.setStyleSheet(f"""
            QFrame {{
                background: {T['bg_surface']};
                border-radius: 14px;
                border: none;
            }}
        """)
        gfx_shadow(sb_header, 8, T["card_shadow"])
        sh_lay = QHBoxLayout(sb_header)
        sh_lay.setContentsMargins(16, 12, 16, 12)
        bell = QLabel("🔔")
        bell.setStyleSheet("font-size: 18px; background: transparent;")
        col = QVBoxLayout(); col.setSpacing(1)
        sb_t = QLabel("Deadline Mendekat")
        sb_t.setStyleSheet(
            f"font-size: 14px; font-weight: 800; color: {T['tx_primary']}; background: transparent;"
        )
        col.addWidget(sb_t)
        sh_lay.addWidget(bell); sh_lay.addSpacing(8); sh_lay.addLayout(col); sh_lay.addStretch()
        sidebar.addWidget(sb_header)

        self._dl_scroll = QScrollArea()
        self._dl_scroll.setWidgetResizable(True)
        self._dl_scroll.setFrameShape(QFrame.NoFrame)
        self._style_scroll(self._dl_scroll)

        dl_inner = QWidget()
        dl_inner.setStyleSheet("background: transparent;")
        self._dl_lay = QVBoxLayout(dl_inner)
        self._dl_lay.setSpacing(9)
        self._dl_lay.setAlignment(Qt.AlignTop)
        self._dl_scroll.setWidget(dl_inner)
        sidebar.addWidget(self._dl_scroll)
        list_tab_lay.addWidget(self._sidebar_container, 1)

        self._tabs.addTab(self._list_tab, "📋  Daftar Peluang")

        # ═══════════════════════════════════════════════
        #  Tab 1 — Dashboard
        # ═══════════════════════════════════════════════
        self.dashboard_tab = DashboardWidget()
        self._tabs.addTab(self.dashboard_tab, "📊  Dashboard Analisis")

        # Hubungkan perubahan tab → update dashboard jika data baru
        self._tabs.currentChanged.connect(self._on_tab_changed)

    def _style_scroll(self, scroll):
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {T['bg_base']}; width: 6px; border-radius: 3px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {T['bd_strong']}; border-radius: 3px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

    def _apply_base_style(self):
        self.setStyleSheet(f"QMainWindow {{ background: {T['bg_base']}; }}")

    def _connect(self):
        self.header.search_input.textChanged.connect(self._refresh)
        self.header.filter_changed.connect(self._refresh)
        self.header.combo_cat.currentTextChanged.connect(self._refresh)
        self.header.combo_level.currentTextChanged.connect(self._refresh)
        self.header.chk_active.stateChanged.connect(self._refresh)
        self.header.btn_semua.clicked.connect(self._refresh)
        self.header.btn_beasiswa.clicked.connect(self._refresh)
        self.header.btn_lomba.clicked.connect(self._refresh)
        self.header.theme_toggled.connect(self._switch_theme)
        # Tombol refresh / scrape
        self._btn_scrape.clicked.connect(self._start_scrape)

    def _switch_theme(self, dark: bool):
        global T
        T = DARK if dark else LIGHT
        self._apply_base_style()
        self.centralWidget().setStyleSheet(f"background: {T['bg_base']};")
        self._list_tab.setStyleSheet(f"background: {T['bg_base']};")
        self.header.full_restyle()
        self._style_scroll(self._main_scroll)
        self._style_scroll(self._dl_scroll)
        self._count_lbl.setStyleSheet(
            f"font-size: 17px; font-weight: 800; color: {T['tx_primary']}; letter-spacing: -0.3px;"
        )
        # Toolbar
        self._toolbar.setStyleSheet(f"background: {T['bg_surface']}; border: none;")
        self._status_lbl.setStyleSheet(
            f"font-size: 12px; color: {T['tx_muted']}; background: transparent;"
        )
        self._last_update_lbl.setStyleSheet(
            f"font-size: 11px; color: {T['tx_muted']}; background: transparent;"
        )
        self._btn_scrape.setStyleSheet(f"""
            QPushButton {{
                background: {T['ac_blue']};
                color: white;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 700;
                border: none;
                padding: 0 18px;
            }}
            QPushButton:hover {{ background: {T['ac_cyan']}; }}
            QPushButton:disabled {{
                background: {T['bd_base']}; color: {T['tx_muted']};
            }}
        """)
        # Tab widget
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {T['bg_base']};
            }}
            QTabBar::tab {{
                background: {T['bg_surface']};
                color: {T['tx_secondary']};
                border: none;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
                min-width: 130px;
                border-bottom: 3px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {T['ac_blue']};
                background: {T['bg_base']};
                border-bottom: 3px solid {T['ac_blue']};
                font-weight: 800;
            }}
            QTabBar::tab:hover:!selected {{
                background: {T['bg_card_hov']};
                color: {T['tx_primary']};
            }}
        """)
        # Dashboard theme refresh
        self.dashboard_tab.refresh_theme()
        self._refresh()

    def _refresh(self):
        # Normalisasi data sekali — idempotent karena pakai level_norm
        if DATA and "level_norm" not in DATA[0]:
            _build_dynamic_options(DATA)
            # Update combo jika filter aktif
            ftype = self.header._current_filter
            if ftype != "Semua":
                self.header.update_combos(ftype)

        q       = self.header.search_input.text()
        q_lower = q.lower()
        ftype   = self.header._current_filter
        fcat    = self.header.combo_cat.currentText()
        flvl    = self.header.combo_level.currentText()
        active  = self.header.chk_active.isChecked()

        # ── Search feedback ──
        if 0 < len(q) < 3:
            self.header.search_hint.setVisible(True)
            search_active = False
        else:
            self.header.search_hint.setVisible(False)
            search_active = len(q) >= 3

        filtered = []
        for item in DATA:
            if active and not item["active"]: continue
            if ftype != "Semua" and item["type"] != ftype: continue
            if fcat  != "Semua Kategori" and item.get("cat","") != fcat: continue
            if flvl != "Semua Jenjang":
                if flvl not in item.get("level_norm", [item.get("level","")]):
                    continue
            if search_active:
                desc = item.get("desc") or ""
                if (q_lower not in item["title"].lower() and
                        q_lower not in item.get("organizer","").lower() and
                        q_lower not in desc.lower()):
                    continue
            filtered.append(item)

        # Stats
        self.header.update_stats(
            len(DATA),
            sum(1 for i in DATA if i["type"]=="Beasiswa"),
            sum(1 for i in DATA if i["type"]=="Lomba"),
            sum(1 for i in DATA if i["active"])
        )
        self._count_lbl.setText(f"Menampilkan {len(filtered)} Peluang")

        # Clear & rebuild cards
        while self._cards_grid.count():
            w = self._cards_grid.takeAt(0).widget()
            if w:
                w.hide()
                w.deleteLater()

        sidebar_w = min(360, max(260, (self.width() - 36*2) // 5))
        cols = max(1, (self.width() - 36*2 - sidebar_w - 22 - 36) // 300)
        for idx, item in enumerate(filtered):
            card = ItemCard(item)
            card.detail_clicked.connect(self._show_detail)
            self._cards_grid.addWidget(card, idx // cols, idx % cols)
        for c in range(cols):
            self._cards_grid.setColumnStretch(c, 1)

        # Deadline sidebar
        while self._dl_lay.count():
            w = self._dl_lay.takeAt(0).widget()
            if w:
                w.hide()
                w.deleteLater()

        upcoming = sorted([i for i in DATA if i["active"] and 0 <= i["days"] <= 14], key=lambda x: x["days"])
        for item in upcoming:
            dl_widget = DeadlineItem(item)
            dl_widget.detail_clicked.connect(self._show_detail)
            self._dl_lay.addWidget(dl_widget)
        if not upcoming:
            e = QLabel("Tidak ada deadline\nmendekat saat ini")
            e.setAlignment(Qt.AlignCenter)
            e.setStyleSheet(f"color: {T['tx_muted']}; font-size: 13px; background: transparent; padding: 20px 0;")
            self._dl_lay.addWidget(e)

        # ── Sinkron dashboard jika sedang ditampilkan ──
        if self._tabs.currentIndex() == 1:
            self.dashboard_tab.update_charts(self.data)

    # ══════════════════════════════════════════════════════════
    #  RELOAD DATA — method pusat untuk refresh semua tampilan
    # ══════════════════════════════════════════════════════════
    def reload_data(self, data_baru: list = None):
        """
        Method pusat untuk memperbarui seluruh UI dengan data terbaru.

        Alur:
          1. Perbarui variabel global DATA dan self.data
          2. Reset normalisasi (hapus level_norm agar dibangun ulang)
          3. Rebuild card list dan sidebar
          4. Update dashboard grafik
          5. Tidak perlu restart aplikasi

        Contoh pemanggilan:
            # Setelah scraping selesai:
            self.reload_data(data_dari_database)

            # Atau dari fungsi lain:
            self.reload_data()   # pakai self.data yang sudah diperbarui
        """
        global DATA

        if data_baru is not None:
            DATA = data_baru
            self.data = data_baru

        # Reset normalisasi agar dibangun ulang dari data baru
        for item in DATA:
            item.pop("level_norm", None)

        # Rebuild filter options
        _build_dynamic_options(DATA)

        # Refresh list & sidebar
        self._refresh()

        # Update dashboard (selalu, bukan hanya saat tab aktif)
        self.dashboard_tab.update_charts(self.data)

    # ── Tab berubah → pastikan dashboard up-to-date ──────────
    def _on_tab_changed(self, index: int):
        if index == 1:
            self.dashboard_tab.update_charts(self.data)

    # ══════════════════════════════════════════════════════════
    #  SCRAPING — QThread workflow
    # ══════════════════════════════════════════════════════════
    def _start_scrape(self):
        """Mulai scraping di background thread."""
        if self._worker and self._worker.isRunning():
            return   # Jangan jalankan dua kali bersamaan

        self._btn_scrape.setEnabled(False)
        self._btn_scrape.setText("⏳  Scraping...")
        self._set_status("Memulai scraping...")

        self._worker = ScrapeWorker()
        self._worker.finished.connect(self.on_scrape_finished)
        self._worker.error.connect(self.on_scrape_error)
        self._worker.progress.connect(self._set_status)
        self._worker.start()

    def on_scrape_finished(self, data_baru: list):
        """
        Dipanggil otomatis setelah ScrapeWorker.finished emit.
        Memperbarui seluruh UI + dashboard tanpa restart aplikasi.
        """
        from datetime import datetime
        waktu = datetime.now().strftime("%H:%M:%S")

        self.reload_data(data_baru)

        self._btn_scrape.setEnabled(True)
        self._btn_scrape.setText("🔄  Refresh Data")
        self._set_status(f"✅  Data diperbarui — {len(data_baru)} item")
        self._last_update_lbl.setText(f"Terakhir update: {waktu}")

    def on_scrape_error(self, pesan: str):
        """Dipanggil jika scraping gagal."""
        self._btn_scrape.setEnabled(True)
        self._btn_scrape.setText("🔄  Refresh Data")
        self._set_status(pesan)

    def _set_status(self, teks: str):
        """Perbarui label status di toolbar."""
        self._status_lbl.setText(teks)

    def _show_detail(self, item):
        DetailDialog(item, self).exec_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start()


# ══════════════════════════════════════════════════════════════
#  ENTRY
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window,        QColor(LIGHT["bg_base"]))
    pal.setColor(QPalette.WindowText,    QColor(LIGHT["tx_primary"]))
    pal.setColor(QPalette.Base,          QColor(LIGHT["bg_surface"]))
    pal.setColor(QPalette.Text,          QColor(LIGHT["tx_primary"]))
    pal.setColor(QPalette.Button,        QColor(LIGHT["bg_card"]))
    pal.setColor(QPalette.ButtonText,    QColor(LIGHT["tx_primary"]))
    pal.setColor(QPalette.Highlight,     QColor(LIGHT["ac_blue"]))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(pal)

    app.setFont(QFont("Segoe UI", 11))

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())