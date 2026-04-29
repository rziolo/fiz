# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi.

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived).
- **Load Balancer:** Apache2 z modułem `mod_proxy_balancer`.
- **Logic:** - **Mirroring:** `/inwestycje`, `/finanse`, `/zdrowie` (aplikacje mają prefiksy w kodzie Pythona).
    - **Stripping:** `/aplikacje` (HUB - przekierowanie na korzeń `/` aplikacji).
- **Storage:** GlusterFS (zsynchronizowany wolumen `/var/www/html/flask`).

## 🚀 Wykaz Aplikacji i Portów (Pełne HA)
| Aplikacja | Ścieżka URL | Port Lokalny | Status / Baza Danych |
| :--- | :--- | :--- | :--- |
| **Aplikacje** | `/aplikacje` | 5000 | **HA** (Local Galera) |
| **Finanse** | `/finanse` | 5001 | **HA** (Local Galera) |
| **Inwestycje**| `/inwestycje`| 5002 | **HA** (Local Galera) |
| **Zdrowie** | `/zdrowie` | 5003 | **HA** (SQLite/GlusterFS) |

## 📈 Kluczowe zmiany (28.04.2026)
- **Ujednolicenie Tras:** Dostosowano trasy w `zdrowie.py` (`/zdrowie/`) oraz `inwestycje.py`, aby zapewnić pełną kompatybilność z Proxy Balancerem.
- **Failover:** Pełna redundancja - w przypadku awarii jednego RPi, ruch jest przejmowany przez drugi węzeł w czasie poniżej 1 sekundy.

## 🛠 Zarządzanie
- **Status klastra:** `sudo systemctl status "flask-*"`
- **Logi Apache:** `tail -f /var/log/apache2/access.log`

---
*Ostatnia aktualizacja: 2026-04-30 00:10
