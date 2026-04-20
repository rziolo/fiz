#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
from datetime import date
import os
import re

# Ścieżki dostosowane do rz-rpi-06
CSV_DIR = "/var/www/html/flask/inwestycje/etl/csv"
CSV_FILE = os.path.join(CSV_DIR, 'import_stooq.csv')

def scrape_stooq():
    # Używamy stabilnego linku XML
    url = "https://static.stooq.pl/aq/p/t_s_plws.xml?1756726022"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        content = response.text.strip()
        start_cdata = content.find('<![CDATA[')
        end_cdata = content.find(']]>')
        
        if start_cdata == -1 or end_cdata == -1:
            print("ERR Nie znaleziono CDATA.")
            return

        html_content = content[start_cdata + 9:end_cdata]
        soup = BeautifulSoup(html_content, 'html.parser')
        tbody = soup.find('tbody', id='f13')
        
        if not tbody:
            print("ERR Nie znaleziono tbody z id='f13'.")
            return

        rows = tbody.find_all('tr')
        data = {}

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2:
                continue

            label = cols[0].get_text(strip=True)

            if "Liczba walorów" in label:
                h_text = cols[1].get_text(strip=True)
                data['h_ilosc'] = int(re.sub(r'[^0-9]', '', h_text.split('(')[0]))
                l_text = cols[2].get_text(strip=True)
                data['l_ilosc'] = int(re.sub(r'[^0-9]', '', l_text.split('(')[0]))

            elif "Wolumen" in label:
                h_text = cols[1].get_text(strip=True)
                data['h_vol'] = int(re.sub(r'[^0-9]', '', h_text))
                l_text = cols[2].get_text(strip=True)
                data['l_vol'] = int(re.sub(r'[^0-9]', '', l_text))

            elif "Obrót" in label:
                if len(cols) < 4:
                    continue
                
                total_pln = 0
                # Sumowanie kolumn: Rosnące, Spadające, Bez zmian
                for i in range(1, 4):
                    col_text = cols[i].get_text()
                    pln_match = re.search(r'([\d\s\xa0]+)PLN', col_text)
                    if pln_match:
                        # Usuwamy spacje i twarde spacje \xa0
                        pln_value = int(re.sub(r'[^\d]', '', pln_match.group(1)))
                        total_pln += pln_value
                
                data['turnover'] = total_pln // 1000

        if not data:
            print("ERR Nie udało się wyciągnąć danych.")
            return

        today = date.today().strftime('%Y-%m-%d')
        os.makedirs(CSV_DIR, exist_ok=True)

        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['data', 'h_ilosc', 'h_vol', 'l_ilosc', 'l_vol', 'turnover'])
            writer.writerow([
                today,
                data.get('h_ilosc', 0),
                data.get('h_vol', 0),
                data.get('l_ilosc', 0),
                data.get('l_vol', 0),
                data.get('turnover', 0)
            ])

        print(f"✅ Dane zapisane do {CSV_FILE}")
        print(f"h_ilosc: {data['h_ilosc']}, turnover: {data['turnover']}")

    except Exception as e:
        print(f"ERR Błąd: {e}")

if __name__ == "__main__":
    scrape_stooq()
