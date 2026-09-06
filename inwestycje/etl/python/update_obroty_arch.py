import datetime
import mysql.connector
from dotenv import load_dotenv
import os

# Wczytanie zmiennych środowiskowych z pliku .env aplikacji inwestycje
env_path = "/var/www/html/flask/inwestycje/.env"
if os.path.exists(env_path):
    load_dotenv(env_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", os.getenv("DB_PASS", ""))
DB_NAME = os.getenv("DB_NAME", "inwestycje")

def update_obroty_arch():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Zapytanie wybierające rekordy z najwyższym id_obroty dla każdego ticker_nm,
        # gdzie akcja jest nadal aktywna (sprzedaz_data IS NULL)
        select_query = """
            SELECT o.zakup_data, o.ticker_nm, o.stop_loss
            FROM obroty o
            INNER JOIN (
                SELECT ticker_nm, MAX(id_obroty) AS max_id
                FROM obroty
                WHERE sprzedaz_data IS NULL
                GROUP BY ticker_nm
            ) sub ON o.id_obroty = sub.max_id
        """
        cursor.execute(select_query)
        rows = cursor.fetchall()

        if rows:
            today = datetime.date.today()
            insert_query = """
                INSERT INTO obroty_arch (data_arch, zakup_data_arch, ticker_nm, stop_loss)
                VALUES (%s, %s, %s, %s)
            """
            data_to_insert = [(today, zakup_data, ticker_nm, stop_loss) for zakup_data, ticker_nm, stop_loss in rows]
            cursor.executemany(insert_query, data_to_insert)
            conn.commit()
            print(f"[{datetime.datetime.now()}] Dodano {cursor.rowcount} rekordów do obroty_arch.")
        else:
            print(f"[{datetime.datetime.now()}] Brak aktywnych pozycji do zarchiwizowania.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[{datetime.datetime.now()}] Błąd podczas aktualizacji obroty_arch: {e}")

if __name__ == "__main__":
    update_obroty_arch()
