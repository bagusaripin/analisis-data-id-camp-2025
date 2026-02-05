# analisis-data-id-camp-2025
# OLIST E-Commerce Dashboard : Executive Summary & Performance Metrics
- Dashboard ini dibuat untuk menganalisis data e-commerce public dataset (Olist)
- Proyek ini mencakup analisi tren penjualan, performa produk, customer segment (RFM Analysis), performa seller, logistik efisiensi, customer satisfaction, dan persebaran customer (analysis geospatial)

# Struktur Folder
📁 submission
 1. 📁 dashboard -> (dashboard.py, all_data_lite.csv, rfm_analysis.csv, geolocation_analysis.csv)
 2. 📁 data -> (customer_dataset.csv, order_items.csv, order_payments_dataset.csv, order_reviews_dataset.csv, order_dataset.csv, product_dataset.csv, seller_dataset.csv, geolocation_dataset.csv, product_category_name_translation.csv, orders_clean.csv  (*#Output Data Orders yang sudah dibersihkan))
3. requirements.txt
4. url.txt
5. notebook.ipynb
6. README.md

## 🛠️ Cara Menjalankan Dashboard Di Lokal & Tautan
untuk tautan bisa cek url.txt atau klik ini https://bagus-data-analytics-id-camp-2025.streamlit.app/

Berikut cara menjalankan dashbord di komputer lokal anda
### 1. Setup Environment
Disarankan untuk menggunakan virtual environment agar tidak mengganggu instalasi Python global.

    **Opsi A: Menggunakan Anaconda**
        ```bash
        conda create --name main-ds python=3.9
        conda activate main-ds
        pip install -r requirements.txt

    **Opsi B: Menggunakan Terminal/Shell/CMD**
        ```bash
        # Windows
        python -m venv venv
        venv\Scripts\activate

        # macOS/Linux
        python3 -m venv venv
        source venv/bin/activate

        # Install dependencies
        pip install -r requirements.txt

### 2. Menjalankan Streamlit
streamlit run dashboard.py

### 3. Selesai
Dashboard akan terbuka di browser bawaan anda.
