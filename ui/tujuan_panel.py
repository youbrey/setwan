"""
ui/tujuan_panel.py
====================
Mixin untuk input "Kota Tujuan Bertugas" (multi lokasi) dengan
autocomplete sederhana. Dipakai baik oleh form Perjalanan Dinas.
"""

import tkinter as tk
import customtkinter as ctk


class TujuanPanelMixin:
    def tambah_tujuan(self):
        val = self.ent_tujuan.get().strip()
        if not val:
            return
        if val not in self.tujuan_terpilih:
            self.tujuan_terpilih.append(val)
            self.refresh_tujuan_list_ui()
        self.ent_tujuan.delete(0, tk.END)
        self.hide_tujuan_suggestions()
        self.schedule_preview_refresh(immediate=True)

    def hapus_tujuan(self, kota):
        if kota in self.tujuan_terpilih:
            self.tujuan_terpilih.remove(kota)
            self.refresh_tujuan_list_ui()
            self.schedule_preview_refresh(immediate=True)

    def refresh_tujuan_list_ui(self):
        for w in self.tujuan_list_frame.winfo_children():
            w.destroy()
        if not self.tujuan_terpilih:
            lbl = ctk.CTkLabel(self.tujuan_list_frame, text="(Belum ada tujuan)",
                                text_color="gray", font=("Arial", 11))
            lbl.pack(padx=8, pady=4, anchor="w")
        for kota in self.tujuan_terpilih:
            row_frame = ctk.CTkFrame(self.tujuan_list_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=4, pady=2)
            lbl = ctk.CTkLabel(row_frame, text=f"📍 {kota}", anchor="w",
                                font=("Arial", 11), text_color="#1E3A8A")
            lbl.pack(side="left", padx=(4, 8))
            btn_del = ctk.CTkButton(row_frame, text="✕", width=28, height=22,
                                     fg_color="#EF4444", hover_color="#DC2626",
                                     font=("Arial", 10, "bold"),
                                     command=lambda k=kota: self.hapus_tujuan(k))
            btn_del.pack(side="right", padx=2)

    def on_tujuan_key_release(self, event):
        val = self.ent_tujuan.get().strip().lower()
        if len(val) >= 2:
            matches = [item for item in self.database_tujuan if val in item.lower()]
            if matches:
                self.show_tujuan_suggestions(matches)
            else:
                self.hide_tujuan_suggestions()
        else:
            self.hide_tujuan_suggestions()
        if event.keysym == "Return":
            self.tambah_tujuan()

    def show_tujuan_suggestions(self, matches):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        for match in matches[:6]:
            btn = ctk.CTkButton(self.suggestion_frame, text=match, anchor="w",
                                 fg_color="transparent", text_color="black", hover_color="#E5E7EB",
                                 command=lambda m=match: self.select_tujuan_suggestion(m))
            btn.pack(fill="x", padx=5, pady=1)
        self.suggestion_frame.pack(fill="x", padx=10, pady=2, before=self.tujuan_list_frame)

    def hide_tujuan_suggestions(self):
        self.suggestion_frame.pack_forget()

    def select_tujuan_suggestion(self, val):
        self.ent_tujuan.delete(0, tk.END)
        self.ent_tujuan.insert(0, val)
        self.hide_tujuan_suggestions()
        self.tambah_tujuan()
