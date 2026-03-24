## 📋 Deskripsi Proyek
Proyek sederhana untuk Project Akhir AI di SMK PGRI 3 Malang.

## 🚀 Cara Menjalankan

### Syarat
- Python 3.8+
- pip (Python package manager)

### Instalasi
```bash
# Clone repository
git clone https://github.com/SKARIGA-RPL-XII/project-kik-zee-mora
cd project-kik-zee-mora

# Setup otomatis (membuat .venv + install dependencies standar)
.\setup.ps1
```

### Opsi Setup
```bash
# Jika menggunakan fitur database/supabase
.\setup.ps1 -WithDatabase

# Jika ingin buat ulang venv dari nol
.\setup.ps1 -RecreateVenv
```

### Aktivasi Virtual Environment
```bash
.\.venv\Scripts\Activate.ps1
```

### Instalasi Manual (Opsional)
```bash
# Buat virtual environment
python -m venv .venv

# Aktivasi venv
.\.venv\Scripts\Activate.ps1

# Install dependency
pip install -r requirements.txt
```

### Menjalankan Aplikasi
```bash
run via jupyter notebook
```

## 📁 Struktur Proyek
```
.
├──datasets
├──── Student lifestyle data.csv
├── main.ipynb
├── requirements.txt
├── requirements_with_db.txt
├── setup.ps1
└── README.md
```

## 🛠️ Teknologi yang Digunakan
- Python
- Jupyter Notebook
- Pandas
- Seaborn
- Matplotlib
- Tkinter
- Numpy

## 📝 Catatan
Terimakasih karena sudah datang ke repo ini