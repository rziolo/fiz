# Moje Aplikacje (Flask Applications Suite)

Zestaw mikroserwisów opartych na frameworku Flask, działających w architekturze jednouzłowej (standalone) bezpośrednio na Raspberry Pi 4 (`rz-rpi-05`).

## Features

- 🍓 Dedykowane środowisko produkcyjne uruchomione na Raspberry Pi 4.
- 🐍 Aplikacje napisane w języku Python z wykorzystaniem Flask.
- ⚡ Szybki dostęp proxy za pośrednictwem serwera Apache2.
- 📊 Dedykowane moduły do zarządzania finansami, inwestycjami i danymi zdrowotnymi.
- 🔐 Bezpieczna konfiguracja zmiennych środowiskowych z plikami `.env`.
- 🔄 Automatyczny pobór danych ETL dla Health Connect z Dysku Google.

## Architecture

┌────────────────────────────────────────────────────────┐
│                    Client Browser                      │
└───────────────────────────┬────────────────────────────┘
                            │ (HTTP / 192.168.1.133)
                            ▼
┌────────────────────────────────────────────────────────┐
│               Apache2 Web Server (Proxy)               │
└─────┬──────────────┬──────────────┬──────────────┬─────┘
      │ /aplikacje   │ /finanse     │ /inwestycje  │ /zdrowie
      ▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│ App: 5000 │  │ App: 5001 │  │ App: 5002 │  │ App: 5003 │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│     MariaDB Database     │  │ SQLite / HA / Health DB  │
└──────────────────────────┘  └──────────────────────────┘

## Project Structure

flask/
├── aplikacje/
│   ├── .env.example
│   └── app.py
├── finanse/
│   ├── .env.example
│   ├── app.py
│   └── structure_finanse.sql
├── inwestycje/
│   ├── .env.example
│   ├── app.py
│   └── structure_inwestycje.sql
├── zdrowie/
│   ├── etl/
│   │   ├── bash/
│   │   │   └── download_health_connect.sh
│   │   └── db/
│   │       └── health_connect/
│   │           └── health_connect_export.db
│   ├── .env.example
│   ├── app.py
│   └── structure_table_vita_pressure.sql
├── shared/
├── venv/
├── README.md
└── requirements.txt

## File Description

| Plik / Katalog | Opis |
|---|---|
| `aplikacje/` | Główny panel nawigacyjny i powiązane mikroserwisy. |
| `finanse/` | Aplikacja do zarządzania finansami osobistymi. |
| `inwestycje/` | Moduł śledzenia portfela inwestycyjnego i notowań GPW. |
| `zdrowie/` | Aplikacja do rejestracji pomiarów ciśnienia oraz analizy danych z Health Connect (`health_connect_export.db`). |
| `shared/` | Wspólne komponenty, szablony HTML oraz moduły pomocnicze. |
| `*.sql` | Skrypty ze strukturą baz danych dla poszczególnych modułów. |
| `.env.example` | Szablony zmiennych środowiskowych. |

## Installation

1. Przejdź do katalogu aplikacji:
   cd /var/www/html/flask

2. Aktywuj wirtualne środowisko Pythona:
   source venv/bin/activate

3. Zainstaluj wymagane zależności:
   pip install -r requirements.txt

## Configuration

Przed uruchomieniem aplikacji należy skonfigurować pliki `.env` w poszczególnych podkatalogach (`finanse`, `inwestycje`, `zdrowie`).

Skopiuj wzorzec dla każdej aplikacji:

cp finanse/.env.example finanse/.env
cp inwestycje/.env.example inwestycje/.env
cp zdrowie/.env.example zdrowie/.env

Uzupełnij właściwe parametry dostępowe:

DB_HOST=192.168.x.xxx
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database

## Security

Nigdy nie należy dodawać produkcyjnych plików `.env` do kontroli wersji Git:

.env
*.key
*.pem

Upewnij się, że plik `.gitignore` zawiera wpis `.env`, aby zapobiec wyciekowi poświadczeń.

## Troubleshooting

### Usługa nie odpowiada

Sprawdź status usług Flask w systemie:

sudo systemctl status "flask-*"

### Restart usług

Zrestartuj wszystkie mikroserwisy:

sudo systemctl restart flask-aplikacje flask-finanse flask-inwestycje flask-zdrowie

### Sprawdzanie logów

journalctl -u flask-zdrowie -f

## Quick Start

Uruchomienie produkcyjne wszystkich usług:

sudo systemctl start flask-aplikacje flask-finanse flask-inwestycje flask-zdrowie

Weryfikacja działania w przeglądarce:

http://192.168.1.133/aplikacje

---

## Credits

Opracowanie Robert Zioło + AI, plik zaktualizowano 2026-09-22
