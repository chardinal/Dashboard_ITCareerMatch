import streamlit as st
import pandas as pd
import base64
import os

from data_loader import (
    load_cv, load_job, load_glints,
    GLINTS_ROLE_COL, GLINTS_WORK_TIME_COL
)

_CITY_COL    = "kota_singkat"
_WORKSYS_COL = "sistem_kerja_label"

from visualizations import (
    fig_bq1, fig_bq2, fig_bq3, fig_bq4, fig_bq5,
    fig_bq6, fig_bq7, fig_bq8, fig_bq9, fig_bq10
)

# Page Config

st.set_page_config(
    page_title="ITCareerMatch — Recruitment Analytics",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper: encode logo

def get_logo_b64(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo_capstone.png")
logo_b64  = get_logo_b64(LOGO_PATH)

# Custom CSS

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.brand-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 60%, #0f3460 100%);
    padding: 1.8rem 2.8rem;
    border-radius: 18px;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}
.brand-bar img {
    height: 68px;
    width: 68px;
    object-fit: contain;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.5));
}
.brand-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #e0f7fa;
    letter-spacing: -0.5px;
    line-height: 1.15;
}
.brand-subtitle {
    font-size: 0.9rem;
    color: #90a4ae;
    margin-top: 4px;
    letter-spacing: 0.2px;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1a3e, #22224a);
    border: 1px solid rgba(99,102,241,0.28);
    border-radius: 12px;
    padding: 1rem;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #a78bfa;
    font-size: 1.55rem;
    font-weight: 700;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #94a3b8;
    font-size: 0.8rem;
}

[data-baseweb="tab-list"] { gap: 5px; }
[data-baseweb="tab"] {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 5px 16px;
    font-weight: 600;
    font-size: 0.82rem;
    color: #94a3b8;
    border: 1px solid rgba(255,255,255,0.06);
}
[aria-selected="true"] {
    background: linear-gradient(135deg, #5c5ff5, #8b5cf6) !important;
    color: white !important;
    border: none !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1120 0%, #161b38 100%);
    border-right: 1px solid rgba(99,102,241,0.22);
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #e2e8f0;
}

.sidebar-heading {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6366f1;
    margin: 1rem 0 0.4rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid rgba(99,102,241,0.25);
}

.bq-question-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.13), rgba(139,92,246,0.08));
    border: 1px solid rgba(99,102,241,0.30);
    border-left: 4px solid #6366f1;
    border-radius: 0 14px 14px 0;
    padding: 1rem 1.3rem;
    margin-bottom: 1.1rem;
    position: relative;
}
.bq-question-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #818cf8;
    margin-bottom: 0.4rem;
}
.bq-question-text {
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0;
    line-height: 1.55;
}

.bq-badge {
    display: inline-block;
    background: linear-gradient(90deg, #5c5ff5, #8b5cf6);
    color: white;
    border-radius: 20px;
    padding: 2px 13px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
    letter-spacing: 0.5px;
}

.conclusion-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.07));
    border-left: 4px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.1rem;
    margin-top: 0.8rem;
    color: #c7d2fe;
    font-size: 0.9rem;
}

hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Header / Brand Bar

logo_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

