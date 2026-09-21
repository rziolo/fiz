#!/bin/bash

# Załadowanie zmiennych środowiskowych z pliku .env
if [ -f "/var/www/html/flask/zdrowie/.env" ]; then
    export $(grep -v '^#' /var/www/html/flask/zdrowie/.env | xargs)
fi

TARGET_DIR="/var/www/html/flask/zdrowie/etl/db/health_connect"
TEMP_DIR="$TARGET_DIR/temp"
FOLDER_ID="${HEALTH_CONNECT_FOLDER_ID}"

# Utworzenie katalogu tymczasowego
mkdir -p "$TEMP_DIR"

# Pobranie całej zawartości folderu
/var/www/html/flask/venv/bin/gdown --folder "$FOLDER_ID" -O "$TEMP_DIR"

# Rozpakowanie archiwum ZIP
ZIP_PATH=$(find "$TEMP_DIR" -iname "*Health*Connect*.zip" -type f | head -n 1)

if [ -n "$ZIP_PATH" ]; then
    unzip -o "$ZIP_PATH" -d "$TARGET_DIR/"
fi

# Czyszczenie katalogu tymczasowego
rm -rf "$TEMP_DIR"
