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
- **Udogodnienia:** Obsługa wprowadzania wagi z przecinkiem (automatyczna konwersja na kropkę dla DB).

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-zdrowie`
- **Podgląd błędów:** `sudo journalctl -u flask-zdrowie -f`
- **Czyszczenie cache Pythona:** `sudo find . -name "*.pyc" -delete && sudo find . -name "__pycache__" -delete`

## 💡 Troubleshooting & Refleksje (Update 2026-04-17)
### 🌐 Problemy z Cache i Routingiem
1. **Przeglądarka vs Zmiany w HTML:** Przy modyfikacji szablonów Jinja2, przeglądarki agresywnie cache'ują kod HTML/CSS. Po wdrożeniu zmian zawsze wymuszaj odświeżenie przez **Ctrl + F5**.
2. **Jawny Routing (Explicit Paths):** W architekturze z Reverse Proxy, funkcja `url_for` może generować błędy przy przechodzeniu między trybami `view` a `edit`. Bezpieczniejszą metodą dla akcji w tabelach okazało się stosowanie bezpośrednich ścieżek URL (np. `/zdrowie/pressure/edit/...`).
3. **JS jako "Bezpiecznik":** Jeśli logika serwerowa niepoprawnie rozpoznaje tryb strony (np. przez błąd przekierowania proxy), skrypty po stronie klienta (JS) weryfikujące `window.location.pathname` są ostatecznym sposobem na wymuszenie poprawnego UI (np. pokazanie przycisku Zapisz).

---
Ostatnia aktualizacja: 2026-04-18 00:10
