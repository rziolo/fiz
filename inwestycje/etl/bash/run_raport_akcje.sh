#!/bin/bash

# Ścieżki
BASE_DIR="/var/www/html/flask/inwestycje"
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
OUTPUT_CSV="/var/www/html/flask/inwestycje/etl/csv/raport_akcje.csv"

# Skrypt Python inline
$PYTHON_BIN -c "
import sys
import os
from dotenv import load_dotenv

sys.path.append('$BASE_DIR')
sys.path.append('/var/www/html/flask/shared')

load_dotenv(os.path.join('$BASE_DIR', '.env'))

from utils import get_stats, get_db_connection
from kursy_nbp import get_nbp_rates

def generate_report():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    nbp_rates = get_nbp_rates()
    stats = get_stats()

    query = \"\"\"
    WITH LastData AS (
        SELECT ticker, data, close, min, waluta,
               LAG(close, 1) OVER (PARTITION BY ticker ORDER BY data) as close_1,
               LAG(min, 2) OVER (PARTITION BY ticker ORDER BY data) as min_m2,
               LAG(min, 1) OVER (PARTITION BY ticker ORDER BY data) as min_m1,
               ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY data DESC) as rn
        FROM dane
    )
    SELECT
        o.ticker_nm, o.zakup_cena, o.zakup_ilosc as ilosc, o.stop_loss,
        d.close as kurs_biezacy, d.close_1, d.waluta,
        d.min_m2, d.min_m1, d.min as min_m0
    FROM obroty o
    JOIN LastData d ON o.ticker_nm = d.ticker AND d.rn = 1
    WHERE o.sprzedaz_data IS NULL
    \"\"\"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    logika_a_list = []
    logika_b_list = []

    for r in rows:
        kurs = float(r['kurs_biezacy'] or 0)
        zakup = float(r['zakup_cena'] or 0)
        ilosc = float(r['ilosc'] or 0)
        close_1 = float(r['close_1']) if r['close_1'] else None
        sl = float(r['stop_loss'] or 0)
        waluta = r['waluta']
        zysk = (kurs * ilosc) - zakup

        m_list = [float(r['min_m0'] or 0), float(r['min_m1'] or 0), float(r['min_m2'] or 0)]
        m_filtered = [v for v in m_list if v > 0]
        min_3d = min(m_filtered) if m_filtered else 0
        
        w1 = min_3d * 0.97
        w2 = (kurs * 0.95) if (close_1 and kurs / close_1 > 1.05) else 0
        sugestia_pln = max(w1, w2)

        # Logika A: Zysk > 300 i SL == 0
        if zysk > 300 and (sl == 0 or sl is None):
            val = sugestia_pln
            if waluta != 'PLN':
                val /= float(nbp_rates.get(waluta, 1))
            logika_a_list.append(f\"{r['ticker_nm']},{int(ilosc)},{waluta},{val:.2f}\")

        # Logika B: SL > 0 i sugestia > SL
        if sl > 0 and sugestia_pln > sl:
            val_b = sugestia_pln
            if waluta != 'PLN':
                val_b /= float(nbp_rates.get(waluta, 1))
            logika_b_list.append(f\"{r['ticker_nm']},{val_b:.2f}\")

    # Sortowanie alfabetyczne spółek dla czytelności
    logika_a_list.sort()
    logika_b_list.sort()

    with open('$OUTPUT_CSV', 'w', encoding='utf-8') as f:
        # Formatowanie ze spacją po dwukropku
        f.write(f\"wystaw: {';'.join(logika_a_list)}\\n\")
        f.write(f\"podnieś: {';'.join(logika_b_list)}\\n\")
        f.write(f\"nowe: {stats.get('gpw_nowe', '')}\\n\")

    db.close()

generate_report()
"
echo "Raport akcje zapisany w: $OUTPUT_CSV"