st.markdown(f"""
<div class="brand-bar">
    {logo_tag}
    <div>
        <div class="brand-title">ITCareerMatch</div>
        <div class="brand-subtitle">Recruitment Analytics · DBS Foundation Data Science Capstone 2026</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load Data

@st.cache_data(show_spinner=False)
def get_all_data():
    return load_cv(), load_job(), load_glints()

with st.spinner("Memuat dataset..."):
    try:
        df_cv, df_job, df_glints = get_all_data()
    except FileNotFoundError as e:
        st.error(f"**Dataset tidak ditemukan:** {e}")
        st.info("Pastikan folder `data/` berisi file Dataset_CV, Dataset_Job, dan Dataset_Glints_Job.")
        st.stop()

# Sidebar Filters

with st.sidebar:
    st.markdown(
        "<div style='font-size:1.1rem; font-weight:800; letter-spacing:1.5px; "
        "text-transform:uppercase; color:#e2e8f0; padding: 0.6rem 0 0.2rem 0; "
        "border-bottom: 2px solid rgba(99,102,241,0.5); margin-bottom:0.8rem;'>"
        "FILTER &amp; INFO"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-heading">CATATAN FILTER</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background:rgba(99,102,241,0.10); border-left:3px solid #6366f1;
                    border-radius:0 10px 10px 0; padding:0.7rem 0.9rem; margin-bottom:0.6rem;'>
            <span style='color:#94a3b8; font-size:0.78rem; line-height:1.5;'>
                Filter berikut hanya berlaku untuk data <b style='color:#a5b4fc;'>Glints_Job</b>.<br>
                <span style='color:#64748b;'>BQ 1, 2, 5, 7, 9 tidak terpengaruh filter ini.</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-heading">FILTER KOTA (GLINTS)</div>', unsafe_allow_html=True)
    all_cities = sorted(df_glints[_CITY_COL].dropna().unique().tolist())
    selected_cities = st.multiselect("Pilih kota (kosong = semua)", options=all_cities, default=[])

    st.markdown('<div class="sidebar-heading">FILTER KATEGORI PERAN (GLINTS)</div>', unsafe_allow_html=True)
    all_roles = sorted(df_glints[GLINTS_ROLE_COL].dropna().unique().tolist())
    selected_roles = st.multiselect("Pilih kategori peran (kosong = semua)", options=all_roles, default=[])

    st.markdown('<div class="sidebar-heading">FILTER SISTEM KERJA (GLINTS)</div>', unsafe_allow_html=True)
    all_worksys = sorted(df_glints[_WORKSYS_COL].dropna().unique().tolist())
    selected_worksys = st.multiselect("Pilih sistem kerja (kosong = semua)", options=all_worksys, default=[])

    st.markdown(
        "<div style='font-size:0.7rem; color:#4a5568; margin-top:0.3rem; padding: 0.3rem 0.2rem; "
        "border-top:1px solid rgba(255,255,255,0.05);'>Filter berlaku pada <b>BQ 3, 4, 6, 8, 10</b></div>",
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border-top:1px solid rgba(255,255,255,0.07); margin:1rem 0;'>", unsafe_allow_html=True)

# Apply filters
df_g = df_glints.copy()
if selected_cities:
    df_g = df_g[df_g[_CITY_COL].isin(selected_cities)]
if selected_roles:
    df_g = df_g[df_g[GLINTS_ROLE_COL].isin(selected_roles)]
if selected_worksys:
    df_g = df_g[df_g[_WORKSYS_COL].isin(selected_worksys)]

# Tabs

tab_labels = [
    "BQ1 · Pendidikan CV",
    "BQ2 · Level Lowongan",
    "BQ3 · Kota & Kerja",
    "BQ4 · Median Gaji",
    "BQ5 · Gap Pendidikan",
    "BQ6 · Top Skill",
    "BQ7 · Skill vs Exp",
    "BQ8 · Tipe Waktu",
    "BQ9 · Restriksi",
    "BQ10 · Gaji x Sistem Kerja",
]

tabs = st.tabs(tab_labels)

# Tab 1 — BQ 1
with tabs[0]:
    st.markdown('<span class="bq-badge">BQ 1</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 1</div>"
        "<div class='bq-question-text'>Bagaimana distribusi tingkat pendidikan kandidat dalam Dataset_CV, dan apakah S1 mendominasi lebih dari 50% dari total kandidat?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Distribusi Tingkat Pendidikan Kandidat")
    st.caption("Sumber data: Dataset_CV · Tidak terpengaruh filter sidebar")

    fig1, m1 = fig_bq1(df_cv)
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Kandidat",       f"{m1['total_kandidat']:,}")
    c2.metric("Persentase S1",         f"{m1['s1_pct']}%")
    c3.metric("Pendidikan Terbanyak",  m1['top_edu'])

    if m1["dominasi"]:
        st.success(f"S1 mendominasi lebih dari 50% kandidat (aktual: **{m1['s1_pct']}%**).")
    else:
        st.warning(f"S1 belum mendominasi >50% (aktual: **{m1['s1_pct']}%**). Pendidikan terbanyak: **{m1['top_edu']}**.")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Jika S1 mendominasi, pasar kandidat IT didominasi lulusan sarjana.
        - Segmen non-S1 (D3, SMA, S2) mungkin under-represented namun bisa memiliki skill praktis tinggi.
        - Recruiter sebaiknya tidak over-filter pada gelar jika fokus pada skill.
        """)

