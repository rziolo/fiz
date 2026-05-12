#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import requests
from bs4 import BeautifulSoup
import datetime

# Ścieżki plików
INPUT_FILE = "/var/www/html/flask/inwestycje/etl/csv/import_gpw.csv"
OUTPUT_FILE = "/var/www/html/flask/inwestycje/etl/csv/import_gpw_chatgpt.csv"

BANKIER_URL = "https://www.bankier.pl/inwestowanie/notowania/akcje/{ticker}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}


def get_stock_data(ticker):
    url = BANKIER_URL.format(ticker=ticker)
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    try:
        price = soup.find("span", {"data-test": "instrument-price-last"}).text.strip().replace(" ", "")
        change = soup.find("span", {"data-test": "instrument-price-change-percent"}).text.strip()
        volume = soup.find("td", {"data-test": "volume"}).text.strip().replace(" ", "")
    except Exception:
        return None

    return {
        "price": price,
        "change": change,
        "volume": volume
    }


def load_companies():
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        # tu poprawka: CSV ma separator przecinek!
        reader = csv.DictReader(f, delimiter=",")
        companies = list(reader)
        fieldnames = reader.fieldnames
    return companies, fieldnames


def save_output(data, fieldnames):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
        writer.writeheader()
        writer.writerows(data)


def main():
    print("⏳ Start ETL GPW z Bankier.pl...")

    companies, fieldnames = load_companies()

    # Nowe kolumny
    for col in ["date", "price", "change", "volume"]:
        if col not in fieldnames:
            fieldnames.append(col)

    output_rows = []
    today = datetime.date.today().isoformat()

    for row in companies:
        # ticker = nazwa spółki
        ticker = row["Nazwa"].split()[0].upper()

        print(f"  → Pobieram dane: {ticker}")

        data = get_stock_data(ticker)

        row["date"] = today
        if data:
            row["price"] = data["price"]
            row["change"] = data["change"]
            row["volume"] = data["volume"]
        else:
            row["price"] = ""
            row["change"] = ""
            row["volume"] = ""

        output_rows.append(row)

    save_output(output_rows, fieldnames)

    print(f"✅ Zakończono. Plik zapisany: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
