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

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-23)
- **Panel Zarządzania Importem (Index):**
    - Dynamiczne monitorowanie dat z plików CSV (GPW, NC, Zagraniczne, Stooq).
    - **Weryfikacja Archiwum GPW:** Dedykowany przycisk "Sprawdź dzisiejsze" (endpoint `/run_gpw_check`).
    - **Ręczny Import:** Przycisk **AKTUALIZUJ** wyzwalający natychmiastowe pobranie i przetworzenie danych GPW.
- **Automatyzacja Raportowania (Raporty CSV):**
    - **Raport Statystyka:** Automatyczne generowanie `raport_statystyka.csv` (Wycena, Wkład, HL/NL, Turnover).
    - **Raport Akcje (Logika A/B):** Inteligentny system sugestii sprzedaży i podnoszenia Stop Loss.
- **Harmonogram Koniec Dnia (`koniec_dnia.sh`):**
    - W pełni zautomatyzowana pętla ETL (19:20 - 23:30) z inteligentnym oczekiwaniem na publikację danych (interwał 10 min).
- **Interfejs & UX:**
    - **Wizualizacja Dynamiki:** Kolorowanie "Kursu bieżącego" względem ceny zamknięcia z dnia poprzedniego (`close_1`): Zielony (wzrost), Czerwony (spadek), Szary (bez zmian).
    - **Kalkulator Walut:** Modale z przeliczeniem kursów NBP w widoku sprzedaży dla pozycji zagranicznych.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-inwestycje`
- **Podgląd logów ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`
- **Proces Koniec Dnia:** `/var/www/html/flask/inwestycje/etl/bash/koniec_dnia.sh`

## 💡 Troubleshooting & Refleksje (Update 2026-04-23)
1. **Zmienne Środowiskowe:** Skrypty Bash Crona wymagają `load_dotenv` do poprawnej autoryzacji z MariaDB.
2. **Synchronizacja Klastra:** Po edycji plików `.html` w GlusterFS konieczny jest restart Gunicorna na obu węzłach, aby przeładować szablony z pamięci RAM.
3. **Logika Wyceny:** SQL z `MAX(data)` zapewnia poprawność portfela przy asynchronicznych sesjach giełdowych.
4. **Zarządzanie Storage:** Automatyczna rotacja plików tymczasowych Excel (utrzymywanie 5 ostatnich wersji).

---
Ostatnia aktualizacja: 2026-04-23 13:00
