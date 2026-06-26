"""
ui/context_builder.py
=======================
Jembatan antara FORM (widget Tkinter/CTk) dan LOGIKA SURAT
(letters/*.py). Semua fungsi di sini membaca isi widget lalu
menyusunnya menjadi `ctx` (dict polos) atau list personel polos,
baru kemudian memanggil fungsi-fungsi di package `letters`.

Dipisah dari ui/perjalanan_form.py supaya jelas batasnya:
- perjalanan_form.py  -> membangun & menata widget
- context_builder.py  -> membaca widget & menjalankan logika surat
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from optional_deps import HAS_TKCALENDAR
from utils.tanggal import format_indonesian_date, terbilang
from letters.surat_tugas import buat_surat_tugas_dprd, buat_surat_tugas_asn
from letters.pemberitahuan import buat_surat_pemberitahuan_multi
from letters.sppd import buat_sppd_dprd, buat_sppd_asn
from letters.daftar_hadir import buat_daftar_hadir
from config import TEMPLATE_PEMBERITAHUAN, TEMPLATE_SPD_DEPAN, TEMPLATE_SPD_BELAKANG


class ContextBuilderMixin:
    # ------------------------------------------------------------------
    # PEMBACA WIDGET -> DATA POLOS
    # ------------------------------------------------------------------
    def _get_date_str(self, picker):
        if HAS_TKCALENDAR:
            return format_indonesian_date(picker.get_date())
        return picker.get().strip()

    def get_selected_dprd(self):
        return [p for nama, p in self.rendered_dprd_widgets.items()
                if self.dprd_vars.get(nama) and self.dprd_vars[nama].get()]

    def get_selected_asn(self):
        return [p for nama, p in self.rendered_asn_widgets.items()
                if self.asn_vars.get(nama) and self.asn_vars[nama].get()]

    def get_selected_pelaksana(self):
        return [p for nama, p in self.rendered_pelaksana_widgets.items()
                if self.pelaksana_vars.get(f"pelaksana_{nama}") and self.pelaksana_vars[f"pelaksana_{nama}"].get()]

    def get_selected_pendamping(self):
        return [p for nama, p in self.rendered_pendamping_widgets.items()
                if self.pendamping_vars.get(f"pendamping_{nama}") and self.pendamping_vars[f"pendamping_{nama}"].get()]

    def build_context(self):
        """Mengumpulkan semua isi form Perjalanan Dinas menjadi satu
        dict `ctx` yang siap dipakai untuk merender semua jenis surat
        (Surat Tugas, Pemberitahuan, SPD, Daftar Hadir)."""
        ctx = {}
        ctx["nomor_surat"] = self.inputs["nomor_surat"].get().strip()
        ctx["nomor_surat_asn"] = self.inputs["nomor_surat_asn"].get().strip()
        ctx["nomor_pemberitahuan_dprd"] = self.inputs["nomor_pemberitahuan_dprd"].get().strip()
        ctx["nomor_pemberitahuan_asn"] = self.inputs["nomor_pemberitahuan_asn"].get().strip()
        ctx["nomor_spd_dprd"] = self.inputs["nomor_spd_dprd"].get().strip()
        ctx["nomor_spd_asn"] = self.inputs["nomor_spd_asn"].get().strip()
        ctx["nomor_spd_pelaksana"] = self.ent_spd_pelaksana.get().strip()
        ctx["nomor_spd_pendamping"] = self.ent_spd_pendamping.get().strip()

        ctx["dasar_surat_tugas_dprd"] = self.txt_dasar_dprd.get("1.0", tk.END).strip()
        ctx["dasar_surat_tugas_asn"] = self.txt_dasar_asn.get("1.0", tk.END).strip()
        ctx["materi_tugas"] = self.txt_materi_st.get("1.0", tk.END).strip()
        ctx["materi_pemberitahuan"] = self.txt_materi_pb.get("1.0", tk.END).strip()

        ctx["jenis_perjalanan"] = self.combo_jenis.get()
        ctx["tanggal_surat"] = self._get_date_str(self.dp_surat)
        ctx["tanggal_mulai"] = self._get_date_str(self.dp_mulai)
        ctx["tanggal_akhir"] = self._get_date_str(self.dp_akhir)

        lama_hari_str = self.ent_lama_hari.get().strip() or "1"
        try:
            lama_hari = int(lama_hari_str)
        except ValueError:
            lama_hari = 1
        ctx["lama_hari"] = lama_hari
        ctx["lama_hari_terbilang"] = terbilang(lama_hari)

        ctx["destinations"] = list(self.tujuan_terpilih)
        ctx["tujuan_bertugas"] = ", ".join(self.tujuan_terpilih) if self.tujuan_terpilih else "-"

        ctx["ttd_dprd"] = self.combo_ttd_dprd.get()
        ctx["ttd_asn"] = self.combo_ttd_asn.get()
        if " - " in ctx["ttd_dprd"]:
            jab, nama = ctx["ttd_dprd"].split(" - ", 1)
            ctx["jabatan_ttd_dprd"], ctx["nama_ttd_dprd"] = jab.strip(), nama.strip()
        if " - " in ctx["ttd_asn"]:
            jab, nama = ctx["ttd_asn"].split(" - ", 1)
            ctx["jabatan_ttd_asn"], ctx["nama_ttd_asn"] = jab.strip(), nama.strip()

        ctx["transportasi_otomatis"] = "Pesawat Udara" if any(
            "DKI" in d or "Jakarta" in d or not self._kota_di_sulut(d) for d in self.tujuan_terpilih
        ) else "Mobil/Darat"

        return ctx

    def _kota_di_sulut(self, kota):
        from utils.geo import extract_city_name, is_in_sulawesi_utara
        return is_in_sulawesi_utara(extract_city_name(kota))

    # ------------------------------------------------------------------
    # AKSI UTAMA: CETAK SEMUA DOKUMEN
    # ------------------------------------------------------------------
    def generate_documents_action(self):
        ctx = self.build_context()

        if self.mode == "dprd":
            sel_dprd = self.get_selected_dprd()
            sel_asn = self.get_selected_asn()
        else:
            sel_dprd = []
            sel_asn = self.get_selected_pelaksana() + self.get_selected_pendamping()

        if not ctx["destinations"]:
            messagebox.showwarning("Peringatan", "Silakan tambahkan minimal satu Kota Tujuan Bertugas.")
            return
        if not sel_dprd and not sel_asn:
            messagebox.showwarning("Peringatan", "Silakan pilih minimal satu personel pelaksana.")
            return

        out_dir = filedialog.askdirectory(title="Pilih Folder Penyimpanan Dokumen")
        if not out_dir:
            return

        try:
            generated = []

            if sel_dprd:
                out_st_dprd = os.path.join(out_dir, "Surat_Tugas_DPRD.docx")
                buat_surat_tugas_dprd(ctx, sel_dprd, out_st_dprd)
                generated.append(out_st_dprd)

                out_spd_d_depan = os.path.join(out_dir, "SPD_DPRD_Depan.docx")
                out_spd_d_belakang = os.path.join(out_dir, "SPD_DPRD_Belakang.docx")
                buat_sppd_dprd(TEMPLATE_SPD_DEPAN, TEMPLATE_SPD_BELAKANG, ctx, sel_dprd,
                                ctx["destinations"], out_spd_d_depan, out_spd_d_belakang)
                generated += [out_spd_d_depan, out_spd_d_belakang]

            if sel_asn:
                out_st_asn = os.path.join(out_dir, "Surat_Tugas_ASN.docx")
                buat_surat_tugas_asn(ctx, sel_asn, out_st_asn)
                generated.append(out_st_asn)

                out_spd_a_depan = os.path.join(out_dir, "SPD_ASN_Depan.docx")
                out_spd_a_belakang = os.path.join(out_dir, "SPD_ASN_Belakang.docx")
                buat_sppd_asn(TEMPLATE_SPD_DEPAN, TEMPLATE_SPD_BELAKANG, ctx, sel_asn,
                              ctx["destinations"], out_spd_a_depan, out_spd_a_belakang)
                generated += [out_spd_a_depan, out_spd_a_belakang]

            if self.mode == "dprd" and os.path.exists(TEMPLATE_PEMBERITAHUAN):
                out_pemberitahuan = os.path.join(out_dir, "Surat_Pemberitahuan.docx")
                base_number = ctx.get("nomor_pemberitahuan_dprd", "")
                buat_surat_pemberitahuan_multi(TEMPLATE_PEMBERITAHUAN, ctx, sel_dprd, sel_asn,
                                                ctx["destinations"], base_number, out_pemberitahuan)
                generated.append(out_pemberitahuan)

            semua_pelaksana = sel_dprd + sel_asn
            if semua_pelaksana:
                out_daftar_hadir = os.path.join(out_dir, "Daftar_Hadir.docx")
                buat_daftar_hadir(ctx, semua_pelaksana, ctx["destinations"], self.mode, out_daftar_hadir)
                generated.append(out_daftar_hadir)

            nomor_key = ctx.get("nomor_surat") or ctx.get("nomor_surat_asn") or "TANPA_NOMOR"
            self.history_db.record(nomor_key, {
                "ctx": ctx,
                "selected_dprd": [p.get("nama") for p in sel_dprd],
                "selected_asn": [p.get("nama") for p in sel_asn],
                "mode": self.mode,
            })
            self.combo_history.configure(values=self.history_db.keys())

            messagebox.showinfo("Berhasil", f"{len(generated)} dokumen berhasil dibuat di:\n{out_dir}")
        except FileNotFoundError as e:
            messagebox.showerror("Template Tidak Ditemukan", str(e))
        except Exception as e:
            messagebox.showerror("Gagal Membuat Dokumen", f"Terjadi kesalahan:\n{e}")

    # ------------------------------------------------------------------
    # RIWAYAT
    # ------------------------------------------------------------------
    def load_selected_history(self):
        nomor_key = self.combo_history.get()
        data = self.history_db.get(nomor_key)
        if not data:
            messagebox.showwarning("Peringatan", "Riwayat tidak ditemukan.")
            return

        ctx = data.get("ctx", {})
        mode = data.get("mode", "dprd")
        self.mode_selector.set("DPRD" if mode == "dprd" else "Setwan")
        self.change_mode("DPRD" if mode == "dprd" else "Setwan")

        def _set_entry(entry, val):
            entry.delete(0, tk.END)
            entry.insert(0, val or "")

        _set_entry(self.inputs["nomor_surat"], ctx.get("nomor_surat", ""))
        _set_entry(self.inputs["nomor_surat_asn"], ctx.get("nomor_surat_asn", ""))
        _set_entry(self.inputs["nomor_pemberitahuan_dprd"], ctx.get("nomor_pemberitahuan_dprd", ""))
        _set_entry(self.inputs["nomor_pemberitahuan_asn"], ctx.get("nomor_pemberitahuan_asn", ""))
        _set_entry(self.inputs["nomor_spd_dprd"], ctx.get("nomor_spd_dprd", ""))
        _set_entry(self.inputs["nomor_spd_asn"], ctx.get("nomor_spd_asn", ""))

        self.txt_dasar_dprd.delete("1.0", tk.END)
        self.txt_dasar_dprd.insert("1.0", ctx.get("dasar_surat_tugas_dprd", ""))
        self.txt_dasar_asn.delete("1.0", tk.END)
        self.txt_dasar_asn.insert("1.0", ctx.get("dasar_surat_tugas_asn", ""))
        self.txt_materi_st.delete("1.0", tk.END)
        self.txt_materi_st.insert("1.0", ctx.get("materi_tugas", ""))
        self.txt_materi_pb.delete("1.0", tk.END)
        self.txt_materi_pb.insert("1.0", ctx.get("materi_pemberitahuan", ""))

        self.tujuan_terpilih = list(ctx.get("destinations", []))
        self.refresh_tujuan_list_ui()

        for nama in data.get("selected_dprd", []):
            if nama in self.dprd_vars:
                self.dprd_vars[nama].set(True)
        for nama in data.get("selected_asn", []):
            if nama in self.asn_vars:
                self.asn_vars[nama].set(True)
            key_pl, key_pd = f"pelaksana_{nama}", f"pendamping_{nama}"
            if key_pl in self.pelaksana_vars:
                self.pelaksana_vars[key_pl].set(True)
            if key_pd in self.pendamping_vars:
                self.pendamping_vars[key_pd].set(True)

        self.refresh_personnel_list()
        self.schedule_preview_refresh(immediate=True)
        messagebox.showinfo("Berhasil", f"Data surat '{nomor_key}' berhasil dimuat.")
