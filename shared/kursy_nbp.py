#!/usr/bin/env python3
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_nbp_rates():
    """Pobiera kursy walut USD, AUD, CAD, EUR, GBP z NBP"""
    currencies = ["USD", "AUD", "CAD", "EUR", "GBP"]
    rates = {}
    for code in currencies:
        url = f"http://api.nbp.pl/api/exchangerates/rates/A/{code}/"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates[code] = round(data["rates"][0]["mid"], 4)
            logger.info(f"✅ Pobrano {code}: {rates[code]}")
        except Exception as e:
            logger.error(f"❌ Błąd dla {code}: {e}")
            rates[code] = None
    return rates

if __name__ == "__main__":
    print(get_nbp_rates())
