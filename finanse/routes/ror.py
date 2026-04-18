from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector, os, datetime, sys

# Ścieżka do shared dla kursów NBP
sys.path.append('/var/www/html/flask/shared')
try:
    from kursy_nbp import get_nbp_rates
except ImportError:
    def get_nbp_rates(): return {"USD": "0.00", "EUR": "0.00"}

ror_bp = Blueprint('ror', __name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        autocommit=True
    )

@ror_bp.route('/')
def list_ror():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Pobieramy pełny zestaw danych dla tabeli ror.html
    cursor.execute("""
        SELECT id_ror, data, PKO, mBank, Millenium, obligacje, fundusze, 
               lokaty, gotowka, ike_ikze, gielda, EURO, EURO_kurs, USD, USD_kurs, uwagi 
        FROM ror ORDER BY data DESC
    """)
    rows = cursor.fetchall()
    db.close()
    return render_template('ror.html', rows=rows)

@ror_bp.route('/manage', defaults={'id': None}, methods=['GET', 'POST'])
@ror_bp.route('/manage/<int:id>', methods=['GET', 'POST'])
def manage(id):
    mode = request.args.get('mode', 'edit' if id else 'create')
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        d = request.form
        # Lista wszystkich pól zgodnie ze strukturą tabeli ror
        fields = ['data', 'PKO', 'mBank', 'Millenium', 'obligacje', 'fundusze', 
                  'lokaty', 'gotowka', 'ike_ikze', 'gielda', 'EURO', 'EURO_kurs', 
                  'USD', 'USD_kurs', 'uwagi']
        
        # Przygotowanie wartości (konwersja separatorów i obsługa pustych pól)
        vals = []
        for f in fields:
            val = d.get(f, '0' if f not in ['data', 'uwagi'] else '')
            if f not in ['data', 'uwagi']:
                val = str(val).replace(',', '.')
            vals.append(val)

        if id:
            # Aktualizacja istniejącego wpisu
            set_clause = ", ".join([f"{f}=%s" for f in fields])
            sql = f"UPDATE ror SET {set_clause} WHERE id_ror=%s"
            cursor.execute(sql, vals + [id])
        else:
            # Wstawianie nowego wpisu
            cols = ", ".join(fields)
            placeholders = ", ".join(["%s"] * len(fields))
            sql = f"INSERT INTO ror ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, vals)
        
        db.close()
        return redirect(url_for('ror.list_ror'))

    # Logika dla metody GET (ładowanie formularza)
    row = None
    if id:
        cursor.execute("SELECT * FROM ror WHERE id_ror = %s", (id,))
        row = cursor.fetchone()
    
    # Inicjalizacja dla nowego wpisu (kursy NBP i dzisiejsza data)
    if not row:
        rates = get_nbp_rates()
        row = {
            'data': datetime.date.today().strftime('%Y-%m-%d'),
            'EURO_kurs': rates.get('EUR', '0.00'),
            'USD_kurs': rates.get('USD', '0.00')
        }
        # Domyślne zera dla pól numerycznych
        for col in ['PKO', 'mBank', 'Millenium', 'obligacje', 'fundusze', 
                    'lokaty', 'gotowka', 'ike_ikze', 'gielda', 'EURO', 'USD']:
            row[col] = '0.00'

    db.close()
    return render_template('ror_create.html', mode=mode, row=row)

@ror_bp.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM ror WHERE id_ror = %s", (id,))
    db.close()
    return redirect(url_for('ror.list_ror'))
