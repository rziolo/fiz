from flask import Blueprint, render_template, request, redirect, url_for
import os
import mysql.connector

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
dane_bp = Blueprint('dane', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

@dane_bp.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dane ORDER BY data DESC LIMIT 100")
    records = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('dane.html', records=records)

@dane_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        d = request.form
        db = get_db_connection()
        cursor = db.cursor()
        sql = """INSERT INTO dane (data, ticker, ISIN, waluta, open, max, min, close, zmiana, volume, number_transactions, turnover) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        zmiana = float(d.get('close', 0)) - float(d.get('open', 0))
        cursor.execute(sql, (d.get('data'), d.get('ticker'), d.get('isin', ''), d.get('waluta', 'PLN'),
                           d.get('open'), d.get('max'), d.get('min'), d.get('close'), zmiana,
                           d.get('volume'), d.get('number_transactions'), d.get('turnover')))
        db.commit()
        db.close()
        return redirect(url_for('dane.index'))
    return render_template('dane_create.html', mode='create', row=None)

@dane_bp.route('/view/<int:id>')
def view(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dane WHERE id_dane = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('dane_create.html', mode='view', row=record)

@dane_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        d = request.form
        zmiana = float(d.get('close', 0)) - float(d.get('open', 0))
        sql = """UPDATE dane SET data=%s, ticker=%s, ISIN=%s, waluta=%s, open=%s, max=%s, min=%s, 
                 close=%s, zmiana=%s, volume=%s, number_transactions=%s, turnover=%s WHERE id_dane=%s"""
        cursor.execute(sql, (d.get('data'), d.get('ticker'), d.get('isin'), d.get('waluta'),
                           d.get('open'), d.get('max'), d.get('min'), d.get('close'), zmiana,
                           d.get('volume'), d.get('number_transactions'), d.get('turnover'), id))
        db.commit()
        db.close()
        return redirect(url_for('dane.index'))
    
    cursor.execute("SELECT * FROM dane WHERE id_dane = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('dane_create.html', mode='edit', row=record)

@dane_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM dane WHERE id_dane = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('dane.index'))
