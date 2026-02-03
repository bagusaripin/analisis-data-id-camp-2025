import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib.ticker as ticker

#Configuration
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

#Definisi Warna Olist
OLIST_TEAL = "#00C2CB"       
OLIST_DARK_BLUE = "#1E3A8A"  
GRAY_TEXT = "#7F7F7F"

#Mengatur Style Mathplotlib
sns.set_style("whitegrid")

#Helper Functions
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return monthly_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_by_seller_df(df):
    agg_dict = {
        "order_id": "nunique",
        "price": "sum"
    }
    if 'review_score' in df.columns:
        agg_dict['review_score'] = 'mean'
        
    by_seller_df = df.groupby("seller_id").agg(agg_dict).reset_index()

    # Rename kolom sesuai logika
    rename_dict = {
        "order_id": "order_count",
        "price": "revenue"
    }
    if 'review_score' in df.columns:
        rename_dict['review_score'] = 'avg_rating'
        
    by_seller_df.rename(columns=rename_dict, inplace=True)
    
    return by_seller_df

#Load Data
all_df = pd.read_csv("all_data_lite.csv")
rfm_df = pd.read_csv("rfm_analysis.csv")
geo_df = pd.read_csv("geolocation_analysis.csv")

#Bersihkan Data Datetime
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

#Sidebar (Filter)
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://storage.googleapis.com/kaggle-organizations/1942/thumbnail.png?r=51")
    st.write("") 
    
    start_date, end_date = st.date_input(
        label='📅 Filter Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    st.caption("Pilih periode waktu analisis.")

#Filter Data Utama Berdasarkan Tanggal
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                 (all_df["order_purchase_timestamp"] <= str(end_date))]
#Filter Status Order
if 'order_status' in main_df.columns:
    main_df = main_df[main_df['order_status'] == 'delivered']

#Menyiapkan Dataframe untuk Visualisasi
monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
by_seller_df = create_by_seller_df(main_df)

#Main Page
#Judul Utama
st.markdown(f"<h1 style='text-align: center; color: {OLIST_DARK_BLUE};'>Olist E-Commerce Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {GRAY_TEXT};'>Executive Summary & Performance Metrics</p>", unsafe_allow_html=True)
st.write("---")

#Chart 1: Monthly Orders Overview
st.subheader('📈 Monthly Orders Trend')

col1, col2 = st.columns(2)
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total Orders", value=f"{total_orders:,}")

with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 6))
#Garis jadi warna Biru Tua (OLIST_DARK_BLUE)
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color=OLIST_DARK_BLUE 
)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=12, rotation=45)
st.pyplot(fig)

st.write("---") 

#Chart 2: Product Performance
st.subheader("🏆 Best & Worst Performing Categories")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

#Warna Bar
colors_best = [OLIST_DARK_BLUE] + ["#D3D3D3"] * 4
colors_worst = ["#D3D3D3"] * 4 + ["#E53E3E"]

#Best Chart
sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors_best, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Revenue (BRL)", fontsize=15)
ax[0].set_title("Top 5 Revenue Generators", loc="center", fontsize=18)
ax[0].tick_params(axis='y', labelsize=15)

#Worst Chart
worst_df = sum_order_items_df.sort_values(by="price", ascending=True).head(5)
sns.barplot(x="price", y="product_category_name_english", data=worst_df, palette=colors_worst, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Revenue (BRL)", fontsize=15)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Bottom 5 Revenue Generators", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)
st.write("---")

#Chart 3: Customer Segment (RFM)
st.subheader("📊 Customer Segmentation Distribution")
st.caption("Distribusi pelanggan berdasarkan analisis RFM (Recency, Frequency, Monetary).")

#Menghitung skor RFM dan membuat Segment
rfm_df['r_score'] = pd.qcut(rfm_df['recency'], q=3, labels=[3, 2, 1]) # 3 = Baru (Bagus)
rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method="first"), q=3, labels=[1, 2, 3]) # 3 = Sering (Bagus)
rfm_df['m_score'] = pd.qcut(rfm_df['monetary'], q=3, labels=[1, 2, 3]) # 3 = Uang Banyak (Bagus)

# Konversi ke string
rfm_df['RFM_Score'] = rfm_df['r_score'].astype(str) + rfm_df['f_score'].astype(str) + rfm_df['m_score'].astype(str)

