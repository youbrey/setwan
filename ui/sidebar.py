"""
ui/sidebar.py
==============
Mixin yang bertugas membangun panel SIDEBAR (kiri) saja:
logo, tombol import database, pemilih mode DPRD/Setwan, riwayat surat,
tombol cetak utama, dan navigasi ke Surat Undangan.

Mixin ini tidak tahu apa pun tentang logika pembuatan surat -- dia
hanya membangun widget dan menghubungkannya ke method lain lewat
`command=`.
"""

import customtkinter as ctk

from config import APP_VERSION_LABEL


class SidebarMixin:
    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SIPS DPRD BITUNG",
                                        font=("Arial", 18, "bold"), text_color="#1E3A8A")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.btn_import_db = ctk.CTkButton(self.sidebar_frame, text="📥 Import Database",
                                            command=self.import_excel_database)
        self.btn_import_db.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.mode_selector = ctk.CTkSegmentedButton(self.sidebar_frame, values=["DPRD", "Setwan"],
                                                     command=self.change_mode)
        self.mode_selector.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.mode_selector.set("DPRD")

        lbl_history = ctk.CTkLabel(self.sidebar_frame, text="Riwayat Edit Surat:", font=("Arial", 11, "bold"))
        lbl_history.grid(row=3, column=0, padx=20, pady=(15, 0), sticky="w")

        history_keys = self.history_db.keys()
        self.combo_history = ctk.CTkComboBox(self.sidebar_frame,
                                              values=history_keys if history_keys else ["Tidak ada riwayat"])
        self.combo_history.grid(row=4, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.btn_load_history = ctk.CTkButton(self.sidebar_frame, text="Load Data Surat",
                                               fg_color="#F59E0B", hover_color="#D97706",
                                               command=self.load_selected_history)
        self.btn_load_history.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="ew")

        self.btn_generate_main = ctk.CTkButton(self.sidebar_frame, text="⚡ CETAK SURAT & SPD",
                                                command=self.generate_documents_action,
                                                fg_color="#10B981", hover_color="#059669",
                                                font=("Arial", 14, "bold"))
        self.btn_generate_main.grid(row=6, column=0, padx=20, pady=15, sticky="ew")

        # Kategori Surat Undangan Section
        lbl_undangan_title = ctk.CTkLabel(self.sidebar_frame, text="Kategori Surat Undangan:",
                                          font=("Arial", 11, "bold"))
        lbl_undangan_title.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="w")

        self.btn_undangan_paripurna = ctk.CTkButton(self.sidebar_frame, text="📨 Undangan Paripurna",
                                                     command=self.show_undangan_paripurna,
                                                     fg_color="#6366F1", hover_color="#4F46E5")
        self.btn_undangan_paripurna.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        self.btn_undangan_biasa = ctk.CTkButton(self.sidebar_frame, text="📋 Undangan Biasa",
                                                command=self.show_undangan_biasa,
                                                fg_color="#8B5CF6", hover_color="#7C3AED")
        self.btn_undangan_biasa.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        self.btn_back_to_perjalanan = ctk.CTkButton(self.sidebar_frame, text="← Kembali ke Perjalanan Dinas",
                                                     command=self.show_perjalanan_dinas,
                                                     fg_color="#64748B", hover_color="#475569")
        self.btn_back_to_perjalanan.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
        self.btn_back_to_perjalanan.grid_remove()

        self.lbl_credit = ctk.CTkLabel(self.sidebar_frame, text=APP_VERSION_LABEL,
                                        font=("Arial", 9), text_color="gray")
        self.lbl_credit.grid(row=11, column=0, padx=20, pady=15, sticky="s")
