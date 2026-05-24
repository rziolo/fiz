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

## 🚀 Wykaz Aplikacji i Portów (Pełne HA / Integracje)
| Aplikacja | Ścieżka URL | Port Lokalny | Status / Baza Danych |
| :--- | :--- | :--- | :--- |
| **Aplikacje** | `/aplikacje` | 5000 | **HA** (Local Galera) |
| **Finanse** | `/finanse` | 5001 | **HA** (Local Galera) |
| **Inwestycje**| `/inwestycje`| 5002 | **HA** (Local Galera) |
| **Zdrowie** | `/zdrowie` | 5003 | **HA** (SQLite/GlusterFS) |
| **n8n** | `http://192.168.1.130:5678/` | 5678 | **External** (rz-rpi-02) |
| **Sprzęt (Centrum Mon.)** | `http://192.168.1.131/mon/` | 80 (Apache) | **External** (rz-rpi-02) |

## 📈 Kluczowe zmiany (24.05.2026)
- **Centrum Monitoringu w HUB-ie:** Do panelu głównego `/aplikacje` dodano piąty kafelek "Sprzęt" linkujący do zewnętrznego systemu `lan_glances` na `rz-rpi-02` (`/mon/`), agregującego teledane z klastra, urządzeń mobilnych i Home Assistant.
- **Optymalizacja Grid UI:** Przebudowano układ siatki na stronie głównej HUB-u przy użyciu klas `row-cols-xl-5` oraz Flexbox, zapewniając idealne wyrównanie przycisków i płynne skalowanie (PC / tablet / smartfon).
- **Automatyzacja Szablonów (Crontab):** Wdrożono skrypt bash `/var/www/html/flask/shared/bash/update_base.sh` uruchamiany codziennie o 00:25, automatycznie synchronizujący nadrzędny plik `base.html` do modułu Finansów.
- **Naprawa UI Finanse:** Rozwiązano problem braku widoczności ikon akcji (podgląd, edycja, usuń) poprzez wstrzyknięcie biblioteki Bootstrap Icons do nadrzędnego szablonu `base.html`.
- **Uporządkowanie Uprawnień:** Przepisano uprawnienia własności struktury katalogów (`chown`) na użytkownika `rz-rpi-06`, eliminując błędy *Permission denied* przy automatyzacji zadań z poziomu crona i pracy w VS Code przez SSH.

## 🛠 Zarządzanie
- **Restart wszystkich usług:** `sudo systemctl restart flask-aplikacje flask-finanse flask-inwestycje flask-zdrowie`
- **Status klastra:** `sudo systemctl status "flask-*"`
- **Logi Apache:** `tail -f /var/log/apache2/access.log`
- **Test JSON HA:** `python3 /var/www/html/flask/finanse/etl/python/get_finanse_json.py`
- **Ręczna synchronizacja szablonu:** `/bin/bash /var/www/html/flask/shared/bash/update_base.sh`

---
*Ostatnia aktualizacja: 2026-05-25 00:10
