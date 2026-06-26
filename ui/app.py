"""
ui/app.py
==========
Kelas utama SIPSApp. File ini SENGAJA dibuat tipis: hanya berisi
__init__, perakitan layout dasar (grid 4 kolom: sidebar, form, panel
personel, preview), dan beberapa method "lem" kecil (import database,
on_close). Semua logika UI detail per-bagian ada di mixin masing-masing:

    SidebarMixin          -> ui/sidebar.py
    PersonnelPanelMixin    -> ui/personnel_panel.py
    TujuanPanelMixin        -> ui/tujuan_panel.py
    PerjalananFormMixin     -> ui/perjalanan_form.py
    UndanganFormMixin       -> ui/undangan_form.py
    PreviewPanelMixin       -> ui/preview_panel.py
    ContextBuilderMixin     -> ui/context_builder.py  (jembatan UI <-> letters/*)

Ingin menambah jenis surat baru? Cukup buat modul baru di `letters/`,
lalu panggil dari ContextBuilderMixin atau UndanganFormMixin. Ingin
mengubah tampilan? Cukup edit mixin UI terkait -- tidak perlu
menyentuh file lain.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config import APP_TITLE, APP_GEOMETRY, APP_MIN_SIZE, APPEARANCE_MODE, COLOR_THEME, DATABASE_XLSX
from database import PersonnelDatabase, HistoryDatabase

from ui.sidebar import SidebarMixin
from ui.personnel_panel import PersonnelPanelMixin
from ui.tujuan_panel import TujuanPanelMixin
from ui.perjalanan_form import PerjalananFormMixin
from ui.undangan_form import UndanganFormMixin
from ui.preview_panel import PreviewPanelMixin
from ui.context_builder import ContextBuilderMixin

ctk.set_appearance_mode(APPEARANCE_MODE)
ctk.set_default_color_theme(COLOR_THEME)


class SIPSApp(
    SidebarMixin,
    PersonnelPanelMixin,
    TujuanPanelMixin,
    PerjalananFormMixin,
    UndanganFormMixin,
    PreviewPanelMixin,
    ContextBuilderMixin,
    ctk.CTk,
):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(*APP_MIN_SIZE)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- STATE DASAR -------------------------------------------------
        self.mode = "dprd"               # "dprd" atau "setwan"
        self.current_view = "perjalanan_dinas"   # "perjalanan_dinas" | "undangan_paripurna" | "undangan_biasa"
        self.tujuan_terpilih = []
        self.database_tujuan = self._load_database_tujuan()

        self.dprd_vars = {}
        self.asn_vars = {}
        self.pelaksana_vars = {}
        self.pendamping_vars = {}
        self.active_categories = {}

        self.rendered_dprd_widgets = {}
        self.rendered_asn_widgets = {}
        self.rendered_pelaksana_widgets = {}
        self.rendered_pendamping_widgets = {}

        # --- DATABASE & RIWAYAT ------------------------------------------
        self.personnel_db = PersonnelDatabase()
        self.personnel_db.load()
        self.history_db = HistoryDatabase()
        self.history_db.load()

        # --- BANGUN UI -----------------------------------------------------
        self.setup_sidebar()

        self.middle_outer_frame = ctk.CTkScrollableFrame(self, label_text="Form Data Surat")
        self.middle_outer_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.middle_frame = self.middle_outer_frame  # alias, dipakai mixin form

        self.setup_perjalanan_dinas_form()
        self._apply_initial_default_values()
        self.calculate_duration()

        self.setup_personnel_panel()
        self.setup_preview_panel()

        self.schedule_preview_refresh(immediate=True)

    # ------------------------------------------------------------------
    # PROPERTI PINTASAN KE DATABASE (agar mixin lain tetap bisa
    # menulis self.db_dprd / self.db_asn seperti sebelumnya)
    # ------------------------------------------------------------------
    @property
    def db_dprd(self):
        return self.personnel_db.db_dprd

    @property
    def db_asn(self):
        return self.personnel_db.db_asn

    def _load_database_tujuan(self):
        from config import DATABASE_TUJUAN
        return DATABASE_TUJUAN

    # ------------------------------------------------------------------
    # IMPORT DATABASE EXCEL/CSV
    # ------------------------------------------------------------------
    def import_excel_database(self):
        file_path = filedialog.askopenfilename(
            title="Pilih file database personel",
            filetypes=[("Excel/CSV files", "*.xlsx *.xls *.csv")]
        )
        if not file_path:
            return
        try:
            jumlah_dprd, jumlah_asn = self.personnel_db.import_from_file(file_path)
            self.refresh_signer_dropdowns()
            self.setup_category_checkboxes()
            self.refresh_personnel_list()
            messagebox.showinfo(
                "Berhasil",
                f"Database berhasil diimpor.\nDPRD: {jumlah_dprd} orang\nASN: {jumlah_asn} orang"
            )
        except Exception as e:
            messagebox.showerror("Gagal Impor", f"Gagal membaca file database:\n{e}")

    # ------------------------------------------------------------------
    # PENUTUP APLIKASI
    # ------------------------------------------------------------------
    def on_close(self):
        self.personnel_db.save()
        self.history_db.save()
        self.destroy()