# Tab 2 — BQ 2
with tabs[1]:
    st.markdown('<span class="bq-badge">BQ 2</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 2</div>"
        "<div class='bq-question-text'>Dari seluruh lowongan di Dataset_Job, berapa persen yang menargetkan kandidat entry-level (0-2 tahun) dibandingkan mid-level (2-5 tahun) dan senior (5+ tahun), kemudian apakah entry-level mendominasi lebih dari 40% dari total lowongan?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Distribusi Level Pengalaman yang Dibutuhkan Lowongan")
    st.caption("Sumber data: Dataset_Job · Tidak terpengaruh filter sidebar")

    fig2, m2 = fig_bq2(df_job)
    st.plotly_chart(fig2, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Lowongan",         f"{m2['total_lowongan']:,}")
    c2.metric("% Entry-Level (0-2 th)", f"{m2['entry_pct']}%")
    c3.metric("Dominasi Entry >40%",    "Ya" if m2['dominasi'] else "Tidak")

    if m2["dominasi"]:
        st.success(f"Entry-level mendominasi lebih dari 40% lowongan (aktual: **{m2['entry_pct']}%**). Pasar masih sangat terbuka untuk fresh graduate.")
    else:
        st.info(f"Entry-level: **{m2['entry_pct']}%** — belum mencapai threshold 40%. Pasar mungkin lebih condong ke kandidat berpengalaman.")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Dominasi entry-level menunjukkan banyak perusahaan terbuka untuk fresh graduate.
        - Segmen mid/senior: persaingan lebih ketat karena supply lebih terbatas.
        - Kandidat 2-5 tahun pengalaman bisa menjadi sweet spot rekrutmen.
        """)

# Tab 3 — BQ 3
with tabs[2]:
    st.markdown('<span class="bq-badge">BQ 3</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 3</div>"
        "<div class='bq-question-text'>Dari seluruh lowongan di Glints_Job, kota mana yang masuk top 5 terbanyak, dan bagaimana komposisi sistem kerja (WFO/WFH/Hybrid) di masing-masing kota tersebut?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Top 5 Kota & Komposisi Sistem Kerja (Glints_Job)")
    st.caption("Sumber data: Glints_Job · Filter sidebar aktif")

    fig3, m3 = fig_bq3(df_g)
    st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "**Top 5 Kota dengan Lowongan Terbanyak:** "
        + " · ".join([f"**{i+1}. {k}**" for i, k in enumerate(m3['top5_cities'])])
    )

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Kota dengan dominasi WFH tinggi cocok untuk target rekrutmen remote-friendly.
        - Jakarta biasanya mendominasi — WFO masih tinggi karena konsentrasi kantor pusat.
        - Kandidat di luar Jabodetabek bisa menargetkan lowongan WFH/Hybrid.
        """)

