"""
Modern GUI dengan CustomTkinter
Fitur tetap sama dengan gui_with_database.py:
- Prediksi stress
- Informasi model
- History prediksi
- Statistik student
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
from dotenv import load_dotenv

try:
    from database import init_database
    DB_AVAILABLE = True
except ImportError as import_error:
    print(f"⚠️ Warning: Database module tidak bisa diimport: {import_error}")
    DB_AVAILABLE = False
    init_database = None


load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

db = init_database(SUPABASE_URL, SUPABASE_KEY) if DB_AVAILABLE else None

FEATURE_COLUMNS = ["Sleep_Duration", "Study_Hours", "Social_Media_Hours", "Physical_Activity"]


class ModernGUIWithDatabase:
    def __init__(self, root, model, X_MIN, X_MAX, y_test, y_test_label, matrix, total_benar):
        self.root = root
        self.model = model
        self.X_MIN = X_MIN
        self.X_MAX = X_MAX
        self.y_test = y_test
        self.y_test_label = y_test_label
        self.matrix = matrix
        self.total_benar = total_benar

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root.title("Stress Level Predictor")
        self.root.geometry("920x720")
        self.root.minsize(920, 720)

        self._build_layout()

    def _build_layout(self):
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            main_container,
            text="Stress Level Predictor",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(pady=(18, 4))

        subtitle = ctk.CTkLabel(
            main_container,
            text="Prediksi, History, dan Statistik Student",
            font=ctk.CTkFont(size=13),
            text_color=("#4b5563", "#9ca3af"),
        )
        subtitle.pack(pady=(0, 12))

        self.tabview = ctk.CTkTabview(main_container, width=880, height=620)
        self.tabview.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.tab_prediction = self.tabview.add("Uji Coba Data")
        self.tab_model = self.tabview.add("Informasi Model")
        self.tab_history = self.tabview.add("History Prediksi")
        self.tab_stats = self.tabview.add("Statistik")

        self._build_prediction_tab()
        self._build_model_tab()
        self._build_history_tab()
        self._build_stats_tab()

    def _build_prediction_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_prediction)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.entry_name = self._input_row(container, "Nama Anda")
        self.entry_sleep = self._input_row(container, "Durasi Jam Tidur /Hari")
        self.entry_study = self._input_row(container, "Durasi Jam Belajar /Hari")
        self.entry_social = self._input_row(container, "Durasi Jam Menggunakan Sosial Media /Hari")
        self.entry_activity = self._input_row(container, "Menit Aktifitas Fisik /Minggu")

        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.pack(fill="x", pady=(16, 8))

        ctk.CTkButton(
            action_frame,
            text="CEK STRESS LEVEL",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._process_prediction,
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            action_frame,
            text="CLEAR INPUT",
            height=40,
            fg_color="gray40",
            hover_color="gray30",
            command=self._clear_inputs,
        ).pack(fill="x")

    def _build_model_tab(self):
        container = ctk.CTkFrame(self.tab_model)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        accuracy = (self.total_benar / len(self.y_test)) * 100 if len(self.y_test) > 0 else 0
        cards = [
            ("Akurasi Model", f"{accuracy:.2f}%"),
            ("Jumlah Data Train", "80%"),
            ("Jumlah Data Test", "20%"),
            ("Model Type", "Linear Regression"),
        ]

        for title, value in cards:
            card = ctk.CTkFrame(container)
            card.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=14, pady=(12, 2))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18)).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_history_tab(self):
        top = ctk.CTkFrame(self.tab_history)
        top.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(top, text="Masukkan Nama:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(12, 8), pady=12)
        self.entry_search_name = ctk.CTkEntry(top, width=260)
        self.entry_search_name.pack(side="left", padx=(0, 8), pady=12)
        ctk.CTkButton(top, text="CARI", width=110, command=self._load_history).pack(side="left", pady=12)

        self.history_frame = ctk.CTkFrame(self.tab_history)
        self.history_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_stats_tab(self):
        top = ctk.CTkFrame(self.tab_stats)
        top.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(top, text="Nama Student:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(12, 8), pady=12)
        self.entry_stat_name = ctk.CTkEntry(top, width=260)
        self.entry_stat_name.pack(side="left", padx=(0, 8), pady=12)
        ctk.CTkButton(top, text="TAMPILKAN", width=130, command=self._load_statistics).pack(side="left", pady=12)

        self.stat_frame = ctk.CTkFrame(self.tab_stats)
        self.stat_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _input_row(self, parent, label_text):
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", pady=8)
        ctk.CTkLabel(row, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), width=260, anchor="w").pack(side="left", padx=12, pady=12)
        entry = ctk.CTkEntry(row, width=320)
        entry.pack(side="right", padx=12, pady=12)
        return entry

    def _get_prediction_inputs(self):
        student_name = self.entry_name.get().strip()
        if not student_name:
            messagebox.showerror("Error", "Silahkan masukkan nama Anda!")
            return None, None

        values = {
            "Sleep_Duration": self.entry_sleep.get().strip(),
            "Study_Hours": self.entry_study.get().strip(),
            "Social_Media_Hours": self.entry_social.get().strip(),
            "Physical_Activity": self.entry_activity.get().strip(),
        }

        if any(input_value == "" for input_value in values.values()):
            messagebox.showerror("Error", "Silahkan isi semua inputan!")
            return None, None

        try:
            converted = {key: float(value) for key, value in values.items()}
            return student_name, converted
        except ValueError:
            messagebox.showerror("Error", "Semua input harus berupa angka!")
            return None, None

    def _normalize_features(self, data_frame):
        denominator = (self.X_MAX - self.X_MIN).replace(0, 1)
        return (data_frame - self.X_MIN) / denominator

    def _process_prediction(self):
        student_name, values = self._get_prediction_inputs()
        if student_name is None or values is None:
            return

        try:
            input_frame = pd.DataFrame([values], columns=FEATURE_COLUMNS)
            normalized = self._normalize_features(input_frame)

            prediction_result = self.model.predict(normalized)
            prediction_value = int(np.clip(np.round(prediction_result[0]), 1, 10))

            low_threshold = np.percentile(self.y_test, 33)
            medium_threshold = np.percentile(self.y_test, 66)

            if prediction_value <= low_threshold:
                stress_category = "Rendah"
            elif prediction_value <= medium_threshold:
                stress_category = "Sedang"
            else:
                stress_category = "Psikolog aja"

            description_map = {
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
            description = description_map.get(prediction_value, "Hasil tidak tersedia")

            if db and db.client:
                try:
                    db.create_or_update_student(student_name)
                    db.save_prediction(student_name, values, prediction_value, stress_category, description)
                    db.update_student_prediction_count(student_name)
                except Exception as database_error:
                    messagebox.showwarning(
                        "Database Error",
                        f"Data tidak tersimpan ke database:\n{database_error}\n\nPrediksi tetap ditampilkan.",
                    )
            else:
                messagebox.showwarning(
                    "Database Not Connected",
                    "Database tidak terhubung. Cek .env file dan Supabase credentials.",
                )

            messagebox.showinfo(
                "Hasil Prediksi",
                f"Tingkatan Stress Anda: {prediction_value}\n\n{description}",
            )
            self._clear_inputs()

        except Exception as prediction_error:
            messagebox.showerror("Error", f"Terjadi error: {prediction_error}")

    def _clear_inputs(self):
        self.entry_name.delete(0, tk.END)
        self.entry_sleep.delete(0, tk.END)
        self.entry_study.delete(0, tk.END)
        self.entry_social.delete(0, tk.END)
        self.entry_activity.delete(0, tk.END)
        self.entry_name.focus_set()

    def _load_history(self):
        student_name = self.entry_search_name.get().strip()
        if not student_name:
            messagebox.showerror("Error", "Silahkan masukkan nama!")
            return

        for widget in self.history_frame.winfo_children():
            widget.destroy()

        try:
            predictions = db.get_predictions_by_student(student_name, limit=20) if db else []
            if not predictions:
                ctk.CTkLabel(self.history_frame, text=f"Tidak ada history untuk {student_name}").pack(padx=12, pady=12)
                return

            columns = ("No", "Tanggal", "Stress Level", "Kategori")
            tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=14)
            tree.pack(fill="both", expand=True, padx=8, pady=8)

            tree.heading("No", text="No")
            tree.heading("Tanggal", text="Tanggal Prediksi")
            tree.heading("Stress Level", text="Stress Level")
            tree.heading("Kategori", text="Kategori")

            tree.column("No", width=50, anchor="center")
            tree.column("Tanggal", width=170, anchor="w")
            tree.column("Stress Level", width=120, anchor="center")
            tree.column("Kategori", width=130, anchor="center")

            for index, prediction in enumerate(predictions, start=1):
                tree.insert(
                    "",
                    "end",
                    values=(
                        index,
                        str(prediction["created_at"])[:10],
                        prediction["prediction_result"],
                        prediction["stress_category"],
                    ),
                )

        except Exception as history_error:
            messagebox.showerror("Error", f"Gagal load history: {history_error}")

    def _load_statistics(self):
        student_name = self.entry_stat_name.get().strip()
        if not student_name:
            messagebox.showerror("Error", "Silahkan masukkan nama!")
            return

        for widget in self.stat_frame.winfo_children():
            widget.destroy()

        try:
            stats = db.get_statistics(student_name) if db else None
            if not stats:
                ctk.CTkLabel(self.stat_frame, text=f"Tidak ada data untuk {student_name}").pack(padx=12, pady=12)
                return

            lines = [
                f"STATISTIK STUDENT: {student_name}",
                "=" * 50,
                "",
                f"Total Prediksi: {stats['total_predictions']} kali",
                "",
                f"Rata-rata Stress Level: {stats['average_stress_level']:.2f}",
                "",
                "Distribusi Kategori Stress:",
            ]

            for category, count in stats["stress_categories"].items():
                percentage = (count / stats["total_predictions"]) * 100 if stats["total_predictions"] else 0
                lines.append(f"  • {category}: {count} kali ({percentage:.1f}%)")

            text_block = "\n".join(lines)
            label = ctk.CTkLabel(
                self.stat_frame,
                text=text_block,
                justify="left",
                anchor="w",
                font=ctk.CTkFont(family="Consolas", size=13),
            )
            label.pack(fill="both", expand=True, padx=14, pady=14)

        except Exception as stats_error:
            messagebox.showerror("Error", f"Gagal load statistik: {stats_error}")
