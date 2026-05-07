import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import time

# Konfiguracja
GPW_URL = "https://www.gpw.pl/archiwum-notowan-full?type=10&date={}&fetch=1"
CSV_PATH = "/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"

def check_gpw_autonomously():
    today_str = date.today().strftime("%Y-%m-%d")
    url = GPW_URL.format(today_str)
    
    # Rozbudowane nagłówki, aby rpi-06 wyglądał inaczej niż wcześniej
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    result = "brak"
    session = requests.Session()

    try:
        # KROK 1: Najpierw wchodzimy na stronę główną, by pobrać ciasteczka sesyjne
        # To często "oszukuje" systemy anty-botowe
        session.get("https://www.gpw.pl/", headers=headers, timeout=10)
        time.sleep(1) # Chwila oddechu

        # KROK 2: Właściwe zapytanie o dane
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()

        if "Brak danych dla wybranych kryteriów." in page_text:
            result = "brak"
        elif "Kurs" in page_text or "Ticker" in page_text:
            result = "OK"
        else:
            result = "brak"

    except Exception as e:
        print(f"Autonomiczna próba nieudana: {e}")
        result = "brak"

    # Zapis wyniku
    try:
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write(result + "\n")
        print(f"Zapisano wynik na rz-rpi-06: {result}")
    except IOError as e:
        print(f"Błąd zapisu: {e}")

if __name__ == "__main__":
    check_gpw_autonomously()
