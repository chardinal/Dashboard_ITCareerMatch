"""
data_loader.py
==============
Modul pemuatan dan preprocessing data untuk Recruitment Analytics Dashboard.

CATATAN NAMA KOLOM:
    Ubah konstanta di bawah ini sesuai nama kolom AKTUAL di file CSV/Excel Anda.
    Semua nama kolom yang digunakan di seluruh proyek mengacu ke konstanta ini.

Penulis: Data Science Capstone — DBS Foundation 2026
"""

import pandas as pd
import numpy as np
import os
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PATH KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ─────────────────────────────────────────────────────────────────────────────
# NAMA KOLOM — SESUAIKAN JIKA BERBEDA DENGAN DATA AKTUAL
# ─────────────────────────────────────────────────────────────────────────────

# === Dataset_CV ===
# File: Dataset_CV.xlsx
CV_EDUCATION_COL    = "pendidikan"      # Tingkat pendidikan (Sarjana (S1), Magister (S2), dst)
CV_EXPERIENCE_COL   = "pengalaman"      # Kolom pengalaman (string, akan di-parse)
CV_SKILL_COL        = "skill"           # Kolom skill, dipisahkan koma
CV_DETAIL_COL       = "detail"          # Kolom detail/deskripsi kandidat

# === Dataset_Job ===
# File: Dataset_Job.xlsx
JOB_POSITION_COL    = "posisi"          # Nama posisi/jabatan
JOB_EXP_COL         = "pengalaman"      # Kolom pengalaman (string, akan di-parse)
JOB_MIN_EXP_COL     = "pengalaman"      # Alias untuk kompatibilitas
JOB_EDU_COL         = "pendidikan"      # Syarat pendidikan minimum
JOB_GENDER_COL      = "gender"          # Syarat gender: 'tanpa ketentuan' / 'Laki-laki saja' / 'Perempuan saja'
JOB_AGE_COL         = "usia"            # Kolom usia (string, bisa NaN)
JOB_SKILL_COL       = "skill"           # Kolom skill lowongan

# === Glints_Job ===
# File: Dataset_Glints_Job.xlsx
GLINTS_ROLE_COL      = "kategori_peran"    # Kategori/peran pekerjaan
GLINTS_CITY_COL      = "lokasi"            # Kota lowongan (format: 'Kota, Provinsi')
GLINTS_WORK_SYS_COL  = "sistem_kerja"      # 'Kerja di kantor' / 'Remote/Dari rumah' / 'Hybrid'
GLINTS_WORK_TIME_COL = "tipe_waktu_kerja"  # 'Penuh Waktu' / 'Magang' / 'Freelance' / 'Kontrak' / 'Paruh Waktu'
GLINTS_SALARY_COL    = "gaji"             # Gaji string: 'RpXX.XXX.XXX - YY.YYY.YYY/Bulan'
GLINTS_SALARY_MIN    = "gaji_min"          # Kolom gaji min hasil parse (angka)
GLINTS_SALARY_MAX    = "gaji_max"          # Kolom gaji max hasil parse (angka)
GLINTS_SKILL_COL     = "skill"            # Kolom skill, dipisahkan koma

# Label ringkas sistem kerja (untuk display di chart)
WORK_SYS_LABELS = {
    "Kerja di kantor"  : "WFO",
    "Remote/Dari rumah": "WFH",
    "Hybrid"           : "Hybrid",
}

# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI PEMBANTU INTERNAL
# ─────────────────────────────────────────────────────────────────────────────

def _find_file(folder: str, base_name: str) -> str:
    """
    Mencari file di folder dengan nama dasar tertentu,
    mendukung ekstensi .csv, .xlsx, .xls secara otomatis.
    """
    for ext in [".csv", ".xlsx", ".xls"]:
        path = os.path.join(folder, base_name + ext)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"File '{base_name}' tidak ditemukan di '{folder}' "
        f"(dicoba ekstensi: .csv, .xlsx, .xls)"
    )


