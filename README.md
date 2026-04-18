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
| **Inwestycje**| `/inwestycje`| `5002` | Portfel inwestycyjny |
| **Zdrowie** | `/zdrowie` | `5003` | Monitoring ciśnienia + HA |

## 💰 Moduł Finanse - Nowe Funkcje (Update 2026-04-18)
- **Bilans:** Automatyczne kolorowanie wartości dodatnich (zielony) i ujemnych (czerwony).
- **Samochód:** - Automatyczne wyliczanie przebiegu miesięcznego na podstawie stanów licznika.
    - Kalkulacja średniego kosztu za 1 km.
- **Wykresy (Chart.js):**
    - 4 interaktywne zakładki: Bilans, Przychody, Wydatki, ROR.
    - Filtrowanie zakresu czasu: 12, 24, 36 miesięcy oraz widok pełny.
    - **Visual Cues:** Czerwone rąby na wykresach liniowych sygnalizują "Uwagi" (po kliknięciu otwiera się modal).
    - **Analityka Pie Chart:** Dynamiczny wykres kołowy średniej z ostatnich 3 miesięcy z etykietami wypchniętymi poza obręb koła dla lepszej czytelności.

## 🛠 Zarządzanie i Logi
- **Restart aplikacji:** `sudo systemctl restart flask-finanse` (lub `flask-zdrowie`)
- **Podgląd błędów:** `sudo journalctl -u flask-finanse -f`
- **Aktualizacja bibliotek:** `pip install -r requirements.txt`

## 💡 Troubleshooting & Refleksje (Update 2026-04-18)
1. **Importy Systemowe:** Przy budowie modułów Flask (`Blueprint`), standardowe biblioteki Pythona (np. `os`, `time`) muszą być importowane niezależnie od paczek Flaska, aby uniknąć błędów typu `ImportError`.
2. **Optymalizacja Wykresów:** Przy dużej ilości małych kategorii na wykresie kołowym, standardowa legenda jest nieczytelna. Zastosowanie wtyczki `datalabels` z parametrami `anchor: end` i `align: end` pozwala na wyprowadzenie etykiet poza koło, co drastycznie poprawia UX.
3. **Formatowanie Walutowe:** Dla czytelności tabel finansowych (szczególnie w module Samochód i Bilans) kluczowe jest stosowanie spacji jako separatora tysięcy i przecinka dla części dziesiętnych.

---
Ostatnia aktualizacja: 2026-04-18 16:45
