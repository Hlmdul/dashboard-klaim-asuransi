import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi halaman
st.set_page_config(
    page_title="Project VisDat - Dashboard Klaim Asuransi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS untuk styling dasar (menghindari kompleksitas)
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f4e79;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("clean.xlsx")
    df['accepted_date'] = pd.to_datetime(df['accepted_date'])
    df['year'] = df['accepted_date'].dt.year
    df['month'] = df['accepted_date'].dt.month
    df['month_year'] = df['accepted_date'].dt.to_period('M').astype(str)
    return df

# Load data
df = load_data()

# Header
st.markdown('<h1 class="main-title">📊 Dashboard Klaim Asuransi Kesehatan</h1>', unsafe_allow_html=True)

# Sidebar untuk filter
st.sidebar.markdown("## Filter Data")

# Filter berdasarkan waktu dengan dropdown
st.sidebar.markdown("### Filter Waktu")

# Tampilkan informasi tentang data yang tersedia
data_years = sorted(df['year'].unique())
st.sidebar.info(f"**Data Tersedia:** {', '.join(map(str, data_years))}")

# Ambil tahun dan bulan yang tersedia dari data
available_years = sorted(df['year'].unique())
available_months = [
    {'value': 1, 'label': 'Januari'}, {'value': 2, 'label': 'Februari'}, 
    {'value': 3, 'label': 'Maret'}, {'value': 4, 'label': 'April'},
    {'value': 5, 'label': 'Mei'}, {'value': 6, 'label': 'Juni'},
    {'value': 7, 'label': 'Juli'}, {'value': 8, 'label': 'Agustus'},
    {'value': 9, 'label': 'September'}, {'value': 10, 'label': 'Oktober'},
    {'value': 11, 'label': 'November'}, {'value': 12, 'label': 'Desember'}
]

# Filter preset atau custom
time_filter_type = st.sidebar.radio(
    "Pilih Jenis Filter:",
    ["Preset Waktu", "Custom Range"]
)

if time_filter_type == "Preset Waktu":
    preset_options = {
        'Semua Data': 'all',
        'Tahun 2020': 'year_2020',
        'Tahun 2016': 'year_2016',
        'Semester Pertama 2020': 'first_half_2020',
        'Semester Kedua 2020': 'second_half_2020',
        'Q1 2020 (Jan-Mar)': 'q1_2020',
        'Q2 2020 (Apr-Jun)': 'q2_2020',
        'Q3 2020 (Jul-Sep)': 'q3_2020',
        'Q4 2020 (Okt-Des)': 'q4_2020'
    }
    
    selected_preset = st.sidebar.selectbox(
        "Pilih Preset:",
        list(preset_options.keys())
    )
    
    # Apply preset filter
    if preset_options[selected_preset] == 'all':
        start_date = df['accepted_date'].min()
        end_date = df['accepted_date'].max()
    elif preset_options[selected_preset] == 'year_2020':
        start_date = pd.to_datetime("2020-01-01")
        end_date = pd.to_datetime("2020-12-31")
    elif preset_options[selected_preset] == 'year_2016':
        start_date = pd.to_datetime("2016-01-01")
        end_date = pd.to_datetime("2016-12-31")
    elif preset_options[selected_preset] == 'first_half_2020':
        start_date = pd.to_datetime("2020-01-01")
        end_date = pd.to_datetime("2020-06-30")
    elif preset_options[selected_preset] == 'second_half_2020':
        start_date = pd.to_datetime("2020-07-01")
        end_date = pd.to_datetime("2020-12-31")
    elif preset_options[selected_preset] == 'q1_2020':
        start_date = pd.to_datetime("2020-01-01")
        end_date = pd.to_datetime("2020-03-31")
    elif preset_options[selected_preset] == 'q2_2020':
        start_date = pd.to_datetime("2020-04-01")
        end_date = pd.to_datetime("2020-06-30")
    elif preset_options[selected_preset] == 'q3_2020':
        start_date = pd.to_datetime("2020-07-01")
        end_date = pd.to_datetime("2020-09-30")
    elif preset_options[selected_preset] == 'q4_2020':
        start_date = pd.to_datetime("2020-10-01")
        end_date = pd.to_datetime("2020-12-31")

else:  # Custom Range
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        start_year = st.selectbox(
            "Dari Tahun:",
            available_years,
            index=0
        )
        
        start_month_options = [m['label'] for m in available_months]
        start_month_labels = st.selectbox(
            "Dari Bulan:",
            start_month_options,
            index=0
        )
        start_month = next(m['value'] for m in available_months if m['label'] == start_month_labels)
    
    with col2:
        end_year = st.selectbox(
            "Sampai Tahun:",
            available_years,
            index=len(available_years)-1
        )
        
        end_month_options = [m['label'] for m in available_months]
        end_month_labels = st.selectbox(
            "Sampai Bulan:",
            end_month_options,
            index=11
        )
        end_month = next(m['value'] for m in available_months if m['label'] == end_month_labels)
    
    # Buat start_date dan end_date dari pilihan dropdown
    start_date = pd.to_datetime(f"{start_year}-{start_month:02d}-01")
    # Untuk end_date, ambil hari terakhir dari bulan yang dipilih
    if end_month == 12:
        end_date = pd.to_datetime(f"{end_year+1}-01-01") - pd.Timedelta(days=1)
    else:
        end_date = pd.to_datetime(f"{end_year}-{end_month+1:02d}-01") - pd.Timedelta(days=1)

# Tampilkan rentang yang dipilih
st.sidebar.info(f"**Periode Dipilih:**\n{start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")

st.sidebar.markdown("---")

# Filter berdasarkan status klaim
status_options = ['Semua'] + list(df['claimstatus'].unique())
selected_status = st.sidebar.selectbox("Status Klaim", status_options)

# Filter berdasarkan diagnosis (top 10)
top_diagnoses = df['diagnosis'].value_counts().head(10).index.tolist()
diagnosis_options = ['Semua'] + top_diagnoses
selected_diagnosis = st.sidebar.selectbox("Diagnosis", diagnosis_options)

# Apply filters
filtered_df = df.copy()

# Filter tanggal berdasarkan start_date dan end_date yang sudah ditentukan
filtered_df = filtered_df[
    (filtered_df['accepted_date'] >= start_date) & 
    (filtered_df['accepted_date'] <= end_date)
]

# Filter status
if selected_status != 'Semua':
    filtered_df = filtered_df[filtered_df['claimstatus'] == selected_status]

# Filter diagnosis
if selected_diagnosis != 'Semua':
    filtered_df = filtered_df[filtered_df['diagnosis'] == selected_diagnosis]

# Metrics Overview - menggunakan Streamlit built-in metrics
st.markdown("## 📈 Ringkasan Statistik")

# Buat metrics menggunakan Streamlit columns dan metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Klaim",
        value=f"{len(filtered_df):,}",
        delta=f"dari {len(df):,} total"
    )

