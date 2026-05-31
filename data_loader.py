"""
data_loader.py
==============
Modul pemuatan dan preprocessing data untuk Recruitment Analytics Dashboard.

Ubah konstanta nama kolom di bawah ini sesuai nama kolom aktual di file dataset.
Semua nama kolom yang digunakan di seluruh proyek mengacu ke konstanta ini.

Penulis: Data Science Capstone — DBS Foundation 2026
"""

import pandas as pd
import numpy as np
import os
import streamlit as st

# Path konfigurasi
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── Nama Kolom Dataset_CV ─────────────────────────────────────────────────────
CV_EDUCATION_COL    = "pendidikan"
CV_EXPERIENCE_COL   = "pengalaman"
CV_SKILL_COL        = "skill"
CV_DETAIL_COL       = "detail"

# ── Nama Kolom Dataset_Job ────────────────────────────────────────────────────
JOB_POSITION_COL    = "posisi"
JOB_EXP_COL         = "pengalaman"
JOB_MIN_EXP_COL     = "pengalaman"
JOB_EDU_COL         = "pendidikan"
JOB_GENDER_COL      = "gender"
JOB_AGE_COL         = "usia"
JOB_SKILL_COL       = "skill"

# ── Nama Kolom Glints_Job ─────────────────────────────────────────────────────
GLINTS_ROLE_COL      = "kategori_peran"
GLINTS_CITY_COL      = "lokasi"
GLINTS_WORK_SYS_COL  = "sistem_kerja"
GLINTS_WORK_TIME_COL = "tipe_waktu_kerja"
GLINTS_SALARY_COL    = "gaji"
GLINTS_SALARY_MIN    = "gaji_min"
GLINTS_SALARY_MAX    = "gaji_max"
GLINTS_SKILL_COL     = "skill"

# Label ringkas sistem kerja untuk display di chart
WORK_SYS_LABELS = {
    "Kerja di kantor"  : "WFO",
    "Remote/Dari rumah": "WFH",
    "Hybrid"           : "Hybrid",
}


def _find_file(folder: str, base_name: str) -> str:
    """Mencari file di folder dengan ekstensi .csv, .xlsx, atau .xls."""
    for ext in [".csv", ".xlsx", ".xls"]:
        path = os.path.join(folder, base_name + ext)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"File '{base_name}' tidak ditemukan di '{folder}' "
        f"(dicoba ekstensi: .csv, .xlsx, .xls)"
    )


