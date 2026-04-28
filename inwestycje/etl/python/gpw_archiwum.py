import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import time

# Konfiguracja
GPW_URL = "https://www.gpw.pl/archiwum-notowan-full?type=10&date={}"
CSV_PATH = "/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"

def check_gpw_data_for_today():
    # Format daty dla GPW to DD-MM-YYYY
    today_str = date.today().strftime("%d-%m-%Y")
    url = GPW_URL.format(today_str)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://www.gpw.pl/archiwum-notowan'
    }

    max_retries = 3
    result = "brak"

    for attempt in range(max_retries):
        try:
            print(f"Próba {attempt + 1} połączenia z GPW...")
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text()

            # Szukamy konkretnych spółek widocznych na Twoim zrzucie ekranu
            # Jeśli są na stronie, to znaczy że dane zostały załadowane poprawnie
            if any(ticker in page_text for ticker in ["11BIT", "KGHM", "PKO_BP", "06MAGNA"]):
                result = "OK"
                break
            else:
                print("Strona załadowana, ale nie znaleziono tickerów (pusta tabela).")
                result = "brak"
            
            # Jeśli doszliśmy tutaj bez błędu, ale z statusem "brak", nie ponawiamy
            break

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
            print(f"Błąd połączenia (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(10) # Czekamy 10 sekund przed kolejną próbą
            continue
        except Exception as e:
            print(f"Inny błąd: {e}")
            break

    # Zapis do CSV
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", encoding="utf-8") as f:
        f.write(result + "\n")

    print(f"Finałowy status dla {today_str}: {result}")

if __name__ == "__main__":
    check_gpw_data_for_today()
