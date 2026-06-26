"""
letters/daftar_hadir.py
=========================
Logika untuk membuat Daftar Hadir, satu halaman per tujuan perjalanan
dinas, dengan judul yang otomatis menyesuaikan kategori pelaksana
(Pimpinan/Anggota/Komisi) dan instansi tujuan.
"""

import os
import tempfile

from docxtpl import DocxTemplate
from docx import Document

from config import TEMPLATE_DAFTAR_HADIR
from utils.geo import extract_city_name
from utils.tanggal import generate_periods
from docx_helpers.table_ops import fill_table_rows_from_master
from docx_helpers.combine import combine_word_pages


def build_judul_daftar_hadir(pelaksana_list, tujuan, jenis_perjalanan, materi, mode):
    """Membangun judul daftar hadir yang menyesuaikan kategori pelaksana
    (mis. 'PIMPINAN DAN ANGGOTA KOMISI I') dan instansi tujuan."""
    kategori_set = set()
    for p in pelaksana_list:
        kat = p.get('kategori', '').strip()
        if kat:
            kategori_set.add(kat)

    if len(kategori_set) == 1:
        kategori = list(kategori_set)[0]
        if kategori in ["Pimpinan DPRD", "Komisi I", "Komisi II", "Komisi III"]:
            has_pimpinan = any(
                "ketua" in p.get('jabatan', '').lower() or
                "wakil" in p.get('jabatan', '').lower() or
                "sekretaris" in p.get('jabatan', '').lower()
                for p in pelaksana_list
            )
            has_anggota = any(
                "anggota" in p.get('jabatan', '').lower()
                for p in pelaksana_list
            )
            if has_pimpinan and has_anggota:
                label = f"Pimpinan dan Anggota {kategori}"
            elif has_pimpinan:
                label = f"Pimpinan {kategori}"
            elif has_anggota:
                label = f"Anggota {kategori}"
            else:
                label = kategori
            if "DPRD" not in label:
                label = f"{label} DPRD Kota Bitung"
            pelaku_str = label.upper()
        else:
            pelaku_str = "PIMPINAN DAN ANGGOTA DPRD KOTA BITUNG"
    else:
        pelaku_str = "PIMPINAN DAN ANGGOTA DPRD KOTA BITUNG"

    tujuan_daerah = extract_city_name(tujuan)
    if "DPRD" not in tujuan_daerah.upper():
        instansi_tujuan = f"DPRD {tujuan_daerah}"
    else:
        instansi_tujuan = tujuan_daerah

    jenis = jenis_perjalanan.upper().strip()
    materi_upper = materi.upper().strip()

    judul_pelaksana = f"{pelaku_str} PADA {jenis} KE {instansi_tujuan} TENTANG {materi_upper}"
    judul_tujuan = f"{instansi_tujuan} PADA {jenis} {pelaku_str} KE {instansi_tujuan} TENTANG {materi_upper}"

    return judul_pelaksana, judul_tujuan


def buat_daftar_hadir(ctx, pelaksana_list, destinations, mode, out_path):
    """Membuat dokumen Daftar Hadir, satu halaman per tujuan."""
    template_path = TEMPLATE_DAFTAR_HADIR
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template {template_path} tidak ditemukan.")

    periods = generate_periods(ctx.get("tanggal_mulai", ""), destinations)

    temp_files = []
    for period in periods:
        tujuan = period["tujuan"]
        hari = period["hari"]
        tanggal = period["tanggal"]

        judul_pelaksana, judul_tujuan = build_judul_daftar_hadir(
            pelaksana_list, tujuan, ctx.get("jenis_perjalanan", ""), ctx.get("materi_tugas", ""), mode
        )

        render_ctx = {
            "MATERI_TUGAS_DPRD_DAFTAR_HADIR": judul_pelaksana,
            "TEMPAT_TUGAS_DPRD_DAFTAR_HADIR": judul_tujuan,
            "HARI": hari,
            "TANGGAL_DAFTAR_HADIR": tanggal,
            "TEMPAT_DAFTAR_HADIR": tujuan,
            "loop": {"index": ""},
            "tabel": {"NAMA_DAFTAR_HADIR": "", "jabatan_daftar_hadir": ""}
        }

        doc_tpl = DocxTemplate(template_path)
        doc_tpl.render(render_ctx)
        tmp_file = tempfile.NamedTemporaryFile(suffix=".docx", delete=False).name
        doc_tpl.save(tmp_file)

        doc = Document(tmp_file)
        header_keywords = ["no", "nama", "jabatan", "tanda tangan"]
        rows_data = []
        for i, p in enumerate(pelaksana_list):
            rows_data.append([
                str(i + 1),
                p.get('nama', ''),
                p.get('jabatan', '')
            ])
        fill_table_rows_from_master(doc, header_keywords, rows_data)
        doc.save(tmp_file)
        temp_files.append(tmp_file)

    if temp_files:
        combine_word_pages(temp_files, out_path)
    else:
        raise Exception("Tidak ada halaman yang dihasilkan.")

    for f in temp_files:
        try:
            os.unlink(f)
        except Exception:
            pass
