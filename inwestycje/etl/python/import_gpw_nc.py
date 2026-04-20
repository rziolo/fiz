#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

def fetch_scanway_data():
    url = "https://www.biznesradar.pl/notowania/SCW"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {
            "data": datetime.now().strftime("%Y-%m-%d"),
            "nazwa": "SCANWAY",
            "isin": "SCW",
            "waluta": "PLN",
            "kurs_otwarcia": soup.find("span", {"class": "q_ch_open"}).get_text(strip=True).replace(",", "."),
            "kurs_max": soup.find("span", {"class": "q_ch_max"}).get_text(strip=True).replace(",", "."),
            "kurs_min": soup.find("span", {"class": "q_ch_min"}).get_text(strip=True).replace(",", "."),
            "kurs_zamkniecia": soup.find("span", {"class": "q_ch_act"}).get_text(strip=True).replace(",", "."),
            "zmiana": soup.find("span", {"class": "q_ch_pkt"}).get_text(strip=True).replace(",", ".").replace("(", "").replace(")", ""),
            "wolumen": soup.find("span", {"class": "q_ch_vol"}).get_text(strip=True).replace(" ", ""),
            "transakcje": soup.find("span", {"class": "q_ch_trnr"}).get_text(strip=True).replace(" ", ""),
            "obrot": soup.find("span", {"class": "q_ch_mc"}).get_text(strip=True).replace(" ", "")
        }

        # Konwersja i formatowanie
        kurs_otwarcia = float(data["kurs_otwarcia"])
        kurs_max = float(data["kurs_max"])
        kurs_min = float(data["kurs_min"])
        kurs_zamkniecia = float(data["kurs_zamkniecia"])
        zmiana = float(data["zmiana"])
        wolumen = int(data["wolumen"])
        liczba_transakcji = int(data["transakcje"])
        obrot_tys = float(data["obrot"]) / 1000

        csv_path = "/var/www/html/flask/inwestycje/etl/csv/import_gpw_nc.csv"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow([
                data["data"], data["nazwa"], data["isin"], data["waluta"],
                f"{kurs_otwarcia:.3f}", f"{kurs_max:.3f}", f"{kurs_min:.3f}",
                f"{kurs_zamkniecia:.3f}", f"{zmiana:.3f}",
                wolumen, liczba_transakcji, f"{obrot_tys:.2f}"
            ])
        print(f"Dane zapisane do: {csv_path}")
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    fetch_scanway_data()
