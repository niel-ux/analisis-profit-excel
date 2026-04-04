import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# KONFIGURASI HALAMAN
# ==============================

st.set_page_config(
    page_title="Analisis Profit Marketplace",
    layout="wide"
)

# ==============================
# STYLE LIQUID GLASS MINIMAL
# ==============================

st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

h1, h2, h3, h4, label, p {
    color: #f1f5f9 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

div[data-testid="stMetric"],
div[data-testid="stFileUploader"],
div[data-testid="stNumberInput"],
div[data-testid="stPlotlyChart"] {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    padding: 18px;
}

hr {
    border: 0.5px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================

st.title("Analisis Profit Marketplace")
st.caption("Dashboard analisis kinerja penjualan dan simulasi harga berbasis data transaksi.")

# ==============================
# UPLOAD FILE
# ==============================

uploaded_file = st.file_uploader("Unggah file laporan transaksi (format Excel)", type=["xlsx"])

if uploaded_file:

    with st.spinner("Memproses data transaksi..."):

        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        required_columns = ["Total Revenue", "Total settlement amount"]

        for col in required_columns:
            if col not in df.columns:
                st.error(f"Kolom '{col}' tidak ditemukan dalam file.")
                st.stop()

        df["Estimasi_Jumlah"] = df["Total Revenue"].apply(lambda x: 2 if x > 95000 else 1)

        total_transaksi = len(df)
        total_qty = df["Estimasi_Jumlah"].sum()
        total_revenue = df["Total Revenue"].sum()
        total_settlement = df["Total settlement amount"].sum()
        total_fees = df["Total Fees"].sum() if "Total Fees" in df.columns else 0

        hpp_default = 47500

    # ==============================
    # PENGATURAN
    # ==============================

    st.subheader("Pengaturan")

    col1, col2 = st.columns(2)
    hpp = col1.number_input("Harga Pokok Penjualan per Produk", value=hpp_default)
    kenaikan_simulasi = col2.number_input("Simulasi Kenaikan Harga per Produk", value=5000)

    total_modal = total_qty * hpp
    laba_bersih = total_settlement - total_modal
    margin = (laba_bersih / total_revenue * 100) if total_revenue != 0 else 0

    st.divider()

    # ==============================
    # RINGKASAN KINERJA
    # ==============================

    st.subheader("Ringkasan Kinerja")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Omzet", f"Rp {total_revenue:,.0f}")
    col2.metric("Dana Diterima", f"Rp {total_settlement:,.0f}")
    col3.metric("Total Modal", f"Rp {total_modal:,.0f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Jumlah Produk Terjual", int(total_qty))
    col5.metric("Total Biaya Marketplace", f"Rp {abs(total_fees):,.0f}")
    col6.metric("Laba Bersih", f"Rp {laba_bersih:,.0f}", f"{margin:.2f}%")

    st.divider()

    # ==============================
    # GRAFIK HARIAN
    # ==============================

    if "Order created time" in df.columns:

        df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
        df = df.dropna(subset=["Order created time"])

        data_harian = (
            df.groupby(df["Order created time"].dt.date)["Total Revenue"]
            .sum()
            .reset_index()
        )

        st.subheader("Grafik Omzet Harian")

        fig = px.line(
            data_harian,
            x="Order created time",
            y="Total Revenue",
            markers=True
        )

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f1f5f9")
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==============================
    # INSIGHT PROFESIONAL
    # ==============================

    st.subheader("Insight Analitis")

    insights = []

    if margin < 20:
        insights.append("Margin keuntungan berada di bawah 20 persen. Disarankan melakukan evaluasi harga jual atau efisiensi biaya operasional.")
    elif margin > 40:
        insights.append("Margin keuntungan berada pada tingkat yang sangat baik dan menunjukkan efisiensi model bisnis.")

    if total_fees != 0 and total_revenue != 0:
        rasio_fee = abs(total_fees) / total_revenue * 100
        if rasio_fee > 15:
            insights.append("Proporsi biaya marketplace melebihi 15 persen dari total omzet. Optimalisasi strategi promosi perlu dipertimbangkan.")

    if laba_bersih < 0:
        insights.append("Usaha berada dalam kondisi rugi. Struktur harga dan biaya perlu ditinjau ulang secara menyeluruh.")

    if total_qty > total_transaksi * 1.3:
        insights.append("Terdapat kecenderungan pembelian lebih dari satu unit per transaksi. Strategi bundling dapat meningkatkan nilai transaksi rata-rata.")

    if insights:
        for item in insights:
            st.write(f"- {item}")
    else:
        st.write("Kinerja usaha berada dalam kondisi stabil berdasarkan data yang dianalisis.")

    st.divider()

    # ==============================
    # SIMULASI KENAIKAN HARGA
    # ==============================

    st.subheader("Simulasi Penyesuaian Harga")

    if kenaikan_simulasi > 0 and total_qty > 0:

        tambahan_revenue = total_qty * kenaikan_simulasi
        revenue_baru = total_revenue + tambahan_revenue

        rasio_settlement = total_settlement / total_revenue if total_revenue != 0 else 0
        settlement_baru = revenue_baru * rasio_settlement

        laba_baru = settlement_baru - total_modal
        margin_baru = (laba_baru / revenue_baru * 100) if revenue_baru != 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Omzet Setelah Penyesuaian", f"Rp {revenue_baru:,.0f}")
        col2.metric("Laba Bersih Setelah Penyesuaian", f"Rp {laba_baru:,.0f}")
        col3.metric("Margin Setelah Penyesuaian", f"{margin_baru:.2f}%")

        selisih = laba_baru - laba_bersih

        if selisih > 0:
            st.write(f"Potensi peningkatan laba sebesar Rp {selisih:,.0f} berdasarkan simulasi kenaikan harga.")
        else:
            st.write("Simulasi penyesuaian harga belum menunjukkan peningkatan laba yang signifikan.")