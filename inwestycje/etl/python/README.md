# 🍓 Klaster RPi 05/06 (Galera & GlusterFS)

Repozytorium zawierające kluczowe pliki konfiguracyjne oraz monitoring klastra wysokiej dostępności (HA).

## 🏗️ Architektura
Klaster działa w trybie Active-Passive dla VIP (Keepalived) oraz Active-Active dla usług (Apache Load Balancer + Galera).

* **Wirtualne IP (VIP):** `192.168.1.156`
* **Węzeł 1:** `rz-rpi-05` (192.168.1.133)
* **Węzeł 2:** `rz-rpi-06` (192.168.1.147) - **Preferowany Lider**

---

## 🔧 Rozwiązane problemy (Knowledge Base)
* **Awaria USB/SSD & Stale Mount GlusterFS (28.05.2026):** Wykryto nagłe odłączenie kontrolera JMicron pod USB (błąd zasilania/I/O superblock). Spowodowało to zablokowanie zasobów i przejście ext4 w tryb Read-Only (`Permission denied`). Rozwiązanie: naprawa struktury przez `fsck.ext4 -y /dev/sda1`, wyczyszczenie zawieszonego punktu montowania GlusterFS za pomocą lazy umount (`sudo umount -l /var/www/html`) oraz restart `glusterd`.
* **Korekta Jednostek Giełdowych ETL (28.05.2026):** Rozwiązano problem zniekształconych danych w pliku `import_zagr.csv`. Biblioteka `yfinance` dla wybranych ETF-ów (np. VanEck Uranium na Xetrze) zwraca notowania w centach zamiast w EUR. Wdrożono jawne mapowanie kolumn za pomocą słownika (`.to_dict()`) oraz wprowadzono parametr `"mult"` (mnożnik) w konfiguracji zasobów Pythona w celu wyrównania cen do bazy PLN.
* **High Availability (28.04.2026):** Naprawiono brak dostępności usług przy awarii węzła poprzez wdrożenie `balancer://cluster` w Apache.
* **Routing URL (28.04.2026):** Rozwiązano problem błędów 404 poprzez dopasowanie logiki `ProxyPass` (Mirror dla Inwestycji/Finansów/Zdrowia oraz Stripping dla HUB-a).
* **Network Bind:** Zmieniono adresy nasłuchiwania Gunicorna z `127.0.0.1` na `0.0.0.0`, aby umożliwić Apache dostęp do instancias aplikacji na obu węzłach.
* **Gunicorn Timeout:** Ustawiono `--timeout 120` dla wszystkich mikroserwisów, eliminując błędy 502/503 przy ciężkich zapytaniach SQL w klastrze Galera.

---

## 📊 Monitoring i Automatyzacja
* **Lider VIP:** Raportowanie aktywnego węzła do Home Assistant.
* **Backup:** `mysql_backup_klaster.sh` na rz-rpi-06 (02:00) zapisuje dane na udział TP-Link.
* **Cron:** Harmonogram ETL Inwestycje zoptymalizowany pod kątem obciążenia klastra.

---

*Ostatnia aktualizacja: 28.05.2026 (Naprawa awarii I/O SSD, reset GlusterFS oraz aktualizacja ETL)*
