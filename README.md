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
| **Inwestycje**| `/inwestycje`| 5002 | **Aktywna**: Portfel, Dane Giełdowe, Moduł Sprzedaży |
| **Zdrowie** | `/zdrowie` | 5003 | Monitoring ciśnienia + HA |

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-20)
- **Panel Zarządzania Importem (Index):**
    - Dynamiczne monitorowanie dat importu dla GPW, NewConnect oraz rynków zagranicznych.
    - System powiadomień kolorystycznych: zielony (aktualne), czerwony (wymaga aktualizacji), różowe tło dla statusu "dzienne".
    - **Podgląd CSV w Modal:** Zintegrowany system odczytu plików `.csv` bezpośrednio w przeglądarce bez opuszczania strony.
- **Analiza Sprzedaży i Stop Loss:**
    - Dynamiczne wyliczanie sugerowanej ceny sprzedaży na podstawie minimów z 3 ostatnich sesji (bufor 3%).
    - System alertów dla pozycji z zyskiem > 300 PLN wymagających ustawienia Stop Loss.
- **Kalkulator Walutowy:**
    - Integracja z API NBP dla kursów USD i EUR.
    - Przeliczanie ceny sprzedaży z PLN na walutę oryginalną w oknach modalnych.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-inwestycje`
- **Podgląd błędów:** `sudo journalctl -u flask-inwestycje -f`
- **Diagnostyka Jinja2:** W przypadku błędów `TemplateSyntaxError` sprawdź domknięcia tagów `{% endblock %}`.

## 💡 Troubleshooting & Refleksje (Update 2026-04-20)
1. **Routing Statyczny:** Pliki CSV wymagają dedykowanej trasy we Flasku (`send_from_directory`), aby uniknąć błędów 404 w oknach modalnych.
2. **GlusterFS:** Wszelkie zmiany w `utils.py` lub szablonach są replikowane między rpi-05 a rpi-06 automatycznie.
3. **UI/UX:** Zastosowanie spójnej kolorystyki (np. `#fce4ec` dla sekcji aktualizacji) poprawia czytelność statusu bazy danych.

---
Ostatnia aktualizacja: 2026-04-20 15:05
