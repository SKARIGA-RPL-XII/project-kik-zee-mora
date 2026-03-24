# CONTOH IMPLEMENTASI DATABASE + GUI
## Tambahkan cell ini ke main.ipynb setelah training model

# === CELL: IMPORT DATABASE MODULE ===
```python
import os
from dotenv import load_dotenv
from database import init_database
from gui_with_database import GUIWithDatabase

# Load environment variables dari .env file
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Initialize database connection
db = init_database(SUPABASE_URL, SUPABASE_KEY)
print(f"Database initialized: {db is not None and db.client is not None}")
```

# === CELL: SAVE MODEL VERSION KE DATABASE ===
```python
# Simpan informasi model ke database
# (Jalankan setelah training model)

if db:
    model_params = {
        'weights': intercept.tolist() if isinstance(intercept, np.ndarray) else list(intercept),
        'bias': float(bias),
        'feature_columns': FEATURE_COLUMNS,
        'learning_rate': 0.01,
        'iterations': 8000
    }
    
    accuracy = (total_benar / len(y_test))
    
    db.save_model_version(
        model_name="LinearRegression_v1.0",
        accuracy=accuracy,
        learning_rate=0.01,
        iterations=8000,
        total_correct=total_benar,
        total_test=len(y_test),
        parameters=model_params
    )
    
    print(f"✓ Model version saved dengan akurasi {accuracy*100:.2f}%")
```

# === CELL: LAUNCH GUI DENGAN DATABASE ===
```python
# Jalankan GUI dengan integrasi database

if __name__ == "__main__":
    root = tk.Tk()
    tabCtrl = ttk.Notebook(root)
    tabCtrl.pack(expand=True, fill='both')
    
    # Gunakan class GUIWithDatabase yang sudah terintegrasi
    gui = GUIWithDatabase(
        root=root,
        tabCtrl=tabCtrl,
        model=ln,  # Model yang sudah di-train
        X_MIN=X_MIN,
        X_MAX=X_MAX,
        y_test=y_test,
        y_test_label=y_test_label,
        matrix=matrix,
        total_benar=total_benar
    )
    
    root.mainloop()
```

---

# CONTOH PENGGUNAAN DATABASE SELAIN GUI

# === Test Save Prediction ===
```python
# Test menyimpan prediction secara manual
db.save_prediction(
    student_name="Andi Wijaya",
    features={
        'Sleep_Duration': 7.5,
        'Study_Hours': 5,
        'Social_Media_Hours': 2.5,
        'Physical_Activity': 120
    },
    prediction_result=4,
    stress_category="Rendah",
    deskripsi="Tingkat stress normal, jaga pola hidup"
)
```

# === Test Get Predictions ===
```python
# Ambil history prediksi untuk student tertentu
predictions = db.get_predictions_by_student("Andi Wijaya", limit=10)
print(f"Total predictions: {len(predictions)}")
for pred in predictions:
    print(f"  - {pred['created_at']}: Stress Level {pred['prediction_result']} ({pred['stress_category']})")
```

# === Test Get Statistics ===
```python
# Ambil statistik untuk student
stats = db.get_statistics("Andi Wijaya")
print(f"Total Predictions: {stats['total_predictions']}")
print(f"Average Stress Level: {stats['average_stress_level']:.2f}")
print(f"Stress Categories:")
for cat, count in stats['stress_categories'].items():
    print(f"  - {cat}: {count}")
```

# === Test Student Management ===
```python
# Buat/update student
db.create_or_update_student("Budi Santoso", "budi@email.com")

# Get student info
student = db.get_student_info("Budi Santoso")
print(f"Student: {student['name']}")
print(f"Total Predictions: {student['total_predictions']}")
print(f"Last Prediction: {student['last_prediction_date']}")
```

# === Test Feedback System ===
```python
# Save feedback untuk prediction
predictions = db.get_predictions_by_student("Andi Wijaya", limit=1)
if predictions:
    pred_id = predictions[0]['id']
    db.save_feedback(
        prediction_id=pred_id,
        user_feedback="correct",
        notes="Prediksi akurat sesuai kondisi saya"
    )
    
    # Get accuracy dari feedback
    accuracy = db.get_prediction_accuracy()
    print(f"Feedback Accuracy: {accuracy:.2f}%")
```

---

# STRUCTURE FILE PROJECT SETELAH SELESAI

```
project-kik-zee-mora/
├── main.ipynb                  # Notebook utama dengan GUI integration
├── database.py                 # Module database (NEW)
├── gui_with_database.py        # GUI dengan database integration (NEW)
├── requirements.txt            # Original dependencies
├── requirements_with_db.txt    # Dependencies dengan Supabase (NEW)
├── .env                        # Environment variables (NEW - KEEP SECRET!)
├── .gitignore                  # Include .env di sini
├── supabase_setup.sql          # SQL schema untuk Supabase (NEW)
├── SUPABASE_SETUP.md          # Setup guide (NEW)
└── datasets/
    └── Student lifestyle data.csv
```

---

# TIPS & TRICKS

## 1. Error Handling Lokal
Jika database offline, aplikasi tetap berjalan tapi tidak menyimpan data:
```python
if db and db.client:  # Cek koneksi sebelum pakai
    db.save_prediction(...)
else:
    print("Database offline, prediksi tidak disimpan")
    # Tapi aplikasi tetap jalan!
```

## 2. Testing Tanpa Database Real
Gunakan mock database untuk testing:
```python
class MockDB:
    def save_prediction(self, *args, **kwargs):
        print("Mock: Prediksi disimpan")
        return True

db = MockDB()  # Untuk testing tanpa internet
```

## 3. Monitoring Database Usage
```python
# Check model yang sedang aktif
active_model = db.get_active_model()
print(f"Active Model: {active_model['model_name']}")
print(f"Accuracy: {active_model['accuracy']*100:.2f}%")
print(f"Created: {active_model['created_at']}")
```

## 4. Export Data ke CSV
```python
import pandas as pd

# Export semua predictions ke CSV
all_predictions = db.get_all_predictions(limit=1000)
df = pd.DataFrame(all_predictions)
df.to_csv('predictions_export.csv', index=False)
print("✓ Data exported ke predictions_export.csv")
```

---

# SECURITY BEST PRACTICES

1. **JANGAN** hardcode credentials di code
2. **JANGAN** push .env file ke git
3. **SELALU** gunakan environment variables
4. Untuk production, gunakan Supabase service role key di backend
5. Enable RLS (Row Level Security) untuk data protection

---

Jika ada pertanyaan atau error, cek:
- SUPABASE_SETUP.md untuk setup guide
- database.py untuk dokumentasi method
- gui_with_database.py untuk contoh implementasi

Happy Coding! 🚀