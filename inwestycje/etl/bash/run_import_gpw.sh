#!/bin/bash

# Ścieżki
APP_DIR="/var/www/html/flask/inwestycje"
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
EXCEL_DIR="$APP_DIR/etl/excel"

echo "--- Start Import GPW ($(date)) ---"

# 1. Uruchomienie skryptu Python
$PYTHON_BIN $APP_DIR/etl/python/import_gpw.py

# 2. Rotacja plików w folderze excel (zachowaj 5 najnowszych)
echo "Czyszczenie folderu excel: $EXCEL_DIR"
cd "$EXCEL_DIR" || exit

# Pobierz listę plików .xls, posortuj czasowo (-t), omiń pierwsze 5 (tail +6) i usuń resztę
ls -t *.xls 2>/dev/null | tail -n +6 | xargs -I {} rm -v {}

echo "--- Koniec procesu GPW ---"
