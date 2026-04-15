# Moje Aplikacje - Klaster Flask HA

System mikroserwisów oparty na Flasku, działający w architekturze wysokiej dostępności (High Availability) na klastrze Raspberry Pi (**rz-rpi-05** i **rz-rpi-06**).

## 🏗 Architektura Systemu
- **Adres VIP:** `192.168.1.156` (zarządzany przez Keepalived)
- **Reverse Proxy:** Apache2 (mod_proxy)
- **Storage:** GlusterFS (folder `/var/www/html/flask`)
- **WSGI Server:** Gunicorn działający wewnątrz Systemd

## 🚀 Wykaz Aplikacji i Portów
| Aplikacja  | Ścieżka URL   | Port Lokalny |
|------------|---------------|--------------|
| **Aplikacje** | `/aplikacje`  | `5000`       |
| **Finanse** | `/finanse`    | `5001`       |
| **Inwestycje**| `/inwestycje` | `5002`       |
| **Zdrowie** | `/zdrowie`    | `5003`       |

## 🛠 Zarządzanie
- Restart usługi: `sudo systemctl restart flask-nazwa`
- Status: `systemctl status flask*`

## 🔄 Backup
Automatyczny commit o 00:10 do `github.com/rziolo/flask_aplikacje`.

---
Ostatnia aktualizacja: 2026-04-15 13:42
