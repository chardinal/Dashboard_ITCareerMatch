"""
visualizations.py
=================
Modul semua fungsi pembuatan chart Plotly untuk Recruitment Analytics Dashboard.
Setiap fungsi merepresentasikan satu Business Question (BQ).

Fungsi-fungsi ini dipakai BERSAMA oleh:
  - app.py           (Streamlit Dashboard)
  - notebooks/EDA.ipynb (eksplorasi interaktif)

Penulis: Data Science Capstone — DBS Foundation 2026
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import (
    CV_EDUCATION_COL, CV_EXPERIENCE_COL, CV_SKILL_COL,
    JOB_POSITION_COL, JOB_MIN_EXP_COL, JOB_EDU_COL,
    GLINTS_ROLE_COL, GLINTS_CITY_COL, GLINTS_WORK_SYS_COL,
    GLINTS_WORK_TIME_COL, GLINTS_SALARY_MIN, GLINTS_SALARY_MAX,
    GLINTS_SKILL_COL, split_skills, top_n_cities, WORK_SYS_LABELS
)

# Kolom kota yang sudah disederhanakan (hasil parse dari load_glints)
_CITY_COL = "kota_singkat"          # 'Jakarta Selatan' bukan 'Jakarta Selatan, DKI Jakarta'
_WORKSYS_COL = "sistem_kerja_label" # 'WFO' / 'WFH' / 'Hybrid'

# ─────────────────────────────────────────────────────────────────────────────
# PALET WARNA KONSISTEN
# ─────────────────────────────────────────────────────────────────────────────

COLOR_SEQ        = px.colors.qualitative.Bold
COLOR_EDUCATION  = px.colors.sequential.Teal
COLOR_WFO        = "#2196F3"
COLOR_WFH        = "#4CAF50"
COLOR_HYBRID     = "#FF9800"
COLOR_THRESHOLD  = "#E53935"

TEMPLATE = "plotly_dark"


# ─────────────────────────────────────────────────────────────────────────────
# BQ 1 — Distribusi Pendidikan Kandidat (Dataset_CV)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq1(df_cv: pd.DataFrame) -> tuple[go.Figure, dict]:
    """
    BQ 1: Distribusi tingkat pendidikan kandidat.
    Chart: Pie Chart + Bar Chart (subplot side-by-side).
    Returns: (fig, metrics_dict)
    """
    counts = df_cv[CV_EDUCATION_COL].value_counts().reset_index()
    counts.columns = ["Pendidikan", "Jumlah"]
    counts["Persentase"] = (counts["Jumlah"] / counts["Jumlah"].sum() * 100).round(2)

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "xy"}]],
        subplot_titles=["Proporsi (Pie Chart)", "Jumlah per Level (Bar Chart)"]
    )

    # Pie
    fig.add_trace(
        go.Pie(
            labels=counts["Pendidikan"],
            values=counts["Jumlah"],
            hole=0.35,
            textinfo="label+percent",
            marker=dict(colors=COLOR_SEQ),
            name="Pendidikan"
        ),
        row=1, col=1
    )

    # Bar
    fig.add_trace(
        go.Bar(
            x=counts["Pendidikan"],
            y=counts["Jumlah"],
            text=counts["Persentase"].apply(lambda x: f"{x}%"),
            textposition="outside",
            marker_color=COLOR_SEQ[:len(counts)],
            name="Jumlah"
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="BQ 1 — Distribusi Tingkat Pendidikan Kandidat",
        template=TEMPLATE,
        showlegend=False,
        height=480
    )

    # Hitung metrik
    total = counts["Jumlah"].sum()
    s1_pct = counts.loc[
        counts["Pendidikan"].str.contains("S1|Sarjana|Bachelor", case=False, na=False),
        "Persentase"
    ].sum()

    metrics = {
        "total_kandidat": int(total),
        "s1_pct": round(float(s1_pct), 2),
        "dominasi": s1_pct > 50,
        "top_edu": counts.iloc[0]["Pendidikan"]
    }
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 2 — Distribusi Level Pengalaman Lowongan (Dataset_Job)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq2(df_job: pd.DataFrame) -> tuple[go.Figure, dict]:
    """
    BQ 2: Distribusi level pengalaman di lowongan (entry/mid/senior).
    Chart: Donut Chart.
    Returns: (fig, metrics_dict)
    """
    counts = df_job["experience_level"].value_counts().reset_index()
    counts.columns = ["Level", "Jumlah"]
    counts["Persentase"] = (counts["Jumlah"] / counts["Jumlah"].sum() * 100).round(2)

    fig = go.Figure(
        go.Pie(
            labels=counts["Level"],
            values=counts["Jumlah"],
            hole=0.45,
            textinfo="label+percent+value",
            marker=dict(colors=[COLOR_WFO, COLOR_WFH, COLOR_HYBRID]),
            pull=[0.05, 0, 0]
        )
    )

    fig.update_layout(
        title_text="BQ 2 — Distribusi Level Pengalaman Lowongan",
        template=TEMPLATE,
        height=480,
        annotations=[dict(text="Level<br>Pengalaman", x=0.5, y=0.5, font_size=14, showarrow=False)]
    )

    total = counts["Jumlah"].sum()
    entry_pct = counts.loc[
        counts["Level"].str.contains("Entry", case=False, na=False), "Persentase"
    ].sum()

    metrics = {
        "total_lowongan": int(total),
        "entry_pct": round(float(entry_pct), 2),
        "dominasi": entry_pct > 40
    }
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 3 — Top 5 Kota & Komposisi Sistem Kerja (Glints_Job)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq3(df_glints: pd.DataFrame) -> tuple[go.Figure, dict]:
    """
    BQ 3: Top 5 kota dan komposisi WFO/WFH/Hybrid.
    Chart: Horizontal Stacked Bar Chart.
    Menggunakan kolom 'kota_singkat' dan 'sistem_kerja_label' hasil parse.
    Returns: (fig, metrics_dict)
    """
    top5 = top_n_cities(df_glints, _CITY_COL, n=5)
    df_top5 = df_glints[df_glints[_CITY_COL].isin(top5)]

    pivot = (
        df_top5.groupby([_CITY_COL, _WORKSYS_COL])
        .size()
        .reset_index(name="Jumlah")
    )

    color_map = {"WFO": COLOR_WFO, "WFH": COLOR_WFH, "Hybrid": COLOR_HYBRID}

    fig = px.bar(
        pivot,
        x="Jumlah",
        y=_CITY_COL,
        color=_WORKSYS_COL,
        orientation="h",
        barmode="stack",
        text="Jumlah",
        color_discrete_map=color_map,
        category_orders={_CITY_COL: top5},
        title="BQ 3 — Top 5 Kota & Komposisi Sistem Kerja",
        labels={_CITY_COL: "Kota", "Jumlah": "Jumlah Lowongan",
                _WORKSYS_COL: "Sistem Kerja"}
    )
    fig.update_layout(template=TEMPLATE, height=420, legend_title="Sistem Kerja")
    fig.update_traces(textposition="inside")

    metrics = {"top5_cities": top5}
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 4 — Top/Bottom 10 Median Gaji per Peran (Glints_Job)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq4(df_glints: pd.DataFrame, min_listings: int = 5) -> tuple[go.Figure, dict]:
    """
    BQ 4: Median gaji 10 tertinggi & 10 terendah, dengan salary range.
    Chart: Horizontal Bar Chart (2 panel) + Box Plot.
    Returns: (fig_bar, fig_box, metrics_dict)
    """
    df_salary = df_glints[df_glints["salary_median"].notna()].copy()

    # Agregasi per kategori peran dengan minimal min_listings
    role_stats = (
        df_salary.groupby(GLINTS_ROLE_COL)
        .agg(
            median_gaji=("salary_median", "median"),
            count=(GLINTS_ROLE_COL, "count"),
            salary_range_min=(GLINTS_SALARY_MIN, "min"),
            salary_range_max=(GLINTS_SALARY_MAX, "max")
        )
        .reset_index()
        .query(f"count >= {min_listings}")
        .sort_values("median_gaji", ascending=False)
        .reset_index(drop=True)
    )

    top10 = role_stats.head(10).copy()
    bot10 = role_stats.tail(10).sort_values("median_gaji").copy()

    def _format_rp(val):
        return f"Rp {val/1_000_000:.1f}Jt"

    # Chart Bar 2 panel
    fig_bar = make_subplots(
        rows=1, cols=2,
        subplot_titles=["10 Peran Gaji Tertinggi", "10 Peran Gaji Terendah"],
        shared_xaxes=False
    )

    # Hitung x-range + padding supaya label tidak terpotong/bertabrakan
    top10_max = top10["median_gaji"].max() if not top10.empty else 1
    bot10_max = bot10["median_gaji"].max() if not bot10.empty else 1

    fig_bar.add_trace(
        go.Bar(
            x=top10["median_gaji"],
            y=top10[GLINTS_ROLE_COL],
            orientation="h",
            marker_color=COLOR_WFH,
            text=top10["median_gaji"].apply(_format_rp),
            textposition="inside",
            insidetextanchor="end",
            name="Tertinggi"
        ),
        row=1, col=1
    )

    fig_bar.add_trace(
        go.Bar(
            x=bot10["median_gaji"],
            y=bot10[GLINTS_ROLE_COL],
            orientation="h",
            marker_color=COLOR_THRESHOLD,
            text=bot10["median_gaji"].apply(_format_rp),
            textposition="inside",
            insidetextanchor="end",
            name="Terendah"
        ),
        row=1, col=2
    )

    fig_bar.update_layout(
        title_text="BQ 4 — Median Gaji per Kategori Peran (Top & Bottom 10)",
        template=TEMPLATE,
        height=560,
        showlegend=False
    )
    # Tick sumbu X setiap 5 juta supaya lebih rapi
    fig_bar.update_xaxes(tickformat=".0s", dtick=5_000_000, row=1, col=1)
    fig_bar.update_xaxes(tickformat=".0s", dtick=5_000_000, row=1, col=2)

    # Box Plot
    df_filtered = df_salary[df_salary[GLINTS_ROLE_COL].isin(top10[GLINTS_ROLE_COL].tolist())]
    fig_box = px.box(
        df_filtered,
        x="salary_median",
        y=GLINTS_ROLE_COL,
        orientation="h",
        title="BQ 4 — Rentang Gaji (Box Plot) — Top 10 Peran",
        labels={"salary_median": "Gaji Median (Rp)", GLINTS_ROLE_COL: "Kategori Peran"},
        color=GLINTS_ROLE_COL,
        color_discrete_sequence=COLOR_SEQ
    )
    fig_box.update_layout(template=TEMPLATE, height=560, showlegend=False)

    metrics = {
        "top_role": top10.iloc[0][GLINTS_ROLE_COL] if not top10.empty else "N/A",
        "top_median": top10.iloc[0]["median_gaji"] if not top10.empty else 0,
        "bot_role": bot10.iloc[0][GLINTS_ROLE_COL] if not bot10.empty else "N/A",
        "bot_median": bot10.iloc[0]["median_gaji"] if not bot10.empty else 0,
    }
    return fig_bar, fig_box, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 5 — Perbandingan Distribusi Pendidikan CV vs. Job
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq5(df_cv: pd.DataFrame, df_job: pd.DataFrame) -> tuple[go.Figure, dict]:
    """
    BQ 5: Perbandingan distribusi pendidikan kandidat vs. syarat lowongan.
    Chart: Grouped Bar Chart + highlight selisih >15 poin.
    Returns: (fig, metrics_dict)
    """
    cv_pct = (
        df_cv[CV_EDUCATION_COL].value_counts(normalize=True) * 100
    ).rename("Kandidat (CV)").round(2)

    job_pct = (
        df_job[JOB_EDU_COL].value_counts(normalize=True) * 100
    ).rename("Syarat Lowongan (Job)").round(2)

    combined = pd.concat([cv_pct, job_pct], axis=1).fillna(0).reset_index()
    combined.columns = ["Pendidikan", "Kandidat (CV)", "Syarat Lowongan (Job)"]
    combined["Selisih"] = (combined["Kandidat (CV)"] - combined["Syarat Lowongan (Job)"]).abs().round(2)
    combined = combined.sort_values("Kandidat (CV)", ascending=False)

    fig = go.Figure()

    for col, color in [("Kandidat (CV)", COLOR_WFO), ("Syarat Lowongan (Job)", COLOR_WFH)]:
        fig.add_trace(go.Bar(
            name=col,
            x=combined["Pendidikan"],
            y=combined[col],
            text=combined[col].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            marker_color=color
        ))

    # Highlight selisih >15 poin — label diletakkan di sisi kanan bar tertinggi
    big_gap = combined[combined["Selisih"] > 15]
    for _, row in big_gap.iterrows():
        y_top = max(row["Kandidat (CV)"], row["Syarat Lowongan (Job)"])
        fig.add_annotation(
            x=row["Pendidikan"],
            y=y_top + 5,          # di atas bar tertinggi
            text=f"⚠ Gap {row['Selisih']:.1f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLOR_THRESHOLD,
            ay=-30,               # panah ke bawah menuju bar
            font=dict(color=COLOR_THRESHOLD, size=11, weight="bold"),
            bgcolor="rgba(30,30,60,0.75)",
            bordercolor=COLOR_THRESHOLD,
            borderwidth=1,
            borderpad=3
        )

    fig.update_layout(
        barmode="group",
        title_text="BQ 5 — Perbandingan Distribusi Pendidikan: Kandidat vs. Lowongan",
        template=TEMPLATE,
        height=480,
        yaxis_title="Persentase (%)",
        legend_title="Sumber Data"
    )

    max_gap_row = combined.loc[combined["Selisih"].idxmax()]
    metrics = {
        "max_gap_level": max_gap_row["Pendidikan"],
        "max_gap_value": round(float(max_gap_row["Selisih"]), 2),
        "has_big_gap": len(big_gap) > 0
    }
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 6 — Top 15 Skill Paling Sering di Glints_Job
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq6(df_glints: pd.DataFrame, top_n: int = 15) -> tuple[go.Figure, dict]:
    """
    BQ 6: Top 15 skill + threshold 30% (skill dominan).
    Chart: Horizontal Bar Chart dengan garis vertikal 30%.
    Returns: (fig, metrics_dict)
    """
    total_jobs = len(df_glints)
    skill_counts = (
        split_skills(df_glints[GLINTS_SKILL_COL])
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    skill_counts.columns = ["Skill", "Jumlah"]
    skill_counts["Persen"] = (skill_counts["Jumlah"] / total_jobs * 100).round(2)
    skill_counts = skill_counts.sort_values("Persen", ascending=True)  # ascending for horizontal

    threshold_pct = 30
    colors = [
        COLOR_THRESHOLD if p >= threshold_pct else COLOR_WFO
        for p in skill_counts["Persen"]
    ]

    fig = go.Figure(go.Bar(
        x=skill_counts["Persen"],
        y=skill_counts["Skill"],
        orientation="h",
        marker_color=colors,
        text=skill_counts["Persen"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        name="Skill Frequency"
    ))

    fig.add_vline(
        x=threshold_pct,
        line_dash="dash",
        line_color=COLOR_THRESHOLD,
        annotation_text="Threshold 30%",
        annotation_position="top right"
    )

    fig.update_layout(
        title_text=f"BQ 6 — Top {top_n} Skill Paling Sering di Glints_Job",
        template=TEMPLATE,
        height=580,
        xaxis_title="Persentase dari Total Lowongan (%)",
        yaxis_title="Skill"
    )

    top_skill = skill_counts.iloc[-1]
    dominant_skills = skill_counts[skill_counts["Persen"] >= threshold_pct]

    metrics = {
        "top_skill": top_skill["Skill"],
        "top_skill_pct": round(float(top_skill["Persen"]), 2),
        "has_dominant": len(dominant_skills) > 0,
        "dominant_count": len(dominant_skills)
    }
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 7 — Rata-rata Skill per Bucket Pengalaman (Dataset_CV)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq7(df_cv: pd.DataFrame) -> tuple[go.Figure, dict]:
    """
    BQ 7: Rata-rata jumlah skill per bucket pengalaman.
    Chart: Bar Chart (vertikal) + Line overlay.
    Menggunakan kolom 'experience_bucket' dan 'skill_count' hasil parse load_cv().
    Returns: (fig, metrics_dict)
    """
    # Pastikan kolom tersedia (fallback jika dipanggil dari notebook)
    df = df_cv.copy()
    if "skill_count" not in df.columns:
        df["skill_count"] = df[CV_SKILL_COL].fillna("").apply(
            lambda x: len([s for s in str(x).split(",") if s.strip()])
        )

    agg = (
        df.groupby("experience_bucket", observed=True)["skill_count"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    agg.columns = ["Bucket", "Mean Skill", "Std", "Jumlah Kandidat"]
    agg["Mean Skill"] = agg["Mean Skill"].round(2)
    agg["Std"] = agg["Std"].fillna(0).round(2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["Bucket"].astype(str),
        y=agg["Mean Skill"],
        name="Rata-rata Skill",
        marker_color=COLOR_SEQ[:len(agg)],
        error_y=dict(type="data", array=agg["Std"].tolist(), visible=True),
        text=agg["Mean Skill"].apply(lambda x: f"{x:.2f}"),
        textposition="outside"
    ))
    fig.add_trace(go.Scatter(
        x=agg["Bucket"].astype(str),
        y=agg["Mean Skill"],
        mode="lines+markers",
        name="Tren Skill",
        line=dict(color=COLOR_THRESHOLD, width=2.5, dash="dot"),
        marker=dict(size=9)
    ))
    fig.update_layout(
        title_text="BQ 7 — Rata-rata Jumlah Skill per Bucket Pengalaman (Dataset_CV)",
        template=TEMPLATE, height=480,
        yaxis_title="Rata-rata Jumlah Skill", legend_title="Keterangan"
    )

    entry_mask = agg["Bucket"].astype(str).str.contains("Entry", case=False, na=False)
    senior_mask = agg["Bucket"].astype(str).str.contains("Senior", case=False, na=False)
    entry_mean = float(agg.loc[entry_mask, "Mean Skill"].values[0]) if entry_mask.any() else 0
    senior_mean = float(agg.loc[senior_mask, "Mean Skill"].values[0]) if senior_mask.any() else 0
    ratio = round(senior_mean / entry_mean, 2) if entry_mean > 0 else 0

    metrics = {
        "entry_mean": round(entry_mean, 2),
        "senior_mean": round(senior_mean, 2),
        "ratio": ratio,
        "is_2x": ratio >= 2.0
    }
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 8 — Dominasi Tipe Waktu Kerja per Kategori Peran (Glints_Job)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq8(df_glints: pd.DataFrame) -> tuple[go.Figure, dict]:
    """
    BQ 8: Dominasi tipe waktu kerja (Penuh Waktu vs. lainnya) per kategori.
    Chart: 100% Stacked Horizontal Bar Chart.
    Penuh Waktu selalu ditampilkan sebagai segmen pertama (kiri) agar mudah
    dibandingkan dengan garis threshold 70%.
    Returns: (fig, metrics_dict)
    """
    pivot = (
        df_glints.groupby([GLINTS_ROLE_COL, GLINTS_WORK_TIME_COL])
        .size()
        .reset_index(name="Jumlah")
    )

    # Normalisasi ke persentase per kategori
    pivot_pct = pivot.copy()
    totals = pivot.groupby(GLINTS_ROLE_COL)["Jumlah"].transform("sum")
    pivot_pct["Persen"] = (pivot["Jumlah"] / totals * 100).round(2)

    # % Penuh Waktu per kategori (untuk sort & outlier check)
    pt_pct = (
        pivot_pct[
            pivot_pct[GLINTS_WORK_TIME_COL].str.contains("Penuh Waktu", case=False, na=False)
        ]
        .set_index(GLINTS_ROLE_COL)["Persen"]
    )

    # Kategori tanpa Penuh Waktu sama sekali → % = 0
    all_roles = pivot[GLINTS_ROLE_COL].unique().tolist()
    for r in all_roles:
        if r not in pt_pct.index:
            pt_pct[r] = 0.0

    # Urutkan: % Penuh Waktu terendah di atas, tertinggi di bawah
    sorted_roles = pt_pct.sort_values(ascending=True).index.tolist()

    # Urutan tipe waktu: Penuh Waktu PERTAMA supaya segmennya paling kiri
    # dan bisa langsung dibandingkan dengan garis 70%
    all_time_types = pivot_pct[GLINTS_WORK_TIME_COL].unique().tolist()
    penuh_waktu_labels = [t for t in all_time_types if "Penuh Waktu" in t]
    other_labels = sorted([t for t in all_time_types if "Penuh Waktu" not in t])
    ordered_time_types = penuh_waktu_labels + other_labels

    # Warna: Penuh Waktu → biru mencolok, sisanya dari palet
    color_map = {}
    color_map[penuh_waktu_labels[0]] = COLOR_WFO  # biru
    palette_rest = [c for c in COLOR_SEQ if c != COLOR_WFO]
    for i, label in enumerate(other_labels):
        color_map[label] = palette_rest[i % len(palette_rest)]

    fig = px.bar(
        pivot_pct,
        x="Persen",
        y=GLINTS_ROLE_COL,
        color=GLINTS_WORK_TIME_COL,
        orientation="h",
        barmode="relative",
        text="Persen",
        title="BQ 8 — Komposisi Tipe Waktu Kerja per Kategori Peran (100%)",
        labels={"Persen": "Persentase (%)", GLINTS_ROLE_COL: "Kategori Peran",
                GLINTS_WORK_TIME_COL: "Tipe Waktu Kerja"},
        category_orders={
            GLINTS_ROLE_COL: sorted_roles,
            GLINTS_WORK_TIME_COL: ordered_time_types   # Penuh Waktu selalu pertama
        },
        color_discrete_map=color_map
    )
    fig.add_vline(x=70, line_dash="dash", line_color=COLOR_THRESHOLD,
                  annotation_text="Threshold 70%", annotation_position="top right")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    fig.update_layout(template=TEMPLATE, height=900)

    # Outlier: semua kategori (termasuk yang % Penuh Waktu = 0) yang < 70%
    outlier_roles = pt_pct[pt_pct < 70].index.tolist()
    metrics = {
        "total_roles": len(all_roles),
        "outlier_roles": outlier_roles,
        "dominasi_penuh": len(outlier_roles) == 0
    }
    return fig, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 9 — Lowongan dengan Batasan Gender/Usia (Dataset_Job)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq9(df_job: pd.DataFrame) -> tuple[go.Figure, go.Figure, dict]:
    """
    BQ 9: % lowongan dengan batasan gender/usia, top posisi pembatas.
    Chart: Pie Chart + Horizontal Bar Chart.
    Gender aktual: 'tanpa ketentuan' | 'Laki-laki saja' | 'Perempuan saja'
    Returns: (fig_pie, fig_bar, metrics_dict)
    """
    total = len(df_job)
    restricted = int(df_job["has_restriction"].sum())
    unrestricted = total - restricted
    pct_restricted = round(restricted / total * 100, 2)

    # Pie Chart
    fig_pie = go.Figure(go.Pie(
        labels=["Ada Batasan Gender/Usia", "Tidak Ada Batasan"],
        values=[restricted, unrestricted],
        hole=0.4,
        marker=dict(colors=[COLOR_THRESHOLD, COLOR_WFH]),
        textinfo="label+percent+value"
    ))
    fig_pie.update_layout(
        title_text="BQ 9 — Proporsi Lowongan dengan Batasan Gender/Usia",
        template=TEMPLATE, height=420
    )

    # Bar Chart: Top posisi dengan batasan
    # Diurutkan ascending (terbanyak di bawah) agar warna gradien
    # dan urutan bar konsisten — makin ke bawah makin banyak batasan
    top_positions = (
        df_job[df_job["has_restriction"]][JOB_POSITION_COL]
        .value_counts()
        .head(15)
        .reset_index()
    )
    top_positions.columns = ["Posisi", "Jumlah Lowongan"]
    # Sort ascending: terbanyak di baris terakhir → tampil di bawah chart horizontal
    top_positions = top_positions.sort_values("Jumlah Lowongan", ascending=True).reset_index(drop=True)

    fig_bar = px.bar(
        top_positions,
        x="Jumlah Lowongan",
        y="Posisi",
        orientation="h",
        text="Jumlah Lowongan",
        title="BQ 9 — Top 15 Posisi dengan Batasan Gender/Usia",
        color="Jumlah Lowongan",
        color_continuous_scale="Reds",
        # Pertahankan urutan sorting (ascending) agar tidak di-override Plotly
        category_orders={"Posisi": top_positions["Posisi"].tolist()}
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(template=TEMPLATE, height=500, showlegend=False)

    metrics = {
        "total": total,
        "restricted": int(restricted),
        "pct_restricted": pct_restricted,
        "exceeds_20pct": pct_restricted > 20,
        "top_position": top_positions.iloc[0]["Posisi"] if not top_positions.empty else "N/A"
    }
    return fig_pie, fig_bar, metrics


# ─────────────────────────────────────────────────────────────────────────────
# BQ 10 — Perbandingan Median Gaji WFO/WFH/Hybrid per Kategori (Glints_Job)
# ─────────────────────────────────────────────────────────────────────────────

def fig_bq10(df_glints: pd.DataFrame) -> tuple[go.Figure, go.Figure, dict]:
    """
    BQ 10: Median gaji per sistem kerja untuk 10 kategori terbanyak.
    Chart: Grouped Bar Chart (horizontal) + Heatmap.
    Menggunakan 'sistem_kerja_label' (WFO/WFH/Hybrid) dan 'salary_median'.
    Returns: (fig_bar, fig_heat, metrics_dict)
    """
    top10_roles = (
        df_glints[GLINTS_ROLE_COL].value_counts().head(10).index.tolist()
    )
    df_filtered = df_glints[
        df_glints[GLINTS_ROLE_COL].isin(top10_roles) &
        df_glints["salary_median"].notna()
    ]

    pivot = (
        df_filtered.groupby([GLINTS_ROLE_COL, "sistem_kerja_label"])["salary_median"]
        .median()
        .reset_index()
    )
    pivot.columns = [GLINTS_ROLE_COL, "Sistem Kerja", "Median Gaji"]

    color_map = {"WFO": COLOR_WFO, "WFH": COLOR_WFH, "Hybrid": COLOR_HYBRID}

    # Grouped Bar Chart
    fig_bar = px.bar(
        pivot,
        x="Median Gaji",
        y=GLINTS_ROLE_COL,
        color="Sistem Kerja",
        barmode="group",
        orientation="h",
        title="BQ 10 — Median Gaji per Sistem Kerja (Top 10 Kategori Peran)",
        color_discrete_map=color_map,
        labels={"Median Gaji": "Median Gaji (Rp)", GLINTS_ROLE_COL: "Kategori Peran"},
        category_orders={GLINTS_ROLE_COL: top10_roles}
    )
    fig_bar.update_layout(template=TEMPLATE, height=560)

    # Heatmap
    heat_data = pivot.pivot(index=GLINTS_ROLE_COL, columns="Sistem Kerja", values="Median Gaji").fillna(0)

    fig_heat = px.imshow(
        heat_data,
        text_auto=".2s",
        aspect="auto",
        color_continuous_scale="Blues",
        title="BQ 10 — Heatmap Median Gaji (Kategori × Sistem Kerja)"
    )
    fig_heat.update_layout(template=TEMPLATE, height=480)

    # Cari sistem kerja dengan median gaji tertinggi secara overall
    overall_best = pivot.groupby("Sistem Kerja")["Median Gaji"].mean().idxmax()

    metrics = {
        "top10_roles": top10_roles,
        "best_work_system": overall_best
    }
    return fig_bar, fig_heat, metrics
