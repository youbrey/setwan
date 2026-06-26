"""
ui/personnel_panel.py
=======================
Mixin yang membangun & mengelola PANEL KANAN (filter kategori +
checklist personel pelaksana). Tidak ada logika pembuatan surat di
sini -- hanya state pilihan personel (checkbox) yang nantinya dibaca
oleh ui/context_builder.py.
"""

import tkinter as tk
import customtkinter as ctk


class PersonnelPanelMixin:
    def setup_personnel_panel(self):
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(4, weight=1)

        lbl_cat_title = ctk.CTkLabel(self.right_frame, text="1. Filter Kategori Calon Pelaksana",
                                      font=("Arial", 13, "bold"), anchor="w")
        lbl_cat_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.category_check_frame = ctk.CTkFrame(self.right_frame, fg_color="#F3F4F6")
        self.category_check_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.setup_category_checkboxes()

        lbl_person_title = ctk.CTkLabel(self.right_frame, text="2. Checklist Personel Pelaksana",
                                         font=("Arial", 13, "bold"), anchor="w")
        lbl_person_title.grid(row=2, column=0, padx=15, pady=(15, 2), sticky="w")

        self.btn_action_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.btn_action_frame.grid(row=3, column=0, padx=15, pady=2, sticky="ew")
        self.btn_sel_all = ctk.CTkButton(self.btn_action_frame, text="Centang Semua Tampil",
                                          command=self.select_all_visible, height=24)
        self.btn_sel_all.pack(side="left", padx=2)
        self.btn_clear_all = ctk.CTkButton(self.btn_action_frame, text="Bersihkan", fg_color="gray",
                                            command=self.clear_all_visible, height=24)
        self.btn_clear_all.pack(side="left", padx=2)

        self.scroll_personnel = ctk.CTkScrollableFrame(self.right_frame)
        self.scroll_personnel.grid(row=4, column=0, padx=15, pady=(5, 15), sticky="nsew")
        self.refresh_personnel_list()

    # ------------------------------------------------------------------
    # FILTER KATEGORI
    # ------------------------------------------------------------------
    def setup_category_checkboxes(self):
        for widget in self.category_check_frame.winfo_children():
            widget.destroy()
        self.cat_chk_widgets = {}
        if self.mode == "dprd":
            categories = ["Pimpinan DPRD", "Komisi I", "Komisi II", "Komisi III", "Custom", "Pendamping ASN"]
            default_active = {"Pimpinan DPRD": True, "Komisi I": True, "Komisi II": False,
                              "Komisi III": False, "Custom": False, "Pendamping ASN": True}
        else:
            categories = ["Pelaksana ASN", "Pendamping ASN"]
            default_active = {"Pelaksana ASN": True, "Pendamping ASN": True}
        for idx, cat in enumerate(categories):
            val = tk.BooleanVar(value=default_active.get(cat, False))
            chk = ctk.CTkCheckBox(self.category_check_frame, text=cat, variable=val,
                                   font=("Arial", 11, "bold"), command=self.on_category_changed)
            chk.grid(row=idx // 3, column=idx % 3, padx=10, pady=10, sticky="w")
            self.cat_chk_widgets[cat] = val
        self.active_categories = {cat: var.get() for cat, var in self.cat_chk_widgets.items()}

    def on_category_changed(self):
        for cat, var in self.cat_chk_widgets.items():
            self.active_categories[cat] = var.get()
        self.refresh_personnel_list()

    # ------------------------------------------------------------------
    # CHECKLIST PERSONEL
    # ------------------------------------------------------------------
    def refresh_personnel_list(self):
        for widget in self.scroll_personnel.winfo_children():
            widget.destroy()
        self.rendered_dprd_widgets, self.rendered_asn_widgets = {}, {}
        self.rendered_pelaksana_widgets, self.rendered_pendamping_widgets = {}, {}

        if self.mode == "dprd":
            for p in self.db_dprd:
                cat = p.get("kategori", "Custom").strip()
                group_cat = cat if cat in ["Pimpinan DPRD", "Komisi I", "Komisi II", "Komisi III"] else "Custom"
                if self.active_categories.get(group_cat, False):
                    nama, jab = p.get('nama', ''), p.get('jabatan', '')
                    if nama not in self.dprd_vars:
                        self.dprd_vars[nama] = tk.BooleanVar(value=False)
                    chk = ctk.CTkCheckBox(
                        self.scroll_personnel,
                        text=f"{nama} ({jab}) [{cat}]",
                        variable=self.dprd_vars[nama],
                        command=lambda: self.schedule_preview_refresh(immediate=True)
                    )
                    chk.pack(fill="x", padx=10, pady=4, anchor="w")
                    self.rendered_dprd_widgets[nama] = p

            if self.active_categories.get("Pendamping ASN", False):
                if self.rendered_dprd_widgets:
                    ctk.CTkFrame(self.scroll_personnel, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)
                for p in self.db_asn:
                    nama, nip, jab = p.get('nama', ''), p.get('nip', '-'), p.get('jabatan', '-')
                    if nama not in self.asn_vars:
                        self.asn_vars[nama] = tk.BooleanVar(value=False)
                    chk = ctk.CTkCheckBox(
                        self.scroll_personnel,
                        text=f"{nama}\nNIP: {nip} | Jabatan: {jab}",
                        variable=self.asn_vars[nama],
                        command=lambda: self.schedule_preview_refresh(immediate=True)
                    )
                    chk.pack(fill="x", padx=10, pady=5, anchor="w")
                    self.rendered_asn_widgets[nama] = p
        else:
            if self.active_categories.get("Pelaksana ASN", False):
                lbl_pelaksana = ctk.CTkLabel(self.scroll_personnel, text="Pelaksana ASN:",
                                             font=("Arial", 12, "bold"), text_color="#1E3A8A")
                lbl_pelaksana.pack(fill="x", padx=10, pady=(5, 2), anchor="w")
                for p in self.db_asn:
                    nama, nip, jab = p.get('nama', ''), p.get('nip', '-'), p.get('jabatan', '-')
                    key = f"pelaksana_{nama}"
                    if key not in self.pelaksana_vars:
                        self.pelaksana_vars[key] = tk.BooleanVar(value=False)
                    chk = ctk.CTkCheckBox(
                        self.scroll_personnel,
                        text=f"{nama}\nNIP: {nip} | Jabatan: {jab}",
                        variable=self.pelaksana_vars[key],
                        command=lambda: self.schedule_preview_refresh(immediate=True)
                    )
                    chk.pack(fill="x", padx=10, pady=5, anchor="w")
                    self.rendered_pelaksana_widgets[nama] = p

            if self.active_categories.get("Pendamping ASN", False):
                if self.rendered_pelaksana_widgets:
                    ctk.CTkFrame(self.scroll_personnel, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)
                lbl_pendamping = ctk.CTkLabel(self.scroll_personnel, text="Pendamping ASN:",
                                              font=("Arial", 12, "bold"), text_color="#059669")
                lbl_pendamping.pack(fill="x", padx=10, pady=(5, 2), anchor="w")
                for p in self.db_asn:
                    nama, nip, jab = p.get('nama', ''), p.get('nip', '-'), p.get('jabatan', '-')
                    key = f"pendamping_{nama}"
                    if key not in self.pendamping_vars:
                        self.pendamping_vars[key] = tk.BooleanVar(value=False)
                    chk = ctk.CTkCheckBox(
                        self.scroll_personnel,
                        text=f"{nama}\nNIP: {nip} | Jabatan: {jab}",
                        variable=self.pendamping_vars[key],
                        command=lambda: self.schedule_preview_refresh(immediate=True)
                    )
                    chk.pack(fill="x", padx=10, pady=5, anchor="w")
                    self.rendered_pendamping_widgets[nama] = p

    def select_all_visible(self):
        for n in self.rendered_dprd_widgets: self.dprd_vars[n].set(True)
        for n in self.rendered_asn_widgets: self.asn_vars[n].set(True)
        for n in self.rendered_pelaksana_widgets:
            key = f"pelaksana_{n}"
            if key in self.pelaksana_vars: self.pelaksana_vars[key].set(True)
        for n in self.rendered_pendamping_widgets:
            key = f"pendamping_{n}"
            if key in self.pendamping_vars: self.pendamping_vars[key].set(True)
        self.schedule_preview_refresh(immediate=True)

    def clear_all_visible(self):
        for n in self.rendered_dprd_widgets: self.dprd_vars[n].set(False)
        for n in self.rendered_asn_widgets: self.asn_vars[n].set(False)
        for n in self.rendered_pelaksana_widgets:
            key = f"pelaksana_{n}"
            if key in self.pelaksana_vars: self.pelaksana_vars[key].set(False)
        for n in self.rendered_pendamping_widgets:
            key = f"pendamping_{n}"
            if key in self.pendamping_vars: self.pendamping_vars[key].set(False)
        self.schedule_preview_refresh(immediate=True)
