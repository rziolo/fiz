#!/bin/bash

# --- KONFIGURACJA ---
BASE_PATH="/var/www/html/flask/inwestycje/etl/bash"
CSV_ARCH="/var/www/html/flask/inwestycje/etl/csv/gpw_archiwum.csv"
CSV_GPW="/var/www/html/flask/inwestycje/etl/csv/import_gpw.csv"
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

    # 30. Czekaj 10 minut na zapisanie pliku (zmiana z 10s na 600s)
    echo "Krok 30: Czekam 10 minut na przetworzenie archiwum..."
    sleep 600

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
        echo "Krok 40: Status w pliku nie jest 'OK'. Czekam 10 sekund... (Godzina: $(date +%H:%M))"
        sleep 10
    fi
done

# --- Sekwencja ETL (Kroki 50-150) ---

:krok50
echo "Krok 50: Uruchamiam run_import_gpw.sh"
/bin/bash "$BASE_PATH/run_import_gpw.sh"

# Krok 55: Bufor na błędy zapisu
sleep 10

# Krok 60: Sprawdzenie daty w import_gpw.csv (Wiersz 2, Kolumna 1)
TODAY=$(date +%Y-%m-%d)
if [ -f "$CSV_GPW" ]; then
    # Wyciąga pierwsze pole z drugiego wiersza
    DATA_IMPORT_GPW=$(awk -F',' 'NR==2 {print $1}' "$CSV_GPW")
    echo "Krok 60: Sprawdzam datę importu: $DATA_IMPORT_GPW (Dzisiaj: $TODAY)"
    
    if [ "$DATA_IMPORT_GPW" == "$TODAY" ]; then
        echo "Krok 60: Data poprawna. Idę do kroku 70."
    else
        echo "Krok 60: Data nie zgadza się. Czekam 10 minut i ponawiam Krok 50..."
        sleep 600
        # Powrót do etykiety krok50 (używając pętli logicznej lub bezpośrednio wywołując sekwencję)
        # W bashu najbezpieczniej powtórzyć logikę przez restart/skok:
        exec /bin/bash "$0" # Restartuje skrypt od początku lub można użyć pętli while
    fi
else
    echo "BŁĄD: Plik $CSV_GPW nie istnieje. Czekam 10 minut..."
    sleep 600
    exec /bin/bash "$0"
fi

echo "Krok 70: Uruchamiam run_laduj.sh"
/bin/bash "$BASE_PATH/run_laduj.sh"
sleep 10

echo "Krok 90: Uruchamiam run_dane_dzienne.sh"
/bin/bash "$BASE_PATH/run_dane_dzienne.sh"
sleep 10

echo "Krok 110: Uruchamiam gpw_nowe.py"
$PYTHON_BIN "/var/www/html/flask/inwestycje/etl/python/gpw_nowe.py"
sleep 10

echo "Krok 130: Uruchamiam run_raport_statystyka.sh"
/bin/bash "$BASE_PATH/run_raport_statystyka.sh"
sleep 10

echo "Krok 150: Uruchamiam run_raport_akcje.sh"
/bin/bash "$BASE_PATH/run_raport_akcje.sh"

echo "SUKCES: Proces Koniec Dnia zakończony: $(date)"
echo "---------------------------------------------------------------"
