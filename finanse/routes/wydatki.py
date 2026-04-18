from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector, os, datetime

wydatki_bp = Blueprint('wydatki', __name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        autocommit=True
    )

@wydatki_bp.route('/')
def list_wydatki():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM wydatki ORDER BY data DESC")
    rows = cursor.fetchall()
    db.close()
    return render_template('wydatki.html', rows=rows)

@wydatki_bp.route('/manage', defaults={'id': None}, methods=['GET', 'POST'])
@wydatki_bp.route('/manage/<int:id>', methods=['GET', 'POST'])
def manage(id):
    mode = request.args.get('mode', 'edit' if id else 'create')
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        d = request.form
        fields = ['data', 'zywnosc', 'niezywnosc', 'car_cost', 'car_km', 'oplaty', 'medycyna', 'inne', 'uwagi']
        vals = []
        for f in fields:
            val = d.get(f, '0' if f != 'data' and f != 'uwagi' else '')
            if f not in ['data', 'uwagi']:
                val = str(val).replace(',', '.')
            vals.append(val)

        if id:
            set_clause = ", ".join([f"{f}=%s" for f in fields])
            cursor.execute(f"UPDATE wydatki SET {set_clause} WHERE id_wydatki=%s", vals + [id])
        else:
            cols, placeholders = ", ".join(fields), ", ".join(["%s"] * len(fields))
            cursor.execute(f"INSERT INTO wydatki ({cols}) VALUES ({placeholders})", vals)
        
        db.close()
        return redirect(url_for('wydatki.list_wydatki'))

    row = None
    if id:
        cursor.execute("SELECT * FROM wydatki WHERE id_wydatki = %s", (id,))
        row = cursor.fetchone()
    
    if not row:
        row = {'data': datetime.date.today().strftime('%Y-%m-%d')}
        for col in ['zywnosc', 'niezywnosc', 'car_cost', 'car_km', 'oplaty', 'medycyna', 'inne']:
            row[col] = '0.00'

    db.close()
    return render_template('wydatki_create.html', mode=mode, row=row)

@wydatki_bp.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM wydatki WHERE id_wydatki = %s", (id,))
    db.close()
    return redirect(url_for('wydatki.list_wydatki'))
