from flask import Blueprint, render_template
import mysql.connector
import os

car_bp = Blueprint('car', __name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        autocommit=True
    )

@car_bp.route('/')
def list_car():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
    SELECT 
        DATE_FORMAT(data, '%Y-%m') as miesiac,
        SUM(car_cost) as koszt_zl,
        MAX(car_km) as stan_licznika
    FROM wydatki
    WHERE car_cost > 0 OR car_km > 0
    GROUP BY miesiac
    ORDER BY miesiac DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Obliczenia przebiegu i kosztu/km
    for i in range(len(rows)):
        current = rows[i]
        # Pobieramy poprzedni stan (następny w liście DESC)
        prev_stan = rows[i+1]['stan_licznika'] if i+1 < len(rows) else current['stan_licznika']
        
        current['poprzedni_stan'] = prev_stan
        current['przebieg'] = current['stan_licznika'] - prev_stan
        
        if current['przebieg'] > 0:
            current['koszt_km'] = float(current['koszt_zl'] or 0) / current['przebieg']
        else:
            current['koszt_km'] = 0

    db.close()
    return render_template('car.html', rows=rows)
