"""
letters/undangan.py
=====================
Logika untuk SURAT UNDANGAN (Rapat Paripurna, dan nanti Undangan
Biasa). Modul ini SENGAJA dipisah total dari surat perjalanan dinas
(surat_tugas.py, pemberitahuan.py, sppd.py, daftar_hadir.py) karena
alur data, template, dan aturan bisnisnya berbeda sepenuhnya:
- Surat Undangan: satu surat, banyak halaman (1 halaman per penerima),
  semua halaman berisi data yang SAMA kecuali nama penerima.
- Surat Perjalanan Dinas: banyak surat berbeda, tergantung jumlah
  pelaksana/tujuan/jenis surat.
"""

import os

from docxtpl import DocxTemplate

from config import TEMPLATE_UNDANGAN_PARIPURNA_CANDIDATES, PENERIMA_UNDANGAN_PARIPURNA
from docx_helpers.combine import combine_word_pages


def find_template_undangan_paripurna():
    """Mencari path template undangan paripurna dari beberapa
    kandidat lokasi yang dikonfigurasi di config.py."""
    for path in TEMPLATE_UNDANGAN_PARIPURNA_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def build_undangan_paripurna_base_context(form_data):
    """Membangun context dasar (tanpa 'penerima') dari data form
    Undangan Paripurna. form_data adalah dict polos, sehingga modul
    ini tidak bergantung pada widget UI apa pun."""
    skenario_list = list(form_data.get("skenario_list", []))
    while len(skenario_list) < 7:
        skenario_list.append("")

    return {
        "nomor_undangan": form_data.get("nomor_undangan", ""),
        "tanggal_surat": form_data.get("tanggal_surat", ""),
        "isi_surat": form_data.get("isi_surat", ""),
        "tanggal_rapat": form_data.get("tanggal_rapat", ""),
        "hari_rapat": form_data.get("hari_rapat", ""),
        "jam_pelaksanaan": form_data.get("jam_pelaksanaan", ""),
        "pakaian": form_data.get("pakaian", ""),
        "jabatan_ttd": form_data.get("jabatan_ttd", ""),
        "nama_ttd": form_data.get("nama_ttd", ""),
        "skenario1": skenario_list[0],
        "skenario2": skenario_list[1],
        "skenario3": skenario_list[2],
        "skenario4": skenario_list[3],
        "skenario5": skenario_list[4],
        "skenario6": skenario_list[5],
        "skenario7": skenario_list[6],
    }


def buat_undangan_paripurna(form_data, out_path, work_dir):
    """Membuat satu file Surat Undangan Paripurna multi-halaman
    (satu halaman per penerima sesuai PENERIMA_UNDANGAN_PARIPURNA).

    Args:
        form_data: dict hasil pembacaan form UI (lihat
            build_undangan_paripurna_base_context).
        out_path: path file output akhir (.docx).
        work_dir: folder sementara untuk menyimpan file per-halaman
            sebelum digabung (biasanya = folder output yang dipilih
            pengguna).
    Returns:
        Jumlah halaman (penerima) yang berhasil dibuat.
    Raises:
        FileNotFoundError jika template tidak ditemukan.
    """
    template_path = find_template_undangan_paripurna()
    if not template_path:
        raise FileNotFoundError(
            "Template Undangan Paripurna tidak ditemukan. "
            "Pastikan file template ada di folder yang benar."
        )

    base_ctx = build_undangan_paripurna_base_context(form_data)

    temp_files = []
    for i, recipient in enumerate(PENERIMA_UNDANGAN_PARIPURNA):
        ctx = base_ctx.copy()
        ctx["penerima"] = recipient
        temp_path = os.path.join(work_dir, f"temp_undangan_{i}.docx")
        doc = DocxTemplate(template_path)
        doc.render(ctx)
        doc.save(temp_path)
        temp_files.append(temp_path)

    combine_word_pages(temp_files, out_path)

    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)

    return len(PENERIMA_UNDANGAN_PARIPURNA)


def render_preview_context(form_data):
    """Context untuk preview halaman pertama (penerima default =
    PIMPINAN DAN ANGGOTA DPRD KOTA BITUNG)."""
    ctx = build_undangan_paripurna_base_context(form_data)
    ctx["penerima"] = PENERIMA_UNDANGAN_PARIPURNA[0]
    return ctx
