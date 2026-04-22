#!/bin/bash

# Konfiguracja ścieżek
BASE_PATH="/var/www/html/flask/inwestycje/etl/bash"
CSV_ARCH="/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"

echo "Rozpoczynam proces Koniec Dnia: $(date)"

# 10. Sprawdź czy nie minęła godz. 23:30
CURRENT_TIME=$(date +%H%M)
if [ "$CURRENT_TIME" -ge "2330" ]; then
    echo "Jest po 23:30. Przerywam skrypt."
    exit 0
fi

# Pętla sprawdzająca dostępność archiwum (Kroki 20-40)
while true; do
    echo "Uruchamiam sprawdzanie archiwum..."
    /bin/bash "$BASE_PATH/run_gpw_archiwum.sh"
    
    # 30. Czekaj 10 sekund
    sleep 10
    
    # 40. Odczytaj status
    STATUS=$(cat "$CSV_ARCH" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')
    
    if [ "$STATUS" == "ok" ]; then
        echo "Dane archiwalne są gotowe. Przechodzę do importu."
        break
    else
        # Sprawdzenie godziny ponownie wewnątrz pętli
        if [ "$(date +%H%M)" -ge "2330" ]; then
            echo "Godzina 23:30 przekroczona podczas oczekiwania. Przerywam."
            exit 0
        fi
        echo "Status: $STATUS. Dane jeszcze niegotowe. Czekam 10 minut..."
        sleep 600
    fi
done

# --- Sekwencja ETL (Kroki 50-150) ---

echo "50. Uruchamiam run_import_gpw.sh"
/bin/bash "$BASE_PATH/run_import_gpw.sh"
sleep 10

echo "70. Uruchamiam run_laduj.sh"
/bin/bash "$BASE_PATH/run_laduj.sh"
sleep 10

echo "90. Uruchamiam run_dane_dzienne.sh"
/bin/bash "$BASE_PATH/run_dane_dzienne.sh"
sleep 10

echo "110. Uruchamiam gpw_nowe.py"
$PYTHON_BIN "/var/www/html/flask/inwestycje/etl/python/gpw_nowe.py"
sleep 10

echo "130. Uruchamiam run_raport_statystyka.sh"
/bin/bash "$BASE_PATH/run_raport_statystyka.sh"
sleep 10

echo "150. Uruchamiam run_raport_akcje.sh"
/bin/bash "$BASE_PATH/run_raport_akcje.sh"

echo "Proces Koniec Dnia zakończony pomyślnie: $(date)"
