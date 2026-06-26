"""
ui/perjalanan_form.py
=======================
Mixin yang membangun & mengelola FORM PERJALANAN DINAS (panel tengah):
nomor surat, nomor SPD, dasar surat tugas, materi, jenis perjalanan,
tanggal, kota tujuan, dan penandatangan. Mixin ini juga mengatur
perpindahan mode DPRD <-> Setwan, karena banyak widget di form ini
yang tampil/sembunyi sesuai mode.

Form Surat Undangan dibangun di file TERPISAH: ui/undangan_form.py.
"""

import tkinter as tk
from datetime import datetime

import customtkinter as ctk

from optional_deps import HAS_TKCALENDAR, DateEntry


class PerjalananFormMixin:
    def setup_perjalanan_dinas_form(self):
        """Membangun ulang isi self.middle_frame dengan form Perjalanan
        Dinas. Dipanggil saat aplikasi pertama dibuka maupun saat
        pengguna menekan 'Kembali ke Perjalanan Dinas'."""
        for widget in self.middle_frame.winfo_children():
            widget.destroy()
        self.inputs = {}
        self.mode_specific_widgets = {}

        # --- Nomor Surat -----------------------------------------------
        for var_name, label in [
            ("nomor_surat", "Nomor Surat Tugas DPRD"),
            ("nomor_surat_asn", "Nomor Surat Tugas Setwan"),
        ]:
            lbl = ctk.CTkLabel(self.middle_frame, text=label, anchor="w", font=("Arial", 12, "bold"))
            lbl.pack(fill="x", padx=10, pady=(8, 2))
            ent = ctk.CTkEntry(self.middle_frame, placeholder_text=f"Masukkan {label.lower()}...")
            ent.pack(fill="x", padx=10, pady=(0, 6))
            ent.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())
            self.inputs[var_name] = ent

        # Pemberitahuan DPRD (mode specific)
        self.mode_specific_widgets["lbl_pemberitahuan_dprd"] = ctk.CTkLabel(
            self.middle_frame, text="Nomor Surat Pemberitahuan DPRD", anchor="w", font=("Arial", 12, "bold"))
        self.mode_specific_widgets["lbl_pemberitahuan_dprd"].pack(fill="x", padx=10, pady=(8, 2))
        self.inputs["nomor_pemberitahuan_dprd"] = ctk.CTkEntry(
            self.middle_frame, placeholder_text="Masukkan nomor surat pemberitahuan dprd...")
        self.inputs["nomor_pemberitahuan_dprd"].pack(fill="x", padx=10, pady=(0, 6))
        self.inputs["nomor_pemberitahuan_dprd"].bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())
        self.mode_specific_widgets["ent_pemberitahuan_dprd"] = self.inputs["nomor_pemberitahuan_dprd"]

        # Pemberitahuan Setwan
        for var_name, label in [
            ("nomor_pemberitahuan_asn", "Nomor Surat Pemberitahuan Setwan"),
        ]:
            lbl = ctk.CTkLabel(self.middle_frame, text=label, anchor="w", font=("Arial", 12, "bold"))
            lbl.pack(fill="x", padx=10, pady=(8, 2))
            ent = ctk.CTkEntry(self.middle_frame, placeholder_text=f"Masukkan {label.lower()}...")
            ent.pack(fill="x", padx=10, pady=(0, 6))
            ent.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())
            self.inputs[var_name] = ent

        # --- Nomor SPD ----------------------------------------------------
        lbl_spd_title = ctk.CTkLabel(self.middle_frame, text="Nomor SPD", anchor="w", font=("Arial", 12, "bold"))
        lbl_spd_title.pack(fill="x", padx=10, pady=(10, 2))

        spd_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        spd_frame.pack(fill="x", padx=10, pady=(0, 6))
        spd_frame.grid_columnconfigure(0, weight=1)
        spd_frame.grid_columnconfigure(1, weight=1)

        self.mode_specific_widgets["lbl_spd_dprd"] = ctk.CTkLabel(
            spd_frame, text="Nomor SPD DPRD :", anchor="w", font=("Arial", 11), text_color="#1E3A8A")
        self.mode_specific_widgets["lbl_spd_dprd"].grid(row=0, column=0, padx=(0, 4), pady=(0, 2), sticky="w")
        self.inputs["nomor_spd_dprd"] = ctk.CTkEntry(spd_frame, placeholder_text="Contoh: 10/SPD/X/2026/")
        self.inputs["nomor_spd_dprd"].grid(row=1, column=0, padx=(0, 4), sticky="ew")
        self.inputs["nomor_spd_dprd"].bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())
        self.mode_specific_widgets["ent_spd_dprd"] = self.inputs["nomor_spd_dprd"]

        self.mode_specific_widgets["lbl_spd_setwan"] = ctk.CTkLabel(
            spd_frame, text="Nomor SPD Setwan (ASN) :", anchor="w", font=("Arial", 11), text_color="#1E3A8A")
        self.mode_specific_widgets["lbl_spd_setwan"].grid(row=0, column=1, padx=(4, 0), pady=(0, 2), sticky="w")
        self.inputs["nomor_spd_asn"] = ctk.CTkEntry(spd_frame, placeholder_text="Contoh: 20/SPD/X/2026/")
        self.inputs["nomor_spd_asn"].grid(row=1, column=1, padx=(4, 0), sticky="ew")
        self.inputs["nomor_spd_asn"].bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        self.lbl_spd_pelaksana = ctk.CTkLabel(
            spd_frame, text="Nomor SPD Pelaksana ASN :", anchor="w", font=("Arial", 11), text_color="#1E3A8A")
        self.ent_spd_pelaksana = ctk.CTkEntry(spd_frame, placeholder_text="Contoh: 10/SPD-PL/X/2026/")
        self.ent_spd_pelaksana.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        self.lbl_spd_pendamping = ctk.CTkLabel(
            spd_frame, text="Nomor SPD Pendamping ASN :", anchor="w", font=("Arial", 11), text_color="#059669")
        self.ent_spd_pendamping = ctk.CTkEntry(spd_frame, placeholder_text="Contoh: 20/SPD-PD/X/2026/")
        self.ent_spd_pendamping.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        lbl_spd_info = ctk.CTkLabel(
            self.middle_frame,
            text="ℹ️  SPD DPRD: semua anggota pakai nomor sama  |  SPD ASN: nomor otomatis berurutan",
            anchor="w", font=("Arial", 10), text_color="gray")
        lbl_spd_info.pack(fill="x", padx=10, pady=(0, 6))
        self.mode_specific_widgets["lbl_spd_info"] = lbl_spd_info

        # --- Dasar Surat Tugas ---------------------------------------------
        lbl_dasar_title = ctk.CTkLabel(self.middle_frame, text="Dasar Surat Tugas", anchor="w", font=("Arial", 12, "bold"))
        lbl_dasar_title.pack(fill="x", padx=10, pady=(10, 2))

        dasar_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        dasar_frame.pack(fill="x", padx=10, pady=(0, 6))
        dasar_frame.grid_columnconfigure(0, weight=1)
        dasar_frame.grid_columnconfigure(1, weight=1)

        lbl_dasar_dprd = ctk.CTkLabel(dasar_frame, text="Dasar Surat Tugas DPRD :", anchor="w",
                                       font=("Arial", 11), text_color="#1E3A8A")
        lbl_dasar_dprd.grid(row=0, column=0, padx=(0, 4), pady=(0, 2), sticky="w")
        self.txt_dasar_dprd = ctk.CTkTextbox(dasar_frame, height=60, wrap="word")
        self.txt_dasar_dprd.grid(row=1, column=0, padx=(0, 4), sticky="ew")
        self.txt_dasar_dprd.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        lbl_dasar_asn = ctk.CTkLabel(dasar_frame, text="Dasar Surat Tugas ASN :", anchor="w",
                                      font=("Arial", 11), text_color="#1E3A8A")
        lbl_dasar_asn.grid(row=0, column=1, padx=(4, 0), pady=(0, 2), sticky="w")
        self.txt_dasar_asn = ctk.CTkTextbox(dasar_frame, height=60, wrap="word")
        self.txt_dasar_asn.grid(row=1, column=1, padx=(4, 0), sticky="ew")
        self.txt_dasar_asn.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        # --- Materi / Agenda Kegiatan --------------------------------------
        lbl_materi_title = ctk.CTkLabel(self.middle_frame, text="Materi / Agenda Kegiatan", anchor="w", font=("Arial", 12, "bold"))
        lbl_materi_title.pack(fill="x", padx=10, pady=(10, 2))

        materi_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        materi_frame.pack(fill="x", padx=10, pady=(0, 6))
        materi_frame.grid_columnconfigure(0, weight=1)
        materi_frame.grid_columnconfigure(1, weight=1)

        lbl_mt_st = ctk.CTkLabel(materi_frame, text="Surat Tugas & SPPD :", anchor="w",
                                   font=("Arial", 11), text_color="#1E3A8A")
        lbl_mt_st.grid(row=0, column=0, padx=(0, 4), pady=(0, 2), sticky="w")
        self.txt_materi_st = ctk.CTkTextbox(materi_frame, height=70, wrap="word")
        self.txt_materi_st.grid(row=1, column=0, padx=(0, 4), sticky="ew")
        self.txt_materi_st.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        lbl_mt_pb = ctk.CTkLabel(materi_frame, text="Surat Pemberitahuan :", anchor="w",
                                   font=("Arial", 11), text_color="#1E3A8A")
        lbl_mt_pb.grid(row=0, column=1, padx=(4, 0), pady=(0, 2), sticky="w")
        self.txt_materi_pb = ctk.CTkTextbox(materi_frame, height=70, wrap="word")
        self.txt_materi_pb.grid(row=1, column=1, padx=(4, 0), sticky="ew")
        self.txt_materi_pb.bind("<KeyRelease>", lambda e: self.schedule_preview_refresh())

        # --- Jenis Perjalanan -----------------------------------------------
        lbl_jp = ctk.CTkLabel(self.middle_frame, text="Jenis Perjalanan", anchor="w", font=("Arial", 12, "bold"))
        lbl_jp.pack(fill="x", padx=10, pady=(8, 2))
        self.combo_jenis = ctk.CTkComboBox(
            self.middle_frame,
            values=["Kunjungan Kerja", "Kunjungan Konsultasi", "Bimbingan Teknis"],
            command=lambda choice: self.schedule_preview_refresh(immediate=True)
        )
        self.combo_jenis.pack(fill="x", padx=10, pady=(0, 6))

        # --- Tanggal-tanggal --------------------------------------------------
        lbl_tgl_surat = ctk.CTkLabel(self.middle_frame, text="Tanggal Surat", anchor="w", font=("Arial", 12, "bold"))
        lbl_tgl_surat.pack(fill="x", padx=10, pady=(8, 2))
        self.dp_surat = self._buat_date_picker(on_change=lambda e=None: self.schedule_preview_refresh())

        lbl_tgl_mulai = ctk.CTkLabel(self.middle_frame, text="Tanggal Mulai Tugas", anchor="w", font=("Arial", 12, "bold"))
        lbl_tgl_mulai.pack(fill="x", padx=10, pady=(8, 2))
        self.dp_mulai = self._buat_date_picker(on_change=lambda e=None: self.calculate_duration())

        lbl_tgl_akhir = ctk.CTkLabel(self.middle_frame, text="Tanggal Akhir Tugas", anchor="w", font=("Arial", 12, "bold"))
        lbl_tgl_akhir.pack(fill="x", padx=10, pady=(8, 2))
        self.dp_akhir = self._buat_date_picker(on_change=lambda e=None: self.calculate_duration())

        lbl_lama_hari = ctk.CTkLabel(self.middle_frame, text="Lama Hari Perjalanan (Otomatis)",
                                      anchor="w", font=("Arial", 12, "bold"))
        lbl_lama_hari.pack(fill="x", padx=10, pady=(8, 2))
        self.ent_lama_hari = ctk.CTkEntry(self.middle_frame, fg_color="#F3F4F6")
        self.ent_lama_hari.pack(fill="x", padx=10, pady=(0, 6))

        # --- Kota Tujuan (multi lokasi) ---------------------------------------
        lbl_tujuan = ctk.CTkLabel(self.middle_frame, text="Kota Tujuan Bertugas (Multi Lokasi)",
                                   anchor="w", font=("Arial", 12, "bold"))
        lbl_tujuan.pack(fill="x", padx=10, pady=(8, 2))

        tujuan_input_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        tujuan_input_frame.pack(fill="x", padx=10, pady=(0, 2))
        tujuan_input_frame.grid_columnconfigure(0, weight=1)

        self.ent_tujuan = ctk.CTkEntry(tujuan_input_frame, placeholder_text="Ketik nama kota lalu klik Tambah...")
        self.ent_tujuan.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.ent_tujuan.bind("<KeyRelease>", self.on_tujuan_key_release)
        self.btn_tambah_tujuan = ctk.CTkButton(tujuan_input_frame, text="+ Tambah",
                                                width=80, command=self.tambah_tujuan)
        self.btn_tambah_tujuan.grid(row=0, column=1, sticky="e")

        self.suggestion_frame = ctk.CTkScrollableFrame(self.middle_frame, height=110, fg_color="#F3F4F6")

        lbl_tujuan_terpilih = ctk.CTkLabel(self.middle_frame, text="Lokasi yang dipilih:",
                                             anchor="w", font=("Arial", 11), text_color="gray")
        lbl_tujuan_terpilih.pack(fill="x", padx=10, pady=(4, 1))
        self.tujuan_list_frame = ctk.CTkScrollableFrame(self.middle_frame, height=80, fg_color="#F0F4FF")
        self.tujuan_list_frame.pack(fill="x", padx=10, pady=(0, 6))

        lbl_tujuan_hint = ctk.CTkLabel(
            self.middle_frame,
            text="ℹ️  Klik ✕ pada lokasi untuk menghapus. Urutan sesuai tampilan.",
            anchor="w", font=("Arial", 10), text_color="gray")
        lbl_tujuan_hint.pack(fill="x", padx=10, pady=(0, 6))

        # --- Penandatangan -----------------------------------------------------
        self.lbl_sign_dprd = ctk.CTkLabel(self.middle_frame, text="Penandatangan DPRD:", font=("Arial", 12, "bold"))
        self.lbl_sign_dprd.pack(fill="x", padx=10, pady=(15, 2))
        self.combo_ttd_dprd = ctk.CTkComboBox(self.middle_frame, values=["-"], height=32,
                                               command=lambda choice: self.schedule_preview_refresh(immediate=True))
        self.combo_ttd_dprd.pack(fill="x", padx=10, pady=(0, 8))

        self.lbl_sign_asn = ctk.CTkLabel(self.middle_frame, text="Penandatangan ASN / SPPD:", font=("Arial", 12, "bold"))
        self.lbl_sign_asn.pack(fill="x", padx=10, pady=(10, 2))
        self.combo_ttd_asn = ctk.CTkComboBox(self.middle_frame, values=["-"], height=32,
                                              command=lambda choice: self.schedule_preview_refresh(immediate=True))
        self.combo_ttd_asn.pack(fill="x", padx=10, pady=(0, 8))

        self.refresh_signer_dropdowns()
        self.refresh_tujuan_list_ui()

        if self.mode == "setwan":
            self._apply_mode_setwan_visibility()

    def _buat_date_picker(self, on_change):
        """Helper kecil: membuat DateEntry (jika tkcalendar tersedia)
        atau CTkEntry biasa sebagai fallback, lalu mem-binding event
        perubahannya ke `on_change`."""
        if HAS_TKCALENDAR:
            picker = DateEntry(self.middle_frame, width=15, background='#2563EB',
                                foreground='white', borderwidth=1, date_pattern='dd/mm/yyyy')
            picker.pack(fill="x", padx=10, pady=(0, 6))
            picker.bind("<<DateEntrySelected>>", on_change)
        else:
            picker = ctk.CTkEntry(self.middle_frame)
            picker.pack(fill="x", padx=10, pady=(0, 6))
            picker.bind("<KeyRelease>", on_change)
        return picker

    def _apply_initial_default_values(self):
        """Mengisi nilai contoh default. Hanya dipanggil SEKALI saat
        aplikasi pertama dibuka."""
        self.inputs["nomor_surat"].insert(0, "170/DPRD/X/2026")
        self.inputs["nomor_surat_asn"].insert(0, "170/SEK-DPRD/X/2026")
        self.inputs["nomor_pemberitahuan_dprd"].insert(0, "180/DPRD/X/2026")
        self.inputs["nomor_pemberitahuan_asn"].insert(0, "181/SEK-DPRD/X/2026")
        self.inputs["nomor_spd_dprd"].insert(0, "090/SPD/")
        self.inputs["nomor_spd_asn"].insert(0, "091/SPD/")
        self.txt_materi_st.insert("1.0", "Studi Banding terkait Pembahasan Peraturan Daerah")
        self.txt_materi_pb.insert("1.0", "Pimpinan dan Anggota DPRD Kota Bitung akan melakukan Studi Banding terkait Pembahasan Peraturan Daerah")
        self.txt_dasar_dprd.insert("1.0", "Keputusan Pimpinan DPRD Kota Bitung")
        self.txt_dasar_asn.insert("1.0", "Surat Perintah Sekretaris DPRD Kota Bitung")

        self.tujuan_terpilih = ["Kota Manado"]
        self.refresh_tujuan_list_ui()

    # ------------------------------------------------------------------
    # MODE DPRD / SETWAN
    # ------------------------------------------------------------------
    def change_mode(self, mode):
        self.mode = "setwan" if mode == "Setwan" else "dprd"
        if self.current_view != "perjalanan_dinas":
            self.setup_category_checkboxes()
            self.refresh_personnel_list()
            return

        if self.mode == "dprd":
            self._apply_mode_dprd_visibility()
        else:
            self._apply_mode_setwan_visibility()

        self.setup_category_checkboxes()
        self.category_check_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.refresh_personnel_list()
        self.refresh_signer_dropdowns()
        self.schedule_preview_refresh(immediate=True)

    def _apply_mode_dprd_visibility(self):
        self.lbl_sign_dprd.pack(fill="x", padx=10, pady=(15, 2), before=self.lbl_sign_asn)
        self.combo_ttd_dprd.pack(fill="x", padx=10, pady=(0, 8), before=self.lbl_sign_asn)
        self.inputs["nomor_surat"].configure(placeholder_text="Masukkan nomor surat tugas dprd...")
        self.mode_specific_widgets["lbl_pemberitahuan_dprd"].pack(fill="x", padx=10, pady=(8, 2))
        self.mode_specific_widgets["ent_pemberitahuan_dprd"].pack(fill="x", padx=10, pady=(0, 6))
        self.mode_specific_widgets["lbl_spd_dprd"].grid(row=0, column=0, padx=(0, 4), pady=(0, 2), sticky="w")
        self.mode_specific_widgets["ent_spd_dprd"].grid(row=1, column=0, padx=(0, 4), sticky="ew")
        self.mode_specific_widgets["lbl_spd_setwan"].grid(row=0, column=1, padx=(4, 0), pady=(0, 2), sticky="w")
        self.mode_specific_widgets["lbl_spd_info"].configure(
            text="ℹ️  SPD DPRD: semua anggota pakai nomor sama  |  SPD ASN: nomor otomatis berurutan")
        self.lbl_spd_pelaksana.grid_forget()
        self.ent_spd_pelaksana.grid_forget()
        self.lbl_spd_pendamping.grid_forget()
        self.ent_spd_pendamping.grid_forget()
        self.combo_jenis.configure(values=["Kunjungan Kerja", "Kunjungan Konsultasi", "Bimbingan Teknis"])

    def _apply_mode_setwan_visibility(self):
        self.lbl_sign_dprd.pack_forget()
        self.combo_ttd_dprd.pack_forget()
        self.inputs["nomor_surat"].configure(placeholder_text="Masukkan nomor surat tugas setwan...")
        self.mode_specific_widgets["lbl_pemberitahuan_dprd"].pack_forget()
        self.mode_specific_widgets["ent_pemberitahuan_dprd"].pack_forget()
        self.mode_specific_widgets["lbl_spd_dprd"].grid_forget()
        self.mode_specific_widgets["ent_spd_dprd"].grid_forget()
        self.mode_specific_widgets["lbl_spd_setwan"].grid_forget()
        self.mode_specific_widgets["lbl_spd_info"].configure(
            text="ℹ️  SPD Pelaksana & Pendamping: nomor otomatis berurutan per kategori")
        self.lbl_spd_pelaksana.grid(row=0, column=0, padx=(0, 4), pady=(0, 2), sticky="w")
        self.ent_spd_pelaksana.grid(row=1, column=0, padx=(0, 4), sticky="ew")
        self.lbl_spd_pendamping.grid(row=0, column=1, padx=(4, 0), pady=(0, 2), sticky="w")
        self.ent_spd_pendamping.grid(row=1, column=1, padx=(4, 0), sticky="ew")
        self.combo_jenis.configure(values=["Studi Komparasi", "Kunjungan Konsultasi", "Bimbingan Teknis"])

    # ------------------------------------------------------------------
    # PENANDATANGAN & DURASI
    # ------------------------------------------------------------------
    def refresh_signer_dropdowns(self):
        ttd_dprd_values = [f"{p.get('jabatan', '')} - {p.get('nama', '')}"
                           for p in self.db_dprd if str(p.get('kategori', '')).lower() == 'pimpinan dprd']
        self.combo_ttd_dprd.configure(values=ttd_dprd_values if ttd_dprd_values else ["-"])
        self.combo_ttd_dprd.set(ttd_dprd_values[0] if ttd_dprd_values else "-")

        ttd_asn_values = [f"{p.get('jabatan', '')} - {p.get('nama', '')}"
                          for p in self.db_asn if 'sekretaris dprd' in str(p.get('jabatan', '')).lower()]
        if not ttd_asn_values:
            ttd_asn_values = [f"{p.get('jabatan', '')} - {p.get('nama', '')}" for p in self.db_asn]
        self.combo_ttd_asn.configure(values=ttd_asn_values if ttd_asn_values else ["-"])
        self.combo_ttd_asn.set(ttd_asn_values[0] if ttd_asn_values else "-")

    def calculate_duration(self, *args):
        try:
            if HAS_TKCALENDAR:
                s_date, e_date = self.dp_mulai.get_date(), self.dp_akhir.get_date()
            else:
                s_date = datetime.strptime(self.dp_mulai.get(), "%d/%m/%Y")
                e_date = datetime.strptime(self.dp_akhir.get(), "%d/%m/%Y")
            delta = (e_date - s_date).days + 1
            if delta < 1:
                delta = 1
            self.ent_lama_hari.configure(state="normal")
            self.ent_lama_hari.delete(0, tk.END)
            self.ent_lama_hari.insert(0, str(delta))
            self.ent_lama_hari.configure(state="readonly")
        except Exception:
            pass
        self.schedule_preview_refresh()
