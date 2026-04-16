# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi (**rz-rpi-05** i **rz-rpi-06**).

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived)
- **Reverse Proxy:** Apache2 (mod_proxy) z przekierowaniem ścieżek (`/zdrowie` -> `port 5003`)
- **Storage:** GlusterFS (zsynchronizowany folder `/var/www/html/flask`)
- **WSGI Server:** Gunicorn zarządzany przez Systemd

## 🚀 Wykaz Aplikacji i Portów
| Aplikacja | Ścieżka URL | Port Lokalny | Status / Funkcje |
| :--- | :--- | :--- | :--- |
| **Aplikacje** | `/aplikacje` | `5000` | HUB - Menu Główne |
| **Finanse** | `/finanse` | `5001` | Zarządzanie budżetem |
| **Inwestycje**| `/inwestycje`| `5002` | Portfel inwestycyjny |
| **Zdrowie** | `/zdrowie` | `5003` | **Aktywna**: Monitoring ciśnienia + Integracja HA |

## 💉 Moduł Zdrowie - Funkcje
- Rejestracja pomiarów ciśnienia i pulsu.
- **Automatyczna integracja:** Pobieranie danych pogodowych (temp, ciśnienie, wilgotność) z Home Assistant podczas dodawania pomiaru.
- Interaktywna historia z okienkami modalnymi dla uwag.
- System generowania wydruków dla lekarza.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-zdrowie`
- **Podgląd błędów:** `sudo journalctl -u flask-zdrowie -f`
- **Konfiguracja Apache:** `/etc/apache2/sites-enabled/000-default.conf`

## 🔄 Synchronizacja i Backup
- Kod przechowywany na wspólnym wolumenie GlusterFS.
- Automatyczny commit o 00:10 do `github.com/rziolo/flask_aplikacje`.

---
Ostatnia aktualizacja: 2026-04-16 19:50 (Poprawki UI i struktury URL)
