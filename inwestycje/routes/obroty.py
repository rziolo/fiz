from flask import Blueprint, render_template, request, redirect, url_for
import os
import mysql.connector

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
obroty_bp = Blueprint('obroty', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

def get_form_data():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT ticker_name FROM ticker ORDER BY ticker_name")
    tickers = [row['ticker_name'] for row in cursor.fetchall()]
    cursor.execute("SELECT platforma_name FROM platforma ORDER BY platforma_name")
    platforms = [row['platforma_name'] for row in cursor.fetchall()]
    db.close()
    return tickers, platforms

@obroty_bp.route('')
@obroty_bp.route('/')
def index():
    # Domyślnie pokazujemy obecne, chyba że jawnie zażądamy wszystkich przez filter=all
    show_all = request.args.get('filter') == 'all'
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    if show_all:
        query = "SELECT * FROM obroty ORDER BY ticker_nm ASC"
    else:
        query = "SELECT * FROM obroty WHERE sprzedaz_data IS NULL ORDER BY ticker_nm ASC"
        
    cursor.execute(query)
    records = cursor.fetchall()
    db.close()
    return render_template('obroty.html', records=records, is_filtered=not show_all)

@obroty_bp.route('/create', methods=['GET', 'POST'])
def create():
    tickers, platforms = get_form_data()
    if request.method == 'POST':
        d = request.form
        db = get_db_connection()
        cursor = db.cursor()
        sql = """INSERT INTO obroty (ticker_nm, zakup_data, zakup_cena, zakup_ilosc, sprzedaz_data, 
                 sprzedaz_cena, kurs_biezacy, stop_loss, platforma, uwagi) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (d.get('ticker_nm'), d.get('zakup_data'), d.get('zakup_cena'), 
                           d.get('zakup_ilosc'), d.get('sprzedaz_data') or None, 
                           d.get('sprzedaz_cena') or None, d.get('kurs_biezacy') or None, 
                           d.get('stop_loss') or None, d.get('platforma'), d.get('uwagi')))
        db.commit()
        db.close()
        return redirect(url_for('obroty.index'))
    return render_template('obroty_create.html', mode='create', row=None, tickers=tickers, platforms=platforms)

@obroty_bp.route('/view/<int:id>')
def view(id):
    tickers, platforms = get_form_data()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM obroty WHERE id_obroty = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('obroty_create.html', mode='view', row=record, tickers=tickers, platforms=platforms)

@obroty_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    tickers, platforms = get_form_data()
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        d = request.form
        sql = """UPDATE obroty SET ticker_nm=%s, zakup_data=%s, zakup_cena=%s, zakup_ilosc=%s, 
                 sprzedaz_data=%s, sprzedaz_cena=%s, kurs_biezacy=%s, stop_loss=%s, 
                 platforma=%s, uwagi=%s WHERE id_obroty=%s"""
        cursor.execute(sql, (d.get('ticker_nm'), d.get('zakup_data'), d.get('zakup_cena'), 
                           d.get('zakup_ilosc'), d.get('sprzedaz_data') or None, 
                           d.get('sprzedaz_cena') or None, d.get('kurs_biezacy') or None, 
                           d.get('stop_loss') or None, d.get('platforma'), d.get('uwagi'), id))
        db.commit()
        db.close()
        return redirect(url_for('obroty.index'))
    cursor.execute("SELECT * FROM obroty WHERE id_obroty = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('obroty_create.html', mode='edit', row=record, tickers=tickers, platforms=platforms)

@obroty_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM obroty WHERE id_obroty = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('obroty.index'))
