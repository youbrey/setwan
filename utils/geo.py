"""
utils/geo.py
============
Fungsi-fungsi untuk mengekstrak nama kota/kabupaten/provinsi dari teks,
dan mengecek apakah suatu kota termasuk Sulawesi Utara atau Jabodetabek.
"""

import re

from config import SULAWESI_UTARA_CITIES, JABODETABEK_CITIES


def extract_city_name(text):
    text = text.strip()
    match = re.search(r'(Kota|Kabupaten|Provinsi)\s+([\w\s]+)', text)
    if match:
        return f"{match.group(1)} {match.group(2).strip()}"
    if "DKI Jakarta" in text:
        return "Kota Jakarta"
    if "Jakarta" in text:
        return "Kota Jakarta"
    return text


def is_in_sulawesi_utara(city_name):
    for c in SULAWESI_UTARA_CITIES:
        if c in city_name:
            return True
    return False


def is_in_jabodetabek(city_name):
    for c in JABODETABEK_CITIES:
        if c in city_name:
            return True
    return False