# Tab 4 — BQ 4
with tabs[3]:
    st.markdown('<span class="bq-badge">BQ 4</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 4</div>"
        "<div class='bq-question-text'>Dari kategori peran di Glints_Job yang memiliki minimal 5 lowongan, mana 10 peran dengan median gaji tertinggi dan terendah (diluar perusahaan yang tidak menampilkan gaji), dan seberapa lebar rentang gajinya?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Median Gaji per Kategori Peran — Top 10 & Bottom 10")
    st.caption("Sumber data: Glints_Job · Filter sidebar aktif · Hanya kategori dengan data gaji")

    min_listing = st.slider("Minimal jumlah lowongan per kategori:", 2, 20, 5, key="bq4_slider")

    try:
        fig4_bar, fig4_box, m4 = fig_bq4(df_g, min_listings=min_listing)

        subtab1, subtab2 = st.tabs(["Bar Chart Median Gaji", "Box Plot Rentang Gaji"])
        with subtab1:
            st.plotly_chart(fig4_bar, use_container_width=True)
        with subtab2:
            st.plotly_chart(fig4_box, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric("Peran Gaji Tertinggi", m4['top_role'], f"Rp {m4['top_median']/1_000_000:.1f} Jt (median)")
        c2.metric("Peran Gaji Terendah",  m4['bot_role'], f"Rp {m4['bot_median']/1_000_000:.1f} Jt (median)")

        st.info(f"Rentang median gaji antara peran tertinggi & terendah: **Rp {(m4['top_median']-m4['bot_median'])/1_000_000:.1f} Jt**")
    except Exception as e:
        st.error(f"Gagal memuat chart BQ 4: {e}")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Peran dengan median gaji tinggi biasanya membutuhkan skill specialized (AI/ML, Cloud, Cybersecurity).
        - Box plot menunjukkan sebaran — rentang lebar berarti negosiasi gaji lebih fleksibel.
        - Kandidat dapat menggunakan data ini untuk benchmark ekspektasi gaji.
        """)

# Tab 5 — BQ 5
with tabs[4]:
    st.markdown('<span class="bq-badge">BQ 5</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 5</div>"
        "<div class='bq-question-text'>Bagaimana perbandingan distribusi tingkat pendidikan antara kandidat (Dataset_CV) dan syarat minimum lowongan (Dataset_Job) secara berdampingan per level pendidikan, serta di level mana selisih persentase antara keduanya paling besar (&gt;15 poin)?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Gap Distribusi Pendidikan: Kandidat (CV) vs. Syarat Lowongan (Job)")
    st.caption("Sumber data: Dataset_CV & Dataset_Job · Tidak terpengaruh filter sidebar")

    fig5, m5 = fig_bq5(df_cv, df_job)
    st.plotly_chart(fig5, use_container_width=True)

    c1, c2 = st.columns(2)
    c1.metric("Level dengan Gap Terbesar", m5['max_gap_level'])
    c2.metric("Selisih Persentase",        f"{m5['max_gap_value']} poin")

    if m5["has_big_gap"]:
        st.warning(
            f"Gap signifikan (>15 poin) ditemukan pada level **{m5['max_gap_level']}** "
            f"dengan selisih **{m5['max_gap_value']} poin**. Ini mengindikasikan mismatch supply-demand."
        )
    else:
        st.success("Tidak ada gap signifikan (>15 poin) antara distribusi pendidikan kandidat dan lowongan.")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Gap besar pada S2 ke atas: over-supply kandidat pascasarjana tapi under-demand.
        - Gap besar pada SMA/SMK: kandidat tanpa gelar banyak, namun lowongan sedikit.
        - Informasi ini berguna untuk lembaga pendidikan dan pembuat kebijakan ketenagakerjaan.
        """)

