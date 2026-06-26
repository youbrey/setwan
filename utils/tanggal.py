"""
utils/tanggal.py
================
Fungsi-fungsi terkait tanggal & hari dalam Bahasa Indonesia:
- generate_periods: membuat daftar (tujuan, hari, tanggal) berurutan
  tanpa duplikasi hari, dipakai oleh surat pemberitahuan & daftar hadir.
- terbilang: angka -> teks bilangan Indonesia (mis. 3 -> "Tiga").
- format_indonesian_date: objek datetime -> "25 Juni 2026".
"""

from datetime import datetime, timedelta

from utils.geo import extract_city_name, is_in_sulawesi_utara

BULAN_INDONESIA = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

BULAN_MAP = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
    "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
    "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}

HARI_INDONESIA = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}


def format_indonesian_date(date_obj):
    """Format objek date/datetime menjadi 'D Bulan YYYY' (Bahasa Indonesia)."""
    if not date_obj:
        return ""
    return f"{date_obj.day} {BULAN_INDONESIA[date_obj.month]} {date_obj.year}"


def terbilang(n):
    """Konversi angka menjadi teks bilangan Indonesia (untuk angka kecil,
    cukup untuk kebutuhan 'lama hari perjalanan')."""
    satuan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh",
              "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12:
        return satuan[n]
    elif n < 20:
        return terbilang(n - 10) + " Belas"
    elif n < 100:
        sisa = satuan[n % 10] if n % 10 != 0 else ""
        return terbilang(n // 10) + " Puluh " + sisa
    return str(n)


def generate_periods(tanggal_mulai_str, destinations):
    """Menghasilkan daftar dict {tujuan, hari, tanggal} berurutan untuk
    setiap tujuan, dimulai dari tanggal_mulai_str (atau +1 hari jika
    tujuan pertama berada di luar Sulawesi Utara, karena dianggap butuh
    1 hari perjalanan)."""
    parts = tanggal_mulai_str.split()
    if len(parts) == 3:
        day = int(parts[0])
        month = BULAN_MAP.get(parts[1], 1)
        year = int(parts[2])
        start_date = datetime(year, month, day)
    else:
        start_date = datetime.now()

    first_city = extract_city_name(destinations[0]) if destinations else ""
    offset = 0 if is_in_sulawesi_utara(first_city) else 1
    base_date = start_date + timedelta(days=offset)

    periods = []
    for idx, dest in enumerate(destinations):
        current_date = base_date + timedelta(days=idx)
        hari_eng = current_date.strftime("%A")
        hari = HARI_INDONESIA.get(hari_eng, hari_eng)
        tanggal_str = f"{current_date.day} {BULAN_INDONESIA[current_date.month]} {current_date.year}"
        periods.append({
            "tujuan": dest,
            "hari": hari,
            "tanggal": tanggal_str
        })
    return periods
