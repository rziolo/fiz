# 🍓 Klaster RPi 05/06 (Galera & GlusterFS)

Repozytorium zawierające kluczowe pliki konfiguracyjne oraz monitoring klastra wysokiej dostępności (HA).

## 🏗️ Architektura
Klaster działa w trybie Active-Passive dla usług sieciowych (Keepalived) oraz Multi-Master dla bazy danych (Galera).

* **Węzeł 1:** `rz-rpi-05` (192.168.1.133) - Przedpokój
* **Węzeł 2:** `rz-rpi-06` (192.168.1.147) - Średni pokój (Master ETL/Backup)
* **Wirtualne IP (VIP):** `192.168.1.156` (Zarządzane przez `keepalived`) - Główny punkt dostępu.

### 🕒 Harmonogram Zadań (Cron)
Zadania automatyzacji są scentralizowane na węźle **rz-rpi-06**, aby uniknąć konfliktów zapisu na wolumenie GlusterFS i blokad (deadlocks) w klastrze Galera:
* **00:05/10:** Backupy konfiguracji i aplikacji do GitHub.
* **00:20:** Zerowanie statusów dziennych (GPW Archiwum).
* **18:20:** Import danych giełdowych (ETL).

### Usługi:
* **Serwer WWW:** Apache2 działający jako Reverse Proxy dla mikroserwisów.
* **Baza danych:** MariaDB Galera Cluster (Synchronizacja Multi-Master dla aplikacji Flask).
* **Pliki (Storage):** GlusterFS (Wolumen `gv_www` w `/var/www/html`). Zapewnia spójność kodu aplikacji między węzłami.
* **Mikroserwisy Flask:**
    - `/aplikacje` (Port 5000) - Hub
    - `/finanse` (Port 5001) - Bilans, Samochód, Wykresy.
    - `/inwestycje` (Port 5002) - Pełny moduł portfela, ETL GPW (.xls), Rotacja plików.
    - `/zdrowie` (Port 5003) - Rejestracja ciśnienia + integracja z HA.

## 🔧 Rozwiązane problemy (Knowledge Base)
* **Python Imports (04.2026):** Naprawiono błędy `ImportError` przy Blueprintach (niezależny import bibliotek systemowych).
* **Uniwersalne Formularze:** Wdrożono mechanizm `mode='view|edit|create'` (jeden plik .html dla wielu akcji).
* **Relacyjne Dropdowny:** Dynamiczne listy wyboru z baz danych zamiast ręcznego wpisywania nazw.
* **Zarządzanie Przestrzenią (04.2026):** Wdrożono automatyczną rotację plików binarnych (.xls) w module Inwestycje (zachowanie 5 ostatnich sesji).
* **Wizualizacja danych:** Optymalizacja czytelności Chart.js na mobile (datalabels anchor/align).

## 📊 Monitoring (Home Assistant)
Status klastra raportowany do HA przez SSH:
* **Lider VIP:** Wykrywanie aktywnego węzła obsługującego `192.168.1.156`.
* **Integracja HA -> Flask:** Aplikacja Zdrowie pobiera dane pogodowe z encji HA.

---
*Ostatnia aktualizacja: 22.04.2026 (Scentralizowanie zadań Cron na rz-rpi-06, aktualizacja logiki ETL)*
