# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi (**rz-rpi-05** i **rz-rpi-06**).

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived)
- **Reverse Proxy:** Apache2 (mod_proxy)
- **Storage:** GlusterFS (zsynchronizowany folder `/var/www/html/flask`)
- **WSGI Server:** Gunicorn zarządzany przez Systemd

## 🚀 Wykaz Aplikacji i Portów
| Aplikacja | Ścieżka URL | Port Lokalny | Status / Funkcje |
| :--- | :--- | :--- | :--- |
| **Aplikacje** | `/aplikacje` | 5000 | HUB - Menu Główne |
| **Finanse** | `/finanse` | 5001 | **Aktywna**: Bilans, Samochód, Wykresy |
| **Inwestycje**| `/inwestycje`| 5002 | **Aktywna**: Portfel, Dane Giełdowe, ETL, Moduł Sprzedaży |
| **Zdrowie** | `/zdrowie` | 5003 | Monitoring ciśnienia + HA |

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-21)
- **Panel Zarządzania Importem (Index):**
    - Dynamiczne monitorowanie dat z plików CSV (GPW, NC, Zagraniczne, Stooq).
    - **Weryfikacja Archiwum GPW:** Dedykowany przycisk "Sprawdź dzisiejsze" (endpoint `/run_gpw_check`).
    - **Nowy Moduł Importu GPW:** Bezpośrednie pobieranie plików `.xls` z serwerów GPW i konwersja do CSV (przycisk AKTUALIZUJ).
- **Automatyzacja ETL i Load:**
    - **Skrypt run_laduj.sh:** Inteligentna synchronizacja (CSV vs SQL).
    - **Skrypt run_import_gpw.sh:** Automatyzacja pobierania danych giełdowych z **rotacją plików Excel** (zachowuje 5 ostatnich sesji, aby oszczędzać miejsce).
    - **Scraping:** Skrypty Python (Stooq, GPW-NC, Investing) z emulacją nagłówków.
    - **Statystyki sesji:** Moduł zapisu (Wycena, Wkład) z walidacją w `utils.py`.
- **Interfejs:**
    - Modale z podglądem treści plików CSV bezpośrednio z tabeli głównej.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-inwestycje`
- **Podgląd logów ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`
- **Ręczny Import GPW (Bash):** `/var/www/html/flask/inwestycje/etl/bash/run_import_gpw.sh`

## 💡 Troubleshooting & Refleksje (Update 2026-04-21)
1. **Scrapowanie:** Użycie `requests.Session()` i obsługa błędów formatu XLS/HTML w pandas rozwiązuje problemy z archiwalnymi danymi GPW.
2. **Środowisko:** Skrypty Bash używają pełnych ścieżek `/var/www/html/flask/inwestycje/venv/bin/python3`, co gwarantuje poprawność w środowisku produkcyjnym.
3. **Logika Wyceny:** SQL z `GROUP BY ticker + MAX(data)` zapewnia poprawną wartość portfela przy asynchronicznych datach notowań (np. gdy zagranica ma sesję, a Polska nie).
4. **Zarządzanie Storage:** Mechanizm `ls -t | tail -n +6 | xargs rm` w skryptach bash zapobiega zapychaniu GlusterFS przez tymczasowe pliki Excel.

---
Ostatnia aktualizacja: 2026-04-22 00:10
