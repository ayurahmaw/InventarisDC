import streamlit as st
import pandas as pd
import sqlite3
import io
import math
import plotly.express as px
from datetime import datetime
from typing import Any

# ==========================================
# KONSTANTA GLOBAL
# ==========================================
DATABASE_FILE_PATH = 'inventaris_v2.db'

# Konstanta Kolom Database / Excel
COL_DEVICE_NAME = "Nama Perangkat"
COL_BRAND = "Brand"
COL_IP_ADDRESS = "IP Address"
COL_SERIAL_NUMBER = "Serial Number"
COL_RACK_LOCATION = "Lokasi Rak"
COL_PIC = "PIC"
COL_CONDITION = "Kondisi"
TEMPLATE_COLUMNS = [COL_DEVICE_NAME, COL_BRAND, COL_IP_ADDRESS, COL_SERIAL_NUMBER, COL_RACK_LOCATION, COL_PIC, COL_CONDITION]

# Konstanta Status Kondisi
CONDITION_GOOD = "Baik"
CONDITION_BROKEN = "Rusak"
CONDITION_MAINTENANCE = "Maintenance"

# Konstanta Menu Navigasi
MENU_ITEM_DASHBOARD = "Dashboard"
MENU_ITEM_ADD = "Tambah Inventaris Baru"
MENU_ITEM_LIST = "Lihat Daftar Inventaris"

# ==========================================
# 1. SETUP HALAMAN & TEMA (FRONTEND)
# ==========================================

st.set_page_config(page_title="Inventaris Pusdatin", layout="wide", page_icon="📦")

