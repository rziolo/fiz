from flask import Blueprint, render_template, request, redirect, url_for
import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Załadowanie zmiennych środowiskowych z pliku .env
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(basedir, '.env'))

shared_path = '/var/www/html/flask/shared'
if shared_path not in sys.path:
    sys.path.append(shared_path)

try:
    from kursy_nbp import get_nbp_rates
except ImportError:
    def get_nbp_rates(): return {}

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
sprzedaj_bp = Blueprint('sprzedaj', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), 
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), 
        database=os.getenv('DB_NAME'), ssl_disabled=True
    )

@sprzedaj_bp.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    nbp_rates = get_nbp_rates()

    # Zoptymalizowane zapytanie: usunięto podzapytania SELECT na rzecz funkcji okienkowych LAG
    query = """
    WITH LastData AS (
        SELECT ticker, data, close, min, waluta,
               LAG(close, 1) OVER (PARTITION BY ticker ORDER BY data) as close_1,
               LAG(min, 2) OVER (PARTITION BY ticker ORDER BY data) as min_m2,
               LAG(min, 1) OVER (PARTITION BY ticker ORDER BY data) as min_m1,
               LAG(data, 1) OVER (PARTITION BY ticker ORDER BY data) as data_m1,
               LAG(data, 2) OVER (PARTITION BY ticker ORDER BY data) as data_m2,
               ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY data DESC) as rn
        FROM dane
    )
    SELECT 
        o.id_obroty, o.ticker_nm, o.platforma as rynek, o.zakup_cena, o.zakup_ilosc as ilosc, o.stop_loss,
        d.close as kurs_biezacy, d.close_1, d.waluta, d.data as data_max,
        d.min_m2, d.min_m1, d.min as min_m0,
        d.data_m1, d.data_m2
    FROM obroty o
    JOIN LastData d ON o.ticker_nm = d.ticker AND d.rn = 1
    WHERE o.sprzedaz_data IS NULL
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    for r in rows:
        kurs = float(r['kurs_biezacy'] or 0)
        zakup = float(r['zakup_cena'] or 0)
        ilosc = float(r['ilosc'] or 0)
        close_1 = float(r['close_1']) if r['close_1'] else None
        sl = float(r['stop_loss'] or 0)

        r['zysk'] = (kurs * ilosc) - zakup

        m_list = [float(r['min_m0'] or 0), float(r['min_m1'] or 0), float(r['min_m2'] or 0)]
        m_filtered = [v for v in m_list if v > 0]
        min_3d = min(m_filtered) if m_filtered else 0
        r['min_3d_val'] = min_3d

        w1 = min_3d * 0.97
        w2 = (kurs * 0.95) if (close_1 and kurs / close_1 > 1.05) else 0
        sugestia = max(w1, w2)

        r['kurs_waluty_nbp'] = float(nbp_rates.get(r['waluta'], 1))

        if r['zysk'] > 300 or sl > 0:
            r['sugestia_sprzedaz'] = sugestia
        else:
            r['sugestia_sprzedaz'] = None

        r['podnies_txt'] = "TAK" if (sl > 0 and r['sugestia_sprzedaz'] and r['sugestia_sprzedaz'] > sl) else ""

    rows.sort(key=lambda x: x['zysk'], reverse=True)
    db.close()
    return render_template('sprzedaj.html', data=rows, rates=nbp_rates)

@sprzedaj_bp.route('/update_sl', methods=['POST'])
def update_sl():
    id_obroty = request.form.get('id_obroty')
    sl_value = request.form.get('stop_loss') or 0
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE obroty SET stop_loss = %s WHERE id_obroty = %s", (sl_value, id_obroty))
    db.commit()
    db.close()
    return redirect(url_for('sprzedaj.index'))
