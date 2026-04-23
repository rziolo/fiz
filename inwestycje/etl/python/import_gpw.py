import requests
import pandas as pd
from datetime import date
import os
import sys
import time
import io
import random

# Konfiguracja ścieżek
BASE_DIR = "/var/www/html/flask/inwestycje"
SAVE_XLS_DIR = os.path.join(BASE_DIR, "etl/excel")
SAVE_CSV = os.path.join(BASE_DIR, "etl/csv/import_gpw.csv")
GPW_URL = "https://www.gpw.pl/archiwum-notowan-full?type=10&date={}&fetch=1"

def download_gpw():
    today_str = date.today().strftime("%Y-%m-%d")
    url = GPW_URL.format(today_str)
    
    # Bardzo realistyczne nagłówki przeglądarki Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        session = requests.Session()
        
        # Krok 1: Inicjalizacja z losowym opóźnieniem
        print("Inicjowanie sesji (symulacja użytkownika)...")
        time.sleep(random.uniform(1.5, 3.5))
        session.get("https://www.gpw.pl/", headers=headers, timeout=20)
        
        # Krok 2: Wejście na stronę archiwum (symulacja kliknięcia)
        print("Wchodzenie na stronę archiwum...")
        time.sleep(random.uniform(2.0, 4.0))
        session.get("https://www.gpw.pl/archiwum-notowan", headers=headers, timeout=20)

        # Krok 3: Pobieranie XLS
        print(f"Pobieranie danych GPW ({today_str})...")
        time.sleep(random.uniform(1.0, 3.0))
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        os.makedirs(SAVE_XLS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(SAVE_CSV), exist_ok=True)

        # Zapisz XLS dla historii
        temp_xls = os.path.join(SAVE_XLS_DIR, f"gpw_{today_str}.xls")
        with open(temp_xls, 'wb') as f:
            f.write(response.content)
        
        # Konwersja do CSV
        # Wymuszamy silnik lxml, który jest najbardziej odporny na błędy kodowania w HTML
        dfs = pd.read_html(io.BytesIO(response.content), flavor='lxml')
        
        if not dfs:
            print("BŁĄD: Serwer zwrócił pustą stronę (możliwa blokada bot-check).")
            return

        df = dfs[0]
        df.to_csv(SAVE_CSV, index=False, sep=';', encoding='utf-8')
        os.chmod(SAVE_CSV, 0o666)
        
        print(f"SUKCES: Dane zaktualizowane w {SAVE_CSV}")

    except Exception as e:
        print(f"WYSTĄPIŁ BŁĄD: {e}")
        # Jeśli to błąd połączenia, sugerujemy przerwę
        if "Connection reset" in str(e):
            print("Wskazówka: GPW zablokowało IP. Odczekaj 5-10 minut przed kolejną próbą.")
        sys.exit(1)

if __name__ == "__main__":
    download_gpw()
