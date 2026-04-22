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

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-22)
- **Panel Zarządzania Importem (Index):**
    - Dynamiczne monitorowanie dat z plików CSV (GPW, NC, Zagraniczne, Stooq).
    - **Weryfikacja Archiwum GPW:** Dedykowany przycisk "Sprawdź dzisiejsze" (endpoint `/run_gpw_check`).
    - **Nowy Moduł Importu GPW:** Bezpośrednie pobieranie plików `.xls` z serwerów GPW i konwersja do CSV (przycisk AKTUALIZUJ).
- **Automatyzacja Raportowania (Raporty CSV):**
    - **Raport Statystyka:** Automatyczne generowanie `raport_statystyka.csv` (Wycena, Wkład, HL/NL, Turnover).
    - **Raport Akcje (Logika A/B):** Inteligentny system sugestii sprzedaży i podnoszenia Stop Loss:
        - **Logika A (Wystaw):** Zysk > 300 PLN przy braku SL (automatyczne przeliczanie walut USD/EUR/GBP wg NBP).
        - **Logika B (Podnieś):** Detekcja konieczności aktualizacji SL na podstawie 3-dniowych minimów.
- **Harmonogram Koniec Dnia (`koniec_dnia.sh`):**
    - W pełni zautomatyzowana pętla ETL (19:20 - 23:30).
    - Inteligentne oczekiwanie na publikację archiwum GPW (interwał 10 min).
    - Sekwencyjne uruchamianie importu, ładowania do SQL i generowania raportów końcowych.
- **Interfejs:**
    - Modale walutowe z kalkulatorem przeliczeń kursów NBP bezpośrednio w widoku sprzedaży.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-inwestycje`
- **Podgląd logów ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`
- **Proces Koniec Dnia:** `/var/www/html/flask/inwestycje/etl/bash/koniec_dnia.sh`

## 💡 Troubleshooting & Refleksje (Update 2026-04-22)
1. **Zmienne Środowiskowe:** Skrypty Bash uruchamiane z Crona wymagają jawnego `load_dotenv` wewnątrz wywołań Pythona, aby poprawnie autoryzować połączenia z bazą danych (MariaDB/MySQL).
2. **Synchronizacja Walut:** Integracja z API NBP (`kursy_nbp.py`) współdzielona między modułami Finanse i Inwestycje zapewnia spójność wycen zagranicznych.
3. **Logika Wyceny:** SQL z `GROUP BY ticker + MAX(data)` zapewnia poprawną wartość portfela przy asynchronicznych datach notowań (np. gdy zagranica ma sesję, a Polska nie).
4. **Zarządzanie Storage:** Mechanizm `ls -t | tail -n +6 | xargs rm` zapobiega zapychaniu GlusterFS przez tymczasowe pliki Excel.

---
Ostatnia aktualizacja: 2026-04-23 00:10
