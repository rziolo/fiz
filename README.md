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

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-20)
- **Panel Zarządzania Importem (Index):**
    - Dynamiczne monitorowanie dat importu dla GPW, NC oraz rynków zagranicznych.
    - **Ręczna Aktualizacja:** Przycisk "AKTUALIZUJ" w GUI wyzwalający skrypt Bash w tle (`subprocess.Popen`).
    - **Podgląd CSV w Modal:** Zintegrowany system odczytu plików `.csv` bezpośrednio w przeglądarce.
- **Automatyzacja ETL:**
    - Skrypty Python do scrapowania danych (Stooq, GPW-NC, Investing).
    - Skrypt zbiorczy Bash: `/inwestycje/etl/bash/run_import_nc_zagr_stooq.sh`.
    - Harmonogram Cron: Codziennie o 18:20 w dni robocze.
- **Analiza Sprzedaży i Stop Loss:**
    - Wyliczanie sugerowanej ceny sprzedaży (minima z 3 sesji + bufor 3%).
    - Alerty dla zysków > 300 PLN wymagających zabezpieczenia.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart inwestycje`
- **Podgląd logów ETL:** `tail -f /var/www/html/flask/inwestycje/etl/python/etl.log`
- **Diagnostyka systemd:** `sudo journalctl -u inwestycje -f`
- **Eksport zależności:** `pip freeze | sudo tee /var/www/html/flask/requirements.txt > /dev/null`

## 💡 Troubleshooting & Refleksje (Update 2026-04-20)
1. **Scrapowanie (Stooq):** Dane pobierane z XML/CDATA wymagają agresywnego czyszczenia znaków `\xa0` i spacji dla poprawnej konwersji `int()`.
2. **Uprawnienia:** Zapisywanie logów i plików `.csv` przez skrypty odppalane z Crona musi uwzględniać uprawnienia zapisu dla użytkownika `www-data`.
3. **Izolacja venv:** Zawsze używaj ścieżki bezwzględnej do interpretera: `/var/www/html/flask/venv/bin/python3`.

---
Ostatnia aktualizacja: 2026-04-20 20:10
