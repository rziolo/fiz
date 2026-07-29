#!/bin/bash

# Załadowanie zmiennych środowiskowych bazy danych
export $(grep -v '^#' /var/www/html/flask/inwestycje/.env | xargs)

# Pobranie danych z utils.py
DATA_VALUES=$(/var/www/html/flask/venv/bin/python3 - <<'END_PY'
import sys
import os
sys.path.append('/var/www/html/flask/inwestycje')
from utils import get_stats

s = get_stats()
# Przygotowujemy tylko wartości liczbowe
print(f"{s['dane_dzienne_wartosc']}, {s['dane_dzienne_wklad']}, {s['csv_stat_h_ilosc']}, {s['csv_stat_h_vol']}, {s['csv_stat_l_ilosc']}, {s['csv_stat_l_vol']}, {s['csv_stat_turnover']}, {s['hl']}, {s['nl']}")
END_PY
)

# Sprawdzenie czy udało się pobrać dane
if [ -z "$DATA_VALUES" ]; then
    echo "Błąd: Nie udało się pobrać danych z utils.py"
    exit 1
fi

# Wykonanie zapytania do bazy danych - używamy --skip-ssl dla starszych wersji mysql/mariadb
mysql --skip-ssl -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
INSERT INTO dane_dzienne (data, wartosc, wklad, H_ilosc, H_vol, L_ilosc, L_vol, turnover, HL, NL)
VALUES (CURDATE(), $DATA_VALUES);"

if [ $? -eq 0 ]; then
    echo "Sukces: Dane dzienne z datą dzisiejszą zostały dodane do bazy."
else
    echo "Błąd podczas zapisu do bazy danych."
    exit 1
fi