with col2:
    st.metric(
        label="Total Nominal Diajukan",
        value=f"Rp {filtered_df['claimsubmitted'].sum():,.0f}",
        delta=f"{(filtered_df['claimsubmitted'].sum()/df['claimsubmitted'].sum()*100):.1f}% dari total"
    )

with col3:
    st.metric(
        label="Total Dibayarkan", 
        value=f"Rp {filtered_df['claimpaid'].sum():,.0f}",
        delta=f"{(filtered_df['claimpaid'].sum()/filtered_df['claimsubmitted'].sum()*100):.1f}% rasio pembayaran"
    )

with col4:
    st.metric(
        label="Rata-rata % Dibayar",
        value=f"{filtered_df['percentagepaid'].mean():.1%}",
        delta=f"Median: {filtered_df['percentagepaid'].median():.1%}"
    )

# Visualisasi
st.markdown("---")
st.markdown("## 📊 Visualisasi Data")

# Gunakan columns untuk responsive layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tren Jumlah Klaim dari Waktu ke Waktu")
    
    # Group by month-year untuk line chart
    monthly_claims = filtered_df.groupby('month_year').size().reset_index(name='count')
    monthly_claims['month_year'] = pd.to_datetime(monthly_claims['month_year'])
    
    fig_line = px.line(
        monthly_claims, 
        x='month_year', 
        y='count',
        title="Tren Klaim Bulanan",
        color_discrete_sequence=['#1565C0']
    )
    fig_line.update_layout(
        height=400,
        xaxis_title="Bulan-Tahun",
        yaxis_title="Jumlah Klaim"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("Distribusi Status Klaim")
    
    status_counts = filtered_df['claimstatus'].value_counts()
    
    # Definisikan warna berdasarkan status
    colors = ['#1565C0', '#64B5F6', '#F3F7FF']
    
    fig_pie = px.pie(
        values=status_counts.values, 
        names=status_counts.index,
        title="Distribusi Status Klaim",
        color_discrete_sequence=colors
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 2: Histogram dan Bar Chart
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Persentase Pembayaran Klaim")
    
    fig_hist = px.histogram(
        filtered_df, 
        x='percentagepaid',
        nbins=30,
        title="Histogram Persentase Pembayaran",
        color_discrete_sequence=['#1565C0']
    )
    fig_hist.update_layout(
        height=400,
        xaxis_title="Persentase Dibayar",
        yaxis_title="Frekuensi"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("Top 10 Diagnosis dengan Klaim Terbanyak")
    
    top_diagnosis = filtered_df['diagnosis'].value_counts().head(10).reset_index()
    top_diagnosis.columns = ['diagnosis', 'count']
    
    fig_bar = px.bar(
        top_diagnosis, 
        x='count', 
        y='diagnosis',
        orientation='h',
        title="Top 10 Diagnosis",
        color_discrete_sequence=['#1565C0']
    )
    fig_bar.update_layout(
        height=400,
        xaxis_title="Jumlah Klaim",
        yaxis_title="Diagnosis",
        yaxis={'categoryorder':'total ascending'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Data Table Section
st.markdown("---")
st.markdown("## 📋 Data Tabel")

# Search and controls
col_search, col_size = st.columns([3, 1])

with col_search:
    search_term = st.text_input("🔍 Cari dalam data (member_id, diagnosis, dll.)")

with col_size:
    page_size = st.selectbox("Baris per halaman", [10, 25, 50, 100], index=1)

if search_term:
    mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
    display_df = filtered_df[mask]
else:
    display_df = filtered_df

# Show filtered data count
st.write(f"Menampilkan {len(display_df)} dari {len(filtered_df)} record")

# Pagination
col_page, col_info = st.columns([1, 2])

with col_page:
    page_number = st.number_input("Halaman", min_value=1, max_value=max(1, len(display_df)//page_size + 1), value=1)

with col_info:
    st.write(f"Total halaman: {max(1, len(display_df)//page_size + 1)}")

start_idx = (page_number - 1) * page_size
end_idx = start_idx + page_size

st.dataframe(
    display_df.iloc[start_idx:end_idx].style.format({
        'percentagepaid': '{:.1%}',
        'claimsubmitted': 'Rp {:,.0f}',
        'claimpaid': 'Rp {:,.0f}'
    }),
    use_container_width=True,
    hide_index=True
)

# Download functionality
st.markdown("---")
st.markdown("## 💾 Export Data")

csv_data = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download sebagai CSV",
    data=csv_data,
    file_name=f"klaim_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# Statistik Deskriptif
st.markdown("---")
st.markdown("## 📊 Statistik Deskriptif")
numeric_columns = ['claimsubmitted', 'claimpaid', 'percentagepaid']
stats_df = filtered_df[numeric_columns].describe()

# Format the statistics table
formatted_stats = stats_df.style.format({
    'claimsubmitted': 'Rp {:,.0f}',
    'claimpaid': 'Rp {:,.0f}',
    'percentagepaid': '{:.1%}'
})

st.dataframe(formatted_stats, use_container_width=True)

# Insight singkat
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Insight Kunci")
    
    avg_submitted = filtered_df['claimsubmitted'].mean()
    avg_paid = filtered_df['claimpaid'].mean()
    avg_percentage = filtered_df['percentagepaid'].mean()
    
    st.write(f"• **Rata-rata klaim diajukan:** Rp {avg_submitted:,.0f}")
    st.write(f"• **Rata-rata dibayarkan:** Rp {avg_paid:,.0f}")
    st.write(f"• **Rata-rata persentase pembayaran:** {avg_percentage:.1%}")
    
    # Analisis rasio pembayaran
    if avg_percentage >= 0.8:
        payment_insight = "Tingkat pembayaran sangat baik"
    elif avg_percentage >= 0.6:
        payment_insight = "Tingkat pembayaran cukup baik"
    else:
        payment_insight = "Tingkat pembayaran perlu perhatian"
    
    st.write(f"• **Status pembayaran:** {payment_insight}")

with col2:
    st.subheader("📈 Distribusi Data")
    
    # Variabilitas data
    std_percentage = filtered_df['percentagepaid'].std()
    if std_percentage <= 0.2:
        variability = "rendah (konsisten)"
    elif std_percentage <= 0.4:
        variability = "sedang"
    else:
        variability = "tinggi (bervariasi)"
    
    st.write(f"• **Variabilitas persentase pembayaran:** {variability}")
    st.write(f"• **Total record yang dianalisis:** {len(filtered_df):,}")
    
    # Outlier detection sederhana
    q75_paid = filtered_df['claimpaid'].quantile(0.75)
    q25_paid = filtered_df['claimpaid'].quantile(0.25)
    iqr = q75_paid - q25_paid
    outliers = len(filtered_df[(filtered_df['claimpaid'] > q75_paid + 1.5*iqr) | 
                               (filtered_df['claimpaid'] < q25_paid - 1.5*iqr)])
    
    st.write(f"• **Potensi outlier:** {outliers} record ({outliers/len(filtered_df)*100:.1f}%)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #1565c0; font-weight: 500; padding: 20px;'>
    📊 Project VisDat - Dashboard Klaim Asuransi Kesehatan<br>
    Dibuat dengan ❤️ menggunakan Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)

