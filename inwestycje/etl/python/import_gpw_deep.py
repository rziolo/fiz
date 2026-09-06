#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import os
import logging
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_CSV = "/var/www/html/flask/inwestycje/etl/csv/import_gpw.csv"
OUTPUT_CSV = "/var/www/html/flask/inwestycje/etl/csv/import_gpw_deep.csv"
TICKERS_LIST_URL = "https://api.gpw.pl/api/lista_spolek?format=csv"  # przykładowy (może nie działać)
# Alternatywnie: użyjemy własnej mapy lub pobierzemy z pliku lokalnego

# Jeśli powyższe nie działa, przygotowałem mapę ręczną dla najpopularniejszych
MANUAL_MAP = {
    "PKOBP": "PKO",
    "PEKAO": "PEO",
    "PKNORLEN": "PKN",
    "KGHM": "KGH",
    "CDPROJEKT": "CDR",
    "PZU": "PZU",
    "ALLEGRO": "ALLEGRO",
    "DINOPL": "DINO",
    "MBANK": "MBK",
    "SANPL": "SPL",
    "MILLENNIUM": "MIL",
    "INGBSK": "ING",
    "HANDLOWY": "BHW",
    "BOS": "BOS",
    "BUDIMEX": "BDX",
    "KRUK": "KRU",
    "LPP": "LPP",
    "CCC": "CCC",
    "EUROCASH": "EUR",
    "GRUPAAZOTY": "ATT",
    "JSW": "JSW",
    "TAURONPE": "TPE",
    "ENERGA": "ENG",
    "ENEA": "ENA",
    "PGE": "PGE",
    "ORANGEPL": "OPL",
    "CYFRPLSAT": "CPS",
    "GPW": "GPW",
    "ASBIS": "ASB",
    "INTERCARS": "ICS",
    "AMICA": "AMC",
    "APATOR": "APR",
    "BORYSZEW": "BRY",
    "COGNOR": "COG",
    "DECORA": "DCR",
    "FERRO": "FER",
    "GRODNO": "GRN",
    "KETY": "KTY",
    "MABION": "MAB",
    "MIRBUD": "MRB",
    "MOSTALPLC": "MSP",
    "MOSTALWAR": "MSW",
    "MOSTALZAB": "MSZ",
    "NEUCA": "NCA",
    "PCCROKITA": "PCR",
    "POLIMEXMS": "PXM",
    "RAINBOW": "RBT",
    "SANOK": "SNK",
    "SNIEZKA": "SKA",
    "STALPROD": "STP",
    "TRAKCJA": "TRK",
    "UNIMOT": "UMT",
    "VINDEXUS": "VDX",
    "WIRTUALNA": "WRT",
    "XTB": "XTB",
    "ZEPAK": "ZPK",
    "ZUE": "ZUE",
    "AMREST": "AMR",
    "ATAL": "ATL",
    "BENEFIT": "BFT",
    "BIOTON": "BIO",
    "CLOUD": "CLD",
    "COMP": "CMP",
    "DATAWALK": "DWT",
    "DEVELIA": "DVL",
    "ECHO": "ECH",
    "ERBUD": "ERB",
    "GRUPRACUJ": "GRC",
    "IMMOBILE": "IMB",
    "INSTALKRK": "INK",
    "KINOPOL": "KPL",
    "KRVITAMIN": "KVT",
    "LENTEX": "LTX",
    "MARVIPOL": "MRV",
    "MERCATOR": "MRC",
    "MOLECURE": "MLC",
    "MURAPOL": "MUR",
    "OPONEO.PL": "OPN",
    "PASSUS": "PAS",
    "PCFGROUP": "PCF",
    "PHN": "PHN",
    "PLAYWAY": "PLW",
    "PROTEKTOR": "PRT",
    "PTWP": "PTW",
    "SELENAFM": "SEL",
    "SNTVERSE": "SNT",
    "SYNEKTIK": "SNX",
    "TALEX": "TLX",
    "TEXT": "TXT",
    "TORPOL": "TRP",
    "TOYA": "TOY",
    "UNIBEP": "UNI",
    "VERCOM": "VRC",
    "VOTUM": "VOT",
    "VRG": "VRG",
    "WAWEL": "WWL",
    "WIELTON": "WLT",
    "WITTCHEN": "WTC",
    "ZABKA": "ZAB"
}

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_yahoo_ticker(nazwa):
    """Zwraca ticker dla Yahoo Finance (z .WA lub z mapy)"""
    # Najpierw sprawdź mapę ręczną
    if nazwa in MANUAL_MAP:
        return MANUAL_MAP[nazwa] + ".WA"
    # Inaczej dodaj .WA i wierz w najlepsze
    return nazwa + ".WA"

def fetch_stock_data(nazwa):
    yf_ticker = get_yahoo_ticker(nazwa)
    try:
        ticker_obj = yf.Ticker(yf_ticker)
        hist = ticker_obj.history(period="2d")
        if hist.empty:
            logger.warning(f"Brak danych dla {nazwa} ({yf_ticker}) – być może zły ticker")
            return (0.0, 0.0, 0.0, 0.0, 0, 0.0)
        
        last = hist.iloc[-1]
        open_p = last['Open']
        high_p = last['High']
        low_p = last['Low']
        close_p = last['Close']
        volume = int(last['Volume']) if not pd.isna(last['Volume']) else 0

        change_pct = 0.0
        if len(hist) >= 2:
            prev_close = hist.iloc[-2]['Close']
            if prev_close != 0:
                change_pct = (close_p - prev_close) / prev_close * 100

        return (open_p, high_p, low_p, close_p, volume, change_pct)
    except Exception as e:
        logger.error(f"Błąd dla {nazwa}: {e}")
        return (0.0, 0.0, 0.0, 0.0, 0, 0.0)

def main():
    logger.info("Pobieranie notowań GPW (Yahoo Finance) z mapowaniem tickerów")

    if not os.path.exists(INPUT_CSV):
        logger.error(f"Brak pliku: {INPUT_CSV}")
        sys.exit(1)

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not rows:
        logger.error("Pusty plik wejściowy")
        sys.exit(1)

    today_str = datetime.today().strftime('%Y-%m-%d')
    output_rows = []

    for idx, row in enumerate(rows, start=1):
        nazwa = row.get('Nazwa', '').strip()
        if not nazwa:
            continue

        logger.info(f"{idx}/{len(rows)}: {nazwa}")
        open_p, high_p, low_p, close_p, volume, change_pct = fetch_stock_data(nazwa)
        turnover = (volume * close_p) / 1000.0 if close_p != 0 else 0.0

        new_row = row.copy()
        new_row['Data'] = today_str
        new_row['Kurs otwarcia'] = f"{open_p:.2f}" if open_p else "0.00"
        new_row['Kurs max'] = f"{high_p:.2f}" if high_p else "0.00"
        new_row['Kurs min'] = f"{low_p:.2f}" if low_p else "0.00"
        new_row['Kurs zamknięcia'] = f"{close_p:.2f}" if close_p else "0.00"
        new_row['Zmiana'] = f"{change_pct:.2f}"
        new_row['Wolumen'] = str(volume)
        new_row['Liczba Transakcji'] = "0"
        new_row['Obrót'] = f"{turnover:.2f}"

        output_rows.append(new_row)

    ensure_directory_exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        writer.writerows(output_rows)

    logger.info(f"Zapisano {len(output_rows)} wierszy do {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
