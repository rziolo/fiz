#!/bin/bash

# Ścieżki
BASE_DIR="/var/www/html/flask/inwestycje"
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
OUTPUT_CSV="/var/www/html/flask/inwestycje/etl/csv/raport_statystyka.csv"

# Skrypt Python inline z ładowaniem zmiennych i funkcją abs()
$PYTHON_BIN -c "
import sys
import os
from dotenv import load_dotenv

# Dodaj katalog główny do ścieżki i załaduj .env
sys.path.append('$BASE_DIR')
load_dotenv(os.path.join('$BASE_DIR', '.env'))

from utils import get_stats

s = get_stats()

def fmt_pln(val):
    try:
        # abs() usuwa znak minus
        return f'{abs(float(val)):,.2f}'.replace(',', ' ').replace('.', ',') + ' PLN'
    except:
        return '0,00 PLN'

lines = [
    f'data_dane:{s.get(\"data_dane\", \"\")}',
    f'data_dane_dzienne:{s.get(\"data_dane_dzienne\", \"\")}',
    f'ticker_ilosc:{int(s.get(\"ticker_ilosc\", 0))}',
    f'dane_dzienne_wartosc:{fmt_pln(s.get(\"dane_dzienne_wartosc\", 0))}',
    f'dane_dzienne_wklad:{fmt_pln(s.get(\"dane_dzienne_wklad\", 0))}',
    f'HL:{int(s.get(\"hl\", 0))}',
    f'NL:{int(s.get(\"nl\", 0))}',
    f'h_ilosc:{int(s.get(\"csv_stat_h_ilosc\", 0))}',
    f'h_vol:{int(s.get(\"csv_stat_h_vol\", 0))}',
    f'l_ilosc:{int(s.get(\"csv_stat_l_ilosc\", 0))}',
    f'l_vol:{int(s.get(\"csv_stat_l_vol\", 0))}',
    f'turnover:{int(s.get(\"csv_stat_turnover\", 0))}'
]

with open('$OUTPUT_CSV', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
"

echo "Raport zapisany w: $OUTPUT_CSV"
