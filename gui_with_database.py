"""
GUI dengan Database Integration
Menambahkan fitur:
- Simpan history prediksi
- View history prediksi
- Tampilkan statistik student
- Feedback untuk prediksi
"""

import tkinter as tk 
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Try to import database module
try:
    from database import init_database
    DB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Database module tidak bisa diimport: {e}")
    DB_AVAILABLE = False
    init_database = None

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Initialize database
db = init_database(SUPABASE_URL, SUPABASE_KEY)

FEATURE_COLUMNS = ['Sleep_Duration', 'Study_Hours', 'Social_Media_Hours', 'Physical_Activity']


class GUIWithDatabase:
    """
    Enhanced GUI dengan integrasi database
    - Tab 1: Uji Coba Data (Prediksi)
    - Tab 2: Informasi Model
    - Tab 3: History Prediksi (NEW)
    - Tab 4: Statistik Student (NEW)
    """
    
    def __init__(self, root, tabCtrl, model, X_MIN, X_MAX, y_test, y_test_label, matrix, total_benar):
        """
        Args:
            root: Tkinter root window
            tabCtrl: Tkinter Notebook widget
            model: Lightning Regression model object (ln)
            X_MIN, X_MAX: Normalisasi parameters
            y_test, y_test_label: Test data
            matrix: Confusion matrix
            total_benar: Total correct predictions
        """
        self.root = root 
        self.tabCtrl = tabCtrl
        self.model = model
        self.X_MIN = X_MIN
        self.X_MAX = X_MAX
        self.y_test = y_test
        self.y_test_label = y_test_label
        self.matrix = matrix
        self.total_benar = total_benar
        
        self.root.geometry("600x800")
        self.root.title("Stress Level Predictor - v2.0")
        self.bg = '#e7eaeb'
        self.header_fonts = ("Segoe UI", 15, 'bold')
        self.form_fonts = ("Helvetica", 12, "bold")
        self.root.resizable(False, False)
        
        # Current student name
        self.current_student = tk.StringVar()
        
        self.create_tabs()
    
    def create_tabs(self):
        """Buat semua tab untuk GUI"""
        # TAB 1: PREDIKSI
        self._create_prediction_tab()
        
        # TAB 2: INFORMASI MODEL
        self._create_model_info_tab()
        
        # TAB 3: HISTORY PREDIKSI
        self._create_history_tab()
        
        # TAB 4: STATISTIK
        self._create_statistics_tab()
    
    # ==================== TAB 1: PREDIKSI ====================
    
    def _create_prediction_tab(self):
        """Tab untuk melakukan prediksi stress level"""
        tab1 = tk.Frame(self.tabCtrl, bg=self.bg)
        self.tabCtrl.add(tab1, text="Uji Coba Data")
        
        # Header
        header = tk.Frame(tab1, borderwidth=1, height=50, bg="#37c466", relief='solid')
        header.pack(fill='x', padx=10, pady=20)
        tk.Label(header, text="PREDIKSI TINGKAT STRESS", font=self.header_fonts, 
                fg='#FFFFFF', bg='#37c466').pack()
        
        # Input Student Name
        form = tk.Frame(tab1, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Nama Anda", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_name = tk.Entry(form, width=30)
        self.entry_name.pack(side='right')
        
        # Input Features
        form = tk.Frame(tab1, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Durasi Jam Tidur /Hari", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_sleep = tk.Entry(form, width=30)
        self.entry_sleep.pack(side='right')
        
        form = tk.Frame(tab1, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Durasi Jam Belajar /Hari", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_study = tk.Entry(form, width=30)
        self.entry_study.pack(side='right')
        
        form = tk.Frame(tab1, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Durasi Sosial Media /Hari", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_doomscroll = tk.Entry(form, width=30)
        self.entry_doomscroll.pack(side='right')
        
        form = tk.Frame(tab1, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Menit Aktifitas Fisik /Minggu", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_sports = tk.Entry(form, width=30)
        self.entry_sports.pack(side='right')
        
        # Buttons
        frame_button = tk.Frame(tab1, bg=self.bg)
        frame_button.pack(fill='both', pady=10)
        tk.Button(frame_button, text="CEK STRESS LEVEL", width=45, height=2, 
                 font=("Segoe UI", 10, "bold"), fg='white', bg="#1bb34e", 
                 command=self._process_prediction).pack()
        
        frame_button = tk.Frame(tab1, bg=self.bg)
        frame_button.pack(fill='both', pady=2)
        tk.Button(frame_button, text="CLEAR INPUT", width=45, height=2, 
                 font=("Segoe UI", 10, "bold"), fg='white', bg="#09a8d8", 
                 command=self._clear_inputs).pack()
    
    def _get_prediction_inputs(self):
        """Ambil input dari form dan validasi"""
        student_name = self.entry_name.get().strip()
        if not student_name:
            messagebox.showerror("Error", "Silahkan masukkan nama Anda!")
            return None, None
        
        values = {
            "Sleep_Duration": self.entry_sleep.get().strip(),
            "Study_Hours": self.entry_study.get().strip(),
            "Social_Media_Hours": self.entry_doomscroll.get().strip(),
            "Physical_Activity": self.entry_sports.get().strip(),
        }
        
        if any(v == "" for v in values.values()):
            messagebox.showerror("Error", "Silahkan isi semua inputan!")
            return None, None
        
        try:
            return student_name, {k: float(v) for k, v in values.items()}
        except ValueError:
            messagebox.showerror("Error", "Semua input harus berupa angka!")
            return None, None
    
    def _normalize_features(self, df):
        """Normalisasi features sesuai training data"""
        denom = (self.X_MAX - self.X_MIN).replace(0, 1)
        return (df - self.X_MIN) / denom
    
    def _process_prediction(self):
        """Proses prediksi dan simpan ke database"""
        student_name, values = self._get_prediction_inputs()
        if student_name is None or values is None:
            return
        
        try:
            # Prepare data for prediction
            df_baru = pd.DataFrame([values], columns=FEATURE_COLUMNS)
            df_baru = self._normalize_features(df_baru)
            
            # Get prediction from model
            pred = self.model.predict(df_baru)
            pred_value = int(np.clip(np.round(pred[0]), 1, 10))
            
            # Determine stress category
            batas_rendah = np.percentile(self.y_test, 33)
            batas_sedang = np.percentile(self.y_test, 66)
            
            if pred_value <= batas_rendah:
                stress_category = 'Rendah'
            elif pred_value <= batas_sedang:
                stress_category = "Sedang"
            else:
                stress_category = "Psikolog aja"
            
            # Description mapping
            deskripsi_map = {
                1: "Stress Level Anda Rendah, Sangat Baik, Tetap Jaga Pola Hidup Anda",
                2: "Stress Level Anda Rendah, Sangat Baik, Tetap Jaga Pola Hidup Anda",
                3: "Stress Level Anda Normal, Hindari Kebiasaan Buruk",
                4: "Stress Level Anda Normal, Hindari Kebiasaan Buruk",
                5: "Stress Level Anda Medium, Perbaiki Kebiasaan Buruk Anda!",
                6: "Stress Level Anda Cukup Tinggi, Perbaiki Kebiasaan Buruk Anda!",
                7: "Stress Level Anda Cukup Tinggi, Perbaiki Kebiasaan Buruk Anda!",
                8: "Stress Level Anda Tinggi, Perbaiki Pola Hidup Anda",
                9: "Stress Level Anda Sangat Tinggi, Anda Harus Segera Memperbaiki Kebiasaan Buruk Anda",
                10: "Stress Level Anda Sangat Tinggi, Anda Harus Segera Memperbaiki Kebiasaan Buruk Anda",
            }
            deskripsi = deskripsi_map.get(pred_value, "Hasil tidak tersedia")
            
            # Save to database
            if db and db.client:
                try:
                    db.create_or_update_student(student_name)
                    db.save_prediction(student_name, values, pred_value, stress_category, deskripsi)
                    db.update_student_prediction_count(student_name)
                except Exception as db_error:
                    messagebox.showwarning("Database Error", 
                                         f"Data tidak tersimpan ke database:\n{str(db_error)}\n\nPrediksi tetap ditampilkan.")
            elif not db or not db.client:
                messagebox.showwarning("Database Not Connected", 
                                     "Database tidak terhubung. Cek .env file dan Supabase credentials.")
            
            messagebox.showinfo("Hasil Prediksi", 
                              f"Tingkatan Stress Anda: {pred_value}\n\n{deskripsi}")
            
            # Clear inputs
            self._clear_inputs()
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi error: {str(e)}")
    
    def _clear_inputs(self):
        """Bersihkan semua input"""
        self.entry_name.delete(0, tk.END)
        self.entry_sleep.delete(0, tk.END)
        self.entry_study.delete(0, tk.END)
        self.entry_doomscroll.delete(0, tk.END)
        self.entry_sports.delete(0, tk.END)
        self.entry_name.focus_set()
    
    # ==================== TAB 2: INFORMASI MODEL ====================
    
    def _create_model_info_tab(self):
        """Tab untuk menampilkan informasi model"""
        tab2 = tk.Frame(self.tabCtrl, bg=self.bg)
        self.tabCtrl.add(tab2, text="Informasi Model")
        
        header2 = tk.Frame(tab2, bg="#13a5af", borderwidth=1, height=50, relief='solid')
        header2.pack(fill='x', pady=20, padx=10)
        tk.Label(header2, text="INFORMASI MODEL", font=self.header_fonts, 
                fg='#FFFFFF', bg='#13a5af').pack()
        
        accuracy = (self.total_benar / len(self.y_test)) * 100
        
        # Display model info
        form2 = tk.Frame(tab2, bg=self.bg, relief="groove", borderwidth=1)
        form2.pack(fill='x', padx=5, pady=20)
        tk.Label(form2, text="Akurasi Model: ", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        tk.Label(form2, text=f"{accuracy:.2f}%", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='right')
        
        form2 = tk.Frame(tab2, bg=self.bg, relief="groove", borderwidth=1)
        form2.pack(fill='x', padx=5, pady=20)
        tk.Label(form2, text="Jumlah Data Train: ", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        tk.Label(form2, text='80%', bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='right')
        
        form2 = tk.Frame(tab2, bg=self.bg, relief="groove", borderwidth=1)
        form2.pack(fill='x', padx=5, pady=20)
        tk.Label(form2, text="Jumlah Data Test: ", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        tk.Label(form2, text="20%", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='right')
        
        form2 = tk.Frame(tab2, bg=self.bg, relief="groove", borderwidth=1)
        form2.pack(fill='x', padx=5, pady=20)
        tk.Label(form2, text="Model Type: ", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        tk.Label(form2, text="Linear Regression", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='right')
    
    # ==================== TAB 3: HISTORY PREDIKSI ====================
    
    def _create_history_tab(self):
        """Tab untuk menampilkan history prediksi"""
        tab3 = tk.Frame(self.tabCtrl, bg=self.bg)
        self.tabCtrl.add(tab3, text="History Prediksi")
        
        header3 = tk.Frame(tab3, bg="#ff9500", borderwidth=1, height=50, relief='solid')
        header3.pack(fill='x', pady=20, padx=10)
        tk.Label(header3, text="HISTORY PREDIKSI ANDA", font=self.header_fonts, 
                fg='#FFFFFF', bg='#ff9500').pack()
        
        # Input untuk query student
        form = tk.Frame(tab3, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Masukkan Nama:", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_search_name = tk.Entry(form, width=30)
        self.entry_search_name.pack(side='left', padx=10)
        tk.Button(form, text="CARI", width=10, height=1, font=("Segoe UI", 10, "bold"), 
                 fg='white', bg="#ff9500", command=self._load_history).pack(side='left')
        
        # Frame untuk tabel history
        self.history_frame = tk.Frame(tab3, bg=self.bg)
        self.history_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _load_history(self):
        """Load dan tampilkan history prediksi"""
        student_name = self.entry_search_name.get().strip()
        if not student_name:
            messagebox.showerror("Error", "Silahkan masukkan nama!")
            return
        
        try:
            # Clear previous data
            for widget in self.history_frame.winfo_children():
                widget.destroy()
            
            # Get predictions from database
            predictions = db.get_predictions_by_student(student_name, limit=20)
            
            if not predictions:
                tk.Label(self.history_frame, text=f"Tidak ada history untuk {student_name}", 
                        bg=self.bg, fg="#24252a", font=self.form_fonts).pack()
                return
            
            # Create table
            columns = ("No", "Tanggal", "Stress Level", "Kategori")
            tree = ttk.Treeview(self.history_frame, columns=columns, height=12)
            tree.pack(fill='both', expand=True)
            
            # Define column headings
            tree.column("#0", width=0)
            tree.column("No", anchor=tk.W, width=30)
            tree.column("Tanggal", anchor=tk.W, width=150)
            tree.column("Stress Level", anchor=tk.CENTER, width=100)
            tree.column("Kategori", anchor=tk.CENTER, width=100)
            
            tree.heading("#0", text="", anchor=tk.W)
            tree.heading("No", text="No", anchor=tk.W)
            tree.heading("Tanggal", text="Tanggal Prediksi", anchor=tk.W)
            tree.heading("Stress Level", text="Stress Level", anchor=tk.CENTER)
            tree.heading("Kategori", text="Kategori", anchor=tk.CENTER)
            
            # Insert data
            for idx, pred in enumerate(predictions, 1):
                tree.insert(parent='', index='end', iid=idx, text='',
                          values=(idx, pred['created_at'][:10], pred['prediction_result'], 
                                 pred['stress_category']))
            
            # Add scroll bar
            scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscroll=scrollbar.set)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load history: {str(e)}")
    
    # ==================== TAB 4: STATISTIK ====================
    
    def _create_statistics_tab(self):
        """Tab untuk menampilkan statistik student"""
        tab4 = tk.Frame(self.tabCtrl, bg=self.bg)
        self.tabCtrl.add(tab4, text="Statistik")
        
        header4 = tk.Frame(tab4, bg="#9c27b0", borderwidth=1, height=50, relief='solid')
        header4.pack(fill='x', pady=20, padx=10)
        tk.Label(header4, text="STATISTIK PREDIKSI", font=self.header_fonts, 
                fg='#FFFFFF', bg='#9c27b0').pack()
        
        # Input untuk query statistik
        form = tk.Frame(tab4, bg=self.bg)
        form.pack(fill='x', padx=10, pady=12)
        tk.Label(form, text="Nama Student:", bg=self.bg, fg="#24252a", font=self.form_fonts).pack(side='left')
        self.entry_stat_name = tk.Entry(form, width=30)
        self.entry_stat_name.pack(side='left', padx=10)
        tk.Button(form, text="TAMPILKAN", width=12, height=1, font=("Segoe UI", 10, "bold"), 
                 fg='white', bg="#9c27b0", command=self._load_statistics).pack(side='left')
        
        # Frame untuk statistik
        self.stat_frame = tk.Frame(tab4, bg=self.bg)
        self.stat_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _load_statistics(self):
        """Load dan tampilkan statistik student"""
        student_name = self.entry_stat_name.get().strip()
        if not student_name:
            messagebox.showerror("Error", "Silahkan masukkan nama!")
            return
        
        try:
            # Clear previous data
            for widget in self.stat_frame.winfo_children():
                widget.destroy()
            
            # Get statistics
            stats = db.get_statistics(student_name)
            
            if not stats:
                tk.Label(self.stat_frame, text=f"Tidak ada data untuk {student_name}", 
                        bg=self.bg, fg="#24252a", font=self.form_fonts).pack()
                return
            
            # Display stats
            info_text = f"""
STATISTIK STUDENT: {student_name}
{'=' * 50}

Total Prediksi: {stats['total_predictions']} kali

Rata-rata Stress Level: {stats['average_stress_level']:.2f}

Distribusi Kategori Stress:
"""
            
            for category, count in stats['stress_categories'].items():
                percentage = (count / stats['total_predictions']) * 100
                info_text += f"\n  • {category}: {count} kali ({percentage:.1f}%)"
            
            text_widget = tk.Label(self.stat_frame, text=info_text, bg=self.bg, 
                                  fg="#24252a", font=("Courier", 11), justify=tk.LEFT)
            text_widget.pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load statistik: {str(e)}")
