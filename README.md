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
| **Inwestycje**| `/inwestycje`| `5002` | **Aktywna**: Portfel, Dane Giełdowe, Moduł Sprzedaży |
| **Zdrowie** | `/zdrowie` | `5003` | Monitoring ciśnienia + HA |

## 📈 Moduł Inwestycje - Nowe Funkcje (Update 2026-04-20)
- **Analiza Sprzedaży i Stop Loss:**
    - Dynamiczne wyliczanie sugerowanej ceny sprzedaży na podstawie minimów z 3 ostatnich sesji (bufor 3%).
    - System alertów: wizualne wyróżnienie (różowe tło) dla pozycji z zyskiem > 300 PLN wymagających ustawienia Stop Loss.
    - Wskaźnik "Podnieś": automatyczna sugestia aktualizacji SL, gdy parametry techniczne ulegną poprawie.
- **Kalkulator Walutowy (Foreign Markets):**
    - Integracja z API NBP (skrypt `shared/kursy_nbp.py`) dla kursów USD i EUR.
    - Interaktywne okno modalne: przelicza sugerowaną cenę sprzedaży z PLN na walutę oryginalną (np. dla IUSQ, NVIDIA).
- **Zarządzanie Obrotami:**
    - Inteligentne filtrowanie "Obecne" oraz dynamiczne listy rozwijane Ticker/Platforma z relacyjnej bazy danych.
- **CRUD & UI:**
    - Uniwersalny formularz Dodaj/Podgląd/Edycja w jednym szablonie.
    - Okna modalne dla kolumny "Uwagi" i formatowanie walutowe `format_pl`.

## 💰 Moduł Finanse
- **Bilans:** Automatyczne kolorowanie wartości dodatnich i ujemnych.
- **Samochód:** Analityka przebiegów miesięcznych i kosztu 1 km.
- **Wykresy:** Interaktywne zakładki (12/24/36m/Wszystko) i wizualne sygnalizatory uwag (czerwone romby).

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-finanse` (lub `flask-inwestycje`, `flask-zdrowie`)
- **Podgląd błędów:** `sudo journalctl -u flask-inwestycje -f`
- **Aktualizacja:** Pamiętaj o synchronizacji przez GlusterFS po edycji plików.

## 💡 Troubleshooting & Refleksje (Update 2026-04-20)
1. **Zmienne Środowiskowe:** Kluczowe dla bezpieczeństwa poświadczeń bazy danych (`python-dotenv`).
2. **Importy współdzielone:** Skrypty w `/shared/` (jak `kursy_nbp.py`) pozwalają na zachowanie zasady DRY (Don't Repeat Yourself) w całym klastrze.
3. **Python 3.13 & Stabilność:** Przy nowych wersjach interpretera kluczowe jest monitorowanie logów Gunicorna pod kątem błędów `SystemExit` związanych z biblioteką `mysql-connector-python`.

---
Ostatnia aktualizacja: 2026-04-20 12:45
