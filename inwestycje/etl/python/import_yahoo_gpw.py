import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Ścieżki do plików
BASE_FILE = "/var/www/html/flask/inwestycje/etl/csv/import_gpw.csv"
OUTPUT_FILE = "/var/www/html/flask/inwestycje/etl/csv/import_yahoo_gpw.csv"

def main():
    if not os.path.exists(BASE_FILE):
        print(f"Błąd: Plik bazowy {BASE_FILE} nie istnieje.")
        return

    # 1. Wczytujemy dane z wczorajszego pliku
    df_base = pd.read_csv(BASE_FILE)
    
    # Tworzymy mapowania: ISIN -> Nazwa oraz Nazwa -> ISIN
    names_dict = dict(zip(df_base['ISIN'], df_base['Nazwa']))
    
    results = []
    today = datetime.now().strftime('%Y-%m-%d')

    print(f"Przetwarzanie {len(df_base)} spółek...")

    for _, row in df_base.iterrows():
        isin = row['ISIN']
        nazwa = row['Nazwa']
        
        # Próba dopasowania tickera Yahoo
        # 1. Najpierw próbujemy Symbol.WA (najbezpieczniejsze dla GPW)
        # 2. Potem ISIN (może zwrócić inne rynki/waluty)
        
        success = False
        # Lista tickerów do sprawdzenia dla danego wiersza
        tickers_to_try = [f"{nazwa}.WA", isin]
        
        # Specjalna poprawka dla skróconych nazw w pliku bazowym (np. 11BIT -> 11B.WA)
        if nazwa == "11BIT": tickers_to_try.insert(0, "11B.WA")
        if nazwa == "WARIMPEX": tickers_to_try = ["WX.WA"] # Bezpośredni ticker Warimpex na GPW
        
        for ticker in tickers_to_try:
            try:
                t_obj = yf.Ticker(ticker)
                hist = t_obj.history(period="2d")
                
                if not hist.empty:
                    # Sprawdzamy walutę - jeśli Yahoo zwraca EUR dla spółki z GPW, szukamy dalej
                    currency = t_obj.fast_info.get('currency', 'PLN')
                    if currency != 'PLN' and ticker == isin:
                        continue
                        
                    px = hist.iloc[-1]
                    prev = hist.iloc[-2]['Close'] if len(hist) > 1 else px['Open']
                    
                    results.append({
                        "Data": today,
                        "Nazwa": names_dict[isin],
                        "ISIN": isin,
                        "Waluta": "PLN",
                        "Kurs otwarcia": round(px['Open'], 3),
                        "Kurs max": round(px['High'], 3),
                        "Kurs min": round(px['Low'], 3),
                        "Kurs zamknięcia": round(px['Close'], 3),
                        "Zmiana": round(((px['Close'] - prev) / prev) * 100, 2),
                        "Wolumen": int(px['Volume']),
                        "Liczba Transakcji": 0,
                        "Obrót": round((px['Close'] * px['Volume']) / 1000, 2)
                    })
                    success = True
                    break
            except:
                continue
                
        if not success:
            print(f"Ostrzeżenie: Brak danych dla {nazwa} ({isin})")

    if results:
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print(f"Sukces: Zapisano {len(results)} spółek.")

if __name__ == "__main__":
    main()
