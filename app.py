import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(
    page_title="Profit Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# Styling — Warm Minimal Aesthetic
# Palette: Cream background, warm slate text, sage green accent
# Font: DM Sans (body) + DM Serif Display (headers)
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #F5F0EB;
    color: #2C2C2C;
}

.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem;
    max-width: 1180px;
}

section[data-testid="stSidebar"] {
    background-color: #EDEAE5;
    border-right: 1px solid #DDD8D0;
}

section[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
}

.dash-header { margin-bottom: 2rem; }

.dash-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1A1A1A;
    margin: 0;
    line-height: 1.2;
}

.dash-subtitle {
    font-size: 0.875rem;
    color: #8A8078;
    margin-top: 4px;
    font-weight: 400;
}

.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9E9488;
    margin-bottom: 12px;
}

.kpi-card {
    background: #FDFAF7;
    border: 1px solid #E5DFD8;
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #7DA68A;
    border-radius: 14px 14px 0 0;
}

.kpi-card.accent-red::before  { background: #C97B6A; }
.kpi-card.accent-blue::before { background: #6A8BAD; }
.kpi-card.accent-gold::before { background: #C4A35A; }

.kpi-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #9E9488;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}

.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #1A1A1A;
    line-height: 1;
}

.kpi-sub {
    font-size: 0.72rem;
    color: #B0A89E;
    margin-top: 5px;
}

.insight-card {
    background: #FDFAF7;
    border: 1px solid #E5DFD8;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-size: 0.82rem;
    color: #4A4540;
    line-height: 1.6;
    display: flex;
    gap: 10px;
    align-items: flex-start;
}

.insight-icon {
    font-size: 1rem;
    margin-top: 1px;
    flex-shrink: 0;
}

.disclaimer {
    background: #FEF9EC;
    border: 1px solid #E8D99A;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.75rem;
    color: #7A6A2A;
    margin-top: 1rem;
}

.soft-divider {
    border: none;
    border-top: 1px solid #E5DFD8;
    margin: 1.8rem 0;
}

.sim-row {
    background: #FDFAF7;
    border: 1px solid #E5DFD8;
    border-radius: 14px;
    padding: 18px 22px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# Sidebar
# =============================
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")
    st.markdown("---")

    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

    st.markdown("**Parameter Biaya**")
    hpp = st.number_input("HPP per produk (Rp)", min_value=1, value=47500, step=500)

    st.markdown("---")
    st.markdown("**Override Revenue**")
    use_override = st.toggle("Gunakan revenue manual")
    override_value = 0
    if use_override:
        override_value = st.number_input("Revenue manual (Rp)", value=0, step=1000)

    st.markdown("---")
    st.markdown("**Simulasi Harga**")
    kenaikan = st.number_input("Kenaikan harga per produk (Rp)", value=5000, step=500)

# =============================
# Header
# =============================
st.markdown("""
<div class='dash-header'>
    <div class='dash-title'>Profit Dashboard</div>
    <div class='dash-subtitle'>Analisis kinerja & profitabilitas penjualan marketplace</div>
</div>
""", unsafe_allow_html=True)

# =============================
# Main Content
# =============================
if not uploaded_file:
    st.info("Unggah file Excel dari sidebar untuk memulai analisis.")
    st.stop()

with st.spinner("Memproses data..."):
    time.sleep(0.5)
    df = pd.read_excel(uploaded_file, sheet_name="Order details")
    df.columns = df.columns.str.strip()

required_columns = ["Total Revenue", "Total settlement amount"]
for col in required_columns:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan dalam file.")
        st.stop()

# Validasi numerik
df["Total Revenue"] = pd.to_numeric(df["Total Revenue"], errors="coerce").fillna(0)
df["Total settlement amount"] = pd.to_numeric(df["Total settlement amount"], errors="coerce").fillna(0)
df["Total Fees"] = pd.to_numeric(df["Total Fees"], errors="coerce").fillna(0) if "Total Fees" in df.columns else 0

# Filter transaksi positif saja (exclude refund/adjustment negatif)
df = df[df["Total Revenue"] > 0].copy()

# =========================================================
# PERBAIKAN 1: Estimasi Qty
# round(revenue / hpp), bukan threshold biner 1 atau 2
# =========================================================
df["Estimated_Qty"] = (df["Total Revenue"] / hpp).round().astype(int).clip(lower=1)

total_transactions = len(df)
total_qty = int(df["Estimated_Qty"].sum())
total_revenue_asli = df["Total Revenue"].sum()
total_settlement = df["Total settlement amount"].sum()
total_fees = abs(df["Total Fees"].sum())

# Revenue aktif (override atau asli)
total_revenue = override_value if use_override and override_value > 0 else total_revenue_asli
total_modal = total_qty * hpp

# =========================================================
# PERBAIKAN 2: Margin konsisten dari sisi revenue
# laba = revenue - modal - fees → margin = laba / revenue
# =========================================================
laba_bersih = total_revenue - total_modal - total_fees
margin = (laba_bersih / total_revenue) * 100 if total_revenue != 0 else 0

# =============================
# KPI Cards
# =============================
st.markdown("<div class='section-label'>Ringkasan Kinerja</div>", unsafe_allow_html=True)

def fmt(val):
    if abs(val) >= 1_000_000:
        return f"Rp {val/1_000_000:.1f}jt"
    return f"Rp {val:,.0f}"

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class='kpi-card accent-blue'>
        <div class='kpi-label'>Total Revenue</div>
        <div class='kpi-value'>{fmt(total_revenue)}</div>
        <div class='kpi-sub'>{total_transactions} transaksi</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Total Settlement</div>
        <div class='kpi-value'>{fmt(total_settlement)}</div>
        <div class='kpi-sub'>Uang diterima bersih</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='kpi-card accent-gold'>
        <div class='kpi-label'>Total Modal (est.)</div>
        <div class='kpi-value'>{fmt(total_modal)}</div>
        <div class='kpi-sub'>~{total_qty} produk × Rp {hpp:,}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    accent = "accent-red" if laba_bersih < 0 else ""
    st.markdown(f"""
    <div class='kpi-card {accent}'>
        <div class='kpi-label'>Laba Bersih (est.)</div>
        <div class='kpi-value'>{fmt(laba_bersih)}</div>
        <div class='kpi-sub'>Setelah modal & biaya</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Margin (est.)</div>
        <div class='kpi-value'>{margin:.1f}%</div>
        <div class='kpi-sub'>Laba / Revenue</div>
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div class='disclaimer'>
    ⚠️ <b>Catatan:</b> Modal, laba, dan margin dihitung berdasarkan estimasi qty (revenue ÷ HPP).
    Akurasi terbaik jika mayoritas produk memiliki HPP yang sama.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# =============================
# Chart + Insight
# =============================
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("<div class='section-label'>Tren Omzet Harian</div>", unsafe_allow_html=True)

    if "Order created time" in df.columns:
        df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
        df_clean = df.dropna(subset=["Order created time"])
        daily = df_clean.groupby(df_clean["Order created time"].dt.date)["Total Revenue"].sum().reset_index()
        daily.columns = ["Tanggal", "Revenue"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["Tanggal"],
            y=daily["Revenue"],
            mode="lines+markers",
            line=dict(color="#7DA68A", width=2.5),
            marker=dict(color="#7DA68A", size=5),
            fill="tozeroy",
            fillcolor="rgba(125,166,138,0.08)",
            hovertemplate="<b>%{x}</b><br>Rp %{y:,.0f}<extra></extra>"
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#9E9488"), showline=False),
            yaxis=dict(showgrid=True, gridcolor="#EDE8E1", tickfont=dict(size=11, color="#9E9488"), showline=False),
            height=260
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Kolom 'Order created time' tidak ditemukan.")

with col_right:
    st.markdown("<div class='section-label'>Insight Otomatis</div>", unsafe_allow_html=True)

    insights = []

    if laba_bersih < 0:
        insights.append(("🔴", "Usaha dalam kondisi <b>rugi</b>. Evaluasi struktur biaya atau harga jual segera."))
    elif margin < 15:
        insights.append(("🟡", "Margin rendah (<15%). Pertimbangkan efisiensi biaya atau kenaikan harga."))
    elif margin > 35:
        insights.append(("🟢", "Margin sangat sehat (>35%). Profitabilitas kuat."))
    else:
        insights.append(("🟢", "Margin dalam rentang normal. Kinerja usaha stabil."))

    if total_revenue > 0:
        fee_ratio = total_fees / total_revenue * 100
        if fee_ratio > 15:
            insights.append(("⚠️", f"Biaya platform {fee_ratio:.1f}% dari revenue — tergolong tinggi."))
        else:
            insights.append(("✅", f"Biaya platform {fee_ratio:.1f}% dari revenue — masih wajar."))

    avg_revenue = total_revenue / total_transactions if total_transactions else 0
    insights.append(("📦", f"Rata-rata revenue per transaksi <b>Rp {avg_revenue:,.0f}</b>."))

    settlement_ratio = (total_settlement / total_revenue * 100) if total_revenue else 0
    insights.append(("💳", f"Settlement rate <b>{settlement_ratio:.1f}%</b> dari revenue."))

    for icon, text in insights:
        st.markdown(f"""
        <div class='insight-card'>
            <span class='insight-icon'>{icon}</span>
            <span>{text}</span>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# =============================
# Breakdown Biaya Platform
# =============================
st.markdown("<div class='section-label'>Breakdown Biaya Platform</div>", unsafe_allow_html=True)

fee_cols = [
    "Platform commission fee", "Payment Fee", "Affiliate Commission",
    "Shipping cost", "Shipping cost borne by the platform"
]
fee_data = {}
for col in fee_cols:
    if col in df.columns:
        val = abs(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())
        if val > 0:
            fee_data[col] = val

if fee_data:
    fig2 = go.Figure(go.Bar(
        x=list(fee_data.values()),
        y=list(fee_data.keys()),
        orientation="h",
        marker_color="#7DA68A",
        hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor="#EDE8E1", tickfont=dict(size=11, color="#9E9488")),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#4A4540")),
        height=220
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# =============================
# Simulasi Kenaikan Harga
# =============================
st.markdown("<div class='section-label'>Simulasi Kenaikan Harga</div>", unsafe_allow_html=True)

if kenaikan > 0:
    tambahan_revenue = total_qty * kenaikan
    revenue_baru = total_revenue + tambahan_revenue

    # =========================================================
    # PERBAIKAN 3: Simulasi pakai total_revenue aktif
    # bukan total_revenue_asli yang bisa berbeda saat override aktif
    # =========================================================
    fees_baru = (total_fees / total_revenue) * revenue_baru if total_revenue != 0 else 0
    laba_baru = revenue_baru - total_modal - fees_baru
    margin_baru = (laba_baru / revenue_baru) * 100 if revenue_baru != 0 else 0

    delta_laba = laba_baru - laba_bersih
    delta_margin = margin_baru - margin

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(f"""
        <div class='sim-row'>
            <div class='kpi-label'>Kenaikan Harga</div>
            <div class='kpi-value'>+Rp {kenaikan:,}</div>
            <div class='kpi-sub'>per produk</div>
        </div>""", unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
        <div class='sim-row'>
            <div class='kpi-label'>Revenue Baru</div>
            <div class='kpi-value'>{fmt(revenue_baru)}</div>
            <div class='kpi-sub'>+{fmt(tambahan_revenue)}</div>
        </div>""", unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
        <div class='sim-row'>
            <div class='kpi-label'>Laba Baru (est.)</div>
            <div class='kpi-value'>{fmt(laba_baru)}</div>
            <div class='kpi-sub'>+{fmt(delta_laba)}</div>
        </div>""", unsafe_allow_html=True)

    with s4:
        st.markdown(f"""
        <div class='sim-row'>
            <div class='kpi-label'>Margin Baru (est.)</div>
            <div class='kpi-value'>{margin_baru:.1f}%</div>
            <div class='kpi-sub'>+{delta_margin:.1f}%</div>
        </div>""", unsafe_allow_html=True)