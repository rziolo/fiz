from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
import os
import requests
from datetime import datetime
from pytz import timezone

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
            ha_res = requests.get(os.getenv('HOME_ASSISTANT_URL'), 
                                headers={"Authorization": f"Bearer {os.getenv('HA_TOKEN')}"}, 
                                verify=False, timeout=2)
            if ha_res.status_code == 200:
                attr = ha_res.json().get('attributes', {})
                ha_data['locality'] = attr.get('locality') or attr.get('city') or "Police"
            
            ow_res = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={ha_data['locality']}&appid={os.getenv('OPENWEATHER_API_KEY')}&units=metric", timeout=2)
            if ow_res.status_code == 200:
                w = ow_res.json()
                ha_data.update({"temp": round(w['main']['temp']), "pressure": w['main']['pressure'], "humidity": w['main']['humidity']})
        except: pass

    if request.method == 'POST':
        data = request.form
        waga = data.get('waga', '0').replace(',', '.')
        if mode == 'create':
            sql = """INSERT INTO ha_vita_pressure (Date, `atmosf.`, P_skurczowe, P_rozkurczowe, Puls, temperatura, wilgotnosc, waga, miasto, uwagi) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (data['Date'], data['atmosf'], data['P_skurczowe'], data['P_rozkurczowe'], data['Puls'], data['temperatura'], data['wilgotnosc'], waga, data['miasto'], data['uwagi']))
        elif mode == 'edit':
            sql = """UPDATE ha_vita_pressure SET Date=%s, `atmosf.`=%s, P_skurczowe=%s, P_rozkurczowe=%s, Puls=%s, temperatura=%s, wilgotnosc=%s, waga=%s, miasto=%s, uwagi=%s 
                     WHERE id_ha_fit=%s"""
            cursor.execute(sql, (data['Date'], data['atmosf'], data['P_skurczowe'], data['P_rozkurczowe'], data['Puls'], data['temperatura'], data['wilgotnosc'], waga, data['miasto'], data['uwagi'], id))
        
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('pressure.list_pressure'))

    warsaw_tz = timezone('Europe/Warsaw')
    now = datetime.now(warsaw_tz).strftime('%Y-%m-%dT%H:%M')
    
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
