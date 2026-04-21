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

    # Bardzo szczegółowe nagłówki imitujące rzeczywistą sesję przeglądarki
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.gpw.pl/archiwum-notowan',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

    try:
        session = requests.Session()
        
        # 1. Najpierw "pukamy" do strony głównej, żeby zainicjować sesję i ciasteczka
        session.get("https://www.gpw.pl/", headers=headers, timeout=10)
        
        # 2. Pobieramy właściwe dane archiwalne
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()

        # Detekcja wyniku
        if "Brak danych dla wybranych kryteriów" in page_text:
            result = "brak"
        elif soup.find('table', {'class': 'table'}): # Szukamy konkretnie tabeli z klasą 'table'
            result = "OK"
        elif "Kod" in page_text and "Kurs" in page_text: # Fallback: jeśli są nagłówki tabeli
            result = "OK"
        else:
            result = "brak"

        # Zapis do CSV
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write(result + "\n")
        
        print(f"Status: {result} (Data: {today_str})")

    except Exception as e:
        print(f"Błąd podczas połączenia: {e}")
        # W razie błędu zapisujemy "brak", aby panel odświeżył status
        try:
            with open(CSV_PATH, "w", encoding="utf-8") as f:
                f.write("brak\n")
        except:
            pass

if __name__ == "__main__":
    check_gpw_data_for_today()