# Tab 6 — BQ 6
with tabs[5]:
    st.markdown('<span class="bq-badge">BQ 6</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 6</div>"
        "<div class='bq-question-text'>Dari seluruh lowongan di Glints_Job, apa 15 skill yang paling sering muncul di kolom skill (dihitung setelah split koma), dan apakah ada 1 skill yang muncul di lebih dari 30% total lowongan sehingga bisa disebut skill dominan pasar IT?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Top 15 Skill Paling Sering di Lowongan Glints")
    st.caption("Sumber data: Glints_Job · Filter sidebar aktif · Garis merah = threshold 30%")

    try:
        fig6, m6 = fig_bq6(df_g)
        st.plotly_chart(fig6, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Skill Paling Sering",       m6['top_skill'])
        c2.metric("Frekuensi Kemunculan",       f"{m6['top_skill_pct']}%")
        c3.metric("Jumlah Skill Dominan (>30%)", m6['dominant_count'])

        if m6["has_dominant"]:
            st.success(
                f"**{m6['top_skill']}** muncul di **{m6['top_skill_pct']}%** dari total lowongan (>30%) — skill wajib pasar IT."
            )
        else:
            st.info(
                f"Belum ada skill tunggal yang melampaui 30%. "
                f"Skill terbanyak (**{m6['top_skill']}**) hanya muncul di {m6['top_skill_pct']}% lowongan."
            )
    except Exception as e:
        st.error(f"Gagal memuat chart BQ 6: {e}")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Skill yang muncul >30% adalah must-have untuk kompetitif di pasar kerja IT.
        - Kandidat sebaiknya prioritaskan skill dengan frekuensi tinggi dalam pengembangan diri.
        - Lembaga pelatihan bisa gunakan data ini sebagai kurikulum prioritas.
        """)

# Tab 7 — BQ 7
with tabs[6]:
    st.markdown('<span class="bq-badge">BQ 7</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 7</div>"
        "<div class='bq-question-text'>Dari kandidat di Dataset_CV, berapa rata-rata jumlah skill per bucket pengalaman, dan apakah kandidat senior (5+ tahun) memiliki rata-rata skill minimal 2x lebih banyak dibanding entry-level (0-1 tahun)?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Rata-rata Jumlah Skill per Bucket Pengalaman (Dataset_CV)")
    st.caption("Sumber data: Dataset_CV · Tidak terpengaruh filter sidebar · Error bar = standar deviasi")

    try:
        fig7, m7 = fig_bq7(df_cv)
        st.plotly_chart(fig7, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Rata-rata Skill Entry (0-1 th)", f"{m7['entry_mean']:.2f}")
        c2.metric("Rata-rata Skill Senior (5+ th)", f"{m7['senior_mean']:.2f}")
        c3.metric("Rasio Senior / Entry",           f"{m7['ratio']}x")

        if m7["is_2x"]:
            st.success(
                f"Kandidat senior (5+ tahun) memiliki rata-rata **{m7['senior_mean']:.2f}** skill — "
                f"**{m7['ratio']}x** lebih banyak dibanding entry-level (**{m7['entry_mean']:.2f}**). Threshold >=2x terpenuhi."
            )
        else:
            st.warning(
                f"Rasio senior/entry = **{m7['ratio']}x** — belum mencapai 2x. "
                f"Senior: {m7['senior_mean']:.2f} vs Entry: {m7['entry_mean']:.2f}."
            )
    except Exception as e:
        st.error(f"Gagal memuat chart BQ 7: {e}")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Rasio <2x: entry-level sudah cukup skill-rich (mungkin karena bootcamp, dll.).
        - Rasio >2x: gap skill jelas dan seniority sangat berpengaruh.
        - Data berguna untuk desain program mentoring & jenjang karir.
        """)

