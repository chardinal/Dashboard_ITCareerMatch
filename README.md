# 📊 Recruitment Analytics Dashboard — Data Science Capstone

> **Senior Data Scientist & Python/Streamlit Developer Project**  
> Analisis komprehensif data rekrutmen menggunakan tiga dataset utama dan divisualisasikan dalam dashboard interaktif berbasis Streamlit.

---

## 📋 Daftar Isi
1. [Konsep & Latar Belakang](#konsep--latar-belakang)
2. [Arsitektur Dashboard](#arsitektur-dashboard)
3. [Struktur File Proyek](#struktur-file-proyek)
4. [Dataset yang Digunakan](#dataset-yang-digunakan)
5. [10 Business Questions & Pemetaan Visualisasi](#10-business-questions--pemetaan-visualisasi)
6. [Cara Menjalankan](#cara-menjalankan)
7. [Dependensi](#dependensi)

---

## 💡 Konsep & Latar Belakang

Dashboard ini dirancang untuk menjawab pertanyaan-pertanyaan bisnis kritis dalam dunia rekrutmen IT di Indonesia, dengan fokus pada:

- **Supply-side analysis** → Profil kandidat (Dataset_CV): pendidikan, pengalaman, dan skill.
- **Demand-side analysis** → Karakteristik lowongan kerja (Dataset_Job & Glints_Job): persyaratan, lokasi, gaji, dan tipe kerja.
- **Gap analysis** → Membandingkan ekspektasi perusahaan dengan profil kandidat yang tersedia.

Insight yang dihasilkan bertujuan membantu **jobseeker**, **recruiter**, dan **pengambil keputusan** memahami dinamika pasar tenaga kerja IT.

---

## 🏗️ Arsitektur Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD (app.py)                  │
│                                                                   │
│  ┌─────────────┐  ┌───────────────────────────────────────────┐  │
│  │   SIDEBAR   │  │              MAIN CONTENT AREA             │  │
│  │             │  │                                            │  │
│  │ • Filter    │  │  [Tab 1]  [Tab 2]  [Tab 3]  [Tab 4]  ... │  │
│  │   Dataset   │  │                                            │  │
│  │ • Filter    │  │  ┌──────────────────────────────────────┐  │  │
│  │   Kota      │  │  │  Chart / Visualization (Plotly)      │  │  │
│  │ • Filter    │  │  │  ─────────────────────────────────   │  │  │
│  │   Peran     │  │  │  st.metric | st.info (Konklusi BQ)  │  │  │
│  │ • Filter    │  │  └──────────────────────────────────────┘  │  │
│  │   Tipe Kerja│  │                                            │  │
│  └─────────────┘  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Data Flow:
D:\DBS_Foundation-2026\data_clean_DS\
    ├── Dataset_CV.*   ──→  @st.cache_data  ──→  EDA Logic  ──→  Chart
    ├── Dataset_Job.*  ──→  @st.cache_data  ──→  EDA Logic  ──→  Chart
    └── Glints_Job.*   ──→  @st.cache_data  ──→  EDA Logic  ──→  Chart
```

**Prinsip Arsitektur:**
- **Separation of Concerns**: Logika data (`data_loader.py`) terpisah dari logika visualisasi (`visualizations.py`) dan UI (`app.py`).
- **Caching**: `@st.cache_data` digunakan untuk semua pemuatan data agar dashboard responsif.
- **Modularitas**: Setiap Business Question menjadi satu fungsi tersendiri.
- **Single-source-of-truth**: Transformasi data hanya dilakukan sekali dan digunakan bersama oleh notebook EDA dan dashboard.

---

## 📁 Struktur File Proyek

```
Dashboard_DS_Capstone/
│
├── README.md                   # Dokumentasi proyek (file ini)
├── requirements.txt            # Daftar dependensi Python
│
├── notebooks/
│   └── EDA.ipynb               # Jupyter Notebook: Exploratory Data Analysis
│                               # Berisi analisis per BQ dengan Markdown & kode
│
├── app.py                      # Entry point Streamlit Dashboard
├── data_loader.py              # Modul: memuat & membersihkan dataset (cache)
├── visualizations.py           # Modul: semua fungsi pembuatan chart Plotly
│
└── assets/
    └── style.css               # (Opsional) Custom CSS untuk styling Streamlit
```

### Penjelasan File Utama

| File | Tipe | Deskripsi |
|------|------|-----------|
| `EDA.ipynb` | Jupyter Notebook | Analisis eksplorasi data end-to-end. Setiap sel markdown menjawab BQ secara eksplisit dengan angka dan persentase. |
| `app.py` | Python Script | Streamlit app entry point. Mengatur layout (tabs + sidebar) dan memanggil fungsi dari modul lain. |
| `data_loader.py` | Python Module | Memuat CSV/Excel dari folder `data_clean_DS`, normalisasi kolom, dan transformasi dasar. |
| `visualizations.py` | Python Module | Fungsi-fungsi chart Plotly (satu fungsi per BQ) yang dipanggil oleh `app.py` maupun `EDA.ipynb`. |
| `requirements.txt` | Config | Pin versi semua library agar lingkungan bisa direproduksi. |

---

## 🗄️ Dataset yang Digunakan

| Dataset | Deskripsi | Kolom Kunci (Asumsi) |
|---------|-----------|----------------------|
| **Dataset_CV** | Data profil kandidat/pelamar | `pendidikan`, `pengalaman_tahun`, `skill`, `kota_asal` |
| **Dataset_Job** | Data lowongan kerja umum | `posisi`, `min_pengalaman`, `max_pengalaman`, `pendidikan_min`, `gender`, `usia_min`, `usia_max` |
| **Glints_Job** | Data lowongan dari platform Glints | `kategori_peran`, `kota`, `sistem_kerja`, `tipe_waktu`, `gaji_min`, `gaji_max`, `skill` |

> ⚠️ **Catatan Nama Kolom**: Nama kolom di atas adalah **asumsi**. Sesuaikan konstanta nama kolom di bagian atas `data_loader.py` jika nama kolom aktual berbeda.

---

## 📊 10 Business Questions & Pemetaan Visualisasi

### BQ 1 — Distribusi Tingkat Pendidikan Kandidat (Dataset_CV)
> *"Bagaimana distribusi tingkat pendidikan kandidat, dan apakah S1 mendominasi lebih dari 50%?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Pie Chart + Bar Chart (side-by-side)** |
| **Library** | Plotly Express (`px.pie` + `px.bar`) |
| **Mengapa** | Pie chart menunjukkan proporsi keseluruhan secara intuitif; bar chart memudahkan perbandingan nilai absolut antar level pendidikan. |
| **Konklusi** | `st.metric` menampilkan persentase S1; `st.info` memberi jawaban ya/tidak berdasarkan threshold 50%. |

---

### BQ 2 — Distribusi Level Pengalaman Lowongan (Dataset_Job)
> *"Berapa persen lowongan entry-level vs. mid-level vs. senior?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Donut Chart (Pie dengan hole) + Stacked Bar Chart** |
| **Library** | Plotly Graph Objects (`go.Pie` dengan `hole=0.4`) |
| **Mengapa** | Donut chart memperlihatkan proporsi tiga segmen secara bersih; bar chart opsional untuk nilai absolut. |
| **Konklusi** | `st.metric` menampilkan % entry-level; `st.success/st.warning` untuk jawaban threshold 40%. |

---

### BQ 3 — Top 5 Kota & Komposisi Sistem Kerja (Glints_Job)
> *"Kota mana top 5 terbanyak dan bagaimana komposisi WFO/WFH/Hybrid di tiap kota?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Grouped/Stacked Bar Chart (horizontal)** |
| **Library** | Plotly Express (`px.bar` dengan `barmode='stack'`, `orientation='h'`) |
| **Mengapa** | Stacked bar horizontal ideal untuk membandingkan komposisi multi-kategori (WFO/WFH/Hybrid) di beberapa kota sekaligus. |
| **Konklusi** | `st.info` menampilkan kota #1 dan sistem kerja dominan di masing-masing kota. |

---

### BQ 4 — Median Gaji per Kategori Peran (Glints_Job)
> *"10 peran dengan median gaji tertinggi dan terendah?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Horizontal Bar Chart (dua panel: Top 10 & Bottom 10) + Box Plot** |
| **Library** | Plotly Express (`px.bar` horizontal, `px.box`) |
| **Mengapa** | Bar chart median memudahkan perbandingan langsung; box plot menambah informasi rentang (IQR, outlier) untuk menjawab "seberapa lebar rentangnya". |
| **Konklusi** | `st.metric` untuk median gaji tertinggi dan terendah; `st.info` untuk lebar rentang. |

---

### BQ 5 — Perbandingan Distribusi Pendidikan Kandidat vs. Lowongan
> *"Selisih persentase per level pendidikan antara Dataset_CV dan Dataset_Job?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Grouped Bar Chart (side-by-side) + Diverging Bar Chart** |
| **Library** | Plotly Express (`px.bar` dengan `barmode='group'`) |
| **Mengapa** | Grouped bar chart memperlihatkan perbandingan langsung per level; diverging bar chart atau highlight warna merah untuk level dengan selisih >15 poin. |
| **Konklusi** | `st.warning` menampilkan level dengan gap terbesar beserta nilai selisihnya. |

---

### BQ 6 — Top 15 Skill Paling Sering Muncul (Glints_Job)
> *"Skill apa yang muncul di >30% total lowongan (skill dominan)?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Horizontal Bar Chart (sorted descending) + Annotation garis 30%** |
| **Library** | Plotly Express (`px.bar`, `add_vline`) |
| **Mengapa** | Bar chart horizontal paling mudah dibaca untuk daftar skill panjang; garis vertikal 30% sebagai threshold visual menjadi pembeda yang kuat. |
| **Konklusi** | `st.metric` untuk skill #1 dan persentasenya; `st.success/st.warning` untuk jawaban threshold dominan. |

---

### BQ 7 — Rata-rata Skill per Bucket Pengalaman (Dataset_CV)
> *"Apakah senior (5+ tahun) punya skill ≥2x lebih banyak dari entry-level (0–1 tahun)?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Bar Chart (vertikal) dengan error bars + Line Chart overlay** |
| **Library** | Plotly Graph Objects (`go.Bar` + `go.Scatter` untuk line) |
| **Mengapa** | Bar chart menunjukkan rata-rata per bucket; line overlay memudahkan melihat tren peningkatan skill seiring pengalaman. Error bars opsional jika tersedia std dev. |
| **Konklusi** | `st.metric` untuk rasio senior/entry-level; `st.success/st.error` untuk jawaban threshold 2x. |

---

### BQ 8 — Dominasi Tipe Waktu Kerja per Kategori Peran (Glints_Job)
> *"Apakah Penuh Waktu >70% di setiap kategori, atau ada yang didominasi Magang/Freelance/Kontrak?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **100% Stacked Bar Chart (horizontal)** |
| **Library** | Plotly Express (`px.bar`, `barmode='relative'`) dengan normalisasi ke 100% |
| **Mengapa** | 100% stacked bar paling efektif untuk melihat proporsi tipe waktu kerja di setiap kategori; kategori yang tidak memenuhi 70% langsung terlihat. |
| **Konklusi** | `st.info` menampilkan jumlah kategori yang memenuhi threshold dan nama kategori outlier. |

---

### BQ 9 — Lowongan dengan Persyaratan Gender/Usia (Dataset_Job)
> *"Berapa persen lowongan yang membatasi gender/usia, dan posisi mana yang paling sering?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Pie Chart (ada/tidak batasan) + Horizontal Bar Chart (top posisi pembatas)** |
| **Library** | Plotly Express (`px.pie`, `px.bar`) |
| **Mengapa** | Pie chart menjawab pertanyaan proporsi secara cepat; bar chart mengidentifikasi posisi spesifik yang paling sering membatasi. |
| **Konklusi** | `st.metric` untuk total % lowongan dengan batasan; `st.error/st.success` untuk threshold 20%. |

---

### BQ 10 — Perbandingan Median Gaji WFO/WFH/Hybrid per Kategori (Glints_Job)
> *"Bagaimana perbandingan median gaji antara WFO, WFH, dan Hybrid untuk 10 kategori terbanyak?"*

| Aspek | Detail |
|-------|--------|
| **Jenis Chart** | **Grouped Bar Chart (horizontal) + Heatmap opsional** |
| **Library** | Plotly Express (`px.bar` grouped, `px.imshow` untuk heatmap) |
| **Mengapa** | Grouped bar chart memungkinkan perbandingan langsung tiga sistem kerja per kategori; heatmap memberikan overview cepat pola gaji secara keseluruhan. |
| **Konklusi** | `st.info` menampilkan sistem kerja dengan median gaji tertinggi per kategori. |

---

## 🚀 Cara Menjalankan

### 1. Siapkan Environment
```bash
# Buat virtual environment
python -m venv venv

# Aktivasi (Windows)
venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt
```

### 2. Jalankan EDA Notebook
```bash
jupyter notebook notebooks/EDA.ipynb
```

### 3. Jalankan Streamlit Dashboard
```bash
streamlit run app.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`

---

## 📦 Dependensi

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.18.0
openpyxl>=3.1.0        # Untuk membaca file .xlsx
jupyter>=1.0.0
notebook>=7.0.0
```

> File lengkap ada di `requirements.txt`

---

## 👨‍💻 Tim & Konteks

- **Project**: Data Science Capstone — DBS Foundation 2026  
- **Sumber Data**: `D:\DBS_Foundation-2026\data_clean_DS\`  
- **Stack**: Python 3.10+, Pandas, Plotly, Streamlit  

---

*Last updated: Mei 2026*
