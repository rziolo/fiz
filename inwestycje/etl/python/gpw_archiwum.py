import requests
from bs4 import BeautifulSoup
from datetime import date
import os

# Konfiguracja
GPW_URL = "https://www.gpw.pl/archiwum-notowan-full?type=10&date={}&fetch=1"
CSV_PATH = "/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"

def check_gpw_data_for_today():
    today_str = date.today().strftime("%Y-%m-%d")
    url = GPW_URL.format(today_str)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.gpw.pl/archiwum-notowan'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()

        # Prosta i skuteczna logika z rz-rpi-02:
        # Jeśli NIE ma napisu o braku danych, uznajemy że są OK
        if "Brak danych dla wybranych kryteriów." in page_text:
            result = "brak"
        else:
            result = "OK"

        # Zapis do CSV
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write(result + "\n")

        print(f"Status: {result} (Data: {today_str})")

    except Exception as e:
        print(f"Błąd podczas połączenia: {e}")
        # W razie błędu nie nadpisujemy pliku lub wpisujemy brak
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write("brak\n")

if __name__ == "__main__":
    check_gpw_data_for_today()
