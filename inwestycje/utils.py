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

def read_csv_row(filepath, row_idx):
    """Zwraca cały wiersz z pliku CSV jako listę."""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            if len(reader) > row_idx:
                return reader[row_idx]
    except Exception as e:
        print(f"Błąd odczytu {filepath}: {e}")
    return None

def get_stats():
    stats = {}

    # --- Dane z Bazy SQL ---
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT MAX(data) as d FROM dane")
        stats['data_dane'] = str(cursor.fetchone()['d'] or "")

        cursor.execute("SELECT MAX(data) as d FROM dane_dzienne")
        stats['data_dane_dzienne'] = str(cursor.fetchone()['d'] or "")

        cursor.execute("SELECT COUNT(DISTINCT ticker_nm) as c FROM obroty WHERE sprzedaz_data IS NULL")
        stats['ticker_ilosc'] = cursor.fetchone()['c']

        cursor.execute("""
            SELECT SUM(d.close * o.zakup_ilosc) as wycena
            FROM obroty o
            JOIN dane d ON o.ticker_nm = d.ticker
            WHERE o.sprzedaz_data IS NULL AND d.data = (SELECT MAX(data) FROM dane)
        """)
        stats['dane_dzienne_wartosc'] = cursor.fetchone()['wycena'] or 0

        cursor.execute("SELECT SUM(COALESCE(sprzedaz_cena, 0) - zakup_cena) as wklad FROM obroty")
        stats['dane_dzienne_wklad'] = cursor.fetchone()['wklad'] or 0
        db.close()
    except Exception as e:
        print(f"Błąd bazy danych: {e}")
        stats.update({'data_dane': 'Błąd', 'data_dane_dzienne': 'Błąd', 'ticker_ilosc': 0, 'dane_dzienne_wartosc': 0, 'dane_dzienne_wklad': 0})

    # --- Dane z Plików CSV ---
    path = "/var/www/html/flask/inwestycje/etl/csv/"

    # GPW
    row_gpw = read_csv_row(path + 'import_gpw.csv', 1)
    stats['data_import_gpw'] = row_gpw[0] if row_gpw else "Brak"

    # NC
    row_nc = read_csv_row(path + 'import_gpw_nc.csv', 0)
    stats['data_import_gpw_nc'] = row_nc[0] if row_nc else "Brak"
    stats['csv_nc_data'] = stats['data_import_gpw_nc']

    # ZAGR
    row_zagr = read_csv_row(path + 'import_zagr.csv', 0)
    stats['data_import_zagr'] = row_zagr[0] if row_zagr else "Brak"
    stats['csv_zagr_data'] = stats['data_import_zagr']

    # STOOQ
    row_stooq = read_csv_row(path + 'import_stooq.csv', 1)
    if row_stooq:
        stats['data_import_stooq'] = row_stooq[0]
        stats['csv_stat_data'] = row_stooq[0]
        stats['csv_stat_h_ilosc'] = row_stooq[1]
        stats['csv_stat_h_vol'] = row_stooq[2]
        stats['csv_stat_l_ilosc'] = row_stooq[3]
        stats['csv_stat_l_vol'] = row_stooq[4]
        stats['csv_stat_turnover'] = row_stooq[5]
    else:
        for k in ['data_import_stooq', 'csv_stat_data', 'csv_stat_h_ilosc', 'csv_stat_h_vol', 'csv_stat_l_ilosc', 'csv_stat_l_vol', 'csv_stat_turnover']:
            stats[k] = "n/a"

    # Statusy dodatkowe
    try:
        with open(path + 'gpw_nowe.csv', 'r') as f:
            stats['gpw_nowe'] = f.read().strip() or 'brak'
    except:
        stats['gpw_nowe'] = 'brak'

    # Nowa logika sprawdzania zawartości pliku gpw_archiwum.csv
    try:
        with open(path + 'gpw_archiwum.csv', 'r') as f:
            content = f.read().strip().lower()
            stats['gpw_archiwum_status'] = "OK" if content == "ok" else "BRAK"
            stats['gpw_archiwum_ok'] = (content == "ok")
    except:
        stats['gpw_archiwum_status'] = "BRAK"
        stats['gpw_archiwum_ok'] = False

    stats['today'] = datetime.now().strftime('%Y-%m-%d')

    return stats
