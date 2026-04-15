import streamlit as st
import pandas as pd
import sqlite3
import io
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. SETUP HALAMAN & TEMA (FRONTEND)
# ==========================================

# st.set_page_config WAJIB dipanggil pertama kali sebelum komponen Streamlit lainnya
st.set_page_config(page_title="Inventaris Pusdatin", layout="wide", page_icon="📦")

def apply_custom_css():
    """!
    @brief Menerapkan CSS Kustom untuk Antarmuka Aplikasi.
    @details Mengubah tema aplikasi menjadi mode gelap (Dark Mode) khusus, menengahkan elemen sidebar, 
    dan mengatur estetika tabel data serta formulir input.
    """
    st.markdown(""" 
    <style>
        .stApp { background-color: #1B2631; }
        section[data-testid="stSidebar"] { background-color: #17202A; }
        [data-testid="stSidebar"] [data-testid="stImage"] {
            text-align: center; display: block; margin-left: auto; margin-right: auto; width: 100%;
        }
        [data-testid="stSidebar"] .block-container h1, 
        [data-testid="stSidebar"] .block-container p,
        [data-testid="stSidebar"] .block-container div {
            text-align: center;
        }
        [data-testid="stSidebar"] .stRadio div { text-align: left !important; }

        div[data-testid="metric-container"] {
            background-color: #212F3C !important;
            border: 1px solid #283747;
            padding: 15px; border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {
            color: #ecf0f1 !important;
        }

        .table-header {
            background-color: #283747;
            padding: 12px; border-radius: 5px 5px 0 0;
            font-weight: bold; color: #ecf0f1 !important;
            display: flex; align-items: center;
            border-bottom: 2px solid #34495e;
        }
        hr { border-top: 1px solid #34495e !important; margin: 0 !important; }
        
        input, select, textarea {
            background-color: #212F3C !important;
            color: white !important;
            border: 1px solid #566573 !important;
        }
        div[data-testid="stForm"] {
            background-color: #212F3C;
            border: 1px solid #566573;
            padding: 20px; border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA DATABASE (BACKEND)
# ==========================================

def init_db():
    """!
    @brief Menginisialisasi Database SQLite.
    @details Membuat file `inventaris_v2.db` dan tabel `perangkat` secara otomatis apabila belum ada.
    """
    conn = sqlite3.connect('inventaris_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS perangkat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_perangkat TEXT,
            brand TEXT,
            ip_address TEXT,
            sn TEXT,
            lokasi_rak TEXT,
            pemilik TEXT,
            kondisi TEXT,
            tgl_update TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_data():
    """!
    @brief Mengambil seluruh entri data dari database.
    @return pandas.DataFrame Data tabel perangkat yang diurutkan dari entri terbaru.
    """
    conn = sqlite3.connect('inventaris_v2.db')
    df = pd.read_sql_query("SELECT * FROM perangkat ORDER BY id DESC", conn)
    conn.close()
    return df

def add_item(nama, brand, ip, sn, rak, pemilik, kondisi):
    """!
    @brief Menyimpan record perangkat keras baru ke dalam database.
    @param nama [str] Nama jenis perangkat.
    @param brand [str] Merk perangkat.
    @param ip [str] IP Address yang dialokasikan.
    @param sn [str] Serial Number perangkat.
    @param rak [str] Lokasi fisik rak di Data Center.
    @param pemilik [str] Penanggungjawab / PIC BMN.
    @param kondisi [str] Kondisi operasional barang.
    """
    conn = sqlite3.connect('inventaris_v2.db')
    c = conn.cursor()
    tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('''INSERT INTO perangkat 
                 (nama_perangkat, brand, ip_address, sn, lokasi_rak, pemilik, kondisi, tgl_update) 
                 VALUES (?,?,?,?,?,?,?,?)''',
              (nama, brand, ip, sn, rak, pemilik, kondisi, tgl))
    conn.commit()
    conn.close()

def update_item(id_brg, nama, brand, ip, sn, rak, pemilik, kondisi):
    """!
    @brief Memperbarui record perangkat keras eksisting.
    @param id_brg [int] ID Baris dari perangkat di database.
    @param nama, brand, ip, sn, rak, pemilik, kondisi [str] Data pembaruan yang akan ditimpa.
    """
    conn = sqlite3.connect('inventaris_v2.db')
    c = conn.cursor()
    tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('''UPDATE perangkat SET 
                 nama_perangkat=?, brand=?, ip_address=?, sn=?, lokasi_rak=?, pemilik=?, kondisi=?, tgl_update=? 
                 WHERE id=?''',
              (nama, brand, ip, sn, rak, pemilik, kondisi, tgl, id_brg))
    conn.commit()
    conn.close()

def delete_item(id_brg):
    """!
    @brief Menghapus record dari database berdasarkan ID.
    @param id_brg [int] ID perangkat yang ingin dihapus.
    """
    conn = sqlite3.connect('inventaris_v2.db')
    c = conn.cursor()
    c.execute('DELETE FROM perangkat WHERE id=?', (id_brg,))
    conn.commit()
    conn.close()

def convert_df_to_excel(df):
    """!
    @brief Mengonversi tipe data Pandas DataFrame ke dalam Memory Bytes format Excel (.xlsx).
    @param df [pandas.DataFrame] Dataset yang akan dikonversi.
    @return [bytes] File stream agar bisa diunduh oleh komponen tombol Streamlit.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data_DC')
    return output.getvalue()

# ==========================================
# 3. KOMPONEN UI (MODULAR)
# ==========================================

def render_sidebar():
    """!
    @brief Merender area Navigasi Sidebar.
    @return [str] Menu yang sedang dipilih aktif oleh pengguna.
    """
    with st.sidebar:
        try:
            st.image("LogoKemhan.png", width=150) 
        except:
            st.warning("Logo tidak ditemukan.")

        st.write("") 
        st.title("Pusdatin Kemhan")
        st.write("Sistem Inventaris DC")
        st.markdown("---")
        menu = st.radio("NAVIGASI UTAMA", 
                        ["Dashboard", "Tambah Inventaris Baru", "Lihat Daftar Inventaris"],
                        label_visibility="collapsed")
        st.markdown("---")
        return menu

def render_metrics(df):
    """!
    @brief Merender Kartu Metrik (Statistik) di Dashboard Utama.
    @param df [pandas.DataFrame] Dataset untuk bahan kalkulasi metrik.
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Perangkat", f"{len(df)}", "Unit")
    with col2: st.metric("Kondisi Baik", f"{len(df[df['kondisi'] == 'Baik'])}", "Unit")
    with col3: st.metric("Maintenance", f"{len(df[df['kondisi'] == 'Maintenance'])}", "Unit")
    with col4: st.metric("Rusak", f"{len(df[df['kondisi'] == 'Rusak'])}", "Unit")
    st.markdown("<br>", unsafe_allow_html=True)

def render_charts(df):
    """!
    @brief Merender grafik Pie Chart menggunakan Plotly.
    @param df [pandas.DataFrame] Dataset untuk visualisasi distribusi Kondisi dan PIC.
    """
    if df.empty:
        return
        
    st.markdown("---")
    cg1, cg2 = st.columns(2)
    
    # Grafik 1: Distribusi Kondisi
    with cg1:
        df_kondisi = df['kondisi'].value_counts().reset_index()
        df_kondisi.columns = ['Kondisi', 'Jumlah']
        
        # Warna kustom (Hijau: Baik, Kuning: Maintenance, Merah: Rusak)
        color_map = {'Baik': '#2ecc71', 'Maintenance': '#f1c40f', 'Rusak': '#e74c3c'}
        fig1 = px.pie(df_kondisi, values='Jumlah', names='Kondisi', 
                      title='Distribusi Kondisi Perangkat', hole=0.4,
                      color='Kondisi', color_discrete_map=color_map)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig1, use_container_width=True)
        
    # Grafik 2: Distribusi Penanggungjawab / PIC
    with cg2:
        # Filter data kosong pada kolom pemilik
        df_valid_pic = df[df['pemilik'].str.strip() != ""]
        if not df_valid_pic.empty:
            df_pic = df_valid_pic['pemilik'].value_counts().reset_index()
            df_pic.columns = ['PIC', 'Jumlah']
            
            fig2 = px.pie(df_pic, values='Jumlah', names='PIC', 
                          title='Proporsi Penanggungjawab / PIC', hole=0.4)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Data Penanggungjawab (PIC) belum tersedia untuk divisualisasikan.")

def render_edit_form(df):
    """!
    @brief Merender formulir pembaruan data secara dinamis apabila ID objek aktif dalam sesi.
    @param df [pandas.DataFrame] Dataset eksisting untuk ditarik nilai lamanya (populate fields).
    """
    if st.session_state.edit_id is not None:
        item_data = df[df['id'] == st.session_state.edit_id]
        if not item_data.empty:
            item = item_data.iloc[0]
            with st.form("edit_form"):
                st.markdown(f"### ✏️ Edit: **{item['nama_perangkat']}**")
                
                # Baris Input 1
                ec1, ec2, ec3, ec4 = st.columns(4)
                e_nama = ec1.text_input("Nama Perangkat", value=item['nama_perangkat'])
                e_brand = ec2.text_input("Brand", value=item['brand'])
                e_ip = ec3.text_input("IP Address", value=item['ip_address'])
                e_sn = ec4.text_input("S/N", value=item['sn'])
                
                # Baris Input 2
                ec5, ec6, ec7 = st.columns(3)
                e_rak = ec5.text_input("Lokasi Rak", value=item['lokasi_rak'])
                e_pemilik = ec6.text_input("Penanggungjawab / PIC", value=item['pemilik'])
                
                # Pengaturan Indeks Dropdown Status Kondisi
                opts = ["Baik", "Rusak", "Maintenance"]
                idx = opts.index(item['kondisi']) if item['kondisi'] in opts else 0
                e_kondisi = ec7.selectbox("Kondisi", opts, index=idx)
                
                # Tombol Aksi Formulir
                btn1, btn2 = st.columns([1, 6])
                if btn1.form_submit_button("💾 SIMPAN"):
                    update_item(st.session_state.edit_id, e_nama, e_brand, e_ip, e_sn, e_rak, e_pemilik, e_kondisi)
                    st.session_state.edit_id = None
                    st.success("Diupdate!")
                    st.rerun()
                if btn2.form_submit_button("❌ BATAL"):
                    st.session_state.edit_id = None
                    st.rerun()
            st.markdown("---")

def render_data_table(df):
    """!
    @brief Merender Tabel Data berbasis HTML kustom untuk daftar Inventaris perangkat.
    @param df [pandas.DataFrame] Dataset yang sudah difilter untuk ditampilkan dalam baris.
    """
    st.subheader("Daftar Perangkat")
    
    # Render Flex Header Tabel
    st.markdown("""
    <div class="table-header">
        <div style="flex: 0.5;">No</div>
        <div style="flex: 1.5;">Nama Perangkat</div>
        <div style="flex: 1;">Brand</div>
        <div style="flex: 1.2;">IP Address</div>
        <div style="flex: 1.2;">S/N</div>
        <div style="flex: 1;">Posisi Rak</div>
        <div style="flex: 1.2;">PIC / Penanggungjawab</div>
        <div style="flex: 1;">Kondisi</div>
        <div style="flex: 1; text-align: center;">Aksi</div>
    </div>
    """, unsafe_allow_html=True)

    if len(df) == 0:
        st.info("Belum ada data.")
        return

    # Render Baris demi Baris Data
    for i, row in df.iterrows():
        bg_badge = "#2ecc71" if row['kondisi'] == "Baik" else "#f1c40f" if row['kondisi'] == "Maintenance" else "#e74c3c"
        
        with st.container():
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.5, 1.5, 1, 1.2, 1.2, 1, 1.2, 1, 1])
            
            c1.markdown(f"<span>{i+1}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span>{row['nama_perangkat']}</span>", unsafe_allow_html=True)
            c3.markdown(f"<span>{row['brand']}</span>", unsafe_allow_html=True)
            c4.markdown(f"<span>{row['ip_address']}</span>", unsafe_allow_html=True)
            c5.markdown(f"<span>{row['sn']}</span>", unsafe_allow_html=True)
            c6.markdown(f"<span>{row['lokasi_rak']}</span>", unsafe_allow_html=True)
            c7.markdown(f"<span>{row['pemilik']}</span>", unsafe_allow_html=True)
            c8.markdown(f"<span style='background-color:{bg_badge}; color:white !important; padding:2px 8px; border-radius:10px; font-size:12px;'>{row['kondisi']}</span>", unsafe_allow_html=True)
            
            # Kolom Eksekusi / Aksi
            with c9:
                bc1, bc2 = st.columns(2)
                if bc1.button("✏️", key=f"e_{row['id']}"):
                    st.session_state.edit_id = row['id']
                    st.rerun()
                if bc2.button("🗑️", key=f"d_{row['id']}"):
                    delete_item(row['id'])
                    st.rerun()
            st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 4. KONTROL HALAMAN (ROUTER)
# ==========================================

def page_dashboard(menu):
    """!
    @brief Pengendali Halaman Dashboard Utama.
    @param menu [str] Menu navigasi aktif yang mengarahkan parameter filter visual Halaman Dashboard.
    """
    st.title("📊 Dashboard Inventaris")
    df = get_all_data()

    # Rendering Metrik & Grafik Khusus Halaman Dashboard
    if menu == "Dashboard":
        render_metrics(df)
        render_charts(df)

    # UI Komponen Pencarian Universal & Download Excel
    c_search, c_dl = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("🔍 Cari (Nama/Brand/IP/SN/PIC)...")
    with c_dl:
        st.write("") 
        excel_data = convert_df_to_excel(df)
        st.download_button("📥 Download Excel", excel_data, "inventaris_pusdatin.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Proses Filtering DataFrame Berdasarkan Kueri
    if search_query:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # Eksekusi Render Tabel Form
    render_edit_form(df)
    render_data_table(df)

def page_add_inventory():
    """!
    @brief Pengendali Halaman Formulir Tambah Data Baru & Import Excel.
    @details Menggunakan sistem Tabs untuk memisahkan input manual dan import massal berdasar template.
    """
    st.title("➕ Manajemen Perangkat Baru")
    
    # Membagi antarmuka menjadi 2 Tab
    tab_manual, tab_import = st.tabs(["✍️ Input Manual", "📁 Import Massal (Excel)"])
    
    # --- TAB 1: INPUT MANUAL ---
    with tab_manual:
        with st.form("add_form", clear_on_submit=True):
            st.write("Silakan isi data perangkat baru:")
            
            c1, c2, c3, c4 = st.columns(4)
            nama = c1.text_input("Nama Perangkat")
            brand = c2.text_input("Brand / Merk")
            ip = c3.text_input("IP Address")
            sn = c4.text_input("Serial Number (S/N)")
            
            c5, c6, c7 = st.columns(3)
            rak = c5.text_input("Lokasi Rak (Cth: Rak A1 - U20)")
            pemilik = c6.text_input("Penanggungjawab / PIC")
            kondisi = c7.selectbox("Kondisi Fisik", ["Baik", "Rusak", "Maintenance"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SIMPAN DATA", type="primary"):
                if nama and sn: 
                    add_item(nama, brand, ip, sn, rak, pemilik, kondisi)
                    st.success(f"Perangkat {nama} berhasil disimpan!")
                else:
                    st.error("Gagal! Nama Perangkat dan Serial Number wajib diisi.")

    # --- TAB 2: IMPORT MASSAL ---
    with tab_import:
        st.info("💡 **Tips Import:** Unduh template Excel yang disediakan, isi data sesuai kolom, lalu unggah kembali file tersebut ke sini.")
        
        # 1. Fitur Unduh Template
        st.markdown("#### Langkah 1: Unduh Template")
        col_template = ["Nama Perangkat", "Brand", "IP Address", "Serial Number", "Lokasi Rak", "PIC", "Kondisi"]
        df_template = pd.DataFrame(columns=col_template)
        template_bytes = convert_df_to_excel(df_template)
        
        st.download_button(
            label="📥 Unduh Template Import (.xlsx)", 
            data=template_bytes, 
            file_name="Template_Import_DC.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # 2. Fitur Upload & Proses
        st.markdown("#### Langkah 2: Upload File Data")
        uploaded_file = st.file_uploader("Unggah file template yang telah diisi (.xlsx)", type=['xlsx'])
        
        if uploaded_file is not None:
            if st.button("🚀 Eksekusi Import Data", type="primary"):
                try:
                    # Membaca excel dan mengisi field kosong (NaN) dengan string kosong
                    df_import = pd.read_excel(uploaded_file).fillna("")
                    
                    # Validasi struktur kolom
                    if all(col in df_import.columns for col in col_template):
                        sukses_count = 0
                        for _, row in df_import.iterrows():
                            v_nama = str(row["Nama Perangkat"]).strip()
                            v_brand = str(row["Brand"]).strip()
                            v_ip = str(row["IP Address"]).strip()
                            v_sn = str(row["Serial Number"]).strip()
                            v_rak = str(row["Lokasi Rak"]).strip()
                            v_pic = str(row["PIC"]).strip()
                            
                            v_kondisi = str(row["Kondisi"]).strip().capitalize()
                            if v_kondisi not in ["Baik", "Rusak", "Maintenance"]:
                                v_kondisi = "Baik" # Default fallback
                                
                            # Cek minimal Nama dan SN terisi agar data valid
                            if v_nama and v_sn:
                                add_item(v_nama, v_brand, v_ip, v_sn, v_rak, v_pic, v_kondisi)
                                sukses_count += 1
                                
                        st.success(f"Proses selesai! Berhasil mengimpor {sukses_count} baris data perangkat ke dalam sistem.")
                    else:
                        st.error("Struktur kolom tidak sesuai. Harap pastikan Anda menggunakan file Template yang diunduh pada Langkah 1.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses file: {e}")


# ==========================================
# 5. ENTRY POINT UTAMA
# ==========================================

def main():
    """!
    @brief Fungsi Main (Utama) untuk menginisiasi skrip secara berurutan.
    """
    apply_custom_css()
    init_db()

    # Inisialisasi Environment Variabel sementara jika baru pertama kali diakses.
    if 'edit_id' not in st.session_state:
        st.session_state.edit_id = None

    menu = render_sidebar()

    # Logika Router
    if menu in ["Dashboard", "Lihat Daftar Inventaris"]:
        page_dashboard(menu)
    elif menu == "Tambah Inventaris Baru":
        page_add_inventory()

if __name__ == '__main__':
    main()
