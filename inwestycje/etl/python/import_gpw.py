#!/usr/bin/env python3
import os
import pandas as pd
import requests
from datetime import datetime

# Ścieżki
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_DIR = os.path.join(BASE_DIR, 'excel')
CSV_OUT = os.path.join(BASE_DIR, 'csv', 'import_gpw.csv')

def import_gpw():
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_gpw_format = datetime.now().strftime('%d-%m-%Y')
    local_file = os.path.join(EXCEL_DIR, f'gpw_{today_str}.xls')
    
    url = f"https://www.gpw.pl/archiwum-notowan?fetch=1&type=10&instrument=&date={today_gpw_format}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        if not os.path.exists(local_file):
            print(f"--- Pobieranie danych z GPW...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            with open(local_file, 'wb') as f:
                f.write(response.content)
        else:
            print(f"--- Używam pliku lokalnego: {local_file}")

        # PRÓBA 1: Czytanie jako prawdziwy binarnego Excela (.xls)
        try:
            df = pd.read_excel(local_file, engine='xlrd')
            print("--- Zinterpretowano jako plik binarny Excel.")
        except:
            # PRÓBA 2: Czytanie jako HTML (stary format GPW)
            print("--- To nie jest plik binarny, próbuję format HTML...")
            with open(local_file, 'r', encoding='iso-8859-2') as f:
                content = f.read()
            tables = pd.read_html(content, decimal=',', thousands=' ')
            df = tables[0]

        # Standaryzacja kolumn (GPW ma ich 11)
        if len(df.columns) >= 11:
            df = df.iloc[:, :11] # bierzemy pierwsze 11 kolumn
            df.columns = [
                'Nazwa', 'ISIN', 'Waluta', 'Kurs otwarcia', 'Kurs max', 'Kurs min', 
                'Kurs zamknięcia', 'Zmiana', 'Wolumen', 'Liczba Transakcji', 'Obrót'
            ]
        
        df.insert(0, 'Data', today_str)
        df.to_csv(CSV_OUT, index=False, encoding='utf-8')
        print(f"✅ Sukces! Zaktualizowano: {CSV_OUT} ({len(df)} wierszy)")

    except Exception as e:
        print(f"❌ KRYTYCZNY BŁĄD: {e}")

if __name__ == "__main__":
    import_gpw()
