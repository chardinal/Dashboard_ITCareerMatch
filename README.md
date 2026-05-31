# Recruitment Analytics Dashboard

Analisis komprehensif data rekrutmen IT di Indonesia menggunakan tiga dataset utama, divisualisasikan dalam dashboard interaktif berbasis Streamlit.

**Project:** Data Science Capstone — DBS Foundation 2026

---

## Daftar Isi

1. [Latar Belakang](#latar-belakang)
2. [Arsitektur Dashboard](#arsitektur-dashboard)
3. [Struktur File](#struktur-file)
4. [Dataset](#dataset)
5. [Business Questions](#business-questions)
6. [Cara Menjalankan](#cara-menjalankan)
7. [Dependensi](#dependensi)

---

## Latar Belakang

Dashboard ini menjawab pertanyaan-pertanyaan bisnis kritis dalam rekrutmen IT di Indonesia, dengan fokus pada:

- **Supply-side analysis** — Profil kandidat (Dataset_CV): pendidikan, pengalaman, dan skill.
- **Demand-side analysis** — Karakteristik lowongan (Dataset_Job & Glints_Job): persyaratan, lokasi, gaji, tipe kerja.
- **Gap analysis** — Membandingkan ekspektasi perusahaan dengan profil kandidat yang tersedia.

Insight yang dihasilkan membantu jobseeker, recruiter, dan pengambil keputusan memahami dinamika pasar tenaga kerja IT.

---

## Arsitektur Dashboard

```
STREAMLIT DASHBOARD (app.py)
├── Sidebar
│   ├── Filter Kota (Glints)
│   ├── Filter Kategori Peran (Glints)
│   └── Filter Sistem Kerja (Glints)
└── Main Content
    └── Tab BQ 1 ... BQ 10
        ├── Chart Plotly
        ├── Metric Cards
        └── Interpretasi & Implikasi

Data Flow:
data/
├── Dataset_CV.*          -> @st.cache_data -> load_cv()    -> fig_bq1(), fig_bq5(), fig_bq7()
├── Dataset_Job.*         -> @st.cache_data -> load_job()   -> fig_bq2(), fig_bq5(), fig_bq9()
└── Dataset_Glints_Job.*  -> @st.cache_data -> load_glints() -> fig_bq3(), fig_bq4(), fig_bq6(), fig_bq8(), fig_bq10()
```

**Prinsip Arsitektur:**
- **Separation of Concerns** — Logika data (`data_loader.py`) terpisah dari visualisasi (`visualizations.py`) dan UI (`app.py`).
- **Caching** — `@st.cache_data` digunakan pada semua pemuatan data agar dashboard responsif.
- **Modularitas** — Setiap Business Question diimplementasikan sebagai satu fungsi tersendiri.

---

## Struktur File

```
Dashboard_Streamlit/
├── README.md
├── requirements.txt
├── app.py                  # Entry point Streamlit Dashboard
├── data_loader.py          # Pemuatan & preprocessing dataset
├── visualizations.py       # Fungsi chart Plotly per Business Question
├── logo_capstone.png
└── data/
    ├── Dataset_CV.xlsx
    ├── Dataset_Job.xlsx
    └── Dataset_Glints_Job.xlsx
```

| File | Deskripsi |
|------|-----------|
| `app.py` | Streamlit app entry point. Mengatur layout (tabs + sidebar) dan memanggil fungsi dari modul lain. |
| `data_loader.py` | Memuat file dari folder `data/`, normalisasi kolom, dan transformasi dasar. |
| `visualizations.py` | Fungsi chart Plotly (satu fungsi per BQ) yang dipanggil oleh `app.py`. |
| `requirements.txt` | Daftar library dengan versi yang diperlukan. |

---

## Dataset

| Dataset | Deskripsi | Kolom Kunci |
|---------|-----------|-------------|
| **Dataset_CV** | Profil kandidat/pelamar | `pendidikan`, `pengalaman`, `skill` |
| **Dataset_Job** | Data lowongan kerja umum | `posisi`, `pengalaman`, `pendidikan`, `gender`, `usia` |
| **Dataset_Glints_Job** | Lowongan dari platform Glints | `kategori_peran`, `lokasi`, `sistem_kerja`, `tipe_waktu_kerja`, `gaji`, `skill` |

> Sesuaikan konstanta nama kolom di bagian atas `data_loader.py` jika nama kolom aktual berbeda.

---

## Business Questions

| BQ | Pertanyaan | Dataset | Chart |
|----|-----------|---------|-------|
| BQ 1 | Distribusi tingkat pendidikan kandidat — apakah S1 > 50%? | Dataset_CV | Pie + Bar Chart |
| BQ 2 | Proporsi lowongan entry / mid / senior — apakah entry > 40%? | Dataset_Job | Donut Chart |
| BQ 3 | Top 5 kota dengan lowongan terbanyak & komposisi WFO/WFH/Hybrid | Glints_Job | Stacked Bar Chart |
| BQ 4 | Top 10 & Bottom 10 kategori peran berdasarkan median gaji | Glints_Job | Bar Chart + Box Plot |
| BQ 5 | Gap distribusi pendidikan kandidat vs. syarat lowongan (> 15 poin) | CV + Job | Grouped Bar Chart |
| BQ 6 | Top 15 skill paling sering — ada yang muncul di > 30% lowongan? | Glints_Job | Horizontal Bar Chart |
| BQ 7 | Rata-rata jumlah skill per bucket pengalaman — senior >= 2x entry? | Dataset_CV | Bar + Line Chart |
| BQ 8 | Dominasi Penuh Waktu > 70% di setiap kategori peran? | Glints_Job | 100% Stacked Bar |
| BQ 9 | Lowongan dengan batasan gender/usia — apakah > 20% dari total? | Dataset_Job | Pie + Bar Chart |
| BQ 10 | Perbandingan median gaji WFO vs. WFH vs. Hybrid per 10 kategori | Glints_Job | Grouped Bar + Heatmap |

---

## Cara Menjalankan

### 1. Siapkan Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Jalankan Dashboard

```bash
streamlit run app.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`.

---

## Dependensi

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.18.0
openpyxl>=3.1.0
```

---

*Stack: Python 3.10+, Pandas, Plotly, Streamlit*
