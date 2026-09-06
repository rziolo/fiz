from flask import Blueprint, render_template, request, redirect, url_for
import os
import mysql.connector

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
platforma_bp = Blueprint('platforma', __name__, template_folder=template_dir)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'), database=os.getenv('DB_NAME')
    )

@platforma_bp.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM platforma ORDER BY platforma_name ASC")
    records = cursor.fetchall()
    db.close()
    return render_template('platforma.html', records=records)

@platforma_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('platforma_name')
        url = request.form.get('url')
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO platforma (platforma_name, url) VALUES (%s, %s)", (name, url))
        db.commit()
        db.close()
        return redirect(url_for('platforma.index'))
    return render_template('platforma_create.html', mode='create', row=None)

@platforma_bp.route('/view/<int:id>')
def view(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM platforma WHERE id_platforma = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('platforma_create.html', mode='view', row=record)

@platforma_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('platforma_name')
        url = request.form.get('url')
        cursor.execute("UPDATE platforma SET platforma_name=%s, url=%s WHERE id_platforma=%s", (name, url, id))
        db.commit()
        db.close()
        return redirect(url_for('platforma.index'))
    cursor.execute("SELECT * FROM platforma WHERE id_platforma = %s", (id,))
    record = cursor.fetchone()
    db.close()
    return render_template('platforma_create.html', mode='edit', row=record)

@platforma_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM platforma WHERE id_platforma = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('platforma.index'))
