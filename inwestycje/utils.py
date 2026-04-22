import os
import csv
import mysql.connector
from datetime import datetime

# --- Konfiguracja Ścieżek ---
BASE_PATH = "/var/www/html/flask/inwestycje/"
CSV_PATH = os.path.join(BASE_PATH, "etl/csv/")
BASH_PATH = os.path.join(BASE_PATH, "etl/bash/")

SCRIPTS = {
    'etl_import': os.path.join(BASH_PATH, "run_import_nc_zagr_stooq.sh"),
    'etl_load': os.path.join(BASH_PATH, "run_laduj.sh"),
    'gpw_check': os.path.join(BASH_PATH, "run_gpw_archiwum.sh"),
    'etl_gpw': os.path.join(BASH_PATH, "run_import_gpw.sh")
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
    stats['today'] = datetime.now().strftime('%Y-%m-%d')

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # 1. Ostatnia data sesji w bazie
        cursor.execute("SELECT MAX(data) as d FROM dane")
        last_date = cursor.fetchone()['d']
        stats['data_dane'] = str(last_date) if last_date else "Brak"

        # 2. Ilość spółek (aktywne)
        cursor.execute("SELECT COUNT(DISTINCT ticker_nm) as c FROM obroty WHERE sprzedaz_data IS NULL")
        stats['ticker_ilosc'] = cursor.fetchone()['c']

        # 3. WARTOŚĆ (Aktualna wycena portfela)
        query_wartosc = """
            SELECT SUM(latest_prices.close * o.zakup_ilosc) as wycena
            FROM obroty o
            JOIN (
                SELECT ticker, close FROM dane
                WHERE (ticker, data) IN (SELECT ticker, MAX(data) FROM dane GROUP BY ticker)
            ) as latest_prices ON o.ticker_nm = latest_prices.ticker
            WHERE o.sprzedaz_data IS NULL
        """
        cursor.execute(query_wartosc)
        stats['dane_dzienne_wartosc'] = cursor.fetchone()['wycena'] or 0

        # 4. WKŁAD
        cursor.execute("SELECT SUM(COALESCE(sprzedaz_cena, 0) - zakup_cena) as wklad FROM obroty")
        stats['dane_dzienne_wklad'] = cursor.fetchone()['wklad'] or 0

        # 5. Ostatnia data w dane_dzienne
        cursor.execute("SELECT MAX(data) as d FROM dane_dzienne")
        res_dd = cursor.fetchone()
        stats['data_dane_dzienne'] = str(res_dd['d']) if res_dd['d'] else "Brak"

        # 6. Wyliczanie HL i NL (250 sesji wstecz)
        cursor.execute("SELECT DISTINCT data FROM dane ORDER BY data DESC LIMIT 1 OFFSET 250")
        offset_row = cursor.fetchone()

        if offset_row and last_date:
            past_date = offset_row['data']
            query_hlnl = """
                SELECT
                    SUM(CASE WHEN d_now.close > d_past.close THEN 1 ELSE 0 END) as hl,
                    SUM(CASE WHEN d_now.close < d_past.close THEN 1 ELSE 0 END) as nl
                FROM (SELECT ticker, close FROM dane WHERE data = %s) d_now
                JOIN (SELECT ticker, close FROM dane WHERE data = %s) d_past
                  ON d_now.ticker = d_past.ticker
            """
            cursor.execute(query_hlnl, (last_date, past_date))
            res_hlnl = cursor.fetchone()
            stats['hl'] = res_hlnl['hl'] or 0
            stats['nl'] = res_hlnl['nl'] or 0
        else:
            stats['hl'], stats['nl'] = 0, 0

        db.close()
    except Exception as e:
        print(f"Błąd bazy danych: {e}")
        stats.update({'hl': 0, 'nl': 0, 'data_dane_dzienne': 'Błąd'})

    # --- Dane z plików CSV ---
    row_stooq = read_csv_row(os.path.join(CSV_PATH, 'import_stooq.csv'), 1)
    def get_val(row, idx, default=0):
        return row[idx] if row and len(row) > idx else default

    if row_stooq:
        stats['csv_stat_data'] = get_val(row_stooq, 0, "Brak")
        stats['csv_stat_h_ilosc'] = get_val(row_stooq, 1, 0)
        stats['csv_stat_h_vol'] = get_val(row_stooq, 2, 0)
        stats['csv_stat_l_ilosc'] = get_val(row_stooq, 3, 0)
        stats['csv_stat_l_vol'] = get_val(row_stooq, 4, 0)
        stats['csv_stat_turnover'] = get_val(row_stooq, 5, 0)

    # Dane pomocnicze dla widoku
    row_gpw = read_csv_row(os.path.join(CSV_PATH, 'import_gpw.csv'), 1)
    stats['data_import_gpw'] = row_gpw[0] if row_gpw else "Brak"
    row_nc = read_csv_row(os.path.join(CSV_PATH, 'import_gpw_nc.csv'), 0)
    stats['csv_nc_data'] = row_nc[0] if row_nc else "Brak"
    row_zagr = read_csv_row(os.path.join(CSV_PATH, 'import_zagr.csv'), 0)
    stats['csv_zagr_data'] = row_zagr[0] if row_zagr else "Brak"

    # Nowe spółki i archiwum
    try:
        with open(os.path.join(CSV_PATH, 'gpw_nowe.csv'), 'r') as f:
            stats['gpw_nowe'] = f.read().strip() or 'brak'
        path_arch = os.path.join(CSV_PATH, 'gpw_archiwum.csv')
        if os.path.exists(path_arch):
            with open(path_arch, 'r') as f:
                content = f.read().strip().lower()
                stats['gpw_archiwum_status'] = "OK" if content == "ok" else "BRAK"
                stats['gpw_archiwum_ok'] = (content == "ok")
    except:
        stats['gpw_nowe'] = 'brak'

    return stats
