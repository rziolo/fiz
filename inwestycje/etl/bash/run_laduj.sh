#!/bin/bash

# Ścieżka do katalogu głównego aplikacji
APP_DIR="/var/www/html/flask/inwestycje"
export PYTHONPATH="${PYTHONPATH}:${APP_DIR}"

# --- KLUCZOWE: Wczytanie zmiennych środowiskowych ---
# Jeśli masz plik .env, wyeksportuj go (pomijając komentarze)
if [ -f "$APP_DIR/.env" ]; then
    export $(grep -v '^#' $APP_DIR/.env | xargs)
fi

# Używamy ścieżki do Pythona z venv, jeśli go używasz
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="/usr/bin/python3"
fi

# Pobieranie dat z utils.py
DATA_IMPORT_GPW=$($PYTHON_BIN -c "import sys; sys.path.append('${APP_DIR}'); from utils import get_stats; print(get_stats()['data_import_gpw'])")
DATA_DANE=$($PYTHON_BIN -c "import sys; sys.path.append('${APP_DIR}'); from utils import get_stats; print(get_stats()['data_dane'])")

echo "Data w pliku CSV (GPW): $DATA_IMPORT_GPW"
echo "Data ostatnia w bazie:  $DATA_DANE"

# Sprawdzenie warunku (dodatkowe zabezpieczenie przed słowem "Błąd")
if [ "$DATA_IMPORT_GPW" == "$DATA_DANE" ] || [ "$DATA_DANE" == "Błąd" ]; then
    if [ "$DATA_DANE" == "Błąd" ]; then
        echo "⚠️ Wystąpił błąd połączenia z bazą. Sprawdź poświadczenia."
    else
        echo "✅ Daty są identyczne ($DATA_DANE). Baza jest aktualna. Przerywam."
    fi
    exit 0
else
    echo "🔄 Daty się różnią. Uruchamiam proces ładowania..."
    
    echo "1/3 Uruchamiam: load_dane.py"
    $PYTHON_BIN ${APP_DIR}/etl/python/load_dane.py
    
    echo "2/3 Czekanie 10 sekund..."
    sleep 10
    
    echo "3/3 Uruchamiam: gpw_nowe.py"
    $PYTHON_BIN ${APP_DIR}/etl/python/gpw_nowe.py
    
    echo "✨ Proces zakończony pomyślnie."
fi
