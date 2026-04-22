#!/ Junior/bin/bash

# Ścieżki
BASE_DIR="/var/www/html/flask/inwestycje"
PYTHON_BIN="/var/www/html/flask/venv/bin/python3"

# Pobranie dat z utils.py za pomocą krótkiego skryptu inline
DATES=$($PYTHON_BIN -c "
import sys
sys.path.append('$BASE_DIR')
from utils import get_stats
s = get_stats()
print(f\"{s['data_import_gpw']}|{s['data_dane']}\")
")

DATA_IMPORT=$(echo $DATES | cut -d'|' -f1)
DATA_BAZA=$(echo $DATES | cut -d'|' -f2)

echo "Data w pliku CSV: $DATA_IMPORT"
echo "Data ostatnia w bazie: $DATA_BAZA"

if [ "$DATA_IMPORT" == "$DATA_BAZA" ]; then
    echo "Daty są identyczne ($DATA_BAZA). Przerywam ładowanie."
    exit 0
else
    echo "Wykryto nową sesję. Uruchamiam load_dane.py..."
    $PYTHON_BIN "$BASE_DIR/etl/python/load_dane.py"
fi
