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
| **Aplikacje** | `/aplikacje` | `5000` | HUB - Menu Główne |
| **Finanse** | `/finanse` | `5001` | **Aktywna**: Bilans, Samochód, Wykresy |
| **Inwestycje**| `/inwestycje`| `5002` | **Aktywna**: Portfel, Dane Giełdowe, Obroty |
| **Zdrowie** | `/zdrowie` | `5003` | Monitoring ciśnienia + HA |

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-19)
- **CRUD 3-w-1:** Zastosowanie uniwersalnego formularza obsługującego tryby: Dodaj, Podgląd (readonly) oraz Edycja w ramach jednego szablonu `.html`.
- **Zarządzanie Obrotami:** - Inteligentne filtrowanie "Obecne" (pokazuje tylko otwarte pozycje).
    - Dynamiczne listy rozwijane (Ticker, Platforma) pobierane prosto z relacyjnych tabel bazy danych.
- **Interfejs Użytkownika:**
    - Numeracja Lp. generowana dynamicznie.
    - Okna modalne dla kolumny "Uwagi" (ikona notatki), oszczędzające miejsce w tabeli głównej.
    - Automatyczne formatowanie walutowe i wizualne wyróżnianie zmian kursów.

## 💰 Moduł Finanse
- **Bilans:** Automatyczne kolorowanie wartości dodatnich i ujemnych.
- **Samochód:** Analityka przebiegów miesięcznych i kosztu 1 km.
- **Wykresy:** Interaktywne zakładki, filtrowanie zakresów (12-36 m-cy) i wizualne sygnalizatory uwag (czerwone rąby).

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-finanse` (lub `flask-inwestycje`, `flask-zdrowie`)
- **Podgląd błędów:** `sudo journalctl -u flask-inwestycje -f`
- **Aktualizacja:** Pamiętaj o synchronizacji przez GlusterFS po edycji plików.

## 💡 Troubleshooting & Refleksje (Update 2026-04-19)
1. **Relacyjność w Formularzach:** Pobieranie danych do dropdownów (np. Ticker) bezpośrednio w trasie `GET` przed renderowaniem formularza drastycznie redukuje błędy literówek w bazie.
2. **Logika Widoków:** Użycie parametrów `request.args` (np. `?filter=current`) pozwala na tworzenie szybkich filtrów bez konieczności budowania osobnych podstron.
3. **Spójność UI:** Stosowanie tego samego zestawu ikon (FontAwesome) dla akcji Oko (widok), Ołówek (edycja) i Kosz (usuwanie) sprawia, że system jest intuicyjny.

---
Ostatnia aktualizacja: 2026-04-19 10:00
