#!/usr/bin/env python3
import os, sys, csv, mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Wczytaj .env z folderu wyżej
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_last_month_range():
    today = datetime.now()
    first_day_current = today.replace(day=1)
    last_day_prev = first_day_current - timedelta(days=1)
    return last_day_prev.replace(day=1).date(), last_day_prev.date()

def main():
    start_date, end_date = get_last_month_range()
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor(dictionary=True)

        # 1. Przychody
        cursor.execute("SELECT SUM(ZUS_Iwona+ZUS_Robert+gielda+odsetki+urzad+inne) as total FROM przychody WHERE data BETWEEN %s AND %s", (start_date, end_date))
        przychody = cursor.fetchone()['total'] or 0.0

        # 2. Wydatki
        cursor.execute("SELECT SUM(zywnosc) as zywnosc, SUM(niezywnosc) as niezywnosc, SUM(car_cost) as car, SUM(oplaty) as oplaty, SUM(inne) as inne, SUM(medycyna) as medycyna FROM wydatki WHERE data BETWEEN %s AND %s", (start_date, end_date))
        w = cursor.fetchone()

        # 3. ROR (ostatni dzień miesiąca)
        cursor.execute("SELECT (PKO+mBank+Millenium) as banki, lokaty, gotowka, gielda, (EURO*EURO_kurs + USD*USD_kurs) as waluty FROM ror WHERE data = %s", (end_date,))
        r = cursor.fetchone() or {'banki':0, 'lokaty':0, 'gotowka':0, 'gielda':0, 'waluty':0}

        results = [
            ['fin_data', end_date],
            ['przychody', f"{przychody:.2f}"],
            ['banki', f"{r['banki']:.2f}"],
            ['lokaty', f"{r['lokaty']:.2f}"],
            ['gotowka', f"{r['gotowka']:.2f}"],
            ['gielda_ror', f"{r['gielda']:.2f}"],
            ['waluty', f"{r['waluty']:.2f}"],
            ['zywnosc', f"{w['zywnosc'] or 0:.2f}"],
            ['niezywnosc', f"{w['niezywnosc'] or 0:.2f}"],
            ['samochod', f"{w['car'] or 0:.2f}"],
            ['oplaty', f"{w['oplaty'] or 0:.2f}"],
            ['inne', f"{w['inne'] or 0:.2f}"],
            ['medycyna', f"{w['medycyna'] or 0:.2f}"]
        ]

        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv', 'finanse_miesiac.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(results)
        
        conn.close()
        print(f"Sukces: {csv_path}")
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    main()
