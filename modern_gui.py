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
    print(f"Warning: Database module tidak bisa diimport: {import_error}")
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

        self.palette = {
            "success": "#16A34A",
            "warning": "#D97706",
            "danger": "#DC2626",
            "muted": "#6B7280",
            "panel": ("#F8FAFC", "#1F2937"),
            "surface": ("#FFFFFF", "#111827"),
        }
        self.validation_labels = {}

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
        scroll_container = ctk.CTkScrollableFrame(self.tab_prediction, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=0, pady=0)

        intro = ctk.CTkFrame(scroll_container, fg_color=self.palette["panel"])
        intro.pack(fill="x", padx=14, pady=(14, 10))
        ctk.CTkLabel(
            intro,
            text="Isi data kebiasaan harian untuk prediksi stress level",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            intro,
            text="Validasi dilakukan otomatis saat Anda mengetik.",
            font=ctk.CTkFont(size=12),
            text_color=self.palette["muted"],
        ).pack(anchor="w", padx=14, pady=(0, 12))

        form_card = ctk.CTkFrame(scroll_container, fg_color=self.palette["surface"])
        form_card.pack(fill="x", padx=14, pady=(0, 10))

        self.entry_name = self._create_input_field(
            form_card,
            field_key="name",
            label_text="Nama Anda",
            placeholder_text="contoh: Rina",
            is_numeric=False,
        )
        self.entry_sleep = self._create_input_field(
            form_card,
            field_key="sleep",
            label_text="Durasi Jam Tidur per Hari",
            placeholder_text="contoh: 7.5",
            helper_text="Gunakan satuan jam (0-24)",
            min_value=0.0,
            max_value=24.0,
        )
        self.entry_study = self._create_input_field(
            form_card,
            field_key="study",
            label_text="Durasi Jam Belajar per Hari",
            placeholder_text="contoh: 4",
            helper_text="Gunakan satuan jam (0-24)",
            min_value=0.0,
            max_value=24.0,
        )
        self.entry_social = self._create_input_field(
            form_card,
            field_key="social",
            label_text="Durasi Sosial Media per Hari",
            placeholder_text="contoh: 3",
            helper_text="Gunakan satuan jam (0-24)",
            min_value=0.0,
            max_value=24.0,
        )
        self.entry_activity = self._create_input_field(
            form_card,
            field_key="activity",
            label_text="Aktivitas Fisik per Minggu",
            placeholder_text="contoh: 120",
            helper_text="Gunakan satuan menit (0-10080)",
            min_value=0.0,
            max_value=10080.0,
        )

        action_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        action_frame.pack(fill="x", padx=14, pady=(8, 14))

        self.predict_button = ctk.CTkButton(
            action_frame,
            text="CEK STRESS LEVEL",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
            command=self._process_prediction,
        )
        self.predict_button.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            action_frame,
            text="CLEAR INPUT",
            height=40,
            fg_color="gray40",
            hover_color="gray30",
            command=self._clear_inputs,
        ).pack(fill="x")

        result_card = ctk.CTkFrame(scroll_container, fg_color=self.palette["surface"])
        result_card.pack(fill="x", padx=14, pady=(0, 14))

        ctk.CTkLabel(
            result_card,
            text="Ringkasan Hasil",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(14, 8))

        self.result_badge = ctk.CTkLabel(
            result_card,
            text="Belum ada prediksi",
            fg_color=("#E5E7EB", "#374151"),
            corner_radius=10,
            padx=10,
            pady=4,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.result_badge.pack(anchor="w", padx=14)

        self.result_score = ctk.CTkLabel(
            result_card,
            text="-",
            font=ctk.CTkFont(size=54, weight="bold"),
        )
        self.result_score.pack(anchor="w", padx=14, pady=(14, 4))

        self.result_student = ctk.CTkLabel(
            result_card,
            text="Nama: -",
            font=ctk.CTkFont(size=13),
            text_color=self.palette["muted"],
        )
        self.result_student.pack(anchor="w", padx=14)

        self.result_desc = ctk.CTkLabel(
            result_card,
            text="Masukkan data lalu klik CEK STRESS LEVEL.",
            justify="left",
            wraplength=700,
            anchor="w",
            font=ctk.CTkFont(size=13),
        )
        self.result_desc.pack(fill="x", padx=14, pady=(14, 10))

        self.result_meta = ctk.CTkLabel(
            result_card,
            text="Skala: 1 (rendah) sampai 10 (tinggi)",
            justify="left",
            wraplength=700,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=self.palette["muted"],
        )
        self.result_meta.pack(fill="x", padx=14, pady=(0, 14))

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
        self.entry_search_name = ctk.CTkEntry(top, width=260, placeholder_text="contoh: Rina")
        self.entry_search_name.pack(side="left", padx=(0, 8), pady=12)
        ctk.CTkButton(top, text="CARI", width=110, command=self._load_history).pack(side="left", pady=12)

        self.history_frame = ctk.CTkFrame(self.tab_history)
        self.history_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._render_empty_state(self.history_frame, "Masukkan nama student, lalu klik CARI untuk melihat history.")

    def _build_stats_tab(self):
        top = ctk.CTkFrame(self.tab_stats)
        top.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(top, text="Nama Student:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(12, 8), pady=12)
        self.entry_stat_name = ctk.CTkEntry(top, width=260, placeholder_text="contoh: Rina")
        self.entry_stat_name.pack(side="left", padx=(0, 8), pady=12)
        ctk.CTkButton(top, text="TAMPILKAN", width=130, command=self._load_statistics).pack(side="left", pady=12)

        self.stat_frame = ctk.CTkFrame(self.tab_stats)
        self.stat_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._render_empty_state(self.stat_frame, "Masukkan nama student, lalu klik TAMPILKAN untuk melihat statistik.")

    def _create_input_field(
        self,
        parent,
        field_key,
        label_text,
        placeholder_text,
        helper_text="",
        is_numeric=True,
        min_value=None,
        max_value=None,
    ):
        block = ctk.CTkFrame(parent, fg_color="transparent")
        block.pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            block,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        entry = ctk.CTkEntry(block, height=38, placeholder_text=placeholder_text)
        entry.pack(fill="x")
        entry.bind("<KeyRelease>", lambda _event: self._on_input_change())

        if helper_text:
            ctk.CTkLabel(
                block,
                text=helper_text,
                font=ctk.CTkFont(size=11),
                text_color=self.palette["muted"],
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

        validation_label = ctk.CTkLabel(
            block,
            text="",
            font=ctk.CTkFont(size=11),
            anchor="w",
            text_color=self.palette["danger"],
        )
        validation_label.pack(fill="x", pady=(2, 0))

        self.validation_labels[field_key] = {
            "label": validation_label,
            "entry": entry,
            "is_numeric": is_numeric,
            "min_value": min_value,
            "max_value": max_value,
        }
        return entry

    def _on_input_change(self):
        is_valid = self._validate_all_fields(show_message=False)
        self.predict_button.configure(state="normal" if is_valid else "disabled")

    def _validate_all_fields(self, show_message):
        has_error = False
        for field_key, field_data in self.validation_labels.items():
            entry = field_data["entry"]
            raw_value = entry.get().strip()
            is_numeric = field_data["is_numeric"]
            validation_label = field_data["label"]
            min_value = field_data.get("min_value")
            max_value = field_data.get("max_value")

            if raw_value == "":
                validation_label.configure(text="Wajib diisi" if show_message else "")
                has_error = True
                continue

            if is_numeric and not self._is_number(raw_value):
                validation_label.configure(text="Harus berupa angka")
                has_error = True
                continue

            if is_numeric and (min_value is not None or max_value is not None):
                numeric_value = float(raw_value)
                if min_value is not None and numeric_value < min_value:
                    validation_label.configure(text=f"Nilai minimal {self._format_number(min_value)}")
                    has_error = True
                    continue
                if max_value is not None and numeric_value > max_value:
                    validation_label.configure(text=f"Nilai maksimal {self._format_number(max_value)}")
                    has_error = True
                    continue

            validation_label.configure(text="")

        return not has_error

    @staticmethod
    def _is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _format_number(value):
        return str(int(value)) if float(value).is_integer() else str(value)

    @staticmethod
    def _result_style(stress_category):
        if stress_category == "Rendah":
            return ("#DCFCE7", "#14532D")
        if stress_category == "Sedang":
            return ("#FEF3C7", "#78350F")
        return ("#FEE2E2", "#7F1D1D")

    def _update_result_panel(self, student_name, prediction_value, stress_category, description):
        fg_color, text_color = self._result_style(stress_category)
        self.result_badge.configure(text=f"Kategori: {stress_category}", fg_color=fg_color, text_color=text_color)
        self.result_score.configure(text=str(prediction_value))
        self.result_student.configure(text=f"Nama: {student_name}")
        self.result_desc.configure(text=description)
        self.result_meta.configure(text="Skala: 1 (rendah) sampai 10 (tinggi)")

    @staticmethod
    def _render_empty_state(frame, text):
        ctk.CTkLabel(
            frame,
            text=text,
            text_color=("#6B7280", "#9CA3AF"),
            font=ctk.CTkFont(size=13),
        ).pack(expand=True, padx=12, pady=12)

    def _get_prediction_inputs(self):
        if not self._validate_all_fields(show_message=True):
            messagebox.showerror("Error", "Periksa kembali input yang masih kosong atau tidak valid.")
            return None, None

        student_name = self.entry_name.get().strip()

        values = {
            "Sleep_Duration": self.entry_sleep.get().strip(),
            "Study_Hours": self.entry_study.get().strip(),
            "Social_Media_Hours": self.entry_social.get().strip(),
            "Physical_Activity": self.entry_activity.get().strip(),
        }

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

            self._update_result_panel(student_name, prediction_value, stress_category, description)
            self._clear_inputs()

        except Exception as prediction_error:
            messagebox.showerror("Error", f"Terjadi error: {prediction_error}")

    def _clear_inputs(self):
        self.entry_name.delete(0, tk.END)
        self.entry_sleep.delete(0, tk.END)
        self.entry_study.delete(0, tk.END)
        self.entry_social.delete(0, tk.END)
        self.entry_activity.delete(0, tk.END)
        for field_data in self.validation_labels.values():
            field_data["label"].configure(text="")

        self.predict_button.configure(state="disabled")
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
