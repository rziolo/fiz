#!/bin/bash

# Konfiguracja ścieżek
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
PY_SCRIPTS_DIR="/var/www/html/flask/inwestycje/etl/python"
LOG_FILE="/var/www/html/flask/inwestycje/etl/python/etl.log"

echo "========================================" >> $LOG_FILE
echo "START ETL (NC, ZAGR, STOOQ): $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 1. GPW NewConnect
echo "[$(date '+%H:%M:%S')] Start: import_gpw_nc.py" >> $LOG_FILE
$PYTHON_BIN $PY_SCRIPTS_DIR/import_gpw_nc.py >> $LOG_FILE 2>&1
sleep 10

# 2. Statystyki Stooq
echo "[$(date '+%H:%M:%S')] Start: import_stooq.py" >> $LOG_FILE
$PYTHON_BIN $PY_SCRIPTS_DIR/import_stooq.py >> $LOG_FILE 2>&1
sleep 10

# 3. Notowania Zagraniczne
echo "[$(date '+%H:%M:%S')] Start: import_zagr.py" >> $LOG_FILE
$PYTHON_BIN $PY_SCRIPTS_DIR/import_zagr.py >> $LOG_FILE 2>&1

echo "========================================" >> $LOG_FILE
echo "KONIEC ETL: $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "" >> $LOG_FILE
