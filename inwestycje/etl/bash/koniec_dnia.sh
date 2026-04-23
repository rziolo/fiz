#!/bin/bash

# --- KONFIGURACJA ---
BASE_PATH="/var/www/html/flask/inwestycje/etl/bash"
CSV_ARCH="/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"
LOG_FILE="/var/www/html/flask/inwestycje/etl/bash/koniec_dnia.log"

# Przekierowanie całego wyjścia (standardowe i błędy) do pliku logu
exec >> "$LOG_FILE" 2>&1

echo "---------------------------------------------------------------"
echo "START PROCESU: $(date)"
cd "$BASE_PATH" || { echo "BŁĄD: Nie można wejść do $BASE_PATH"; exit 1; }

# 10. Sprawdź czy nie minęła godz. 23:30 (zabezpieczenie startu)
CURRENT_TIME=$(date +%H%M)
if [ "$CURRENT_TIME" -ge "2330" ]; then
    echo "KONIEC: Jest po 23:30. Przerywam skrypt."
    exit 0
fi

# Pętla sprawdzająca dostępność archiwum (Kroki 20-40)
while true; do
    echo "Krok 20: Uruchamiam sprawdzanie archiwum (run_gpw_archiwum.sh)..."
    /bin/bash "$BASE_PATH/run_gpw_archiwum.sh"

    # 30. Czekaj 10 sekund na zapisanie pliku
    sleep 10

    # 40. Odczytaj status - używamy grep -qi (ignoruje wielkość liter i białe znaki)
    if grep -qi "ok" "$CSV_ARCH"; then
        echo "Krok 40: Status OK znaleziony w pliku. Przechodzę do sekwencji ETL."
        break
    else
        # Sprawdzenie godziny ponownie wewnątrz pętli
        if [ "$(date +%H%M)" -ge "2330" ]; then
            echo "KONIEC: Godzina 23:30 przekroczona podczas oczekiwania. Przerywam."
            exit 0
        fi
        echo "Krok 40: Status w pliku nie jest 'OK'. Czekam 10 minut... (Godzina: $(date +%H:%M))"
        sleep 600
    fi
done

# --- Sekwencja ETL (Kroki 50-150) ---

echo "Krok 50: Uruchamiam run_import_gpw.sh"
/bin/bash "$BASE_PATH/run_import_gpw.sh"
sleep 10

echo "Krok 70: Uruchamiam run_laduj.sh"
/bin/bash "$BASE_PATH/run_laduj.sh"
sleep 10

echo "Krok 90: Uruchamiam run_dane_dzienne.sh"
/bin/bash "$BASE_PATH/run_dane_dzienne.sh"
sleep 10

echo "Krok 110: Uruchamiam gpw_nowe.py"
# Upewnij się, że ścieżka do venv jest poprawna
$PYTHON_BIN "/var/www/html/flask/inwestycje/etl/python/gpw_nowe.py"
sleep 10

echo "Krok 130: Uruchamiam run_raport_statystyka.sh"
/bin/bash "$BASE_PATH/run_raport_statystyka.sh"
sleep 10

echo "Krok 150: Uruchamiam run_raport_akcje.sh"
/bin/bash "$BASE_PATH/run_raport_akcje.sh"

echo "SUKCES: Proces Koniec Dnia zakończony: $(date)"
echo "---------------------------------------------------------------"
