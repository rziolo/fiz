#!/bin/bash
# Ścieżki
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
PY_SCRIPT="/var/www/html/flask/inwestycje/etl/python/gpw_archiwum.py"
LOG_FILE="/var/www/html/flask/inwestycje/etl/python/etl.log"

echo "--- Start GPW Archiwum Check: $(date) ---" >> $LOG_FILE
$PYTHON_BIN $PY_SCRIPT >> $LOG_FILE 2>&1
echo "--- Koniec: $(date) ---" >> $LOG_FILE
