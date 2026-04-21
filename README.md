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
    - **Weryfikacja Archiwum GPW:** Dedykowany przycisk "Sprawdź dzisiejsze" (endpoint `/run_gpw_check`) weryfikujący dostępność plików `.prn` na serwerach GPW.
    - **Ręczna Aktualizacja:** Zoptymalizowany proces importu z wizualizacją postępu (czas operacji ~40s).
- **Automatyzacja Danych Dziennych:**
    - Nowy moduł zapisu statystyk sesji (Wartość portfela, Wkład, H/L, Turnover, HL/NL).
    - Skrypt `/inwestycje/etl/bash/run_dane_dzienne.sh` automatycznie utrwalający stan sesji w bazie SQL.
    - Dynamiczne formularze (tryby: `view`, `edit`, `create`) z automatycznym podpowiadaniem danych z plików ETL.
- **Automatyzacja ETL:**
    - Skrypty Python do scrapowania danych (Stooq, GPW-NC, Investing) z emulacją nagłówków przeglądarki.
    - Skrypt zbiorczy Bash: `/inwestycje/etl/bash/run_import_nc_zagr_stooq.sh`.
    - Harmonogram Cron: Codziennie o 18:20 w dni robocze.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-inwestycje`
- **Status usługi:** `sudo systemctl status flask-inwestycje`
- **Podgląd logów ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`
- **Zapis statystyk dnia:** `/var/www/html/flask/inwestycje/etl/bash/run_dane_dzienne.sh`

## 💡 Troubleshooting & Refleksje (Update 2026-04-21)
1. **Scrapowanie (Stooq/GPW):** Zastosowano `requests.Session()` oraz rozbudowane nagłówki, aby uniknąć błędów `Connection reset by peer`.
2. **Łączność SQL w Bash:** W przypadku błędów `TLS/SSL error` lub `SSL is required` w skryptach Bash, należy stosować flagę `--skip-ssl` przy wywołaniu klienta `mysql`.
3. **Synchronizacja plików:** Dzięki GlusterFS zmiany w `/var/www/html/flask` są replikowane między rpi-05 i rpi-06.
4. **Logika Panelu:** Funkcja `get_stats()` w `utils.py` weryfikuje zawartość plików statusowych, co pozwala na dynamiczne kolorowanie statusów (OK/BRAK) w GUI.

---
Ostatnia aktualizacja: 2026-04-21 14:15
