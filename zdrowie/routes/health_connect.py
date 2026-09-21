import os
import sqlite3
import subprocess
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, send_file, abort

health_connect_bp = Blueprint('health_connect', __name__)
DB_PATH = '/var/www/html/flask/zdrowie/etl/db/health_connect/health_connect_export.db'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_db_connection():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn

@health_connect_bp.route('/health-connect/pdf')
def serve_pdf():
    today_dt = datetime.now()
    default_date_to = today_dt.strftime('%Y-%m-%d')
    default_date_from = (today_dt - timedelta(days=30)).strftime('%Y-%m-%d')

    date_from = request.args.get('date_from', default_date_from)
    date_to = request.args.get('date_to', default_date_to)
    tab = request.args.get('tab', 'weight')

    gen_script = os.path.join(BASE_DIR, 'etl', 'generuj_wykres.py')
    pdf_path = os.path.join(BASE_DIR, 'static', 'wykres.pdf')
    
    if os.path.exists(gen_script):
        try:
            subprocess.run(['python3', gen_script, date_from, date_to, tab], check=True, timeout=10)
        except Exception as e:
            print(f"Błąd generowania PDF: {e}")

    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        abort(404, description="Brak wygenerowanego pliku wykres.pdf w katalogu static.")

@health_connect_bp.route('/health-connect')
def index():
    conn = get_db_connection()
    
    today_dt = datetime.now()
    default_date_to = today_dt.strftime('%Y-%m-%d')
    default_date_from = (today_dt - timedelta(days=30)).strftime('%Y-%m-%d')

    date_from = request.args.get('date_from', default_date_from)
    date_to = request.args.get('date_to', default_date_to)
    active_tab = request.args.get('tab', 'weight')

    from_ms = int(datetime.strptime(f"{date_from} 00:00:00", '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    to_ms = int(datetime.strptime(f"{date_to} 23:59:59", '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

    weight_raw = conn.execute('''
        SELECT * FROM weight_record_table
        WHERE time BETWEEN ? AND ?
        ORDER BY time DESC
    ''', (from_ms, to_ms)).fetchall()

    daily_weight = {}
    for row in weight_raw:
        row_dict = dict(row)
        time_ms = row_dict.get('time') or 0
        dzien = conn.execute("SELECT date(?, 'unixepoch', 'localtime')", (time_ms / 1000,)).fetchone()[0]
        dt_minute = conn.execute("SELECT strftime('%Y-%m-%d %H:%M', ?, 'unixepoch', 'localtime')", (time_ms / 1000,)).fetchone()[0]
        
        if dzien not in daily_weight:
            raw_w = 0
            for col_name in ['weight', 'weight_in_kg', 'weight_kg', 'weight_grams']:
                if col_name in row_dict and row_dict[col_name] is not None:
                    raw_w = row_dict[col_name]
                    break
            
            val_kg = raw_w / 1000.0 if raw_w > 1000 else float(raw_w)
            val_formatted = f"{val_kg:,.1f}".replace(',', ' ').replace('.', ',')
            
            daily_weight[dzien] = {
                'data_pomiaru': dt_minute,
                'weight_in_kg_str': val_formatted
            }

    weight_data = list(daily_weight.values())

    steps_raw = conn.execute('''
        SELECT date(start_time/1000, 'unixepoch', 'localtime') as dzien,
               MAX(count) as max_krokow,
               SUM(count) as suma_krokow
        FROM steps_record_table
        WHERE start_time BETWEEN ? AND ?
        GROUP BY dzien
        ORDER BY dzien DESC
    ''', (from_ms, to_ms)).fetchall()

    steps_data = []
    for row in steps_raw:
        kroki = row['max_krokow'] if row['suma_krokow'] > 15000 and row['max_krokow'] > 0 else row['suma_krokow']
        steps_data.append({
            'dzien': row['dzien'],
            'suma_krokow_str': f"{int(kroki):,}".replace(',', ' ')
        })

    hr_raw = conn.execute('''
        SELECT 
            s.beats_per_minute,
            s.epoch_millis,
            e.title as exercise_title
        FROM heart_rate_record_series_table s
        JOIN heart_rate_record_table r ON s.parent_key = r.row_id
        LEFT JOIN exercise_session_record_table e 
            ON s.epoch_millis BETWEEN e.start_time AND e.end_time
        WHERE s.epoch_millis BETWEEN ? AND ?
        ORDER BY s.epoch_millis DESC
        LIMIT 500
    ''', (from_ms, to_ms)).fetchall()

    heart_rate_data = []
    for row in hr_raw:
        time_ms = row['epoch_millis'] or 0
        dt_str = conn.execute("SELECT strftime('%Y-%m-%d %H:%M', ?, 'unixepoch', 'localtime')", (time_ms / 1000,)).fetchone()[0]
        info = row['exercise_title'] if row['exercise_title'] else "Spoczynek / Aktywność"
        
        heart_rate_data.append({
            'data_pomiaru': dt_str,
            'rate': row['beats_per_minute'],
            'info': info
        })

    sleep_raw = conn.execute('''
        SELECT * FROM sleep_session_record_table
        WHERE start_time BETWEEN ? AND ?
        ORDER BY start_time DESC
    ''', (from_ms, to_ms)).fetchall()

    daily_sleep = {}
    for row in sleep_raw:
        row_dict = dict(row)
        s_time = row_dict.get('start_time') or 0
        e_time = row_dict.get('end_time') or 0
        dzien = conn.execute("SELECT date(?, 'unixepoch', 'localtime')", (s_time / 1000,)).fetchone()[0]
        
        duration_minutes = (e_time - s_time) / 60000.0 if e_time > s_time else 0
        
        if dzien not in daily_sleep or duration_minutes > daily_sleep[dzien]:
            daily_sleep[dzien] = duration_minutes

    sleep_data = []
    for dzien, total_minutes in daily_sleep.items():
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        sleep_data.append({
            'dzien': dzien,
            'czas_snu_str': f"{hours}h {minutes}m"
        })

    conn.close()

    return render_template(
        'health_connect.html',
        weight=weight_data,
        steps=steps_data,
        heart_rate=heart_rate_data,
        sleep=sleep_data,
        date_from=date_from,
        date_to=date_to,
        active_tab=active_tab
    )
