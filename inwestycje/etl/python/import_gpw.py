#!/usr/bin/env python3
import os
import pandas as pd
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_DIR = os.path.join(BASE_DIR, 'excel')
CSV_OUT = os.path.join(BASE_DIR, 'csv', 'import_gpw.csv')

def import_gpw():
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_gpw_format = datetime.now().strftime('%d-%m-%Y')
    local_file = os.path.join(EXCEL_DIR, f'gpw_{today_str}.xls')
    
    url = f"https://www.gpw.pl/archiwum-notowan?fetch=1&type=10&instrument=&date={today_gpw_format}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

    try:
        if not os.path.exists(local_file):
            print(f"--- Pobieranie danych z GPW...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            with open(local_file, 'wb') as f:
                f.write(response.content)
        else:
            print(f"--- Używam pliku lokalnego: {local_file}")

        try:
            df = pd.read_excel(local_file, engine='xlrd')
        except:
            with open(local_file, 'r', encoding='iso-8859-2') as f:
                df = pd.read_html(f.read(), decimal=',', thousands=' ')[0]

        # NAPRAWA KOLUMN: GPW czasem dodaje zbędną kolumnę na początku lub ma inną strukturę
        # Szukamy kolumny z ISIN, żeby wiedzieć gdzie są dane
        if 'ISIN' not in df.columns:
            df.columns = df.iloc[0] # Spróbuj ustawić pierwszy wiersz jako nagłówek
            df = df[1:]

        # Wybieramy tylko potrzebne dane i nadajemy im stałe nazwy
        cols_needed = ['Nazwa', 'ISIN', 'Waluta', 'Kurs otwarcia', 'Kurs max', 'Kurs min', 
                       'Kurs zamknięcia', 'Zmiana', 'Wolumen', 'Liczba Transakcji', 'Obrót']
        
        # Filtrujemy tylko te kolumny (ignorując ewentualną datę z pliku)
        df = df[cols_needed].copy()
        
        # Wstawiamy naszą czystą datę na początek
        df.insert(0, 'Data', today_str)

        df.to_csv(CSV_OUT, index=False, encoding='utf-8')
        print(f"✅ Sukces! Zaktualizowano: {CSV_OUT} ({len(df)} wierszy)")

    except Exception as e:
        print(f"❌ KRYTYCZNY BŁĄD: {e}")

if __name__ == "__main__":
    import_gpw()
