#!/usr/bin/env python3
import yfinance as yf
import datetime as dt
import os
import logging
import sys

# Dodanie ścieżki do shared, aby móc zaimportować kursy_nbp
sys.path.append('/var/www/html/flask/shared')
try:
    from kursy_nbp import get_nbp_rates
except ImportError:
    print("Błąd: Nie znaleziono /var/www/html/flask/shared/kursy_nbp.py")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

CSV_DIR = "/var/www/html/flask/inwestycje/etl/csv"
CSV_FILE = os.path.join(CSV_DIR, 'import_zagr.csv')

def download_stock_data(ticker):
    end_date = dt.datetime.today()
    start_date = end_date - dt.timedelta(days=7)
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
        if not data.empty:
            return data.tail(1)
    except Exception as e:
        logger.error(f"❌ Błąd yfinance dla {ticker}: {e}")
    return None

def main():
    # Pobranie kursów z Twojego skryptu shared
    rates = get_nbp_rates()
    eur_rate = rates.get("EUR")
    usd_rate = rates.get("USD")

    if not eur_rate or not usd_rate:
        logger.error("❌ Brak kursów walut z NBP. Przerwanie.")
        return

    assets = [
        {"ticker": "IUSQ.DE", "name": "IUSQ", "full_name": "IUSQ", "is_ticker": "IUSQ", "currency": "EUR", "rate": eur_rate},
        {"ticker": "FER.MC", "name": "Ferrovial", "full_name": "FERROVIAL", "is_ticker": "FER", "currency": "EUR", "rate": eur_rate},
        {"ticker": "PPC.AT", "name": "Public Power", "full_name": "PUBLIC POWER CORP", "is_ticker": "DEH", "currency": "EUR", "rate": eur_rate},
        {"ticker": "PRY.MI", "name": "Prysmian", "full_name": "PRYSMIAN", "is_ticker": "PRY", "currency": "EUR", "rate": eur_rate},
        {"ticker": "ABBV", "name": "AbbVie", "full_name": "ABBVIE", "is_ticker": "ABBV", "currency": "USD", "rate": usd_rate},
        {"ticker": "NVDA", "name": "NVIDIA", "full_name": "NVIDIA", "is_ticker": "NVDA", "currency": "USD", "rate": usd_rate},
        {"ticker": "REXR", "name": "Rexford", "full_name": "REXFORD", "is_ticker": "REXR", "currency": "USD", "rate": usd_rate},
        {"ticker": "TKC", "name": "Turkcell", "full_name": "TURKCELL", "is_ticker": "TKC", "currency": "USD", "rate": usd_rate},
        {"ticker": "BCC", "name": "Boise Cascade", "full_name": "BOISE CASCADE", "is_ticker": "BCC", "currency": "USD", "rate": usd_rate},
        {"ticker": "DHT", "name": "DHT Holdings", "full_name": "DHT HOLDINGS INC", "is_ticker": "DHT", "currency": "USD", "rate": usd_rate}
    ]

    csv_rows = []
    today_str = dt.datetime.now().strftime("%Y-%m-%d")

    for asset in assets:
        df = download_stock_data(asset["ticker"])
        if df is None: continue
        try:
            o_val = df['Open'].iloc[0].item()
            h_val = df['High'].iloc[0].item()
            l_val = df['Low'].iloc[0].item()
            c_val = df['Close'].iloc[0].item()
            v_val = int(df['Volume'].iloc[0].item())

            r = asset["rate"]
            row = [
                today_str, asset["full_name"], asset["is_ticker"], asset["currency"],
                f"{o_val * r:.3f}", f"{h_val * r:.3f}", f"{l_val * r:.3f}", f"{c_val * r:.3f}",
                f"{(h_val - l_val) * r:.3f}", v_val, 1, "1.00"
            ]
            csv_rows.append(row)
        except Exception as e:
            logger.error(f"❌ Błąd danych dla {asset['name']}: {e}")

    if csv_rows:
        os.makedirs(CSV_DIR, exist_ok=True)
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            for row in csv_rows:
                f.write(','.join(map(str, row)) + '\n')
        logger.info(f"🚀 Plik zapisany: {CSV_FILE}")

if __name__ == "__main__":
    main()
