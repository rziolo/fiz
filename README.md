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

## 📈 Kluczowe zmiany (30.04.2026)
- **Integracja Home Assistant:** Wdrożono skrypt `get_finanse_json.py`, który parsuje dane CSV do formatu JSON na potrzeby sensora `command_line` w HA.
- **Korekta Logiki Finansowej:** Wprowadzono funkcję `ABS()` w modułach `historia.py` oraz `chart.py`. Wkład jest teraz traktowany jako wartość dodatnia.
- **Interfejs Zdrowie:** Przebudowano formularz ciśnienia na czytelny układ 4-kolumnowy.
- **HUB Aplikacji:** Dodano kartę "Automatyzacja" z linkiem do n8n (rz-rpi-02).

## 🛠 Zarządzanie
- **Restart wszystkich usług:** `sudo systemctl restart "flask-*"`
- **Status klastra:** `sudo systemctl status "flask-*"`
- **Logi Apache:** `tail -f /var/log/apache2/access.log`
- **Test JSON HA:** `python3 /var/www/html/flask/finanse/etl/python/get_finanse_json.py`

---
*Ostatnia aktualizacja: 2026-05-03 00:10
