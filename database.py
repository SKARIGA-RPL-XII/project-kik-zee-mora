"""
Database Module untuk Supabase Integration
Menghandle semua operasi database (CRUD) untuk predictions, students, dan model versions
"""

from datetime import datetime
import os
from typing import Dict, List, Optional
import json

# Try to import supabase, if it fails, we'll handle it gracefully
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Supabase tidak terinstall. Database features tidak akan bekerja: {e}")
    SUPABASE_AVAILABLE = False
    Client = None
    create_client = None

class SupabaseDB:
    """
    Class untuk mengelola koneksi dan operasi database Supabase
    """
    
    def __init__(self, url: str, key: str):
        """
        Args:
            url: Supabase Project URL (dari Supabase dashboard)
            key: Supabase Anon Key (dari Supabase dashboard)
        """
        if not SUPABASE_AVAILABLE:
            print("⚠️ Supabase tidak tersedia. Jalankan: pip install supabase")
            self.client = None
            return
            
        try:
            self.client = create_client(url, key)
            print("✓ Koneksi Supabase berhasil!")
        except Exception as e:
            print(f"✗ Gagal koneksi Supabase: {e}")
            self.client = None
    
    # ==================== PREDICTIONS TABLE ====================
    
    def save_prediction(self, student_name: str, features: Dict, 
                       prediction_result: int, stress_category: str, 
                       deskripsi: str) -> bool:
        """
        Simpan hasil prediksi ke database
        
        Args:
            student_name: Nama student yang melakukan prediksi
            features: Dict berisi {'Sleep_Duration', 'Study_Hours', 'Social_Media_Hours', 'Physical_Activity'}
            prediction_result: Hasil prediksi (1-10)
            stress_category: Kategori stress ('Rendah', 'Sedang', 'Psikolog aja')
            deskripsi: Deskripsi lengkap hasil prediksi
        
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            if not self.client:
                raise Exception("Database tidak terhubung! Cek .env file dan Supabase credentials.")
            
            data = {
                'student_name': student_name,
                'sleep_duration': float(features.get('Sleep_Duration', 0)),
                'study_hours': float(features.get('Study_Hours', 0)),
                'social_media_hours': float(features.get('Social_Media_Hours', 0)),
                'physical_activity': float(features.get('Physical_Activity', 0)),
                'prediction_result': int(prediction_result),
                'stress_category': stress_category,
                'deskripsi': deskripsi
            }
            
            response = self.client.table('predictions').insert(data).execute()
            
            # Validasi response
            if not response.data or len(response.data) == 0:
                raise Exception(f"Insert gagal: {response}")
            
            print(f"✓ Prediksi {student_name} berhasil disimpan!")
            return True
            
        except Exception as e:
            error_msg = f"✗ Error menyimpan prediksi: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def get_predictions_by_student(self, student_name: str, limit: int = 10) -> List[Dict]:
        try:
            if not self.client:
                return []
            
            response = self.client.table('predictions')\
                .select('*')\
                .eq('student_name', student_name)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"✗ Error ambil prediksi: {e}")
            return []
    
    def get_predictions_by_student_and_date(self, student_name: str, start_date: str = None, end_date: str = None, limit: int = 100) -> List[Dict]:
        try:
            if not self.client:
                return []
            
            # Query dasar
            query = self.client.table('predictions')\
                .select('*')\
                .eq('student_name', student_name)
            
            # Filter tanggal jika ada
            if start_date:
                query = query.gte('created_at', f"{start_date}T00:00:00")
            
            if end_date:
                query = query.lte('created_at', f"{end_date}T23:59:59")
            
            # Urutkan dan batasi hasil
            response = query.order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"✗ Error ambil prediksi dengan filter tanggal: {e}")
            return []
    
    def get_all_predictions(self, limit: int = 100) -> List[Dict]:
        """
        Ambil semua prediksi terbaru
        
        Args:
            limit: Jumlah data yang diambil
        
        Returns:
            List of all prediction records
        """
        try:
            if not self.client:
                return []
            
            response = self.client.table('predictions')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"✗ Error ambil semua prediksi: {e}")
            return []
    
    def get_statistics(self, student_name: Optional[str] = None) -> Dict:
        try:
            if not self.client:
                return {}
            
            if student_name:
                predictions = self.get_predictions_by_student(student_name, limit=1000)
            else:
                predictions = self.get_all_predictions(limit=1000)
            
            if not predictions:
                return {}
            
            stats = {
                'total_predictions': len(predictions),
                'stress_categories': {},
                'average_stress_level': 0,
            }
            
            stress_levels = []
            for pred in predictions:
                category = pred['stress_category']
                stats['stress_categories'][category] = stats['stress_categories'].get(category, 0) + 1
                stress_levels.append(pred['prediction_result'])
            
            stats['average_stress_level'] = sum(stress_levels) / len(stress_levels) if stress_levels else 0
            
            return stats
            
        except Exception as e:
            print(f"✗ Error ambil statistik: {e}")
            return {}
    
    # ==================== STUDENTS TABLE ====================
    
    def create_or_update_student(self, name: str, email: Optional[str] = None) -> bool:
        """
        Buat atau update profil student
        
        Args:
            name: Nama student
            email: Email student (optional)
        
        Returns:
            bool: True jika berhasil
        """
        try:
            if not self.client:
                raise Exception("Database tidak terhubung!")
            
            # Cek apakah student sudah ada
            existing = self.client.table('students')\
                .select('*')\
                .eq('name', name)\
                .execute()
            
            if existing.data:
                # Update existing
                self.client.table('students')\
                    .update({'updated_at': datetime.now().isoformat()})\
                    .eq('name', name)\
                    .execute()
            else:
                # Create new
                data = {
                    'name': name,
                    'email': email,
                    'total_predictions': 0
                }
                response = self.client.table('students').insert(data).execute()
                if not response.data:
                    raise Exception(f"Gagal membuat student: {response}")
            
            print(f"✓ Student {name} berhasil dibuat/diupdate!")
            return True
            
        except Exception as e:
            error_msg = f"✗ Error buat/update student: {str(e)}"
            print(error_msg)
            return False
    
    def update_student_prediction_count(self, student_name: str) -> bool:
        """
        Update jumlah prediksi dan tanggal terakhir prediksi untuk student
        
        Args:
            student_name: Nama student
        
        Returns:
            bool: True jika berhasil
        """
        try:
            if not self.client:
                return False
            
            # Ambil data student
            response = self.client.table('students')\
                .select('total_predictions')\
                .eq('name', student_name)\
                .execute()
            
            if response.data:
                current_count = response.data[0]['total_predictions'] or 0
                update_response = self.client.table('students')\
                    .update({
                        'total_predictions': current_count + 1,
                        'last_prediction_date': datetime.now().isoformat()
                    })\
                    .eq('name', student_name)\
                    .execute()
                
                if update_response.data:
                    return True
                else:
                    print(f"✗ Gagal update student count: {update_response}")
                    return False
            
            print(f"✗ Student {student_name} tidak ditemukan")
            return False
            
        except Exception as e:
            print(f"✗ Error update prediction count: {e}")
            return False
    
    def get_student_info(self, student_name: str) -> Optional[Dict]:
        """
        Ambil informasi student
        
        Args:
            student_name: Nama student
        
        Returns:
            Student record or None
        """
        try:
            if not self.client:
                return None
            
            response = self.client.table('students')\
                .select('*')\
                .eq('name', student_name)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"✗ Error ambil info student: {e}")
            return None
    
    # ==================== MODEL VERSIONS TABLE ====================
    
    def save_model_version(self, model_name: str, accuracy: float, 
                          learning_rate: float, iterations: int, 
                          total_correct: int, total_test: int,
                          parameters: Dict) -> bool:
        """
        Simpan versi model untuk tracking
        
        Args:
            model_name: Nama model
            accuracy: Akurasi model (0-1)
            learning_rate: Learning rate yang digunakan
            iterations: Jumlah iterasi training
            total_correct: Total prediksi benar
            total_test: Total data test
            parameters: Model parameters (weights, bias, dll)
        
        Returns:
            bool: True jika berhasil
        """
        try:
            if not self.client:
                return False
            
            # Set model lain menjadi inactive
            try:
                self.client.table('model_versions')\
                    .update({'is_active': False})\
                    .eq('is_active', True)\
                    .execute()
            except Exception as update_error:
                print(f"⚠️ Warning nonaktifkan model lama gagal: {update_error}")
            
            data = {
                'model_name': model_name,
                'accuracy': float(accuracy),
                'learning_rate': float(learning_rate),
                'iterations': int(iterations),
                'total_correct_predictions': int(total_correct),
                'total_test_data': int(total_test),
                'parameters': parameters,
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }
            
            self.client.table('model_versions').insert(data).execute()
            print(f"✓ Model version {model_name} berhasil disimpan!")
            return True
            
        except Exception as e:
            error_text = str(e)
            print(f"✗ Error simpan model version: {error_text}")
            if 'row-level security' in error_text.lower():
                print("Kemungkinan penyebab: RLS/FORCE RLS masih aktif di tabel model_versions atau key yang dipakai adalah anon key.")
                print("Solusi cepat: jalankan SQL reset policy + DISABLE/NO FORCE RLS, atau gunakan service_role key untuk aplikasi backend/desktop.")
            return False
    
    def get_active_model(self) -> Optional[Dict]:
        """
        Ambil model yang sedang aktif
        
        Returns:
            Active model record or None
        """
        try:
            if not self.client:
                return None
            
            response = self.client.table('model_versions')\
                .select('*')\
                .eq('is_active', True)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"✗ Error ambil active model: {e}")
            return None
    
    # ==================== FEEDBACKS TABLE ====================
    
    def save_feedback(self, prediction_id: int, user_feedback: str, 
                     notes: Optional[str] = None) -> bool:
        """
        Simpan feedback tentang akurasi prediksi
        
        Args:
            prediction_id: ID dari prediction yang di-feedback
            user_feedback: 'correct', 'incorrect', atau 'neutral'
            notes: Catatan tambahan (optional)
        
        Returns:
            bool: True jika berhasil
        """
        try:
            if not self.client:
                return False
            
            data = {
                'prediction_id': int(prediction_id),
                'user_feedback': user_feedback,
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
            
            self.client.table('feedbacks').insert(data).execute()
            print(f"✓ Feedback berhasil disimpan!")
            return True
            
        except Exception as e:
            print(f"✗ Error simpan feedback: {e}")
            return False
    
    def get_prediction_accuracy(self) -> float:
        """
        Hitung akurasi dari feedback yang ada
        
        Returns:
            Akurasi sebagai persentase (0-100)
        """
        try:
            if not self.client:
                return 0
            
            feedbacks = self.client.table('feedbacks')\
                .select('user_feedback')\
                .execute()
            
            if not feedbacks.data:
                return 0
            
            correct_count = sum(1 for f in feedbacks.data if f['user_feedback'] == 'correct')
            accuracy = (correct_count / len(feedbacks.data)) * 100
            
            return accuracy
            
        except Exception as e:
            print(f"✗ Error hitung akurasi: {e}")
            return 0


# ==================== HELPER FUNCTION ====================

def init_database(url: str, key: str) -> SupabaseDB:
    """
    Inisialisasi koneksi database
    
    Args:
        url: Supabase Project URL
        key: Supabase Anon Key
    
    Returns:
        SupabaseDB instance
    """
    if not SUPABASE_AVAILABLE:
        print("⚠️ Supabase tidak tersedia. Akan membuat instance tanpa koneksi...")
    return SupabaseDB(url, key)
