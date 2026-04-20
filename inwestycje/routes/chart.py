from flask import Blueprint, render_template, request
import os
import mysql.connector
from datetime import datetime, timedelta

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
chart_bp = Blueprint('chart', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

@chart_bp.route('/')
def index():
    selected_ticker = request.args.get('ticker')
    months = request.args.get('months', 'all')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Filtrowanie okresu dla Bilansu Ogólnego
    date_limit_sql = ""
    if months != 'all':
        limit_date = (datetime.now() - timedelta(days=int(months)*30)).strftime('%Y-%m-%d')
        date_limit_sql = f"WHERE data >= '{limit_date}'"

    # 1. Dane do Bilansu Ogólnego
    cursor.execute(f"SELECT data, wartosc, wklad FROM dane_dzienne {date_limit_sql} ORDER BY data ASC")
    daily_rows = cursor.fetchall()

    # 2. Lista tickerów
    cursor.execute("SELECT DISTINCT ticker_nm FROM obroty ORDER BY ticker_nm ASC")
    tickers = [row['ticker_nm'] for row in cursor.fetchall()]

    # 3. Dane dla konkretnej spółki
    ticker_data = []
    total_result = 0
    if selected_ticker:
        # Pobieramy ceny jednostkowe (zakup_cena i sprzedaz_cena)
        cursor.execute("""
            SELECT ticker_nm, data, typ, wartosc FROM (
                SELECT ticker_nm, zakup_data as data, 'kupno' as typ, zakup_cena as wartosc 
                FROM obroty WHERE ticker_nm = %s
                UNION ALL
                SELECT ticker_nm, sprzedaz_data as data, 'sprzedaż' as typ, sprzedaz_cena as wartosc 
                FROM obroty WHERE ticker_nm = %s AND sprzedaz_data IS NOT NULL
            ) as subquery 
            ORDER BY data DESC
        """, (selected_ticker, selected_ticker))
        ticker_data = cursor.fetchall()

        # Wynik pozostaje jako suma zysku (Wartość końcowa - Wkład)
        cursor.execute("""
            SELECT SUM((IFNULL(sprzedaz_cena, kurs_biezacy) - zakup_cena) * zakup_ilosc) as wynik
            FROM obroty WHERE ticker_nm = %s
        """, (selected_ticker,))
        res = cursor.fetchone()
        total_result = res['wynik'] if res and res['wynik'] else 0

    db.close()

    return render_template('chart.html', 
                         labels_all=[str(r['data']) for r in daily_rows], 
                         vals_wartosc=[float(r['wartosc']) for r in daily_rows], 
                         vals_wklad=[float(r['wklad']) for r in daily_rows], 
                         vals_zysk=[float(r['wartosc'] - r['wklad']) for r in daily_rows],
                         tickers=tickers,
                         selected_ticker=selected_ticker,
                         ticker_data=ticker_data,
                         total_result=total_result,
                         current_months=months)
