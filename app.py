import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Marketplace Profit Analyzer",
    layout="wide"
)

# =============================
# Minimal Liquid Glass Styling
# =============================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.glass {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.4);
    box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# Header
# =============================
st.title("Marketplace Profit Analyzer")
st.caption("Dashboard analisis profitabilitas penjualan marketplace")

# =============================
# Sidebar Configuration
# =============================
with st.sidebar:
    st.header("Pengaturan")

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
        time.sleep(0.8)
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

    if "Total Revenue" not in df.columns or "Total settlement amount" not in df.columns:
        st.error("Kolom 'Total Revenue' atau 'Total settlement amount' tidak ditemukan.")
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
    # KPI UTAMA
    # =============================
    st.markdown("<div class='section-title'>Ringkasan Kinerja</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"Rp {total_revenue:,.0f}")
    col2.metric("Laba Bersih", f"Rp {laba_bersih:,.0f}")
    col3.metric("Margin", f"{margin:.2f}%")

    # KPI Pendukung
    col4, col5, col6 = st.columns(3)
    col4.metric("Total Produk Terjual", int(total_qty))
    col5.metric("Total Biaya Marketplace", f"Rp {abs(total_fees):,.0f}")
    col6.metric("Total Modal", f"Rp {total_modal:,.0f}")

    st.markdown(" ")

    # =============================
    # Grafik dan Insight
    # =============================
    col_left, col_right = st.columns([2,1])

    with col_left:
        st.markdown("<div class='section-title'>Grafik Omzet Harian</div>", unsafe_allow_html=True)

        if "Order created time" in df.columns:
            df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
            df = df.dropna(subset=["Order created time"])

            daily = df.groupby(df["Order created time"].dt.date)["Total Revenue"].sum().reset_index()

            fig = px.line(
                daily,
                x="Order created time",
                y="Total Revenue",
                markers=True
            )
            fig.update_layout(template="simple_white", margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'>Analisis Otomatis</div>", unsafe_allow_html=True)

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
            insights.append("Kondisi usaha saat ini mengalami kerugian. Evaluasi struktur harga dan biaya disarankan.")

        if insights:
            for item in insights:
                st.write("- " + item)
        else:
            st.write("Kinerja usaha berada dalam kondisi stabil.")

    st.markdown(" ")

    # =============================
    # Simulasi Harga
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