import os
import csv
import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )

def read_csv_date(filepath, row_idx, col_idx):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            return reader[row_idx][col_idx]
    except:
        return "Brak pliku"

def get_stats():
    stats = {}
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. MAX dane.data
    cursor.execute("SELECT MAX(data) as d FROM dane")
    stats['data_dane'] = str(cursor.fetchone()['d'] or "")
    
    # 2. MAX dane_dzienne.data
    cursor.execute("SELECT MAX(data) as d FROM dane_dzienne")
    stats['data_dane_dzienne'] = str(cursor.fetchone()['d'] or "")

    # 3. ticker_ilosc (aktywne spółki)
    cursor.execute("SELECT COUNT(DISTINCT ticker_nm) as c FROM obroty WHERE sprzedaz_data IS NULL")
    stats['ticker_ilosc'] = cursor.fetchone()['c']

    # 4. dane_dzienne_wartosc (Suma close * ilosc)
    cursor.execute("""
        SELECT SUM(d.close * o.zakup_ilosc) as wycena 
        FROM obroty o 
        JOIN dane d ON o.ticker_nm = d.ticker 
        WHERE o.sprzedaz_data IS NULL AND d.data = (SELECT MAX(data) FROM dane)
    """)
    stats['dane_dzienne_wartosc'] = cursor.fetchone()['wycena'] or 0

    # 5. dane_dzienne_wklad (suma narastająca: sprzedaz - zakup)
    cursor.execute("SELECT SUM(COALESCE(sprzedaz_cena, 0) - zakup_cena) as wklad FROM obroty")
    stats['dane_dzienne_wklad'] = cursor.fetchone()['wklad'] or 0

    db.close()

    # 6. CSV Imports
    path = "/var/www/html/flask/inwestycje/etl/csv/"
    stats['data_import_gpw'] = read_csv_date(path + 'import_gpw.csv', 1, 0)
    stats['data_import_gpw_nc'] = read_csv_date(path + 'import_gpw_nc.csv', 0, 0)
    stats['data_import_zagr'] = read_csv_date(path + 'import_zagr.csv', 0, 0)
    stats['data_import_stooq'] = read_csv_date(path + 'import_stooq.csv', 1, 0)
    
    # 7. gpw_nowe
    try:
        with open(path + 'gpw_nowe.csv', 'r') as f:
            stats['gpw_nowe'] = f.read().strip()
    except:
        stats['gpw_nowe'] = 'brak'

    # 8. Status Archiwum
    stats['gpw_archiwum_ok'] = os.path.exists(path + 'gpw_archiwum.csv')
    
    stats['today'] = datetime.now().strftime('%Y-%m-%d')
    return stats
