from flask import Blueprint, render_template, request, redirect, url_for
import os
import mysql.connector

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
ticker_bp = Blueprint('ticker', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

@ticker_bp.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ticker ORDER BY ticker_name ASC")
    records = cursor.fetchall()
    db.close()
    return render_template('ticker.html', records=records)

@ticker_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        d = request.form
        db = get_db_connection()
        cursor = db.cursor()
        sql = "INSERT INTO ticker (ticker_name, market, rating, altman) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (d.get('ticker_name'), d.get('market'), d.get('rating'), d.get('altman') or None))
        db.commit()
        db.close()
        return redirect(url_for('ticker.index'))
    return render_template('ticker_create.html', mode='create', row=None)

@ticker_bp.route('/view/<int:id>')
def view(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ticker WHERE id_ticker = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('ticker_create.html', mode='view', row=record)

@ticker_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        d = request.form
        sql = "UPDATE ticker SET ticker_name=%s, market=%s, rating=%s, altman=%s WHERE id_ticker=%s"
        cursor.execute(sql, (d.get('ticker_name'), d.get('market'), d.get('rating'), d.get('altman') or None, id))
        db.commit()
        db.close()
        return redirect(url_for('ticker.index'))
    cursor.execute("SELECT * FROM ticker WHERE id_ticker = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('ticker_create.html', mode='edit', row=record)

@ticker_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM ticker WHERE id_ticker = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('ticker.index'))
