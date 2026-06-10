# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi.

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived).
- **Load Balancer:** Apache2 z modułem `mod_proxy_balancer`.
- **Logic:**
    - **Mirroring:** `/inwestycje`, `/finanse`, `/zdrowie` (aplikacje mają prefiksy w kodzie Pythona).
    - **Stripping:** `/aplikacje` (HUB - przekierowanie na korzeń `/` aplikacji).
- **Storage:** GlusterFS (zsynchronizowany wolumen `/var/www/html/html` podpięty pod `/var/www/html`).
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

## 📈 Kluczowe zmiany i poprawki (Knowledge Base - App)
- **Korekta mnożników walutowych ETL (28.05.2026):** Naprawiono problem błędnych wartości cenowych w module Inwestycji. Ponieważ biblioteka `yfinance` dla wybranych instrumentów europejskich (np. `U3O8.DE` - VanEck Uranium na Xetra) domyślnie zwraca wartości w centach zamiast w EUR, zmodyfikowano `import_zagr.py`. Wdrożono precyzyjne pobieranie pól przez słownik `.to_dict()` oraz wprowadzono parametr `"mult"` (mnożnik jednostkowy), zapewniając prawidłowe przeliczenia na PLN.
- **Obsługa awarii sprzętowej dysku i I/O (26.05.2026):** Usunięto krytyczny błąd blokady operacji wejścia/wyjścia na węźle `rz-rpi-06` spowodowany degradacją kabla USB/SATA. Wymieniono okablowanie, stabilizując zasilanie dysku SSD.
- **Naprawa systemu plików i logicznego storage (26.05.2026):** Przeprowadzono naprawę uszkodzonych i-węzłów za pomocą `fsck`, odtworzono brakujący punkt montowania `/var/www/html` dla GlusterFS oraz przywrócono poprawną lokalizację partycji `/dev/sda1` w `/mnt/ssd` na potrzeby skryptu zdrowia klastra.
- **Centrum Monitoringu w HUB-ie (24.05.2026):** Do panelu głównego `/aplikacje` dodano piąty kafelek "Sprzęt" linkujący do zewnętrznego systemu `lan_glances` na `rz-rpi-02` (`/mon/`), agregującego teledane z klastra, urządzeń mobilnych i Home Assistant.
- **Optymalizacja Grid UI (24.05.2026):** Przebudowano układ siatki na stronie głównej HUB-u przy użyciu klas `row-cols-xl-5` oraz Flexbox, zapewniając idealne wyrównanie przycisków i płynne skalowanie (PC / tablet / smartfon).
- **Automatyzacja Szablonów (Crontab):** Wdrożono skrypt bash `/var/www/html/flask/shared/bash/update_base.sh` uruchamiany codziennie o 00:25, automatycznie synchronizujący nadrzędny plik `base.html` do modułu Finansów.

## 🛠 Zarządzanie
- **Montowanie zasobów klastra:** `sudo mount -t glusterfs localhost:/gvol0 /var/www/html`
- **Restart wszystkich usług:** `sudo systemctl restart flask-aplikacje flask-finanse flask-inwestycje flask-zdrowie`
- **Status klastra i aplikacji:** `sudo systemctl status "flask-*"` lub `~/klaster-rpi0506/check_disk_health.sh`
- **Logi Apache:** `tail -f /var/log/apache2/access.log`
- **Test JSON HA:** `python3 /var/www/html/flask/finanse/etl/python/get_finanse_json.py`
- **Ręczna synchronizacja szablonu:** `/bin/bash /var/www/html/flask/shared/bash/update_base.sh`

---

## 🔗 Powiązane komponenty i infrastruktura
* **Konfiguracja sprzętowa i sieciowa klastra HA:** Dokumentacja konfiguracji GlusterFS, Galera, Keepalived oraz skryptów monitorujących zdrowie dysków znajduje się pod ścieżką: `/home/rz-rpi-06/klaster-rpi0506/README.md`

---
*Ostatnia aktualizacja: 2026-06-11 00:10
