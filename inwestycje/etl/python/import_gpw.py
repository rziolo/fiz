# -*- coding: utf-8 -*-
import os
import requests
from datetime import date, datetime
import pandas as pd
import logging
import traceback

# Konfiguracja ścieżek
BASE_DIR = "/var/www/html/flask/inwestycje"
CSV_DIR = os.path.join(BASE_DIR, 'etl/csv')
EXCEL_DIR = os.path.join(BASE_DIR, 'etl/excel')
FINAL_CSV = os.path.join(CSV_DIR, 'import_gpw.csv')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GPW_URL = "https://www.gpw.pl/archiwum-notowan-full?type=10&date={}&fetch=1"

def download_and_convert_gpw_data(target_date=None):
    try:
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
        
        date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        url_date = date_obj.strftime('%d-%m-%Y')
        url = GPW_URL.format(url_date)

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        if len(response.content) < 10000:
            logger.warning("Plik zbyt mały - prawdopodobnie brak sesji.")
            return False

        temp_excel = os.path.join(EXCEL_DIR, f"gpw_{target_date}.xls")
        with open(temp_excel, 'wb') as f:
            f.write(response.content)

        try:
            df = pd.read_excel(temp_excel)
        except:
            df = pd.read_html(temp_excel)[0]

        # Czyszczenie i formatowanie
        cols_to_drop = ['Liczba otwartych pozycji', 'Wartość otwartych pozycji', 'Cena nominalna']
        df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d')
        else:
            df.insert(0, 'Data', target_date)

        num_cols = ['Kurs otwarcia', 'Kurs max', 'Kurs min', 'Kurs zamknięcia', 'Zmiana', 'Obrót']
        for col in num_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                df[col] = df[col].map(lambda x: f"{x:.3f}")

        for col in ['Wolumen', 'Liczba Transakcji']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(' ', '').replace('nan', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        expected_cols = ['Data', 'Nazwa', 'ISIN', 'Waluta', 'Kurs otwarcia', 'Kurs max', 'Kurs min', 'Kurs zamknięcia', 'Zmiana', 'Wolumen', 'Liczba Transakcji', 'Obrót']
        for col in expected_cols:
            if col not in df.columns: df[col] = 0

        df[expected_cols].to_csv(FINAL_CSV, index=False, encoding='utf-8')
        logger.info(f"Sukces: {FINAL_CSV}")
        return True
    except Exception as e:
        logger.error(f"Błąd: {e}")
        return False

if __name__ == "__main__":
    download_and_convert_gpw_data()
