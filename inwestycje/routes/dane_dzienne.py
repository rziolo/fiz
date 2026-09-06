from flask import Blueprint, render_template, request, redirect, url_for
import os
import mysql.connector
from utils import get_stats

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
dane_dzienne_bp = Blueprint('dane_dzienne', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

@dane_dzienne_bp.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dane_dzienne ORDER BY data DESC LIMIT 100")
    records = cursor.fetchall()
    db.close()
    return render_template('dane_dzienne.html', records=records)

@dane_dzienne_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        d = request.form
        db = get_db_connection()
        cursor = db.cursor()
        sql = """INSERT INTO dane_dzienne (data, wartosc, wklad, H_ilosc, H_vol, L_ilosc, L_vol, turnover, HL, NL)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (d.get('data'), d.get('wartosc'), d.get('wklad'), d.get('h_ilosc'),
                           d.get('h_vol'), d.get('l_ilosc'), d.get('l_vol'), d.get('turnover'),
                           d.get('hl'), d.get('nl')))
        db.commit()
        db.close()
        return redirect(url_for('dane_dzienne.index'))
    
    # Pobranie statystyk do automatycznego wypełnienia formularza
    stats_data = get_stats()
    return render_template('dane_dzienne_create.html', mode='create', row=None, s=stats_data)

@dane_dzienne_bp.route('/view/<int:id>')
def view(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dane_dzienne WHERE id_dane_dzienne = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('dane_dzienne_create.html', mode='view', row=record)

@dane_dzienne_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        d = request.form
        sql = """UPDATE dane_dzienne SET data=%s, wartosc=%s, wklad=%s, H_ilosc=%s, H_vol=%s,
                 L_ilosc=%s, L_vol=%s, turnover=%s, HL=%s, NL=%s WHERE id_dane_dzienne=%s"""
        cursor.execute(sql, (d.get('data'), d.get('wartosc'), d.get('wklad'), d.get('h_ilosc'),
                           d.get('h_vol'), d.get('l_ilosc'), d.get('l_vol'), d.get('turnover'),
                           d.get('hl'), d.get('nl'), id))
        db.commit()
        db.close()
        return redirect(url_for('dane_dzienne.index'))
    cursor.execute("SELECT * FROM dane_dzienne WHERE id_dane_dzienne = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('dane_dzienne_create.html', mode='edit', row=record)

@dane_dzienne_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM dane_dzienne WHERE id_dane_dzienne = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('dane_dzienne.index'))
