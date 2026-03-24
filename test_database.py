"""
Test script untuk diagnostik database connection dan insert operations
Jalankan: python test_database.py
"""

import os
from dotenv import load_dotenv
from database import init_database

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

# 1. Load environment variables
print("\n1. Loading environment variables from .env...")
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL:
    print("  [FAIL] SUPABASE_URL tidak ditemukan di .env")
else:
    print(f"  [OK] SUPABASE_URL: {SUPABASE_URL[:50]}...")

if not SUPABASE_KEY:
    print("  [FAIL] SUPABASE_KEY tidak ditemukan di .env")
else:
    print(f"  [OK] SUPABASE_KEY: {SUPABASE_KEY[:20]}...")

# 2. Initialize database
print("\n2. Initializing database connection...")
db = init_database(SUPABASE_URL, SUPABASE_KEY)

if not db or not db.client:
    print("  [FAIL] Gagal terhubung ke Supabase Database")
    print("  Pastikan:")
    print("     - .env file ada di root project")
    print("     - SUPABASE_URL benar")
    print("     - SUPABASE_KEY benar")
    exit(1)

print("  [OK] Koneksi Supabase berhasil!")

# 3. Test insert student
print("\n3. Testing student insert...")
try:
    result = db.create_or_update_student("Test User 123", "test@example.com")
    if result:
        print("  [OK] Student berhasil dibuat/diupdate")
    else:
        print("  [FAIL] Gagal membuat/update student")
except Exception as e:
    print(f"  [FAIL] Error: {str(e)}")

# 4. Test insert prediction
print("\n4. Testing prediction insert...")
try:
    features = {
        'Sleep_Duration': 7.5,
        'Study_Hours': 5.0,
        'Social_Media_Hours': 2.5,
        'Physical_Activity': 120.0
    }
    result = db.save_prediction(
        student_name="Test User 123",
        features=features,
        prediction_result=5,
        stress_category="Sedang",
        deskripsi="Test prediction dari test script"
    )
    if result:
        print("  [OK] Prediction berhasil disimpan")
    else:
        print("  [FAIL] Gagal menyimpan prediction")
except Exception as e:
    print(f"  [FAIL] Error: {str(e)}")

# 5. Test get predictions
print("\n5. Testing get predictions by student...")
try:
    predictions = db.get_predictions_by_student("Test User 123", limit=5)
    if predictions:
        print(f"  [OK] Ditemukan {len(predictions)} prediction(s)")
        for pred in predictions[:1]:
            print(f"     - {pred['created_at']}: Stress Level {pred['prediction_result']}")
    else:
        print("  [FAIL] Tidak ada prediction ditemukan")
except Exception as e:
    print(f"  [FAIL] Error: {str(e)}")

# 6. Test get statistics
print("\n6. Testing get statistics...")
try:
    stats = db.get_statistics("Test User 123")
    if stats:
        print(f"  [OK] Statistics retrieved:")
        print(f"     - Total Predictions: {stats.get('total_predictions', 0)}")
        print(f"     - Average Stress Level: {stats.get('average_stress_level', 0):.2f}")
        print(f"     - Categories: {stats.get('stress_categories', {})}")
    else:
        print("  [FAIL] Gagal mengambil statistics")
except Exception as e:
    print(f"  [FAIL] Error: {str(e)}")

print("\n" + "=" * 60)
print("TEST SELESAI")
print("=" * 60)
print("\nJika semua test PASS, database siap digunakan!")
print("Jika ada yang FAIL, cek error message di atas.")
