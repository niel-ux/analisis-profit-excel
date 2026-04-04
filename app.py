import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Marketplace Profit Analyzer", layout="wide")

st.title("📊 Marketplace Profit Analyzer v2")
st.markdown("Analisa laba bersih marketplace dengan tampilan lebih profesional.")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    if "Total Revenue" not in df.columns or "Total settlement amount" not in df.columns:
        st.error("Kolom 'Total Revenue' atau 'Total settlement amount' tidak ditemukan.")
        st.stop()

    st.subheader("⚙ Pengaturan")

    colA, colB = st.columns(2)
    hpp = colA.number_input("HPP per produk", min_value=0, value=47500)
    qty_rule = colB.number_input("Jika revenue > berapa dianggap 2 pcs?", value=95000)

    # Estimasi Qty
    df["Estimated_Qty"] = df["Total Revenue"].apply(lambda x: 2 if x > qty_rule else 1)

    total_transactions = len(df)
    total_qty = df["Estimated_Qty"].sum()
    total_revenue = df["Total Revenue"].sum()
    total_settlement = df["Total settlement amount"].sum()
    total_fees = df["Total Fees"].sum() if "Total Fees" in df.columns else 0

    total_modal = total_qty * hpp
    laba_bersih = total_settlement - total_modal
    margin = (laba_bersih / total_revenue) * 100 if total_revenue != 0 else 0

    st.divider()

    # === SUMMARY BOX ===
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Omzet", f"Rp {total_revenue:,.0f}")
    col2.metric("Dana Diterima", f"Rp {total_settlement:,.0f}")
    col3.metric("Total Modal", f"Rp {total_modal:,.0f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Produk Terjual", int(total_qty))
    col5.metric("Total Fee Marketplace", f"Rp {abs(total_fees):,.0f}")

    if laba_bersih >= 0:
        col6.metric("Laba Bersih", f"Rp {laba_bersih:,.0f}", f"{margin:.2f}%")
    else:
        col6.metric("Rugi Bersih", f"Rp {laba_bersih:,.0f}", f"{margin:.2f}%")

    st.divider()

    # === GRAFIK HARIAN ===
    if "Order created time" in df.columns:
        df["Order created time"] = pd.to_datetime(df["Order created time"], errors="coerce")
        df = df.dropna(subset=["Order created time"])

        daily = df.groupby(df["Order created time"].dt.date)["Total Revenue"].sum().reset_index()

        st.subheader("📈 Grafik Omzet Harian")
        fig = px.line(daily, x="Order created time", y="Total Revenue",
                      markers=True, title="Omzet per Hari")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # === FEE BREAKDOWN ===
    st.subheader("💸 Breakdown Fee")

    fee_columns = [
        "Platform commission fee",
        "Payment Fee",
        "Affiliate Commission",
        "GMV Max ad fee"
    ]

    fee_data = {}
    for col in fee_columns:
        if col in df.columns:
            fee_data[col] = abs(df[col].sum())

    if fee_data:
        fee_df = pd.DataFrame(list(fee_data.items()), columns=["Jenis Fee", "Total"])
        fig2 = px.pie(fee_df, names="Jenis Fee", values="Total",
                      title="Distribusi Fee Marketplace")
        st.plotly_chart(fig2, use_container_width=True)

    st.success("Analisa selesai 🚀")

# ==============================
# 🤖 AI INSIGHT OTOMATIS
# ==============================

st.divider()
st.subheader("🤖 AI Insight Otomatis")

insights = []

# 1️⃣ Margin Check
if margin < 20:
    insights.append("⚠ Margin keuntungan di bawah 20%. Pertimbangkan menaikkan harga atau menekan biaya.")
elif margin > 40:
    insights.append("🔥 Margin sangat sehat! Produk ini sangat menguntungkan.")

# 2️⃣ Fee Check
if total_fees != 0:
    fee_ratio = abs(total_fees) / total_revenue * 100
    if fee_ratio > 15:
        insights.append("💸 Fee marketplace di atas 15% dari omzet. Pertimbangkan optimasi iklan atau affiliate.")

# 3️⃣ Quantity Behavior
if total_qty > total_transactions * 1.3:
    insights.append("📦 Banyak pembelian 2pcs. Bisa buat bundling resmi untuk meningkatkan AOV.")

# 4️⃣ Loss Detection
if laba_bersih < 0:
    insights.append("🚨 Saat ini bisnis dalam kondisi rugi. Segera evaluasi harga & biaya.")
    
# 5️⃣ Revenue Trend
if "Order created time" in df.columns:
    daily_avg = daily["Total Revenue"].mean()
    last_day = daily["Total Revenue"].iloc[-1]
    if last_day > daily_avg:
        insights.append("📈 Omzet hari terakhir di atas rata-rata. Tren sedang naik.")
    else:
        insights.append("📉 Omzet hari terakhir di bawah rata-rata. Perlu strategi promosi.")

# 6️⃣ Price Suggestion
if total_qty > 0:
    avg_profit_per_item = laba_bersih / total_qty
    if avg_profit_per_item < 10000:
        suggested_price = hpp * 2
        insights.append(f"💡 Rekomendasi harga ideal minimal sekitar Rp {suggested_price:,.0f} untuk profit lebih sehat.")

# Display Insights
if insights:
    for insight in insights:
        st.info(insight)
else:
    st.success("Bisnis dalam kondisi optimal 🚀")

st.success("Analisa selesai 🚀")

# ==============================
# 💰 SIMULASI NAIK HARGA
# ==============================

st.divider()
st.subheader("💰 Simulasi Kenaikan Harga")

kenaikan = st.number_input("Naikkan harga per produk (Rp)", value=5000)

if kenaikan > 0:

    tambahan_revenue = total_qty * kenaikan
    revenue_baru = total_revenue + tambahan_revenue
    settlement_ratio = total_settlement / total_revenue if total_revenue != 0 else 0
    settlement_baru = revenue_baru * settlement_ratio

    laba_baru = settlement_baru - total_modal
    margin_baru = (laba_baru / revenue_baru) * 100 if revenue_baru != 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue Baru", f"Rp {revenue_baru:,.0f}")
    col2.metric("Laba Bersih Baru", f"Rp {laba_baru:,.0f}")
    col3.metric("Margin Baru", f"{margin_baru:.2f}%")

    selisih_laba = laba_baru - laba_bersih

    if selisih_laba > 0:
        st.success(f"🔥 Profit naik Rp {selisih_laba:,.0f} jika harga dinaikkan Rp {kenaikan:,.0f}")
    else:
        st.warning("Tidak ada peningkatan signifikan.")