from flask import Blueprint, render_template
import mysql.connector
import os

chart_bp = Blueprint('chart', __name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        autocommit=True
    )

@chart_bp.route('/')
def show_charts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # 1. Dane PRZYCHODY
    cursor.execute("SELECT data, ZUS_Iwona, ZUS_Robert, gielda, odsetki, urzad, inne, uwagi FROM przychody ORDER BY data ASC")
    przychody = cursor.fetchall()

    # 2. Dane WYDATKI
    cursor.execute("SELECT data, zywnosc, niezywnosc, car_cost, oplaty, inne, medycyna, uwagi FROM wydatki ORDER BY data ASC")
    wydatki = cursor.fetchall()

    # 3. Dane ROR (z przeliczeniem walut)
    cursor.execute("""
        SELECT data, PKO, mBank, Millenium, obligacje, fundusze, lokaty, gotowka, ike_ikze, gielda, 
        (EURO * EURO_kurs) as euro_pln, (USD * USD_kurs) as usd_pln, uwagi 
        FROM ror ORDER BY data ASC
    """)
    ror = cursor.fetchall()

    # 4. Dane BILANS
    cursor.execute("""
        SELECT 
            DATE_FORMAT(p.data, '%Y-%m') as miesiac,
            SUM(p.ZUS_Iwona + p.ZUS_Robert + p.gielda + p.odsetki + p.urzad + p.inne) as p_sum,
            (SELECT SUM(zywnosc + niezywnosc + car_cost + oplaty + inne + medycyna) 
             FROM wydatki WHERE DATE_FORMAT(data, '%Y-%m') = miesiac) as w_sum
        FROM przychody p GROUP BY miesiac ORDER BY miesiac ASC
    """)
    bilans_raw = cursor.fetchall()
    bilans = []
    for b in bilans_raw:
        p = float(b['p_sum'] or 0)
        w = float(b['w_sum'] or 0)
        bilans.append({
            "data": b['miesiac'],
            "przychody": p,
            "wydatki": w,
            "wynik": p - w
        })

    db.close()
    
    # Konwersja dat na stringi dla JSON (bezpieczeństwo serializacji)
    for ds in [przychody, wydatki, ror]:
        for row in ds:
            if 'data' in row and row['data']:
                row['data'] = row['data'].strftime('%Y-%m-%d')

    return render_template('chart.html', przychody=przychody, wydatki=wydatki, ror=ror, bilans=bilans)
