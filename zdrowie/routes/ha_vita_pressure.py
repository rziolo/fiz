from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
import os
import requests
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv

# Wymuszenie ładowania zmiennych z pliku .env
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

pressure_bp = Blueprint('pressure', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )

@pressure_bp.route('/pressure')
def list_pressure():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ha_vita_pressure ORDER BY Date DESC")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('ha_vita_pressure.html', rows=rows, tytul_aplikacji='Pomiary Ciśnienia')

@pressure_bp.route('/pressure/create', methods=['GET', 'POST'])
@pressure_bp.route('/pressure/edit/<int:id>', methods=['GET', 'POST'])
@pressure_bp.route('/pressure/view/<int:id>', methods=['GET'])
def manage_pressure(id=None):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    mode = 'create'
    if 'view' in request.path: mode = 'view'
    elif 'edit' in request.path: mode = 'edit'

    row = None
    if id:
        cursor.execute("SELECT * FROM ha_vita_pressure WHERE id_ha_fit = %s", (id,))
        row = cursor.fetchone()

    ha_data = {"locality": "Police", "temp": 0, "pressure": 1013, "humidity": 0}
    
    if mode == 'create':
        try:
            # Czyszczenie zmiennych z cudzysłowów
            url = os.getenv('HOME_ASSISTANT_URL', '').strip('"').strip("'")
            token = os.getenv('HA_TOKEN', '').strip('"').strip("'")
            ow_key = os.getenv('OPENWEATHER_API_KEY', '').strip('"').strip("'")

            if url and token:
                res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    # Zgodnie z Twoim curlem: miasto jest w 'state'
                    ha_data['locality'] = data.get('state') or "Police"
                    
                    if ow_key:
                        ow_url = f"http://api.openweathermap.org/data/2.5/weather?q={ha_data['locality']}&appid={ow_key}&units=metric"
                        ow_res = requests.get(ow_url, timeout=5)
                        if ow_res.status_code == 200:
                            w = ow_res.json()
                            ha_data.update({
                                "temp": round(w['main']['temp']),
                                "pressure": w['main']['pressure'],
                                "humidity": w['main']['humidity']
                            })
        except Exception as e:
            print(f"DEBUG Error fetching weather: {e}")

    if request.method == 'POST':
        d = request.form
        waga = d.get('waga', '0').replace(',', '.')
        if mode == 'create':
            sql = """INSERT INTO ha_vita_pressure (Date, `atmosf.`, P_skurczowe, P_rozkurczowe, Puls, temperatura, wilgotnosc, waga, miasto, uwagi)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (d['Date'], d['atmosf'], d['P_skurczowe'], d['P_rozkurczowe'], d['Puls'], d['temperatura'], d['wilgotnosc'], waga, d['miasto'], d['uwagi']))
        elif mode == 'edit':
            sql = """UPDATE ha_vita_pressure SET Date=%s, `atmosf.`=%s, P_skurczowe=%s, P_rozkurczowe=%s, Puls=%s, temperatura=%s, wilgotnosc=%s, waga=%s, miasto=%s, uwagi=%s
                     WHERE id_ha_fit=%s"""
            cursor.execute(sql, (d['Date'], d['atmosf'], d['P_skurczowe'], d['P_rozkurczowe'], d['Puls'], d['temperatura'], d['wilgotnosc'], waga, d['miasto'], d['uwagi'], id))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('pressure.list_pressure'))

    now = datetime.now(timezone('Europe/Warsaw')).strftime('%Y-%m-%dT%H:%M')
    cursor.close()
    db.close()
    return render_template('ha_vita_pressure_create.html', mode=mode, row=row, ha_data=ha_data, now=now)

@pressure_bp.route('/pressure/delete/<int:id>')
def delete_pressure(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM ha_vita_pressure WHERE id_ha_fit = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('pressure.list_pressure'))

@pressure_bp.route('/pressure/print')
def print_pressure():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ha_vita_pressure ORDER BY Date DESC")
    rows = cursor.fetchall()
    db.close()
    return render_template('ha_vita_pressure_print.html', rows=rows, now=datetime.now())
