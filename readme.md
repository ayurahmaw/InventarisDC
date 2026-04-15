# **Sistem Inventaris Data Center **

Aplikasi berbasis web interaktif untuk mengelola inventaris perangkat keras infrastruktur TIK di Data Center secara terpusat. Dibangun menggunakan **Python**, **Streamlit**, dan **SQLite**.


## **📋 Prasyarat Sistem**

- **Sistem Operasi**: Windows, Linux, atau macOS.

- **Python**: Versi 3.12 atau lebih baru.

- **Package Manager**: pipenv (Disarankan) atau pip standar.


## **🛠️ Langkah-Langkah Persiapan (Local Development)**

Proyek ini menggunakan Pipfile untuk manajemen dependensi. Sangat disarankan menggunakan pipenv agar versi _library_ terisolasi dan sesuai.


### **Opsi A: Menggunakan Pipenv (Rekomendasi)**

1. **Install Pipenv** (jika belum ada di sistem):\
   pip install pipenv

2. **Install Dependensi**: Buka terminal di dalam folder proyek ini, lalu jalankan:\
   pipenv install

3. **Aktifkan Virtual Environment**:\
   pipenv shell

4. **Jalankan Aplikasi**:\
   streamlit run app.py


### **Opsi B: Menggunakan Pip Biasa (Tanpa Pipenv)**

Jika kamu tidak menggunakan pipenv, jalankan perintah berikut di terminal:

1. Install modul yang dibutuhkan:\
   pip install streamlit==1.56.0 pandas==3.0.2 openpyxl

2. Jalankan aplikasi:\
   streamlit run app.py


## **🚀 Panduan Deployment (Distribusi ke Server Target)**

Agar aplikasi dapat diakses 24/7 oleh pengguna lain melalui jaringan, aplikasi perlu di-_deploy_ sebagai _Background Service_ di server.


### **1. Deployment di Linux Server (Ubuntu/Debian) - Paling Disarankan**

Metode terbaik di Linux adalah menggunakan **Systemd** untuk memastikan aplikasi otomatis menyala saat server _restart_.

1. **Pindahkan File**: Pindahkan seluruh file proyek ke server (misal di /var/www/inventaris\_dc).

2. **Install Python & Dependensi**: Lakukan langkah instalasi dependensi seperti di atas.

3. **Buat Service Systemd**:\
   Buat file konfigurasi service baru:\
   sudo nano /etc/systemd/system/inventaris.service\
   \
   Isi file tersebut dengan konfigurasi berikut:\
   \[Unit]\
   Description=Streamlit Inventaris App\
   After=network.target\
   \
   \[Service]\
   User=root\
   WorkingDirectory=/var/www/inventaris\_dc\
   ExecStart=/usr/local/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0\
   Restart=always\
   \
   \[Install]\
   WantedBy=multi-user.target

4. **Jalankan Service**:\
   sudo systemctl daemon-reload\
   sudo systemctl start inventaris\
   sudo systemctl enable inventaris

5. **Akses Web**: Buka port 8501 pada firewall (sudo ufw allow 8501). Web dapat diakses melalui http\://IP-SERVER-LINUX:8501.


### **2. Deployment di Windows Server**

Di Windows Server, kita bisa menggunakan **NSSM** (Non-Sucking Service Manager) untuk mengubah perintah streamlit run menjadi _Windows Service_.

1. **Pindahkan File**: Taruh folder aplikasi di direktori yang aman (misal C:\inventaris\_dc).

2. **Install Dependensi**: Buka CMD/PowerShell, arahkan ke folder tersebut, dan install library yang dibutuhkan.

3. **Download NSSM**: Unduh NSSM dari website resminya dan ekstrak file .exe nya.

4. **Install Service**:

- Buka CMD sebagai **Administrator**.

- Arahkan ke folder tempat nssm.exe berada dan jalankan:\
  nssm install InventarisStreamlit

- Akan muncul jendela GUI. Konfigurasi bagian berikut:

* **Path**: Lokasi python.exe atau streamlit.exe kamu.

* **Arguments**: -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0

* **Details / Directory**: C:\inventaris\_dc

- Klik tombol **Install service**.

5. **Jalankan Service**: Buka _Windows Services_ (services.msc), cari **InventarisStreamlit**, lalu klik **Start**. Pastikan port 8501 dibuka di _Windows Defender Firewall_.


## **📂 Struktur Direktori Proyek**

- app.py: File utama aplikasi web (berisi _frontend_ dan _backend_).

- inventaris\_v2.db: File _database_ SQLite (otomatis terbuat jika belum ada).

- Logo.jpg: File gambar logo yang dirender pada sidebar.

- Pipfile & Pipfile.lock: Manajemen dependensi environment.
