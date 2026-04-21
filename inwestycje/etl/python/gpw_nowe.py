import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = "/var/www/html/flask/inwestycje"
CSV_DIR = os.path.join(BASE_DIR, 'etl/csv')
OUTPUT_FILE = os.path.join(CSV_DIR, 'gpw_nowe.csv')

# Załaduj dane dostępowe do bazy
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )

def get_new_tickers():
    """Porównuje tickery w tabeli 'dane' z tabelą 'ticker'"""
    nowe = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQL wybierający unikalne tickery z 'dane', których nie ma w 'ticker'
        query = """
            SELECT DISTINCT d.ticker 
            FROM dane d 
            LEFT JOIN ticker t ON d.ticker = t.ticker_name 
            WHERE t.ticker_name IS NULL
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        nowe = [row[0].strip() for row in rows if row[0]]
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Błąd bazy danych: {e}")
    return nowe

def main():
    print("🔍 Szukanie nowych spółek w bazie danych (dane vs ticker)...")
    
    nowe_spolki = get_new_tickers()
    
    try:
        # Zapewnij istnienie katalogu na plik wynikowy dla dashboardu
        os.makedirs(CSV_DIR, exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            if nowe_spolki:
                wynik = ', '.join(sorted(nowe_spolki))
                f.write(wynik)
                print(f"✨ Znaleziono nowe spółki w notowaniach: {wynik}")
            else:
                f.write('brak')
                print("✅ Brak nowych spółek. Słownik 'ticker' jest aktualny.")
                
    except Exception as e:
        print(f"❌ Błąd zapisu pliku wynikowego: {e}")

if __name__ == "__main__":
    main()
