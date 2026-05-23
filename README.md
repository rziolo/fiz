# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi.

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived).
- **Load Balancer:** Apache2 z modułem `mod_proxy_balancer`.
- **Logic:**
    - **Mirroring:** `/inwestycje`, `/finanse`, `/zdrowie` (aplikacje mają prefiksy w kodzie Pythona).
    - **Stripping:** `/aplikacje` (HUB - przekierowanie na korzeń `/` aplikacji).
- **Storage:** GlusterFS (zsynchronizowany wolumen `/var/www/html/flask`).
- **Integracje:** Eksport danych finansowych do Home Assistant via JSON/SSH.

## 🚀 Wykaz Aplikacji i Portów (Pełne HA)
| Aplikacja | Ścieżka URL | Port Lokalny | Status / Baza Danych |
| :--- | :--- | :--- | :--- |
| **Aplikacje** | `/aplikacje` | 5000 | **HA** (Local Galera) |
| **Finanse** | `/finanse` | 5001 | **HA** (Local Galera) |
| **Inwestycje**| `/inwestycje`| 5002 | **HA** (Local Galera) |
| **Zdrowie** | `/zdrowie` | 5003 | **HA** (SQLite/GlusterFS) |
| **n8n** | `http://192.168.1.130:5678/` | 5678 | **External** (rz-rpi-02) |

## 📈 Kluczowe zmiany (06.05.2026)
- **Ujednolicenie UI (Globalne):** Wprowadzono wspólny szablon `base.html` z czarnym paskiem nawigacji (Dark Navbar) i ujednoliconym statusem połączenia z bazą danych ("pigułka" OK).
- **Inwestycje - Logika Kontrolna:** Wdrożono dynamiczne kolorowanie dat (`text-green` / `text-red`) w tabeli importu. System porównuje daty plików i bazy z aktualnym dniem (`today()`).
- **Inwestycje - Funkcje ETL:** Przywrócono pełną obsługę JavaScript dla przycisków: Sprawdź Dzisiejsze, Importuj, Load oraz Aktualizuj. Dodano modal do podglądu plików CSV bezpośrednio w przeglądarce.
- **Finanse - Optymalizacja Layoutu:** Przebudowano kafelki menu na mniejsze (grid 6-kolumnowy), zapewniając poprawną widoczność stopki autorskiej na urządzeniach mobilnych i tabletach.
- **Stabilność:** Naprawiono błędy `Internal Server Error` poprzez ujednolicenie ścieżek do szablonów i przywrócenie lokalnych plików `base.html` tam, gdzie współdzielenie wolumenu powodowało konflikty.

## 🛠 Zarządzanie
- **Restart wszystkich usług:** `sudo systemctl restart flask-aplikacje flask-finanse flask-inwestycje flask-zdrowie`
- **Status klastra:** `sudo systemctl status "flask-*"`
- **Logi Apache:** `tail -f /var/log/apache2/access.log`
- **Test JSON HA:** `python3 /var/www/html/flask/finanse/etl/python/get_finanse_json.py`

---
*Ostatnia aktualizacja: 2026-05-24 00:10