def _read_file(path: str) -> pd.DataFrame:
    """Membaca CSV atau Excel secara otomatis berdasarkan ekstensi."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(path, engine="openpyxl")
    else:
        raise ValueError(f"Format file tidak didukung: {ext}")


def _parse_experience(series: pd.Series) -> pd.Series:
    """
    Parse kolom pengalaman dari format string ke angka tahun (float).

    Format yang ditangani (dari data aktual):
      '< 1 tahun'         → 0
      '1 tahun'           → 1
      '1-2 tahun'         → 1   (ambil batas bawah)
      '5-10 tahun'        → 5
      '10+ tahun'         → 10
      '5+ tahun'          → 5
      '0 tahun (magang)'  → 0
      'tidak ada'         → NaN
      NaN                 → NaN
    """
    import re

    def _to_num(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().lower()
        if s in ("tidak ada", "", "nan", "tidak ada pengalaman"):
            return np.nan
        # '< 1 tahun' atau '<1 tahun'
        if re.match(r"^<\s*\d", s):
            return 0.0
        # '10+ tahun' atau '5+ tahun'
        m = re.match(r"^(\d+)\+", s)
        if m:
            return float(m.group(1))
        # '1-2 tahun', '3-5 tahun', '5-10 tahun'
        m = re.match(r"^(\d+)\s*[-–]\s*(\d+)", s)
        if m:
            return float(m.group(1))   # ambil batas bawah
        # '1 tahun', '2 tahun', '0 tahun (magang)'
        m = re.match(r"^(\d+)", s)
        if m:
            return float(m.group(1))
        return np.nan

    return series.apply(_to_num)


def _count_skills(series: pd.Series) -> pd.Series:
    """
    Menghitung jumlah skill dari sebuah Series berisi string yang dipisahkan koma.
    NaN dihitung sebagai 0.
    """
    return series.fillna("").apply(
        lambda x: len([s for s in str(x).split(",") if s.strip()])
    )


# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI PEMUATAN DATA (di-cache oleh Streamlit)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Memuat Dataset_CV…")
def load_cv() -> pd.DataFrame:
    """
    Memuat dan memproses Dataset_CV.

    Transformasi:
    - Kolom pengalaman dikonversi ke numerik.
    - Kolom skill di-strip whitespace.
    - Kolom pendidikan di-title-case untuk konsistensi.
    - Menambah kolom 'experience_bucket' untuk BQ 7.
    - Menambah kolom 'skill_count' untuk BQ 7.
    """
    path = _find_file(DATA_DIR, "Dataset_CV")  # → Dataset_CV.xlsx
    df = _read_file(path)

    # Normalisasi pendidikan
    if CV_EDUCATION_COL in df.columns:
        df[CV_EDUCATION_COL] = df[CV_EDUCATION_COL].astype(str).str.strip()

    # Parse pengalaman → angka tahun
    # Format string di data: '2 tahun', '3-5 tahun', 'fresh graduate', dst.
    if CV_EXPERIENCE_COL in df.columns:
        df["pengalaman_tahun"] = _parse_experience(df[CV_EXPERIENCE_COL])
        df["experience_bucket"] = pd.cut(
            df["pengalaman_tahun"],
            bins=[-1, 1, 2, 5, 100],
            labels=["Entry (0–1 th)", "Junior (1–2 th)", "Mid (2–5 th)", "Senior (5+ th)"]
        )

    # Hitung jumlah skill
    if CV_SKILL_COL in df.columns:
        df["skill_count"] = _count_skills(df[CV_SKILL_COL])

    return df


@st.cache_data(show_spinner="Memuat Dataset_Job…")
def load_job() -> pd.DataFrame:
    """
    Memuat dan memproses Dataset_Job.

    Transformasi:
    - Min pengalaman dikonversi ke numerik.
    - Menambah kolom 'experience_level' (Entry/Mid/Senior).
    - Menambah kolom 'has_restriction' untuk BQ 9 (True jika ada batasan gender/usia).
    """
    path = _find_file(DATA_DIR, "Dataset_Job")  # → Dataset_Job.xlsx
    df = _read_file(path)

    # Normalisasi pendidikan
    if JOB_EDU_COL in df.columns:
        df[JOB_EDU_COL] = df[JOB_EDU_COL].astype(str).str.strip()

    # Parse pengalaman → angka tahun → level
    if JOB_EXP_COL in df.columns:
        df["pengalaman_tahun"] = _parse_experience(df[JOB_EXP_COL])
        df["experience_level"] = pd.cut(
            df["pengalaman_tahun"],
            bins=[-1, 2, 5, 100],
            labels=["Entry-Level (0–2 th)", "Mid-Level (2–5 th)", "Senior (5+ th)"]
        )

    # BQ 9: flag lowongan dengan batasan gender atau usia
    # Nilai gender: 'tanpa ketentuan' | 'Laki-laki saja' | 'Perempuan saja'
    # Nilai usia : 'tanpa batasan usia' | '20-35 tahun' | dst.
    has_gender = pd.Series(False, index=df.index)
    if JOB_GENDER_COL in df.columns:
        has_gender = (
            df[JOB_GENDER_COL].notna() &
            ~df[JOB_GENDER_COL].astype(str).str.lower().isin(["tanpa ketentuan", "nan", ""])
        )

    has_age = pd.Series(False, index=df.index)
    if JOB_AGE_COL in df.columns:
        has_age = (
            df[JOB_AGE_COL].notna() &
            ~df[JOB_AGE_COL].astype(str).str.lower().isin(["tanpa batasan usia", "nan", "", "tidak ada"])
        )

    df["has_restriction"] = has_gender | has_age

    return df


@st.cache_data(show_spinner="Memuat Glints_Job…")
def load_glints() -> pd.DataFrame:
    """
    Memuat dan memproses Glints_Job.

    Transformasi:
    - Kolom gaji min/max dikonversi ke numerik (hilangkan 'Rp', koma, dll.).
    - Menambah kolom 'salary_median' = rata-rata gaji_min dan gaji_max.
    - Normalisasi sistem_kerja dan tipe_waktu ke title-case.
    """
    path = _find_file(DATA_DIR, "Dataset_Glints_Job")  # → Dataset_Glints_Job.xlsx
    df = _read_file(path)

    # Normalisasi kolom teks
    for col in [GLINTS_ROLE_COL, GLINTS_CITY_COL, GLINTS_WORK_SYS_COL, GLINTS_WORK_TIME_COL]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Sederhanakan label kota → ambil bagian sebelum koma pertama
    # Contoh: 'Jakarta Selatan, DKI Jakarta' → 'Jakarta Selatan'
    if GLINTS_CITY_COL in df.columns:
        df["kota_singkat"] = df[GLINTS_CITY_COL].str.split(",").str[0].str.strip()

    # Buat label WFO/WFH/Hybrid yang ringkas untuk chart
    if GLINTS_WORK_SYS_COL in df.columns:
        df["sistem_kerja_label"] = df[GLINTS_WORK_SYS_COL].map(WORK_SYS_LABELS).fillna(df[GLINTS_WORK_SYS_COL])

    # Parse kolom gaji dari string → dua kolom numerik (gaji_min & gaji_max)
    # Format: 'Rp20.000.000 - 25.000.000/Bulan'
    if GLINTS_SALARY_COL in df.columns:
        salary_str = df[GLINTS_SALARY_COL].astype(str)
        # Hapus prefix 'Rp', suffix '/Bulan' (case insensitive), lalu hapus titik RIBUAN
        salary_clean = (
            salary_str
            .str.replace(r"Rp", "", regex=False)
            .str.replace(r"/[Bb]ulan", "", regex=True)
            .str.replace(r"\.", "", regex=True)   # hapus titik ribuan: 20.000.000 → 20000000
            .str.strip()
        )
        # Split berdasarkan ' - '
        split_salary = salary_clean.str.split(r"\s*-\s*", expand=True, regex=True)
        df[GLINTS_SALARY_MIN] = pd.to_numeric(
            split_salary[0].str.strip().replace({"nan": np.nan, "": np.nan}),
            errors="coerce"
        )
        df[GLINTS_SALARY_MAX] = pd.to_numeric(
            split_salary[1].str.strip().replace({"nan": np.nan, "": np.nan}),
            errors="coerce"
        ) if split_salary.shape[1] > 1 else np.nan

    # Kolom median gaji (digunakan di BQ 4 & BQ 10)
    if GLINTS_SALARY_MIN in df.columns and GLINTS_SALARY_MAX in df.columns:
        df["salary_median"] = df[[GLINTS_SALARY_MIN, GLINTS_SALARY_MAX]].mean(axis=1)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI BANTU EKSPLORASI (dipakai di EDA.ipynb)
# ─────────────────────────────────────────────────────────────────────────────

def split_skills(series: pd.Series) -> pd.Series:
    """
    Meledakkan kolom skill (dipisah koma) menjadi satu skill per baris.
    Berguna untuk menghitung frekuensi skill.

    Returns:
        pd.Series berisi satu skill per baris (sudah di-strip dan di-lower-case).
    """
    exploded = (
        series.dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .str.lower()
    )
    return exploded[exploded != ""]


def top_n_cities(df: pd.DataFrame, city_col: str, n: int = 5) -> list:
    """Mengembalikan daftar N kota dengan jumlah lowongan terbanyak."""
    return df[city_col].value_counts().head(n).index.tolist()