def inject_custom_theme_css() -> None:
    """!
    @brief Menerapkan CSS Kustom untuk Antarmuka Aplikasi.
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
            margin-top: 10px;
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
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA DATABASE (BACKEND)
# ==========================================

def initialize_database() -> None:
    """!
    @brief Menginisialisasi Database SQLite secara aman menggunakan Context Manager.
    """
    with sqlite3.connect(DATABASE_FILE_PATH) as db_connection:
        db_cursor = db_connection.cursor()
        db_cursor.execute('''
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

def fetch_all_inventory_data() -> pd.DataFrame:
    """!
    @brief Mengambil seluruh entri data dari tabel perangkat.
    @return pandas.DataFrame Dataset inventaris lengkap.
    """
    with sqlite3.connect(DATABASE_FILE_PATH) as db_connection:
        inventory_dataframe = pd.read_sql_query("SELECT * FROM perangkat ORDER BY id DESC", db_connection)
    return inventory_dataframe

def insert_new_device(device_name: str, brand_name: str, ip_address: str, serial_number: str, rack_location: str, pic_name: str, condition_status: str) -> None:
    """!
    @brief Menyimpan entri perangkat keras baru ke dalam sistem basis data.
    """
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DATABASE_FILE_PATH) as db_connection:
        db_cursor = db_connection.cursor()
        db_cursor.execute('''INSERT INTO perangkat 
                     (nama_perangkat, brand, ip_address, sn, lokasi_rak, pemilik, kondisi, tgl_update) 
                     VALUES (?,?,?,?,?,?,?,?)''',
                  (device_name, brand_name, ip_address, serial_number, rack_location, pic_name, condition_status, current_timestamp))

def update_existing_device(device_id: int, device_name: str, brand_name: str, ip_address: str, serial_number: str, rack_location: str, pic_name: str, condition_status: str) -> None:
    """!
    @brief Memperbarui data perangkat keras eksisting berdasarkan ID Primary Key.
    """
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DATABASE_FILE_PATH) as db_connection:
        db_cursor = db_connection.cursor()
        db_cursor.execute('''UPDATE perangkat SET 
                     nama_perangkat=?, brand=?, ip_address=?, sn=?, lokasi_rak=?, pemilik=?, kondisi=?, tgl_update=? 
                     WHERE id=?''',
                  (device_name, brand_name, ip_address, serial_number, rack_location, pic_name, condition_status, current_timestamp, device_id))

def remove_device_by_id(device_id: int) -> None:
    """!
    @brief Menghapus record secara permanen dari database.
    """
    with sqlite3.connect(DATABASE_FILE_PATH) as db_connection:
        db_cursor = db_connection.cursor()
        db_cursor.execute('DELETE FROM perangkat WHERE id=?', (device_id,))

def export_dataframe_to_excel_bytes(dataframe_to_export: pd.DataFrame) -> bytes:
    """!
    @brief Mengonversi objek DataFrame Pandas ke dalam bentuk binary Excel (.xlsx).
    @return bytes Stream file raw yang siap dimuat oleh modul Download Streamlit.
    """
    byte_output_stream = io.BytesIO()
    with pd.ExcelWriter(byte_output_stream, engine='openpyxl') as excel_writer:
        dataframe_to_export.to_excel(excel_writer, index=False, sheet_name='Data_DC')
    return byte_output_stream.getvalue()

# ==========================================
# 3. KOMPONEN UI (MODULAR)
# ==========================================

def render_sidebar_navigation() -> str:
    """!
    @brief Merender antarmuka Navigasi pada Sidebar.
    @return str Indikator menu navigasi yang dipilih.
    """
    with st.sidebar:
        try:
            st.image("LogoKemhan.png", width=150) 
        except Exception:
            st.warning("Logo tidak ditemukan.")

        st.write("") 
        st.title("Pusdatin Kemhan")
        st.write("Sistem Inventaris DC")
        st.markdown("---")
        selected_menu = st.radio("NAVIGASI UTAMA", 
                        [MENU_ITEM_DASHBOARD, MENU_ITEM_ADD, MENU_ITEM_LIST],
                        label_visibility="collapsed")
        
        # Validasi Fallback aman
        if selected_menu is None:
            selected_menu = MENU_ITEM_DASHBOARD
            
        st.markdown("---")
        return str(selected_menu)

def render_dashboard_statistics(inventory_dataframe: pd.DataFrame) -> None:
    """!
    @brief Menampilkan 4 Kartu Metrik Statistik Utama pada menu Dashboard.
    """
    metric_col_total, metric_col_good, metric_col_mt, metric_col_broken = st.columns(4)
    
    with metric_col_total: 
        st.metric("Total Perangkat", f"{len(inventory_dataframe)}", "Unit")
    with metric_col_good: 
        st.metric(f"Kondisi {CONDITION_GOOD}", f"{len(inventory_dataframe[inventory_dataframe['kondisi'] == CONDITION_GOOD])}", "Unit")
    with metric_col_mt: 
        st.metric(CONDITION_MAINTENANCE, f"{len(inventory_dataframe[inventory_dataframe['kondisi'] == CONDITION_MAINTENANCE])}", "Unit")
    with metric_col_broken: 
        st.metric(f"Kondisi {CONDITION_BROKEN}", f"{len(inventory_dataframe[inventory_dataframe['kondisi'] == CONDITION_BROKEN])}", "Unit")
        
    st.markdown("<br>", unsafe_allow_html=True)

def render_dashboard_visualizations(inventory_dataframe: pd.DataFrame) -> None:
    """!
    @brief Merender Visualisasi Grafis (Pie Chart) distribusi Kondisi dan PIC secara dinamis.
    """
    if inventory_dataframe.empty:
        return
        
    st.markdown("---")
    chart_col_condition, chart_col_pic = st.columns(2)
    
    with chart_col_condition:
        condition_counts_df = inventory_dataframe['kondisi'].value_counts().reset_index()
        condition_counts_df.columns = ['Kondisi', 'Jumlah']
        condition_color_map = {CONDITION_GOOD: '#2ecc71', CONDITION_MAINTENANCE: '#f1c40f', CONDITION_BROKEN: '#e74c3c'}
        
        pie_chart_condition = px.pie(condition_counts_df, values='Jumlah', names='Kondisi', 
                      title='Distribusi Kondisi Perangkat', hole=0.4,
                      color='Kondisi', color_discrete_map=condition_color_map)
        pie_chart_condition.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(pie_chart_condition, use_container_width=True)
        
    with chart_col_pic:
        valid_pic_dataframe = inventory_dataframe[inventory_dataframe['pemilik'].astype(str).str.strip() != ""]
        if not valid_pic_dataframe.empty:
            pic_counts_df = valid_pic_dataframe['pemilik'].value_counts().reset_index()
            pic_counts_df.columns = ['PIC', 'Jumlah']
            
            pie_chart_pic = px.pie(pic_counts_df, values='Jumlah', names='PIC', 
                          title='Proporsi Penanggungjawab / PIC', hole=0.4)
            pie_chart_pic.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            pie_chart_pic.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(pie_chart_pic, use_container_width=True)

def render_inline_edit_form(inventory_dataframe: pd.DataFrame) -> None:
    """!
    @brief Membangkitkan formulir pembaruan data secara "Inline" ketika ID target aktif.
    """
    # Guard Clause: Hentikan fungsi jika mode edit tidak aktif
    if st.session_state.edit_id is None:
        return

    target_device_data = inventory_dataframe[inventory_dataframe['id'] == st.session_state.edit_id]
    
    # Guard Clause: Hentikan jika ID tidak ditemukan pada dataframe
    if target_device_data.empty:
        return

    device_record = target_device_data.iloc[0]
    with st.form("edit_form"):
        st.markdown(f"### ✏️ Edit: **{device_record['nama_perangkat']}**")
        
        # FORM VERTIKAL: Menghapus layout berkolom (st.columns), 
        # sehingga komponen merender urut vertikal penuh sesuai gaya desain baru
        input_edit_name = st.text_input(COL_DEVICE_NAME, value=str(device_record['nama_perangkat']))
        input_edit_brand = st.text_input(COL_BRAND, value=str(device_record['brand']))
        input_edit_ip = st.text_input(COL_IP_ADDRESS, value=str(device_record['ip_address']))
        input_edit_sn = st.text_input(COL_SERIAL_NUMBER, value=str(device_record['sn']))
        input_edit_rack = st.text_input(COL_RACK_LOCATION, value=str(device_record['lokasi_rak']))
        input_edit_pic = st.text_input("PIC / Penanggungjawab", value=str(device_record['pemilik']))
        
        condition_options = [CONDITION_GOOD, CONDITION_BROKEN, CONDITION_MAINTENANCE]
        current_condition_value = str(device_record['kondisi'])
        
        condition_index = 0
        if current_condition_value in condition_options:
            condition_index = condition_options.index(current_condition_value)
            
        input_edit_condition = st.selectbox(COL_CONDITION, condition_options, index=condition_index)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col_save, btn_col_cancel = st.columns([1, 6])
        
        if btn_col_save.form_submit_button("💾 SIMPAN"):
            final_condition = CONDITION_GOOD
            if input_edit_condition:
                final_condition = str(input_edit_condition)
                
            update_existing_device(st.session_state.edit_id, input_edit_name, input_edit_brand, input_edit_ip, input_edit_sn, input_edit_rack, input_edit_pic, final_condition)
            st.session_state.edit_id = None
            st.success("Data berhasil diperbarui!")
            st.rerun()
            
        if btn_col_cancel.form_submit_button("❌ BATAL"):
            st.session_state.edit_id = None
            st.rerun()

def render_interactive_data_table(inventory_dataframe: pd.DataFrame) -> None:
    """!
    @brief Merender *Smart Datatable* lengkap dengan filter Search Bar, Paginasi, dan Export Excel.
    """
    st.markdown("---")
    st.subheader("Daftar Perangkat TIK")
    
    # KONTROL PENCARIAN
    search_input_col, search_button_col = st.columns([10, 2])
    with search_input_col:
        search_query = st.text_input("Pencarian Data", placeholder="🔍 Ketik Nama, Brand, IP, SN, atau PIC...", label_visibility="collapsed")
    with search_button_col:
        st.button("Cari", use_container_width=True)

    if search_query:
        inventory_dataframe = inventory_dataframe[inventory_dataframe.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # RENDER FORM EDIT
    render_inline_edit_form(inventory_dataframe)

    # KONTROL PAGINASI
    inventory_dataframe = inventory_dataframe.reset_index(drop=True)
    if len(inventory_dataframe) == 0:
        st.info("Belum ada data atau tidak ditemukan hasil pencarian.")
        return

    st.write("") 

    pagination_col_per_page, pagination_col_page_num, pagination_col_info = st.columns([2, 2, 6])
    
    with pagination_col_per_page:
        selected_per_page = st.selectbox("Baris per halaman:", [10, 20, 50, 100], index=0)
        items_per_page = 10
        if selected_per_page:
            items_per_page = int(selected_per_page)
    
    total_pages = max(1, math.ceil(len(inventory_dataframe) / items_per_page))
    
    with pagination_col_page_num:
        selected_page_num = st.selectbox("Halaman ke:", range(1, total_pages + 1), index=0)
        current_page_number = 1
        if selected_page_num:
            current_page_number = int(selected_page_num)

    slice_start_index = (current_page_number - 1) * items_per_page
    slice_end_index = min(slice_start_index + items_per_page, len(inventory_dataframe))
    
    with pagination_col_info:
        st.markdown(f"<div style='text-align: right; padding-top: 32px; color: #bdc3c7;'>Menampilkan <b>{slice_start_index + 1} - {slice_end_index}</b> dari total <b>{len(inventory_dataframe)}</b> perangkat</div>", unsafe_allow_html=True)

    paginated_dataframe = inventory_dataframe.iloc[slice_start_index:slice_end_index]

    # RENDER TABEL (HTML)
    st.markdown(f"""
    <div class="table-header">
        <div style="flex: 0.5;">No</div>
        <div style="flex: 1.5;">{COL_DEVICE_NAME}</div>
        <div style="flex: 1;">{COL_BRAND}</div>
        <div style="flex: 1.2;">{COL_IP_ADDRESS}</div>
        <div style="flex: 1.2;">{COL_SERIAL_NUMBER}</div>
        <div style="flex: 1;">{COL_RACK_LOCATION}</div>
        <div style="flex: 1.2;">PIC / Penanggungjawab</div>
        <div style="flex: 1;">{COL_CONDITION}</div>
        <div style="flex: 1; text-align: center;">Aksi</div>
    </div>
    """, unsafe_allow_html=True)

    for index, row_data in paginated_dataframe.iterrows():
        # Menentukan warna lencana berdasarkan status
        if row_data['kondisi'] == CONDITION_GOOD:
            badge_color = "#2ecc71"
        elif row_data['kondisi'] == CONDITION_MAINTENANCE:
            badge_color = "#f1c40f"
        else:
            badge_color = "#e74c3c"
            
        display_number = slice_start_index + index + 1 
        
        with st.container():
            table_col_no, table_col_name, table_col_brand, table_col_ip, table_col_sn, table_col_rack, table_col_pic, table_col_cond, table_col_action = st.columns([0.5, 1.5, 1, 1.2, 1.2, 1, 1.2, 1, 1])
            
            table_col_no.markdown(f"<span>{display_number}</span>", unsafe_allow_html=True)
            table_col_name.markdown(f"<span>{row_data['nama_perangkat']}</span>", unsafe_allow_html=True)
            table_col_brand.markdown(f"<span>{row_data['brand']}</span>", unsafe_allow_html=True)
            table_col_ip.markdown(f"<span>{row_data['ip_address']}</span>", unsafe_allow_html=True)
            table_col_sn.markdown(f"<span>{row_data['sn']}</span>", unsafe_allow_html=True)
            table_col_rack.markdown(f"<span>{row_data['lokasi_rak']}</span>", unsafe_allow_html=True)
            table_col_pic.markdown(f"<span>{row_data['pemilik']}</span>", unsafe_allow_html=True)
            table_col_cond.markdown(f"<span style='background-color:{badge_color}; color:white !important; padding:2px 8px; border-radius:10px; font-size:12px;'>{row_data['kondisi']}</span>", unsafe_allow_html=True)
            
            with table_col_action:
                action_btn_edit, action_btn_delete = st.columns(2)
                if action_btn_edit.button("✏️", key=f"e_{row_data['id']}"):
                    st.session_state.edit_id = row_data['id']
                    st.rerun()
                if action_btn_delete.button("🗑️", key=f"d_{row_data['id']}"):
                    remove_device_by_id(int(row_data['id']))
                    st.rerun()
            st.markdown("<hr>", unsafe_allow_html=True)

    # KONTROL EXPORT DATA
    st.markdown("<br>", unsafe_allow_html=True)
    _, export_button_col = st.columns([8, 2])
    with export_button_col:
        excel_binary_data = export_dataframe_to_excel_bytes(inventory_dataframe)
        st.download_button(
            label="📥 Export Data (Excel)", 
            data=excel_binary_data, 
            file_name="inventaris_pusdatin.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            use_container_width=True
        )

# ==========================================
# 4. KONTROL HALAMAN & HELPER IMPORT
# ==========================================

def _process_dataframe_to_database(imported_dataframe: pd.DataFrame) -> int:
    """!
    @brief Menguraikan baris demi baris pada objek Excel impor dan menyimpannya ke Database.
    @param imported_dataframe Dataset hasil validasi dari file Excel yang terunggah.
    @return int Akumulasi jumlah data yang sukses diproses.
    """
    successful_import_count = 0
    for _, row_data in imported_dataframe.iterrows():
        imported_name = str(row_data[COL_DEVICE_NAME]).strip()
        imported_brand = str(row_data[COL_BRAND]).strip()
        imported_ip = str(row_data[COL_IP_ADDRESS]).strip()
        imported_sn = str(row_data[COL_SERIAL_NUMBER]).strip()
        imported_rack = str(row_data[COL_RACK_LOCATION]).strip()
        imported_pic = str(row_data[COL_PIC]).strip()
        
        imported_condition = str(row_data[COL_CONDITION]).strip().capitalize()
        if imported_condition not in [CONDITION_GOOD, CONDITION_BROKEN, CONDITION_MAINTENANCE]:
            imported_condition = CONDITION_GOOD
            
        if imported_name and imported_sn:
            insert_new_device(imported_name, imported_brand, imported_ip, imported_sn, imported_rack, imported_pic, imported_condition)
            successful_import_count += 1
            
    return successful_import_count

def _handle_excel_file_upload(uploaded_excel_file: Any) -> None:
    """!
    @brief Mengontrol logika utama penanganan berkas unggahan untuk Import Batch Excel.
    """
    try:
        parsed_excel_dataframe = pd.read_excel(uploaded_excel_file).fillna("")
        
        if not all(column in parsed_excel_dataframe.columns for column in TEMPLATE_COLUMNS):
            st.error("Struktur kolom tidak sesuai. Harap pastikan Anda menggunakan file Template yang diunduh pada Langkah 1.")
            return

        total_imported_rows = _process_dataframe_to_database(parsed_excel_dataframe)
        st.success(f"Proses selesai! Berhasil mengimpor {total_imported_rows} baris data perangkat ke dalam sistem.")
        
    except Exception as error_message:
        st.error(f"Terjadi kesalahan saat memproses file: {str(error_message)}")

def _render_manual_data_entry_form() -> None:
    """!
    @brief Merender formulir statis untuk menginput satu barang baru secara manual.
    """
    with st.form("add_form", clear_on_submit=True):
        st.write("Silakan isi data perangkat baru:")
        
        # FORM VERTIKAL: Semua input dibariskan turun ke bawah
        input_device_name = st.text_input(COL_DEVICE_NAME)
        input_brand = st.text_input(f"{COL_BRAND} / Merk")
        input_ip_address = st.text_input(COL_IP_ADDRESS)
        input_serial_number = st.text_input(f"{COL_SERIAL_NUMBER} (S/N)")
        input_rack_location = st.text_input(f"{COL_RACK_LOCATION} (Cth: Rak A1 - U20)")
        input_pic = st.text_input("PIC / Penanggungjawab") 
        input_condition = st.selectbox("Kondisi Fisik", [CONDITION_GOOD, CONDITION_BROKEN, CONDITION_MAINTENANCE])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("SIMPAN DATA", type="primary"):
            if input_device_name and input_serial_number: 
                final_condition_status = CONDITION_GOOD
                if input_condition:
                    final_condition_status = str(input_condition)
                    
                insert_new_device(input_device_name, input_brand, input_ip_address, input_serial_number, input_rack_location, input_pic, final_condition_status)
                st.success(f"Perangkat {input_device_name} berhasil disimpan!")
            else:
                st.error("Gagal! Nama Perangkat dan Serial Number wajib diisi.")

def _render_batch_excel_import_section() -> None:
    """!
    @brief Merender antarmuka unduhan template dan area unggah untuk migrasi Excel massal.
    """
    st.info("💡 **Tips Import:** Unduh template Excel yang disediakan, isi data sesuai kolom, lalu unggah kembali file tersebut ke sini.")
    
    st.markdown("#### Langkah 1: Unduh Template")
    empty_template_dataframe = pd.DataFrame(columns=TEMPLATE_COLUMNS)
    excel_template_bytes = export_dataframe_to_excel_bytes(empty_template_dataframe)
    
    st.download_button(
        label="📥 Unduh Template Import (.xlsx)", 
        data=excel_template_bytes, 
        file_name="Template_Import_DC.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.markdown("---")
    
    st.markdown("#### Langkah 2: Upload File Data")
    uploaded_excel_file = st.file_uploader("Unggah file template yang telah diisi (.xlsx)", type=['xlsx'])
    
    if uploaded_excel_file is not None:
        if st.button("🚀 Eksekusi Import Data", type="primary"):
            _handle_excel_file_upload(uploaded_excel_file)

def route_to_dashboard_page(active_menu: str) -> None:
    """!
    @brief Pengendali Alur Halaman Dashboard Utama.
    @param active_menu Menu navigasi yang sedang dipilih.
    """
    st.title("📊 Dashboard Inventaris")
    inventory_dataframe = fetch_all_inventory_data()

    if active_menu == MENU_ITEM_DASHBOARD:
        render_dashboard_statistics(inventory_dataframe)
        render_dashboard_visualizations(inventory_dataframe)
    else:
        render_interactive_data_table(inventory_dataframe)

def route_to_management_page() -> None:
    """!
    @brief Pengendali Alur Halaman "Tambah Data Baru" dan Import Data.
    """
    st.title("➕ Manajemen Perangkat Baru")
    
    ui_tab_manual, ui_tab_import = st.tabs(["Input Manual", "Import Massal (Excel)"])
    
    with ui_tab_manual:
        _render_manual_data_entry_form()

    with ui_tab_import:
        _render_batch_excel_import_section()

# ==========================================
# 5. ENTRY POINT UTAMA
# ==========================================

def main() -> None:
    """!
    @brief Fungsi Inisiasi Main Router.
    """
    inject_custom_theme_css()
    initialize_database()

    if 'edit_id' not in st.session_state:
        st.session_state.edit_id = None

    selected_menu = render_sidebar_navigation()

    if selected_menu in [MENU_ITEM_DASHBOARD, MENU_ITEM_LIST]:
        route_to_dashboard_page(selected_menu)
    elif selected_menu == MENU_ITEM_ADD:
        route_to_management_page()

if __name__ == '__main__':
    main()