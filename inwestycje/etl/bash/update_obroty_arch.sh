#!/bin/bash

# Uruchomienie skryptu Python przy użyciu dedykowanego środowiska venv
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
SCRIPT_PATH="/var/www/html/flask/inwestycje/etl/python/update_obroty_arch.py"

$PYTHON_BIN "$SCRIPT_PATH"
