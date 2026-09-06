from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector, os
from datetime import date

przychody_bp = Blueprint('przychody', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )

@przychody_bp.route('/')
def list_przychody():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM przychody ORDER BY data DESC")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    
    def format_pl(val):
        if val is None or val == 0: return ""
        # Formatowanie: spacja jako separator tysięcy
        return f"{val:,.2f}".replace(",", " ").replace(".", ",").replace(" ", " ")

    return render_template('przychody.html', rows=rows, format_pl=format_pl)

@przychody_bp.route('/manage', methods=['GET', 'POST'])
@przychody_bp.route('/manage/<int:id>', methods=['GET', 'POST'])
def manage(id=None):
    # Pobieramy tryb z adresu URL (?mode=edit lub ?mode=view)
    mode = request.args.get('mode', 'edit') 
    if not id: mode = 'create'
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        d = request.form
        params = (d.get('data'), d.get('ZUS_Iwona'), d.get('ZUS_Robert'), 
                  d.get('gielda'), d.get('odsetki'), d.get('urzad'), 
                  d.get('inne'), d.get('uwagi'))

        if id:
            sql = """UPDATE przychody SET data=%s, ZUS_Iwona=%s, ZUS_Robert=%s, 
                     gielda=%s, odsetki=%s, urzad=%s, inne=%s, uwagi=%s WHERE id_przychody=%s"""
            cursor.execute(sql, params + (id,))
        else:
            sql = """INSERT INTO przychody (data, ZUS_Iwona, ZUS_Robert, gielda, odsetki, urzad, inne, uwagi) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, params)
        
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('przychody.list_przychody'))

    row = {'data': date.today().strftime('%Y-%m-%d')}
    if id:
        cursor.execute("SELECT * FROM przychody WHERE id_przychody = %s", (id,))
        row = cursor.fetchone()
    
    cursor.close()
    db.close()
    return render_template('przychody_create.html', row=row, mode=mode)

@przychody_bp.route('/delete/<int:id>')
def delete(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM przychody WHERE id_przychody = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('przychody.list_przychody'))
