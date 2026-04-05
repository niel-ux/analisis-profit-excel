import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Analisis Excel",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=Mulish:wght@300;400;500;600&display=swap');

/* Reset background */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
    background-color: #F7F4F0 !important;
    font-family: 'Mulish', sans-serif !important;
    color: #2C2C2C;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F0EDE8 !important;
    border-right: 1px solid #E2DDD8 !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    font-family: 'Mulish', sans-serif !important;
    color: #2C2C2C !important;
}

.block-container {
    padding: 2.5rem 3rem 4rem 3rem !important;
    max-width: 1200px;
}

/* Page title */
.page-title {
    font-family: 'Lora', serif;
    font-size: 1.85rem;
    font-weight: 600;
    color: #1C1C1C;
    margin: 0 0 4px 0;
}

.page-sub {
    font-size: 0.84rem;
    color: #AAA;
    margin-bottom: 2.2rem;
    font-weight: 400;
}

/* Section label */
.sec-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #BBBBBB;
    margin-bottom: 12px;
    margin-top: 2px;
}

/* KPI card */
.kpi {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 12px;
    padding: 20px 20px 16px 20px;
    position: relative;
    overflow: hidden;
}

.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #C5BFB8;
    border-radius: 12px 12px 0 0;
}

.kpi.green::before { background: #6B9E78; }
.kpi.blue::before  { background: #6A8BAD; }
.kpi.gold::before  { background: #B89A5A; }
.kpi.red::before   { background: #B85A5A; }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #BBBBBB;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.kpi-val {
    font-family: 'Lora', serif;
    font-size: 1.45rem;
    color: #1C1C1C;
    line-height: 1.1;
}

.kpi-sub {
    font-size: 0.71rem;
    color: #C5BFB8;
    margin-top: 6px;
}

/* Insight card */
.ins-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 10px;
    padding: 13px 16px;
    margin-bottom: 9px;
    font-size: 0.82rem;
    color: #4A4540;
    line-height: 1.65;
}

/* Disclaimer */
.disclaimer {
    background: #FFFBEF;
    border: 1px solid #E8D98A;
    border-radius: 9px;
    padding: 10px 14px;
    font-size: 0.76rem;
    color: #7A6A2A;
    margin-top: 1rem;
}

/* Notice */
.notice {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 10px;
    padding: 16px 20px;
    font-size: 0.84rem;
    color: #888;
    text-align: center;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #E8E4DF;
    margin: 2rem 0;
}

/* Sim card */
.sim-card {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 12px;
    padding: 18px 20px;
}
</style>
""", unsafe_allow_html=True)

# ============================
# Sidebar
# ============================
with st.sidebar:
    st.markdown("### Pengaturan")
    st.divider()

    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])
    st.divider()

    st.markdown("**Harga Pokok Produksi**")
    hpp = st.number_input("HPP per produk (Rp)", min_value=1, value=47500, step=500)
    st.divider()

    st.markdown("**Override Revenue**")
    use_override = st.toggle("Gunakan revenue manual")
    override_value = 0
    if use_override:
        override_value = st.number_input("Revenue manual (Rp)", value=0, step=1000)
    st.divider()

    st.markdown("**Simulasi Harga**")
    kenaikan = st.number_input("Kenaikan harga per produk (Rp)", value=5000, step=500)

# ============================
# Header
# ============================
st.markdown("<div class='page-title'>Analisis Excel</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Analisis kinerja dan profitabilitas penjualan marketplace</div>", unsafe_allow_html=True)

# ============================
# Belum upload
# ============================
if not uploaded_file:
    st.markdown("<div class='notice'>Unggah file Excel dari sidebar untuk memulai analisis.</div>", unsafe_allow_html=True)
    st.stop()

# ============================
# Load data
# ============================
with st.spinner("Memproses data..."):
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Order details")
    except Exception:
        df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

for col in ["Total Revenue", "Total settlement amount"]:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan dalam file.")
        st.stop()

# Validasi numerik
df["Total Revenue"]            = pd.to_numeric(df["Total Revenue"], errors="coerce").fillna(0)
df["Total settlement amount"]  = pd.to_numeric(df["Total settlement amount"], errors="coerce").fillna(0)
df["Total Fees"]               = pd.to_numeric(df.get("Total Fees", 0), errors="coerce").fillna(0) if "Total Fees" in df.columns else pd.Series([0]*len(df))

# Filter transaksi positif saja
df = df[df["Total Revenue"] > 0].copy()

# ============================
# Kalkulasi
# ============================

# Perbaikan 1: estimasi qty pakai round(revenue / hpp), bukan threshold biner
df["Estimated_Qty"] = (df["Total Revenue"] / hpp).round().astype(int).clip(lower=1)

total_transactions = len(df)
total_qty          = int(df["Estimated_Qty"].sum())
total_revenue_asli = df["Total Revenue"].sum()
total_settlement   = df["Total settlement amount"].sum()
total_fees         = abs(df["Total Fees"].sum())

# Perbaikan 3: pakai total_revenue aktif di semua kalkulasi hilir
total_revenue = override_value if use_override and override_value > 0 else total_revenue_asli
total_modal   = total_qty * hpp

# Perbaikan 2: laba dan margin konsisten dari sisi revenue
laba_bersih = total_revenue - total_modal - total_fees
margin      = (laba_bersih / total_revenue * 100) if total_revenue else 0

# Helper format
def fmt(val):
    if abs(val) >= 1_000_000:
        return f"Rp {val/1_000_000:.1f}jt"
    return f"Rp {val:,.0f}"

# ============================
# KPI
# ============================
st.markdown("<div class='sec-label'>Ringkasan Kinerja</div>", unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""<div class='kpi blue'>
        <div class='kpi-label'>Total Revenue</div>
        <div class='kpi-val'>{fmt(total_revenue)}</div>
        <div class='kpi-sub'>{total_transactions} transaksi</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class='kpi'>
        <div class='kpi-label'>Total Settlement</div>
        <div class='kpi-val'>{fmt(total_settlement)}</div>
        <div class='kpi-sub'>Dana diterima</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class='kpi'>
        <div class='kpi-label'>Total Fee</div>
        <div class='kpi-val'>{fmt(total_fees)}</div>
        <div class='kpi-sub'>Biaya platform</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class='kpi gold'>
        <div class='kpi-label'>Total Modal</div>
        <div class='kpi-val'>{fmt(total_modal)}</div>
        <div class='kpi-sub'>~{total_qty} produk</div>
    </div>""", unsafe_allow_html=True)

with c5:
    acc = "red" if laba_bersih < 0 else "green"
    st.markdown(f"""<div class='kpi {acc}'>
        <div class='kpi-label'>Laba Bersih</div>
        <div class='kpi-val'>{fmt(laba_bersih)}</div>
        <div class='kpi-sub'>Estimasi</div>
    </div>""", unsafe_allow_html=True)

with c6:
    st.markdown(f"""<div class='kpi'>
        <div class='kpi-label'>Margin</div>
        <div class='kpi-val'>{margin:.1f}%</div>
        <div class='kpi-sub'>Laba / Revenue</div>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class='disclaimer'>
    Catatan: Modal, laba, dan margin adalah estimasi berdasarkan revenue dibagi HPP.
    Akurasi terbaik jika mayoritas produk memiliki HPP yang sama.
</div>""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ============================
# Chart + Insight
# ============================
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("<div class='sec-label'>Tren Omzet Harian</div>", unsafe_allow_html=True)

    if "Order created time" in df.columns:
        df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
        df_clean = df.dropna(subset=["Order created time"])
        daily = df_clean.groupby(df_clean["Order created time"].dt.date)["Total Revenue"].sum().reset_index()
        daily.columns = ["Tanggal", "Revenue"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["Tanggal"], y=daily["Revenue"],
            mode="lines+markers",
            line=dict(color="#6B9E78", width=2),
            marker=dict(color="#6B9E78", size=5),
            fill="tozeroy",
            fillcolor="rgba(107,158,120,0.07)",
            hovertemplate="<b>%{x}</b><br>Rp %{y:,.0f}<extra></extra>"
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=8, b=0),
            height=250,
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#BBBBBB"), showline=False),
            yaxis=dict(showgrid=True, gridcolor="#EEEBE7", tickfont=dict(size=11, color="#BBBBBB"), showline=False),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Kolom 'Order created time' tidak ditemukan.")

with col_right:
    st.markdown("<div class='sec-label'>Insight Otomatis</div>", unsafe_allow_html=True)

    insights = []

    if laba_bersih < 0:
        insights.append("Usaha dalam kondisi rugi. Evaluasi harga jual atau struktur biaya segera.")
    elif margin < 15:
        insights.append(f"Margin {margin:.1f}% tergolong rendah. Pertimbangkan kenaikan harga atau efisiensi biaya.")
    elif margin > 35:
        insights.append(f"Margin {margin:.1f}% sangat sehat. Profitabilitas dalam kondisi kuat.")
    else:
        insights.append(f"Margin {margin:.1f}% dalam rentang normal. Kinerja usaha stabil.")

    if total_revenue > 0:
        fee_ratio = total_fees / total_revenue * 100
        if fee_ratio > 15:
            insights.append(f"Biaya platform mencapai {fee_ratio:.1f}% dari revenue. Cek struktur komisi dan iklan.")
        else:
            insights.append(f"Biaya platform {fee_ratio:.1f}% dari revenue, masih dalam batas wajar.")

    avg_rev = total_revenue / total_transactions if total_transactions else 0
    insights.append(f"Rata-rata revenue per transaksi Rp {avg_rev:,.0f}.")

    if "Order created time" in df.columns and len(daily) > 1:
        daily_avg = daily["Revenue"].mean()
        last_day  = daily["Revenue"].iloc[-1]
        if last_day > daily_avg:
            insights.append("Omzet hari terakhir berada di atas rata-rata harian.")
        else:
            insights.append("Omzet hari terakhir berada di bawah rata-rata harian.")

    if total_qty > 0:
        profit_per_item = laba_bersih / total_qty
        if profit_per_item < 10000:
            insights.append(f"Laba per produk hanya Rp {profit_per_item:,.0f}. Pertimbangkan revisi harga jual.")

    for text in insights:
        st.markdown(f"<div class='ins-card'>{text}</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ============================
# Fee Breakdown
# ============================
st.markdown("<div class='sec-label'>Breakdown Biaya Platform</div>", unsafe_allow_html=True)

fee_cols = ["Platform commission fee", "Payment Fee", "Affiliate Commission", "GMV Max ad fee",
            "Shipping cost", "Shipping cost borne by the platform"]
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
        marker_color="#6B9E78",
        hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=8, b=0),
        height=210,
        xaxis=dict(showgrid=True, gridcolor="#EEEBE7", tickfont=dict(size=11, color="#BBBBBB")),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#555")),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ============================
# Simulasi Kenaikan Harga
# ============================
st.markdown("<div class='sec-label'>Simulasi Kenaikan Harga</div>", unsafe_allow_html=True)

if kenaikan > 0:
    tambahan_revenue = total_qty * kenaikan
    revenue_baru     = total_revenue + tambahan_revenue

    # Perbaikan 3: fees diskala proporsional terhadap revenue aktif
    fees_baru    = (total_fees / total_revenue) * revenue_baru if total_revenue else 0
    laba_baru    = revenue_baru - total_modal - fees_baru
    margin_baru  = (laba_baru / revenue_baru * 100) if revenue_baru else 0
    delta_laba   = laba_baru - laba_bersih
    delta_margin = margin_baru - margin

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(f"""<div class='sim-card'>
            <div class='kpi-label'>Kenaikan Harga</div>
            <div class='kpi-val'>+Rp {kenaikan:,}</div>
            <div class='kpi-sub'>per produk</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class='sim-card'>
            <div class='kpi-label'>Revenue Baru</div>
            <div class='kpi-val'>{fmt(revenue_baru)}</div>
            <div class='kpi-sub'>+{fmt(tambahan_revenue)}</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class='sim-card'>
            <div class='kpi-label'>Laba Baru</div>
            <div class='kpi-val'>{fmt(laba_baru)}</div>
            <div class='kpi-sub'>+{fmt(delta_laba)}</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class='sim-card'>
            <div class='kpi-label'>Margin Baru</div>
            <div class='kpi-val'>{margin_baru:.1f}%</div>
            <div class='kpi-sub'>+{delta_margin:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    if delta_laba > 0:
        st.markdown(f"<div class='ins-card'>Jika harga dinaikkan Rp {kenaikan:,} per produk, estimasi laba bertambah {fmt(delta_laba)}.</div>", unsafe_allow_html=True)