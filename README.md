# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi (**rz-rpi-05** i **rz-rpi-06**).

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived)
- **Reverse Proxy:** Apache2 (mod_proxy) z Load Balancingiem
- **Storage:** GlusterFS (zsynchronizowany wolumen `/var/www/html/flask`)
- **Baza Danych:** MariaDB Galera Cluster (Multi-Master)
  - **Zmigrowano:** Baza `finanse` (2026-04-24)
  - **W planie:** Baza `inwestycje` (obecnie jeszcze na rz-rpi-02)
- **WSGI Server:** Gunicorn zarządzany przez Systemd

## 🚀 Wykaz Aplikacji i Portów
| Aplikacja | Ścieżka URL | Port Lokalny | Status / Baza Danych |
| :--- | :--- | :--- | :--- |
| **Aplikacje** | `/aplikacje` | 5000 | HUB - Menu Główne |
| **Finanse** | `/finanse` | 5001 | **AKTYWNA** (Baza: Local Galera) |
| **Inwestycje**| `/inwestycje`| 5002 | **W TRAKCIE** (Baza: rz-rpi-02) |
| **Zdrowie** | `/zdrowie` | 5003 | **AKTYWNA** (Baza: SQLite/HA) |

## 📈 Moduł Inwestycje - Nowe Funkcje
- **Panel Zarządzania Importem:** Dynamiczne monitorowanie dat z plików CSV (GPW, NC, Stooq).
- **Automatyzacja ETL:** Skrypty Bash i Python zintegrowane z harmonogramem Cron.
- **Weryfikacja Archiwum:** Przycisk "Sprawdź dzisiejsze" (endpoint `/run_gpw_check`).
- **Wizualizacja:** Dynamiczne kolorowanie kursów względem zamknięcia z dnia poprzedniego.

## ⚙️ Operacje Migracyjne (2026-04-24)
1. **Migracja Finanse:** Baza `finanse` została przeniesiona z `rz-rpi-02` do klastra MariaDB Galera.
2. **Konfiguracja .env:** Zmieniono `DB_HOST=localhost` w module Finanse, co umożliwia pełną redundancję.
3. **Weryfikacja ETL:** Skrypty w `/etl/python/` zostały zweryfikowane pod kątem współpracy z `venv` i nową bazą.

## 🛠 Zarządzanie i Diagnostyka
- **Status usług:** `sudo systemctl status "flask-*"`
- **Restart wszystkich:** `sudo systemctl restart flask-finanse flask-inwestycje flask-aplikacje`
- **Logi systemowe:** `sudo journalctl -u flask-finanse -f`
- **Logi ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`

---
*Ostatnia aktualizacja: 2026-04-28 00:10
