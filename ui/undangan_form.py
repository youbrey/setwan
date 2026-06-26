"""
ui/undangan_form.py
=====================
Mixin untuk FORM SURAT UNDANGAN (Rapat Paripurna & Undangan Biasa),
serta logika berpindah tampilan panel tengah antara mode "Perjalanan
Dinas" dan mode "Undangan". Logika pembuatan dokumennya sendiri ada
di letters/undangan.py -- mixin ini hanya membaca form lalu
memanggilnya, sama seperti pola di ui/context_builder.py.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from optional_deps import HAS_TKCALENDAR
from utils.tanggal import HARI_INDONESIA
from letters.undangan import buat_undangan_paripurna


class UndanganFormMixin:
    # ------------------------------------------------------------------
    # NAVIGASI ANTAR TAMPILAN
    # ------------------------------------------------------------------
    def show_perjalanan_dinas(self):
        self.current_view = "perjalanan_dinas"
        self.btn_back_to_perjalanan.grid_remove()
        self.right_frame.grid()
        self.setup_perjalanan_dinas_form()
        self.setup_category_checkboxes()
        self.refresh_personnel_list()
        self.schedule_preview_refresh(immediate=True)

    def show_undangan_paripurna(self):
        self.current_view = "undangan_paripurna"
        self.btn_back_to_perjalanan.grid()
        self.right_frame.grid_remove()
        self.setup_undangan_paripurna_form()
        self.schedule_preview_refresh(immediate=True)

    def show_undangan_biasa(self):
        self.current_view = "undangan_biasa"
        self.btn_back_to_perjalanan.grid()
        self.right_frame.grid_remove()
        self.setup_undangan_biasa_form()

    # ------------------------------------------------------------------
    # FORM: UNDANGAN PARIPURNA
    # ------------------------------------------------------------------
    def setup_undangan_paripurna_form(self):
        for widget in self.middle_frame.winfo_children():
            widget.destroy()
        self.undangan_inputs = {}
        self.skenario_entries = []

        title = ctk.CTkLabel(self.middle_frame, text="📨 Surat Undangan Rapat Paripurna",
                              font=("Arial", 15, "bold"), text_color="#6366F1")
        title.pack(fill="x", padx=10, pady=(10, 10))

        for key, label, placeholder in [
            ("nomor_undangan", "Nomor Surat Undangan", "Contoh: 005/UND/X/2026"),
            ("isi_surat", "Perihal / Isi Singkat Surat", "Contoh: Rapat Paripurna Pengambilan Keputusan..."),
            ("jam_pelaksanaan", "Jam Pelaksanaan", "Contoh: 09:00 WITA s.d. selesai"),
            ("pakaian", "Pakaian", "Contoh: Pakaian Sipil Harian (PSH)"),
            ("jabatan_ttd", "Jabatan Penandatangan", "Contoh: Ketua DPRD Kota Bitung"),
            ("nama_ttd", "Nama Penandatangan", "Contoh: VIVY JEANET GANAP, S.E."),
        ]:
            lbl = ctk.CTkLabel(self.middle_frame, text=label, anchor="w", font=("Arial", 12, "bold"))
            lbl.pack(fill="x", padx=10, pady=(8, 2))
            ent = ctk.CTkEntry(self.middle_frame, placeholder_text=placeholder)
            ent.pack(fill="x", padx=10, pady=(0, 6))
            ent.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())
            self.undangan_inputs[key] = ent

        lbl_tgl_surat = ctk.CTkLabel(self.middle_frame, text="Tanggal Surat", anchor="w", font=("Arial", 12, "bold"))
        lbl_tgl_surat.pack(fill="x", padx=10, pady=(8, 2))
        self.dp_undangan_surat = self._buat_date_picker(on_change=lambda e=None: self.schedule_preview_refresh())

        lbl_tgl_rapat = ctk.CTkLabel(self.middle_frame, text="Tanggal Rapat", anchor="w", font=("Arial", 12, "bold"))
        lbl_tgl_rapat.pack(fill="x", padx=10, pady=(8, 2))
        self.dp_undangan_rapat = self._buat_date_picker(on_change=lambda e=None: self.update_hari_rapat())

        lbl_hari_rapat = ctk.CTkLabel(self.middle_frame, text="Hari Rapat (Otomatis)", anchor="w", font=("Arial", 12, "bold"))
        lbl_hari_rapat.pack(fill="x", padx=10, pady=(8, 2))
        self.ent_hari_rapat = ctk.CTkEntry(self.middle_frame, fg_color="#F3F4F6")
        self.ent_hari_rapat.pack(fill="x", padx=10, pady=(0, 6))
        self.update_hari_rapat()

        lbl_skenario = ctk.CTkLabel(self.middle_frame, text="Susunan Acara / Skenario Rapat (maks. 7 baris)",
                                     anchor="w", font=("Arial", 12, "bold"))
        lbl_skenario.pack(fill="x", padx=10, pady=(12, 2))
        self.skenario_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        self.skenario_frame.pack(fill="x", padx=10, pady=(0, 6))
        for i in range(7):
            self._add_skenario_row(i)

        self.btn_cetak_undangan = ctk.CTkButton(self.middle_frame, text="⚡ CETAK SURAT UNDANGAN PARIPURNA",
                                                 command=self.generate_undangan_paripurna,
                                                 fg_color="#10B981", hover_color="#059669",
                                                 font=("Arial", 13, "bold"))
        self.btn_cetak_undangan.pack(fill="x", padx=10, pady=20)

    def _add_skenario_row(self, index):
        ent = ctk.CTkEntry(self.skenario_frame, placeholder_text=f"Acara ke-{index + 1}...")
        ent.pack(fill="x", padx=0, pady=2)
        ent.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())
        self.skenario_entries.append(ent)

    def update_hari_rapat(self):
        try:
            if HAS_TKCALENDAR:
                tgl = self.dp_undangan_rapat.get_date()
            else:
                from datetime import datetime
                tgl = datetime.strptime(self.dp_undangan_rapat.get(), "%d/%m/%Y")
            hari_eng = tgl.strftime("%A")
            hari = HARI_INDONESIA.get(hari_eng, hari_eng)
            self.ent_hari_rapat.configure(state="normal")
            self.ent_hari_rapat.delete(0, tk.END)
            self.ent_hari_rapat.insert(0, hari)
            self.ent_hari_rapat.configure(state="readonly")
        except Exception:
            pass
        self.schedule_preview_refresh()

    def build_undangan_paripurna_form_data(self):
        return {
            "nomor_undangan": self.undangan_inputs["nomor_undangan"].get().strip(),
            "tanggal_surat": self._get_date_str(self.dp_undangan_surat),
            "isi_surat": self.undangan_inputs["isi_surat"].get().strip(),
            "tanggal_rapat": self._get_date_str(self.dp_undangan_rapat),
            "hari_rapat": self.ent_hari_rapat.get().strip(),
            "jam_pelaksanaan": self.undangan_inputs["jam_pelaksanaan"].get().strip(),
            "pakaian": self.undangan_inputs["pakaian"].get().strip(),
            "jabatan_ttd": self.undangan_inputs["jabatan_ttd"].get().strip(),
            "nama_ttd": self.undangan_inputs["nama_ttd"].get().strip(),
            "skenario_list": [e.get().strip() for e in self.skenario_entries],
        }

    def generate_undangan_paripurna(self):
        form_data = self.build_undangan_paripurna_form_data()
        if not form_data["nomor_undangan"]:
            messagebox.showwarning("Peringatan", "Nomor surat undangan belum diisi.")
            return

        out_dir = filedialog.askdirectory(title="Pilih Folder Penyimpanan Dokumen")
        if not out_dir:
            return

        out_path = os.path.join(out_dir, "Surat_Undangan_Paripurna.docx")
        try:
            jumlah = buat_undangan_paripurna(form_data, out_path, out_dir)
            messagebox.showinfo("Berhasil", f"Surat Undangan Paripurna ({jumlah} halaman) berhasil dibuat:\n{out_path}")
        except FileNotFoundError as e:
            messagebox.showerror("Template Tidak Ditemukan", str(e))
        except Exception as e:
            messagebox.showerror("Gagal Membuat Dokumen", f"Terjadi kesalahan:\n{e}")

    # ------------------------------------------------------------------
    # FORM: UNDANGAN BIASA (placeholder, silakan kembangkan di sini)
    # ------------------------------------------------------------------
    def setup_undangan_biasa_form(self):
        for widget in self.middle_frame.winfo_children():
            widget.destroy()
        title = ctk.CTkLabel(self.middle_frame, text="📋 Surat Undangan Biasa",
                              font=("Arial", 15, "bold"), text_color="#8B5CF6")
        title.pack(fill="x", padx=10, pady=(10, 10))
        info = ctk.CTkLabel(
            self.middle_frame,
            text="Form Undangan Biasa belum diimplementasikan.\n\n"
                 "Tambahkan field & logikanya di:\n"
                 "- ui/undangan_form.py  (method setup_undangan_biasa_form)\n"
                 "- letters/undangan.py  (fungsi buat_undangan_biasa)",
            justify="left", anchor="w", text_color="gray"
        )
        info.pack(fill="x", padx=10, pady=10)
