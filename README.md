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
    - **Weryfikacja Archiwum GPW:** Dedykowany przycisk "Sprawdź dzisiejsze" (endpoint `/run_gpw_check`) weryfikujący dostępność plików `.prn`.
- **Automatyzacja ETL i Load:**
    - **Skrypt run_laduj.sh:** Inteligentna synchronizacja. Porównuje daty CSV vs SQL; blokuje import, jeśli dane są już w bazie.
    - **Scraping:** Skrypty Python (Stooq, GPW-NC, Investing) z emulacją nagłówków.
    - **Statystyki sesji:** Nowy moduł zapisu (Wartość, Wkład, H/L) z walidacją w `utils.py`.
- **Interfejs:**
    - Modale z podglądem treści plików CSV bezpośrednio z tabeli głównej.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-inwestycje`
- **Podgląd logów ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`
- **Ręczny Load (z kontrolą):** `/var/www/html/flask/inwestycje/etl/bash/run_laduj.sh`

## 💡 Troubleshooting & Refleksje (Update 2026-04-21)
1. **Scrapowanie:** Użycie `requests.Session()` eliminuje błędy `Connection reset`.
2. **Środowisko skryptów:** Skrypty Bash muszą eksportować zmienne z `.env` i używać `/venv/bin/python3`, aby uniknąć `Access denied` przy połączeniach SQL.
3. **Logika Wyceny:** SQL z `GROUP BY ticker + MAX(data)` zapewnia poprawną wartość portfela przy asynchronicznych datach notowań.
4. **Synchronizacja:** Zmiany w `/var/www/html/flask` są automatycznie replikowane przez GlusterFS na oba węzły klastra.

---
Ostatnia aktualizacja: 2026-04-21 16:30
