import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Marketplace Profit Analyzer",
    layout="wide"
)

# =============================
# Styling Bersih dan Modern
# =============================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
    max-width: 1200px;
}

.section {
    margin-top: 2.5rem;
    margin-bottom: 2rem;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 1rem;
}

.kpi-primary {
    font-size: 26px;
    font-weight: 600;
}

.kpi-secondary {
    font-size: 18px;
    font-weight: 500;
    color: #555;
}

.insight-box {
    padding: 18px;
    border-radius: 12px;
    background: #f8f9fb;
    border: 1px solid #e6e8ec;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# Header
# =============================
st.title("Marketplace Profit Analyzer")
st.caption("Analisis kinerja dan profitabilitas penjualan marketplace")

# =============================
# Sidebar
# =============================
with st.sidebar:
    st.header("Konfigurasi")

    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

    hpp = st.number_input("Harga Pokok Produksi per Produk", min_value=0, value=47500)
    qty_rule = st.number_input("Batas revenue untuk estimasi dua produk", value=95000)

    st.markdown("---")
    st.subheader("Penyesuaian Revenue")
    use_override = st.toggle("Gunakan revenue manual")

    override_value = 0
    if use_override:
        override_value = st.number_input("Masukkan revenue manual", value=0)

    st.markdown("---")
    st.subheader("Simulasi Harga")
    kenaikan = st.number_input("Kenaikan harga per produk", value=5000)

# =============================
# Data Processing
# =============================
if uploaded_file:

    with st.spinner("Memproses data..."):
        time.sleep(0.6)
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

    required_cols = ["Total Revenue", "Total settlement amount"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Kolom '{col}' tidak ditemukan.")
            st.stop()

    df["Estimated_Qty"] = df["Total Revenue"].apply(lambda x: 2 if x > qty_rule else 1)

    total_transactions = len(df)
    total_qty = df["Estimated_Qty"].sum()

    total_revenue_asli = df["Total Revenue"].sum()
    total_settlement_asli = df["Total settlement amount"].sum()
    total_fees = df["Total Fees"].sum() if "Total Fees" in df.columns else 0

    if use_override and override_value > 0:
        ratio = total_settlement_asli / total_revenue_asli if total_revenue_asli != 0 else 0
        total_revenue = override_value
        total_settlement = total_revenue * ratio
    else:
        total_revenue = total_revenue_asli
        total_settlement = total_settlement_asli

    total_modal = total_qty * hpp
    laba_bersih = total_settlement - total_modal
    margin = (laba_bersih / total_revenue) * 100 if total_revenue != 0 else 0

    # =============================
    # KPI UTAMA (Lebih Dominan)
    # =============================
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Ringkasan Utama</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='kpi-primary'>Rp {total_revenue:,.0f}</div>", unsafe_allow_html=True)
    col1.caption("Total Revenue")

    col2.markdown(f"<div class='kpi-primary'>Rp {laba_bersih:,.0f}</div>", unsafe_allow_html=True)
    col2.caption("Laba Bersih")

    col3.markdown(f"<div class='kpi-primary'>{margin:.2f}%</div>", unsafe_allow_html=True)
    col3.caption("Margin")

    st.markdown("</div>", unsafe_allow_html=True)

    # =============================
    # KPI Pendukung
    # =============================
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Detail Operasional</div>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    col4.markdown(f"<div class='kpi-secondary'>{int(total_qty)}</div>", unsafe_allow_html=True)
    col4.caption("Total Produk Terjual")

    col5.markdown(f"<div class='kpi-secondary'>Rp {abs(total_fees):,.0f}</div>", unsafe_allow_html=True)
    col5.caption("Total Biaya Marketplace")

    col6.markdown(f"<div class='kpi-secondary'>Rp {total_modal:,.0f}</div>", unsafe_allow_html=True)
    col6.caption("Total Modal")

    st.markdown("</div>", unsafe_allow_html=True)

    # =============================
    # Grafik (Full Width Lebih Nyaman)
    # =============================
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Grafik Omzet Harian</div>", unsafe_allow_html=True)

    if "Order created time" in df.columns:
        df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
        df = df.dropna(subset=["Order created time"])

        if not df.empty:
            daily = df.groupby(df["Order created time"].dt.date)["Total Revenue"].sum().reset_index()

            fig = px.line(
                daily,
                x="Order created time",
                y="Total Revenue",
                markers=True
            )
            fig.update_layout(template="simple_white")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =============================
    # Insight (Lebih Rapi Dibaca)
    # =============================
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Analisis Otomatis</div>", unsafe_allow_html=True)

    insights = []

    if margin < 20:
        insights.append("Margin keuntungan berada pada tingkat rendah dan memerlukan evaluasi.")
    if laba_bersih < 0:
        insights.append("Kinerja usaha menunjukkan kondisi kerugian.")
    if total_revenue > 0:
        fee_ratio = abs(total_fees) / total_revenue * 100
        if fee_ratio > 15:
            insights.append("Proporsi biaya marketplace terhadap revenue tergolong tinggi.")
    if total_qty > total_transactions * 1.3:
        insights.append("Terdapat kecenderungan pembelian lebih dari satu produk per transaksi.")

    if insights:
        for item in insights:
            st.markdown(f"<div class='insight-box'>{item}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='insight-box'>Tidak ditemukan anomali signifikan pada kinerja usaha.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =============================
    # Simulasi
    # =============================
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Simulasi Kenaikan Harga</div>", unsafe_allow_html=True)

    if kenaikan > 0:

        tambahan_revenue = total_qty * kenaikan
        revenue_baru = total_revenue + tambahan_revenue
        settlement_ratio = total_settlement / total_revenue if total_revenue != 0 else 0
        settlement_baru = revenue_baru * settlement_ratio

        laba_baru = settlement_baru - total_modal
        margin_baru = (laba_baru / revenue_baru) * 100 if revenue_baru != 0 else 0

        colA, colB, colC = st.columns(3)

        colA.markdown(f"<div class='kpi-secondary'>Rp {revenue_baru:,.0f}</div>", unsafe_allow_html=True)
        colA.caption("Revenue Baru")

        colB.markdown(f"<div class='kpi-secondary'>Rp {laba_baru:,.0f}</div>", unsafe_allow_html=True)
        colB.caption("Laba Bersih Baru")

        colC.markdown(f"<div class='kpi-secondary'>{margin_baru:.2f}%</div>", unsafe_allow_html=True)
        colC.caption("Margin Baru")

    st.markdown("</div>", unsafe_allow_html=True)