def _read_file(path: str) -> pd.DataFrame:
    """Membaca CSV atau Excel berdasarkan ekstensi file."""
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

    Format yang ditangani:
      '< 1 tahun'         -> 0
      '1 tahun'           -> 1
      '1-2 tahun'         -> 1   (ambil batas bawah)
      '5-10 tahun'        -> 5
      '10+ tahun'         -> 10
      '0 tahun (magang)'  -> 0
      'tidak ada'         -> NaN
    """
    import re

    def _to_num(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().lower()
        if s in ("tidak ada", "", "nan", "tidak ada pengalaman"):
            return np.nan
        if re.match(r"^<\s*\d", s):
            return 0.0
        m = re.match(r"^(\d+)\+", s)
        if m:
            return float(m.group(1))
        m = re.match(r"^(\d+)\s*[-–]\s*(\d+)", s)
        if m:
            return float(m.group(1))
        m = re.match(r"^(\d+)", s)
        if m:
            return float(m.group(1))
        return np.nan

    return series.apply(_to_num)


def _count_skills(series: pd.Series) -> pd.Series:
    """Menghitung jumlah skill dari Series berisi string yang dipisahkan koma."""
    return series.fillna("").apply(
        lambda x: len([s for s in str(x).split(",") if s.strip()])
    )


@st.cache_data(show_spinner="Memuat Dataset_CV...")
def load_cv() -> pd.DataFrame:
    """
    Memuat dan memproses Dataset_CV.

    Transformasi:
    - Kolom pengalaman dikonversi ke numerik.
    - Kolom skill di-strip whitespace.
    - Menambah kolom 'experience_bucket' dan 'skill_count'.
    """
    path = _find_file(DATA_DIR, "Dataset_CV")
    df = _read_file(path)

    if CV_EDUCATION_COL in df.columns:
        df[CV_EDUCATION_COL] = df[CV_EDUCATION_COL].astype(str).str.strip()

    if CV_EXPERIENCE_COL in df.columns:
        df["pengalaman_tahun"] = _parse_experience(df[CV_EXPERIENCE_COL])
        df["experience_bucket"] = pd.cut(
            df["pengalaman_tahun"],
            bins=[-1, 1, 2, 5, 100],
            labels=["Entry (0-1 th)", "Junior (1-2 th)", "Mid (2-5 th)", "Senior (5+ th)"]
        )

    if CV_SKILL_COL in df.columns:
        df["skill_count"] = _count_skills(df[CV_SKILL_COL])

    return df


@st.cache_data(show_spinner="Memuat Dataset_Job...")
def load_job() -> pd.DataFrame:
    """
    Memuat dan memproses Dataset_Job.

    Transformasi:
    - Min pengalaman dikonversi ke numerik.
    - Menambah kolom 'experience_level' (Entry/Mid/Senior).
    - Menambah kolom 'has_restriction' (True jika ada batasan gender/usia).
    """
    path = _find_file(DATA_DIR, "Dataset_Job")
    df = _read_file(path)

    if JOB_EDU_COL in df.columns:
        df[JOB_EDU_COL] = df[JOB_EDU_COL].astype(str).str.strip()

    if JOB_EXP_COL in df.columns:
        df["pengalaman_tahun"] = _parse_experience(df[JOB_EXP_COL])
        df["experience_level"] = pd.cut(
            df["pengalaman_tahun"],
            bins=[-1, 2, 5, 100],
            labels=["Entry-Level (0-2 th)", "Mid-Level (2-5 th)", "Senior (5+ th)"]
        )

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


@st.cache_data(show_spinner="Memuat Glints_Job...")
def load_glints() -> pd.DataFrame:
    """
    Memuat dan memproses Dataset_Glints_Job.

    Transformasi:
    - Kolom gaji min/max dikonversi ke numerik.
    - Menambah kolom 'salary_median'.
    - Normalisasi sistem_kerja ke label WFO/WFH/Hybrid.
    - Menambah kolom 'kota_singkat' dari kolom lokasi.
    """
    path = _find_file(DATA_DIR, "Dataset_Glints_Job")
    df = _read_file(path)

    for col in [GLINTS_ROLE_COL, GLINTS_CITY_COL, GLINTS_WORK_SYS_COL, GLINTS_WORK_TIME_COL]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if GLINTS_CITY_COL in df.columns:
        df["kota_singkat"] = df[GLINTS_CITY_COL].str.split(",").str[0].str.strip()

    if GLINTS_WORK_SYS_COL in df.columns:
        df["sistem_kerja_label"] = df[GLINTS_WORK_SYS_COL].map(WORK_SYS_LABELS).fillna(df[GLINTS_WORK_SYS_COL])

    if GLINTS_SALARY_COL in df.columns:
        salary_str = df[GLINTS_SALARY_COL].astype(str)
        salary_clean = (
            salary_str
            .str.replace(r"Rp", "", regex=False)
            .str.replace(r"/[Bb]ulan", "", regex=True)
            .str.replace(r"\.", "", regex=True)
            .str.strip()
        )
        split_salary = salary_clean.str.split(r"\s*-\s*", expand=True, regex=True)
        df[GLINTS_SALARY_MIN] = pd.to_numeric(
            split_salary[0].str.strip().replace({"nan": np.nan, "": np.nan}),
            errors="coerce"
        )
        df[GLINTS_SALARY_MAX] = pd.to_numeric(
            split_salary[1].str.strip().replace({"nan": np.nan, "": np.nan}),
            errors="coerce"
        ) if split_salary.shape[1] > 1 else np.nan

    if GLINTS_SALARY_MIN in df.columns and GLINTS_SALARY_MAX in df.columns:
        df["salary_median"] = df[[GLINTS_SALARY_MIN, GLINTS_SALARY_MAX]].mean(axis=1)

    return df


def split_skills(series: pd.Series) -> pd.Series:
    """
    Meledakkan kolom skill (dipisah koma) menjadi satu skill per baris.
    Returns: pd.Series berisi satu skill per baris (sudah di-strip dan lowercase).
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