#Fungsi Segmentasi
def segment_customer(row):
    # Logika segmentasi sederhana (bisa disesuaikan dengan logika notebook kamu)
    if row['RFM_Score'] == '333':
        return 'Best Customers'
    elif row['RFM_Score'] in ['332', '323', '322', '313']:
        return 'Loyal Customers'
    elif row['r_score'] == 3: 
        return 'Active / New'
    elif row['r_score'] == 2: 
        return 'At Risk'
    else: 
        return 'Inactive / Churn'
    
rfm_df['customer_segment'] = rfm_df.apply(segment_customer, axis=1)
segment_order = ['Best Customers', 'Loyal Customers', 'Active / New', 'At Risk', 'Inactive / Churn']

#Visualisasi Segment
col1, col2 = st.columns([1, 2]) 

with col1:
    # Menampilkan Ringkasan Metric
    best_count = rfm_df[rfm_df['customer_segment'] == 'Best Customers'].shape[0]
    churn_count = rfm_df[rfm_df['customer_segment'] == 'Inactive / Churn'].shape[0]
    
    st.metric("Total Customers", f"{rfm_df.shape[0]:,}")
    st.metric("Best Customers", f"{best_count:,}", delta="High Value")
    st.metric("Inactive / Churn", f"{churn_count:,}", delta="- Risk", delta_color="inverse")

with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Warna per segmen
    colors_segment = {
        'Best Customers': OLIST_DARK_BLUE,
        'Loyal Customers': OLIST_TEAL, 
        'Active / New': '#87CEEB',    
        'At Risk': '#FFD700',         
        'Inactive / Churn': '#E53E3E' 
    }
    
    sns.countplot(
        y='customer_segment', 
        data=rfm_df, 
        order=segment_order, 
        palette=colors_segment,
        ax=ax
    )
    
    ax.set_title("Number of Customers per Segment", fontsize=15)
    ax.set_xlabel("Count of Customers", fontsize=12)
    ax.set_ylabel(None)
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=12)

    # Menambahkan label angka di ujung bar
    for p in ax.patches:
        width = p.get_width()
        ax.text(width + 50, 
                p.get_y() + p.get_height()/2, 
                '{:1.0f}'.format(width), 
                ha="left", va="center")
    
    # Hilangkan border
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    st.pyplot(fig)

#Chart 4 : Performa Seller
st.subheader("💼 Top 5 Sellers by Revenue")
fig, ax = plt.subplots(figsize=(12, 6))

#Ambil Top 5 Seller
top_sellers = by_seller_df.sort_values(by="revenue", ascending=False).head(5)

#Warna 
colors_seller = [OLIST_DARK_BLUE] + ["#D3D3D3"] * 4

sns.barplot(
    x="revenue", 
    y="seller_id", 
    data=top_sellers, 
    palette=colors_seller,
    ax=ax
)

ax.set_title("Best Performing Sellers (Revenue)", loc="center", fontsize=18)
ax.set_xlabel("Total Revenue (BRL)", fontsize=15)
ax.set_ylabel("Seller ID", fontsize=15)

#Label ID Seller & Angka
labels = [item.get_text()[:8] + '...' for item in ax.get_yticklabels()]
ax.set_yticklabels(labels)

#Label Angka Revenue
for p in ax.patches:
    width = p.get_width()
    ax.text(width + 500, p.get_y() + p.get_height()/2, 
            f'BRL {width:,.0f}', ha="left", va="center", fontsize=10)
    
#Hilangkan Border
sns.despine(left=True, bottom=True)
st.pyplot(fig)
st.write("---")

#Chart 5 : Efisiensi Logistik
st.subheader("🚚 Logistic Efficiency (Delivery Time)")

#Menghitung Selisih Hari (Estimasi - Aktual)
logistics_df = main_df.dropna(subset=['order_estimated_delivery_date', 'order_delivered_customer_date']).copy()
logistics_df['order_estimated_delivery_date'] = pd.to_datetime(logistics_df['order_estimated_delivery_date'])
logistics_df['order_delivered_customer_date'] = pd.to_datetime(logistics_df['order_delivered_customer_date'])

