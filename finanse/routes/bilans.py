from flask import Blueprint, render_template
import mysql.connector
import os

bilans_bp = Blueprint('bilans', __name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        autocommit=True
    )

@bilans_bp.route('/')
def list_bilans():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Zapytanie łączące przychody, wydatki i stan kont ror wraz z uwagami
    query = """
    SELECT 
        DATE_FORMAT(p.data, '%Y-%m') as rok_miesiac,
        SUM(p.ZUS_Iwona + p.ZUS_Robert + p.gielda + p.odsetki + p.urzad + p.inne) as przychody,
        p.uwagi as przychody_uwagi,
        (SELECT SUM(zywnosc + niezywnosc + car_cost + oplaty + inne + medycyna) 
         FROM wydatki 
         WHERE DATE_FORMAT(data, '%Y-%m') = DATE_FORMAT(p.data, '%Y-%m')) as wydatki,
        (SELECT uwagi 
         FROM wydatki 
         WHERE DATE_FORMAT(data, '%Y-%m') = DATE_FORMAT(p.data, '%Y-%m')
         LIMIT 1) as wydatki_uwagi,
        (SELECT (PKO + mBank + Millenium + obligacje + fundusze + lokaty + gotowka + ike_ikze + gielda + (EURO * EURO_kurs) + (USD * USD_kurs))
         FROM ror 
         WHERE DATE_FORMAT(data, '%Y-%m') = DATE_FORMAT(p.data, '%Y-%m')
         ORDER BY data DESC LIMIT 1) as ror_total
    FROM przychody p
    GROUP BY rok_miesiac
    ORDER BY rok_miesiac DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    for row in rows:
        # Konwersja na float i obsługa None
        p_val = float(row['przychody'] or 0)
        w_val = float(row['wydatki'] or 0)
        row['przychody'] = p_val
        row['wydatki'] = w_val
        row['bilans'] = p_val - w_val
        row['ror_total'] = float(row['ror_total'] or 0)

    db.close()
    return render_template('bilans.html', rows=rows)
