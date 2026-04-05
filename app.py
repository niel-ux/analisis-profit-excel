import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Analisis Profit",
    layout="wide"
)

# =============================
# Modern Minimal Styling
# =============================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #F9FAFB;
}

/* Main Container */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
    max-width: 1200px;
}

/* Section Title */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 16px;
    color: #111827;
}

/* Modern Glass Card */
.card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

/* Metric */
.metric-title {
    font-size: 14px;
    color: #6B7280;
}

.metric-value {
    font-size: 26px;
    font-weight: 600;
    color: #111827;
}

/* Insight Box */
.insight-box {
    background: #FFFFFF;
    border-left: 4px solid #2563EB;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

# =============================
# Header
# =============================
st.title("Analisis Profit")
st.caption("Dashboard analisis kinerja dan profitabilitas penjualan marketplace")

# =============================
# Sidebar Configuration
# =============================
with st.sidebar:
    st.header("Pengaturan Data")

    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

    st.markdown("### Parameter Biaya")
    hpp = st.number_input("Harga Pokok Produksi per Produk", min_value=0, value=47500)
    qty_rule = st.number_input("Batas revenue untuk estimasi dua produk", value=95000)

    st.markdown("---")
    st.subheader("Override Revenue")
    use_override = st.toggle("Gunakan revenue manual")
    override_value = 0
    if use_override:
        override_value = st.number_input("Masukkan revenue manual", value=0)

    st.markdown("---")
    st.subheader("Simulasi Harga")
    kenaikan = st.number_input("Kenaikan harga per produk", value=5000)

# =============================
# Processing
# =============================
if uploaded_file:

    with st.spinner("Memproses data..."):
        time.sleep(0.8)
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

    required_columns = ["Total Revenue", "Total settlement amount"]
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Kolom '{col}' tidak ditemukan dalam file.")
            st.stop()

    df["Estimated_Qty"] = df["Total Revenue"].apply(lambda x: 2 if x > qty_rule else 1)

    total_transactions = len(df)
    total_qty = df["Estimated_Qty"].sum()
    total_revenue_asli = df["Total Revenue"].sum()
    total_settlement = df["Total settlement amount"].sum()
    total_fees = df["Total Fees"].sum() if "Total Fees" in df.columns else 0

    total_revenue = override_value if use_override and override_value > 0 else total_revenue_asli

    total_modal = total_qty * hpp
    laba_bersih = total_settlement - total_modal
    margin = (laba_bersih / total_revenue) * 100 if total_revenue != 0 else 0

    # =============================
    # KPI SECTION
    # =============================
    st.markdown("<div class='section-title'>Ringkasan Kinerja</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Total Revenue</div>
            <div class='metric-value'>Rp {total_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Laba Bersih</div>
            <div class='metric-value'>Rp {laba_bersih:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Margin</div>
            <div class='metric-value'>{margin:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>Total Produk Terjual</div>
            <div class='metric-value'>{int(total_qty)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(" ")

    # =============================
    # Chart + Insight
    # =============================
    col_left, col_right = st.columns([2,1])

    with col_left:
        st.markdown("<div class='section-title'>Tren Omzet Harian</div>", unsafe_allow_html=True)

        if "Order created time" in df.columns:
            df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
            df = df.dropna(subset=["Order created time"])
            daily = df.groupby(df["Order created time"].dt.date)["Total Revenue"].sum().reset_index()

            fig = px.line(daily, x="Order created time", y="Total Revenue", markers=True)
            fig.update_layout(
                template="simple_white",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'>Insight Otomatis</div>", unsafe_allow_html=True)

        insights = []

        if margin < 20:
            insights.append("Margin keuntungan berada pada tingkat rendah. Evaluasi harga atau efisiensi biaya diperlukan.")
        elif margin > 40:
            insights.append("Margin keuntungan berada pada tingkat sangat sehat dan menunjukkan profitabilitas kuat.")

        if total_revenue > 0:
            fee_ratio = abs(total_fees) / total_revenue * 100
            if fee_ratio > 15:
                insights.append("Proporsi biaya marketplace terhadap revenue tergolong tinggi dan perlu dioptimalkan.")

        if total_qty > total_transactions * 1.3:
            insights.append("Terdapat kecenderungan pembelian lebih dari satu produk per transaksi. Strategi bundling dapat dipertimbangkan.")

        if laba_bersih < 0:
            insights.append("Kondisi usaha saat ini mengalami kerugian dan memerlukan evaluasi struktur biaya.")

        if insights:
            for item in insights:
                st.markdown(f"<div class='insight-box'>{item}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='insight-box'>Kinerja usaha berada dalam kondisi stabil.</div>", unsafe_allow_html=True)

    st.markdown(" ")

    # =============================
    # Price Simulation
    # =============================
    st.markdown("<div class='section-title'>Simulasi Kenaikan Harga</div>", unsafe_allow_html=True)

    if kenaikan > 0:

        tambahan_revenue = total_qty * kenaikan
        revenue_baru = total_revenue + tambahan_revenue

        settlement_ratio = total_settlement / total_revenue_asli if total_revenue_asli != 0 else 0
        settlement_baru = revenue_baru * settlement_ratio

        laba_baru = settlement_baru - total_modal
        margin_baru = (laba_baru / revenue_baru) * 100 if revenue_baru != 0 else 0

        colA, colB, colC = st.columns(3)

        colA.metric("Revenue Baru", f"Rp {revenue_baru:,.0f}")
        colB.metric("Laba Bersih Baru", f"Rp {laba_baru:,.0f}")
        colC.metric("Margin Baru", f"{margin_baru:.2f}%")