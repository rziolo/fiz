import os
import csv
import mysql.connector
from datetime import datetime

BASE_PATH = "/var/www/html/flask/inwestycje/"
CSV_PATH = os.path.join(BASE_PATH, "etl/csv/")
BASH_PATH = os.path.join(BASE_PATH, "etl/bash/")

SCRIPTS = {
    'etl_import': os.path.join(BASH_PATH, "run_import_nc_zagr_stooq.sh"),
    'gpw_check': os.path.join(BASH_PATH, "run_gpw_archiwum.sh")
}

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )

def read_csv_row(filepath, row_idx):
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
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT data FROM dane ORDER BY data DESC LIMIT 251")
        sesje = cursor.fetchall()

        if len(sesje) > 0:
            last_date = str(sesje[0]['data'])
            stats['data_dane'] = last_date
            if len(sesje) > 250:
                past_date = str(sesje[250]['data'])
                query_compare = """
                    SELECT
                        SUM(CASE WHEN d_now.close > d_past.close THEN 1 ELSE 0 END) as hl,
                        SUM(CASE WHEN d_now.close < d_past.close THEN 1 ELSE 0 END) as nl
                    FROM dane d_now
                    JOIN dane d_past ON d_now.ticker = d_past.ticker
                    WHERE d_now.data = %s AND d_past.data = %s
                """
                cursor.execute(query_compare, (last_date, past_date))
                res = cursor.fetchone()
                stats['hl'] = res['hl'] or 0
                stats['nl'] = res['nl'] or 0
            else:
                stats['hl'] = 0
                stats['nl'] = 0

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
        stats.update({'hl': 0, 'nl': 0, 'data_dane': 'Błąd', 'data_dane_dzienne': '', 'dane_dzienne_wartosc': 0, 'dane_dzienne_wklad': 0})

    # CSV STOOQ - mapowanie na konkretne pola
    row_stooq = read_csv_row(os.path.join(CSV_PATH, 'import_stooq.csv'), 1)
    if row_stooq:
        stats['csv_stat_h_ilosc'] = row_stooq[1]
        stats['csv_stat_h_vol'] = row_stooq[2]
        stats['csv_stat_l_ilosc'] = row_stooq[3]
        stats['csv_stat_l_vol'] = row_stooq[4]
        stats['csv_stat_turnover'] = row_stooq[5]
    else:
        for k in ['csv_stat_h_ilosc', 'csv_stat_h_vol', 'csv_stat_l_ilosc', 'csv_stat_l_vol', 'csv_stat_turnover']:
            stats[k] = 0

    stats['today'] = datetime.now().strftime('%Y-%m-%d')
    return stats