# Tab 8 — BQ 8
with tabs[7]:
    st.markdown('<span class="bq-badge">BQ 8</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 8</div>"
        "<div class='bq-question-text'>Dari kategori peran di Glints_Job, apakah tipe waktu kerja Penuh Waktu mendominasi lebih dari 70% di setiap kategori, atau ada kategori tertentu yang justru didominasi Magang/Freelance/Kontrak?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Dominasi Tipe Waktu Kerja per Kategori Peran (Glints_Job)")
    st.caption("Sumber data: Glints_Job · Filter sidebar aktif · Garis merah = threshold 70% Penuh Waktu")

    try:
        fig8, m8 = fig_bq8(df_g)
        st.plotly_chart(fig8, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric("Total Kategori Peran", m8['total_roles'])
        c2.metric(
            "Penuh Waktu >70% Semua Kategori?",
            "Ya" if m8['dominasi_penuh'] else f"Tidak ({len(m8['outlier_roles'])} outlier)"
        )

        if m8["dominasi_penuh"]:
            st.success("Penuh Waktu mendominasi >70% di **semua** kategori peran.")
        else:
            st.warning(
                f"Terdapat **{len(m8['outlier_roles'])}** kategori dengan Penuh Waktu <70%:\n\n"
                + "\n".join([f"- {r}" for r in m8['outlier_roles']])
            )
    except Exception as e:
        st.error(f"Gagal memuat chart BQ 8: {e}")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Kategori yang didominasi Magang biasanya adalah peran junior atau program khusus.
        - Freelance tinggi di kategori kreatif atau project-based roles.
        - Kontrak tinggi bisa mengindikasikan pekerjaan musiman atau project IT.
        """)

# Tab 9 — BQ 9
with tabs[8]:
    st.markdown('<span class="bq-badge">BQ 9</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 9</div>"
        "<div class='bq-question-text'>Dari seluruh lowongan di Dataset_Job, berapa persen yang masih mencantumkan persyaratan gender atau usia spesifik, dan posisi apa yang paling sering membatasinya, serta apakah total lowongan yang membatasi melebihi 20% dari keseluruhan?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Lowongan dengan Persyaratan Gender atau Usia Spesifik")
    st.caption("Sumber data: Dataset_Job · Tidak terpengaruh filter sidebar · Threshold = 20% dari total lowongan")

    try:
        fig9_pie, fig9_bar, m9 = fig_bq9(df_job)

        col_pie, col_bar = st.columns([1, 1.6])
        with col_pie:
            st.plotly_chart(fig9_pie, use_container_width=True)
        with col_bar:
            st.plotly_chart(fig9_bar, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Lowongan",           f"{m9['total']:,}")
        c2.metric("Lowongan dengan Batasan",  f"{m9['restricted']:,} ({m9['pct_restricted']}%)")
        c3.metric("Posisi Pembatas Terbanyak", m9['top_position'])

        if m9["exceeds_20pct"]:
            st.error(
                f"Lowongan dengan batasan melebihi 20% (aktual: **{m9['pct_restricted']}%**)! "
                f"Perlu perhatian dari perspektif kesetaraan & inklusivitas. "
                f"Posisi paling sering membatasi: **{m9['top_position']}**."
            )
        else:
            st.success(
                f"Lowongan dengan batasan gender/usia: **{m9['pct_restricted']}%** "
                f"— masih di bawah threshold 20%."
            )
    except Exception as e:
        st.error(f"Gagal memuat chart BQ 9: {e}")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - Batasan gender/usia dapat mengindikasikan praktik rekrutmen diskriminatif.
        - Perusahaan dengan lebih banyak batasan perlu diadvokasi untuk kebijakan inklusif.
        - Data ini penting untuk laporan Diversity & Inclusion (D&I) dalam HR analytics.
        """)

# Tab 10 — BQ 10
with tabs[9]:
    st.markdown('<span class="bq-badge">BQ 10</span>', unsafe_allow_html=True)
    st.markdown(
        "<div class='bq-question-card'>"
        "<div class='bq-question-label'>Business Question 10</div>"
        "<div class='bq-question-text'>Dari 10 kategori peran terbanyak di Glints_Job, bagaimana perbandingan median gaji antara lowongan WFO, WFH, dan Hybrid?</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.subheader("Perbandingan Median Gaji WFO vs. WFH vs. Hybrid per Kategori (Glints_Job)")
    st.caption("Sumber data: Glints_Job · Filter sidebar aktif · 10 kategori peran terbanyak")

    try:
        fig10_bar, fig10_heat, m10 = fig_bq10(df_g)

        subtab1, subtab2 = st.tabs(["Grouped Bar Chart", "Heatmap"])
        with subtab1:
            st.plotly_chart(fig10_bar, use_container_width=True)
        with subtab2:
            st.plotly_chart(fig10_heat, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric("Top 10 Kategori Dianalisis",                    len(m10['top10_roles']))
        c2.metric("Sistem Kerja dengan Median Gaji Tertinggi", m10['best_work_system'])

        st.info(
            f"Sistem kerja **{m10['best_work_system']}** memiliki median gaji tertinggi "
            f"di antara 10 kategori peran terbanyak di Glints."
        )
    except Exception as e:
        st.error(f"Gagal memuat chart BQ 10: {e}")

    with st.expander("Interpretasi & Implikasi"):
        st.markdown("""
        - WFH/Hybrid dengan gaji lebih tinggi menunjukkan tren remote premium di pasar IT.
        - WFO lebih rendah bisa berarti perusahaan menganggap kehadiran fisik sebagai standar.
        - Kandidat bisa negosiasi gaji lebih tinggi untuk posisi WFO yang mengharuskan commute.
        """)

# Footer

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#475569; font-size:0.82rem; padding: 0.8rem 0'>"
    "<b>ITCareerMatch</b> · DBS Foundation Data Science Capstone 2026 · Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
