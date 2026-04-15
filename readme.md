# Sistem Inventaris Data Center

Aplikasi berbasis web untuk mengelola dan mendata seluruh perangkat keras pada infrastruktur TIK di Data Center secara terpusat. Dikembangkan menggunakan bahasa pemrograman Python, antarmuka Streamlit, dan penyimpanan lokal SQLite.


## 📋 Prasyarat Sistem

- **Sistem Operasi**: Windows Server, Linux (Ubuntu/Debian), atau macOS.

- **Python**: Versi 3.12 atau yang lebih baru.

- **Package Manager**: `pipenv` (Sangat direkomendasikan untuk manajemen modul virtual) atau `pip` bawaan.


## 🛠️ Langkah-Langkah Persiapan (Local Environment)

Aplikasi ini menggunakan berkas `Pipfile` untuk menjaga konsistensi versi dependensi.


### Menggunakan Pipenv (Rekomendasi Utama)

1. **Instalasi Pipenv** (jika belum terpasang):

       pip install pipenv

2. **Instalasi Dependensi Proyek**: Buka terminal, arahkan ke direktori root proyek ini, kemudian jalankan:

       pipenv install

3. **Aktivasi Lingkungan Virtual**:

       pipenv shell

4. **Menjalankan Layanan**:

       streamlit run app.py


### Menggunakan Pip Standar (Tanpa Pipenv)

Jika aturan instansi membatasi penggunaan pipenv, gunakan metode instalasi manual:

1. **Instalasi Modul Esensial**:

       pip install streamlit==1.56.0 pandas==3.0.2 openpyxl plotly

2. **Menjalankan Layanan**:

       streamlit run app.py


## 🚀 Panduan Distribusi dan Deployment ke Server

Agar sistem inventaris dapat diakses oleh banyak divisi melalui jaringan secara terus-menerus (24/7), aplikasi harus dijalankan sebagai _Background Service_.


### 1. Deployment di Linux Server (Direkomendasikan)

Linux menggunakan **Systemd** untuk memastikan skrip Python otomatis aktif kembali (_auto-restart_) setiap kali server dinyalakan.

1. **Persiapan Berkas**: Salin semua direktori proyek ke dalam server (contoh rute: `/var/www/inventaris_dc`).

2. **Persiapan Dependensi**: Instal _library_ (Pandas, Streamlit, dsb.) sesuai instruksi di fase lokal.

3. **Membuat Berkas Konfigurasi Systemd**: Buat berkas layanan baru menggunakan _text editor_:

       sudo nano /etc/systemd/system/inventaris.service

   Salin dan tempel parameter berikut:

       [Unit]
       Description=Layanan Streamlit Inventaris Data Center
       After=network.target

       [Service]
       User=root
       WorkingDirectory=/var/www/inventaris_dc
       ExecStart=/usr/local/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
       Restart=always

       [Install]
       WantedBy=multi-user.target

4. **Eksekusi dan Inisialisasi**:

       sudo systemctl daemon-reload
       sudo systemctl start inventaris
       sudo systemctl enable inventaris

5. **Konfigurasi Akses Jaringan**: Pastikan port `8501` tidak diblokir oleh _firewall_ jaringan (`sudo ufw allow 8501`).


### 2. Deployment di Windows Server

Untuk OS berbasis Windows Server, distribusi dilangsungkan menggunakan bantuan aplikasi layanan pihak ketiga bernama **NSSM** (Non-Sucking Service Manager).

1. **Persiapan Berkas**: Letakkan _source code_ aplikasi pada direktori statis (contoh: `C:\inventaris_dc`).

2. **Persiapan Dependensi**: Buka _Command Prompt_ (CMD) atau _PowerShell_, arahkan ke folder proyek, dan jalankan perintah instalasi modul.

3. **Pemasangan NSSM**: Unduh utilitas NSSM, lalu ekstrak fail `nssm.exe` ke lokasi yang aman di partisi sistem.

4. **Pembuatan Windows Service**:

   - Buka CMD dengan hak akses **Run as Administrator**.

   - Arahkan kursor ke folder berisi `nssm.exe` dan jalankan:

         nssm install Inventaris

   - Jendela pengaturan GUI akan muncul. Lengkapi isian utamanya:

     - **Path**: Arahkan ke jalur `python.exe` (atau `streamlit.exe`) yang ada di sistem.

     - **Arguments**: `-m streamlit run app.py --server.port 8501 --server.address 0.0.0.0`

     - **Details / Directory**: Arahkan ke `C:\inventaris_dc`

   - Konfirmasi dengan menekan tombol **Install service**.

5. **Menjalankan Layanan**: Akses program sistem _Windows Services_ (`services.msc`), temukan layanan bernama **Inventaris**, klik kanan, lalu pilih opsi **Start**. Pastikan konfigurasi _Windows Defender Firewall_ telah mengizinkan jalur masuk pada port 8501.
