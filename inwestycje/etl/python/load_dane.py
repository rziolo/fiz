#!/usr/bin/env python3
import os
import sys
import csv
import logging
import pymysql
from dotenv import load_dotenv

# Konfiguracja ścieżek
BASE_DIR = "/var/www/html/flask/inwestycje"
CSV_DIR = os.path.join(BASE_DIR, "etl", "csv")
load_dotenv(os.path.join(BASE_DIR, '.env'))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4'
    )

def main():
    logger.info("🏁 Start ETL Load (PyMySQL Mode)")
    
    files = [
        (os.path.join(CSV_DIR, 'import_gpw.csv'), True),
        (os.path.join(CSV_DIR, 'import_gpw_nc.csv'), False),
        (os.path.join(CSV_DIR, 'import_zagr.csv'), False)
    ]

    all_rows = []
    for filepath, skip in files:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    start = 1 if skip else 0
                    valid = [r for r in rows[start:] if r and len(r) >= 12]
                    all_rows.extend(valid)
                    logger.info(f"✅ Pobrano {len(valid)} wierszy z {os.path.basename(filepath)}")
            except Exception as e:
                logger.error(f"❌ Błąd odczytu pliku {filepath}: {e}")

    if not all_rows:
        logger.error("❌ Brak danych do załadowania.")
        return

    try:
        db = get_db_connection()
        cur = db.cursor()

        cur.execute("SELECT COALESCE(MAX(id_dane), 0) FROM dane")
        next_id = int(cur.fetchone()[0]) + 1

        dates = list(set(row[1] for row in all_rows))
        format_strings = ','.join(['%s'] * len(dates))
        cur.execute(f"SELECT DISTINCT data FROM dane WHERE data IN ({format_strings})", dates)
        existing_dates = {str(r[0]) for r in cur.fetchall()}

        if existing_dates:
            logger.warning(f"⚠️ Dane dla dat {existing_dates} już są w bazie. Przerywam.")
            return

        final_data = []
        for i, row in enumerate(all_rows):
            final_data.append([next_id + i] + row[:12])

        query = """INSERT INTO dane (id_dane, data, ticker, ISIN, waluta, `open`, `max`, `min`, `close`, zmiana, volume, number_transactions, turnover) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.executemany(query, final_data)
        db.commit()
        logger.info(f"🚀 Sukces! Załadowano {len(final_data)} rekordów.")
        
    except Exception as e:
        logger.error(f"❌ Błąd bazy: {e}")
    finally:
        if 'db' in locals(): db.close()

if __name__ == "__main__":
    main()
