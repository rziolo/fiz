#!/usr/bin/env python3
# Plik: /var/www/html/flask/inwestycje/etl/python/gpw_archiwum.py (lub dowolna lokalizacja na nowym serwerze)

import requests
from bs4 import BeautifulSoup
from datetime import date
import subprocess
import sys
import os

# --- KONFIGURACJA DLA NOWEGO SERWERA ---
# URL może wskazywać na inne archiwum (np. inna giełda, inna domena)
GPW_URL = "https://www.gpw.pl/archiwum-notowan-full?type=10&date={}&fetch=1"
# Ścieżka docelowa CSV – zgodna z podaną w zadaniu
CSV_PATH = "/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"
# Opcjonalny plik debug HTML (można zmienić lub usunąć)
DEBUG_HTML = "/tmp/gpw_debug_new.html"

def write_with_sudo_tee(content: str, file_path: str) -> bool:
    """
    Zapisuje treść do pliku przy użyciu 'sudo tee'.
    Zwraca True jeśli sukces, False w przypadku błędu.
    """
    try:
        # Uruchomienie: echo "content" | sudo tee file_path
        proc = subprocess.Popen(
            ['sudo', 'tee', file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )
        _, stderr = proc.communicate(input=content)
        if proc.returncode != 0:
            print(f"Błąd sudo tee: {stderr.strip()}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"Wyjątek podczas zapisu przez sudo tee: {e}", file=sys.stderr)
        return False

def check_gpw_data_for_today():
    today_str = date.today().strftime("%Y-%m-%d")
    url = GPW_URL.format(today_str)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Błąd pobierania strony GPW: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Zapis HTML do debugu (opcjonalnie)
    try:
        with open(DEBUG_HTML, "w", encoding="utf-8") as f:
            f.write(response.text)
    except IOError:
        pass  # ignorujemy błędy zapisu debugowego

    # Detekcja braku danych
    page_text = soup.get_text()
    if "Brak danych dla wybranych kryteriów." in page_text:
        result = "brak"
    else:
        result = "OK"

    # Zapis wyniku do CSV przez sudo tee
    if write_with_sudo_tee(result + "\n", CSV_PATH):
        print(f"Zapisano wynik '{result}' do {CSV_PATH} (przez sudo tee)")
    else:
        print(f"Nie udało się zapisać wyniku do {CSV_PATH}")

if __name__ == "__main__":
    check_gpw_data_for_today()
