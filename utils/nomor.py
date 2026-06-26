"""
utils/nomor.py
==============
Fungsi-fungsi untuk menambah (increment) angka pertama pada format
nomor surat, contoh: "10/SPD/X/2026" + 1 -> "11/SPD/X/2026"
"""


def increment_nomor(nomor_base, increment=0):
    """Increment nomor surat tugas/pemberitahuan biasa."""
    if increment == 0:
        return nomor_base
    parts = nomor_base.split('/')
    try:
        angka = int(parts[0].strip())
        parts[0] = str(angka + increment)
        return '/'.join(parts)
    except (ValueError, IndexError):
        return nomor_base


def increment_nomor_spd(nomor_base, increment=0):
    """Increment nomor SPD (Surat Perintah Dinas), dipisah agar bisa
    diubah independen dari aturan penomoran surat tugas biasa."""
    if increment == 0:
        return nomor_base
    parts = nomor_base.split('/')
    try:
        angka = int(parts[0].strip())
        parts[0] = str(angka + increment)
        return '/'.join(parts)
    except (ValueError, IndexError):
        return nomor_base
