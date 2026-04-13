import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime

# --- 1. SETUP HALAMAN & DARK MODE ---
st.set_page_config(page_title="Inventaris Pusdatin", layout="wide", page_icon="📦")

st.markdown(""" 
<style>
    /* Background Utama */
    .stApp { background-color: #1B2631; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #17202A; }

    /* Rata Tengah Sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center; display: block; margin-left: auto; margin-right: auto; width: 100%;
    }
    [data-testid="stSidebar"] .block-container h1, 
    [data-testid="stSidebar"] .block-container p,
    [data-testid="stSidebar"] .block-container div {
        text-align: center;
    }
    [data-testid="stSidebar"] .stRadio div { text-align: left !important; }

    /* Kartu Statistik */
    div[data-testid="metric-container"] {
        background-color: #212F3C !important;
        border: 1px solid #283747;
        padding: 15px; border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {
        color: #ecf0f1 !important;
    }

    /* Tabel Header */
    .table-header {
        background-color: #283747;
        padding: 12px; border-radius: 5px 5px 0 0;
        font-weight: bold; color: #ecf0f1 !important;
        display: flex; align-items: center;
        border-bottom: 2px solid #34495e;
    }
    hr { border-top: 1px solid #34495e !important; margin: 0 !important; }
    
    /* Form & Input */
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

# --- 2. DATABASE (Backend - Versi 2) ---
def init_db():
    # NAMA DATABASE BARU AGAR TIDAK BENTROK
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
    conn = sqlite3.connect('inventaris_v2.db')
    df = pd.read_sql_query("SELECT * FROM perangkat ORDER BY id DESC", conn)
    conn.close()
    return df

def add_item(nama, brand, ip, sn, rak, pemilik, kondisi):
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
    conn = sqlite3.connect('inventaris_v2.db')
    c = conn.cursor()
    c.execute('DELETE FROM perangkat WHERE id=?', (id_brg,))
    conn.commit()
    conn.close()

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data_DC')
    return output.getvalue()

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- 3. APLIKASI UTAMA ---
def main():
    init_db()

    # SIDEBAR
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
        #st.info("💡 **Tips:** Klik ✏️ untuk edit.")

    # DASHBOARD & LIST
    if menu == "Dashboard" or menu == "Lihat Daftar Inventaris":
        st.title("📊 Dashboard Inventaris")
        
        df = get_all_data()

        if menu == "Dashboard":
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Perangkat", f"{len(df)}", "Unit")
            with col2: st.metric("Kondisi Baik", f"{len(df[df['kondisi'] == 'Baik'])}", "Unit")
            with col3: st.metric("Maintenance", f"{len(df[df['kondisi'] == 'Maintenance'])}", "Unit")
            with col4: st.metric("Rusak", f"{len(df[df['kondisi'] == 'Rusak'])}", "Unit")
            st.markdown("<br>", unsafe_allow_html=True)

        c_search, c_dl = st.columns([3, 1])
        with c_search:
            search_query = st.text_input("🔍 Cari (Nama/Brand/IP/SN)...")

        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        # LOGIKA EDIT
        if st.session_state.edit_id is not None:
            item_data = df[df['id'] == st.session_state.edit_id]
            if not item_data.empty:
                item = item_data.iloc[0]
                with st.form("edit_form"):
                    st.markdown(f"### ✏️ Edit: **{item['nama_perangkat']}**")
                    ec1, ec2, ec3, ec4 = st.columns(4)
                    e_nama = ec1.text_input("Nama Perangkat", value=item['nama_perangkat'])
                    e_brand = ec2.text_input("Brand", value=item['brand'])
                    e_ip = ec3.text_input("IP Address", value=item['ip_address'])
                    e_sn = ec4.text_input("S/N", value=item['sn'])
                    
                    ec5, ec6, ec7 = st.columns(3)
                    e_rak = ec5.text_input("Lokasi Rak", value=item['lokasi_rak'])
                    e_pemilik = ec6.text_input("Pemilik (PIC)", value=item['pemilik'])
                    
                    opts = ["Baik", "Rusak", "Maintenance"]
                    idx = opts.index(item['kondisi']) if item['kondisi'] in opts else 0
                    e_kondisi = ec7.selectbox("Kondisi", opts, index=idx)
                    
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

        # TABEL DAFTAR BARANG
        st.subheader("Daftar Perangkat")
        
        # Header Tabel Custom (Layout Fleksibel)
        st.markdown("""
        <div class="table-header">
            <div style="flex: 0.5;">No</div>
            <div style="flex: 1.5;">Nama Perangkat</div>
            <div style="flex: 1;">Brand</div>
            <div style="flex: 1.2;">IP Address</div>
            <div style="flex: 1.2;">S/N</div>
            <div style="flex: 1;">Posisi Rak</div>
            <div style="flex: 1.2;">Pemilik</div>
            <div style="flex: 1;">Kondisi</div>
            <div style="flex: 1; text-align: center;">Aksi</div>
        </div>
        """, unsafe_allow_html=True)

        if len(df) > 0:
            for i, row in df.iterrows():
                bg_badge = "#2ecc71" if row['kondisi'] == "Baik" else "#f1c40f" if row['kondisi'] == "Maintenance" else "#e74c3c"
                
                with st.container():
                    # Menyesuaikan rasio kolom dengan header
                    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.5, 1.5, 1, 1.2, 1.2, 1, 1.2, 1, 1])
                    
                    c1.markdown(f"<span>{i+1}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span>{row['nama_perangkat']}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span>{row['brand']}</span>", unsafe_allow_html=True)
                    c4.markdown(f"<span>{row['ip_address']}</span>", unsafe_allow_html=True)
                    c5.markdown(f"<span>{row['sn']}</span>", unsafe_allow_html=True)
                    c6.markdown(f"<span>{row['lokasi_rak']}</span>", unsafe_allow_html=True)
                    c7.markdown(f"<span>{row['pemilik']}</span>", unsafe_allow_html=True)
                    c8.markdown(f"<span style='background-color:{bg_badge}; color:white !important; padding:2px 8px; border-radius:10px; font-size:12px;'>{row['kondisi']}</span>", unsafe_allow_html=True)
                    
                    with c9:
                        bc1, bc2 = st.columns(2)
                        if bc1.button("✏️", key=f"e_{row['id']}"):
                            st.session_state.edit_id = row['id']
                            st.rerun()
                        if bc2.button("🗑️", key=f"d_{row['id']}"):
                            delete_item(row['id'])
                            st.rerun()
                    
                    st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.info("Belum ada data.")
        
        with c_dl:
            st.write("") 
            excel_data = convert_df_to_excel(df)
            st.download_button("📥 Download Excel", excel_data, "inventaris_pusdatin.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


    # MENU TAMBAH BARANG
    elif menu == "Tambah Inventaris Baru":
        st.title("➕ Tambah Perangkat Baru")
        
        with st.form("add_form", clear_on_submit=True):
            st.write("Silakan isi data perangkat baru:")
            
            # Baris 1 Input
            c1, c2, c3, c4 = st.columns(4)
            nama = c1.text_input("Nama Perangkat")
            brand = c2.text_input("Brand / Merk")
            ip = c3.text_input("IP Address")
            sn = c4.text_input("Serial Number (S/N)")
            
            # Baris 2 Input
            c5, c6, c7 = st.columns(3)
            rak = c5.text_input("Lokasi Rak (Cth: Rak A1 - U20)")
            pemilik = c6.text_input("Pemilik (Cth: Bid. InfraTIK)")
            kondisi = c7.selectbox("Kondisi Fisik", ["Baik", "Rusak", "Maintenance"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("SIMPAN", type="primary"):
                if nama and sn: # Wajib diisi minimal Nama dan SN
                    add_item(nama, brand, ip, sn, rak, pemilik, kondisi)
                    st.success(f"Perangkat {nama} berhasil disimpan!")
                else:
                    st.error("Gagal! Nama Perangkat dan Serial Number wajib diisi.")

if __name__ == '__main__':
    main()