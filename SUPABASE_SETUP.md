# SETUP GUIDE - INTEGRASI SUPABASE KE PROJECT

## 📋 Step-by-Step Setup

### 1. **Buat Account Supabase** (Gratis)
   - Kunjungi: https://supabase.com
   - Daftar dengan GitHub atau email
   - Create new project

### 2. **Setup Database Schema**
   - Di Supabase dashboard, masuk ke **SQL Editor**
   - Copy-paste semua kode dari `supabase_setup.sql`
   - Jalankan dengan klik tombol "Run" atau Ctrl+Enter
   - Tunggu hingga semua table sudah dibuat ✓

### 3. **Ambil API Keys**
   - Klik menu **Settings** di supabase dashboard
   - Pilih **API** atau **Configuration**
   - Copy:
     - **Project URL** (NEXT_PUBLIC_SUPABASE_URL)
     - **Anon Key** (NEXT_PUBLIC_SUPABASE_ANON_KEY)

### 4. **Buat File `.env`** di root project
   Buat file bernama `.env` dengan isi:
   ```
   SUPABASE_URL=YOUR_PROJECT_URL
   SUPABASE_KEY=YOUR_ANON_KEY
   ```
   
   Contoh:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### 5. **Install Package Supabase**
   Jalankan di terminal:
   ```bash
   pip install supabase
   ```
   
   Atau jika ingin install sekaligus dengan dependencies lain:
   ```bash
   pip install -r requirements_with_db.txt
   ```

### 6. **Modifikasi main.ipynb**
   - Tambahkan cell di awal untuk load environment variables:
   ```python
   import os
   from dotenv import load_dotenv
   from database import init_database
   
   # Load environment variables
   load_dotenv()
   
   # Initialize database
   SUPABASE_URL = os.getenv('SUPABASE_URL')
   SUPABASE_KEY = os.getenv('SUPABASE_KEY')
   db = init_database(SUPABASE_URL, SUPABASE_KEY)
   ```

### 7. **Update GUI Class**
   - Update method `process()` di class GUI untuk:
     - Simpan hasil prediksi ke database
     - Ambil dan tampilkan history prediksi
     - Tampilkan statistik user
   
   Contoh integrasi di method `process()`:
   ```python
   # Setelah prediksi berhasil
   student_name = "John Doe"  # Input dari user
   db.create_or_update_student(student_name)
   db.save_prediction(student_name, values, pred_value, stress_category, deskripsi)
   db.update_student_prediction_count(student_name)
   ```

---

## 🧪 Testing

### Test Koneksi Database
```python
from database import init_database

db = init_database("YOUR_URL", "YOUR_KEY")

# Test save prediction
db.save_prediction(
    student_name="Test User",
    features={
        'Sleep_Duration': 7,
        'Study_Hours': 5,
        'Social_Media_Hours': 2,
        'Physical_Activity': 60
    },
    prediction_result=5,
    stress_category="Sedang",
    deskripsi="Test prediction"
)

# Test get predictions
predictions = db.get_predictions_by_student("Test User")
print(predictions)

# Test statistics
stats = db.get_statistics("Test User")
print(stats)
```

---

## 📊 Database Structure

### Tabel: `predictions`
Menyimpan setiap prediksi yang dilakukan user
- `id` - Primary key
- `student_name` - Nama student
- `sleep_duration`, `study_hours`, `social_media_hours`, `physical_activity` - Input features
- `prediction_result` - Hasil prediksi (1-10)
- `stress_category` - Kategori (Rendah/Sedang/Psikolog aja)
- `deskripsi` - Deskripsi lengkap
- `created_at` - Waktu prediksi

### Tabel: `students`
Profil student untuk tracking
- `id` - Primary key
- `name` - Nama student
- `email` - Email (optional)
- `total_predictions` - Jumlah prediksi yang pernah dilakukan
- `last_prediction_date` - Tanggal terakhir prediksi

### Tabel: `model_versions`
Tracking versi model untuk rollback jika diperlukan
- `id` - Primary key
- `model_name` - Nama model
- `accuracy` - Akurasi model
- `parameters` - Model parameters (JSON)
- `is_active` - Status model (aktif/tidak)

### Tabel: `feedbacks`
Feedback dari user tentang akurasi prediksi
- `prediction_id` - FK ke table predictions
- `user_feedback` - 'correct', 'incorrect', 'neutral'
- `notes` - Catatan tambahan

---

## 🚀 Best Practices

1. **Error Handling**: Semua method sudah punya try-except, jadi app tidak akan crash meski DB offline
2. **Async Operations**: Untuk app yang lebih responsif, pertimbangkan async database calls
3. **Authentication**: Enable RLS (Row Level Security) di tabel untuk keamanan production
4. **Rate Limiting**: Supabase free tier punya rate limit, monitor penggunaan

---

## ⚠️ Important Notes

- File `.env` harus di-exclude dari git! Tambahkan ke `.gitignore`:
  ```
  .env
  .env.local
  __pycache__/
  *.pyc
  ```

- Jangan hardcode API keys di code! Selalu gunakan environment variables

- Untuk production, gunakan service role key untuk backend operations

---

## 📚 Resources

- Supabase Docs: https://supabase.com/docs
- Python SDK: https://github.com/supabase-community/supabase-py
- REST API: https://supabase.com/docs/guides/api

Jika ada pertanyaan, baca dokumentasi Supabase atau tanya AI aja