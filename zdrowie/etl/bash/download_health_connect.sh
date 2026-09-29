#!/bin/bash

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

BASE_DIR="/var/www/html/flask/zdrowie/etl/db/health_connect"
TEMP_DIR="${BASE_DIR}/temp"
TARGET_DB="${BASE_DIR}/health_connect_export.db"
GDOWN_BIN="/var/www/html/flask/venv/bin/gdown"

mkdir -p "${TEMP_DIR}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rozpoczynam pobieranie bazy Health Connect..."

# Pobranie pliku z Google Drive na podstawie adresu ID
${GDOWN_BIN} "https://drive.google.com/uc?id=1iuSllTbMi8vC6TuLgMvtF4K67ABRM2Mi" -O "${TEMP_DIR}/Health Connect.zip"

if [ -f "${TEMP_DIR}/Health Connect.zip" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rozpakowywanie archiwum..."
    rm -rf "${TEMP_DIR}/extracted"
    mkdir -p "${TEMP_DIR}/extracted"
    unzip -o "${TEMP_DIR}/Health Connect.zip" -d "${TEMP_DIR}/extracted"
    
    EXTRACTED_DB=$(find "${TEMP_DIR}/extracted" -type f -name "*.db" | head -n 1)
    
    if [ -n "${EXTRACTED_DB}" ] && [ -f "${EXTRACTED_DB}" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Podmieniam bazę na ${TARGET_DB}"
        cp -f "${EXTRACTED_DB}" "${TARGET_DB}"
        chmod 664 "${TARGET_DB}"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Aktualizacja bazy zakończona pomyślnie."
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] BŁĄD: Nie znaleziono pliku .db po rozpakowaniu!"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] BŁĄD: Nie udało się pobrać Health Connect.zip"
fi

rm -rf "${TEMP_DIR}"