#Metrik
on_time_count = (logistics_df['diff_delivery_days'] >= 0).sum()
total_count = len(logistics_df)
on_time_percentage = (on_time_count / total_count) * 100
avg_early = logistics_df['diff_delivery_days'].mean()

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("On-Time Orders", f"{on_time_percentage:.1f}%")
    st.metric("Avg Days Difference", f"{avg_early:.1f} Days")
    st.caption("Positive (+): Arrived Early\nNegative (-): Arrived Late")

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    
    #Visualisasi Histogram 
    sns.histplot(
        data=logistics_df, 
        x='diff_delivery_days', 
        bins=50, 
        kde=True, 
        color=OLIST_TEAL, 
        ax=ax
    )
    #Garis Batas Tepat Waktu (0)
    ax.axvline(x=0, color='red', linestyle='--', label='Estimated Date (0)')
    
    ax.set_title("Distribution of Delivery Time (Estimated - Actual)", fontsize=15)
    ax.set_xlabel("Days Difference (Positive = Faster)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.legend()
    
    sns.despine()
    st.pyplot(fig)

st.write("---")

#Chart 6: Customer Satisfaction
st.subheader("⭐ Customer Satisfaction (Review Scores)")

#Bersihkan duplikat agar review_id double
review_df = main_df.drop_duplicates(subset=['review_id'])

col1, col2 = st.columns([1, 2])
with col1:
    avg_score = review_df['review_score'].mean()
    st.metric("Average Review Score", f"{avg_score:.2f} / 5.0")

#Menghitung Kepuasan (Score 4 & 5 puas)
satisfied_count = review_df[review_df['review_score'] >= 4].shape[0]
satisfaction_rate = (satisfied_count / review_df.shape[0]) * 100
st.metric("Satisfaction Rate (>4 Stars)", f"{satisfaction_rate:.1f}%")

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))

#Warna
colors_score = ["#E53E3E", "#D3D3D3", "#D3D3D3", OLIST_TEAL, OLIST_TEAL]
    
sns.countplot(
        x='review_score', 
        data=review_df, 
        palette=colors_score,
        ax=ax
    )
    
ax.set_title("Distribution of Review Scores", fontsize=15)
ax.set_xlabel("Review Score (Stars)", fontsize=12)
ax.set_ylabel("Count", fontsize=12)

#Label
total = len(review_df) 
    
for p in ax.patches:
    height = p.get_height()
    #Hitung Persentase
    percentage = '{:.1f}%'.format(100 * height / total)
    #Menampilkan Label
    ax.text(p.get_x() + p.get_width()/2., height + (height * 0.02), percentage,
            ha="center", fontsize=12, color='black', weight='bold')
sns.despine()
st.pyplot(fig)

#Chart 7: Map
st.subheader("🗺️ Customer Density Map")
st.caption("Peta persebaran pelanggan di Brazil (Titik biru = Lokasi pelanggan).")

fig, ax = plt.subplots(figsize=(10, 10))

#Plot titik Peta
sns.scatterplot(
    x='geolocation_lng', 
    y='geolocation_lat', 
    data=geo_df, 
    alpha=0.5, 
    s=15, 
    color=OLIST_TEAL,
    edgecolor=None,
    ax=ax
)
#Label Anotasi untuk wilayah customer tertinggi
# Label São Paulo
ax.text(
    x=-46.0, y=-23.0, 
    s="São Paulo\n(Highest Density)",
    color="black", 
    fontsize=12, 
    fontweight='bold', 
    ha='right' 
)

# Label Rio de Janeiro
ax.text(
    x=-43.0, y=-22.0, 
    s="Rio de Janeiro", 
    color="black", 
    fontsize=12, 
    fontweight='bold',
    ha='left'
)
ax.set_title("Brazil Customer Distribution", fontsize=16)
ax.set_xlim(-75, -30)
ax.set_ylim(-35, 5)
ax.axis('off') 
st.pyplot(fig)
st.write("---")

#Footer
st.write("---")
st.markdown(f"""
    <p style='text-align: center; color: #555555;'>
    ID Camp 2025 - Data Scientist Learning Path : Data Analytics Project &copy; 2026 <br>
    Dashboard created with Streamlit by <b>Bagus Aripin Prastyo</b>
    </p>
    """, unsafe_allow_html=True)